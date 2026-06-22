# Circle AI Contract Runner

The contract runner is the parameterized surface for the proof-carrying AI lane.
It takes a user configuration and emits a text summary, full JSON receipt, or
compact JSON receipt view with:

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

python scripts/circle_ai_certify.py rope \
  --head-dim 128 \
  --base 10000 \
  --context 131072 \
  --requested-margin 1/328459 \
  --format compact-json \
  --compact-json-out reports/rope_compact_receipt.json

python scripts/circle_ai_certify.py rope \
  --context 4096 \
  --requested-margin 1/4099 \
  --turn-ratio-numerator 1 \
  --turn-ratio-denominator 4099 \
  --format json

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

python scripts/circle_ai_certify.py recurrence \
  --period 6 \
  --position 9 \
  --horizon-steps 8 \
  --sequence-length 24 \
  --block-start 6 \
  --block-width 6 \
  --shift-amount 18

python scripts/circle_ai_certify.py strided-fanout

python scripts/circle_ai_certify.py cyclic-memory

python scripts/circle_ai_certify.py multicoil-phase

python scripts/circle_ai_certify.py cyclic-mixer

python scripts/circle_ai_certify.py seed-rule
```

Add `--format json` for the full machine-readable audit receipt, `--json-out
PATH` to write that full receipt to disk, and `--request-out PATH` to save the
exact versioned request JSON used by the run. Add `--format compact-json` when
another project only needs the stable downstream-consumer view: decision,
proof-status summary, selected evidence fields, theorem ids, validation
commands, non-claims, and fingerprints. Use `--compact-json-out PATH` to write
that compact view; `--json-out` remains the full audit receipt so receipt-check
and artifact-manifest checks keep their source of truth. Add
`--request-validation-report-out PATH` when a direct single-config run should
also save the schema-validated preflight report for the exact request that
produced the receipt. Add
`--certification-bundle-out PATH` when CI wants one schema-validated artifact
containing request preflight, receipt, gate report, and any model-config or
architecture-config import report that records parameter provenance.

For CI gates, add `--require-status STATUS`, `--require-decision VERDICT`,
`--require-assurance LEVEL`, and/or `--require-passed`. The runner still prints
or writes the receipt, then exits nonzero if the emitted receipt does not match
the required status, decision verdict, assurance level, or if `request_passed`
is not `true`.
Add `--gate-report-out PATH` when CI also needs a schema-validated JSON gate
report but does not need to save the full receipt. Add `--receipt-check-out
PATH` with `--json-out PATH` when the report should point at a saved receipt
file for audit logs.

For explicitly rationalized or discretized phase policies, add
`--turn-ratio-numerator N --turn-ratio-denominator D` to request the finite
nearest-integer margin certificate for the declared scalar turn ratio `N/D`.
For example, `1/4099` over context `4096` with requested margin `1/4099`
emits `rational_turn_ratio_finite_margin_certificate` and the text line
`rope_rational_turn_ratio=... requested_status=proved`. This is a
theorem-backed certificate for that declared rational/discretized turn ratio,
not a proof that the standard irrational RoPE frequency schedule has the same
margin.

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

The guided runner currently exposes nine ready contract families:

| Family | Command | Main proved/computed surface |
| --- | --- | --- |
| RoPE | `rope` | exact integer-bank distinguishability plus scoped D19 real-phase request classification |
| KV-cache | `kv-cache` | residue slot, retained window, stale-read, and sink-plus-rolling-window facts |
| Sparse attention | `sparse-attention` | finite lag coverage, gaps, repair windows, and candidate-budget fields |
| Recurrence | `recurrence` | finite loop schedule, active/inactive work, exit step, and whole-period shift facts |
| Strided fanout | `strided-fanout` | stride reachability, visited candidate count, and path-budget accounting |
| Cyclic memory | `cyclic-memory` | residue/winding memory address facts for cyclic event banks |
| Multicoil phase | `multicoil-phase` | period-bank residues, repeat horizon, and relative phase features |
| Cyclic mixer | `cyclic-mixer` | circulant/block-cyclic parameter accounting for mixer layouts |
| Seed rule | `seed-rule` | exact regeneration and storage-accounting facts for a deterministic finite generator |

Each family emits the same receipt shape: normalized parameters, theorem ids,
computed fields, unsupported fields, non-claims, recommendations, and
fingerprints. The runner does not claim these contracts improve model quality;
it certifies the finite structural facts that the contract pack actually backs.
For recurrence, looped-transformer aliases such as `--period`,
`--horizon-steps`, and `--shift-amount` normalize to the canonical request
fields `loop_period`, `max_loops`, and `shift_passes`; non-periodic shift
amounts are rejected instead of silently weakening the contract.

For project-level AI configs that already store explicit RoPE, cache,
sparse-attention, or recurrence settings, the runner can translate a small
architecture config into the same versioned request shape:

```bash
python scripts/circle_ai_certify.py rope \
  --architecture-config examples/circle_ai_architecture_configs/basic_transformer_contract_config.json \
  --architecture-config-import-report-out reports/rope_architecture_import.json \
  --format json \
  --require-passed

python scripts/circle_ai_certify.py sparse-attention \
  --architecture-config examples/circle_ai_architecture_configs/basic_transformer_contract_config.json \
  --architecture-config-import-report-out reports/sparse_architecture_import.json \
  --format json \
  --require-passed

python scripts/circle_ai_certify.py recurrence \
  --architecture-config examples/circle_ai_architecture_configs/basic_transformer_contract_config.json \
  --architecture-config-import-report-out reports/recurrence_architecture_import.json \
  --sample-index 9 \
  --format json
```

Supported sections are `rope`, `model`, `transformer`, `kv_cache`,
`sparse_attention`, and `recurrence`, with a small set of documented aliases
such as `rope_theta`, `rotary_dim`, `hidden_size / num_attention_heads`,
`partial_rotary_factor`, `kv_cache_size`, `context_length`, `sliding_window`,
`max_hops`, `max_recurrence_steps`, `horizon_steps`, `loop_budget`, `tokens`,
`middle_block_width`, and `block_width`. If a RoPE architecture section has no
explicit rotary/head dimension but does have hidden size and attention-head
count fields, the import report derives `head_dim` and records the exact fields
used. Recurrence configs may also provide `shift_amount`; it is accepted only
when it is a nonnegative exact multiple of `loop_period`, then the import report
records a derived `shift_passes` source rather than pretending the amount was
already a pass count. Explicit CLI flags override imported fields; an explicit
`--shift-amount` override is recorded as a derived explicit source in the saved
import report. This import step is only deterministic translation/provenance;
the theorem-backed claim is the emitted receipt. Use
`--architecture-config-import-report-out PATH` to save the schema-validated
import report for audit logs. Its schema is
`site/data/generated/circle_ai_architecture_config_import.schema.json`, and its
fields record the source architecture-config fingerprint, the emitted request
fingerprint, parameter-source provenance, unsupported target-section fields,
and any import failures. Unsupported target-section fields do not make the
translation fail by themselves, but they are not part of the theorem-linked
claim and must be reviewed before treating the receipt as a gate for the whole
architecture behavior.
In default text mode, config-backed runs also print a `source_config=` line with
the source path, source config fingerprint, derived request kind, unsupported
architecture-field count/names, and request fingerprint, so a terminal log can
be replayed or pinned later.
When `--certification-bundle-out` is also used with `--architecture-config`,
that same architecture import report is embedded in the bundle beside the
request preflight, receipt, and gate report.

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

Every emitted full receipt is checked against
`site/data/generated/circle_ai_contract_receipt.schema.json` and then validated
against the loaded contract pack before it is printed or written. The pack-aware
check covers the claimed pack fingerprint, contract fingerprint, contract id,
and theorem-id membership. Use `--receipt-schema` to pin a generated schema path
in a downstream project.
By default, emitted receipts are issued against
`site/data/generated/circle_ai_contract_pack.json`, the same public pack used by
the saved-receipt verifier. Use `--pack` only when intentionally testing a
different generated pack.
Compact receipt views are checked against
`site/data/generated/circle_ai_contract_compact_receipt.schema.json`. They are
derived from a validated full receipt and carry the full
`receipt_content_fingerprint`; they are not a substitute for the audit receipt
when reproducing or debugging a contract run. Each compact receipt also includes
`selected_evidence_proof_layers`, a path-to-label map that marks every selected
evidence field as `proved`, `computed`, `numerical_only`, `unsupported`,
`mixed`, or `unclassified`.
For sparse-attention receipts, the compact view includes both lag-side and
query-side collision accounting: no-collision booleans, dedup-loss counts,
pair-collision counts, pair-count-bounds-dedup-loss checks, and
unique-plus-loss-equals-raw accounting. Downstream CI can therefore gate on
candidate alias severity without reopening the full sparse certificate.
The same compact view now exposes selected evidence for the extended ready
families: strided fanout coverage/budget fields, cyclic-memory residue and
alias fields, multicoil repeat/relative-phase fields, cyclic-mixer parameter
accounting, and seed-rule exact-regeneration/storage fields. Fields that are
not in a family contract's theorem-backed minimum consumer set remain labeled
`computed` rather than `proved`.
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
In text mode, config-backed certifier runs print a `source_config=` line before
the optional `artifacts=` line. The `artifacts=` line lists every request,
receipt, gate, bundle, or check file written by that invocation.
Use `--artifact-dir reports/rope_contract` when you want the standard audit set
without naming every file. It fills unset paths for:

```text
<prefix>_request.json
<prefix>_request_validation.json
<prefix>_model_config_import.json       # RoPE model-config runs only
<prefix>_architecture_config_import.json # architecture-config runs only
<prefix>_receipt.json
<prefix>_receipt_check.json
<prefix>_receipt_replay_check.json
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
the manifest's mirrored receipt status fields. When a
`_receipt_replay_check.json` sidecar is present, the manifest-check report also
requires that replay report to be `ok`, that its replay command matches the
embedded request, that all replay comparison fields match, and that its original
and replayed receipt fingerprints match the saved receipt. The saved
`_receipt_check.json`, `_gate_report.json`, and
`_certification_bundle_check.json` sidecars are also audited: each must be `ok`,
use the manifest's gate policy, and point back to the same receipt fingerprint.
Request preflight sidecars are checked too: `_request_validation.json`, RoPE
`_model_config_import.json`, and `_architecture_config_import.json` must be `ok`
and must point back to the same request fingerprint.
Pass the dependency-pin flags below directly to `scripts/circle_ai_certify.py`
with `--artifact-dir` when the first generated `_artifact_manifest_check.json`
should already carry and enforce the reusable `pin_policy`.

Downstream projects can verify a complete artifact directory from that manifest:

```bash
python scripts/check_circle_ai_artifact_manifest.py \
  reports/rope_contract/standard_rope_config_artifact_manifest.json \
  --report-out reports/rope_contract/standard_rope_config_artifact_manifest_check.json
```

The checker validates the manifest schema, referenced file existence,
SHA-256 fingerprints, declared content schema ids, and the receipt summary
fields mirrored into the manifest. It also audits any saved replay-check sidecar
against the receipt fingerprint, so stale replay reports fail the whole artifact
directory instead of being silently listed as extra files. The receipt-check,
gate-report, and bundle-check sidecars get the same semantic treatment: if a
downstream job updates their file hash but leaves stale receipt facts inside,
the manifest check still fails. Request-validation and model-config import
sidecars are also checked against the manifest request fingerprint.
It also accepts `--require-kind`, `--require-theorem-id`,
`--require-evidence-field`, `--require-recommendation-id`, and
`--require-validation-command` for first-party CI jobs that need the same
policy pins as the copyable standalone verifier. For RoPE model-config imports,
add `--require-model-config-fingerprint FINGERPRINT` with the SHA-256 value
from the model-config import report when CI must prove it is checking the same
source `config.json`. For architecture-config imports, add
`--require-architecture-config-fingerprint FINGERPRINT` with the SHA-256 value
from the architecture-config import report. Use `--require-normalized-param
KEY=JSON_VALUE` to pin the parameter value a downstream job depends on.
For a copyable standard-library-only downstream gate, use
`examples/downstream_ci_verify_circle_ai_artifacts.py`; it performs the same
artifact-integrity checks without importing Circle or `jsonschema`. It also
accepts `--pin-policy` with either a whole prior report or just the
`pin_policy` object, and its JSON report records the merged `pin_policy` for
replay. The standalone verifier also validates
`architecture_config_import_report` sidecars against the manifest request
fingerprint and supports the same architecture-config fingerprint pin.
The standard artifact-directory path and standalone verifier are covered for all
nine ready receipt families, so downstream CI can adopt one gate shape across
the current contract suite.
When a downstream job emits multiple manifests, add `--require-kind` for each
contract family that must be present; the verifier fails if any required family
is missing.
Add `--require-theorem-id THEOREM_ID` when the downstream job depends on a
specific theorem appearing in at least one saved receipt artifact.
Add `--require-evidence-field FIELD` or `--require-recommendation-id ID` when
automation consumes a specific receipt field or planner recommendation.
Add `--require-validation-command COMMAND` when CI depends on an exact recheck
command emitted by the receipt.
Add `--require-model-config-fingerprint FINGERPRINT` when a RoPE artifact
directory was produced from a model `config.json` and CI must pin that source
config hash.
Add `--require-architecture-config-fingerprint FINGERPRINT` when an artifact
directory was produced from an architecture config and CI must pin that source
config hash.
Add `--require-normalized-param KEY=JSON_VALUE` when CI needs to pin a top-level
`normalized_request` value such as `head_dim=128` or `sequence_length=32`.
First-party check reports include a `pin_policy` block recording these requested
dependencies, so audit logs show both what was required and what was observed.
Reuse that policy later with `--pin-policy reports/check_report.json`; the
checker accepts either the whole report or just the `pin_policy` object, and
explicit `--require-*` flags are merged with the loaded pins.
`scripts/circle_ai_certify.py --artifact-dir ... --pin-policy
reports/check_report.json` accepts the same shape when regenerating a contract
artifact set under a previously saved dependency policy.

Copyable starting points live under:

```text
examples/circle_ai_requests/rope_request.json
examples/circle_ai_requests/rope_rational_turn_ratio_request.json
examples/circle_ai_requests/kv_cache_request.json
examples/circle_ai_requests/sparse_attention_request.json
examples/circle_ai_requests/recurrence_request.json
examples/circle_ai_requests/strided_fanout_request.json
examples/circle_ai_requests/cyclic_memory_request.json
examples/circle_ai_requests/multicoil_phase_request.json
examples/circle_ai_requests/cyclic_mixer_request.json
examples/circle_ai_requests/seed_rule_request.json
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
  --compact-receipt-out-dir reports/circle_ai_compact_receipts \
  --model-config-import-report-out-dir reports/circle_ai_imports \
  --architecture-config-import-report-out-dir reports/circle_ai_architecture_imports \
  --request-validation-report-out-dir reports/circle_ai_request_validation \
  --certification-bundle-out-dir reports/circle_ai_certification_bundles \
  --certification-bundle-check-out-dir reports/circle_ai_certification_bundle_checks \
  --report-out reports/circle_ai_runner_check.json \
  --require-status proved \
  --require-decision passed \
  --require-passed
```

The checker also builds the compact receipt for every request, model-config, and
architecture-config example. It fails if selected compact evidence is empty, if
proof-layer labels do not cover exactly the selected evidence paths, or if any
selected path is still `unclassified`. Add `--compact-receipt-out-dir` to save
those compact handoff files for every checked item. Its JSON report records the
compact receipt path, selected-evidence count, unclassified count, and label set
for each example.

Run the same checker for only one contract family:

```bash
python scripts/check_circle_ai_contract_runner.py \
  --kind sparse-attention \
  --report-out reports/sparse_runner_check.json
```

`--kind` accepts the same aliases as the request schema, including `rope`,
`kv-cache`, `sparse-attention`, `recurrence`, `strided-fanout`,
`cyclic-memory`, `multicoil-phase`, `cyclic-mixer`, and `seed-rule`, and may be
passed more than once. The runner-check report records the canonical
`selected_kinds` list so a downstream CI log can show whether it checked the
whole example set or one contract lane.

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
Architecture-config summaries similarly inline
`architecture_config_parameter_sources`, and
`--architecture-config-import-report-out-dir` writes the schema-validated import
reports for the KV-cache, sparse-attention, and recurrence receipts emitted from
each architecture config. Optional architecture parameters that use receipt
defaults are materialized in the emitted request and labeled with source
`default`, so bundles can verify the import request against the receipt request.
The same summaries also inline `unsupported_architecture_config_fields`, so
batch reports expose target-section behavior that was present in the source
config but not certified by the emitted request.
When `--request-validation-report-out-dir` is set, every summary also points to
the schema-validated preflight report for the exact request that produced the
receipt.
When `--certification-bundle-out-dir` is set, every summary also points to a
schema-validated certification bundle containing the preflight report, receipt,
gate report, and any model-config or architecture-config import provenance.
When `--certification-bundle-check-out-dir` is also set, every summary points to
a schema-validated verification report for that bundle. This is useful when a
batch job should leave both portable artifacts and CI-readable pass/fail
evidence beside them.
By default it checks both `examples/circle_ai_requests/*.json` request files and
`examples/circle_ai_model_configs/*.json` standard RoPE model configs, currently
including 128k examples at RoPE bases `10000` and `500000`, plus
`examples/circle_ai_architecture_configs/*.json` architecture configs.
Model config and architecture config examples are first converted into versioned
Circle request JSON, then checked by the same receipt path. Each architecture
config emits RoPE, KV-cache, sparse-attention, and recurrence receipts by
default; pass `--architecture-config-kind` to restrict any architecture-derived
family.

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
optional model-config or architecture-config import provenance, and optional
status, decision, assurance, pass, theorem-id, evidence-field, recommendation-id,
validation-command, normalized-parameter, model-config fingerprint, or
architecture-config fingerprint gates. Add
`--require-kind KIND`, `--require-theorem-id THEOREM_ID`,
`--require-evidence-field FIELD`, `--require-recommendation-id ID`,
`--require-validation-command COMMAND`, or `--require-normalized-param
KEY=JSON_VALUE` when a downstream project depends on specific embedded receipt
content. Add `--require-model-config-fingerprint FINGERPRINT` with the
`model_config_fingerprint` from the embedded import report when the bundle came
from an imported RoPE `config.json`. Add
`--require-architecture-config-fingerprint FINGERPRINT` with the
`architecture_config_fingerprint` from the embedded import report when the
bundle came from an architecture config. It is the preferred CI-facing
command when a downstream project stores the full certification bundle rather
than just the receipt.
The bundle-check report records those requested dependencies in `pin_policy`.
Reuse the same bundle dependency contract later with `--pin-policy
reports/rope_certification_bundle_check.json`; the checker accepts either the
whole report or just the `pin_policy` object, and explicit `--require-*` flags
are merged with the loaded pins.

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
decision, assurance, pass, theorem-id, evidence-field, recommendation-id,
validation-command, or normalized-parameter gates. Add `--require-theorem-id
THEOREM_ID`, `--require-kind KIND`, `--require-evidence-field FIELD`,
`--require-recommendation-id ID`, `--require-validation-command COMMAND`, or
`--require-normalized-param KEY=JSON_VALUE` when a downstream project depends on
specific receipt content.
It validates its own report against
`site/data/generated/circle_ai_contract_receipt_file_check.schema.json` and can
write that report to disk for audit logs. It is the smallest CI-facing command
for downstream projects that want to reject stale or tampered Circle AI receipts
without running Lean. The report summary includes the loaded contract-pack
fingerprint, contract fingerprint, receipt fingerprint, request-content
fingerprint, normalized-request fingerprint, theorem ids, evidence fields,
recommendation ids, validation commands, and normalized request, so CI can
record what was certified without reopening every receipt file.
The receipt-check report also records requested dependency pins in `pin_policy`.
Reuse the same receipt dependency contract later with `--pin-policy
reports/rope_receipt_check.json`; the checker accepts either the whole report
or just the `pin_policy` object, and explicit `--require-*` flags are merged
with the loaded pins.

Replay a saved receipt when CI needs to prove it can still be regenerated from
its embedded request under the current runner code and contract pack:

```bash
python scripts/check_circle_ai_receipt_replay.py reports/rope_receipt.json \
  --report-out reports/rope_receipt_replay.json
```

The replay checker does not execute shell commands embedded in the receipt. It
rebuilds the receipt through the public Python request API, then compares the
original and regenerated status, decision, request fingerprint, normalized
request fingerprint, and receipt fingerprint. This catches stale-but-well-formed
receipt files whose JSON shape and pack fingerprints still validate but whose
computed evidence no longer matches the current runner.

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

For RoPE receipts, `real_phase_nearest_integer_bridge` is the theorem-backed
finite-certificate shape: a real turn-ratio margin can be checked by finite
floor/ceiling nearest-integer endpoint witnesses over the positive gaps below
the context. This is a bridge, not a proof that the requested margin holds.

`real_phase_dirichlet_guardrail` is a theorem-backed finite-context ceiling.
When `context > 1`, theorem ids `AIRA-T0239` through `AIRA-T0241` justify the
`1/context` guardrail: a requested real-phase margin strictly above `1/context`
is impossible. A margin at or below that ceiling is not automatically proved by
this field; it still needs a D19-style certificate or future sharper theorem.

## Python API

```python
from circle_math.applications import (
    build_architecture_config_certification_bundle,
    build_contract_artifact_manifest_file_check_report,
    build_contract_certification_bundle,
    build_contract_certification_bundle_file_check_report,
    build_contract_receipt_file_check_report,
    build_contract_receipt_gate_report,
    build_contract_receipt_replay_check_report,
    build_contract_request,
    build_contract_request_validation_report,
    build_rope_contract_request_from_model_config,
    build_rope_model_config_certification_bundle,
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
rope_bundle = build_rope_model_config_certification_bundle(
    model_config,
    requested_margin="1/328459",
    pack=pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("mixed_theorem_and_computation",),
    require_passed=True,
)
assert rope_bundle["model_config_import_report"]["request"] == request

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
assert receipt["validation_commands"][0].startswith(
    "python scripts/circle_ai_certify.py rope "
)
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
replay_report = build_contract_receipt_replay_check_report(
    receipt,
    pack,
    receipt_path="reports/rope_receipt.json",
)
assert replay_report["ok"] is True
assert replay_report["comparison"]["all_replay_fields_match"] is True
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

architecture_config = {
    "sparse_attention": {
        "context_length": 9,
        "sliding_window": 2,
        "strides": [3, 4, 7],
        "max_hops": 2,
    }
}
architecture_bundle = build_architecture_config_certification_bundle(
    "sparse-attention",
    architecture_config,
    pack=pack,
    required_statuses=("proved",),
    required_decision_verdicts=("passed",),
    required_assurance_levels=("theorem_backed",),
    require_passed=True,
)
assert architecture_bundle["architecture_config_import_report"]["ok"] is True
```

The bundle's top-level `request_content_fingerprint` is the fingerprint of the
submitted request object used for preflight. If the request came from
`--model-config` or from `build_rope_model_config_import_report`, the optional
`model_config_import_report` section carries the model-config fingerprint, the
config-to-request parameter sources, and the emitted request fingerprint. If it
came from `--architecture-config` or
`build_architecture_config_import_report`, the parallel
`architecture_config_import_report` section carries the source
architecture-config fingerprint, parameter sources, and emitted request
fingerprint. The
embedded receipt still carries its own `request_content_fingerprint` for the
canonical request that the certifier emitted after applying contract defaults.
Use `build_rope_model_config_certification_bundle` or
`build_architecture_config_certification_bundle` when a downstream Python
consumer wants receipt, gate report, and source-config provenance in one
schema-validated object.

For every parameterized receipt, the first `validation_commands` entry is the
request-specific replay command for those exact runner parameters. The remaining
commands come from the contract pack and recheck fixture readiness, theorem
coverage, and family-specific tests.

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
site/data/generated/circle_ai_contract_compact_receipt.schema.json
site/data/generated/circle_ai_contract_runner_check.schema.json
site/data/generated/circle_ai_contract_receipt_file_check.schema.json
site/data/generated/circle_ai_contract_receipt_replay_check.schema.json
site/data/generated/circle_ai_contract_certification_bundle.schema.json
site/data/generated/circle_ai_contract_certification_bundle_file_check.schema.json
site/data/generated/circle_ai_contract_artifact_manifest.schema.json
site/data/generated/circle_ai_contract_artifact_manifest_file_check.schema.json
```

The request schema has contract-specific parameter shapes. RoPE, recurrence,
and the five compact ready families may rely on defaults, while KV-cache and
sparse-attention requests must include their required fields. RoPE `head_dim`
values must be positive and even. Recurrence `max_loops` and
`selected_block_width` values must be positive. New compact families still reject
ill-formed parameters such as empty period lists, nonpositive bank sizes, or a
cyclic-mixer block size larger than the channel count.
Unknown top-level request keys and unknown parameter keys are rejected so typoed
configs fail before a receipt is issued.

`validate_contract_request(request)` applies the same contract-specific checks
inside Python, including required fields, unknown keys, numeric ranges, and
RoPE margin parsing.

## Non-Claims

The runner proves finite contract fields only. It does not prove model quality,
training improvement, deployment safety, implementation correctness, memory
savings, throughput, or useful context-length improvement.
