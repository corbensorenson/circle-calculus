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

Finite Fourier and circulant helpers are also stable through `circle_math.core`:

```python
from circle_math.core import circular_convolution, spectral_convolution_report

kernel = [2, 0, 1, 0]
signal = [1, 2, 0, -1]

assert circular_convolution(kernel, signal) == [2 + 0j, 3 + 0j, 1 + 0j, 0 + 0j]
assert spectral_convolution_report(kernel, signal).passed is True
```

The Lean proof spine for these helpers lives in `Circle.Core.FiniteFourier` and
`Circle.Applications.CirculantSpectral`; see
[FINITE_FOURIER_CIRCULANT.md](FINITE_FOURIER_CIRCULANT.md).

Finite circular-statistics helpers are stable through `circle_math.core`:

```python
from math import tau

from circle_math.core import circular_mean_report, finite_residue_histogram

assert finite_residue_histogram(5, [0, 5, 7, 12]) == {0: 2, 2: 2}
report = circular_mean_report([0.0, tau / 4.0])
assert report.undefined_mean is False
```

The Lean proof spine for the finite residue layer lives in
`Circle.Applications.CircularStatistics`; see
[CIRCULAR_STATISTICS_CONTRACTS.md](CIRCULAR_STATISTICS_CONTRACTS.md).

Finite cyclic equivariance helpers are stable through `circle_math.core`:

```python
from circle_math.core import circulant_equivariance_report, cyclic_shift

assert cyclic_shift([1, 2, 3, 4], 1) == (4 + 0j, 1 + 0j, 2 + 0j, 3 + 0j)
report = circulant_equivariance_report([2, 0, 1, 0], [[1, 2, 0, -1]])
assert report.passed is True
```

The Lean proof spine for this layer lives in
`Circle.Applications.CyclicEquivariance`; see
[CYCLIC_EQUIVARIANCE.md](CYCLIC_EQUIVARIANCE.md).

Finite phase-loop helpers are stable through `circle_math.core`:

```python
from circle_math.core import phase_lock_report, phase_loop_report

loop = phase_loop_report(12, [3, 4, 7], base_gauge=5)
assert loop.charge == 2
assert loop.closed_loop_gauge_invariant is True

locked = phase_lock_report(12, [1, 13, 25])
assert locked.all_locked is True
```

The Lean proof spine for this layer lives in `Circle.Applications.PhaseLoop`;
see [PHASE_LOOP_CONTRACTS.md](PHASE_LOOP_CONTRACTS.md).

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

The same facade exposes reusable integer phase-bank helpers for sinusoidal,
RoPE-family, scaled, and 2D positional phase descriptors:

```python
from circle_math.ai_contracts import (
    phase_bank_collision_report,
    phase_bank_from_periods,
)

bank = phase_bank_from_periods("diagnostic", [6, 9, 13])
report = phase_bank_collision_report(bank, 0, 36)
assert report.witness_channels == ("phase_2",)
```

The Lean proof spine for this layer lives in
`Circle.Applications.PositionPhase`; see
[POSITION_PHASE_BANKS.md](POSITION_PHASE_BANKS.md).

It also exposes a graph-shaped sparse-attention coverage wrapper:

```python
from circle_math.ai_contracts import circle_graph_coverage_report

report = circle_graph_coverage_report(
    context=9,
    strides=(3, 4, 7),
    path_length=2,
    local_window=2,
)
assert report.coverage_complete is True
```

The Lean wrapper surface lives in `Circle.Applications.CircleGraphCoverage`;
see [CIRCLE_GRAPH_COVERAGE.md](CIRCLE_GRAPH_COVERAGE.md).

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
  --artifact-dir /tmp/circle_rope_contract \
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
  --compact-json-out /tmp/circle_sparse_compact_receipt.json \
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
`--format compact-json` or `--compact-json-out` when the handoff should expose
only the stable decision, selected evidence, theorem summary, validation
commands, non-claims, and full receipt fingerprint. Use
`--request-validation-report-out` when it wants the request preflight saved as
a standalone JSON artifact. Use
`--certification-bundle-out` and `--certification-bundle-check-out` when the
handoff should carry the request preflight, theorem-linked receipt, gate
report, and bundle validation result as one archived object. Use
`--artifact-manifest-out` and `--artifact-manifest-check-out` when the handoff
also needs file fingerprints and a manifest self-check for every sidecar this
invocation wrote. Use `--artifact-dir` when the installed command should choose
stable names for the complete request, receipt, diagnostics, bundle, manifest,
and check-report set.

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
