from dataclasses import dataclass


@dataclass(frozen=True)
class ProofGlyph:
    glyph_id: str
    theorem_id: str
    lean_name: str


@dataclass(frozen=True)
class TheoremMetadata:
    theorem_id: str
    lean_name: str


def glyph_matches_metadata(glyph: ProofGlyph, metadata: TheoremMetadata) -> bool:
    return glyph.theorem_id == metadata.theorem_id and glyph.lean_name == metadata.lean_name


def proof_glyph_valid_against(glyph: ProofGlyph, manifest: tuple[TheoremMetadata, ...]) -> bool:
    return any(glyph_matches_metadata(glyph, metadata) for metadata in manifest)


def test_proof_glyph_exposes_theorem_id() -> None:
    glyph = ProofGlyph(
        glyph_id="glyph:c13_stride5",
        theorem_id="CC-T0005",
        lean_name="Circle.period_eq_n_div_gcd",
    )
    assert glyph.theorem_id == "CC-T0005"


def test_proof_glyph_exposes_lean_name() -> None:
    glyph = ProofGlyph(
        glyph_id="glyph:c13_stride5",
        theorem_id="CC-T0005",
        lean_name="Circle.period_eq_n_div_gcd",
    )
    assert glyph.lean_name == "Circle.period_eq_n_div_gcd"


def test_proof_glyph_exposes_glyph_id() -> None:
    glyph = ProofGlyph(
        glyph_id="glyph:c13_stride5",
        theorem_id="CC-T0005",
        lean_name="Circle.period_eq_n_div_gcd",
    )
    assert glyph.glyph_id == "glyph:c13_stride5"


def test_proof_glyph_validates_against_matching_metadata() -> None:
    glyph = ProofGlyph(
        glyph_id="glyph:c13_stride5",
        theorem_id="CC-T0005",
        lean_name="Circle.period_eq_n_div_gcd",
    )
    manifest = (
        TheoremMetadata(theorem_id="CC-T0002", lean_name="Circle.rot_comp"),
        TheoremMetadata(theorem_id="CC-T0005", lean_name="Circle.period_eq_n_div_gcd"),
    )

    assert proof_glyph_valid_against(glyph, manifest)


def test_proof_glyph_rejects_missing_theorem_id() -> None:
    glyph = ProofGlyph(
        glyph_id="glyph:unknown",
        theorem_id="CC-T9999",
        lean_name="Circle.period_eq_n_div_gcd",
    )
    manifest = (TheoremMetadata(theorem_id="CC-T0005", lean_name="Circle.period_eq_n_div_gcd"),)

    assert not proof_glyph_valid_against(glyph, manifest)


def test_proof_glyph_rejects_lean_name_mismatch() -> None:
    glyph = ProofGlyph(
        glyph_id="glyph:c13_stride5",
        theorem_id="CC-T0005",
        lean_name="Circle.wrong_name",
    )
    manifest = (TheoremMetadata(theorem_id="CC-T0005", lean_name="Circle.period_eq_n_div_gcd"),)

    assert not proof_glyph_valid_against(glyph, manifest)


def test_proof_glyph_validity_survives_manifest_growth() -> None:
    glyph = ProofGlyph(
        glyph_id="glyph:c13_stride5",
        theorem_id="CC-T0005",
        lean_name="Circle.period_eq_n_div_gcd",
    )
    manifest = (TheoremMetadata(theorem_id="CC-T0005", lean_name="Circle.period_eq_n_div_gcd"),)
    grown_manifest = (
        TheoremMetadata(theorem_id="CC-T0007", lean_name="Circle.prime_full_coils"),
        *manifest,
    )

    assert proof_glyph_valid_against(glyph, manifest)
    assert proof_glyph_valid_against(glyph, grown_manifest)
