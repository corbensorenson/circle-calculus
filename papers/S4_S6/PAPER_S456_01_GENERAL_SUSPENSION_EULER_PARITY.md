# Circle Calculus S456.1: General Suspension and Euler Parity

Status: draft scaffold with the common suspension/Euler spine and S4-S6 parity theorem proved.

## Aim

This paper proves the finite suspension Euler parity bridge across `S^4`, `S^5`, and `S^6`.

## Target Spine

- `COMMON-T0001`: `Circle.Common.eulerCharacteristic`
- `COMMON-T0002`: `Circle.Common.suspensionCounts`
- `COMMON-T0003`: `Circle.Common.suspensionEuler`
- `S456-T0001`: `Circle.S4.iteratedSuspensionEulerParity`

## Proved Common Core

`COMMON-T0001` is represented by the Lean declaration `Circle.Common.eulerCharacteristic`.

`COMMON-T0002` is represented by the Lean declaration `Circle.Common.suspensionCounts`.

`COMMON-T0003` is proved by `Circle.Common.suspensionEuler`: for every finite cell-count list, the suspension transform changes Euler characteristic by

```text
chi(Susp(K)) = 2 - chi(K)
```

This supplies the shared algebraic step for the dimension-specific parity theorem.

## Proved S4-S6 Parity

`S456-T0001` is proved by `Circle.S4.iteratedSuspensionEulerParity`.

Starting from the finite `S^3` suspension model with Euler characteristic `0`, the next three suspensions have Euler characteristics:

```text
chi(S4) = 2
chi(S5) = 0
chi(S6) = 2
```

This is the finite-count version of the parity pattern `chi(S^d)=1+(-1)^d` for the dimensions currently in this bridge.

The Python sidecar checks the same common suspension-Euler formula and the `S^4`, `S^5`, `S^6` parity pattern on finite suspended-circle examples.

## Dictionary Targets

- `COMMON-0001`: finite cell-count list
- `COMMON-0002`: Euler characteristic
- `COMMON-0003`: suspension cell-count transform
- `S456-0001`: iterated suspension Euler parity

## Notes

This bridge keeps `S^4`, `S^5`, and `S^6` in the geometric ladder instead of skipping directly from `S^3` to `S^7`.
