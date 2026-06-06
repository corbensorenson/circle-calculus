# Paper 1 - Circle Calculus I: Finite Circles, Rotations, and Coils

## Abstract

This paper introduces the finite v0 core of Circle Calculus. A circle `CC-0001` is treated as a finite cyclic address space, not a Euclidean metric object. Nodes `CC-0002` are addresses in that space, rotations `CC-0101` are additions by a stride, coils `CC-0201` are repeated rotations, closure `CC-0202` is return to the start address, and period `CC-0205` is the return time. The first formal target is a proof-carrying account of modular recurrence and prime full-coil behavior `CC-0206`.

## Status

- Dictionary version: `dictionary/circle_dictionary.yaml`
- Manifest version: `manifests/theorem_manifest.yaml`
- Lean sidecar: `sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean`
- Python sidecar: `sidecars/PAPER_01_FINITE_CIRCLES/python/test_paper_01_examples.py`
- Theorem ids proved in Lean: `CC-T0001`, `CC-T0002`, `CC-T0003`, `CC-T0004`, `CC-T0005`, `CC-T0006`, `CC-T0007`, `CC-T0054`, `CC-T0055`, `CC-T0059`, `CC-T0060`, `CC-T0061`
- Theorem ids deferred or planned: none for the current Paper 1 minimum theorem set

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean
```

The Python examples are:

```text
sidecars/PAPER_01_FINITE_CIRCLES/python/test_paper_01_examples.py
sidecars/PAPER_01_FINITE_CIRCLES/python/test_finite_coil_search_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python examples and finite-coil search fixture are executable support; Lean declarations determine proof status.

## 1. Motivation

Closed recurrence is a primitive mathematical pattern: a process moves through addresses, eventually returns, and thereby exposes divisibility, periodicity, and symmetry. Circle Calculus begins with this pattern in the smallest rigorous setting: finite cyclic address spaces. The visual circle is allowed as an interface, but the formal object is `ZMod n`.

## 2. Dictionary Additions

| Dictionary id | Term | Role |
|---|---|---|
| `CC-0001` | Circle | Finite cyclic address space |
| `CC-0002` | Node | Address in `C_n` |
| `CC-0101` | Rotation | Addition by a stride |
| `CC-0201` | Coil | Orbit of repeated rotation |
| `CC-0202` | Closure | Return condition for a coil |
| `CC-0205` | Period | Return time of a coil |
| `CC-0206` | Full Coil | Coil visiting every node before return |
| `CC-0207` | Orbit Class | Coset/cycle class under repeated stride |
| `CC-0208` | Orbit Class Count | Number of stride orbit classes |

## 3. Formal Definitions

The v0 circle `CC-0001` is modeled in Lean as:

```lean
abbrev Circle.C (n : Nat) := ZMod n
```

A rotation `CC-0101` is:

```lean
def Circle.rot (n : Nat) (k : Nat) (x : Circle.C n) : Circle.C n :=
  x + (k : ZMod n)
```

A coil step `CC-0201` is the node reached after a fixed number of repeated rotations:

```lean
def Circle.coilStep (n : Nat) (stride start steps : Nat) : Circle.C n :=
  start + steps * stride
```

Closure `CC-0202` is represented by `Circle.closesAt`. Period `CC-0205` is represented by the additive order of the stride:

```lean
def Circle.period (n k : Nat) : Nat :=
  addOrderOf (Circle.stride n k)
```

## 4. Main Theorems

| Theorem id | Lean name | Statement | Status |
|---|---|---|---|
| `CC-T0001` | `Circle.rot_zero` | Rotation by zero leaves every node unchanged. | `proved` |
| `CC-T0002` | `Circle.rot_comp` | Composing rotations adds their strides. | `proved` |
| `CC-T0003` | `Circle.rot_inverse_left` | Adding and then subtracting the same stride returns to the start. | `proved` |
| `CC-T0004` | `Circle.closesAt_iff_stride_multiple_zero` | A coil closes exactly when the stride multiple is zero in `C_n`. | `proved` |
| `CC-T0005` | `Circle.period_eq_n_div_gcd` | The period is `n/gcd(n,k)` for `n != 0`. | `proved` |
| `CC-T0006` | `Circle.orbit_decomposition_count` | The stride partitions `C_n` into `gcd(n,k)` orbit classes. | `proved` |
| `CC-T0007` | `Circle.prime_full_coil` | Every nonzero stride on a prime circle is full. | `proved` |
| `CC-T0054` | `Circle.fullCoil_iff_coprime` | A stride is a full coil exactly when it is coprime to the nonzero circle size. | `proved` |
| `CC-T0055` | `Circle.sameOrbit_iff_difference_mem_orbitSubgroup` | Two nodes are in the same stride-orbit quotient exactly when their difference lies in the stride subgroup. | `proved` |
| `CC-T0059` | `Circle.sameOrbit_nat_modEq_gcd_of_sameOrbit` | Same-orbit natural representatives are congruent modulo `gcd(n,k)`. | `proved` |
| `CC-T0060` | `Circle.sameOrbit_of_nat_modEq_gcd` | Natural representatives congruent modulo `gcd(n,k)` are in the same stride-orbit quotient. | `proved` |
| `CC-T0061` | `Circle.sameOrbit_nat_iff_modEq_gcd` | Same-orbit natural representatives are exactly the representatives congruent modulo `gcd(n,k)`. | `proved` |

## 5. Proof Sketches

`CC-T0001`, `CC-T0002`, and `CC-T0003` are algebraic facts about addition in `ZMod n`. The Lean declarations live in `Circle/Core/Rotation.lean`.

`CC-T0004` reduces the start-address equality to the zero condition on `steps * stride` in `ZMod n`. The Lean declaration lives in `Circle/Core/Coil.lean`.

`CC-T0005` is proved from mathlib's additive-order theorem for natural-number coercions into `ZMod n`. `CC-T0054` packages the exact full-coil criterion: for nonzero `n`, `period(n,k)=n` exactly when `gcd(n,k)=1`, equivalently when `n` and `k` are coprime. `CC-T0007` is the prime specialization: a positive stride below a prime modulus is coprime to that modulus.

`CC-T0006` formalizes orbit decomposition by quotienting `C_n` by the additive subgroup generated by the stride. Its proof combines Lagrange's theorem for additive subgroup quotients, the cardinality of the generated stride subgroup, and the period theorem.

`CC-T0055` exposes the same quotient boundary as a membership theorem: two nodes are in the same stride-orbit quotient exactly when their difference lies in the additive subgroup generated by the stride.

`CC-T0059` proves the first natural-representative bridge from that quotient API: if two natural representatives are already known to be in the same stride-orbit quotient, then their representatives are congruent modulo `gcd(n,k)`.

`CC-T0060` proves the reverse implication using Bezout's identity: if two representatives are congruent modulo `gcd(n,k)`, their difference can be written as an `n`-multiple plus a `k`-multiple. The `n`-multiple vanishes in `C_n`, so the difference lies in the stride subgroup.

`CC-T0061` packages the two directions: two natural representatives are in the same stride-orbit quotient exactly when they are congruent modulo `gcd(n,k)`.

## 6. Executable Examples

Python examples live in `sidecars/PAPER_01_FINITE_CIRCLES/python/`. They show the intended behavior but are not formal proofs.

For `C_13` with stride `5`, the orbit from `0` is:

```text
0 -> 5 -> 10 -> 2 -> 7 -> 12 -> 4 -> 9 -> 1 -> 6 -> 11 -> 3 -> 8
```

For `C_12` with stride `4`, the orbit from `0` is:

```text
0 -> 4 -> 8
```

The second example has period `3` and decomposes into `4` cycles.

## 6.1 Finite-Coil Signature Search Fixture

`P5-EDGE-002` adds an exploratory Python search fixture:

```text
circle_math/finite_search.py
sidecars/PAPER_01_FINITE_CIRCLES/python/test_finite_coil_search_examples.py
```

The fixture normalizes finite-circle examples to gcd, period, orbit-count, and full-coil signatures, then indexes existing theorem ids by tags such as `period`, `gcd`, `full-coil`, and `same-orbit`.

The ordinary baseline is name/type lookup over theorem declarations. Signature lookup is useful when the reader starts from a shape, for example "`C_12` with stride `4` has four cycles of period three; which theorems explain this?" It is less useful when the reader already knows the exact theorem name or needs a non-S1 theorem. This is proof navigation, not theorem discovery evidence.

## 7. Translation To Standard Mathematics

The standard interpretation is modular arithmetic. `C_n` is `ZMod n`; rotation is addition by a residue; a coil is an additive orbit; period is additive order. Circle diagrams can be rendered from these terms, but the diagram is not the proof.

## 8. Limitations

This paper does not introduce continuous circles, real angles, Euclidean geometry, topology, trigonometry, calculus, or a new foundation for all mathematics. It establishes the finite combinatorial layer needed before those later papers can be made rigorous.

## 9. Next Paper Dependencies

Paper 2 depends on preserving winding count instead of collapsing everything modulo `n`. The required next dictionary term is `CC-0301`, and the first target theorem is `CC-T0009` / `Circle.lift_unique`.
