# Circle Calculus Phase II.5: Proof-Carrying Glyphs

Status: draft with a proved glyph-certificate seed.

## Aim

Build glyphs and diagrams that compile to formal syntax, theorem ids, Lean declarations, proof certificates, semantic models, and projection views.

The current formal seed is `COMMON-0013`, a proof-glyph certificate carrying:

```text
glyph id
theorem id
Lean declaration name
```

This is not a diagram normalizer yet. It is the checked metadata contract that a rendered glyph must satisfy before it can be called proof-carrying.

## Theorem Spine

- `P2G-T0001`: a constructed proof glyph exposes its theorem id. Lean declaration: `Circle.Phase2.proofGlyphTheoremId_mk`.
- `P2G-T0002`: a constructed proof glyph exposes its Lean declaration name. Lean declaration: `Circle.Phase2.proofGlyphLeanName_mk`.

These are Lean-proved certificate projection facts. They support the future glyph interface, but they do not prove glyph semantics, diagram normalization, theorem dependency correctness, or proof search.

## Next Program

- Begin with finite-circle diagrams such as `C_13` stride `5` and `C_36` stride `8`.
- Require every glyph claim to link to a theorem id or an explicit exploratory status.
- Treat diagrams as proof interfaces, not proof substitutes.

## Guardrail

The first demonstrator should be proof-carrying circle diagrams for modular arithmetic and prime structure.
