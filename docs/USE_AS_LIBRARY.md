# Use Circle Calculus As A Library

This page is the shortest public path for using Circle Calculus as code instead
of reading it as a book. The examples use stable facades:

- Python core: `circle_math.core`
- Python contracts: `circle_math.ai_contracts` and `circle_math.contracts`
- Lean core import: `Circle.Core`
- Lean contract import: `Circle.Contracts`
- Rust crate: `circle-prime`

Claim boundary: the examples below expose finite cyclic structure and
proof-linked receipts. They do not claim model-quality, speed, memory, context
length, physics, or universal-compression improvements.

## Python: Finite Circle Orbit

```python
from circle_math.core import finite_orbit, finite_period, is_full_coil

orbit = finite_orbit(12, 5)
period = finite_period(12, 5)
full = is_full_coil(12, 5)

print(orbit)
print(period)
print(full)
```

Expected output:

```text
[0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7]
12
True
```

## Python: RoPE Contract Receipt

```python
from circle_math.ai_contracts import (
    build_contract_pack,
    build_rope_receipt,
    build_validated_rope_receipt_from_model_config,
)

pack = build_contract_pack()
receipt = build_rope_receipt(
    head_dim=128,
    base=10000,
    context=4096,
    pack=pack,
)

print(receipt["contract_id"])
print(receipt["decision"]["verdict"])
print(receipt["decision"]["claim_status"])
print(receipt["decision"]["all_theorem_ids_proved"])
```

This returns a theorem-linked structural receipt for the declared RoPE request.
Read the `not_claimed` field before treating the receipt as an engineering
result.

For a model-style config object, use the standard-RoPE importer:

```python
model_config = {
    "hidden_size": 4096,
    "num_attention_heads": 32,
    "max_position_embeddings": 4096,
    "rope_theta": 10000.0,
}

receipt = build_validated_rope_receipt_from_model_config(model_config, pack=pack)
print(receipt["request"]["parameters"])
```

## Python: Sparse-Attention Coverage Contract

```python
from circle_math.ai_contracts import (
    build_contract_pack,
    build_sparse_attention_receipt,
)

pack = build_contract_pack()
receipt = build_sparse_attention_receipt(
    context=9,
    strides=(3, 4, 7),
    path_length=2,
    local_window=2,
    pack=pack,
)

print(receipt["contract_id"])
print(receipt["decision"]["verdict"])
print(receipt["evidence"]["coverage_complete"])
print(receipt["evidence"]["uncovered_lag_count"])
```

The compact fixture above is a complete finite coverage example. For a gap
example with explicit uncovered lags, use `context=120`, `strides=(7, 13)`,
`path_length=3`, and `local_window=4`.

## CLI Entry Points

After `python -m pip install -e .`, these package-native entry points are
available:

```bash
circle-ai-certify rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --request-out /tmp/circle_rope_request.json --model-config-import-report-out /tmp/circle_rope_import_report.json --format json
circle-ai-certify kv-cache --cache-size 16 --current 31 --token 20 --batch-tokens 20,24,29,31 --sink-size 4 --require-passed --format json
circle-ai-certify sparse-attention --context 9 --strides 3,4,7 --path-length 2 --local-window 2 --format json
circle-ai-certify recurrence --format json
circle-ai-contract-ready --kind sparse_attention_coverage
circle-ai-contract-receipt --kind rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --request-out /tmp/circle_rope_request.json --model-config-import-report-out /tmp/circle_rope_import_report.json
circle-ai-contract-receipt --request-file examples/circle_ai_requests/kv_cache_request.json --request-out /tmp/circle_kv_request.json
circle-ai-contract-receipt --request-file examples/circle_ai_requests/kv_cache_request.json --require-passed --require-status proved --require-decision passed
circle-ai-contract-receipt --kind sparse-attention --parameters '{"context": 9, "strides": [3, 4, 7], "path_length": 2, "local_window": 2}'
circle-rope-certify --preset llama_style_10000_4k
circle-sparse-attention-certify --context 9 --strides 3,4,7 --path-length 2 --local-window 2
```

`circle-ai-certify` is the installed-package path for guided RoPE, KV-cache,
sparse-attention, recurrence, and request-file receipts without using the
repository-only scripts. It accepts `--model-config-file` for standard RoPE
configs and writes the same theorem-linked receipt shape as the lower-level
receipt command. Use `--request-out` to save the exact versioned Circle request
and `--model-config-import-report-out` to save the parameter-source audit
report for a RoPE model config.
`circle-ai-contract-receipt` remains available when callers already have a kind
alias and JSON parameter object.
Use `--request-file` when the input is already a versioned Circle request for
RoPE, KV-cache, sparse attention, or recurrence.
Use `--require-passed`, `--require-status`, `--require-decision`, and
`--require-assurance` when the command is part of downstream CI. Gate failures
return exit code `2` after writing the receipt, so CI logs keep the theorem
ids, proof layers, and non-claims needed to debug the rejection.
Use `--gate-report-out`, `--receipt-check-out`, and
`--receipt-replay-check-out` when CI should save compact machine-readable
receipt diagnostics without using repository-only scripts. Use
`--certification-bundle-out` with `--certification-bundle-check-out` when the
installed CLI should also archive a request-validation, receipt, gate, and
bundle-check handoff object.

Non-default `rope_scaling` values are rejected by the standard-RoPE importer.
That rejection is intentional: scaled-RoPE variants need separate theorem
coverage before the CLI may certify them as standard RoPE.

The richer repository maintenance commands under `scripts/` are still the
source-tree tools for generating and validating all artifacts.

## Lean Imports

For finite cyclic mathematics:

```lean
import Circle.Core
```

For proof-carrying application contracts:

```lean
import Circle.Contracts
```

For application facts without large generated RoPE certificate files:

```lean
import Circle.Applications.Public
```

## Rust Prime Engine

The Rust workspace package remains focused on prime and horizon utilities:

```bash
cargo run -p circle-prime -- --help
cargo run -p circle-prime --bin circle-prime-count -- --help
cargo test -p circle-prime
```

Rust crate docs should build with:

```bash
cargo doc -p circle-prime --no-deps
```
