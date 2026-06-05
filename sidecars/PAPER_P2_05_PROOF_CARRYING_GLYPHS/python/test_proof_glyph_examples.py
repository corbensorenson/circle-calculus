from dataclasses import dataclass


@dataclass(frozen=True)
class ProofGlyph:
    glyph_id: str
    theorem_id: str
    lean_name: str


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
