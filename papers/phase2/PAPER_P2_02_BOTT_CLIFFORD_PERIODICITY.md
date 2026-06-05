# Circle Calculus Phase II.2: Bott and Clifford Periodicity

Status: draft with a proved finite period-8 clock seed.

## Aim

Track the dimension-clock program around real Clifford algebras, spinors, Bott periodicity, K-theory, and KO-theory without claiming those theories are formalized here yet.

The current formal seed is only `COMMON-0006`, the finite bookkeeping clock

```text
dimension |-> dimension mod 8
```

This clock is useful because later Bott/Clifford work is organized by eight-step dimension classes. It is not itself Bott periodicity.

## Theorem Spine

- `P2B-T0001`: the clock index is always below `8`. Lean declaration: `Circle.Phase2.bottClockIndex_lt_eight`.
- `P2B-T0002`: adding `8` preserves the clock index. Lean declaration: `Circle.Phase2.bottClockIndex_add_eight`.
- `P2B-T0003`: dimension zero has clock index zero. Lean declaration: `Circle.Phase2.bottClockIndex_zero`.

These are Lean-proved finite arithmetic facts. They support dimension-indexed organization, but they do not prove any Clifford algebra, K-theory, KO-theory, or Bott periodicity theorem.

## Next Program

- Choose a formal Clifford algebra representation before adding Clifford-periodicity theorem ids.
- Keep Bott and K-theory claims as cited background until a Lean formalization path is selected.
- Link this clock to the stable-sphere paper only as roadmap structure, not as a proof that stable invariants are periodic.

## Guardrail

No periodicity theorem is treated as proved until it has a compiled Lean declaration or an explicitly cited background status.
