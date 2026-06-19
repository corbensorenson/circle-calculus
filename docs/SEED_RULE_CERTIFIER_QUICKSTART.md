# Seed-Rule Certifier Quickstart

This quickstart is the public entry point for the seed/rule exact-regeneration
contract. It is for auditing whether a declared generator record rebuilds an
artifact and whether a finite declared candidate set has exact or shorter
candidates. It is not a global compression or minimality result.

## Run

```bash
python scripts/seed_rule_certify.py
python scripts/seed_rule_certify.py --format json
python scripts/seed_rule_certify.py --n 8
python scripts/seed_rule_certify.py --json-out /tmp/seed_rule_contract.json
python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration --digest --field storage_saving --include-recommendations
```

The default positive fixture is:

```text
artifact_id=finite_circle
fixture_n=128
```

The `--n 8` run is intentionally useful as a negative case: exact regeneration
still holds, but the seed/rule record is not shorter than explicit storage, so
the downstream readiness gate is false.

## Read The Report

The text report is organized as:

```text
seed_rule_contract=...
storage_accounting=...
bounded_search=...
candidate_ranking=...
generator_record=...
consumer_check=...
bounded_search_note=...
not_claimed=...
```

The main positive-case line is:

```text
seed_rule_contract=READY artifact_id=finite_circle fixture_n=128 exact_regeneration=True generator_shorter=True
```

The bounded-search line is scoped to the declared finite candidate list:

```text
bounded_search=search_id=public_seed_rule_finite_circle_search candidate_count=3 exact_candidate_count=2 exact_count_le_candidate_count=True has_best_exact=True best_exact_regenerates=True has_best_shorter=True best_shorter_generator_shorter=True
```

The candidate-ranking line distinguishes stable candidate ids from the shared
`artifact_id=finite_circle` label:

```text
candidate_ranking=by_generator_length=('finite_circle_unit_fixture', 'finite_circle_broken_fixture', 'finite_circle_public_fixture') exact_by_generator_length=('finite_circle_unit_fixture', 'finite_circle_public_fixture') shorter_by_generator_length=('finite_circle_public_fixture',) best_exact=finite_circle_unit_fixture best_shorter=finite_circle_public_fixture
```

This means the smallest exact declared generator is the unit fixture, while the
only exact declared generator that is shorter than explicit object storage is
the public `C_128` fixture.

## JSON Contract

The JSON output is a generic Circle AI contract object:

```text
id=CC-AI-CONTRACT-SEED-RULE-001
kind=seed_rule_exact_regeneration
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

They should also preserve `not_claimed`, `bounded_search_note`, and the theorem
ids in any derived report.

## Planner Recommendations

The generated AI contract pack exposes two optional recommendation records:

```text
SEED-RULE-USE-EXACT-REGENERATION-RECIPE
SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE
```

The first record packages the public finite-circle seed/rule recipe for exact
regeneration. The second record packages the bounded finite-search result that
selects the exact shorter `finite_circle` candidate with storage saving `71`
under the declared length metric. JSON consumers can inspect
`bounded_search_candidates`,
`bounded_search_candidate_ids_by_generator_length`,
`bounded_search_best_exact_candidate_id`, and
`bounded_search_best_shorter_candidate_id` to audit the declared finite search
without re-running the candidate comparison.

These records are scoped to the emitted fixture and declared candidate list.
They do not prove global minimality, Kolmogorov complexity, universal
compression, semantic equivalence, or model quality.

## Main Theorem Cluster

- `GEN-T0037`: a positive exact count is equivalent to having a best exact candidate in the declared finite search.
- `GEN-T0044`: exact candidate count is bounded by declared candidate count.
- `GEN-T0045`: a returned best exact candidate implies the declared candidate set is nonempty.
- `GEN-T0046` through `GEN-T0050`: public `C_128` storage-accounting fixture fields.

## What This Does Not Prove

The seed-rule certifier does not prove global minimality, Kolmogorov
complexity, universal compression, model quality, storage savings for all
objects, or semantic usefulness. It proves exact regeneration and finite
declared-search/accounting facts for the emitted fixture.
