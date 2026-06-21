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
circle-ai-certify rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --request-out /tmp/circle_rope_request.json --request-validation-report-out /tmp/circle_rope_request_validation.json --model-config-import-report-out /tmp/circle_rope_import_report.json --format json
circle-ai-certify kv-cache --cache-size 16 --current 31 --token 20 --batch-tokens 20,24,29,31 --sink-size 4 --require-passed --format json
circle-ai-certify sparse-attention --context 9 --strides 3,4,7 --path-length 2 --local-window 2 --format json
circle-ai-certify sparse-attention --context 9 --strides 3,4,7 --path-length 2 --local-window 2 --format compact-json
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
and `--request-validation-report-out` to save the schema-validated request
preflight report. Use `--model-config-import-report-out` to save the
parameter-source audit report for a RoPE model config.
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
`--format compact-json` or `--compact-json-out` when downstream tools only need
the stable receipt decision, selected evidence, theorem summary, replay
commands, non-claims, and the full receipt fingerprint. Use
`--certification-bundle-out` with `--certification-bundle-check-out` when the
installed CLI should also archive a request-validation, receipt, gate, and
bundle-check handoff object. Use `--artifact-manifest-out` with
`--artifact-manifest-check-out` when it should also fingerprint the sidecar
files and verify the manifest. Use `--artifact-dir` when it should choose
stable names for the full sidecar set automatically.

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
