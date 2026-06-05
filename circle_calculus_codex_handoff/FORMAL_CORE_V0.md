# Formal Core v0

## Scope

v0 is finite and combinatorial. A circle is a cyclic address space, not a Euclidean object.

The core model is the additive group of integers modulo `n`.

Recommended Lean interpretation:

```lean
import Mathlib.Data.ZMod.Basic
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.Data.Nat.Prime.Basic

namespace Circle

abbrev C (n : Nat) := ZMod n

def rot (n : Nat) (k : Nat) (x : C n) : C n :=
  x + (k : ZMod n)

def stride (n : Nat) (k : Nat) : C n :=
  (k : ZMod n)

def period (n k : Nat) : Nat :=
  addOrderOf (stride n k)

end Circle
```

The project should use existing mathlib facts where possible, especially:

```lean
ZMod.addOrderOf_one
ZMod.addOrderOf_coe
IsOfFinAddOrder.addOrderOf_nsmul
```

## Definitions

### Circle

`Cₙ` is a finite cyclic address space with `n` residues.

Formal model:

```text
Cₙ := ZMod n
```

Restriction:
- v0 theorems requiring finite nondegenerate behavior should assume `n ≠ 0`.
- `C₀` in `ZMod` has special meaning and should not be used as the finite circle of zero nodes.

### Node

A node is an element of `Cₙ`.

### Rotation

A rotation by stride `k` is:

```text
rot(n,k)(x) = x + k mod n
```

### Coil

A coil is the orbit of a start node under repeated rotation:

```text
coil(n,k,start) = { start + t*k mod n | t ∈ ℕ }
```

### Closure

The coil closes at step `m` when:

```text
start + m*k ≡ start mod n
```

Equivalent:

```text
m*k ≡ 0 mod n
```

### Period

The period is the least positive closure step. In Lean, use additive order:

```text
period(n,k) = addOrderOf (k : ZMod n)
```

Expected theorem for `n ≠ 0`:

```text
period(n,k) = n / gcd(n,k)
```

### Full Coil

A full coil visits every node before returning.

Expected characterization:

```text
full_coil(n,k) ↔ gcd(n,k) = 1
```

### Prime Full-Coil Theorem

If `p` is prime and `0 < k < p`, then the stride `k` coil on `Cₚ` is full.

Expected proof route:

```text
Nat.Prime p
0 < k
k < p
=> gcd(p,k)=1
=> period(p,k)=p
=> visits all nodes
```

## v0 Theorem Targets

| ID | Lean name | Informal statement | Priority |
|---|---|---|---|
| CC-T0001 | `Circle.rot_zero` | rotation by zero is identity | P0 |
| CC-T0002 | `Circle.rot_comp` | composing rotations adds strides | P0 |
| CC-T0003 | `Circle.rot_inverse_left` | rotating by `k` then `-k` returns | P0 |
| CC-T0004 | `Circle.period_eq_n_div_gcd` | period is `n / gcd(n,k)` for `n ≠ 0` | P0 |
| CC-T0005 | `Circle.full_coil_iff_coprime` | full coil iff stride coprime to circle size | P1 |
| CC-T0006 | `Circle.prime_full_coil` | every nonzero stride on prime circle is full | P1 |
| CC-T0007 | `Circle.orbit_decomposition_count` | stride `k` partitions `Cₙ` into `gcd(n,k)` cycles | P2 |
| CC-T0008 | `Circle.scale_invertible_iff_coprime` | scaling by `k` is invertible iff `gcd(n,k)=1` | P2 |
| CC-T0009 | `Circle.lift_unique` | every natural has unique winding/residue decomposition | P1 |
| CC-T0010 | `Circle.addition_as_path_concat` | lifted path concatenation models addition | P1 |

## v0 Lean acceptance

A theorem is accepted only when:

```text
lake build
```

succeeds and the theorem is not in any fake-proof exception list.

Do not use:
- `sorry`
- `admit`
- unapproved `axiom`
- unapproved `unsafe`
- theorem statements that are tautological hacks
- definitions that bake the answer into the theorem
