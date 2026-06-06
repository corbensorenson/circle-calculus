"""Python reference models for Circle Calculus.

These models support examples and tests. They are not formal proofs.
"""

from .finite import Circle
from .finite_search import (
    FiniteCoilSignature,
    build_s1_signature_index,
    finite_coil_signature,
    search_theorems_by_tags,
    signature_tags,
)

__all__ = [
    "Circle",
    "FiniteCoilSignature",
    "build_s1_signature_index",
    "finite_coil_signature",
    "search_theorems_by_tags",
    "signature_tags",
]
