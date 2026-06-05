# Circle Calculus S1.3: Integers, Orientation, and Reversible Motion

Status: polished draft with the signed-rotation theorem spine Lean-proved and Python examples linked.

## Aim

This paper extends finite-circle motion from natural-number strides to signed, reversible integer strides.

The earlier `S1.1` circle core proves rotation by natural strides. The `S1.2` winding paper lifts natural-number motion into quotient/remainder coordinates. This paper adds the missing orientation layer: motion can now go forward or backward around the same finite circle.

## Model

Signed rotation is the integer-stride version of finite-circle rotation:

```text
Circle.S1.signedRot n k x = x + (k : ZMod n)
```

Positive and negative integers represent the two orientations of motion on the same finite circle `C_n`.

The model is still finite and modular. A negative stride does not require a new object; it is interpreted by coercion into `ZMod n`, where additive inverses already exist.

## Target Spine

- `S1O-T0001`: `Circle.S1.signedRot_zero`
- `S1O-T0002`: `Circle.S1.signedRot_comp`
- `S1O-T0003`: `Circle.S1.signedRot_inverse`

## Proved Core

`S1O-T0001` is proved by `Circle.S1.signedRot_zero`: signed rotation by `0` fixes every node.

`S1O-T0002` is proved by `Circle.S1.signedRot_comp`: composing signed rotations adds signed strides.

`S1O-T0003` is proved by `Circle.S1.signedRot_inverse`: moving by `k` and then by `-k` returns to the starting node.

The Python sidecar checks the same signed finite-circle examples for zero stride, composition by adding signed strides, and inverse motion. These examples support the paper but do not replace the Lean theorem spine.

## Interpretation

The important shift is from one-way counting to reversible motion.

In natural-stride rotation, a stride is a nonnegative number of steps. In signed rotation, a stride carries direction:

```text
k  = move forward k steps
-k = move backward k steps
```

On a finite circle, both are still just address changes modulo `n`. The signed notation gives the paper a clean way to discuss orientation without changing the underlying finite address space.

## Why This Matters

The signed-rotation layer is the first bridge from finite cyclic arithmetic toward integer-like behavior.

It supports later work in several ways:

- Reversible motion is needed before orientation can be treated as first-class.
- Inverse steps are needed for proof-carrying diagrams that show undo/redo paths.
- Signed strides make it easier to state symmetry and reflection facts.
- Later quaternion and spin papers reuse the idea that changing direction or sign can preserve a structured action.

This paper is intentionally narrow. It does not yet build a full signed winding object or prove all integer arithmetic. It proves the group-action facts needed for reversible motion on `C_n`.

## Dictionary Targets

- `S1-0002`: signed rotation
- `S1-0003`: reversible signed motion

## Guardrails

This paper should keep the existing `S^1` finite core green. It must not import higher-dimensional modules, and it must not smuggle in continuous orientation or smooth geometry.

All claims are finite `ZMod n` claims. Diagrams may show clockwise and counterclockwise motion, but the proof is the Lean algebra of signed rotation.

## Next Step

The next `S^1` paper, `S1.4`, uses the finite-circle and orientation spine to study scaling, factors, images, kernels, and fibers. Those results are where multiplication-like structure starts to interact with circle traversal.
