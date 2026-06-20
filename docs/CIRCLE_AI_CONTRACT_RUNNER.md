# Circle AI Contract Runner

The contract runner is the parameterized surface for the proof-carrying AI lane.
It takes a user configuration and emits a text or JSON receipt with:

- normalized input parameters,
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
  --model-config path/to/config.json \
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
used by the run.

For standard RoPE model configs, `--model-config` infers `head_dim` from
`head_dim` or `hidden_size / num_attention_heads`, `base` from `rope_theta`
when present, and `context` from `max_position_embeddings` or related context
fields. Explicit `--head-dim`, `--base`, `--context`, `--tolerance`, and
`--discretization` flags override inferred values. Non-default `rope_scaling`
metadata is rejected rather than treated as proved by the current standard-RoPE
contract.

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
  --json-out path/to/receipt.json
```

Preflight a request file without issuing a receipt:

```bash
python scripts/circle_ai_certify.py request \
  --request-json path/to/request.json \
  --validate-only \
  --format json
```

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
  --report-out reports/circle_ai_runner_check.json
```

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
    build_contract_receipt,
    build_contract_receipt_from_request,
    build_contract_request,
    build_contract_request_validation_report,
    validate_contract_request,
)

request = build_contract_request(
    "rope",
    {
        "head_dim": 128,
        "base": 10000.0,
        "context": 131072,
        "requested_margin": "1/328459",
    },
)

receipt = build_contract_receipt(
    request["kind"],
    request["parameters"],
)
assert receipt["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
assert receipt["proof_status"]["all_theorem_ids_proved"] is True
assert receipt["request_content_fingerprint"]
assert receipt["normalized_request_fingerprint"]
assert receipt["recommendations"]
assert receipt["validation_commands"]

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
receipt = build_contract_receipt_from_request(request)
```

The versioned request and receipt JSON Schemas are generated by:

```bash
python scripts/export_circle_ai_contracts.py
```

and written to:

```text
site/data/generated/circle_ai_contract_request.schema.json
site/data/generated/circle_ai_contract_request_validation.schema.json
site/data/generated/circle_ai_contract_receipt.schema.json
site/data/generated/circle_ai_contract_runner_check.schema.json
```

The request schema has contract-specific parameter shapes. RoPE and recurrence
requests may rely on defaults, while KV-cache and sparse-attention requests must
include their required fields. Unknown parameter keys are rejected so typoed
configs fail before a receipt is issued.

`validate_contract_request(request)` applies the same contract-specific checks
inside Python, including required fields, unknown keys, numeric ranges, and
RoPE margin parsing.

## Non-Claims

The runner proves finite contract fields only. It does not prove model quality,
training improvement, deployment safety, implementation correctness, memory
savings, throughput, or useful context-length improvement.
