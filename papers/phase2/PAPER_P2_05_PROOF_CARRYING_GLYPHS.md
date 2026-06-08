# Circle Calculus Phase II.5: Proof-Carrying Glyphs

Status: polished draft with a proved glyph-certificate and finite metadata-validity seed.

## Aim

This paper states one of the central interface goals of Circle Calculus: diagrams should become proof-carrying objects, not decorative companions to proofs. A glyph should eventually compile to formal syntax, theorem ids, Lean declarations, proof certificates, semantic models, and projection views.

The current formal seed is `COMMON-0013`, a proof-glyph certificate carrying:

```text
glyph id
theorem id
Lean declaration name
```

This is not a diagram normalizer yet. It is the checked metadata contract that a rendered glyph must satisfy before it can be called proof-carrying.

The Phase IV audit adds a second bounded layer:

```text
theorem metadata entry = theorem id + Lean declaration name
glyph validity = glyph fields match some metadata entry
```

This is still not a JSON parser or a live theorem-browser proof. It is the finite predicate that the exporter/site layer must respect.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_P2_05_PROOF_CARRYING_GLYPHS/lean/PaperP205.lean
```

The Python examples are:

```text
sidecars/PAPER_P2_05_PROOF_CARRYING_GLYPHS/python/test_proof_glyph_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The generated glyph fixture is checked by `scripts/check_glyph_fixtures.py`; Lean declarations determine proof status.

## Theorem Spine

- `P2G-T0001`: `Circle.Phase2.proofGlyphTheoremId_mk`
- `P2G-T0002`: `Circle.Phase2.proofGlyphLeanName_mk`
- `P2G-T0003`: `Circle.Phase2.proofGlyphGlyphId_mk`
- `P2G-T0004`: `Circle.Phase2.proofGlyphValidAgainst_resolves_metadata`
- `P2G-T0005`: `Circle.Phase2.proofGlyphValidAgainst_of_matching_metadata`
- `P2G-T0006`: `Circle.Phase2.proofGlyphValidAgainst_cons`

## Proved Core

The three proved facts are projection laws for constructed certificates:

```text
certificate.theoremId = theorem id supplied at construction
certificate.leanName = Lean declaration supplied at construction
certificate.glyphId = glyph id supplied at construction
```

These laws look small, but they establish the basic integrity contract for proof-carrying diagrams. If a visual glyph claims to represent a theorem, the system must be able to recover the theorem id and Lean declaration from the object itself, not from a caption or informal explanation.

`P2G-T0004` proves the validity boundary: if a glyph is valid against finite theorem metadata, then some metadata entry is present and its theorem id and Lean declaration name match the glyph fields. `P2G-T0005` proves the constructor direction: an included matching metadata entry is enough to make the glyph valid against that finite metadata list.

`P2G-T0006` proves manifest-growth monotonicity: if a glyph is already valid against a finite metadata list, it remains valid after a new metadata entry is prepended. This is a small but important registry law for a Living Book whose theorem manifest grows over time.

The Python sidecar checks the same certificate-field projections on a finite-circle glyph example, then checks matching metadata, missing theorem id rejection, Lean-name mismatch rejection, and preservation under manifest growth.

## Generated Glyph Fixture

`P5-EDGE-001` adds the first generated glyph fixture:

```text
manifests/glyphs/proof_glyph_fixtures.yaml
site/data/generated/glyph_index.json
```

The fixture resolves glyph theorem ids and dictionary ids against generated site data. It includes Lean-proved glyphs for already proved theorem ids.

The fixture also includes `S15-T0001` (`Circle.Future.S15.octonionicHopfRoadmap`) as a future roadmap glyph. That roadmap glyph must render with planned status. This is a status compiler for the interface layer, not a proof of glyph syntax, semantics, or diagram normalization.

## First Demonstrator

The first serious target should be proof-carrying circle diagrams for modular arithmetic and prime structure:

```text
C_13, stride 5
  -> orbit diagram
  -> period/gcd certificate
  -> theorem manifest id
  -> Lean declaration
  -> Python example
  -> paper section
```

Composite examples such as `C_36, stride 8` should add orbit decomposition, fiber/kernel provenance, and explicit links back to the scaling and factor papers.

## Next Program

- Define glyph syntax trees and normal forms.
- Require every glyph claim to link to a theorem id or an explicit exploratory status.
- Expand the generated glyph fixture into syntax-tree and normal-form examples.
- Connect the finite theorem metadata model to generated site theorem data without changing the proof predicate.
- Use manifest-growth monotonicity as the safe rule for expanding generated theorem metadata.
- Add semantic checks only after the syntax and theorem dependency model are clear.
- Treat diagrams as proof interfaces, not proof substitutes.

## Guardrail

This paper proves certificate-field projection facts and finite metadata validity only. Glyph semantics, normal forms, generated-JSON parsing, dependency correctness, proof search, and visual theorem browsing remain future work until formalized.
