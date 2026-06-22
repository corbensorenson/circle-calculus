# Recurrence Schedule Certifier Quickstart

This quickstart is the public entry point for the looped/recursive schedule
contract. It is for auditing finite schedule bookkeeping before model
experiments, not for claiming model-quality gains.

## Run

```bash
python scripts/recurrence_schedule_certify.py
python scripts/recurrence_schedule_certify.py --format json
python scripts/recurrence_schedule_certify.py --shift-passes 4 --json-out /tmp/recurrence_schedule_contract.json
python scripts/circle_ai_certify.py recurrence --period 6 --position 9 --horizon-steps 8 --sequence-length 24 --block-start 6 --block-width 6 --shift-amount 18
python scripts/circle_ai_contract_ready.py --kind recurrence_schedule --digest --field scheduled_work_saving --field post_period_multi_extension_scheduled_work_saving --include-recommendations
```

The unified runner accepts looped-transformer-friendly aliases and normalizes
them into the canonical receipt fields: `--period` is `loop_period`,
`--position` is `sample_index`, `--horizon-steps` is `max_loops`,
`--sequence-length` is `token_count`, and `--block-start`/`--block-width`
select the routed block. `--shift-amount` is accepted only when it is an exact
multiple of the loop period; the receipt records the corresponding
`periodic_shift_passes`.

For a strict downstream receipt over both recurrence planner actions:

```bash
python scripts/circle_ai_contract_ready.py \
  --kind recurrence_schedule \
  --receipt \
  --format json \
  --field periodic_shift_required_steps_invariant \
  --field periodic_shift_active_at_step_invariant \
  --field total_active_token_work \
  --field scheduled_work_saving \
  --field scheduled_work_saving_accounting \
  --field active_inactive_work_accounting \
  --field scheduled_work_saving_positive \
  --field post_period_multi_extension_scheduled_work_saving \
  --require-theorem AIM-T0026 \
  --require-theorem AIM-T0130 \
  --require-theorem AIM-T0159 \
  --require-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE \
  --require-recommendation RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT \
  --require-recommendation-evidence-field RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=total_active_token_work \
  --require-recommendation-evidence-field RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving \
  --require-recommendation-evidence-field RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=post_period_multi_extension_scheduled_work_saving \
  --require-recommendation-evidence-field RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=periodic_shift_required_steps_invariant \
  --require-recommendation-evidence-field RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=periodic_shift_active_at_step_invariant \
  --require-recommendation-theorem RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130 \
  --require-recommendation-theorem RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159 \
  --require-recommendation-theorem RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026 \
  --require-recommendation-action-parameter RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period \
  --require-recommendation-action-parameter RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving \
  --require-recommendation-action-parameter RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token \
  --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period \
  --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count \
  --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps \
  --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving \
  --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=post_period_multi_extension_scheduled_work_saving \
  --require-recommendation-action-parameter-path RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token \
  --require-recommendation-action-parameter-path RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token \
  --require-recommendation-action-parameter-path RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount
```

That receipt pins the finite active-token work schedule and whole-period
index-reuse witness. It is not a runtime, memory, adaptive-halting,
reasoning-quality, or model-quality proof.

Default fixture:

```text
loop_period=5
sample_index=8
max_loops=7
token_count=8
shift_passes=3
```

## Read The Report

The text report is organized as:

```text
recurrence_schedule_contract=READY ...
exit_contract=...
active_work=...
work_budget=...
schedule_trace=...
periodic_shift=...
consumer_check=...
not_claimed=...
```

The most important planner-facing line is:

```text
schedule_trace=active_counts=(8, 6, 4, 2, 1) inactive_counts=(0, 2, 4, 6, 7) active_sum_matches_total=True inactive_sum_matches_total=True first_inactive_steps_match_budget_successor=True
```

This is the finite stop schedule for the default token set. The active-count
trace sums to `21`, the inactive-count trace sums to `19`, and each token's
first inactive step is exactly one past its active recurrence budget. A
downstream scheduler can use this as an audit trace for index reuse and work
gating. It is not a runtime measurement or adaptive-halting quality claim.

The index-reuse line is:

```text
periodic_shift=base_token=7 passes=3 amount=15 shifted_token=22 required_steps_invariant=True recurrence_budget_invariant=True training_free_budget_invariant=True exit_step_invariant=True overthinking_boundary_invariant=True active_step=2 active_at_step_invariant=True
```

This says that shifting the token index by a whole number of loop periods
preserves the finite recurrence schedule fields in the current fixture. It is
an index-reuse/schedule contract, not evidence that a looped transformer will
reason better.

## JSON Contract

The JSON output is a generic Circle AI contract object:

```text
id=CC-AI-CONTRACT-RECURRENCE-001
kind=recurrence_schedule
consumer_check.ready_for_downstream_fixture_use=True
proof_status.all_theorem_ids_proved=True
```

Downstream tools should require:

```text
consumer_check.ready_for_downstream_fixture_use == true
consumer_check.required_fields_present == true
consumer_check.all_theorem_ids_proved == true
consumer_check.missing_minimum_fields == []
```

They should also preserve `not_claimed` and the theorem ids in any derived
report.

## Planner Recommendations

The generated AI contract pack exposes two optional recommendation records:

```text
RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE
RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT
```

The first record packages the theorem-backed active-token work schedule:
`21` active token-steps, `19` inactive/saved token-steps, and `40` fixed-depth
token-steps in the default `loop_period=5`, `token_count=8`, `horizon=5`
fixture. It now also exposes the count traces
`active_token_count_trace=[8,6,4,2,1]` and
`inactive_token_count_trace=[0,2,4,6,7]`, plus a per-token
`first_inactive_steps` table. It also reports the post-period extension boundary: extending the
horizon to `6` steps leaves active token work at `21` while scheduled-work
saving rises to `27`, meaning the extra step is all inactive/saved work in the
finite schedule. The generalized overrun field repeats the same check for
`3` extra post-period steps: horizon `8` still has active token work `21`, while
scheduled-work saving rises to `43`, exactly `19 + 3 * 8`. The second record
packages the whole-period shift witness from
token `7` to token `22`, preserving required steps, recurrence budget, wrapper
budget, exit step, overthinking boundary, and active-at-step status.

These recommendation records are finite schedule/index fixtures. They are not
runtime, memory, adaptive-halting, reasoning-quality, or model-quality claims.

## Main Theorem Cluster

- `AIM-T0026`: required steps are invariant under whole loop-period shifts.
- `AIM-T0027`: token recurrence budgets are invariant under whole loop-period shifts.
- `AIM-T0028`: training-free wrapper budgets are invariant under whole loop-period shifts.
- `AIM-T0029`: overthinking boundaries are invariant under whole loop-period shifts.
- `AIM-T0030`: exit availability is invariant under whole loop-period shifts.
- `AIM-T0033` and `AIM-T0034`: shifted exit certificates preserve exit step and boundary.
- `AIM-T0036`: active-at-step membership is invariant under whole loop-period token shifts.
- `AIM-T0130`, `AIM-T0131`, `AIM-T0144`, and `AIM-T0145`: finite active/inactive work accounting and saved-work accounting.
- `AIM-T0150` through `AIM-T0152`: after the loop-period boundary, one more horizon step adds no active work, adds exactly one token count of inactive work, and increases scheduled-work saving by exactly one token count.
- `AIM-T0153` and `AIM-T0154`: the default `loop_period=5`, `token_count=8`, `horizon=6` fixture keeps active work unchanged and increases scheduled-work saving from `19` to `27`.
- `AIM-T0155` through `AIM-T0157`: after the loop-period boundary, any declared number of extra horizon steps adds no active work, adds exactly `extra_steps * token_count` inactive work, and increases scheduled-work saving by that same amount.
- `AIM-T0158` and `AIM-T0159`: the default `loop_period=5`, `token_count=8`, `horizon=8` fixture keeps active work unchanged and increases scheduled-work saving from `19` to `43`.

## What This Does Not Prove

The recurrence schedule certifier does not prove recursive reasoning,
adaptive-exit quality, perplexity, throughput, memory savings, deployment
safety, or model quality. It proves finite schedule/index/accounting facts for
the declared fixture and reports them in a form another AI project can consume.
