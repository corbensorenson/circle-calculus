# Circle Calculus S7.1: Topological 7-Sphere by Iterated Suspension

Status: polished draft with the finite topological `S^7` theorem spine Lean-proved.

## Aim

This paper separates the topological/combinatorial `S^7` layer from the octonion algebra layer. In the Circle Calculus roadmap, `S^7` matters for two different reasons: it is the next odd sphere in the suspension ladder, and it is the dimension where octonion unit coordinates become relevant. Those are related in the long view, but they should not be conflated.

The purpose here is the safe first part: construct a finite `S^7` count model by suspension and prove its Euler characteristic. Octonion multiplication, nonassociativity, and octonionic Hopf ambitions are left to later papers.

## Model

The finite `S^7` model is one suspension above the finite `S^6` count model:

```text
Circle.S7.iteratedSuspensionModel n =
  Circle.Common.suspensionCounts (Circle.S6.counts n)
```

This mirrors the earlier `S^2`, `S^3`, and `S^4` through `S^6` construction pattern: each new topological sphere model is introduced through a controlled finite suspension step, and Euler parity is checked rather than assumed.

## Theorem Spine

- `S7C-T0001`: `Circle.S7.iteratedSuspensionModel`
- `S7C-T0002`: `Circle.S7.eulerCharacteristic`
- `S7C-T0003`: `Circle.S7.iteratedSuspensionModel_eq_suspension_s6`

## Proved Core

`S7C-T0001` registers the model itself. `S7C-T0003` proves that the registered model is exactly the suspension of the finite `S^6` counts, so the `S^7` paper does not silently introduce a disconnected cell-count convention.

`S7C-T0002` proves the Euler characteristic:

```text
chi(Circle.S7.iteratedSuspensionModel n) = 0
```

for every natural `n`. This is the expected odd-sphere parity and it fits the common suspension theorem used by the `S^4` through `S^6` bridge.

The Python sidecar checks the same suspension-from-`S^6` count definition and verifies Euler characteristic `0` across finite examples. These executable examples support the paper, but the proof status comes from the Lean declarations listed in the manifest.

## Role In The Ladder

This paper is the gate between the general suspension track and the exceptional algebra track:

- before it, `S^4`, `S^5`, and `S^6` establish that the project did not jump from `S^3` to `S^7`;
- after it, the quaternionic Hopf and octonion papers can use `S^7` as a dimension with a proved finite topological anchor;
- beyond it, the future `S^15` paper can build an eightfold-suspension horizon without claiming a false infinite Hopf pattern.

## Dictionary Targets

- `S7C-0001`: topological S7 suspension model
- `S456-0001`: iterated suspension Euler parity

## Guardrails

This paper proves a finite combinatorial suspension model and its Euler characteristic. It does not prove a smooth sphere theorem, an octonion multiplication theorem, a Lie group structure, or an octonionic Hopf fibration. Those claims require their own models, theorem ids, sidecars, and checks.
