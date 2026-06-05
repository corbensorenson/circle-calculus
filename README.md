# Circle Calculus

Circle Calculus is a staged paper-and-proof corpus for rebuilding familiar mathematical structures from finite circular address spaces, rotations, coils, winding, lifted arithmetic, and eventually a dimension-indexed sphere ladder.

The long-term aim is not just to write essays. The aim is to keep every serious concept tied to:

- a human-readable paper in `papers/`,
- Lean 4/mathlib declarations in `Circle/` and paper-specific Lean sidecars in `sidecars/`,
- executable Python reference models in `circle_math/`,
- a shared dictionary in `dictionary/circle_dictionary.yaml`, and
- theorem metadata in `manifests/theorem_manifest.yaml`.

The rule is simple: papers are allowed to be ambitious, but claimed theorems must be traceable.

## What This Project Aims To Prove

The project starts from the finite cyclic address space `C_n`, modeled in Lean as `ZMod n`, and builds upward in stages.

Current focus:

- finite marked circles and nodes,
- rotations as addition in `C_n`,
- coils as repeated rotations,
- closure and period,
- orbit decomposition,
- prime full-coil behavior,
- lifted winding/residue coordinates, and
- natural-number addition and successor as lifted circular motion with carry.

Planned later stages include oriented winding for integers, multiplication and scaling, factor structure, geometry, analysis-flavored limits, higher spheres, and a careful foundations layer. Those later stages are not claimed as proved until their theorem manifest entries, Lean declarations, and checks exist.

## Dimensional Roadmap

The expanded long-horizon plan is dimension-organized:

```text
S^0 -> S^1 -> S^2 -> S^3 -> S^4/S^5/S^6 -> S^7 -> Future/S^15
```

The current proved layer is `S^1`: finite circles, rotations, coils, period, orbit decomposition, prime full coils, winding, and lifted natural-number arithmetic.

Future dimensional work is split into two related ladders:

- Geometric ladder: `S^0`, `S^1`, `S^2`, `S^3`, `S^4`, `S^5`, `S^6`, `S^7`.
- Algebraic ladder: `S^0` signs, `S^1` unit complex phase, `S^3` unit quaternions, `S^7` unit octonions.

The repository rule for that expansion is strict: higher dimensions may depend on lower dimensions, but lower dimensions must not import or rely on higher dimensions. The first dimensional implementation stage should be scaffolding only: dimension manifests, dictionary files, paper folders, Lean/Python roots, and import-check scripts, with all future theorem statuses kept planned, deferred, or exploratory until proofs exist.

See `docs/COMPLETION_ROADMAP.md`, `docs/DIMENSIONAL_LADDER.md`, `docs/PHASE2_AND_APPLICATIONS.md`, and `circle_calculus_dimensional_handoff/` for the detailed roadmap and guardrails.

## Current Status

This is an early public research scaffold with two promoted papers and a working verification pipeline.

| Paper | Status | Formal spine |
| --- | --- | --- |
| `papers/PAPER_01_FINITE_CIRCLES.md` | outline/draft | `CC-T0001` through `CC-T0007` proved |
| `papers/PAPER_02_WINDING_NATURALS.md` | draft | `CC-T0009` through `CC-T0016` proved |

The theorem manifest also includes `CC-T0008`, proving that scaling by `k` is invertible on `C_n` exactly when `n` and `k` are coprime.

The D0 dimensional scaffold is also in place: dimension manifests, dimension dictionaries, planned paper stubs, Lean/Python scaffolds, and dimension validation scripts. Future-dimension theorems remain planned, deferred, exploratory, or stated until actual Lean proofs exist.

## Proof Standard

A theorem is treated as proved only when all of the following are true:

1. It has a theorem id in `manifests/theorem_manifest.yaml`.
2. It has an exact Lean declaration name.
3. Its manifest status is `proved`.
4. `lake build` succeeds.
5. `scripts/check_no_fake_proofs.py` finds no forbidden proof placeholders.

Python tests and generated diagrams are executable support. They help keep the papers honest, but they are not formal proofs.

For the fuller policy, see `docs/PROOF_POLICY.md`.

## Repository Layout

```text
Circle/                         Lean 4/mathlib formalization
Circle.lean                     Root Lean import file
circle_math/                    Python reference models
dictionary/                     Shared Circle Calculus vocabulary
docs/                           Proof policy and foundational notes
manifests/                      Paper and theorem metadata
papers/                         Human-readable papers
scripts/                        Repository validation scripts
sidecars/                       Per-paper Lean, Python, and diagram artifacts
tests/                          Python regression/property tests
circle_calculus_codex_handoff/  Original planning pack and source logs
circle_calculus_dimensional_handoff/  Dimensional-ladder planning pack
```

## Getting Started

Install Lean through `elan` if it is not already installed:

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y --default-toolchain none
```

Set up Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Run the full verification suite:

```bash
make check
```

The first Lean build may take time because Lake has to fetch and build mathlib dependencies pinned by `lean-toolchain` and `lake-manifest.json`.

## Useful Commands

```bash
make lean        # build the root Lean library
make sidecarlean # check all per-paper Lean sidecars
make test        # run Python tests
make manifest    # validate theorem metadata
make dictionary  # validate dictionary metadata
make paperlinks  # verify papers cite known theorem ids
make dimensioncheck # validate dimension manifests, imports, and paper links
make nofake      # reject forbidden proof placeholders
make examples    # regenerate current example diagrams
make check       # run the full suite
```

## How To Read The Project

Start with:

1. `papers/PAPER_01_FINITE_CIRCLES.md`
2. `sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean`
3. `papers/PAPER_02_WINDING_NATURALS.md`
4. `sidecars/PAPER_02_WINDING_NATURALS/lean/Paper02.lean`
5. `dictionary/circle_dictionary.yaml`
6. `manifests/theorem_manifest.yaml`
7. `docs/COMPLETION_ROADMAP.md`
8. `docs/DIMENSIONAL_LADDER.md`

The papers give the conceptual path. The sidecars show the proof links. The dictionary fixes vocabulary so later papers reuse the same meanings instead of drifting.

## How To Add A Paper

Use `papers/template.md` and keep the paper connected from the beginning.

1. Add or reuse dictionary entries in `dictionary/circle_dictionary.yaml`.
2. Add theorem ids to `manifests/theorem_manifest.yaml`.
3. Add the paper entry to `manifests/paper_manifest.yaml`.
4. Put Lean sidecars under `sidecars/<PAPER_ID>/lean/`.
5. Put executable examples or tests under `sidecars/<PAPER_ID>/python/`.
6. Add diagrams under `sidecars/<PAPER_ID>/diagrams/` when they clarify the argument.
7. Run `make check`.

If a statement is important but not proved yet, mark it as planned or blocked in the manifest instead of presenting it as proved.

## Current Theorem Spine

Proved finite-circle core:

- `CC-T0001`: rotation by zero
- `CC-T0002`: rotation composition
- `CC-T0003`: rotation inverse
- `CC-T0004`: closure condition
- `CC-T0005`: period equals `n / gcd(n,k)`
- `CC-T0006`: orbit decomposition count
- `CC-T0007`: prime full coil
- `CC-T0008`: scaling invertible iff coprime

Proved winding/natural-number core:

- `CC-T0009`: unique winding/residue lift
- `CC-T0010`: lifted addition decomposition
- `CC-T0011`: lifted existence
- `CC-T0012`: successor with carry
- `CC-T0013`: lifted addition right zero identity
- `CC-T0014`: lifted addition associativity at reconstructed-value level
- `CC-T0015`: lifted addition left zero identity
- `CC-T0016`: iterated lifted successor

## What This Does Not Claim Yet

This repository does not currently claim to have rebuilt all of mathematics from circles. It contains a verified starting spine and an explicit roadmap for growing it.

It also does not claim that Python tests are proofs, that diagrams are proofs, that `S^2` has a natural group structure, that `S^3` is globally `S^2 x S^1`, that unit octonions form a group, or that formalization bypasses foundational limitations. See `docs/GODEL_AND_LIMITATIONS.md` for the current limitations note.

For the deferred application and compute tracks, see `docs/PHASE2_AND_APPLICATIONS.md`. Local compute experiments should be MLX/Mac-first; CUDA-specific references are future portability notes or external benchmark baselines.
