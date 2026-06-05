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
from .sphere_grid import sphere_grid_counts, suspended_circle_counts

__all__ = [
    "euler_characteristic",
    "hopf_fiber_point",
    "hopf_map",
    "normalize_pair",
    "pair_norm_sq",
    "phase_rotate",
    "sphere_grid_counts",
    "sphere_norm_sq",
    "suspended_circle_counts",
    "suspension_counts",
    "unit_phase",
]
