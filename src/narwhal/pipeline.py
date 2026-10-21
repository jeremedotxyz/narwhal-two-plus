"""Replay, reconstruction and a seeded plane-scene simulator."""
from dataclasses import dataclass, asdict
import math
import random
from .physics import C0, unit_ray, path_length, bistatic_range

NO_RETURN = 1
OUT_OF_RANGE = 2
SATURATED = 4
INVALID = 8
UNSYNCED = 16
SIMULATED = 32

@dataclass(frozen=True)
class Point:
    timestamp_ns: int
    x: float
    y: float
    z: float
    range_tx_m: float
    intensity: int
    angle_rad: float
    line_id: int
    quality: int
    status: int = 0

    def to_dict(self):
        d = asdict(self)
        for k,v in d.items():
            if isinstance(v,float) and not math.isfinite(v):
                d[k] = None
        return d

def geometry(config):
    return (0.0,-config.baseline_m/2,0.0),(0.0,config.baseline_m/2,0.0)

def reconstruct(event, config):
    if event.get('schema_version') != 1:
        raise ValueError('event schema_version must be 1')
    simulated = event.get('simulated')
    if type(simulated) is not bool:
        raise ValueError('simulated must be an explicit boolean')
    base = (SIMULATED if simulated else 0) | (0 if event.get('time_basis') == 'TAI' else UNSYNCED)
    timestamp = event['timestamp_ns']; line_id = event['line_id']; intensity = event.get('intensity',0)
    if type(timestamp) is not int or not 0 <= timestamp < 2**64:
        raise ValueError('invalid timestamp')
    if type(line_id) is not int or not 0 <= line_id < 2**32:
        raise ValueError('invalid line ID')
    if type(intensity) is not int or not 0 <= intensity <= 65535:
        raise ValueError('intensity outside uint16')
    angle = float(event['angle_rad'])
    ray = unit_ray(angle)
    if abs(angle) > math.radians(config.fov_deg/2)+1e-9:
        raise ValueError('angle outside calibrated scan field')
    q = base | (SATURATED if intensity == 65535 else 0)
    r = math.nan
    delay = event.get('tof_ns')
    if delay is None:
        q |= NO_RETURN
    else:
        try:
            tx,rx = geometry(config)
            r = bistatic_range(float(delay)-config.source_delay_ns,ray,tx,rx,config.n_group)
            if not config.range_min_m <= r <= config.range_max_m:
                r=math.nan; q |= OUT_OF_RANGE
        except (ValueError, TypeError, OverflowError):
            q |= INVALID
    tx,_ = geometry(config)
    xyz=tuple(tx[i]+r*ray[i] for i in range(3)) if math.isfinite(r) else (math.nan,)*3
    return Point(timestamp,*xyz,r,intensity,angle,line_id,q)

def simulate(config, lines=2, plane_z_m=5.0, seed=532):
    if type(lines) is not int or lines < 1 or not math.isfinite(plane_z_m) or plane_z_m <= 0:
        raise ValueError('positive line count and plane distance required')
    rng=random.Random(seed);tx,rx=geometry(config)
    for line_id in range(lines):
        for sample in range(config.samples_per_line):
            # Pixel centers avoid duplicating endpoints; flyback is omitted.
            angle=math.radians(config.fov_deg)*((sample+0.5)/config.samples_per_line-0.5)
            ray=unit_ray(angle);r=plane_z_m/ray[2]
            p=tuple(tx[i]+r*ray[i] for i in range(3));length=path_length(p,tx,rx)
            delay=length*config.n_group/C0*1e9+config.source_delay_ns+rng.gauss(0,config.timing_sigma_ns)
            intensity=min(65535,max(0,round(60000*math.exp(-config.attenuation_m_inv*length)/max(r*r,1))))
            if rng.random() < config.dropout_probability:
                delay=None;intensity=0
            yield {'schema_version':1,'timestamp_ns':round((line_id*config.samples_per_line+sample)/config.pulse_rate_hz*1e9),
                   'time_basis':'SIM_RELATIVE','simulated':True,'line_id':line_id,'angle_rad':angle,
                   'tof_ns':delay,'intensity':intensity}
