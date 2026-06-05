# Paper 2 - Circle Calculus II: Winding, Lifted Circles, and Natural Numbers

## Abstract

Finite circles remember position but forget completed turns. This paper introduces winding as the first lift out of pure modular arithmetic. A lifted node `CC-0301` records a modulus, a winding count, and a residue, representing an ordinary natural number as full rotations plus a final address. The first formal results establish existence and uniqueness of winding/residue decomposition, define successor with carry `CC-0302`, model addition as lifted path concatenation `CC-0303`, and represent induction as iterated lifted successor `CC-0304`.

## Status

- Dictionary version: `dictionary/circle_dictionary.yaml`
- Manifest version: `manifests/theorem_manifest.yaml`
- Lean sidecar: `sidecars/PAPER_02_WINDING_NATURALS/lean/Paper02.lean`
- Python sidecar: `sidecars/PAPER_02_WINDING_NATURALS/python/test_paper_02_examples.py`
- Theorem ids proved in Lean: `CC-T0009`, `CC-T0010`, `CC-T0011`, `CC-T0012`, `CC-T0013`, `CC-T0014`, `CC-T0015`, `CC-T0016`
- Theorem ids deferred or planned: none for the current Paper 2 minimum theorem set

## 1. Motivation

On `C_n`, positions wrap around. That is useful for recurrence, but ordinary counting needs to remember how many complete turns have happened. Winding stores that lost information. For example, `17` steps around `C_5` is `3` full turns plus residue `2`.

## 2. Dictionary Additions

| Dictionary id | Term | Role |
|---|---|---|
| `CC-0301` | Winding | Full-turn count plus residue |
| `CC-0302` | Successor With Carry | Unit residue motion plus winding carry |
| `CC-0303` | Lifted Addition | Path concatenation with residue carry |
| `CC-0304` | Iterated Lifted Successor | Repeated unit steps / induction |

## 3. Formal Definitions

The Lean core defines:

```lean
structure Circle.LiftedNode where
  modulus : Nat
  winding : Nat
  residue : Nat
```

The value interpretation is:

```lean
def Circle.LiftedNode.value (x : Circle.LiftedNode) : Nat :=
  x.winding * x.modulus + x.residue
```

The canonical winding and residue functions are:

```lean
def Circle.liftWinding (modulus value : Nat) : Nat := value / modulus
def Circle.liftResidue (modulus value : Nat) : Nat := value % modulus
```

Successor with carry is represented by:

```lean
def Circle.liftSuccCarry (modulus value : Nat) : Nat :=
  (Circle.liftResidue modulus value + 1) / modulus

def Circle.liftSuccWinding (modulus value : Nat) : Nat :=
  Circle.liftWinding modulus value + Circle.liftSuccCarry modulus value

def Circle.liftSuccResidue (modulus value : Nat) : Nat :=
  (Circle.liftResidue modulus value + 1) % modulus
```

Lifted addition is represented by:

```lean
def Circle.liftAddCarry (modulus left right : Nat) : Nat :=
  (Circle.liftResidue modulus left + Circle.liftResidue modulus right) / modulus

def Circle.liftAddWinding (modulus left right : Nat) : Nat :=
  Circle.liftWinding modulus left + Circle.liftWinding modulus right +
    Circle.liftAddCarry modulus left right

def Circle.liftAddResidue (modulus left right : Nat) : Nat :=
  (Circle.liftResidue modulus left + Circle.liftResidue modulus right) % modulus
```

Iterated lifted successor is represented by a recursive transition on `(winding, residue)` pairs:

```lean
def Circle.liftSuccPair (modulus : Nat) (state : Nat × Nat) : Nat × Nat
def Circle.liftIterSuccPair (modulus steps : Nat) (state : Nat × Nat) : Nat × Nat
```

## 4. Main Theorems

| Theorem id | Lean name | Statement | Status |
|---|---|---|---|
| `CC-T0009` | `Circle.lift_unique` | If `value = winding*modulus + residue`, `modulus != 0`, and `residue < modulus`, then winding and residue are the canonical quotient and remainder. | `proved` |
| `CC-T0010` | `Circle.lift_add_decomposition` | Lifted addition reconstructs `left + right` and keeps residue bounded. | `proved` |
| `CC-T0011` | `Circle.lift_exists` | For `modulus != 0`, the canonical quotient and remainder reconstruct the value and produce a bounded residue. | `proved` |
| `CC-T0012` | `Circle.lift_successor_decomposition` | Successor increments the lifted value by one while keeping the residue bounded through carry. | `proved` |
| `CC-T0013` | `Circle.lift_add_zero_right` | Adding zero on the right preserves the lifted winding and residue. | `proved` |
| `CC-T0014` | `Circle.lift_add_assoc_value` | Lifted addition is associative at the reconstructed-value level. | `proved` |
| `CC-T0015` | `Circle.lift_add_zero_left` | Adding zero on the left preserves the lifted winding and residue. | `proved` |
| `CC-T0016` | `Circle.lift_iter_successor_decomposition` | Repeated lifted successor reconstructs `value + steps` and keeps residue bounded. | `proved` |

## 5. Proof Sketches

`CC-T0011` is the existence half of Euclidean division: the canonical quotient and remainder reconstruct the original value and the remainder is smaller than the positive modulus.

`CC-T0009` is the uniqueness half specialized to the Circle Calculus winding vocabulary. Lean proves the winding component by dividing `winding*modulus + residue` by `modulus`, using `residue < modulus`. It proves the residue component by reducing the same expression modulo `modulus`.

`CC-T0012` proves successor with carry. The residue is incremented by one, then decomposed again by quotient and remainder; the quotient part is the carry into the winding.

`CC-T0010` proves addition as path concatenation. Two lifted counts are concatenated by adding full windings, adding residues, and carrying any residue overflow into the winding count.

`CC-T0013` and `CC-T0015` prove that zero is the right and left identity for lifted addition at the component level. `CC-T0014` proves associativity at the reconstructed-value level by reducing both lifted groupings to ordinary natural-number addition.

`CC-T0016` proves the induction correspondence. Starting from any valid lifted state, repeated successor preserves bounded residue and reconstructs the original value plus the number of unit steps.

## 6. Executable Examples

Python examples live in `sidecars/PAPER_02_WINDING_NATURALS/python/`. They show the intended behavior but are not formal proofs.

For `17` steps around `C_5`:

```text
winding = 3
residue = 2
value = 3*5 + 2 = 17
```

Successor has two cases:

```text
succ_lift(5,17) = lifted_node(5,3,3)
succ_lift(5,19) = lifted_node(5,4,0)
```

Addition concatenates paths:

```text
add_lift(5,17,8) = lifted_node(5,5,0)
add_lift(5,17,0) = lifted_node(5,3,2)
add_lift(5,0,17) = lifted_node(5,3,2)
iter_succ_lift(5,17,8) = lifted_node(5,5,0)
```

## 7. Translation To Standard Mathematics

The standard interpretation is Euclidean division of natural numbers. The circle address is the remainder; the winding count is the quotient.

## 8. Limitations

This paper does not yet prove multiplication or integer orientation. Multiplication is staged into the scaling/factor papers; integer orientation is staged into Paper 3.

## 9. Next Paper Dependencies

Paper 3 will depend on adding orientation to winding so that clockwise and counterclockwise motion model integer addition.
