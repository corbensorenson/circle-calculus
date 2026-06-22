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

## Python: Finite Fourier And Circulant Algebra

```python
from circle_math.core import (
    circular_convolution,
    spectral_aliasing_report,
    spectral_convolution_report,
)

signal = [1, 2, 0, -1]
kernel = [2, 0, 1, 0]

print(circular_convolution(kernel, signal))
print(spectral_convolution_report(kernel, signal).passed)
print(spectral_aliasing_report(4, [-1, 0, 3, 4, 7]))
```

The corresponding Lean facts are in `Circle.Core.FiniteFourier` and
`Circle.Applications.CirculantSpectral`. The executable residual check is a
floating-point diagnostic; the algebraic identities are the Lean-proved layer.

## Python: Position Phase Bank

```python
from circle_math.ai_contracts import (
    phase_bank_collision_report,
    phase_bank_from_periods,
)

bank = phase_bank_from_periods("diagnostic", [6, 9, 13])
report = phase_bank_collision_report(bank, 0, 36)

print(report.all_channels_collide)
print(report.witness_channels)
print([row.period_divides_gap for row in report.channel_results])
```

Expected output:

```text
False
('phase_2',)
[True, True, False]
```

The corresponding Lean facts are in `Circle.Applications.PositionPhase`.
This is an exact integer-period residue contract. It is not a real-valued
RoPE, xPos, YaRN, LongRoPE, model-quality, or context-length proof.

## Python: Circle Graph Coverage

```python
from circle_math.ai_contracts import circle_graph_coverage_report

report = circle_graph_coverage_report(
    context=9,
    strides=(3, 4, 7),
    path_length=2,
    local_window=2,
)

print(report.coverage_complete)
print(report.uncovered_lags)
print(report.directed_edge_count)
```

Expected output:

```text
True
()
72
```

The corresponding Lean facts are in `Circle.Applications.CircleGraphCoverage`.
This is a finite direct-lag coverage contract, not a sparse-attention quality,
speed, or memory claim.

## Python: Circular Statistics

```python
from math import tau

from circle_math.core import (
    circular_mean_report,
    finite_residue_histogram,
    finite_wrapped_distance,
)

print(finite_wrapped_distance(12, 1, 11))
print(finite_residue_histogram(5, [0, 5, 7, 12], include_zero_counts=True))

report = circular_mean_report([0.0, tau / 4.0])
print(report.mean_angle)
print(report.mean_resultant_length)
print(report.undefined_mean)
```

The corresponding Lean facts are in
`Circle.Applications.CircularStatistics`. The finite residue and histogram
helpers are proof-facing; the real-valued mean/resultant fields are executable
floating-point diagnostics, not statistical-quality or numerical-stability
proofs.

## Python: Cyclic Equivariance

```python
from circle_math.core import (
    circulant_equivariance_report,
    cyclic_sum_invariance_report,
    dihedral_transform,
)

print(dihedral_transform([10, 20, 30, 40], shift=1, reflected=True))

report = circulant_equivariance_report(
    [2, 0, 1, 0],
    [[1, 2, 0, -1], [0, 3, 1, 2]],
)
print(report.passed)
print(report.max_abs_delta)

pooling = cyclic_sum_invariance_report([[1, 2, 3, 4]])
print(pooling.passed)
```

The corresponding Lean facts are in
`Circle.Applications.CyclicEquivariance`. This proves finite shift/reflection
structure and circulant-layer cyclic equivariance, not continuous rotation
equivariance, robustness, or model quality.

## Python: Phase Loop And Locking

```python
from circle_math.core import phase_lock_report, phase_loop_report

loop = phase_loop_report(12, [3, 4, 7], base_gauge=5)
print(loop.charge)
print(loop.reverse_charge)
print(loop.charge_plus_reverse)
print(loop.closed_loop_gauge_invariant)

locked = phase_lock_report(12, [1, 13, 25])
print(locked.all_locked)
print(locked.order_parameter)
```

The corresponding Lean facts are in `Circle.Applications.PhaseLoop`. This is a
finite modular phase-loop contract, not a Kuramoto stability, synchronization,
continuum-vortex, quantum-holonomy, or physics proof.

## Python: RoPE Contract Receipt

```python
from circle_math.ai_contracts import (
    build_contract_pack,
    build_rope_model_config_certification_bundle,
    build_rope_receipt,
    build_validated_rope_receipt_from_model_config,
)

pack = build_contract_pack()
receipt = build_rope_receipt(
    head_dim=128,
    base=10000,
    context=4096,
    requested_margin="1/328459",
    pack=pack,
)

print(receipt["contract_id"])
print(receipt["decision"]["verdict"])
print(receipt["decision"]["claim_status"])
print(receipt["decision"]["all_theorem_ids_proved"])
print(receipt["evidence"]["standard_channel0_d19_bank_bridge"]["applies"])
```

This returns a theorem-linked structural receipt for the declared RoPE request.
With the requested margin above, the D19 first-channel bank bridge is the
theorem-backed payload that makes the smaller-context request pass. It is still
conditional on the standard channel-0 first-frequency bank shape. Read the
`not_claimed` field before treating the receipt as an engineering result.

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

bundle = build_rope_model_config_certification_bundle(
    model_config,
    pack=pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
)
print(bundle["model_config_import_report"]["parameter_sources"])
```

If the model config declares `partial_rotary_factor` or `rotary_pct`, the
standard-RoPE importer certifies the resulting rotary sub-dimension rather than
the full attention-head dimension. The import report records both the head
dimension source and the rotary-fraction source so downstream CI can audit the
conversion. If the config already declares an explicit rotary dimension such as
`rotary_dim`, `rotary_emb_dim`, `rotary_ndims`, `qk_rope_head_dim`, or
`rope_head_dim`, the importer uses that value directly and does not apply the
rotary fraction again. For context length, it accepts
`max_position_embeddings`, `max_seq_len`, `max_seq_length`,
`max_sequence_length`, `model_max_length`, `seq_len`, `context_length`,
`seq_length`, or `n_positions`. For base/theta, it accepts `rope_theta`,
`rope_base`, `rotary_emb_base`, `rotary_base`, or `rotary_theta`.

For project-level architecture configs, use the explicit architecture adapter.
It currently covers explicit RoPE, KV-cache, sparse-attention, and recurrence
contracts:

```python
from circle_math.ai_contracts import (
    build_architecture_config_certification_bundle,
    build_architecture_config_import_report,
    build_architecture_config_import_json_schema,
    build_validated_contract_receipt_from_architecture_config,
)

architecture_config = {
    "rope": {
        "head_dim": 128,
        "base": 10000.0,
        "context_length": 4096,
        "requested_margin": "1/4099",
        "turn_ratio_numerator": 1,
        "turn_ratio_denominator": 4099,
    },
    "kv_cache": {"cache_size": 16, "current": 31, "token": 20, "sink_size": 4},
    "sparse_attention": {
        "context_length": 9,
        "strides": [3, 4, 7],
        "max_hops": 2,
        "local_window": 2,
    },
    "recurrence": {
        "period": 5,
        "horizon_steps": 7,
        "tokens": 8,
        "block_start": 2,
        "block_width": 3,
        "shift_amount": 15,
    },
}

report = build_architecture_config_import_report(
    "sparse-attention",
    architecture_config,
)
assert report["ok"]
schema = build_architecture_config_import_json_schema()

receipt = build_validated_contract_receipt_from_architecture_config(
    "kv-cache",
    architecture_config,
    pack=pack,
)
assert receipt["kind"] == "kv_cache_ring_buffer"

bundle = build_architecture_config_certification_bundle(
    "kv-cache",
    architecture_config,
    pack=pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    require_passed=True,
)
print(bundle["architecture_config_import_report"]["parameter_sources"])
```

The architecture import report is provenance, not proof. It records which config
field or explicit override supplied each request parameter; the receipt remains
the theorem-linked artifact. The schema builder above matches
`site/data/generated/circle_ai_architecture_config_import.schema.json`.
The report also lists unsupported fields inside the target section, so a
downstream project can see when extra architecture behavior was present but not
certified by the emitted request.
For recurrence configs, `shift_amount` is translated to `shift_passes` only when
it is a nonnegative exact multiple of `loop_period`; the import report labels
that parameter source as derived instead of treating a token shift as a pass
count.
Use `build_rope_model_config_certification_bundle` or
`build_architecture_config_certification_bundle` when downstream code wants
config-to-request provenance alongside the request preflight, receipt, and gate
report in one in-memory object.

For in-memory batch checks, use the same runner-check report shape without a
subprocess:

```python
from circle_math.ai_contracts import build_contract_runner_check_report

runner_report = build_contract_runner_check_report(
    model_configs=[model_config],
    architecture_configs=[architecture_config],
    model_config_source_paths=["standard_rope_config.json"],
    architecture_config_source_paths=["basic_transformer_contract_config.json"],
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    pack=pack,
)

print(runner_report["schema_id"])
print(runner_report["ok"])
print(runner_report["summaries"][0]["model_config_parameter_sources"])
```

When `architecture_configs` is populated, the in-memory report emits RoPE,
KV-cache, sparse-attention, and recurrence receipts by default, matching
`circle-ai-certify batch --architecture-config-file`. Pass
`architecture_config_kinds=("sparse-attention",)` when a downstream job only
needs one contract family.

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
circle-ai-certify rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --request-out /tmp/circle_rope_request.json --request-validation-report-out /tmp/circle_rope_request_validation.json --model-config-import-report-out /tmp/circle_rope_import_report.json --format json
circle-ai-certify rope --architecture-config-file examples/circle_ai_architecture_configs/basic_transformer_contract_config.json --architecture-config-import-report-out /tmp/circle_rope_architecture_import.json --format json --require-passed
circle-ai-certify kv-cache --cache-size 16 --current 31 --token 20 --batch-tokens 20,24,29,31 --sink-size 4 --require-passed --format json
circle-ai-certify kv-cache --architecture-config-file examples/circle_ai_architecture_configs/basic_transformer_contract_config.json --architecture-config-import-report-out /tmp/circle_kv_architecture_import.json --format json
circle-ai-certify sparse-attention --context 9 --strides 3,4,7 --path-length 2 --local-window 2 --format json
circle-ai-certify sparse-attention --context 9 --strides 3,4,7 --path-length 2 --local-window 2 --format compact-json
circle-ai-certify batch --request-file examples/circle_ai_requests/kv_cache_request.json --request-file examples/circle_ai_requests/sparse_attention_request.json --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --architecture-config-file examples/circle_ai_architecture_configs/basic_transformer_contract_config.json --artifact-dir /tmp/circle_ai_contract_batch --artifact-prefix architecture-suite --require-passed --require-status proved --require-decision passed --format json
circle-ai-certify recurrence --format json
circle-ai-certify strided-fanout --format compact-json
circle-ai-certify cyclic-memory --format compact-json
circle-ai-certify multicoil-phase --format compact-json
circle-ai-certify cyclic-mixer --format compact-json
circle-ai-certify seed-rule --format compact-json
circle-ai-contract-ready --kind sparse_attention_coverage
circle-ai-contract-receipt --kind rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --request-out /tmp/circle_rope_request.json --model-config-import-report-out /tmp/circle_rope_import_report.json
circle-ai-contract-receipt --request-file examples/circle_ai_requests/kv_cache_request.json --request-out /tmp/circle_kv_request.json
circle-ai-contract-receipt --request-file examples/circle_ai_requests/kv_cache_request.json --require-passed --require-status proved --require-decision passed
circle-ai-contract-receipt --kind sparse-attention --parameters '{"context": 9, "strides": [3, 4, 7], "path_length": 2, "local_window": 2}'
circle-rope-certify --preset llama_style_10000_4k
circle-sparse-attention-certify --context 9 --strides 3,4,7 --path-length 2 --local-window 2
```

`circle-ai-certify` is the installed-package path for guided RoPE, KV-cache,
sparse-attention, recurrence, strided-fanout, cyclic-memory, multicoil-phase,
cyclic-mixer, seed-rule, and request-file receipts without using the
repository-only scripts. It accepts `--model-config-file` for standard RoPE
configs and writes the same theorem-linked receipt shape as the lower-level
receipt command. For RoPE imports, `--model-config-file` may point directly at
the JSON file or at the containing model directory with `config.json`. Use
`--request-out` to save the exact versioned Circle request and
`--request-validation-report-out` to save the schema-validated request preflight
report. Use `--model-config-import-report-out` to save the parameter-source
audit report for a RoPE model config. Use
`--architecture-config-import-report-out` with `--architecture-config-file` on
RoPE, KV-cache, sparse-attention, or recurrence runs to save the same
parameter-source audit boundary for architecture configs.
Installed wheels carry a generated theorem-status snapshot under
`circle_math/data/generated/theorem_status_index.json`, so contract readiness
can still resolve theorem ids when the repository `manifests/` directory is not
present.
`circle-ai-contract-receipt` remains available when callers already have a kind
alias and JSON parameter object.
Use `--request-file` when the input is already a versioned Circle request for
RoPE, KV-cache, sparse attention, or recurrence.
Use `circle-ai-certify batch` when downstream CI has several versioned request
files, standard RoPE model configs, or architecture configs and should
write per-source full receipts, compact receipts, model-config and
architecture-config import reports, request-validation preflights,
certification bundles, bundle checks, and one schema-validated runner-check
report without depending on repository-only scripts. Use `--artifact-dir` when
the installed batch command should choose stable subdirectories for that
portable handoff set. By default, each architecture config emits RoPE,
KV-cache, sparse-attention, and recurrence receipts; pass
`--architecture-config-kind` to restrict that set. The copyable
standard-library verifier `examples/downstream_ci_verify_circle_ai_batch.py`
validates a saved runner-check report plus every sidecar path that report names
without importing Circle.
Use `--require-passed`, `--require-status`, `--require-decision`, and
`--require-assurance` when the command is part of downstream CI. Gate failures
return exit code `2` after writing the receipt, so CI logs keep the theorem
ids, proof layers, and non-claims needed to debug the rejection.
Use `--gate-report-out`, `--receipt-check-out`, and
`--receipt-replay-check-out` when CI should save compact machine-readable
receipt diagnostics without using repository-only scripts. Use
`--format compact-json` or `--compact-json-out` when downstream tools only need
the stable receipt decision, selected evidence, theorem summary, replay
commands, non-claims, and the full receipt fingerprint. Use
`--certification-bundle-out` with `--certification-bundle-check-out` when the
installed CLI should also archive a request-validation, receipt, gate, and
bundle-check handoff object. For single-receipt commands, use
`--artifact-manifest-out` with `--artifact-manifest-check-out` when it should
also fingerprint the sidecar files and verify the manifest. Use
`--artifact-dir` when it should choose stable names for the sidecar set
automatically.

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
