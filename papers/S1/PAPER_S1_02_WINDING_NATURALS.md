# Circle Calculus S1.2: Winding, Lifted Circles, and Natural Numbers

Status: polished dimension guide draft with the winding theorem spine linked to the root Paper 2 artifacts.

## Aim

This paper is the `S^1` dimension home for winding, lifted residue coordinates, successor with carry, lifted addition, and iterated successor.

The detailed root paper remains `papers/PAPER_02_WINDING_NATURALS.md`. This dimension paper explains how winding fits into the dimensional ladder: finite circles remember address, but winding remembers how many full turns were completed before landing at that address.

## Motivation

Pure modular arithmetic forgets turns. On `C_5`, the values `2`, `7`, `12`, and `17` all have residue `2`. That is correct for cyclic position, but ordinary counting needs the missing full-turn count.

Circle Calculus calls that count winding:

```text
value = winding * modulus + residue
```

For example:

```text
17 = 3 * 5 + 2
```

The residue is the visible address on the circle. The winding is the number of completed turns. Together they recover the natural number exactly.

## Formal Model

The Lean core defines a lifted node:

```lean
structure Circle.LiftedNode where
  modulus : Nat
  winding : Nat
  residue : Nat
```

Its reconstructed value is:

```lean
def Circle.LiftedNode.value (x : Circle.LiftedNode) : Nat :=
  x.winding * x.modulus + x.residue
```

The canonical decomposition uses ordinary Euclidean division:

```lean
def Circle.liftWinding (modulus value : Nat) : Nat := value / modulus
def Circle.liftResidue (modulus value : Nat) : Nat := value % modulus
```

The project vocabulary is circle-first, but the formal theorem spine is intentionally standard: quotient, remainder, carry, and reconstruction.

## Theorem Spine

- `CC-T0009`: `Circle.lift_unique`, bounded winding/residue decompositions are unique.
- `CC-T0010`: `Circle.lift_add_decomposition`, lifted addition reconstructs `left + right` and keeps residue bounded.
- `CC-T0011`: `Circle.lift_exists`, every value has the canonical winding/residue decomposition for positive modulus.
- `CC-T0012`: `Circle.lift_successor_decomposition`, successor advances the lifted value by one with the correct carry.
- `CC-T0013`: `Circle.lift_add_zero_right`, adding zero on the right preserves lifted components.
- `CC-T0014`: `Circle.lift_add_assoc_value`, lifted addition is associative at the reconstructed-value level.
- `CC-T0015`: `Circle.lift_add_zero_left`, adding zero on the left preserves lifted components.
- `CC-T0016`: `Circle.lift_iter_successor_decomposition`, repeated successor reconstructs `value + steps` and keeps residue bounded.

All eight theorem ids are registered in `manifests/theorem_manifest.yaml`, checked by Lean, and linked through the paper manifest.

## Source Trail

The detailed prose proof sketches live in `papers/PAPER_02_WINDING_NATURALS.md`.

The Lean sidecars are:

```text
sidecars/PAPER_02_WINDING_NATURALS/lean/Paper02.lean
sidecars/PAPER_S1_02_WINDING_NATURALS/lean/PaperS102.lean
```

`Paper02.lean` carries the root paper checks, and `PaperS102.lean` re-exports the declarations from the dimension layout. The Python examples live in:

```text
sidecars/PAPER_02_WINDING_NATURALS/python/test_paper_02_examples.py
```

The examples check canonical lift, successor with carry, lifted addition, zero identities, and iterated successor behavior. They are executable support; the proof status still comes from Lean.

## Relation To The Circle Core

`S1.1` proves how to move on a finite circle after reducing to a residue. `S1.2` adds the information needed to count without losing completed turns.

The two layers should not be collapsed:

- `C_n` position is residue-level information.
- Winding is quotient-level information.
- A lifted node is a certified reconstruction of both.

This distinction matters later when scaling, kernels, fibers, integer orientation, and provenance all need to know whether a result is purely cyclic or lifted from a longer path.

## Guardrails

This paper does not prove multiplication, signed integer arithmetic, factor lattices, or continuous covering maps. It proves the natural-number lift that makes those later papers possible.

The winding model is also not a claim that every periodic dataset has a discovered period. It is a finite arithmetic representation for a fixed positive modulus.

## Next Step

`S1.3` adds signed orientation so motion can run forward and backward. `S1.4` then uses the circle and winding spine to formalize scaling, factors, images, kernels, and fibers.
