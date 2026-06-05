# Circle Calculus Compute 4: Coil Systems Applications

Status: polished draft with a proved round-robin schedule seed.

## Aim

This paper keeps the broader systems application queue organized without turning hypotheses into claims. The tracked families are:

```text
CoilHash, CoilMotion, CoilPRM, CoilCodec, CoilANN,
CoilAcquire, CoilCAM, CoilTorsion, CoilDetect, CoilSched, CoilQ
```

They share a practical rule: Circle Calculus may help only when the workload has real cyclic, periodic, angular, toroidal, rotational, ring-buffer, or phase structure.

The current formal seed is `COMMON-0024`, the round-robin slot schedule

```text
slot(slot_count,tick) = tick mod slot_count
```

for positive slot counts. This is a `CoilSched`-style primitive, not a fairness or load-balancing theorem.

## Theorem Spine

- `COMPS-T0001`: `Circle.Applications.roundRobinSlot_lt_slotCount`
- `COMPS-T0002`: `Circle.Applications.roundRobinSlot_add_slotCount`
- `COMPS-T0003`: `Circle.Applications.roundRobinSlot_zero`

## Proved Core

`COMPS-T0001` proves that the selected slot is bounded by the positive slot count. `COMPS-T0002` proves closure after one full pass through the slots. `COMPS-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

These facts are enough to certify a basic round-robin address schedule. They do not prove fairness, starvation freedom, load balancing, remapping bounds, robotics coverage, codec quality, ANN recall, acquisition quality, CAM path optimality, torsion-model performance, anomaly-detection accuracy, or quantum-circuit simplification.

## Application Queue

- `CoilHash`: multi-ring consistent hashing, hotspot diagnostics, and remapping proofs.
- `CoilMotion`: phase-aware animation loops and quaternion orientation blending.
- `CoilPRM` / `CoilRRT`: torus and `S^3` samplers for robotics configuration spaces.
- `CoilCodec`: phase-aware audio/video compression and loop detection.
- `CoilANN`: angular/hash-ring vector indexing through products of circles.
- `CoilAcquire`, `CoilCAM`, `CoilTorsion`, `CoilDetect`, `CoilSched`, and `CoilQ`: domain-specific tracks requiring their own models and baselines.

## Next Program

- Prefer small demonstrators with clear baselines.
- Add fairness/starvation statements only after choosing an explicit scheduler model.
- Benchmark or domain-test each systems hypothesis before claiming usefulness.
- Record failures and negative results as project information.

## Guardrail

These are application hypotheses, not automatic consequences of the mathematical spine. Each domain needs its own model, sidecar, benchmark, and manifest entries before stronger claims are made.
