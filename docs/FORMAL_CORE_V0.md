# Formal Core v0

The v0 formal core is finite and combinatorial. A circle is a cyclic address space, not a Euclidean object.

The Lean model is:

```lean
abbrev Circle.C (n : Nat) := ZMod n
```

The main v0 primitives are:

- `Circle.rot`
- `Circle.coilStep`
- `Circle.closesAt`
- `Circle.stride`
- `Circle.period`
- `Circle.orbitSubgroup`
- `Circle.orbitClassQuotient`
- `Circle.orbitClassCount`
- `Circle.fullCoil`
- `Circle.LiftedNode`
- `Circle.liftWinding`
- `Circle.liftResidue`
- `Circle.liftSuccCarry`
- `Circle.liftSuccWinding`
- `Circle.liftSuccResidue`
- `Circle.liftAddCarry`
- `Circle.liftAddWinding`
- `Circle.liftAddResidue`
- `Circle.liftSuccPair`
- `Circle.liftIterSuccPair`

The first theorem ids are tracked in `manifests/theorem_manifest.yaml`.

## Current Paper 1 Theorem Spine

- `CC-T0001` / `Circle.rot_zero`
- `CC-T0002` / `Circle.rot_comp`
- `CC-T0003` / `Circle.rot_inverse_left`
- `CC-T0004` / `Circle.closesAt_iff_stride_multiple_zero`
- `CC-T0005` / `Circle.period_eq_n_div_gcd`
- `CC-T0006` / `Circle.orbit_decomposition_count`
- `CC-T0007` / `Circle.prime_full_coil`
- `CC-T0009` / `Circle.lift_unique`
- `CC-T0010` / `Circle.lift_add_decomposition`
- `CC-T0011` / `Circle.lift_exists`
- `CC-T0012` / `Circle.lift_successor_decomposition`
- `CC-T0013` / `Circle.lift_add_zero_right`
- `CC-T0014` / `Circle.lift_add_assoc_value`
- `CC-T0015` / `Circle.lift_add_zero_left`
- `CC-T0016` / `Circle.lift_iter_successor_decomposition`
