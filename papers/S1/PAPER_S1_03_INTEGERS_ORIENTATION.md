# Circle Calculus S1.3: Integers, Orientation, and Reversible Motion

Status: draft scaffold with the signed-rotation theorem spine proved.

## Aim

This paper extends finite-circle motion from natural strides to oriented, reversible signed strides.

## Target Spine

- `S1O-T0001`: `Circle.S1.signedRot_zero`
- `S1O-T0002`: `Circle.S1.signedRot_comp`
- `S1O-T0003`: `Circle.S1.signedRot_inverse`

## Model

Signed rotation is the integer-stride version of finite-circle rotation:

```text
Circle.S1.signedRot n k x = x + (k : ZMod n)
```

Positive and negative integers represent the two orientations of motion on the same finite circle `C_n`.

## Proved Core

`S1O-T0001` is proved by `Circle.S1.signedRot_zero`: signed rotation by `0` fixes every node.

`S1O-T0002` is proved by `Circle.S1.signedRot_comp`: composing signed rotations adds signed strides.

`S1O-T0003` is proved by `Circle.S1.signedRot_inverse`: moving by `k` and then by `-k` returns to the starting node.

The Python sidecar checks the same signed finite-circle examples for zero stride, composition by adding signed strides, and inverse motion. These examples support the paper but do not replace the Lean theorem spine.

## Dictionary Targets

- `S1-0002`: signed rotation
- `S1-0003`: reversible signed motion

## Notes

This paper should keep the existing `S^1` finite core green. It should not import higher-dimensional modules.
