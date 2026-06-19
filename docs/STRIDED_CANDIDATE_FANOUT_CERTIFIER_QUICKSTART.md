# Strided Candidate Fanout Certifier Quickstart

This certifier packages the finite strided-candidate fanout fixture as a public
Circle AI contract. It answers one narrow question:

```text
Given a finite context, a start index, and a stride, which candidates are
visited, how many distinct indices are reachable, and where do duplicates appear
in a fixed candidate budget?
```

It is useful for auditing sparse candidate generators, branch fanout plans,
retrieval probes, and stride-based routing schedules before treating them as
model-quality or search-quality improvements.

Run the default full-coverage fixture:

```bash
python scripts/strided_candidate_fanout_certify.py
```

The default text report should include:

```text
strided_candidate_fanout_contract=READY context_length=12 start_index=0 stride=5 gcd=1 predicted_reach=12 full_coverage=True
orbit=nodes=(0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7) orbit_unique=True predicted_reach_matches_orbit_length=True theorems=AIT-T0001,AIT-T0002,AIT-T0003
candidate_path=nodes=(7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0) candidate_budget=12 unique_candidate_count=12 effective_candidate_budget=12 duplicate_count=0 path_unique=True candidate_budget_accounting=True candidate_budget_shortfall=0 effective_budget_reaches_predicted_reach=True
consumer_check=ready=True required_fields_present=True all_theorem_ids_proved=True missing_fields=0
```

Emit JSON for downstream tools:

```bash
python scripts/strided_candidate_fanout_certify.py --format json
python scripts/strided_candidate_fanout_certify.py --json-out /tmp/fanout_contract.json
```

Try a non-coprime stride with duplicate collapse:

```bash
python scripts/strided_candidate_fanout_certify.py \
  --context-length 10 \
  --stride 4 \
  --start-index 1 \
  --path-length 8
```

Expected evidence fields:

| Field | Meaning |
| --- | --- |
| `context_length` | Finite candidate context size. |
| `stride` | Fixed step used by the fanout path. |
| `start_index` | Start/query index for the orbit and predecessor path. |
| `gcd` | `gcd(context_length, stride)`. |
| `predicted_reach` | Reachable orbit size, `context_length / gcd`. |
| `orbit` | Distinct forward orbit from the start index. |
| `full_coverage` | Whether the stride reaches every context index. |
| `candidate_path` | Fixed-budget predecessor candidates. |
| `candidate_budget` | Number of emitted predecessor candidates. |
| `unique_candidate_count` | Number of distinct candidates in the emitted path. |
| `effective_candidate_budget` | Duplicate-collapsed budget available to a planner. |
| `duplicate_count` | Candidate slots lost to duplicate indices. |
| `candidate_budget_accounting` | Whether `effective_candidate_budget + duplicate_count = candidate_budget`. |
| `effective_budget_matches_unique_candidates` | Whether the effective budget equals the distinct candidate count. |
| `candidate_budget_shortfall` | Missing unique candidates relative to `predicted_reach`. |
| `effective_budget_reaches_predicted_reach` | Whether the duplicate-collapsed path reaches the predicted orbit size. |

The theorem cluster is:

| Theorem id | Role |
| --- | --- |
| `AIT-T0001` | Fixed stride lives in a finite cyclic context. |
| `AIT-T0002` | GCD controls orbit reach. |
| `AIT-T0003` | Coprime stride corresponds to full finite coverage. |

The generated contract pack stores the same certificate under
`strided_candidate_fanout`:

```bash
python scripts/export_circle_ai_contracts.py
python scripts/circle_ai_contract_ready.py --kind strided_candidate_fanout --digest \
  --field gcd \
  --field predicted_reach \
  --field full_coverage \
  --field effective_candidate_budget \
  --field candidate_budget_accounting \
  --field candidate_budget_shortfall \
  --field duplicate_count \
  --include-recommendations
```

The planner recommendations are:

- `FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE`: use the declared coprime stride cycle as a finite full-coverage candidate path.
- `FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET`: audit the fixed candidate path for duplicate collapse, effective budget, and shortfall.

These records are finite routing/candidate bookkeeping. They do not prove search quality, retrieval quality, ranking quality, runtime, or model quality.

Non-claims:

- This is finite candidate-index bookkeeping, not a search-quality theorem.
- It does not prove retrieval quality, model quality, speed, context-length
  improvement, deployment safety, or ASI.
- The Python report is an executable certificate surface; the formal source is
  still the Lean theorem ids resolved through the manifest.
