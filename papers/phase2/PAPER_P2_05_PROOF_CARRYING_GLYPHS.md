# Circle Calculus Phase II.5: Proof-Carrying Glyphs

Status: polished draft with a proved glyph-certificate seed.

## Aim

This paper states one of the central interface goals of Circle Calculus: diagrams should become proof-carrying objects, not decorative companions to proofs. A glyph should eventually compile to formal syntax, theorem ids, Lean declarations, proof certificates, semantic models, and projection views.

The current formal seed is `COMMON-0013`, a proof-glyph certificate carrying:

```text
glyph id
theorem id
Lean declaration name
```

This is not a diagram normalizer yet. It is the checked metadata contract that a rendered glyph must satisfy before it can be called proof-carrying.

## Theorem Spine

- `P2G-T0001`: `Circle.Phase2.proofGlyphTheoremId_mk`
- `P2G-T0002`: `Circle.Phase2.proofGlyphLeanName_mk`
- `P2G-T0003`: `Circle.Phase2.proofGlyphGlyphId_mk`

## Proved Core

The three proved facts are projection laws for constructed certificates:

```text
certificate.theoremId = theorem id supplied at construction
certificate.leanName = Lean declaration supplied at construction
certificate.glyphId = glyph id supplied at construction
```

These laws look small, but they establish the basic integrity contract for proof-carrying diagrams. If a visual glyph claims to represent a theorem, the system must be able to recover the theorem id and Lean declaration from the object itself, not from a caption or informal explanation.

The Python sidecar checks the same certificate-field projections on a finite-circle glyph example.

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
- Add semantic checks only after the syntax and theorem dependency model are clear.
- Treat diagrams as proof interfaces, not proof substitutes.

## Guardrail

This paper proves certificate-field projection facts only. Glyph semantics, normal forms, dependency correctness, proof search, and visual theorem browsing remain future work until formalized.
