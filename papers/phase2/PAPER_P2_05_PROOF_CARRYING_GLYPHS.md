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

## Theorem Spine

- `P2G-T0001`: `Circle.Phase2.proofGlyphTheoremId_mk`
- `P2G-T0002`: `Circle.Phase2.proofGlyphLeanName_mk`
- `P2G-T0003`: `Circle.Phase2.proofGlyphGlyphId_mk`
- `P2G-T0004`: `Circle.Phase2.proofGlyphValidAgainst_resolves_metadata`
- `P2G-T0005`: `Circle.Phase2.proofGlyphValidAgainst_of_matching_metadata`

## Proved Core

The three proved facts are projection laws for constructed certificates:

```text
certificate.theoremId = theorem id supplied at construction
certificate.leanName = Lean declaration supplied at construction
certificate.glyphId = glyph id supplied at construction
```

These laws look small, but they establish the basic integrity contract for proof-carrying diagrams. If a visual glyph claims to represent a theorem, the system must be able to recover the theorem id and Lean declaration from the object itself, not from a caption or informal explanation.

`P2G-T0004` proves the validity boundary: if a glyph is valid against finite theorem metadata, then some metadata entry is present and its theorem id and Lean declaration name match the glyph fields. `P2G-T0005` proves the constructor direction: an included matching metadata entry is enough to make the glyph valid against that finite metadata list.

The Python sidecar checks the same certificate-field projections on a finite-circle glyph example, then checks matching metadata, missing theorem id rejection, and Lean-name mismatch rejection.

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
- Connect the finite theorem metadata model to generated site theorem data without changing the proof predicate.
- Add semantic checks only after the syntax and theorem dependency model are clear.
- Treat diagrams as proof interfaces, not proof substitutes.

## Guardrail

This paper proves certificate-field projection facts and finite metadata validity only. Glyph semantics, normal forms, generated-JSON parsing, dependency correctness, proof search, and visual theorem browsing remain future work until formalized.
