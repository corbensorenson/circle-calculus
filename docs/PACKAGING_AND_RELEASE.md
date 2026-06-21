# Packaging And Release Checklist

This project has four public release surfaces:

- Lean/Lake package metadata for Reservoir-style discovery;
- Python package metadata and console scripts;
- Rust `circle-prime` crate metadata and docs;
- GitHub release artifacts and Living Book publication.

Do not publish external releases from an automated local pass unless the user
explicitly asks for that publication step.

## Pre-Release Checks

```bash
lake build Circle
python scripts/check_manifest.py
python scripts/check_manifest_lean_names.py
python scripts/check_no_fake_proofs.py
python scripts/check_paper_theorem_links.py
python -m pytest tests/test_public_api.py -q
cargo check -p circle-prime
cargo test -p circle-prime
cargo doc -p circle-prime --no-deps
```

Use `make check` before a release-grade commit when time allows.

## Current v0.1 RC Dry-Run Evidence

Recorded locally on 2026-06-21:

- `python scripts/export_circle_ai_contracts.py` regenerated the public
  contract pack, JSON Schemas, and packaged theorem-status index.
- `make public-api-docs` regenerated `docs/generated/PUBLIC_API_REFERENCE.md`.
- `python -m pytest tests/test_public_api.py -q` passed:
  `27 passed in 151.21s`.
- Clean Python artifact check passed with `build 1.2.1`, `twine 6.2.0`,
  `pkginfo 1.12.1.2`, and `packaging 26.2`: `python -m build` followed by
  `python -m twine check dist/*`.
- Clean wheel smoke passed in `/tmp/circle-calculus-wheel-smoke-3`: importing
  `circle_math.core`, building the contract pack, checking sparse-attention
  readiness, building a RoPE receipt, and running installed
  `circle-ai-certify sparse-attention --context 9 --strides 3,4,7
  --path-length 2 --local-window 2 --format compact-json`.
- `cargo doc -p circle-prime --no-deps` passed and generated
  `target/doc/circle_prime/index.html`.
- `COPYFILE_DISABLE=1 cargo package -p circle-prime --allow-dirty` passed
  after clearing generated macOS `.DS_Store` metadata under `target/package`.
- `cargo test -p circle-prime` passed: `116 passed; 1 ignored` library tests,
  `14` `circle-prime` binary tests, and `3` benchmark-filter tests.

## Lean / Reservoir Readiness

The Lake package metadata should include:

- `description`
- `keywords`
- `homepage`
- `license`
- `licenseFiles`
- `readmeFile`
- `reservoir := true`

Dry run:

```bash
lake build Circle.Core Circle.Contracts
```

Reservoir publication is index-driven; this repository should be tagged and
publicly reachable before expecting external discovery to work.

## Python Package Dry Run

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
python -m pytest tests/test_public_api.py -q
python -m build
python -m twine check dist/*
```

The Python metadata uses an SPDX license expression and therefore emits
`Metadata-Version: 2.4`; use `twine>=6.2` or another verifier with
Metadata 2.4 support.
The wheel also includes `circle_math/data/generated/theorem_status_index.json`
as package data so contract-pack readiness can resolve theorem ids outside a
repo checkout. Regenerate it with `python scripts/export_circle_ai_contracts.py`
before building a release artifact.

The package exposes these console scripts:

```bash
circle-ai-certify rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --format json
circle-ai-certify rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --artifact-dir /tmp/circle_rope_contract --format json
circle-ai-certify rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --request-out /tmp/circle_rope_request.json --request-validation-report-out /tmp/circle_rope_request_validation.json --model-config-import-report-out /tmp/circle_rope_import_report.json --certification-bundle-out /tmp/circle_rope_bundle.json --certification-bundle-check-out /tmp/circle_rope_bundle_check.json --artifact-manifest-out /tmp/circle_rope_manifest.json --artifact-manifest-check-out /tmp/circle_rope_manifest_check.json --format json
circle-ai-certify sparse-attention --context 9 --strides 3,4,7 --path-length 2 --local-window 2 --format compact-json --compact-json-out /tmp/circle_sparse_compact_receipt.json
circle-ai-certify kv-cache --cache-size 16 --current 31 --token 20 --batch-tokens 20,24,29,31 --sink-size 4 --require-passed
circle-ai-certify sparse-attention --context 9 --strides 3,4,7 --path-length 2 --local-window 2
circle-ai-certify recurrence --format json
circle-ai-contract-ready --kind sparse_attention_coverage
circle-ai-contract-receipt --kind rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json
circle-ai-contract-receipt --kind sparse-attention --parameters '{"context": 9, "strides": [3, 4, 7], "path_length": 2, "local_window": 2}'
circle-ai-contract-receipt --request-file examples/circle_ai_requests/kv_cache_request.json --require-passed --require-status proved --require-decision passed
circle-rope-certify --preset llama_style_10000_4k
circle-sparse-attention-certify --context 9 --strides 3,4,7 --path-length 2 --local-window 2
```

Only upload to PyPI after checking metadata, generated artifacts, and the
release tag.

## Rust Crate Dry Run

```bash
cargo check -p circle-prime
cargo test -p circle-prime
cargo doc -p circle-prime --no-deps
cargo package -p circle-prime --allow-dirty
```

Use `--allow-dirty` only for local dry-runs in an active worktree. Do not use it
for publication.

## GitHub Release

Before drafting a GitHub release:

1. Update `README.md`, `docs/PUBLIC_API.md`, and this file if the public API
   changed.
2. Regenerate API docs and theorem graph artifacts.
3. Run the release checks above.
4. Create a tag such as `v0.1.0`.
5. Attach generated contract schemas and any release notes if needed.

GitHub release publication should happen after the repository state is committed
and pushed.
