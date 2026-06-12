# Dimension-Organized Repository Plan

## Principle

The repository should be organized so that each sphere dimension has:

- its own Lean namespace,
- its own theorem manifest,
- its own dictionary additions,
- its own paper folder,
- its own Python exploratory module,
- its own proof status.

The current S¹ work is the foundation. Do not let future S²/S³/S⁷ concepts leak backward into the S¹ core.

## Namespace convention

Use:

```lean
namespace CircleMath

namespace S0
namespace S1
namespace S2
namespace S3
namespace S4
namespace S5
namespace S6
namespace S7

end CircleMath
```

If the existing project already uses another namespace, preserve it and add aliases or import shims instead of breaking existing files.

## Recommended Lean layout

```text
Circle/
  Common/
    FiniteCellCount.lean
    EulerCharacteristic.lean
    SuspensionCount.lean
    DimensionIndex.lean

  S0/
    Opposition.lean
    BoundaryInterval.lean

  S1/
    Core/
      FiniteCircle.lean
      Rotation.lean
      Coil.lean
      Period.lean
      Prime.lean
      Scaling.lean
      Winding.lean
    PaperBindings.lean

  S2/
    Combinatorial/
      SuspendedCircle.lean
      SphereGrid.lean
      Euler.lean
      LatitudeRings.lean
      PoleCollapse.lean
    PaperBindings.lean

  S3/
    Combinatorial/
      SuspendedSphere.lean
      Euler.lean
    Quaternion/
      Basic.lean
      Unit.lean
      Rotation.lean
      Noncommutative.lean
    Hopf/
      ComplexPair.lean
      HopfMap.lean
      PhaseInvariance.lean
    PaperBindings.lean

  S4/
    Combinatorial/
      SuspensionModel.lean
      Euler.lean

  S5/
    Combinatorial/
      SuspensionModel.lean
      ProjectiveBridge.lean

  S6/
    Combinatorial/
      SuspensionModel.lean
      OctonionShadow.lean
      Warnings.lean

  S7/
    Combinatorial/
      SuspensionModel.lean
      Euler.lean
    QuaternionicHopf/
      Planned.lean
    Octonion/
      BasicExploratory.lean
      UnitExploratory.lean
      NonAssociativeExploratory.lean

  Future/
    S15/
      OctonionicHopfRoadmap.lean
```

## Compatibility shims

If the current S¹ core already lives under:

```text
Circle/Core/
```

then do not immediately move it. Instead, after S¹ is green:

```text
Circle/Core/Rotation.lean
```

may become a shim:

```lean
import Circle.S1.Core.Rotation
```

Only do this when CI is green before and after the move.

## Recommended Python layout

```text
circle_math/
  dimensions/
    __init__.py
    common.py
    suspension.py
    finite_cell_count.py
    sphere_grid.py
    hypersphere.py
    quaternion.py
    hopf.py
    octonion.py

tests/
  dimensions/
    test_suspension_counts.py
    test_sphere_grid.py
    test_hypersphere_counts.py
    test_quaternion.py
    test_hopf.py
    test_octonion_exploratory.py
```

## Recommended paper layout

```text
papers/
  S1/
    PAPER_S1_01_FINITE_CIRCLES.md
    PAPER_S1_02_WINDING_NATURALS.md
    PAPER_S1_03_INTEGERS_ORIENTATION.md
    PAPER_S1_04_FACTORS_PRIME_COILS.md

  S2/
    PAPER_S2_01_SUSPENDED_CIRCLES.md
    PAPER_S2_02_SPHERE_GRIDS_LATITUDE_COILS.md
    PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE.md

  S3/
    PAPER_S3_01_FINITE_HYPERSPHERES.md
    PAPER_S3_02_QUATERNION_COILS.md
    PAPER_S3_03_HOPF_COILS.md
    PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md

  S4_S6/
    PAPER_S456_01_GENERAL_SUSPENSION_EULER_PARITY.md
    PAPER_S4_01_BASE_OF_QUATERNIONIC_HOPF.md
    PAPER_S5_01_COMPLEX_PROJECTIVE_BRIDGE.md
    PAPER_S6_01_OCTONION_SHADOW_AND_WARNINGS.md

  S7/
    PAPER_S7_01_TOPOLOGICAL_7SPHERE.md
    PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md
    PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md

  future/
    PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP.md
```

## Import direction rule

Higher dimensions may depend on lower dimensions.

Lower dimensions must not depend on higher dimensions.

Allowed import direction:

```text
Common → S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7 → Future/S15
```

This is a dependency direction, not a claim that all mathematical meaning is linear.
