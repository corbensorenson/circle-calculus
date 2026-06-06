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
from .number_provenance import (
    NumberProvenance,
    StrideProvenance,
    divisors,
    factor_pairs,
    number_provenance,
    provenance_summary,
    stride_provenance,
    value_only_summary,
)

__all__ = [
    "Circle",
    "FiniteCoilSignature",
    "NumberProvenance",
    "StrideProvenance",
    "build_s1_signature_index",
    "divisors",
    "factor_pairs",
    "finite_coil_signature",
    "number_provenance",
    "provenance_summary",
    "search_theorems_by_tags",
    "signature_tags",
    "stride_provenance",
    "value_only_summary",
]
