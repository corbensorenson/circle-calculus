from circle_math.number_provenance import (
    divisors,
    factor_pairs,
    provenance_summary,
    stride_provenance,
    value_only_summary,
)


def test_number_provenance_records_divisors_and_factor_pairs() -> None:
    assert divisors(36) == (1, 2, 3, 4, 6, 9, 12, 18, 36)
    assert factor_pairs(36) == ((1, 36), (2, 18), (3, 12), (4, 9), (6, 6))


def test_stride_provenance_records_orbit_period_and_cofactor() -> None:
    view = stride_provenance(36, 8)
    assert view.divisor == 4
    assert view.cofactor == 9
    assert view.period == 9
    assert view.orbit_count == 4
    assert "CC-T0005" in view.theorem_ids
    assert "CC-T0006" in view.theorem_ids


def test_full_coil_stride_provenance_links_full_coil_theorem() -> None:
    view = stride_provenance(13, 5)
    assert view.divisor == 1
    assert view.period == 13
    assert view.orbit_count == 1
    assert "CC-T0054" in view.theorem_ids


def test_provenance_summary_adds_views_missing_from_value_only_summary() -> None:
    value_only = value_only_summary(36)
    provenance = provenance_summary(36, (8, 12))
    assert set(value_only) == {"value"}
    assert provenance["value"] == 36
    assert "divisors" in provenance
    assert "factor_pairs" in provenance
    assert "stride_views" in provenance
    assert "theorem_ids" in provenance
