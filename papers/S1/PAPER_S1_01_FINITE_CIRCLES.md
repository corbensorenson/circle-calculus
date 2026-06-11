# Circle Calculus S1.1: Finite Circles, Rotations, and Coils

Status: polished dimension guide draft with the finite-circle theorem spine linked to the root Paper 1 artifacts.

## Aim

This paper is the `S^1` home for the finite circle core. It organizes the first Circle Calculus layer around cyclic address spaces, rotations, coils, closure, period, orbit decomposition, the full-coil coprime criterion, and prime full-coil behavior.

The detailed root paper remains `papers/PAPER_01_FINITE_CIRCLES.md`. This dimension paper gives the ladder-facing version: why these results are the `S^1` base layer, which theorem ids they carry, and how later dimensions depend on them.

## Position In The Ladder

The first serious object in the project is not a smooth Euclidean circle. It is a finite cyclic address space:

```text
C_n = ZMod n
```

A node is an address in `C_n`. A rotation is addition by a stride. A coil is the orbit produced by repeating the same rotation. Closure means returning to the starting address, and period is the first positive return time.

This finite model is deliberately modest. It is strong enough to prove recurrence, divisibility, orbit decomposition, and prime full traversal without invoking real analysis, trigonometry, topology, or a geometric drawing as evidence.

## Formal Model

The Lean model is:

```lean
abbrev Circle.C (n : Nat) := ZMod n
```

The core rotation operation is:

```lean
def Circle.rot (n : Nat) (k : Nat) (x : Circle.C n) : Circle.C n :=
  x + (k : ZMod n)
```

The coil step operation records repeated rotation from a starting address:

```lean
def Circle.coilStep (n : Nat) (stride start steps : Nat) : Circle.C n :=
  start + steps * stride
```

The period operation is the additive order of the stride in `C_n`:

```lean
def Circle.period (n k : Nat) : Nat :=
  addOrderOf (Circle.stride n k)
```

These declarations are ordinary modular arithmetic in Lean. The Circle Calculus vocabulary adds a visual and organizational interface, not a new foundation.

## Theorem Spine

- `CC-T0001`: `Circle.rot_zero`, rotation by zero fixes every node.
- `CC-T0002`: `Circle.rot_comp`, composing rotations adds their strides.
- `CC-T0003`: `Circle.rot_inverse_left`, a stride and its inverse return to the start.
- `CC-T0004`: `Circle.closesAt_iff_stride_multiple_zero`, closure is the zero stride-multiple condition in `C_n`.
- `CC-T0005`: `Circle.period_eq_n_div_gcd`, the period is `n / gcd(n,k)` when `n != 0`.
- `CC-T0006`: `Circle.orbit_decomposition_count`, the stride partitions `C_n` into `gcd(n,k)` orbit classes.
- `CC-T0007`: `Circle.prime_full_coil`, every nonzero stride on a prime circle is a full coil.
- `CC-T0054`: `Circle.fullCoil_iff_coprime`, for nonzero `n`, a stride is a full coil exactly when it is coprime to `n`.
- `CC-T0055`: `Circle.sameOrbit_iff_difference_mem_orbitSubgroup`, same-orbit quotient equality is exactly membership of the node difference in the stride-generated subgroup.
- `CC-T0059`: `Circle.sameOrbit_nat_modEq_gcd_of_sameOrbit`, same-orbit natural representatives are congruent modulo `gcd(n,k)`.
- `CC-T0060`: `Circle.sameOrbit_of_nat_modEq_gcd`, gcd-congruent natural representatives lie in the same stride-orbit quotient.
- `CC-T0061`: `Circle.sameOrbit_nat_iff_modEq_gcd`, same-orbit natural representatives are exactly the representatives congruent modulo `gcd(n,k)`.

All twelve theorem ids are registered in `manifests/theorem_manifest.yaml`, checked by Lean, and linked through the paper manifest.

## Source Trail

The detailed prose proof sketches live in `papers/PAPER_01_FINITE_CIRCLES.md`.

The Lean sidecars are:

```text
sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean
sidecars/PAPER_S1_01_FINITE_CIRCLES/lean/PaperS101.lean
```

`Paper01.lean` carries the root paper checks, and `PaperS101.lean` re-exports the declarations from the dimension layout. The Python examples live in:

```text
sidecars/PAPER_01_FINITE_CIRCLES/python/test_paper_01_examples.py
```

Those examples demonstrate finite orbits such as `C_13` with stride `5` and composite decompositions such as `C_12` with stride `4`. They are useful executable support, but the proof status comes only from the Lean declarations.

## Why This Matters Later

The `S^1` finite circle layer feeds the whole project:

- `S^2` latitude rings reuse `C_n` behavior.
- `S^3` Hopf phase laws depend on circle-like phase action.
- Scaling and factor papers use the period and orbit decomposition spine.
- Proof-carrying glyphs for modular diagrams start from finite circle theorems.
- Compute and AI applications reuse cyclic addresses, periods, and closure laws as safe finite primitives.

## Continuum Bridge

A finite circle is not only an analogy for the real circle — it embeds into it. Using
mathlib's homomorphism `ZMod.toAddCircle` (`j mod n ↦ j / n mod 1`) into the real circle
`UnitAddCircle = ℝ / ℤ`, the following are Lean-proved:

- `S1C-T0001`: `Circle.S1.finiteCircle_toRealCircle_add` — the embedding turns rotation in `C n` into rotation of the real circle (it is a group homomorphism).
- `S1C-T0002`: `Circle.S1.finiteCircle_toRealCircle_zero` — the base node maps to the base point.
- `S1C-T0003`: `Circle.S1.finiteCircle_toRealCircle_injective` — `C n` embeds faithfully: distinct nodes hit distinct real-circle points.
- `S1C-T0004`: `Circle.S1.finiteCircle_toRealCircle_inj` — nodes coincide on the real circle iff equal in `C n`.
- `S1C-T0005`: `Circle.S1.finiteCircle_lands_in_torsion` — the image lies in the `n`-torsion (the `n`-th roots of unity).
- `S1C-T0006`: `Circle.S1.finiteCircle_refines` — **the continuum-limit spine**: node `k` of `C n` is the same real-circle point as node `k*d` of `C (n*d)`, so the finite circles nest into a directed family `C₁ ⊆ C₂ ⊆ C₆ ⊆ …` filling the rational points `ℚ/ℤ ⊆ ℝ/ℤ`.

This makes precise the sense in which the finite circles *approximate* the real circle: each `C n` is a genuine finite subgroup, and refinement nests them toward `ℝ / ℤ`.

**Roadmap (not yet claimed).** That the union of all finite circles is *dense* in the real
circle, and that the real circle is its metric completion, are tracked rather than
asserted; they use the topology of `AddCircle` and are the next step.

## Guardrails

Beyond the continuum bridge above (which lands in the actual real circle `ℝ / ℤ` and is
explicit about what remains roadmap), this paper proves finite modular recurrence, not
smooth-circle analysis, Fourier theory, Lie-group, or full topology results. Diagrams can
explain a theorem, but they are not the theorem.

## Next Step

`S1.2` lifts finite circle motion into winding/residue coordinates so completed turns are no longer forgotten. That is the bridge from pure cyclic address spaces to natural-number arithmetic.
