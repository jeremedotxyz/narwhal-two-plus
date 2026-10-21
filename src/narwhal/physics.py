"""Homogeneous-water geometry. Ports and component delays need calibration."""
import math
C0 = 299792458.0

def unit_ray(angle_rad):
    if not math.isfinite(angle_rad) or abs(angle_rad) >= math.pi / 2:
        raise ValueError('scan angle must be finite and inside +/-90 degrees')
    return (math.sin(angle_rad), 0.0, math.cos(angle_rad))

def path_length(point, tx, rx):
    return math.dist(point, tx) + math.dist(point, rx)

def bistatic_range(tof_ns, ray, tx, rx, n_group=1.34):
    """Exact ellipsoid/ray intersection; returns distance measured from TX."""
    if not math.isfinite(tof_ns) or not math.isfinite(n_group) or n_group <= 0:
        raise ValueError('invalid delay or group index')
    if not all(math.isfinite(v) for v in (*ray, *tx, *rx)) or not math.isclose(sum(v*v for v in ray),1,abs_tol=1e-10):
        raise ValueError('finite geometry and a unit ray required')
    total = C0 * tof_ns * 1e-9 / n_group
    b = tuple(rx[i]-tx[i] for i in range(3))
    b2 = sum(v*v for v in b)
    if total <= math.sqrt(b2):
        raise ValueError('delay is shorter than the TX/RX baseline path')
    distance = (total*total-b2) / (2*(total-sum(ray[i]*b[i] for i in range(3))))
    if not math.isfinite(distance) or distance <= 0:
        raise ValueError('nonphysical range')
    return distance

def air_to_water_angle(angle_air_rad, n_phase=1.333):
    if not math.isfinite(angle_air_rad) or not math.isfinite(n_phase) or n_phase <= 1 or abs(angle_air_rad) >= math.pi/2:
        raise ValueError('invalid refraction parameters')
    return math.asin(math.sin(angle_air_rad)/n_phase)

def derived_metrics(config):
    return {
        'group_velocity_m_s': C0/config.n_group,
        'monostatic_tof_5m_ns': 10*config.n_group/C0*1e9,
        'range_spacing_at_2GSps_m': C0*0.5e-9/(2*config.n_group),
        'swath_at_5m_m': 10*math.tan(math.radians(config.fov_deg/2)),
        'ideal_line_rate_hz': config.pulse_rate_hz/config.samples_per_line,
        'seawater_pressure_300m_pa': 1025*9.81*300,
        'clear_aperture_load_60mm_n': 1025*9.81*300*math.pi*0.03**2,
        'optical_average_power_w': 5e-6*config.pulse_rate_hz,
    }
