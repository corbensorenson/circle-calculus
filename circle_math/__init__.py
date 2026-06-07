"""Python reference models for Circle Calculus.

These models support examples and tests. They are not formal proofs.
"""

from .finite import Circle
from .additive import (
    CauchyDavenportExample,
    cauchy_davenport_example,
    circle_pair_sum_counts,
    circle_sumset,
    egz_sharpness_family,
    has_zero_sum_subsequence,
    zero_sum_subsequence_witnesses,
)
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
    "CauchyDavenportExample",
    "FiniteCoilSignature",
    "NumberProvenance",
    "StrideProvenance",
    "build_s1_signature_index",
    "cauchy_davenport_example",
    "circle_pair_sum_counts",
    "circle_sumset",
    "divisors",
    "egz_sharpness_family",
    "factor_pairs",
    "finite_coil_signature",
    "has_zero_sum_subsequence",
    "number_provenance",
    "provenance_summary",
    "search_theorems_by_tags",
    "signature_tags",
    "stride_provenance",
    "value_only_summary",
    "zero_sum_subsequence_witnesses",
]
