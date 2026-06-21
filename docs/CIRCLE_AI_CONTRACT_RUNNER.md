# Circle AI Contract Runner

The contract runner is the parameterized surface for the proof-carrying AI lane.
It takes a user configuration and emits a text or JSON receipt with:

- normalized input parameters,
- a compact `decision` block for downstream gates,
- theorem ids used by the receipt,
- proof-status summary from the generated contract pack,
- evidence fields from the relevant Python certifier,
- top-level planner recommendations and validation commands,
- explicit proved, computed, numerical-only, unsupported, and non-claim labels,
- request, normalized-request, pack, contract, and receipt fingerprints.

The runner does not re-run Lean. Lean remains the formal proof source, and the
generated contract pack remains the public proof-status index.

## First Commands

```bash
python scripts/circle_ai_certify.py rope \
  --head-dim 128 \
  --base 10000 \
  --context 131072 \
  --requested-margin 1/328459

python scripts/circle_ai_certify.py rope \
  --model-config examples/circle_ai_model_configs/standard_rope_config.json \
  --requested-margin 1/328459 \
  --format json \
  --request-out reports/rope_request.json \
  --json-out reports/rope_receipt.json

python scripts/circle_ai_certify.py kv-cache \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31 \
  --sink-size 4

python scripts/circle_ai_certify.py sparse-attention \
  --context 120 \
  --strides 7,13 \
  --path-length 3 \
  --local-window 4

python scripts/circle_ai_certify.py recurrence
```

Add `--format json` for a machine-readable receipt, `--json-out PATH` to write
one to disk, and `--request-out PATH` to save the exact versioned request JSON
used by the run. Add `--request-validation-report-out PATH` when a direct
single-config run should also save the schema-validated preflight report for
the exact request that produced the receipt. Add
`--certification-bundle-out PATH` when CI wants one schema-validated artifact
containing request preflight, receipt, gate report, and, for `--model-config`
runs, the model-config import report that records parameter provenance.

For CI gates, add `--require-status STATUS`, `--require-decision VERDICT`,
`--require-assurance LEVEL`, and/or `--require-passed`. The runner still prints
or writes the receipt, then exits nonzero if the emitted receipt does not match
the required status, decision verdict, assurance level, or if `request_passed`
is not `true`.
Add `--gate-report-out PATH` when CI also needs a schema-validated JSON gate
report but does not need to save the full receipt. Add `--receipt-check-out
PATH` with `--json-out PATH` when the report should point at a saved receipt
file for audit logs.

For standard RoPE model configs, `--model-config` infers `head_dim` from
`head_dim` or `hidden_size / num_attention_heads`, `base` from `rope_theta`
when present, and `context` from `max_position_embeddings` or related context
fields. Explicit `--head-dim`, `--base`, `--context`, `--tolerance`, and
`--discretization` flags override inferred values. Non-default `rope_scaling`
metadata is rejected rather than treated as proved by the current standard-RoPE
contract. `head_dim` must be even because the current RoPE contract models
rotary dimension pairs.
Use `--model-config-import-report-out PATH` to write a schema-validated import
report even when a real config contains unsupported fields such as non-default
`rope_scaling`. That report is not a receipt; it says whether the config could
be converted into the standard-RoPE request frontier and includes fingerprints
for the source config and emitted request when one exists. It also includes
`parameter_sources`, which records whether each standard-RoPE request parameter
came from an explicit override, a config field, derived config fields, a
default, or an omitted optional input.
When `--request-out` is used with `--model-config`, the saved request is the
exact versioned Circle request object emitted by the import report and used to
produce the receipt.
When `--certification-bundle-out` is used with `--model-config`, that same
import report is embedded in the certification bundle, so a downstream project
can audit the model-config fingerprint and parameter sources without opening a
separate sidecar.
The copyable fixture is
`examples/circle_ai_model_configs/standard_rope_config.json`.

External projects can also use the versioned request schema directly:

```json
{
  "schema_id": "circle_calculus.ai_contract_request.v0",
  "kind": "rope_position_distinguishability",
  "parameters": {
    "head_dim": 128,
    "base": 10000.0,
    "context": 131072,
    "requested_margin": "1/328459"
  }
}
```

Run it with:

```bash
python scripts/circle_ai_certify.py request \
  --request-json path/to/request.json \
  --format json \
  --json-out path/to/receipt.json \
  --receipt-check-out path/to/receipt_check.json \
  --require-status proved \
  --require-decision passed \
  --require-assurance mixed_theorem_and_computation \
  --require-passed
```

Preflight a request file without issuing a receipt:

```bash
python scripts/circle_ai_certify.py request \
  --request-json path/to/request.json \
  --validate-only \
  --format json \
  --json-out reports/request_validation.json
```

The validate-only report is checked against
`site/data/generated/circle_ai_contract_request_validation.schema.json` before it
is printed or written. It includes the request-content fingerprint so CI can pin
the exact request JSON that was preflighted.

Every emitted receipt is checked against
`site/data/generated/circle_ai_contract_receipt.schema.json` and then validated
against the loaded contract pack before it is printed or written. The pack-aware
check covers the claimed pack fingerprint, contract fingerprint, contract id,
and theorem-id membership. Use `--receipt-schema` to pin a generated schema path
in a downstream project.
By default, emitted receipts are issued against
`site/data/generated/circle_ai_contract_pack.json`, the same public pack used by
the saved-receipt verifier. Use `--pack` only when intentionally testing a
different generated pack.
Use `--receipt-check-out` with `--json-out` to write the same schema-validated
pack-aware check report that a later `scripts/check_circle_ai_receipt.py` run
would produce for the saved receipt.
Use `--gate-report-out` without `--json-out` to write the same gate shape for
the in-memory receipt:

```bash
python scripts/circle_ai_certify.py rope \
  --head-dim 128 \
  --base 10000 \
  --context 131072 \
  --requested-margin 1/328459 \
  --gate-report-out reports/rope_gate.json \
  --require-status proved \
  --require-decision passed \
  --require-assurance mixed_theorem_and_computation \
  --require-passed
```

Both report paths are validated against
`site/data/generated/circle_ai_contract_receipt_file_check.schema.json`.
Certification bundles are validated against
`site/data/generated/circle_ai_contract_certification_bundle.schema.json`.
Use `--certification-bundle-check-out` with `--certification-bundle-out` to
write the same schema-validated bundle verification report that a later
`scripts/check_circle_ai_certification_bundle.py` run would produce:

```bash
python scripts/circle_ai_certify.py rope \
  --head-dim 128 \
  --base 10000 \
  --context 131072 \
  --requested-margin 1/328459 \
  --json-out reports/rope_receipt.json \
  --certification-bundle-out reports/rope_certification_bundle.json \
  --certification-bundle-check-out reports/rope_certification_bundle_check.json \
  --require-status proved \
  --require-decision passed \
  --require-assurance mixed_theorem_and_computation \
  --require-passed
```

The bundle-check report is validated against
`site/data/generated/circle_ai_contract_certification_bundle_file_check.schema.json`.
In text mode, the certifier prints an `artifacts=` line listing every request,
receipt, gate, bundle, or check file written by that invocation.
Use `--artifact-dir reports/rope_contract` when you want the standard audit set
without naming every file. It fills unset paths for:

```text
<prefix>_request.json
<prefix>_request_validation.json
<prefix>_model_config_import.json       # RoPE model-config runs only
<prefix>_receipt.json
<prefix>_receipt_check.json
<prefix>_gate_report.json
<prefix>_certification_bundle.json
<prefix>_certification_bundle_check.json
<prefix>_artifact_manifest.json
<prefix>_artifact_manifest_check.json
```

The default prefix is the request or model-config filename stem when available,
otherwise the contract family name. Use `--artifact-prefix` to override it. The
manifest indexes the generated files, their schema ids, and their file SHA-256
hashes. The manifest-check report re-hashes those indexed files and verifies
the manifest's mirrored receipt status fields.

Downstream projects can verify a complete artifact directory from that manifest:

```bash
python scripts/check_circle_ai_artifact_manifest.py \
  reports/rope_contract/standard_rope_config_artifact_manifest.json \
  --report-out reports/rope_contract/standard_rope_config_artifact_manifest_check.json
```

The checker validates the manifest schema, referenced file existence,
SHA-256 fingerprints, declared content schema ids, and the receipt summary
fields mirrored into the manifest.
It also accepts `--require-kind`, `--require-theorem-id`,
`--require-evidence-field`, and `--require-recommendation-id` for first-party
CI jobs that need the same policy pins as the copyable standalone verifier.
For a copyable standard-library-only downstream gate, use
`examples/downstream_ci_verify_circle_ai_artifacts.py`; it performs the same
artifact-integrity checks without importing Circle or `jsonschema`.
The standard artifact-directory path and standalone verifier are covered for
RoPE, KV-cache, sparse-attention, and recurrence receipts, so downstream CI can
adopt one gate shape across all four current contract families.
When a downstream job emits multiple manifests, add `--require-kind` for each
contract family that must be present; the verifier fails if any required family
is missing.
Add `--require-theorem-id THEOREM_ID` when the downstream job depends on a
specific theorem appearing in at least one saved receipt artifact.
Add `--require-evidence-field FIELD` or `--require-recommendation-id ID` when
automation consumes a specific receipt field or planner recommendation.

Copyable starting points live under:

```text
examples/circle_ai_requests/rope_request.json
examples/circle_ai_requests/kv_cache_request.json
examples/circle_ai_requests/sparse_attention_request.json
examples/circle_ai_requests/recurrence_request.json
```

Check all public request examples and their receipt schemas with:

```bash
python scripts/check_circle_ai_contract_runner.py
```

Write receipt JSON files for a request directory:

```bash
python scripts/check_circle_ai_contract_runner.py \
  --example-dir examples/circle_ai_requests \
  --receipt-out-dir reports/circle_ai_receipts \
  --model-config-import-report-out-dir reports/circle_ai_imports \
  --request-validation-report-out-dir reports/circle_ai_request_validation \
  --certification-bundle-out-dir reports/circle_ai_certification_bundles \
  --certification-bundle-check-out-dir reports/circle_ai_certification_bundle_checks \
  --report-out reports/circle_ai_runner_check.json \
  --require-status proved \
  --require-decision passed \
  --require-passed
```

The batch checker records its gate policy in
`circle_ai_runner_check.json`. If any receipt violates `--require-status`,
`--require-decision`, `--require-assurance`, or `--require-passed`, the report
is still written with the receipt summaries and the command exits nonzero. Each
summary includes the `normalized_request` object so downstream CI can compare
the certified parameters without reopening every receipt file. Each summary
also includes `source_content_fingerprint` so request files and model configs
can be pinned in audit logs. Model-config summaries also inline
`model_config_parameter_sources`, so audit logs can show which request values
were overridden, read from config fields, derived, defaulted, or omitted without
reopening the import sidecar. When `--model-config-import-report-out-dir` is set,
model-config summaries also point to the schema-validated import report that
converted the config into a Circle request.
When `--request-validation-report-out-dir` is set, every summary also points to
the schema-validated preflight report for the exact request that produced the
receipt.
When `--certification-bundle-out-dir` is set, every summary also points to a
schema-validated certification bundle containing the preflight report, receipt,
gate report, and any model-config import provenance.
When `--certification-bundle-check-out-dir` is also set, every summary points to
a schema-validated verification report for that bundle. This is useful when a
batch job should leave both portable artifacts and CI-readable pass/fail
evidence beside them.
By default it checks both `examples/circle_ai_requests/*.json` request files and
`examples/circle_ai_model_configs/*.json` standard RoPE model configs, currently
including 128k examples at RoPE bases `10000` and `500000`. Model config
examples are first converted into versioned Circle request JSON, then checked
by the same receipt path.

Validate a saved certification bundle that another project has already
produced:

```bash
python scripts/check_circle_ai_certification_bundle.py \
  reports/rope_certification_bundle.json \
  --require-status proved \
  --require-decision passed \
  --require-assurance mixed_theorem_and_computation \
  --require-passed \
  --report-out reports/rope_certification_bundle_check.json
```

This checker validates the bundle JSON Schema, request-validation report,
embedded receipt against the loaded contract pack, embedded gate report,
optional model-config import provenance, and optional status, decision,
assurance, or pass gates. It is the preferred CI-facing command when a
downstream project stores the full certification bundle rather than just the
receipt.

Validate a saved receipt file that another project has already produced:

```bash
python scripts/check_circle_ai_receipt.py reports/rope_receipt.json \
  --require-status proved \
  --require-decision passed \
  --require-assurance mixed_theorem_and_computation \
  --require-passed \
  --report-out reports/rope_receipt_check.json
```

This checker validates the receipt JSON Schema, the in-process receipt shape,
the receipt fingerprint, the loaded contract-pack fingerprint, the contract
fingerprint, theorem-id membership in the loaded contract, and optional status
decision, assurance, or pass gates. It validates its own report against
`site/data/generated/circle_ai_contract_receipt_file_check.schema.json` and can
write that report to disk for audit logs. It is the smallest CI-facing command
for downstream projects that want to reject stale or tampered Circle AI receipts
without running Lean. The report summary includes the loaded contract-pack
fingerprint, contract fingerprint, receipt fingerprint, request-content
fingerprint, normalized-request fingerprint, and normalized request, so CI can
record what was certified without reopening every receipt file.

Receipt JSON is strict at the top level: unknown fields are rejected, while
contract-specific details live under `evidence`, `support`, and `proof_layers`.
The embedded `request` object is also validated against the public request
schema, and its contract kind must match the receipt kind.

For downstream code, read `decision` first. It repeats the receipt status in a
small stable shape:

```json
{
  "schema_id": "circle_calculus.ai_contract_decision.v0",
  "verdict": "passed",
  "assurance": "mixed_theorem_and_computation",
  "claim_status": "proved",
  "request_passed": true,
  "theorem_count": 43,
  "all_theorem_ids_proved": true,
  "proof_layer_counts": {
    "proved_fields": 5,
    "computed_fields": 2,
    "numerical_only_fields": 4,
    "unsupported_fields": 2
  },
  "summary": "rope_position_distinguishability request passed with receipt status proved.",
  "next_action": "Use the receipt as a theorem-linked structural certificate."
}
```

The validator rejects stale decisions: `claim_status`, `request_passed`,
`theorem_count`, `all_theorem_ids_proved`, and proof-layer counts must match the
rest of the receipt.

## Receipt Statuses

| Status | Meaning |
| --- | --- |
| `proved` | The receipt's finite structural claim is theorem-backed by ids resolved through the contract pack. |
| `impossible` | The requested property is theorem-backed as impossible in the stated range. |
| `undecided` | The request is deliberately inside a proved open gap or otherwise not decided by the current theorem frontier. |
| `numerical_only` | The evidence is executable numerical support, not a formal theorem. |
| `outside_scope` | The requested parameter range is outside the currently proved contract family. |

`request_passed` is separate from `status`. For example, a KV-cache stale-read
request can have `status = proved` and `request_passed = false`, because the
failure itself is theorem-backed.

For RoPE receipts, `real_phase_dirichlet_guardrail` is a theorem-backed
finite-context ceiling. When `context > 1`, theorem ids `AIRA-T0239` through
`AIRA-T0241` justify the `1/context` guardrail: a requested real-phase margin
strictly above `1/context` is impossible. A margin at or below that ceiling is
not automatically proved by this field; it still needs a D19-style certificate or
future sharper theorem.

## Python API

```python
from circle_math.applications import (
    build_contract_artifact_manifest_file_check_report,
    build_contract_certification_bundle,
    build_contract_certification_bundle_file_check_report,
    build_contract_receipt_file_check_report,
    build_contract_receipt_gate_report,
    build_contract_request,
    build_contract_request_validation_report,
    build_rope_contract_request_from_model_config,
    build_validated_contract_receipt,
    build_validated_contract_receipt_from_request,
    build_validated_rope_receipt_from_model_config,
    validate_contract_request,
    validate_contract_receipt_against_pack,
    load_contract_pack,
    require_contract_receipt_gate,
)

pack = load_contract_pack("site/data/generated/circle_ai_contract_pack.json")
model_config = {
    "hidden_size": 4096,
    "num_attention_heads": 32,
    "rope_theta": 10000.0,
    "max_position_embeddings": 131072,
}
request = build_rope_contract_request_from_model_config(
    model_config,
    requested_margin="1/328459",
)
receipt = build_validated_rope_receipt_from_model_config(
    model_config,
    requested_margin="1/328459",
    pack=pack,
)
assert receipt["request"] == request

request = build_contract_request(
    "rope",
    {
        "head_dim": 128,
        "base": 10000.0,
        "context": 131072,
        "requested_margin": "1/328459",
    },
)

receipt = build_validated_contract_receipt(
    request["kind"],
    request["parameters"],
    pack=pack,
)
assert receipt["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
assert receipt["decision"]["verdict"] == "passed"
assert receipt["proof_status"]["all_theorem_ids_proved"] is True
assert receipt["request_content_fingerprint"]
assert receipt["normalized_request_fingerprint"]
assert receipt["recommendations"]
assert receipt["validation_commands"]
assert validate_contract_receipt_against_pack(receipt, pack) == []
check_report = build_contract_receipt_file_check_report(
    receipt,
    pack,
    receipt_path="reports/rope_receipt.json",
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("mixed_theorem_and_computation",),
    require_passed=True,
)
assert check_report["ok"] is True
gate_report = build_contract_receipt_gate_report(
    receipt,
    pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("mixed_theorem_and_computation",),
    require_passed=True,
)
assert gate_report["ok"] is True
require_contract_receipt_gate(
    receipt,
    pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("mixed_theorem_and_computation",),
    require_passed=True,
)

request = {
    "schema_id": "circle_calculus.ai_contract_request.v0",
    "kind": "sparse-attention",
    "parameters": {
        "context": 120,
        "strides": (7, 13),
        "path_length": 3,
        "local_window": 4,
    },
}
assert validate_contract_request(request) == []
assert build_contract_request_validation_report(request)["ok"] is True
receipt = build_validated_contract_receipt_from_request(request, pack=pack)
bundle = build_contract_certification_bundle(
    request,
    pack=pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("theorem_backed",),
    require_passed=True,
)
assert bundle["request_validation_report"]["ok"] is True
assert bundle["receipt"] == receipt
assert bundle["gate_report"]["ok"] is True
bundle_check_report = build_contract_certification_bundle_file_check_report(
    bundle,
    pack,
    bundle_path="reports/sparse_attention_certification_bundle.json",
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("theorem_backed",),
    require_passed=True,
)
assert bundle_check_report["ok"] is True
```

The bundle's top-level `request_content_fingerprint` is the fingerprint of the
submitted request object used for preflight. If the request came from
`--model-config` or from `build_rope_model_config_import_report`, the optional
`model_config_import_report` section carries the model-config fingerprint, the
config-to-request parameter sources, and the emitted request fingerprint. The
embedded receipt still carries its own `request_content_fingerprint` for the
canonical request that the certifier emitted after applying contract defaults.

The public Circle AI runner JSON Schemas are generated by:

```bash
python scripts/export_circle_ai_contracts.py
```

and written to:

```text
site/data/generated/circle_ai_contract_request.schema.json
site/data/generated/circle_ai_contract_request_validation.schema.json
site/data/generated/circle_ai_rope_model_config_import.schema.json
site/data/generated/circle_ai_contract_receipt.schema.json
site/data/generated/circle_ai_contract_runner_check.schema.json
site/data/generated/circle_ai_contract_receipt_file_check.schema.json
site/data/generated/circle_ai_contract_certification_bundle.schema.json
site/data/generated/circle_ai_contract_certification_bundle_file_check.schema.json
site/data/generated/circle_ai_contract_artifact_manifest.schema.json
site/data/generated/circle_ai_contract_artifact_manifest_file_check.schema.json
```

The request schema has contract-specific parameter shapes. RoPE and recurrence
requests may rely on defaults, while KV-cache and sparse-attention requests must
include their required fields. RoPE `head_dim` values must be positive and even.
Recurrence `max_loops` and `selected_block_width` values must be positive.
Unknown top-level request keys and unknown parameter keys are rejected so typoed
configs fail before a receipt is issued.

`validate_contract_request(request)` applies the same contract-specific checks
inside Python, including required fields, unknown keys, numeric ranges, and
RoPE margin parsing.

## Non-Claims

The runner proves finite contract fields only. It does not prove model quality,
training improvement, deployment safety, implementation correctness, memory
savings, throughput, or useful context-length improvement.
