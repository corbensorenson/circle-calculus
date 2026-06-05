# Circle Calculus S1.4: Factors, Scaling, and Prime Coils

Status: draft with the first scaling theorem spine proved.

## Aim

This paper will connect multiplication, scaling, factors, invertibility, and prime-circle behavior inside `S^1`.

## Target Spine

- `CC-T0008`: `Circle.scale_invertible_iff_coprime`
- `CC-T0017`: `Circle.scale_one`
- `CC-T0018`: `Circle.scale_comp`
- `CC-T0019`: `Circle.scale_rot`
- `CC-T0020`: `Circle.scale_coilStep`
- multiplication as repeated rotation or scaling
- scaling invertibility iff coprime
- factor structure through orbit decomposition
- prime rings as full-cycle systems

## Proved Core

`CC-T0017` is proved by `Circle.scale_one`: scaling by one is the identity map on every finite circle.

`CC-T0018` is proved by `Circle.scale_comp`: scaling by `b` and then scaling by `a` is the same as scaling once by `a*b`.

`CC-T0019` is proved by `Circle.scale_rot`: scaling transports rotation/coils by multiplying the stride. Scaling a node after one stride step is the same as scaling the node first and then rotating by the scaled stride.

`CC-T0020` is proved by `Circle.scale_coilStep`: scaling transports any finite coil step to the corresponding coil step with both start and stride scaled.

Together these theorems make scaling into a checked multiplicative action on finite-circle addresses and finite coil steps:

```text
scale(n,1)(x) = x
scale(n,a)(scale(n,b)(x)) = scale(n,a*b)(x)
scale(n,k)(rot(n,stride)(x)) = rot(n,k*stride)(scale(n,k)(x))
scale(n,k)(coil_step(n,stride,start,steps))
  = coil_step(n,k*stride,k*start,steps)
```

`CC-T0008` is proved by `Circle.scale_invertible_iff_coprime`.

For every modulus `n` and multiplier `k`, the scaling map

```text
scale(n,k)(x) = k*x in C_n
```

is a bijection exactly when `Nat.Coprime n k`. In ordinary gcd language, scaling is reversible exactly when `gcd(n,k)=1`.

The Lean proof reduces scaling to left multiplication by `(k : ZMod n)`. Mathlib then supplies the two standard bridges:

- left multiplication is bijective exactly when the multiplier is a unit;
- `(k : ZMod n)` is a unit exactly when `k` is coprime to `n`.

## Dictionary Targets

- `S1-0001`: S1 finite circle core
- `CC-0105`: Scaling
- new factor entries as the proof model matures

## Notes

The remaining factor-structure targets should build on `CC-T0008`, `CC-T0017`, `CC-T0018`, `CC-T0019`, and `CC-T0020` without claiming more than the current finite-circle model proves.
