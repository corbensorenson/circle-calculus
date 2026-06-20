LAKE := $(shell command -v lake 2>/dev/null || printf "%s/.elan/bin/lake" "$$HOME")
QUARTO := $(shell if command -v quarto >/dev/null 2>&1; then command -v quarto; elif [ -x ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto" ]; then printf ".tools/quarto-pkg/quarto-core.pkg/Payload/bin/quarto"; else printf "quarto"; fi)
QUARTO_HOME ?= $(CURDIR)/.tools/quarto-home
QUARTO_DENO_DIR ?= $(CURDIR)/.tools/quarto-deno
QUARTO_ENV := HOME="$(QUARTO_HOME)" DENO_DIR="$(QUARTO_DENO_DIR)"
TARGETED_ARGS :=
CIRCLE_PRIME_THREADS ?= 8
EXTERNAL_PRIME_THREADS ?= $(CIRCLE_PRIME_THREADS)
CIRCLE_PRIME_SEGMENT_SIZES ?= 0,32768,65536,98304,131072,196608,262144,524288,1048576,1310720,1376256,1441792,1507328,1572864,2097152,2359296,2621440,3145728,4194304
CIRCLE_PRIME_TUNE_COUNT_MODES ?= segmented,balanced,dynamic,prefix-pi,presieve13,presieve17,wheel30-mark,hybrid-wheel30-mark
CIRCLE_PRIME_BENCH_ONLY ?= scalar,next
CIRCLE_PRIME_BENCH_NAMES ?= scalar_u64_batch,next_prime_search
CIRCLE_PRIME_BENCH_ROUNDS ?= 7
CIRCLE_PRIME_BENCH_BASELINE ?= sidecars/PRIME_ENGINE/results/prime_engine_benchmark_latest.csv
CIRCLE_PRIME_BENCH_CANDIDATE ?= sidecars/PRIME_ENGINE/results/prime_engine_benchmark_candidate_latest.csv
CIRCLE_PRIME_BENCH_MAX_REGRESSION_RATIO ?= 1.05
CIRCLE_PRIME_BENCH_REQUIRE_IMPROVEMENT_RATIO ?=
CIRCLE_PRIME_BENCH_COMPARE_ARGS := --baseline $(CIRCLE_PRIME_BENCH_BASELINE) --max-regression-ratio $(CIRCLE_PRIME_BENCH_MAX_REGRESSION_RATIO)
CIRCLE_PRIME_EXTERNAL_COMPARE_ROUNDS ?= 7
CIRCLE_PRIME_EXTERNAL_COMPARE_RANGES ?= 0:10000000,0:100000000,1000000000000:1000010000000
CIRCLE_PRIME_EXTERNAL_COMPARE_BASELINE ?= sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_latest.csv
CIRCLE_PRIME_EXTERNAL_COMPARE_CANDIDATE ?= sidecars/PRIME_ENGINE/results/prime_engine_external_controls_candidate_latest.csv
CIRCLE_PRIME_EXTERNAL_COMPARE_SAMPLES ?= sidecars/PRIME_ENGINE/results/prime_engine_external_controls_candidate_samples_latest.csv
CIRCLE_PRIME_EXTERNAL_COMPARE_METADATA ?= sidecars/PRIME_ENGINE/results/prime_engine_external_controls_candidate_latest.json
CIRCLE_PRIME_COMPETITIVE_SHORT_ROUNDS ?= 5
CIRCLE_PRIME_COMPETITIVE_SHORT_BATCH_SIZE ?= 3
CIRCLE_PRIME_COMPETITIVE_SHORT_WARMUP_ROUNDS ?= 1
CIRCLE_PRIME_COMPETITIVE_SHORT_RANGES ?= 0:10000000,0:100000000,1000000000:2000000000,1000000000000:1000010000000
CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_BASELINE ?= sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_latest.csv
CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_CANDIDATE ?= sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_candidate_latest.csv
CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_SAMPLES ?= sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_candidate_samples_latest.csv
CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_METADATA ?= sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_candidate_latest.json
CIRCLE_PRIME_EXTERNAL_THROUGHPUT_MEDIAN_FLOOR ?= 1.0
CIRCLE_PRIME_HIGH_OFFSET_COMPARE_RANGES ?= 1000000000000:1000010000000
CIRCLE_PRIME_HIGH_OFFSET_COMPARE_ROUNDS ?= 25
CIRCLE_PRIME_HIGH_OFFSET_COMPARE_SEGMENT_SIZES ?= 786432,1048576,1310720,1376256,1441792,1507328,1572864,1835008,2097152,2621440,3145728
CIRCLE_PRIME_HIGH_OFFSET_COMPARE_COUNT_MODES ?= default,segmented,dynamic,balanced,presieve13,presieve17
CIRCLE_PRIME_HIGH_OFFSET_COMPARE_OUTPUT ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_compare_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_COMPARE_SAMPLES ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_compare_samples_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_COMPARE_METADATA ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_compare_latest.json
CIRCLE_PRIME_HIGH_OFFSET_QUICK_ROUNDS ?= 13
CIRCLE_PRIME_HIGH_OFFSET_QUICK_SEGMENT_SIZES ?= 1310720,1376256,1441792,1507328,2097152,3145728,4194304
CIRCLE_PRIME_HIGH_OFFSET_QUICK_COUNT_MODES ?= segmented,presieve13,presieve17
CIRCLE_PRIME_HIGH_OFFSET_QUICK_OUTPUT ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_quick_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_QUICK_SAMPLES ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_quick_samples_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_QUICK_METADATA ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_quick_latest.json
CIRCLE_PRIME_HIGH_OFFSET_TIGHT_ROUNDS ?= 17
CIRCLE_PRIME_HIGH_OFFSET_TIGHT_SEGMENT_SIZES ?= 1310720,1376256,1441792,1507328,4194304
CIRCLE_PRIME_HIGH_OFFSET_TIGHT_COUNT_MODES ?= segmented,presieve13,presieve17
CIRCLE_PRIME_HIGH_OFFSET_TIGHT_OUTPUT ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_tight_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_TIGHT_SAMPLES ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_tight_samples_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_TIGHT_METADATA ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_tight_latest.json
CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_ROUNDS ?= 11
CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_BATCH_SIZE ?= 3
CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_WARMUP_ROUNDS ?= 2
CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_VARIANTS ?= presieve13:1507328:1,presieve13:1507328:2,presieve13:1507328:3,presieve13:1507328:4,presieve13:1507328:5,presieve13:1507328:6,presieve13:1507328:7,presieve13:1507328:8,presieve13:2097152:4,presieve13:3145728:3,presieve13:4194304:3,presieve17:1507328:7
CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_OUTPUT ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_thread_sweep_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_SAMPLES ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_thread_sweep_samples_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_METADATA ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_thread_sweep_latest.json
CIRCLE_PRIME_HIGH_OFFSET_HOT_COLD_ROUNDS ?= 7
CIRCLE_PRIME_HIGH_OFFSET_HOT_COLD_OUTPUT ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_hot_cold_latest.csv
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_RUNS ?= 5
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_ROUNDS ?= 9
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_BATCH_SIZE ?= 3
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_WARMUP_ROUNDS ?= 1
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_MIN ?= 2
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_FAIL ?=
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_BASELINE_PRIORITY ?= external_primesieve_count_server,external_primesieve_count,external_primecount_pi_diff
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_EXTERNAL_BASELINES ?= external_primesieve_count_server
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_CIRCLE_SERVER_ONLY ?= 1
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_CIRCLE_VARIANTS ?= default:0,presieve13:1310720,presieve13:1441792,presieve13:1507328,presieve17:1507328,presieve17:4194304,balanced:1507328
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_OUTPUT ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_confirmation_latest.json
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_MD ?= sidecars/PRIME_ENGINE/results/prime_engine_high_offset_confirmation_latest.md
CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_RUNS ?= 3
CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_BATCH_SIZE ?= 3
CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_MIN ?= 2
CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_FAIL ?=
CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_SEGMENT_SIZES ?= 0
CIRCLE_PRIME_EXTERNAL_MIN_MEDIAN_SPEEDUP_RATIO ?= 0.90
CIRCLE_PRIME_EXTERNAL_MIN_BEST_SPEEDUP_RATIO ?= 0.85
CIRCLE_PRIME_EXTERNAL_MEDIAN_REGRESSION_BEST_FLOOR ?= 0.90
CIRCLE_PRIME_EXTERNAL_COMPARE_NAMES ?=
CIRCLE_PRIME_EXTERNAL_COMPARE_BASELINES ?= external_primesieve_count
CIRCLE_PRIME_EXTERNAL_REQUIRE_ANY_MEDIAN_SPEEDUP ?=
CIRCLE_PRIME_EXTERNAL_COMPARE_ARGS := --baseline $(CIRCLE_PRIME_EXTERNAL_COMPARE_BASELINE) --min-median-speedup-ratio $(CIRCLE_PRIME_EXTERNAL_MIN_MEDIAN_SPEEDUP_RATIO) --min-best-speedup-ratio $(CIRCLE_PRIME_EXTERNAL_MIN_BEST_SPEEDUP_RATIO) --median-regression-best-speedup-ratio-floor $(CIRCLE_PRIME_EXTERNAL_MEDIAN_REGRESSION_BEST_FLOOR)
CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_ARGS := --baseline $(CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_BASELINE) --names circle_prime_default_count --baselines external_primesieve_count --min-median-speedup-ratio 0.0 --min-best-speedup-ratio 0.0 --require-each-median-speedup-at-least $(CIRCLE_PRIME_EXTERNAL_THROUGHPUT_MEDIAN_FLOOR)
CIRCLE_PRIME_EXTERNAL_NEXT_STARTS ?= 90,1000000,4294967000,1000000000000,18446744073709551500
CIRCLE_PRIME_EXTERNAL_NEXT_ROUNDS ?= 5
CIRCLE_PRIME_EXTERNAL_NEXT_BATCH_SIZE ?= 4
CIRCLE_PRIME_EXTERNAL_NEXT_PRIMECOUNT_MAX_START ?= 1000000000000
CIRCLE_PRIME_EXTERNAL_NEXT_PRIMESIEVE_LIBRARY_MAX_START ?= 18446744073709551615
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_STARTS ?= 4294967000,1000000000000,18446744073709551500
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_BASELINES ?= external_primesieve_next_prime,external_primesieve_generate_next_server
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_BASELINE ?= sidecars/PRIME_ENGINE/results/prime_engine_external_next_latest.csv
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_CANDIDATE ?= sidecars/PRIME_ENGINE/results/prime_engine_external_next_candidate_latest.csv
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_SAMPLES ?= sidecars/PRIME_ENGINE/results/prime_engine_external_next_candidate_samples_latest.csv
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_METADATA ?= sidecars/PRIME_ENGINE/results/prime_engine_external_next_candidate_latest.json
CIRCLE_PRIME_EXTERNAL_NEXT_MIN_MEDIAN_SPEEDUP_RATIO ?= 0.85
CIRCLE_PRIME_EXTERNAL_NEXT_MIN_BEST_SPEEDUP_RATIO ?= 0.85
CIRCLE_PRIME_EXTERNAL_NEXT_MEDIAN_REGRESSION_BEST_FLOOR ?= 0.90
CIRCLE_PRIME_EXTERNAL_NEXT_BEST_REGRESSION_MEDIAN_FLOOR ?= 0.90
CIRCLE_PRIME_EXTERNAL_NEXT_DOMINANT_SPEEDUP_FLOOR ?= 1000.0
CIRCLE_PRIME_EXTERNAL_NEXT_DOMINANT_MIN_SPEEDUP_RATIO ?= 0.75
CIRCLE_PRIME_EXTERNAL_NEXT_REQUIRE_ANY_MEDIAN_SPEEDUP ?= 1.0
CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_LIB_BASELINE ?= external_primesieve_generate_next_server
CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_LIB_MEDIAN_FLOOR ?= 1.0
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_ARGS := --baseline $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_BASELINE) --starts $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_STARTS) --min-median-speedup-ratio $(CIRCLE_PRIME_EXTERNAL_NEXT_MIN_MEDIAN_SPEEDUP_RATIO) --min-best-speedup-ratio $(CIRCLE_PRIME_EXTERNAL_NEXT_MIN_BEST_SPEEDUP_RATIO) --median-regression-best-speedup-ratio-floor $(CIRCLE_PRIME_EXTERNAL_NEXT_MEDIAN_REGRESSION_BEST_FLOOR) --best-regression-median-speedup-ratio-floor $(CIRCLE_PRIME_EXTERNAL_NEXT_BEST_REGRESSION_MEDIAN_FLOOR) --dominant-speedup-floor $(CIRCLE_PRIME_EXTERNAL_NEXT_DOMINANT_SPEEDUP_FLOOR) --dominant-min-speedup-ratio $(CIRCLE_PRIME_EXTERNAL_NEXT_DOMINANT_MIN_SPEEDUP_RATIO)
CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_LIB_COMPARE_ARGS := $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_ARGS) --names circle_prime_server_next_prime --baselines $(CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_LIB_BASELINE) --require-each-median-speedup-at-least $(CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_LIB_MEDIAN_FLOOR)
ifneq ($(strip $(CIRCLE_PRIME_BENCH_NAMES)),)
CIRCLE_PRIME_BENCH_COMPARE_ARGS += --names $(CIRCLE_PRIME_BENCH_NAMES)
endif
ifneq ($(strip $(CIRCLE_PRIME_BENCH_REQUIRE_IMPROVEMENT_RATIO)),)
CIRCLE_PRIME_BENCH_COMPARE_ARGS += --require-improvement-ratio $(CIRCLE_PRIME_BENCH_REQUIRE_IMPROVEMENT_RATIO)
endif
ifneq ($(strip $(CIRCLE_PRIME_EXTERNAL_COMPARE_NAMES)),)
CIRCLE_PRIME_EXTERNAL_COMPARE_ARGS += --names $(CIRCLE_PRIME_EXTERNAL_COMPARE_NAMES)
endif
ifneq ($(strip $(CIRCLE_PRIME_EXTERNAL_COMPARE_BASELINES)),)
CIRCLE_PRIME_EXTERNAL_COMPARE_ARGS += --baselines $(CIRCLE_PRIME_EXTERNAL_COMPARE_BASELINES)
endif
ifneq ($(strip $(CIRCLE_PRIME_EXTERNAL_REQUIRE_ANY_MEDIAN_SPEEDUP)),)
CIRCLE_PRIME_EXTERNAL_COMPARE_ARGS += --require-any-median-speedup-at-least $(CIRCLE_PRIME_EXTERNAL_REQUIRE_ANY_MEDIAN_SPEEDUP)
endif
ifneq ($(strip $(CIRCLE_PRIME_EXTERNAL_NEXT_REQUIRE_ANY_MEDIAN_SPEEDUP)),)
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_ARGS += --require-any-median-speedup-at-least $(CIRCLE_PRIME_EXTERNAL_NEXT_REQUIRE_ANY_MEDIAN_SPEEDUP)
endif
ifneq ($(strip $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_BASELINES)),)
CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_ARGS += --baselines $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_BASELINES)
endif
CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_ARGS := --runs $(CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_RUNS) --rounds 5 --batch-size $(CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_BATCH_SIZE) --ranges $(CIRCLE_PRIME_EXTERNAL_COMPARE_RANGES) --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --segment-sizes $(CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_SEGMENT_SIZES) --min-confirmations $(CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_MIN)
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_ARGS := --runs $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_RUNS) --rounds $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_ROUNDS) --batch-size $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_BATCH_SIZE) --warmup-rounds $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_WARMUP_ROUNDS) --ranges $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_RANGES) --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --external-baselines $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_EXTERNAL_BASELINES) --segment-sizes $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_SEGMENT_SIZES) --circle-count-modes $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_COUNT_MODES) --circle-variant $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_CIRCLE_VARIANTS) --include-circle-server --include-primesieve-count-server --require-tool primesieve-library --baseline-priority $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_BASELINE_PRIORITY) --min-confirmations $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_MIN) --output-json $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_OUTPUT) --output-md $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_MD)
ifneq ($(strip $(CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_FAIL)),)
CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_ARGS += --fail-on-unconfirmed
endif
ifneq ($(strip $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_FAIL)),)
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_ARGS += --fail-on-unconfirmed
endif
ifneq ($(strip $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_CIRCLE_SERVER_ONLY)),)
CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_ARGS += --circle-server-only
endif
ifneq ($(strip $(TARGETED_BASE)),)
TARGETED_ARGS += --base $(TARGETED_BASE)
endif
ifneq ($(strip $(TARGETED_FILES)),)
TARGETED_ARGS += --files $(TARGETED_FILES)
endif

.PHONY: check sourcecheck targeted-check targeted-check-list targeted-check-json targeted-check-full lean sidecarlean test manifest leannamecheck dictionary papermanifest paperlinks papersources researchmanifests capabilityshowcase claimlanguage phase4targets phase5targets phase6targets phase7targets phase8targets applicationguardrails glyphfixtures dimensioncheck dimensionindex dimensionimports dimensionmanifests dimensionpaperlinks nofake proofdepthaudit examples prime-engine-check prime-engine-benchmark prime-engine-benchmark-record prime-engine-benchmark-compare prime-engine-external-correctness prime-engine-external-controls prime-engine-external-controls-parallel prime-engine-external-controls-compare prime-engine-competitive-short prime-engine-high-offset-quick prime-engine-high-offset-tight prime-engine-high-offset-thread-sweep prime-engine-high-offset-hot-cold prime-engine-high-offset-confirm prime-engine-high-offset-compare prime-engine-external-next prime-engine-external-next-compare prime-engine-external-throughput prime-engine-external-throughput-compare prime-engine-external-segment-sweep prime-engine-external-mode-sweep prime-engine-external-mode-confirm prime-engine-calibrate-defaults prime-engine-calibrate-defaults-check prime-engine-tune prime-engine-tune-night prime-engine-report prime-engine-overnight prime-engine-overnight-improve circle-ai-contracts circle-ai-contracts-check circle-ai-contracts-ready recurrence-schedule-certify strided-candidate-fanout-certify cyclic-memory-certify multicoil-phase-feature-certify seed-rule-certify theseus-ai-contracts theseus-ai-feedback site-data sitenavcontract capabilitycontracts sitecheck quarto-dirs site-render site-render-check site-preview living-book-check

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

prime-engine-check:
	python scripts/check_prime_engine.py

prime-engine-benchmark:
	python scripts/check_prime_engine.py --benchmark --benchmark-rounds 3 --min-primal-speedup 1.0

prime-engine-benchmark-record:
	python scripts/check_prime_engine.py --benchmark --benchmark-rounds 5 --min-primal-speedup 1.0 --benchmark-output sidecars/PRIME_ENGINE/results/prime_engine_benchmark_latest.csv

prime-engine-benchmark-compare:
	mkdir -p sidecars/PRIME_ENGINE/results
	cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds $(CIRCLE_PRIME_BENCH_ROUNDS) --only $(CIRCLE_PRIME_BENCH_ONLY) > $(CIRCLE_PRIME_BENCH_CANDIDATE)
	python scripts/compare_prime_engine_benchmarks.py $(CIRCLE_PRIME_BENCH_CANDIDATE) $(CIRCLE_PRIME_BENCH_COMPARE_ARGS)

prime-engine-external-correctness:
	python scripts/check_prime_external_correctness.py --require-tool primesieve --require-tool primecount --circle-count-modes all --segment-sizes 0,65536,196608,1310720,1441792,1507328,2621440,4194304 --output sidecars/PRIME_ENGINE/results/prime_engine_external_correctness_latest.json

prime-engine-external-controls:
	python scripts/benchmark_prime_external_controls.py --rounds 7 --interleaved --require-tool primesieve --require-tool primecount --circle-count-modes default --output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_latest.csv --sample-output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_samples_latest.csv --metadata-output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_latest.json

prime-engine-external-controls-parallel:
	python scripts/benchmark_prime_external_controls.py --rounds 7 --interleaved --include-circle-server --include-primesieve-count-server --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --circle-count-modes default --output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_latest.csv --sample-output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_samples_latest.csv --metadata-output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_latest.json

prime-engine-external-controls-compare:
	python scripts/benchmark_prime_external_controls.py --ranges $(CIRCLE_PRIME_EXTERNAL_COMPARE_RANGES) --rounds $(CIRCLE_PRIME_EXTERNAL_COMPARE_ROUNDS) --interleaved --include-circle-server --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --circle-count-modes default --output $(CIRCLE_PRIME_EXTERNAL_COMPARE_CANDIDATE) --sample-output $(CIRCLE_PRIME_EXTERNAL_COMPARE_SAMPLES) --metadata-output $(CIRCLE_PRIME_EXTERNAL_COMPARE_METADATA)
	python scripts/compare_prime_external_controls.py $(CIRCLE_PRIME_EXTERNAL_COMPARE_CANDIDATE) $(CIRCLE_PRIME_EXTERNAL_COMPARE_ARGS)

prime-engine-competitive-short:
	python scripts/benchmark_prime_external_controls.py --ranges $(CIRCLE_PRIME_COMPETITIVE_SHORT_RANGES) --rounds $(CIRCLE_PRIME_COMPETITIVE_SHORT_ROUNDS) --batch-size $(CIRCLE_PRIME_COMPETITIVE_SHORT_BATCH_SIZE) --warmup-rounds $(CIRCLE_PRIME_COMPETITIVE_SHORT_WARMUP_ROUNDS) --interleaved --include-circle-server --include-primesieve-count-server --require-tool primesieve --require-tool primecount --require-tool primesieve-library --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --circle-count-modes default --output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_latest.csv --sample-output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_samples_latest.csv --metadata-output sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_latest.json
	$(MAKE) prime-engine-report

prime-engine-high-offset-compare:
	python scripts/benchmark_prime_external_controls.py --ranges $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_RANGES) --rounds $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_ROUNDS) --interleaved --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --segment-sizes $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_SEGMENT_SIZES) --circle-count-modes $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_COUNT_MODES) --output $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_OUTPUT) --sample-output $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_SAMPLES) --metadata-output $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_METADATA)

prime-engine-high-offset-quick:
	python scripts/benchmark_prime_external_controls.py --ranges $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_RANGES) --rounds $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_ROUNDS) --interleaved --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --segment-sizes $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_SEGMENT_SIZES) --circle-count-modes $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_COUNT_MODES) --output $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_OUTPUT) --sample-output $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_SAMPLES) --metadata-output $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_METADATA)

prime-engine-high-offset-tight:
	python scripts/benchmark_prime_external_controls.py --ranges $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_RANGES) --rounds $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_ROUNDS) --interleaved --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --segment-sizes $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_SEGMENT_SIZES) --circle-count-modes $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_COUNT_MODES) --output $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_OUTPUT) --sample-output $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_SAMPLES) --metadata-output $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_METADATA)

prime-engine-high-offset-thread-sweep:
	python scripts/benchmark_prime_external_controls.py --ranges $(CIRCLE_PRIME_HIGH_OFFSET_COMPARE_RANGES) --rounds $(CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_ROUNDS) --batch-size $(CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_BATCH_SIZE) --warmup-rounds $(CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_WARMUP_ROUNDS) --interleaved --include-circle-server --include-primesieve-count-server --require-tool primesieve-library --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --circle-variant $(CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_VARIANTS) --output $(CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_OUTPUT) --sample-output $(CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_SAMPLES) --metadata-output $(CIRCLE_PRIME_HIGH_OFFSET_THREAD_SWEEP_METADATA)

prime-engine-high-offset-hot-cold:
	mkdir -p sidecars/PRIME_ENGINE/results
	cargo build --release -p circle-prime --bin circle-prime
	cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds $(CIRCLE_PRIME_HIGH_OFFSET_HOT_COLD_ROUNDS) --only high-offset,cold > $(CIRCLE_PRIME_HIGH_OFFSET_HOT_COLD_OUTPUT)

prime-engine-high-offset-confirm:
	python scripts/confirm_prime_external_modes.py $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_ARGS)

prime-engine-external-next:
	python scripts/benchmark_prime_external_next.py --starts $(CIRCLE_PRIME_EXTERNAL_NEXT_STARTS) --rounds $(CIRCLE_PRIME_EXTERNAL_NEXT_ROUNDS) --batch-size $(CIRCLE_PRIME_EXTERNAL_NEXT_BATCH_SIZE) --include-circle-server --include-primecount --include-primesieve-library-server --primecount-max-start $(CIRCLE_PRIME_EXTERNAL_NEXT_PRIMECOUNT_MAX_START) --primesieve-library-max-start $(CIRCLE_PRIME_EXTERNAL_NEXT_PRIMESIEVE_LIBRARY_MAX_START) --external-threads $(EXTERNAL_PRIME_THREADS) --require-tool primesieve --require-tool primecount --require-tool primesieve-library --output sidecars/PRIME_ENGINE/results/prime_engine_external_next_latest.csv --sample-output sidecars/PRIME_ENGINE/results/prime_engine_external_next_samples_latest.csv --metadata-output sidecars/PRIME_ENGINE/results/prime_engine_external_next_latest.json

prime-engine-external-next-compare:
	python scripts/benchmark_prime_external_next.py --starts $(CIRCLE_PRIME_EXTERNAL_NEXT_STARTS) --rounds $(CIRCLE_PRIME_EXTERNAL_NEXT_ROUNDS) --batch-size $(CIRCLE_PRIME_EXTERNAL_NEXT_BATCH_SIZE) --include-circle-server --include-primecount --include-primesieve-library-server --primecount-max-start $(CIRCLE_PRIME_EXTERNAL_NEXT_PRIMECOUNT_MAX_START) --primesieve-library-max-start $(CIRCLE_PRIME_EXTERNAL_NEXT_PRIMESIEVE_LIBRARY_MAX_START) --external-threads $(EXTERNAL_PRIME_THREADS) --require-tool primesieve --require-tool primecount --require-tool primesieve-library --output $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_CANDIDATE) --sample-output $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_SAMPLES) --metadata-output $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_METADATA)
	python scripts/compare_prime_external_next.py $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_CANDIDATE) $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_ARGS)
	python scripts/compare_prime_external_next.py $(CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_CANDIDATE) $(CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_LIB_COMPARE_ARGS)

prime-engine-external-throughput:
	python scripts/benchmark_prime_external_controls.py --ranges 0:1000000000,1000000000:2000000000 --rounds 5 --interleaved --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --circle-variant default:0 --circle-variant segmented:131072 --circle-variant segmented:196608 --circle-variant segmented:262144 --circle-variant segmented:524288 --circle-variant prefix-pi:0:1 --circle-variant prefix-pi:0 --output sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_latest.csv --sample-output sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_samples_latest.csv --metadata-output sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_latest.json

prime-engine-external-throughput-compare:
	python scripts/benchmark_prime_external_controls.py --ranges 0:1000000000,1000000000:2000000000 --rounds 5 --interleaved --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --circle-variant default:0 --circle-variant segmented:131072 --circle-variant segmented:196608 --circle-variant segmented:262144 --circle-variant segmented:524288 --circle-variant prefix-pi:0:1 --circle-variant prefix-pi:0 --output $(CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_CANDIDATE) --sample-output $(CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_SAMPLES) --metadata-output $(CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_METADATA)
	python scripts/compare_prime_external_controls.py $(CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_CANDIDATE) $(CIRCLE_PRIME_EXTERNAL_THROUGHPUT_COMPARE_ARGS)

prime-engine-external-segment-sweep:
	python scripts/benchmark_prime_external_controls.py --rounds 5 --interleaved --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --segment-sizes $(CIRCLE_PRIME_SEGMENT_SIZES) --output sidecars/PRIME_ENGINE/results/prime_engine_external_segment_sweep_latest.csv --sample-output sidecars/PRIME_ENGINE/results/prime_engine_external_segment_sweep_samples_latest.csv --metadata-output sidecars/PRIME_ENGINE/results/prime_engine_external_segment_sweep_latest.json

prime-engine-external-mode-sweep:
	python scripts/benchmark_prime_external_controls.py --rounds 5 --interleaved --require-tool primesieve --require-tool primecount --circle-threads $(CIRCLE_PRIME_THREADS) --external-threads $(EXTERNAL_PRIME_THREADS) --circle-count-modes segmented,balanced,dynamic,prefix-pi,presieve13,presieve17,wheel30-mark,hybrid-wheel30-mark --output sidecars/PRIME_ENGINE/results/prime_engine_external_mode_sweep_latest.csv --sample-output sidecars/PRIME_ENGINE/results/prime_engine_external_mode_sweep_samples_latest.csv --metadata-output sidecars/PRIME_ENGINE/results/prime_engine_external_mode_sweep_latest.json

prime-engine-external-mode-confirm:
	python scripts/confirm_prime_external_modes.py $(CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_ARGS)

prime-engine-calibrate-defaults:
	cargo build --release -p circle-prime --bin circle-prime
	python scripts/calibrate_prime_engine_defaults.py --external-high-offset-quick $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_OUTPUT) --external-high-offset-quick-metadata $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_METADATA) --external-high-offset-tight $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_OUTPUT) --external-high-offset-tight-metadata $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_METADATA) --external-high-offset-confirmation $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_OUTPUT)

prime-engine-calibrate-defaults-check:
	cargo build --release -p circle-prime --bin circle-prime
	python scripts/calibrate_prime_engine_defaults.py --external-high-offset-quick $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_OUTPUT) --external-high-offset-quick-metadata $(CIRCLE_PRIME_HIGH_OFFSET_QUICK_METADATA) --external-high-offset-tight $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_OUTPUT) --external-high-offset-tight-metadata $(CIRCLE_PRIME_HIGH_OFFSET_TIGHT_METADATA) --external-high-offset-confirmation $(CIRCLE_PRIME_HIGH_OFFSET_CONFIRM_OUTPUT) --fail-on-drift

prime-engine-apply-defaults:
	python scripts/apply_prime_engine_defaults.py

prime-engine-apply-defaults-check:
	python scripts/apply_prime_engine_defaults.py --check

prime-engine-tune:
	python scripts/tune_prime_engine.py --rounds 9 --ranges 0:1000000,0:10000000,0:100000000,1000000000000:1000010000000 --segment-sizes 32768,65536,98304,131072,196608,262144,524288,1048576,1310720,1376256,1441792,1507328,1572864,2097152,2359296,2621440,3145728,4194304 --thread-counts 1,2,4,8 --count-modes $(CIRCLE_PRIME_TUNE_COUNT_MODES)

prime-engine-tune-night:
	python scripts/tune_prime_engine.py --seconds 28800 --rounds 5 --ranges 0:1000000,0:10000000,1000000000:1010000000,100000000000:100010000000,1000000000000:1000010000000 --segment-sizes 32768,65536,131072,196608,262144,524288,1048576,1310720,1376256,1441792,1507328,1572864,2097152,2359296,2621440,3145728,4194304 --thread-counts 1,2,3,4,8 --count-modes $(CIRCLE_PRIME_TUNE_COUNT_MODES)

prime-engine-report:
	python scripts/report_prime_engine_results.py --require-inputs

prime-engine-overnight:
	$(MAKE) prime-engine-benchmark-record
	$(MAKE) prime-engine-external-correctness
	$(MAKE) prime-engine-external-controls-parallel
	$(MAKE) prime-engine-external-next
	$(MAKE) prime-engine-external-mode-sweep
	$(MAKE) prime-engine-external-mode-confirm
	$(MAKE) prime-engine-external-throughput
	$(MAKE) prime-engine-external-segment-sweep
	$(MAKE) prime-engine-tune-night
	$(MAKE) prime-engine-calibrate-defaults
	$(MAKE) prime-engine-report

prime-engine-overnight-improve:
	$(MAKE) prime-engine-overnight
	$(MAKE) prime-engine-apply-defaults
	cargo fmt --all
	$(MAKE) prime-engine-check
	$(MAKE) prime-engine-apply-defaults-check
	$(MAKE) prime-engine-benchmark-compare CIRCLE_PRIME_BENCH_ONLY=parallel,high-offset CIRCLE_PRIME_BENCH_NAMES=parallel_segmented_range_count_8t,parallel_high_offset_default_range_count_8t CIRCLE_PRIME_BENCH_ROUNDS=5 CIRCLE_PRIME_BENCH_MAX_REGRESSION_RATIO=1.10
	$(MAKE) prime-engine-external-controls-compare
	$(MAKE) prime-engine-external-next-compare
	$(MAKE) prime-engine-benchmark-record
	$(MAKE) prime-engine-external-correctness
	$(MAKE) prime-engine-external-controls-parallel
	$(MAKE) prime-engine-external-next
	$(MAKE) prime-engine-calibrate-defaults-check
	$(MAKE) prime-engine-report

circle-ai-contracts:
	python scripts/export_circle_ai_contracts.py

circle-ai-contracts-check: circle-ai-contracts
	python scripts/check_circle_ai_contract_pack.py
	python scripts/check_circle_ai_contract_docs.py

circle-ai-contracts-ready: circle-ai-contracts-check
	python scripts/example_validate_circle_ai_contract_pack_schema.py --summary >/dev/null
	python scripts/circle_ai_contract_ready.py
	python scripts/circle_ai_contract_ready.py --list-kinds
	python scripts/circle_ai_contract_ready.py --list-recommendations
	python scripts/circle_ai_contract_ready.py --action-plan
	python scripts/circle_ai_contract_ready.py --action-plan --recommendation ROPE-USE-D19-MARGIN-FRONTIER --format json >/dev/null
	python scripts/circle_ai_contract_ready.py --action-plan --recommendation ROPE-USE-D19-MARGIN-FRONTIER --include-values --format json >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --all-readiness >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --fingerprints >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --planner --planner-kind sparse_attention_coverage --planner-kind rope_position_distinguishability >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --planner --planner-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --planner-include-values >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --planner --planner-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK --planner-include-values >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --planner --planner-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST --planner-include-values >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --planner --planner-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE --planner-include-values >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --planner --planner-kind rope_position_distinguishability --planner-recommendation ROPE-USE-D19-MARGIN-FRONTIER --planner-include-values >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --kind kv_cache_ring_buffer --readiness >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --kind sparse_attention_coverage --field first_uncovered_lag --include-recommendations >/dev/null
	python scripts/example_consume_circle_ai_contract_pack.py --kind sparse_attention_coverage --receipt --field first_uncovered_lag --require-theorem AIT-T0104 --require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --require-recommendation-evidence-field SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start --require-recommendation-theorem SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104 >/dev/null
	python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage --receipt --format json --field first_uncovered_lag --field first_uncovered_interval_start --field complete_repair_window --field complete_repair_window_covers_context --field complete_repair_window_minimal_for_declared_stride_family --field complete_repair_window_minimal_witness_lag --require-theorem AIT-T0104 --require-theorem AIT-T0172 --require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --require-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK --require-recommendation-evidence-field SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start --require-recommendation-evidence-field SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_covers_context --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_uses_dense_threshold --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=local_window_complete_threshold_is_exact_local_minimum --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_for_declared_stride_family --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_witness_lag --require-recommendation-theorem SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0023 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0034 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0168 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0169 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0170 --require-recommendation-action-parameter SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window --require-recommendation-action-parameter SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window --require-recommendation-action-parameter SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots --require-recommendation-action-parameter-path SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window --require-recommendation-action-parameter-path SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window --require-recommendation-action-parameter-path SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots >/dev/null
	python scripts/check_circle_ai_contract_acceptance_policy.py --format json >/dev/null
	python scripts/check_downstream_ci_acceptance_example.py --summary
	python examples/downstream_ci_accept_circle_ai_contracts.py --format json >/dev/null
	python examples/downstream_ci_accept_circle_ai_contracts.py --format json --planner-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --include-values >/dev/null
	python examples/downstream_ci_accept_circle_ai_contracts.py --format json --planner-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK --include-values >/dev/null
	python examples/downstream_ci_accept_circle_ai_contracts.py --format json --planner-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST --include-values >/dev/null
	python examples/downstream_ci_accept_circle_ai_contracts.py --format json --planner-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE --include-values >/dev/null
	python examples/downstream_ci_accept_circle_ai_contracts.py --format json --planner-recommendation ROPE-USE-D19-MARGIN-FRONTIER --include-values >/dev/null
	python scripts/circle_ai_contract_ready.py --acceptance-policy
	python scripts/circle_ai_contract_ready.py --acceptance-policy --format json >/dev/null
	python scripts/circle_ai_contract_ready.py --print-refreshed-policy >/dev/null
	python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration --action-plan --include-values --format json >/dev/null
	python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability
	python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability --digest --format json --field d19_proved_request_status --field d19_impossible_request_status --field d19_undecided_request_status --field d19_proved_first_channel_bank_transfer --field d19_proved_first_channel_bank_shape --field d19_proved_first_channel_pair_scope --field d19_proved_first_channel_context_wide_contract --field d19_proved_first_channel_bank_tolerance_rule --include-recommendations >/dev/null
	python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability --receipt --format json --field d19_proved_request_status --field d19_impossible_request_status --field d19_undecided_request_status --field d19_proved_first_channel_bank_transfer --field d19_proved_first_channel_bank_shape --field d19_proved_first_channel_pair_scope --field d19_proved_first_channel_context_wide_contract --field d19_proved_first_channel_bank_tolerance_rule --require-theorem AIRA-T0171 --require-theorem AIRA-T0172 --require-theorem AIRA-T0234 --require-theorem AIRA-T0235 --require-recommendation ROPE-USE-D19-MARGIN-FRONTIER --require-recommendation-evidence-field ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_bank_transfer --require-recommendation-evidence-field ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_context_wide_contract --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234 --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235 --require-recommendation-action-parameter ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer --require-recommendation-action-parameter-path ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.applies --require-recommendation-action-parameter-path ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.context_wide_contract --require-recommendation-action-parameter-path ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.theorem_ids >/dev/null
	python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer
	python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer --digest --field stale_probe_first_stale_token --field stale_probe_stale_requested_count
	python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer --receipt --format json --field stale_probe_first_stale_token --field sink_tokens_retained_by_policy --field sink_window_exact_policy --field sink_window_tokens_distinct --field sink_prefix_disjoint_from_live_window --field sink_tokens_outside_ordinary_rolling_window --require-theorem AIM-T0103 --require-theorem AIM-T0104 --require-theorem AIM-T0149 --require-recommendation KV-DROP-STALE-REQUEST-TOKEN --require-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST --require-recommendation-evidence-field KV-DROP-STALE-REQUEST-TOKEN=stale_probe_first_stale_token --require-recommendation-evidence-field KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_tokens_retained_by_policy --require-recommendation-evidence-field KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_tokens_outside_ordinary_rolling_window --require-recommendation-theorem KV-DROP-STALE-REQUEST-TOKEN=AIM-T0103 --require-recommendation-theorem KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149 --require-recommendation-action-parameter KV-DROP-STALE-REQUEST-TOKEN=target_token --require-recommendation-action-parameter KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size --require-recommendation-action-parameter-path KV-DROP-STALE-REQUEST-TOKEN=target_token --require-recommendation-action-parameter-path KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size --require-recommendation-action-parameter-path KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count --require-recommendation-action-parameter-path KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count_bound --require-recommendation-action-parameter-path KV-USE-SINK-ROLLING-WINDOW-REQUEST=cache_size --require-recommendation-action-parameter-path KV-USE-SINK-ROLLING-WINDOW-REQUEST=current >/dev/null
	python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage --receipt --format json --field first_uncovered_lag --field first_uncovered_interval_start --field complete_repair_window --field complete_repair_window_covers_context --field complete_repair_window_minimal_for_declared_stride_family --field complete_repair_window_minimal_witness_lag --require-theorem AIT-T0104 --require-theorem AIT-T0172 --require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --require-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK --require-recommendation-evidence-field SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start --require-recommendation-evidence-field SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_covers_context --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_uses_dense_threshold --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=local_window_complete_threshold_is_exact_local_minimum --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_for_declared_stride_family --require-recommendation-evidence-field SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_witness_lag --require-recommendation-theorem SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0023 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0034 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0168 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0169 --require-recommendation-theorem SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0170 --require-recommendation-action-parameter SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window --require-recommendation-action-parameter SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window --require-recommendation-action-parameter SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots --require-recommendation-action-parameter-path SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window --require-recommendation-action-parameter-path SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window --require-recommendation-action-parameter-path SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots >/dev/null
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
	python scripts/circle_ai_contract_ready.py --kind recurrence_schedule --receipt --format json --field periodic_shift_required_steps_invariant --field periodic_shift_active_at_step_invariant --field total_active_token_work --field scheduled_work_saving --field scheduled_work_saving_accounting --field active_inactive_work_accounting --field scheduled_work_saving_positive --field post_period_multi_extension_scheduled_work_saving --require-theorem AIM-T0026 --require-theorem AIM-T0130 --require-theorem AIM-T0159 --require-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE --require-recommendation RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT --require-recommendation-evidence-field RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=total_active_token_work --require-recommendation-evidence-field RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving --require-recommendation-evidence-field RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=post_period_multi_extension_scheduled_work_saving --require-recommendation-evidence-field RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=periodic_shift_required_steps_invariant --require-recommendation-evidence-field RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=periodic_shift_active_at_step_invariant --require-recommendation-theorem RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130 --require-recommendation-theorem RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159 --require-recommendation-theorem RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026 --require-recommendation-action-parameter RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period --require-recommendation-action-parameter RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving --require-recommendation-action-parameter RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving --require-recommendation-action-parameter-path RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=post_period_multi_extension_scheduled_work_saving --require-recommendation-action-parameter-path RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token --require-recommendation-action-parameter-path RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token --require-recommendation-action-parameter-path RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount >/dev/null
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
