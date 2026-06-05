# Circle Calculus S0.1: Two-Point Opposition

Status: polished draft with the two finite opposition facts Lean-proved and Python examples linked.

## Aim

This paper fixes the bottom object in the dimensional ladder: `S^0` is a two-point opposition object, not the one-node circle `C_1`.

That distinction is small but important. Circle Calculus uses finite cyclic address spaces heavily, and `C_1` is a valid degenerate cyclic address object. It is not the same thing as `S^0`. The zero-sphere is the minimal opposition pair: two points with an antipode map that swaps them.

## Model

The Lean model is deliberately finite:

```text
Sign = neg | pos
```

The antipode is the flip:

```text
antipode(neg) = pos
antipode(pos) = neg
```

There is no hidden geometry here. This is not a metric sphere, a smooth manifold, or a degenerate circle. It is the two-point combinatorial base object used by the later sphere notation.

## Target Spine

- `S0-T0001`: `Circle.S0.card_sign`
- `S0-T0002`: `Circle.S0.antipode_involutive`
- `S0-W0001`: `C_1` is not `S^0`

## Proved Core

`S0-T0001` is proved by `Circle.S0.card_sign`: the finite `S^0` sign model has exactly two points.

`S0-T0002` is proved by `Circle.S0.antipode_involutive`: applying the antipode twice returns the original sign.

The Python sidecar checks the same two-point model, the antipode involution, and the guardrail that the one-node circle `C_1` is not `S^0`. These examples are executable support, not a replacement for the Lean proofs.

## Why This Is Not C1

`C_1` has one cyclic address:

```text
C_1 = {0}
```

Every rotation on `C_1` is trivial because every address is already the same address. That is useful for cyclic-address edge cases, but it does not represent opposition.

`S^0` has two points:

```text
S^0 = {neg, pos}
```

The antipode swaps them. That nontrivial swap is the structure needed for later notions of poles, antipodes, signs, and suspension endpoints.

The project therefore keeps the two objects separate:

- `C_1`: a one-node cyclic address space.
- `S^0`: a two-point opposition sphere.

## Dependency Role

This paper supports later dimensions in three ways.

First, it gives the geometric ladder a real base object. When the project writes `S^0 -> S^1 -> S^2`, `S^0` means a two-point opposition pair.

Second, it provides the simplest antipode example. Later antipode constructions on suspended circles and sphere grids should be read as higher-dimensional analogs of this two-point flip, not as rotations on a one-node circle.

Third, it prevents notation drift. Without `S0-W0001`, a reader could collapse the base sphere into the degenerate cyclic object and then misread later suspension models.

## Dictionary Targets

- `S0-0001`: two-point opposition
- `S0-0002`: S0 antipode
- `S0-W0001`: C1 is not S0 warning

## Guardrails

This paper does not prove a general theory of antipodal maps. It proves a finite two-point model and its involution. Continuous antipodal geometry belongs to later papers only when the needed formal model exists.

The warning `S0-W0001` remains active because confusing `S^0` with `C_1` would break the dimension-indexed vocabulary from the start.
