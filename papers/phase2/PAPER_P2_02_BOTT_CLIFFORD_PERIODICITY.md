# Circle Calculus Phase II.2: Bott and Clifford Periodicity

Status: polished draft with a proved finite period-8 clock seed.

## Aim

This paper opens the Bott/Clifford direction without pretending that Circle Calculus has already formalized Clifford algebras, spinor modules, K-theory, KO-theory, or Bott periodicity. The immediate goal is only to install a checked eight-step dimension clock that later work can use for indexing.

That clock matters because many real Clifford and Bott-periodic phenomena are organized by dimension classes modulo `8`. The project needs that bookkeeping layer before it can responsibly attach stronger algebraic or topological statements.

## Current Model

The formal seed is `COMMON-0006`:

```text
dimension |-> dimension mod 8
```

This model is finite arithmetic. It is not Bott periodicity itself. It is a proof-carrying dimension index that can appear in future manifests, dictionaries, and papers without smuggling in unproved theory.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY/lean/PaperP202.lean
```

The Python examples are:

```text
sidecars/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY/python/test_bott_clock_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks period-8 examples; Lean declarations determine proof status.

## Theorem Spine

- `P2B-T0001`: `Circle.Phase2.bottClockIndex_lt_eight`
- `P2B-T0002`: `Circle.Phase2.bottClockIndex_add_eight`
- `P2B-T0003`: `Circle.Phase2.bottClockIndex_zero`
- `P2B-T0004`: `Circle.Phase2.bottClockIndex_add_mul_eight`

## Proved Core

`P2B-T0001` proves that every clock index is bounded below `8`. This makes the dimension class a genuine finite index rather than informal notation.

`P2B-T0002` proves the eight-step closure law:

```text
bottClockIndex (dimension + 8) = bottClockIndex dimension
```

`P2B-T0004` proves the multi-pass closure law:

```text
bottClockIndex (dimension + passes * 8) = bottClockIndex dimension
```

`P2B-T0003` proves that dimension zero lands at clock index zero.

Together these theorems give the future Bott/Clifford program a reliable indexing primitive. The Python sidecar checks the same period-8 examples, including wraparound behavior and the zero case.

## Next Program

- Choose a formal Clifford algebra representation before adding Clifford-periodicity theorem ids.
- Decide whether to rely on existing mathlib infrastructure or build a small bounded model first.
- Keep Bott, K-theory, and KO-theory claims as cited background until Lean declarations exist.
- Link this clock to stable-sphere work as roadmap structure, not as proof that stable invariants are periodic.

## Guardrail

No Clifford, spinor, K-theory, KO-theory, or Bott periodicity theorem is proved by this paper. Only the modulo-8 clock facts are proved. Stronger claims must remain background, planned, or future until they have compiled Lean declarations and manifest entries.
