# Circle Calculus Living Book Widgets

Widgets are deterministic browser-native explanation tools. They are not proofs. Their formulas should be small, auditable, and parity-checked against Python reference behavior where practical.

## Shared Constraints

- No backend server for first-milestone S1 widgets.
- No remote resource fetches at runtime.
- Plain HTML/SVG/JavaScript preferred.
- Inputs must have labels.
- Widget panels must be named regions.
- Dynamic widget output must be an `aria-live` region.
- Do not communicate status by color alone.
- SVG diagrams should expose a title, description, and visible node labels.
- Widget captions must not call output a proof.

## Shared Files

Implemented shared JavaScript:

- `site/widgets/shared/circle_math_core.js`
- `site/widgets/shared/svg_helpers.js`
- `site/widgets/shared/widget_base.js`

## S1 Widgets

### finite_circle_rotator

- Inputs: `n`, selected node `i`.
- Outputs: SVG finite circle `C_n`, highlighted node, residue label `i mod n`.
- Dictionary ids: Circle and Node entries where available.
- Validation: node reduction agrees with `circle_math` finite-circle reference behavior.

### rotation_composition

- Inputs: `n`, start `x`, stride `a`, stride `b`.
- Outputs: `rot(n,b)(x)`, `rot(n,a)(rot(n,b)(x))`, and `rot(n,a+b)(x)`.
- Theorem ids: rotation composition theorem when available in manifests.
- Validation: JavaScript formula agrees with Python rotation behavior.

### coil_orbit_explorer

- Inputs: `n`, stride `k`, start.
- Outputs: orbit sequence, visited nodes, closed-loop visualization, `gcd(n,k)`, predicted period `n/gcd(n,k)`, actual orbit length.
- Theorem ids: orbit/period theorem when available.
- Validation: orbit sequence and period agree with Python reference behavior.

### period_gcd_visualizer

- Inputs: `n`, `k`.
- Outputs: `gcd(n,k)`, number of cycles, cycle length, decomposition into `gcd(n,k)` orbits.
- Theorem ids: period/gcd theorem when available.
- Validation: gcd orbit count and cycle decomposition agree with Python reference behavior.

### prime_full_coil_explorer

- Inputs: `n`.
- Outputs: which strides `1 <= k < n` are full coils; prime/composite behavior; theorem status for prime full-coil behavior when available.
- Guardrail: do not imply primality behavior is Lean-proved unless the manifest says so.
- Validation: full-coil stride list agrees with Python reference behavior.

### winding_lift_explorer

- Inputs: base `n`, step count `t`.
- Outputs: quotient `q = t div n`, residue `r = t mod n`, lifted coordinate `(q,r)`, visual distinction between residue and winding.
- Theorem ids: winding/lift theorem ids when available.
- Guardrail: mark as planned/draft if the corresponding Lean theorem is not proved.
- Validation: quotient/residue decomposition agrees with Python reference behavior.

## Generative Widgets

### seed_rule_diagram_generator

- Inputs: selected generated artifact.
- Outputs: a generated finite-circle successor diagram or finite physics-loop plaquette diagram; seed; rules; schedule; closure condition; generated-object summary; theorem-status badges; dictionary links.
- Theorem ids: `CC-T0001`, `CC-T0002`, `PHYS-T0005`, `PHYS-T0012`, `GEN-T0017`, and `GEN-T0019`.
- Dictionary ids: finite circle/node ids plus finite gauge/generative provenance ids.
- Python references: `circle_math.generative.finite_circle_diagram_generator` and `circle_math.generative.physics_loop_diagram_generator`.
- Guardrail: the widget is generated explanation only. It displays linked proof statuses from the theorem manifest, but the diagram itself is not a proof and does not prove compression minimality or physics claims.
- Validation: deterministic JavaScript diagram formulas are parity-checked against the Python seed-rule fixtures.

## AI Widgets

### loop_recurrence_budget

- Inputs: loop period, sample/token index, maximum loops, overthinking tolerance.
- Outputs: loop phase, required loop count, token recurrence budget, capped training-free loop budget, exit availability, overthinking boundary, and one-period-shift periodicity checks.
- Theorem ids: `AIM-T0018`, `AIM-T0019`, `AIM-T0020`, and `AIM-T0021`.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0054`, `COMMON-0059`, and `COMMON-0067`.
- Python references: `circle_math.applications.circle_ai.loop_required_steps`, `circle_math.applications.circle_ai.token_recurrence_budget`, and `circle_math.applications.circle_ai.training_free_loop_budget`.
- Guardrail: the widget is finite schedule bookkeeping only. It does not prove model quality, speed, reasoning improvement, memory improvement, or context-length improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python AI recurrence helpers.

## Future Placeholders

- `site/widgets/S2/sphere_grid_placeholder.js`
- `site/widgets/S3/hopf_placeholder.js`

These should be visibly marked placeholder/exploratory until implemented and linked to checked theorem status.

The placeholder widgets are included in `site/data/generated/widget_index.json` so every mounted widget is discoverable from generated site data, even when it is scaffold-only.

## Validation Strategy

Checkers:

- `scripts/site/check_site_widget_contracts.py` verifies that every `data-widget` page mount exists in `widget_index.json`, imports the matching widget script, and points to a JavaScript file that calls `mountWidgets("<widget_id>", ...)`.
- `scripts/site/check_site_accessibility_contract.py` verifies shared widget accessibility contracts: named widget regions, labelled number inputs, live output regions, SVG title/description metadata, visible focus styling, and scaffold-only placeholder guardrails.
- `scripts/site/check_widget_python_parity.py` validates deterministic S1 formulas against Python reference behavior.
- `scripts/site/check_widget_runtime_links.py` imports the shared widget runtime under Node and verifies that real repository paths become GitHub source links while symbolic paper-section references remain plain text.

Minimum parity cases:

- node reduction;
- rotation;
- rotation composition;
- orbit sequence;
- period `n/gcd(n,k)`;
- gcd orbit count;
- winding/residue decomposition.
- finite-circle generated diagram nodes and successor edges;
- finite physics-loop generated diagram normalized phases, closed-loop flag, and holonomy.
- AI recurrence phase, required loop count, token recurrence budget, capped training-free budget, exit availability, overthinking boundary, and one-period-shift periodicity.
