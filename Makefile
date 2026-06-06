LAKE := $(shell command -v lake 2>/dev/null || printf "%s/.elan/bin/lake" "$$HOME")
QUARTO := $(shell if command -v quarto >/dev/null 2>&1; then command -v quarto; elif [ -x ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto" ]; then printf ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto"; else printf "quarto"; fi)
QUARTO_HOME ?= $(CURDIR)/.tools/quarto-home
QUARTO_DENO_DIR ?= $(CURDIR)/.tools/quarto-deno
QUARTO_ENV := HOME="$(QUARTO_HOME)" DENO_DIR="$(QUARTO_DENO_DIR)"

.PHONY: check lean sidecarlean test manifest dictionary papermanifest paperlinks papersources claimlanguage phase4targets phase5targets phase6targets glyphfixtures dimensioncheck dimensionindex dimensionimports dimensionmanifests dimensionpaperlinks nofake examples site-data sitecheck site-render site-preview living-book-check

check: lean sidecarlean test manifest dictionary papermanifest paperlinks papersources claimlanguage phase4targets phase5targets phase6targets glyphfixtures dimensioncheck nofake sitecheck

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

papersources:
	python scripts/check_paper_source_trails.py

claimlanguage:
	python scripts/check_claim_language.py

phase4targets:
	python scripts/check_phase4_targets.py

phase5targets:
	python scripts/check_phase5_targets.py

phase6targets:
	python scripts/check_phase6_sweep_targets.py

glyphfixtures:
	python scripts/check_glyph_fixtures.py

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

site-data:
	python scripts/site/export_site_data.py

sitecheck: site-data
	python scripts/site/check_quarto_structure.py
	python scripts/site/check_site_manifest_links.py
	python scripts/site/check_site_dictionary_links.py
	python scripts/site/check_site_theorem_status.py
	python scripts/site/check_site_paper_links.py
	python scripts/site/check_widget_python_parity.py

site-render: site-data
	$(QUARTO_ENV) $(QUARTO) render site

site-preview: site-data
	$(QUARTO_ENV) $(QUARTO) preview site

living-book-check: lean sidecarlean test manifest dictionary papermanifest paperlinks papersources dimensioncheck nofake sitecheck site-render
