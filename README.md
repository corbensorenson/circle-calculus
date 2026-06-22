# Circle Calculus

[![CI](https://github.com/corbensorenson/circle-calculus/actions/workflows/ci.yml/badge.svg)](https://github.com/corbensorenson/circle-calculus/actions/workflows/ci.yml)
[![Deploy Living Book](https://github.com/corbensorenson/circle-calculus/actions/workflows/pages.yml/badge.svg)](https://github.com/corbensorenson/circle-calculus/actions/workflows/pages.yml)

Circle Calculus is a proof-carrying finite cyclic mathematics project: Lean
proofs, Python reference models, Rust prime/horizon utilities, theorem
manifests, papers, and a Quarto Living Book all tied together by explicit proof
status.

Start with the public site: <https://corbensorenson.github.io/circle-calculus/>.

## Use It

- Learn the project: [Living Book](https://corbensorenson.github.io/circle-calculus/)
- Use it as code: [docs/USE_AS_LIBRARY.md](docs/USE_AS_LIBRARY.md)
- Inspect stable APIs: [docs/PUBLIC_API.md](docs/PUBLIC_API.md)
- Use finite Fourier/circulant algebra: [docs/FINITE_FOURIER_CIRCULANT.md](docs/FINITE_FOURIER_CIRCULANT.md)
- Use positional phase-bank contracts: [docs/POSITION_PHASE_BANKS.md](docs/POSITION_PHASE_BANKS.md)
- Use circle graph coverage contracts: [docs/CIRCLE_GRAPH_COVERAGE.md](docs/CIRCLE_GRAPH_COVERAGE.md)
- Use finite circular statistics contracts: [docs/CIRCULAR_STATISTICS_CONTRACTS.md](docs/CIRCULAR_STATISTICS_CONTRACTS.md)
- Use finite cyclic equivariance contracts: [docs/CYCLIC_EQUIVARIANCE.md](docs/CYCLIC_EQUIVARIANCE.md)
- Use phase loop/winding/locking contracts: [docs/PHASE_LOOP_CONTRACTS.md](docs/PHASE_LOOP_CONTRACTS.md)
- Consume AI/system contracts: [docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md](docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md)
- Check contract schema/version policy: [docs/CONTRACT_SCHEMA_VERSIONING.md](docs/CONTRACT_SCHEMA_VERSIONING.md)
- Browse circle research expansion ideas: [docs/CIRCLE_RESEARCH_EXPANSION_BACKLOG.md](docs/CIRCLE_RESEARCH_EXPANSION_BACKLOG.md)
- Verify claims: [site/verify_claim.qmd](site/verify_claim.qmd)
- Understand "proved": [docs/PROOF_POLICY.md](docs/PROOF_POLICY.md)

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For Lean, install `elan`; Lake reads the pinned toolchain from
`lean-toolchain`.

## Stable Entry Points

Python:

```python
from circle_math.core import finite_orbit, finite_period
from circle_math.ai_contracts import (
    build_contract_pack,
    build_contract_runner_check_report,
    build_rope_receipt,
)
```

CLI receipt path:

```bash
circle-ai-certify rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json --format json
circle-ai-contract-receipt --kind rope --model-config-file examples/circle_ai_model_configs/standard_rope_config.json
circle-ai-certify batch \
  --request-file examples/circle_ai_requests/kv_cache_request.json \
  --request-file examples/circle_ai_requests/sparse_attention_request.json \
  --model-config-file examples/circle_ai_model_configs/standard_rope_config.json \
  --architecture-config-file examples/circle_ai_architecture_configs/basic_transformer_contract_config.json \
  --artifact-dir reports/circle_ai_contract_batch \
  --artifact-prefix architecture-suite \
  --require-passed \
  --require-status proved \
  --require-decision passed \
  --format json
```

Lean:

```lean
import Circle.Core
import Circle.Contracts
```

Rust:

```bash
cargo run -p circle-prime -- --help
cargo doc -p circle-prime --no-deps
```

## Verify

```bash
make targeted-check
make check
```

Core focused checks:

```bash
lake build Circle
python scripts/check_manifest.py
python scripts/check_manifest_lean_names.py
python scripts/check_no_fake_proofs.py
python scripts/check_paper_theorem_links.py
```

## Proof Boundary

A claim is treated as proved only when it has a theorem id, a compiled Lean
declaration, manifest status `proved` or `lean_proved`, a passing Lean build,
and no forbidden proof placeholders. Python tests, diagrams, widgets, benchmark
fixtures, and generated JSON are useful evidence layers, not proofs.

The AI and systems contracts prove finite structural facts such as cyclic
indexing, RoPE phase-bank conditions, sparse-attention coverage fields,
ring-buffer freshness, recurrence schedules, and circulant/block-cyclic mixer
laws. They do not claim model-quality, speed, memory, context-length,
deployment-safety, physics, or universal-compression improvements.

The current contract surface distinguishes 9 public contract families from
6 compatibility downstream-transfer contract families. The public package CLI can
issue single-config receipts or batch request/model-config handoff reports
without importing repository-only scripts.

## Repository Layout

```text
Circle/        Lean 4 / mathlib formalization
circle_math/   Python public APIs and reference models
rust/          Rust prime/horizon engine
dictionary/    Shared vocabulary
docs/          Policy, guides, quickstarts, and release notes
manifests/     Theorem, paper, target, and capability metadata
papers/        Human-readable papers
sidecars/      Per-paper Lean, Python, diagram, and result artifacts
site/          Quarto Living Book
scripts/       Validation, export, and repository maintenance tools
tests/         Python regression and contract tests
```

## Contribute

Use [CONTRIBUTING.md](CONTRIBUTING.md) for the four common workflows:

- adding a theorem,
- adding a Python model,
- adding a contract,
- adding a paper.

## Release Readiness

Release and package preparation lives in
[docs/PACKAGING_AND_RELEASE.md](docs/PACKAGING_AND_RELEASE.md). The project is
MIT licensed; citation metadata is in [CITATION.cff](CITATION.cff).
