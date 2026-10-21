"""Validated SI configuration; water indices are supplied, never inferred from T/S."""
from dataclasses import dataclass, asdict
import json
import math

@dataclass(frozen=True)
class Config:
    schema_version: int = 1
    calibration_id: str = 'concept-A-20261021'
    n_group: float = 1.34
    n_phase: float = 1.333
    baseline_m: float = 0.06
    fov_deg: float = 30.0
    samples_per_line: int = 1000
    pulse_rate_hz: int = 20000
    range_min_m: float = 1.0
    range_max_m: float = 15.0
    attenuation_m_inv: float = 0.1
    timing_sigma_ns: float = 0.1
    dropout_probability: float = 0.02
    source_delay_ns: float = 0.0
    water_temperature_c: float = 15.0
    salinity_psu: float = 35.0

    def __post_init__(self):
        for name, value in asdict(self).items():
            if name not in ('calibration_id',) and (not isinstance(value, (float, int)) or isinstance(value, bool) or not math.isfinite(value)):
                raise ValueError(f'{name} must be a finite number')
        for name in ('schema_version', 'samples_per_line', 'pulse_rate_hz'):
            if type(getattr(self, name)) is not int:
                raise ValueError(f'{name} must be an integer')
        if self.schema_version != 1 or not isinstance(self.calibration_id, str) or not self.calibration_id:
            raise ValueError('unsupported schema or missing calibration identifier')
        if not (1 < self.n_group < 2 and 1 < self.n_phase < 2):
            raise ValueError('water indices must be between 1 and 2')
        if not (0 <= self.baseline_m < self.range_min_m < self.range_max_m):
            raise ValueError('require 0 <= baseline < minimum range < maximum range')
        if not (0 < self.fov_deg < 90 and 2 <= self.samples_per_line <= 100000 and self.pulse_rate_hz > 0):
            raise ValueError('invalid scan geometry or pulse rate')
        if self.attenuation_m_inv < 0 or self.timing_sigma_ns < 0 or not 0 <= self.dropout_probability <= 1:
            raise ValueError('invalid attenuation, jitter, or dropout')
        if self.salinity_psu < 0:
            raise ValueError('salinity must be nonnegative')

    @classmethod
    def load(cls, path):
        with open(path, encoding='utf-8') as stream:
            return cls(**json.load(stream))
