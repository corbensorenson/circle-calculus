# Circle Calculus S456.1: General Suspension and Euler Parity

Status: polished draft with the common suspension/Euler spine and the `S^4` through `S^6` parity theorem Lean-proved.

## Aim

This paper proves the finite suspension Euler parity bridge across `S^4`, `S^5`, and `S^6`.

The point of this bridge is organizational as well as mathematical. Circle Calculus should not jump directly from the algebraically special `S^3` to the algebraically special `S^7`. The geometric ladder needs the intermediate dimensions, even when those dimensions do not carry the same simple multiplication story.

## Common Finite Suspension

The shared input is a finite cell-count list:

```text
[c_0, c_1, ..., c_d]
```

Its Euler characteristic is the alternating sum:

```text
chi = c_0 - c_1 + c_2 - ...
```

The finite suspension transform adds two poles and cones each cell dimension into the next:

```text
Susp([c_0, c_1, ..., c_d])
```

The proved suspension law is:

```text
chi(Susp(K)) = 2 - chi(K)
```

This formula is the whole engine behind the even/odd sphere Euler parity in the finite-count model.

## Target Spine

- `COMMON-T0001`: `Circle.Common.eulerCharacteristic`
- `COMMON-T0002`: `Circle.Common.suspensionCounts`
- `COMMON-T0003`: `Circle.Common.suspensionEuler`
- `S456-T0001`: `Circle.S4.iteratedSuspensionEulerParity`

## Proved Common Core

`COMMON-T0001` is represented by `Circle.Common.eulerCharacteristic`, the finite alternating-sum operation.

`COMMON-T0002` is represented by `Circle.Common.suspensionCounts`, the finite suspension count transform.

`COMMON-T0003` is proved by `Circle.Common.suspensionEuler`: for every finite cell-count list, suspension changes Euler characteristic by `2 - chi`.

These are finite combinatorial facts. They do not assert smooth realization, homeomorphism classification, or stable homotopy.

## Proved S4-S6 Parity

`S456-T0001` is proved by `Circle.S4.iteratedSuspensionEulerParity`.

Starting from the finite `S^3` suspension model with Euler characteristic `0`, the next three suspensions have Euler characteristics:

```text
chi(S4) = 2
chi(S5) = 0
chi(S6) = 2
```

This is the finite-count version of the parity pattern:

```text
chi(S^d) = 1 + (-1)^d
```

for the dimensions currently in this bridge.

The Python sidecar checks the same common suspension-Euler formula and the `S^4`, `S^5`, `S^6` parity pattern on finite suspended-circle examples.

## Why The Bridge Matters

The bridge gives `S^4`, `S^5`, and `S^6` honest positions in the corpus:

- `S^4` becomes the finite base dimension needed for the quaternionic Hopf roadmap.
- `S^5` stays visible near future projective and bundle work.
- `S^6` records the correct Euler parity while carrying explicit warnings before octonionic `S^7`.

The paper therefore keeps the dimensional ladder continuous without overclaiming algebraic structure.

## Dictionary Targets

- `COMMON-0001`: finite cell-count list
- `COMMON-0002`: Euler characteristic
- `COMMON-0003`: suspension cell-count transform
- `S456-0001`: iterated suspension Euler parity

## Guardrails

This paper proves finite count and Euler facts only. It does not prove smooth sphere topology, projective geometry, Hopf fibrations, characteristic classes, stable homotopy, or a complex structure on `S^6`.

Every stronger geometric claim remains future work until it has its own model, theorem ids, Lean declarations, sidecars, and checks.
