from circle_math.finite_search import (
    build_s1_signature_index,
    finite_coil_signature,
    search_theorems_by_tags,
    signature_tags,
)


def test_finite_coil_signature_records_gcd_period_and_orbits() -> None:
    signature = finite_coil_signature(12, 4)
    assert signature.gcd == 4
    assert signature.period == 3
    assert signature.orbit_count == 4
    assert not signature.full_coil


def test_prime_stride_signature_is_full_coil() -> None:
    signature = finite_coil_signature(13, 5)
    assert signature.gcd == 1
    assert signature.period == 13
    assert signature.orbit_count == 1
    assert signature.full_coil
    assert "coprime" in signature_tags(signature)


def test_signature_index_covers_existing_s1_theorems() -> None:
    index = build_s1_signature_index()
    theorem_ids = {theorem_id for theorem_group in index.values() for theorem_id in theorem_group}
    assert len(theorem_ids) >= 10
    assert "CC-T0005" in theorem_ids
    assert "CC-T0061" in theorem_ids


def test_search_by_signature_tags_finds_period_and_gcd_theorems() -> None:
    matches = search_theorems_by_tags(["period", "gcd"])
    assert "CC-T0005" in matches


def test_search_by_signature_tags_finds_same_orbit_gcd_bridge() -> None:
    matches = search_theorems_by_tags(["same-orbit", "gcd-congruence"])
    assert matches == ("CC-T0059", "CC-T0060", "CC-T0061")
