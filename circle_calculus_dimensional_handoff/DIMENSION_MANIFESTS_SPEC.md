# Dimension Manifest Specification

## Manifest location

Use one manifest per dimension:

```text
manifests/dimensions/S1_circle.yaml
manifests/dimensions/S2_sphere.yaml
manifests/dimensions/S3_hypersphere.yaml
...
```

A master index points to them:

```text
manifests/dimensions/dimension_index.yaml
```

## Dimension index schema

```yaml
dimensions:
  - id: S1
    display_name: "Circle"
    sphere_notation: "S^1"
    role: "finite cyclic address core"
    status: active
    lean_namespace: "CircleMath.S1"
    lean_root: "Circle/S1"
    python_root: "circle_math/dimensions"
    paper_root: "papers/S1"
    theorem_manifest: "manifests/dimensions/S1_circle.yaml"
    dictionary_file: "dictionary/dimensions/S1.yaml"
    allowed_import_dimensions: ["Common", "S0"]
    forbidden_import_dimensions: ["S2", "S3", "S4", "S5", "S6", "S7", "Future"]
```

## Theorem id convention

Keep existing S¹ theorem ids if they already exist.

For new dimensions, use dimension prefixes:

```text
S0-T0001
S2-T0001
S3C-T0001   # S3 combinatorial/topological
S3Q-T0001   # S3 quaternion
S3H-T0001   # S3 Hopf
S4-T0001
S5-T0001
S6-T0001
S7C-T0001   # S7 combinatorial/topological
S7QH-T0001  # S7 quaternionic Hopf
S7O-T0001   # S7 octonion
S15-T0001   # future
```

## Theorem manifest entry

```yaml
theorems:
  - id: S2-T0001
    dimension: S2
    track: combinatorial
    name: suspended_circle_euler_characteristic
    status: planned
    lean_name: CircleMath.S2.suspendedCircle_chi
    informal_statement: "The suspended finite circle has Euler characteristic 2."
    formal_statement: "∀ n ≥ 3, χ(SuspC n) = 2"
    dictionary_dependencies:
      - S2-0001
      - S2-0002
      - COMMON-0001
    paper_refs:
      - papers/S2/PAPER_S2_01_SUSPENDED_CIRCLES.md#main-theorems
    imports_allowed:
      - Common
      - S1
    verification:
      lean_build_required: true
      no_sorry_required: true
      python_property_tests:
        - "sphere_grid Euler count examples"
    blocker: ""
```

## Status values

Use exactly:

```text
planned
exploratory_python
lean_stated
lean_proved
paper_draft
paper_complete
blocked
deferred
```

Rules:

- `lean_proved` requires compiled Lean theorem.
- `paper_complete` requires all formal theorem dependencies to be `lean_proved`.
- `exploratory_python` is not proof.
- `blocked` requires a blocker field.
- `deferred` is for long-horizon topics not currently pursued.

## Dimension check scripts

### check_dimension_index.py

Must verify:

- every dimension id is unique,
- every manifest path exists,
- every dictionary file exists,
- every Lean root exists or is intentionally marked future,
- allowed and forbidden imports are consistent.

### check_dimension_imports.py

Must verify:

- no Lean file in S1 imports S2/S3/S4/S5/S6/S7/Future,
- no Lean file in S2 imports S3/S4/S5/S6/S7/Future,
- no Lean file in S3 imports S4/S5/S6/S7/Future unless file is explicitly under a future roadmap folder,
- no future/speculative file is used by a theorem marked lean_proved.

### check_dimension_manifests.py

Must verify:

- theorem ids are unique across all dimension manifests,
- every theorem has a dimension,
- every paper ref exists,
- every dictionary dependency exists,
- every theorem marked lean_proved resolves to a Lean declaration,
- no blocked/deferred theorem is cited as proven.

### check_dimension_paper_links.py

Must verify:

- every theorem id in papers exists,
- every formal claim has a theorem id or is marked background/conjecture/future,
- no paper in a lower dimension relies on a theorem from a higher dimension unless explicitly labeled as motivation.
