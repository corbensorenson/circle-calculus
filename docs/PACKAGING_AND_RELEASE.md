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

The package exposes these console scripts:

```bash
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
