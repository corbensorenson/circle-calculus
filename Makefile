LAKE := $(shell command -v lake 2>/dev/null || printf "%s/.elan/bin/lake" "$$HOME")

.PHONY: check lean sidecarlean test manifest dictionary papermanifest paperlinks dimensioncheck dimensionindex dimensionimports dimensionmanifests dimensionpaperlinks nofake examples

check: lean sidecarlean test manifest dictionary papermanifest paperlinks dimensioncheck nofake

lean:
	$(LAKE) build

sidecarlean:
	python scripts/check_lean_sidecars.py

test:
	python -m pytest

manifest:
	python scripts/check_manifest.py

dictionary:
	python scripts/check_dictionary.py

papermanifest:
	python scripts/check_paper_manifest.py

paperlinks:
	python scripts/check_paper_theorem_links.py

dimensioncheck: dimensionindex dimensionimports dimensionmanifests dimensionpaperlinks

dimensionindex:
	python scripts/check_dimension_index.py

dimensionimports:
	python scripts/check_dimension_imports.py

dimensionmanifests:
	python scripts/check_dimension_manifests.py

dimensionpaperlinks:
	python scripts/check_dimension_paper_links.py

nofake:
	python scripts/check_no_fake_proofs.py

examples:
	python scripts/render_examples.py
