# Public API Surfaces

This file records the intended stable entry points for users who treat Circle
Calculus as a library.

## Stability Rule

Stable APIs are allowed to grow, but they should not be removed or renamed
without a version bump and migration note. Research modules may change faster.

Stable:

- Python: `circle_math.core`, `circle_math.contracts`, `circle_math.ai_contracts`
- Lean: `Circle.Core`, `Circle.Applications.Public`, `Circle.Contracts`
- Rust: the `circle-prime` crate root and documented binaries

Research/internal:

- large generated Lean certificate modules except through `Circle.Contracts`;
- repository maintenance scripts under `scripts/`;
- sidecar benchmark scripts and raw result fixtures;
- private-transfer compatibility lanes.

## Python Core

Use `circle_math.core` for finite cyclic mathematics:

```python
from circle_math.core import finite_orbit, finite_period, is_full_coil

assert finite_orbit(12, 5)[0:4] == [0, 5, 10, 3]
assert finite_period(12, 5) == 12
assert is_full_coil(12, 5) is True
```

## Python Contracts

Use `circle_math.ai_contracts` to build public contract fixtures and receipts:

```python
from circle_math.ai_contracts import (
    build_contract_pack,
    build_rope_receipt,
    build_validated_rope_receipt_from_model_config,
)

pack = build_contract_pack()
receipt = build_rope_receipt(context=4096, pack=pack)
assert receipt["decision"]["all_theorem_ids_proved"] is True

model_config = {
    "hidden_size": 4096,
    "num_attention_heads": 32,
    "max_position_embeddings": 4096,
    "rope_theta": 10000.0,
}
receipt_from_config = build_validated_rope_receipt_from_model_config(
    model_config,
    pack=pack,
)
assert receipt_from_config["kind"] == "rope_position_distinguishability"
```

Use `circle_math.contracts` to consume an already exported pack:

```python
from circle_math.contracts import load_contract_pack, require_ready_contract

pack = load_contract_pack("site/data/generated/circle_ai_contract_pack.json")
contract = require_ready_contract(pack, "sparse_attention_coverage")
print(contract["id"])
```

The installed CLI exposes a guided subcommand runner for shell users:

```bash
circle-ai-certify rope \
  --model-config-file examples/circle_ai_model_configs/standard_rope_config.json \
  --request-out /tmp/circle_rope_request.json \
  --request-validation-report-out /tmp/circle_rope_request_validation.json \
  --model-config-import-report-out /tmp/circle_rope_import_report.json \
  --format json

circle-ai-certify kv-cache \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31 \
  --sink-size 4 \
  --require-passed \
  --format json

circle-ai-certify sparse-attention \
  --context 9 \
  --strides 3,4,7 \
  --path-length 2 \
  --local-window 2 \
  --json-out /tmp/circle_sparse_receipt.json \
  --gate-report-out /tmp/circle_sparse_gate.json \
  --receipt-replay-check-out /tmp/circle_sparse_replay.json \
  --certification-bundle-out /tmp/circle_sparse_bundle.json \
  --certification-bundle-check-out /tmp/circle_sparse_bundle_check.json \
  --artifact-manifest-out /tmp/circle_sparse_manifest.json \
  --artifact-manifest-check-out /tmp/circle_sparse_manifest_check.json \
  --format json
```

Use `--gate-report-out` when downstream CI needs a compact machine-readable
pass/fail report, `--receipt-check-out` when it wants a pack-aware receipt
validation artifact, and `--receipt-replay-check-out` when it wants to rebuild
the receipt from the embedded request and compare stable fingerprints. Use
`--request-validation-report-out` when it wants the request preflight saved as
a standalone JSON artifact. Use
`--certification-bundle-out` and `--certification-bundle-check-out` when the
handoff should carry the request preflight, theorem-linked receipt, gate
report, and bundle validation result as one archived object. Use
`--artifact-manifest-out` and `--artifact-manifest-check-out` when the handoff
also needs file fingerprints and a manifest self-check for every sidecar this
invocation wrote.

The lower-level installed receipt command accepts kind aliases plus JSON
parameters directly:

```bash
circle-ai-contract-receipt \
  --kind rope \
  --model-config-file examples/circle_ai_model_configs/standard_rope_config.json \
  --request-out /tmp/circle_rope_request.json \
  --model-config-import-report-out /tmp/circle_rope_import_report.json \
  --format json

circle-ai-contract-receipt \
  --request-file examples/circle_ai_requests/kv_cache_request.json \
  --request-out /tmp/circle_kv_request.json \
  --require-passed \
  --require-status proved \
  --require-decision passed \
  --format json

circle-ai-contract-receipt \
  --kind sparse-attention \
  --parameters '{"context": 9, "strides": [3, 4, 7], "path_length": 2, "local_window": 2}' \
  --format json
```

## Lean Imports

Finite cyclic mathematics:

```lean
import Circle.Core
```

Application facts without huge generated certificate imports:

```lean
import Circle.Applications.Public
```

All public proof-carrying application contracts, including generated RoPE
certificate facts:

```lean
import Circle.Contracts
```

## Rust

The Rust workspace package stays focused on prime and horizon utilities:

```bash
cargo run -p circle-prime -- --help
cargo run -p circle-prime --bin circle-prime-count -- --help
cargo doc -p circle-prime --no-deps
```

Keep new Rust API additions in that scope unless the project deliberately
creates a separate crate.
