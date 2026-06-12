# Repository Structure

Recommended repository tree:

```text
circle-calculus/
  README.md
  LICENSE
  Makefile
  lean-toolchain
  lakefile.lean
  pyproject.toml
  .github/workflows/ci.yml

  Circle/
    Basic.lean
    Core/
      Finite.lean
      Rotation.lean
      Coil.lean
      Period.lean
      Prime.lean
      Scaling.lean
      Winding.lean
    Proof/
      NormalForm.lean
      ManifestBindings.lean
    Meta/
      SafeAxioms.lean

  circle_math/
    __init__.py
    finite.py
    orbit.py
    scaling.py
    winding.py
    glyph.py

  tests/
    test_rotation.py
    test_orbit_period.py
    test_prime_coils.py
    test_scaling.py
    test_winding.py

  scripts/
    check_manifest.py
    check_dictionary.py
    check_no_fake_proofs.py
    check_paper_theorem_links.py
    render_examples.py

  dictionary/
    circle_dictionary.schema.json
    circle_dictionary.yaml

  manifests/
    theorem_manifest.schema.json
    theorem_manifest.yaml
    paper_manifest.yaml

  papers/
    PAPER_01_FINITE_CIRCLES.md
    PAPER_02_WINDING_NATURALS.md
    PAPER_03_INTEGERS_ORIENTATION.md
    ROADMAP.md
    template.md

  docs/
    FORMAL_CORE_V0.md
    GODEL_AND_LIMITATIONS.md
    PROOF_POLICY.md
    GLOSSARY.md
    speculative/
      infinity_as_horizon.md
      future_geometry.md
      future_analysis.md
```

## Make targets

```makefile
.PHONY: check lean test manifest dictionary paperlinks nofake

check: lean test manifest dictionary paperlinks nofake

lean:
	lake build

test:
	python -m pytest

manifest:
	python scripts/check_manifest.py

dictionary:
	python scripts/check_dictionary.py

paperlinks:
	python scripts/check_paper_theorem_links.py

nofake:
	python scripts/check_no_fake_proofs.py
```

## Proof policy

`Circle/Core` must be axiom-free and sorry-free.

Allowed future/speculative files may contain placeholders only when:
- they live outside the proved core,
- they are marked `planned`, `blocked`, or `deferred` in the manifest,
- CI excludes them from “proved theorem” checks,
- papers do not cite them as completed results.
