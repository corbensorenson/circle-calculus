# Circle Calculus Compute 4: Coil Systems Applications

Status: draft with a proved round-robin schedule seed.

## Aim

Track systems applications: `CoilHash`, `CoilMotion`, `CoilPRM`, `CoilCodec`, `CoilANN`, `CoilAcquire`, `CoilCAM`, `CoilTorsion`, `CoilDetect`, `CoilSched`, and `CoilQ`.

The current formal seed is `COMMON-0024`, the round-robin slot schedule

```text
slot(slot_count,tick) = tick mod slot_count
```

for positive slot counts. This is a `CoilSched`-style schedule primitive, not a fairness or load-balancing theorem.

## Theorem Spine

- `COMPS-T0001`: for positive slot count, the round-robin slot is bounded by the slot count. Lean declaration: `Circle.Applications.roundRobinSlot_lt_slotCount`.
- `COMPS-T0002`: for positive slot count, adding one full slot count preserves the round-robin slot. Lean declaration: `Circle.Applications.roundRobinSlot_add_slotCount`.

The Python sidecar checks the same finite examples. Fairness, starvation-freedom, load balancing, and domain-specific systems claims still require explicit models and tests.

## Next Program

- Keep each domain as a benchmarkable or domain-tested roadmap.
- Prefer small demonstrators with clear baselines.
- Record failures and negative results as useful project information.

## Guardrail

These are application hypotheses, not automatic consequences of the mathematical spine.
