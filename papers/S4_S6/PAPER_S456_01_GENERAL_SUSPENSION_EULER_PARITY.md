# Circle Calculus S456.1: General Suspension and Euler Parity

Status: draft scaffold with the common definitions compiled.

## Aim

This paper will prove the general finite suspension Euler parity bridge across `S^4`, `S^5`, and `S^6`.

## Target Spine

- `COMMON-T0001`: `Circle.Common.eulerCharacteristic`
- `COMMON-T0002`: `Circle.Common.suspensionCounts`
- `COMMON-T0003`: `Circle.Common.suspensionEuler`
- `S456-T0001`: iterated suspension Euler parity

## Compiled Common Core

`COMMON-T0001` is represented by the Lean declaration `Circle.Common.eulerCharacteristic`.

`COMMON-T0002` is represented by the Lean declaration `Circle.Common.suspensionCounts`.

`COMMON-T0003` remains planned. It will prove that for every finite cell-count list, the suspension transform changes Euler characteristic by

```text
chi(Susp(K)) = 2 - chi(K)
```

The current blocker is proof-engineering, not mathematics: the identity should be proved without importing the broad tactic stack.

## Dictionary Targets

- `COMMON-0001`: finite cell-count list
- `COMMON-0002`: Euler characteristic
- `COMMON-0003`: suspension cell-count transform
- `S456-0001`: iterated suspension Euler parity

## Notes

This bridge keeps `S^4`, `S^5`, and `S^6` in the geometric ladder instead of skipping directly from `S^3` to `S^7`.
