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
    build_architecture_config_certification_bundle,
    build_contract_certification_bundle,
    build_architecture_config_import_report,
    build_contract_pack,
    build_contract_runner_check_report,
    build_rope_model_config_certification_bundle,
    build_rope_receipt,
    build_validated_contract_receipt_from_architecture_config,
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
rope_bundle = build_rope_model_config_certification_bundle(
    model_config,
    pack=pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
)
assert rope_bundle["model_config_import_report"]["request"] == (
    receipt_from_config["request"]
)

architecture_config = {
    "kv_cache": {"cache_size": 16, "current": 31, "token": 20},
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
architecture_report = build_architecture_config_import_report(
    "sparse-attention",
    architecture_config,
)
assert architecture_report["ok"] is True
architecture_receipt = build_validated_contract_receipt_from_architecture_config(
    "sparse-attention",
    architecture_config,
    pack=pack,
)
assert architecture_receipt["kind"] == "sparse_attention_coverage"
architecture_bundle = build_architecture_config_certification_bundle(
    "sparse-attention",
    architecture_config,
    pack=pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("theorem_backed",),
    require_passed=True,
)
assert architecture_bundle["architecture_config_import_report"]["request"] == (
    architecture_receipt["request"]
)

runner_report = build_contract_runner_check_report(
    model_configs=[model_config],
    architecture_configs=[architecture_config],
    model_config_source_paths=["standard_rope_config.json"],
    architecture_config_source_paths=["basic_transformer_contract_config.json"],
    required_kinds=("rope", "kv-cache", "sparse-attention", "recurrence"),
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    pack=pack,
)
assert runner_report["schema_id"] == "circle_calculus.ai_contract_runner_check.v0"
assert runner_report["ok"] is True
```

Pass `require_no_unsupported_architecture_fields=True` when an in-memory
architecture-config batch should fail if a source field was present but not
mapped into the theorem-linked request. The default keeps those fields visible
in `unsupported_architecture_config_fields` without rejecting the receipt.

For partial-rotary configs, the importer uses `partial_rotary_factor` or
`rotary_pct` to reduce the certified RoPE dimension and records both source
fields in the model-config import report. If the config already exposes an
explicit rotary dimension such as `rotary_dim`, `rotary_emb_dim`,
`rotary_ndims`, `qk_rope_head_dim`, or `rope_head_dim`, that field is treated
as the certified RoPE dimension and the rotary fraction is not applied again.
Non-default `rope_scaling` remains outside the standard-RoPE importer.
For base/theta, the importer accepts `rope_theta`, `rope_base`,
`rotary_emb_base`, `rotary_base`, or `rotary_theta`.
For context length, the importer accepts `max_position_embeddings`,
`max_seq_len`, `max_seq_length`, `max_sequence_length`, `model_max_length`,
`seq_len`, `context_length`, `seq_length`, or `n_positions`.

For project-level AI configs, the facade exposes a source-tracked architecture
adapter for explicit RoPE, KV-cache, sparse-attention, and recurrence contracts:

```python
from circle_math.ai_contracts import (
    build_architecture_config_certification_bundle,
    build_architecture_config_import_json_schema,
    build_architecture_config_import_report,
    build_contract_request_from_architecture_config,
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
    "sparse_attention": {
        "context_length": 9,
        "strides": [3, 4, 7],
        "max_hops": 2,
        "local_window": 2,
    }
}

report = build_architecture_config_import_report(
    "sparse-attention",
    architecture_config,
)
schema = build_architecture_config_import_json_schema()
assert report["ok"] is True

request = build_contract_request_from_architecture_config(
    "sparse-attention",
    architecture_config,
)
receipt = build_validated_contract_receipt_from_architecture_config(
    "sparse-attention",
    architecture_config,
    pack=pack,
)
assert receipt["request"] == request
bundle = build_architecture_config_certification_bundle(
    "sparse-attention",
    architecture_config,
    pack=pack,
)
assert bundle["architecture_config_import_report"]["request"] == request
```

The config adapter is deterministic translation/provenance only; the receipt is
the theorem-linked artifact. The import-report schema builder matches
`site/data/generated/circle_ai_architecture_config_import.schema.json`. The same
stable facade also exposes `build_contract_certification_bundle` for already
versioned requests, plus `build_rope_model_config_certification_bundle` and
`build_architecture_config_certification_bundle` when a downstream handoff
should carry request preflight, receipt, gate report, and config-to-request
provenance in one object.
The same in-memory runner-check helper accepts architecture configs and emits
RoPE, KV-cache, sparse-attention, and recurrence summaries by default. Pass
`architecture_config_kinds=("sparse-attention",)` when a caller only needs one
family. Use `architecture_config_selected_contract_kinds(config, defaults)` or
`architecture_config_contract_kind_hints(config)` from `circle_math.ai_contracts`
when a downstream adapter wants to honor the same `circle_ai_contract_kinds`
metadata before running its own targeted validation.

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

When installed as a Python package, Circle Calculus includes
`circle_math/data/generated/theorem_status_index.json` as a compact theorem
status fallback. That package data lets contract readiness resolve theorem ids
when the source repository's `manifests/` directory is not available.

The installed CLI exposes a guided subcommand runner for shell users:

```bash
circle-ai-certify rope \
  --model-config-file examples/circle_ai_model_configs/standard_rope_config.json \
  --artifact-dir /tmp/circle_rope_contract \
  --request-out /tmp/circle_rope_request.json \
  --request-validation-report-out /tmp/circle_rope_request_validation.json \
  --model-config-import-report-out /tmp/circle_rope_import_report.json \
  --format json

circle-ai-certify rope \
  --architecture-config-file examples/circle_ai_architecture_configs/basic_transformer_contract_config.json \
  --architecture-config-import-report-out /tmp/circle_rope_architecture_import.json \
  --format json \
  --require-passed

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

circle-ai-certify batch \
  --request-file examples/circle_ai_requests/kv_cache_request.json \
  --request-file examples/circle_ai_requests/sparse_attention_request.json \
  --model-config-file examples/circle_ai_model_configs/standard_rope_config.json \
  --architecture-config-file examples/circle_ai_architecture_configs/basic_transformer_contract_config.json \
  --artifact-dir /tmp/circle_ai_contract_batch \
  --artifact-prefix architecture-suite \
  --require-passed \
  --require-status proved \
  --require-decision passed \
  --format json

circle-ai-certify strided-fanout --format compact-json
circle-ai-certify cyclic-memory --format compact-json
circle-ai-certify multicoil-phase --format compact-json
circle-ai-certify cyclic-mixer --format compact-json
circle-ai-certify seed-rule --format compact-json
```

Add `--require-no-unsupported-architecture-fields` to `circle-ai-certify batch`
when the generated runner-check report should fail if an architecture config
contains fields that Circle did not map into a theorem-linked request.

For RoPE imports, `--model-config-file` may point directly at a JSON file or at
a model directory containing `config.json`.

Use `--gate-report-out` when downstream CI needs a compact machine-readable
pass/fail report, `--receipt-check-out` when it wants a pack-aware receipt
validation artifact, and `--receipt-replay-check-out` when it wants to rebuild
the receipt from the embedded request and compare stable fingerprints. Use
`--format compact-json` or `--compact-json-out` when the handoff should expose
only the stable decision, selected evidence, theorem summary, validation
commands, non-claims, and full receipt fingerprint. In text mode,
single-receipt commands print each replay/check command as a
`validation_command=...` line. Parameterized receipts keep the repository-script
replay first for strict audit checks and the installed `circle-ai-certify`
entry-point replay second for downstream projects. Use
`circle-ai-certify batch` when a downstream project already has several
versioned Circle request files, standard RoPE model configs, or project-level
architecture configs and wants per-source full receipts, compact receipts,
model-config and architecture-config import reports, request-validation
preflights, certification bundles, bundle checks, one runner-check summary, and
a batch artifact manifest/check without importing repository-only scripts. Use
`--artifact-dir` when the installed batch command should choose stable
subdirectories and manifest paths for that portable handoff set. Pass
`--require-kind` one or more times when CI should fail unless the batch emits at
least one receipt for each required contract family. The top-level report
records both `required_kinds` and `kind_counts`, and each runner
summary includes both `theorem_count` and the concrete `theorem_ids` cited by
the receipt, plus resolved/proved booleans and any unresolved or unproved
theorem ids. Architecture configs emit RoPE, KV-cache, sparse-attention, and
recurrence receipts by default; pass `--architecture-config-kind` to restrict
that set globally, or set `circle_ai_contract_kinds` inside one architecture
config to restrict that file only. The copyable standard-library verifier
`examples/downstream_ci_verify_circle_ai_batch.py` validates a saved
runner-check report plus every receipt, compact receipt, import report,
request-validation report, certification bundle, and bundle-check sidecar that
the batch report names. When the runner report names a batch artifact manifest,
the verifier also checks its SHA-256 fingerprints and coverage of the runner
report plus every emitted sidecar; pass `--artifact-manifest` only to override
or supply a relocated manifest. The runner report also records a top-level
`validation_commands` list with the JSON-mode verifier command for the handoff.
In text mode, `circle-ai-certify batch` prints the same command as a
`validation_command=...` line so a human can copy it without opening the JSON.
It validates the runner report's own `gate_policy`,
`example_count`, `selected_kinds`, `required_kinds`, and `kind_counts`, so stale
reports with mismatched metadata or missing current policy fields fail before
being accepted as CI evidence. An
accepted verifier report includes a reusable `pin_policy`; pass it back with
`--pin-policy` to reject future batch reports whose runner `gate_policy` has
drifted from the pinned CI contract. Its
summaries preserve unsupported
architecture-config field counts and names, so CI logs keep the boundary
between certified request fields and source-config behavior that was not
claimed. Add `--require-no-unsupported-architecture-fields` when downstream CI
should reject any architecture config whose extra fields were not mapped into a
theorem-linked request. For single-receipt commands, use `--artifact-manifest-out` and
`--artifact-manifest-check-out` when the handoff also needs file fingerprints and
a manifest self-check for every sidecar that invocation wrote.

The lower-level installed receipt command accepts kind aliases plus JSON
parameters directly. The same receipt shape works for all nine ready families:
`rope`, `kv-cache`, `sparse-attention`, `recurrence`, `strided-fanout`,
`cyclic-memory`, `multicoil-phase`, `cyclic-mixer`, and `seed-rule`.

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

For RoPE imports, `--model-config-file` accepts either the `config.json` file
itself or the containing model directory.

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
