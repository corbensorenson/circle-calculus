"""Exploratory dimensional helpers for Circle Calculus."""

from .common import euler_characteristic, suspension_counts
from .hopf import (
    hopf_fiber_point,
    hopf_map,
    normalize_pair,
    pair_norm_sq,
    phase_rotate,
    sphere_norm_sq,
    unit_phase,
)
from .quaternion import (
    Quaternion,
    normalize_pair as normalize_quaternion_pair,
    pair_squared_norm as quaternion_pair_squared_norm,
    quaternionic_hopf_map,
    r5_norm_sq,
    right_phase_rotate,
    unit_i_phase,
)
from .sphere_grid import sphere_grid_counts, suspended_circle_counts

__all__ = [
    "euler_characteristic",
    "hopf_fiber_point",
    "hopf_map",
    "normalize_pair",
    "pair_norm_sq",
    "phase_rotate",
    "Quaternion",
    "quaternion_pair_squared_norm",
    "quaternionic_hopf_map",
    "r5_norm_sq",
    "right_phase_rotate",
    "normalize_quaternion_pair",
    "sphere_grid_counts",
    "sphere_norm_sq",
    "suspended_circle_counts",
    "suspension_counts",
    "unit_i_phase",
    "unit_phase",
]
