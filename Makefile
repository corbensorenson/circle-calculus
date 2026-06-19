LAKE := $(shell command -v lake 2>/dev/null || printf "%s/.elan/bin/lake" "$$HOME")
QUARTO := $(shell if command -v quarto >/dev/null 2>&1; then command -v quarto; elif [ -x ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto" ]; then printf ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto"; else printf "quarto"; fi)
QUARTO_HOME ?= $(CURDIR)/.tools/quarto-home
QUARTO_DENO_DIR ?= $(CURDIR)/.tools/quarto-deno
QUARTO_ENV := HOME="$(QUARTO_HOME)" DENO_DIR="$(QUARTO_DENO_DIR)"
TARGETED_ARGS :=
ifneq ($(strip $(TARGETED_BASE)),)
TARGETED_ARGS += --base $(TARGETED_BASE)
endif
ifneq ($(strip $(TARGETED_FILES)),)
TARGETED_ARGS += --files $(TARGETED_FILES)
endif

.PHONY: check sourcecheck targeted-check targeted-check-list targeted-check-json targeted-check-full lean sidecarlean test manifest leannamecheck dictionary papermanifest paperlinks papersources researchmanifests capabilityshowcase claimlanguage phase4targets phase5targets phase6targets phase7targets phase8targets applicationguardrails glyphfixtures dimensioncheck dimensionindex dimensionimports dimensionmanifests dimensionpaperlinks nofake proofdepthaudit examples circle-ai-contracts circle-ai-contracts-check circle-ai-contracts-ready recurrence-schedule-certify strided-candidate-fanout-certify cyclic-memory-certify multicoil-phase-feature-certify circulant-block-cyclic-mixer-certify seed-rule-certify theseus-ai-contracts theseus-ai-feedback site-data sitenavcontract capabilitycontracts sitecheck quarto-dirs site-render site-render-check site-preview living-book-check

check: lean sourcecheck

sourcecheck: sidecarlean test manifest leannamecheck dictionary papermanifest paperlinks papersources researchmanifests capabilityshowcase circle-ai-contracts-ready claimlanguage phase4targets phase5targets phase6targets phase7targets phase8targets applicationguardrails glyphfixtures dimensioncheck nofake proofdepthaudit sitecheck

targeted-check:
	python scripts/targeted_check.py $(TARGETED_ARGS)

targeted-check-list:
	python scripts/targeted_check.py $(TARGETED_ARGS) --list

targeted-check-json:
	@python scripts/targeted_check.py $(TARGETED_ARGS) --list --format json

targeted-check-full:
	python scripts/targeted_check.py --full

lean:
	$(LAKE) build

sidecarlean:
	python scripts/check_lean_sidecars.py

test:
	python -m pytest

manifest:
	python scripts/check_manifest.py

leannamecheck:
	python scripts/check_manifest_lean_names.py

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

phase8targets:
	python scripts/check_phase8_targets.py

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

proofdepthaudit:
	python scripts/check_proof_depth_audit.py --fail-on-review-required

examples:
	python scripts/render_examples.py

circle-ai-contracts:
	python scripts/export_circle_ai_contracts.py

circle-ai-contracts-check: circle-ai-contracts
	python scripts/check_circle_ai_contract_pack.py
	python scripts/check_circle_ai_contract_docs.py

circle-ai-contracts-ready: circle-ai-contracts-check
	python scripts/circle_ai_contract_ready.py --list-kinds
	python scripts/circle_ai_contract_ready.py --list-recommendations
	python scripts/circle_ai_contract_ready.py --action-plan
	python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration --action-plan --include-values --format json
	python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability
	python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability --digest --format json --field d19_proved_request_status --field d19_impossible_request_status --include-recommendations
	python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer
	python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer --digest --field stale_probe_first_stale_token --field stale_probe_stale_requested_count
	python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage
	python scripts/circle_ai_contract_ready.py --kind strided_candidate_fanout
	python scripts/circle_ai_contract_ready.py --kind strided_candidate_fanout --digest --field gcd --field predicted_reach --field full_coverage --field effective_candidate_budget --field candidate_budget_accounting --field candidate_budget_shortfall --field duplicate_count --include-recommendations
	$(MAKE) strided-candidate-fanout-certify
	python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding
	python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding --digest --field same_residue_events --field same_residue_windings --field max_alias_load
	python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding --digest --field max_alias_load --include-recommendations
	$(MAKE) cyclic-memory-certify
	python scripts/circle_ai_contract_ready.py --kind multicoil_phase_feature
	python scripts/circle_ai_contract_ready.py --kind multicoil_phase_feature --digest --field phase_tuple --field joint_repeat_horizon --field shifted_phase_tuple --field relative_phase --field shifted_relative_phase --include-recommendations
	$(MAKE) multicoil-phase-feature-certify
	python scripts/circle_ai_contract_ready.py --kind circulant_block_cyclic_mixer
	python scripts/circle_ai_contract_ready.py --kind circulant_block_cyclic_mixer --digest --field max_abs_dense_delta --field circulant_parameters --field dense_parameters --field block_cyclic_parameters --field block_to_dense_ratio --include-recommendations
	$(MAKE) circulant-block-cyclic-mixer-certify
	python scripts/circle_ai_contract_ready.py --kind recurrence_schedule
	python scripts/circle_ai_contract_ready.py --kind recurrence_schedule --digest --field scheduled_work_saving --field post_period_multi_extension_scheduled_work_saving --include-recommendations
	$(MAKE) recurrence-schedule-certify
	python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration
	python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration --digest --field storage_saving --include-recommendations
	$(MAKE) seed-rule-certify

recurrence-schedule-certify:
	python scripts/recurrence_schedule_certify.py
	python scripts/recurrence_schedule_certify.py --format json >/dev/null

strided-candidate-fanout-certify:
	python scripts/strided_candidate_fanout_certify.py
	python scripts/strided_candidate_fanout_certify.py --format json >/dev/null
	python scripts/strided_candidate_fanout_certify.py --context-length 10 --stride 4 --start-index 1 --path-length 8 >/dev/null

cyclic-memory-certify:
	python scripts/cyclic_memory_certify.py
	python scripts/cyclic_memory_certify.py --format json >/dev/null
	python scripts/cyclic_memory_certify.py --bank-size 5 --event-index 12 --event-count 20 >/dev/null

multicoil-phase-feature-certify:
	python scripts/multicoil_phase_feature_certify.py
	python scripts/multicoil_phase_feature_certify.py --format json >/dev/null
	python scripts/multicoil_phase_feature_certify.py --periods 4,6 --position 10 --query-position 17 --key-position 5 >/dev/null

circulant-block-cyclic-mixer-certify:
	python scripts/circulant_block_cyclic_mixer_certify.py
	python scripts/circulant_block_cyclic_mixer_certify.py --format json >/dev/null
	python scripts/circulant_block_cyclic_mixer_certify.py --period 4 --channel-count 16 --block-size 4 >/dev/null

seed-rule-certify:
	python scripts/seed_rule_certify.py
	python scripts/seed_rule_certify.py --format json >/dev/null
	python scripts/seed_rule_certify.py --n 8 >/dev/null

theseus-ai-contracts:
	python scripts/export_theseus_hive_ai_contracts.py

theseus-ai-feedback:
	python scripts/import_theseus_hive_ai_feedback.py

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
	mkdir -p "$(QUARTO_HOME)" "$(QUARTO_DENO_DIR)"

site-render: site-data quarto-dirs
	$(QUARTO_ENV) python scripts/site/render_quarto_site.py "$(QUARTO)"

site-render-check:
	python scripts/site/check_rendered_site.py

site-preview: site-data quarto-dirs
	$(QUARTO_ENV) $(QUARTO) preview site

living-book-check: check site-render site-render-check
