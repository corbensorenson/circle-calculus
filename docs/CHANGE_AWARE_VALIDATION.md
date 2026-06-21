# Change-Aware Validation

Circle Calculus has two validation modes:

1. **Targeted edit-loop validation** runs only the checks that are likely to be affected by changed files.
2. **Full release validation** runs the complete Lean, Python, manifest, paper, dictionary, and Living Book gates.

Targeted validation is for speed while writing papers, proofs, certifiers, widgets, and dictionary entries. It is not a weaker proof standard and does not replace the full gate before release.

## Commands

Preview the inferred check plan:

```bash
make targeted-check-list
```

Preview the inferred check plan as machine-readable JSON for Codex or other
automation:

```bash
make targeted-check-json
```

Run the inferred check plan:

```bash
make targeted-check
```

Run the inferred plan for explicit files:

```bash
make targeted-check TARGETED_FILES="Circle/Applications/RoPECertifier.lean scripts/rope_certify.py"
```

Preview explicit-file or explicit-base plans:

```bash
make targeted-check-list TARGETED_FILES="site/chapters/applications/rope_certifier.qmd"
make targeted-check-list TARGETED_BASE=origin/main
make targeted-check-json TARGETED_FILES="scripts/targeted_check.py"
```

Run the full gate through the same runner:

```bash
make targeted-check-full
```

The authoritative full gates remain:

```bash
make check
make living-book-check
```

## How The Runner Chooses Checks

`scripts/targeted_check.py` reads changed files from git:

- committed changes since the upstream merge base when an upstream exists,
- otherwise committed changes since `HEAD~1`,
- unstaged changes,
- staged changes,
- and untracked files.

You can bypass git detection with explicit files:

```bash
python scripts/targeted_check.py --files Circle/Applications/RoPECertifier.lean scripts/rope_certify.py
```

The Makefile exposes the same bypass through `TARGETED_FILES`; use that form for normal local work so shell history keeps one consistent entry point.
Use `make targeted-check-json` when another script or agent needs the planned
commands without scraping text output.
The JSON payload includes `validation_scope`, `release_gate_required`,
`release_gate_commands`, `changed_file_count`, `check_count`,
`ai_contract_validation_scope`, `impacted_ai_contract_kinds`, and
`strict_receipt_kinds` so automation can distinguish a fast edit-loop pass from
a release-quality gate and can route AI-contract edits without scraping command
text.

The AI contract scope is one of:

- `none`: the changed files do not map to the public AI contract suite.
- `kind_specific`: the changed files map to one or more named contract kinds.
- `all_contracts`: shared contract-pack, integration, generated-pack, or
  validation-router surfaces changed.
- `full_release`: `--full` was requested, so every public contract kind is in
  scope.

The mapping is conservative:

- `Circle/**/*.lean` builds the corresponding Lean module to refresh declaration artifacts, then rebuilds the aggregate `Circle` module before fake-proof checks and manifest Lean-name checks. The aggregate build is intentional: `scripts/check_manifest_lean_names.py` imports `Circle`, so a newly added declaration can otherwise typecheck in its local module while the manifest check sees a stale aggregate import. The runner does not also run a separate file-level Lean elaboration when the module name is known, because the module build is the useful local proof artifact and duplicate elaboration is too expensive for large application files.
- application Lean files also run application guardrails and proof-depth audit.
  Contract-backed application Lean files such as `RoPECertifier.lean`,
  `RoPEFrontier.lean`, `RoPEGeneratedCertificates.lean`, and
  `CircleTransformer.lean` also run the matching public contract export,
  pack/docs checks, and kind-specific readiness/digest path. This catches the
  case where a theorem compiles but the downstream contract pack or Living Book
  evidence surface has not been refreshed. The focused digests include the
  current flagship evidence fields: RoPE D19 request-classifier and
  first-channel bank-transfer fields, KV-cache stale/sink-window policy fields,
  and sparse-attention first-gap plus complete-fallback fields.
- RoPE-backed application Lean files also run `tests/test_rope_certifier.py`,
  because that file compares the committed RoPE preset result sidecars against
  their generator and catches stale theorem-id trails after proof-surface edits.
- RoPE Python or CLI changes run the RoPE certifier tests.
- KV-cache Python or CLI changes run the KV-cache certifier tests.
- sparse-attention / Circle AI changes run the sparse and Circle transformer tests.
- Shared Circle AI contract-surface changes run `make circle-ai-contracts-ready`, the contract-pack tests, the importable consumer-adapter tests, the pinned acceptance-policy tests, the copyable example-consumer CLI tests, and the standalone downstream-CI tests. This broad path is reserved for schema/exporter/consumer changes that can affect every public contract family or the downstream artifact-pinning path. The regular readiness target also smokes the schema-sidecar validator, the first-party strict receipt path, the pinned flagship acceptance policy, its recommendation evidence-field pins, plus the example consumer's all-readiness, fingerprint, planner, single-readiness, digest, strict receipt paths, and the standard-library-only downstream CI acceptance example.
- The JSON plan mirrors that decision with `ai_contract_validation_scope` and
  `impacted_ai_contract_kinds`, which downstream automation can use before
  deciding whether to run kind-specific checks or a full public pack gate.
- Single-contract certifier, quickstart, results note, review packet, and guided Living Book lesson changes run the matching certifier tests plus `scripts/export_circle_ai_contracts.py`, `scripts/check_circle_ai_contract_pack.py`, `scripts/check_circle_ai_contract_docs.py`, and `scripts/circle_ai_contract_ready.py --kind ...` with a kind-specific digest. This keeps RoPE, KV-cache, sparse-attention, recurrence, fanout, cyclic-memory, phase-feature, mixer, and seed-rule edits from running unrelated contract lanes during the edit loop.
- For the four flagship contracts, the same kind-specific path also runs the strict receipt command that a downstream consumer would pin: RoPE D19 position distinguishability, KV stale/sink-window freshness, sparse coverage/gap repair, and recurrence schedule/work-saving. Those receipt commands require named evidence fields, theorem ids, planner recommendations, recommendation evidence fields, recommendation theorem ids, and action-parameter paths. Secondary contracts still use readiness and digest checks only, unless they later gain a strict receipt policy.
- Circle AI contract documentation changes under `docs/AI_CONTRACT_SUITE.md`, `docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md`, and `site/chapters/applications/ai_contract_pack_audit.qmd` still use the broad pack path because those files document the whole generated minimum-field schema.
- The AI Contract Ladder lesson and audit page also use the broad pack path because they teach the whole public sequence across RoPE, KV cache, sparse attention, recurrence, and mixer contracts.
- generative seed-rule source changes run the generative sidecar tests and the seed-rule contract readiness/digest path because seed-rule provenance is exported as a downstream-consumable AI contract.
- generated sidecar result artifacts under `sidecars/*/results/*.json` or `*.md` run that paper sidecar's local Python tests; AI and generative sidecar result artifacts also run the public Circle AI contract readiness and consumer checks because those files feed reusable contract fixtures.
- prime-engine calibration/report scripts and generated artifacts under `sidecars/PRIME_ENGINE/results/` run the matching local prime-engine regression tests, such as default calibration and report rendering, instead of falling back to generic manifest or source checks.
- Rust prime-engine changes under `rust/circle-prime/` run `cargo test -p circle-prime` plus the Python CLI regression tests, because those edits affect executable counting behavior and cannot be validated by manifest or documentation checks.
- generated contract JSON changes under `site/data/generated/circle_ai_contract_pack.json`, `site/data/generated/circle_ai_contract_pack.schema.json`, `site/data/generated/circle_ai_contract_acceptance_policy.schema.json`, `site/data/generated/circle_ai_contract_acceptance_policy_report.schema.json`, `site/data/generated/circle_ai_contract_acceptance_receipt.schema.json`, `site/data/generated/circle_ai_downstream_rejection_report.schema.json`, `site/data/generated/circle_ai_contract_request.schema.json`, `site/data/generated/circle_ai_contract_request_validation.schema.json`, `site/data/generated/circle_ai_contract_receipt.schema.json`, `site/data/generated/circle_ai_contract_runner_check.schema.json`, `site/data/generated/circle_ai_contract_receipt_file_check.schema.json`, `site/data/generated/circle_ai_contract_certification_bundle.schema.json`, and `site/data/generated/theseus_hive_ai_contracts.json` run their pack validators and compatibility tests instead of relying on generic site checks.
- dictionary changes run dictionary, paper-link, and Living Book source checks.
- manifest changes run manifest, paper, research, capability, phase, and Living Book source checks.
- paper changes run paper manifest/link/source checks and claim-language checks.
- Living Book source changes run generated-data, source-link, theorem-status, dictionary-link, backlink, and widget checks as appropriate. The showcase page also runs the capability-showcase validator because it mirrors manifest evidence text and theorem ids.
- generated Living Book JSON changes under `site/data/generated/` run the same source-of-truth site checks, because those files feed public theorem, dictionary, paper, widget, and target indexes.
- `Makefile` changes always run a targeted-check smoke. The runner then
  inspects the changed Makefile lines when git diff context is available:
  prime-engine target/default edits run the matching prime-engine regression
  tests, Living Book target edits run site checks, targeted-check wrapper edits
  run the planner tests, and AI-contract or unclassified Makefile edits still
  run `make circle-ai-contracts-ready`. This keeps known local target edits
  focused while preserving the conservative path for ambiguous build changes.
- build or CI plumbing changes such as `pyproject.toml` or GitHub workflow files still escalate to `make sourcecheck`.

If no changed files are detected, the runner performs a small baseline manifest and dictionary check.

## Boundary

Targeted validation answers:

> Did the files I just changed pass the checks most likely to catch local regressions?

It does not answer:

> Does every Lean theorem, Python test, paper link, dictionary entry, widget, and rendered Living Book page still pass?

Use `make check` before commits that change proof status, public claims, major generated data, or cross-cutting infrastructure. Use `make living-book-check` before treating the public Living Book as release-ready.

Use targeted validation for the send-and-forget edit cycle: run the focused plan before a commit or handoff, then move on to the next artifact. Check remote CI status before the next send/push, not as a blocking wait after every local change.

Automation should treat `release_gate_required: true` in the JSON plan as an
explicit reminder that the focused checks were local evidence only. A completed
targeted run is enough to continue iteration, but it is not enough to publish a
release checkpoint or upgrade proof/status claims.

## Why This Exists

The project now contains Lean proofs, theorem manifests, dictionary entries, papers, Python certifiers, generated site data, widgets, and Quarto pages. Running the entire suite after every small edit wastes time when the dependency surface is local. Change-aware validation keeps the work moving while preserving the full suite as the final arbiter.
