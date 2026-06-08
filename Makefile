LAKE := $(shell command -v lake 2>/dev/null || printf "%s/.elan/bin/lake" "$$HOME")
QUARTO := $(shell if command -v quarto >/dev/null 2>&1; then command -v quarto; elif [ -x ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto" ]; then printf ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto"; else printf "quarto"; fi)
QUARTO_HOME ?= $(CURDIR)/.tools/quarto-home
QUARTO_DENO_DIR ?= $(CURDIR)/.tools/quarto-deno
QUARTO_ENV := HOME="$(QUARTO_HOME)" DENO_DIR="$(QUARTO_DENO_DIR)"

.PHONY: check sourcecheck lean sidecarlean test manifest dictionary papermanifest paperlinks papersources researchmanifests capabilityshowcase claimlanguage phase4targets phase5targets phase6targets phase7targets applicationguardrails glyphfixtures dimensioncheck dimensionindex dimensionimports dimensionmanifests dimensionpaperlinks nofake examples site-data sitenavcontract capabilitycontracts sitecheck quarto-dirs site-render site-render-check site-preview living-book-check

check: lean sourcecheck

sourcecheck: sidecarlean test manifest dictionary papermanifest paperlinks papersources researchmanifests capabilityshowcase claimlanguage phase4targets phase5targets phase6targets phase7targets applicationguardrails glyphfixtures dimensioncheck nofake sitecheck

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

researchmanifests:
	python scripts/check_research_manifests.py

capabilityshowcase:
	python scripts/check_capability_showcase.py

claimlanguage:
	python scripts/check_claim_language.py

phase4targets:
	python scripts/check_phase4_targets.py

phase5targets:
	python scripts/check_phase5_targets.py

phase6targets:
	python scripts/check_phase6_sweep_targets.py

phase7targets:
	python scripts/check_phase7_targets.py

applicationguardrails:
	python scripts/check_application_guardrails.py

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

sitenavcontract:
	python scripts/site/check_site_navigation_contract.py

capabilitycontracts:
	python scripts/site/check_capability_contracts.py

sitecheck: site-data
	python scripts/site/check_quarto_structure.py
	python scripts/site/check_site_navigation_contract.py
	python scripts/site/check_capability_contracts.py
	python scripts/site/check_site_scaffold_contract.py
	python scripts/site/check_site_manifest_links.py
	python scripts/site/check_site_dictionary_links.py
	python scripts/site/check_site_theorem_status.py
	python scripts/site/check_site_paper_links.py
	python scripts/site/check_site_source_links.py
	python scripts/site/check_site_static_source_links.py
	python scripts/site/check_site_data_backlinks.py
	python scripts/site/check_site_widget_contracts.py
	python scripts/site/check_site_accessibility_contract.py
	python scripts/site/check_widget_python_parity.py
	python scripts/site/check_widget_runtime_links.py

quarto-dirs:
	mkdir -p "$(QUARTO_HOME)" "$(QUARTO_DENO_DIR)" "site/_site"
	python -c 'from pathlib import Path; root = Path("site"); out = root / "_site"; [((out / path.relative_to(root)).mkdir(parents=True, exist_ok=True)) for path in root.rglob("*") if path.is_dir() and "_site" not in path.parts]'

site-render: site-data quarto-dirs
	$(QUARTO_ENV) python scripts/site/render_quarto_site.py "$(QUARTO)"

site-render-check:
	python scripts/site/check_rendered_site.py

site-preview: site-data quarto-dirs
	$(QUARTO_ENV) $(QUARTO) preview site

living-book-check: check site-render site-render-check
