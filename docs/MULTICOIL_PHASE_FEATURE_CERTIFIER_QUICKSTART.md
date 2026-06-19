# MultiCoil Phase Feature Certifier Quickstart

This certifier packages the finite MultiCoil phase-feature fixture as a public
Circle AI contract. It answers one narrow question:

```text
Given one or more declared periods, what phase tuple does a position have,
what is the joint repeat horizon, and does a full joint-cycle shift preserve
both the phase tuple and the relative phase used by a query/key pair?
```

It is useful for auditing phase tags, relative-position features, periodic
state labels, and recurrence schedules before treating them as model features.

Run the default fixture:

```bash
python scripts/multicoil_phase_feature_certify.py
```

The default text report should include:

```text
multicoil_phase_feature_contract=READY periods=(5, 7) position=37 phase_tuple=(2, 2) joint_repeat_horizon=35
joint_shift=shifted_position=72 shifted_phase_tuple=(2, 2) phase_invariant=True theorems=AIA-T0001,AIA-T0002,AIA-T0004
relative_phase=query_position=41 key_position=18 relative_period=5 relative_phase=3 shifted_relative_phase=3 relative_phase_invariant=True theorems=AIT-T0004,AIT-T0005
consumer_check=ready=True required_fields_present=True all_theorem_ids_proved=True missing_fields=0
```

Emit JSON for downstream tools:

```bash
python scripts/multicoil_phase_feature_certify.py --format json
python scripts/multicoil_phase_feature_certify.py --json-out /tmp/multicoil_phase_feature_contract.json
```

Try a custom period bank:

```bash
python scripts/multicoil_phase_feature_certify.py \
  --periods 4,6 \
  --position 10 \
  --query-position 17 \
  --key-position 5
```

Expected evidence fields:

| Field | Meaning |
| --- | --- |
| `periods` | Declared finite periods. |
| `position` | Position whose phase tuple is inspected. |
| `phase_tuple` | Residue of `position` in each declared period. |
| `joint_repeat_horizon` | First full shift where all declared phases repeat. |
| `shifted_position` | `position + joint_repeat_horizon`. |
| `shifted_phase_tuple` | Phase tuple after the full joint-cycle shift. |
| `relative_period` | Period used by the query/key relative-phase channel. |
| `relative_phase` | Residue of `query_position - key_position`. |
| `shifted_relative_phase` | Relative phase after shifting both query and key by the joint horizon. |

The theorem cluster is:

| Theorem id | Role |
| --- | --- |
| `AIA-T0001` | Phase channel is residue-valued. |
| `AIA-T0002` | MultiCoil phase tuples are finite products of residues. |
| `AIA-T0004` | Full joint-cycle shift preserves phase tuples. |
| `AIT-T0004` | Relative phase is stable under common shifts. |
| `AIT-T0005` | The query/key relative-phase fixture is theorem-linked. |

The generated contract pack stores the same certificate under
`multicoil_phase_feature`:

```bash
python scripts/export_circle_ai_contracts.py
python scripts/circle_ai_contract_ready.py --kind multicoil_phase_feature --digest \
  --field phase_tuple \
  --field joint_repeat_horizon \
  --field shifted_phase_tuple \
  --field relative_phase \
  --field shifted_relative_phase \
  --include-recommendations
```

The planner recommendations are:

- `PHASE-USE-JOINT-REPEAT-HORIZON`: use the declared period bank's joint repeat horizon for finite phase-tag auditing.
- `PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT`: audit the query/key relative phase under a common joint-cycle shift.

These records are finite phase-feature bookkeeping. They do not prove learned embedding quality, attention quality, extrapolation behavior, context-length improvement, or model quality.

Non-claims:

- This is finite phase bookkeeping, not a learned-position embedding theorem.
- It does not prove model quality, training stability, context-length
  improvement, transfer, deployment safety, or ASI.
- The Python report is an executable certificate surface; the formal source is
  still the Lean theorem ids resolved through the manifest.
