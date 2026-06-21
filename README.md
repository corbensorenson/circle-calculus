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
- Consume AI/system contracts: [docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md](docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md)
- Check contract schema/version policy: [docs/CONTRACT_SCHEMA_VERSIONING.md](docs/CONTRACT_SCHEMA_VERSIONING.md)
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
from circle_math.ai_contracts import build_contract_pack, build_rope_receipt
```

CLI receipt path:

```bash
circle-ai-contract-receipt --kind sparse-attention --parameters '{"context": 9, "strides": [3, 4, 7], "path_length": 2, "local_window": 2}'
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

The current contract surface distinguishes 8 public contract families from 6 compatibility
downstream-transfer contract families.

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
