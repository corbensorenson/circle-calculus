from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.report_prime_engine_results import (
    apply_count_binary_cold_confirmation_readout,
    build_report,
    circle_row_label,
    high_offset_promotion_action,
    high_offset_shifted_candidate_action,
    render_external_segment_sweep_markdown,
    render_external_control_provenance_markdown,
    render_markdown,
    sample_spread_text,
    sample_stats,
    summarize_external_control_provenance,
    summarize_external_metadata,
    summarize_external_next_metadata,
    summarize_high_offset_count_binary_segment_sweep,
    summarize_high_offset_promotion_readout,
    summarize_high_offset_shifted_candidate_readout,
)


def test_external_metadata_summary_preserves_provenance_hashes() -> None:
    metadata = {
        "circle_prime_defaults": {
            "available": True,
            "path": "rust/circle-prime/prime_engine_defaults.json",
            "sha256": "d" * 64,
            "modified_at_utc": "2026-01-01T00:00:00Z",
        },
        "tools": {
            "circle_prime": {
                "available": True,
                "path": "target/release/circle-prime",
                "binary": {"available": True, "sha256": "b" * 64},
                "defaults": {"available": True, "sha256": "d" * 64},
            }
        },
    }

    summary = summarize_external_metadata(metadata)

    assert summary["circle_prime_defaults"]["sha256"] == "d" * 64
    assert summary["tools"]["circle_prime"]["binary"]["sha256"] == "b" * 64
    assert summary["tools"]["circle_prime"]["defaults"]["sha256"] == "d" * 64


def test_external_control_provenance_rollup_renders_key_tool_versions() -> None:
    summary = summarize_external_control_provenance(
        [
            (
                "competitive_smoke",
                {
                    "started_at_utc": "2026-01-01T00:00:00Z",
                    "finished_at_utc": "2026-01-01T00:00:05Z",
                    "rounds": 5,
                    "tools": {
                        "primesieve": {
                            "available": True,
                            "path": "/opt/homebrew/bin/primesieve",
                            "version": "primesieve 12.14\nextra detail",
                        },
                        "primecount_pi_server": {
                            "available": True,
                            "path": "target/prime-controls/primecount-pi-server",
                            "method": "primecount_pi(HIGH-1)-primecount_pi(LOW-1)",
                            "binary": {
                                "path": "target/prime-controls/primecount-pi-server",
                                "sha256": "a" * 64,
                            },
                            "source_fingerprint": {
                                "path": "sidecars/PRIME_ENGINE/controls/primecount_pi_server.c",
                                "sha256": "b" * 64,
                            },
                        },
                        "primesieve_count_server": {
                            "available": False,
                            "error": "failed to build helper",
                        },
                    },
                },
            )
        ]
    )

    assert summary["available"] is True
    assert [row["tool"] for row in summary["rows"]] == [
        "primesieve",
        "primesieve_count_server",
        "primecount_pi_server",
    ]
    markdown = "\n".join(render_external_control_provenance_markdown(summary))
    assert "External Control Provenance" in markdown
    assert "`primesieve 12.14`" in markdown
    assert "`failed to build helper`" in markdown
    assert "`bin aaaaaaaaaaaa, src bbbbbbbbbbbb`" in markdown


def test_count_binary_segment_sweep_filters_full_cli_rows() -> None:
    rows = [
        {
            "kind": "timing",
            "name": "circle_prime_parallel_default_count_8t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1310720",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.000",
            "median_ms": "5.500",
            "rate_per_second": "2000000000",
            "median_rate_per_second": "1818181818",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "",
            "best_speedup": "",
            "median_speedup": "",
            "count_mode": "presieve13",
        },
        {
            "kind": "timing",
            "name": "circle_prime_count_binary_parallel_default_count_8t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1310720",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.100",
            "median_ms": "5.600",
            "rate_per_second": "1960784313",
            "median_rate_per_second": "1785714285",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "",
            "best_speedup": "",
            "median_speedup": "",
            "count_mode": "presieve13",
        },
        {
            "kind": "timing",
            "name": "circle_prime_count_binary_parallel_presieve13_count_6t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1835008",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.200",
            "median_ms": "5.000",
            "rate_per_second": "1923076923",
            "median_rate_per_second": "2000000000",
            "threads": "6",
            "requested_threads": "6",
            "baseline": "",
            "best_speedup": "",
            "median_speedup": "",
            "count_mode": "presieve13",
        },
        {
            "kind": "timing",
            "name": "external_primesieve_count",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "0",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.000",
            "median_ms": "5.100",
            "rate_per_second": "2000000000",
            "median_rate_per_second": "1960784313",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "",
            "best_speedup": "",
            "median_speedup": "",
            "count_mode": "",
        },
        {
            "kind": "speedup",
            "name": "circle_prime_parallel_default_count_8t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1310720",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.000",
            "median_ms": "5.500",
            "rate_per_second": "2000000000",
            "median_rate_per_second": "1818181818",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "external_primesieve_count",
            "best_speedup": "1.000",
            "median_speedup": "0.927",
            "count_mode": "presieve13",
        },
        {
            "kind": "speedup",
            "name": "circle_prime_count_binary_parallel_default_count_8t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1310720",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.100",
            "median_ms": "5.600",
            "rate_per_second": "1960784313",
            "median_rate_per_second": "1785714285",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "external_primesieve_count",
            "best_speedup": "0.980",
            "median_speedup": "0.911",
            "count_mode": "presieve13",
        },
        {
            "kind": "speedup",
            "name": "circle_prime_count_binary_parallel_presieve13_count_6t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1835008",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.200",
            "median_ms": "5.000",
            "rate_per_second": "1923076923",
            "median_rate_per_second": "2000000000",
            "threads": "6",
            "requested_threads": "6",
            "baseline": "external_primesieve_count",
            "best_speedup": "0.962",
            "median_speedup": "1.020",
            "count_mode": "presieve13",
        },
    ]
    samples = [
        *count_sample_rows(
            "circle_prime_count_binary_parallel_default_count_8t",
            segment_size=1310720,
            threads=8,
            requested_threads=8,
            values=[5.4, 5.5, 5.6, 5.7, 5.8],
        ),
        *count_sample_rows(
            "circle_prime_count_binary_parallel_presieve13_count_6t",
            segment_size=1835008,
            threads=6,
            requested_threads=6,
            values=[4.9, 5.0, 5.0, 5.1, 5.2],
        ),
        *count_sample_rows(
            "external_primesieve_count",
            segment_size=0,
            threads=8,
            requested_threads=8,
            values=[5.0, 5.0, 5.1, 5.2, 5.2],
        ),
    ]

    summary = summarize_high_offset_count_binary_segment_sweep(rows, None, samples)

    assert [row["name"] for row in summary["speedups"]] == [
        "circle_prime_count_binary_parallel_default_count_8t",
        "circle_prime_count_binary_parallel_presieve13_count_6t",
    ]
    assert summary["speedups"][0]["median_circle_speedup"] == 0.911
    assert summary["cold_candidate_readout"][0]["action"] == (
        "hold_best_speedup_below_floor"
    )
    assert summary["cold_candidate_readout"][0]["best"]["circle_threads"] == 6
    markdown = "\n".join(
        render_external_segment_sweep_markdown(
            summary,
            title="High-Offset Count-Binary Mode/Segment Sweep",
            include_circle_row=True,
        )
    )
    assert "Cold one-shot count-binary candidate readout" in markdown
    assert "hold_best_speedup_below_floor" in markdown
    assert "1.12x" in markdown


def test_count_binary_sweep_readout_marks_confirmation_hold() -> None:
    sweep_rows = [
        {
            "kind": "timing",
            "name": "circle_prime_count_binary_parallel_default_count_8t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1310720",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.100",
            "median_ms": "5.600",
            "rate_per_second": "1960784313",
            "median_rate_per_second": "1785714285",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "",
            "best_speedup": "",
            "median_speedup": "",
            "count_mode": "presieve13",
        },
        {
            "kind": "timing",
            "name": "circle_prime_count_binary_parallel_presieve13_count_7t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1507328",
            "result": "361726",
            "rounds": "9",
            "best_ms": "4.900",
            "median_ms": "5.000",
            "rate_per_second": "2040816326",
            "median_rate_per_second": "2000000000",
            "threads": "7",
            "requested_threads": "8",
            "baseline": "",
            "best_speedup": "",
            "median_speedup": "",
            "count_mode": "presieve13",
        },
        {
            "kind": "timing",
            "name": "external_primesieve_count",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "0",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.000",
            "median_ms": "5.100",
            "rate_per_second": "2000000000",
            "median_rate_per_second": "1960784313",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "",
            "best_speedup": "",
            "median_speedup": "",
            "count_mode": "",
        },
        {
            "kind": "speedup",
            "name": "circle_prime_count_binary_parallel_default_count_8t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1310720",
            "result": "361726",
            "rounds": "9",
            "best_ms": "5.100",
            "median_ms": "5.600",
            "rate_per_second": "1960784313",
            "median_rate_per_second": "1785714285",
            "threads": "8",
            "requested_threads": "8",
            "baseline": "external_primesieve_count",
            "best_speedup": "0.980",
            "median_speedup": "0.967",
            "count_mode": "presieve13",
        },
        {
            "kind": "speedup",
            "name": "circle_prime_count_binary_parallel_presieve13_count_7t",
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": "1507328",
            "result": "361726",
            "rounds": "9",
            "best_ms": "4.900",
            "median_ms": "5.000",
            "rate_per_second": "2040816326",
            "median_rate_per_second": "2000000000",
            "threads": "7",
            "requested_threads": "8",
            "baseline": "external_primesieve_count",
            "best_speedup": "1.015",
            "median_speedup": "1.049",
            "count_mode": "presieve13",
        },
    ]
    sweep_samples = [
        *count_sample_rows(
            "circle_prime_count_binary_parallel_default_count_8t",
            segment_size=1310720,
            threads=8,
            requested_threads=8,
            values=[5.4, 5.5, 5.6, 5.7, 5.8],
        ),
        *count_sample_rows(
            "circle_prime_count_binary_parallel_presieve13_count_7t",
            segment_size=1507328,
            threads=7,
            requested_threads=8,
            values=[4.9, 5.0, 5.0, 5.1, 5.2],
        ),
        *count_sample_rows(
            "external_primesieve_count",
            segment_size=0,
            threads=8,
            requested_threads=8,
            values=[5.0, 5.0, 5.1, 5.2, 5.2],
        ),
    ]
    confirm_rows = [
        {
            **row,
            "rounds": "17",
            "best_speedup": "0.976" if row["name"].endswith("default_count_8t") else "0.975",
            "median_speedup": "1.004" if row["name"].endswith("default_count_8t") else "1.017",
        }
        for row in sweep_rows
        if row["kind"] == "speedup"
    ]

    sweep = summarize_high_offset_count_binary_segment_sweep(
        sweep_rows,
        None,
        sweep_samples,
    )
    confirm = summarize_high_offset_count_binary_segment_sweep(
        confirm_rows,
        None,
        [],
        readout_require_stable_samples=False,
    )

    annotated = apply_count_binary_cold_confirmation_readout(sweep, confirm)

    readout = annotated["cold_candidate_readout"][0]
    assert readout["action"] == "trial_cold_count_binary_candidate"
    assert readout["confirmation_action"] == "hold_small_gain_candidate"
    assert readout["final_action"] == "held_by_focused_confirmation"
    markdown = "\n".join(
        render_external_segment_sweep_markdown(
            annotated,
            title="High-Offset Count-Binary Mode/Segment Sweep",
        )
    )
    assert "Final Action" in markdown
    assert "held_by_focused_confirmation" in markdown


def test_external_next_metadata_summary_preserves_provenance_hashes() -> None:
    metadata = {
        "circle_prime_defaults": {
            "available": True,
            "path": "rust/circle-prime/prime_engine_defaults.json",
            "sha256": "e" * 64,
        },
        "tools": {
            "circle_prime": {
                "available": True,
                "path": "target/release/circle-prime",
                "binary": {"available": True, "sha256": "c" * 64},
                "defaults": {"available": True, "sha256": "e" * 64},
            }
        },
        "starts": [90],
    }

    summary = summarize_external_next_metadata(metadata)

    assert summary["circle_prime_defaults"]["sha256"] == "e" * 64
    assert summary["tools"]["circle_prime"]["binary"]["sha256"] == "c" * 64
    assert summary["tools"]["circle_prime"]["defaults"]["sha256"] == "e" * 64


def count_sample_rows(
    name: str,
    *,
    segment_size: int,
    threads: int,
    requested_threads: int,
    values: list[float],
) -> list[dict[str, str]]:
    return [
        {
            "kind": "sample",
            "name": name,
            "low": "1000000000000",
            "high": "1000010000000",
            "span": "10000000",
            "segment_size": str(segment_size),
            "result": "361726",
            "sample_index": str(index),
            "elapsed_ms": f"{value:.3f}",
            "threads": str(threads),
            "requested_threads": str(requested_threads),
            "count_mode": "presieve13" if name.startswith("circle_") else "",
        }
        for index, value in enumerate(values)
    ]


def test_prime_engine_report_summarizes_artifacts(tmp_path: Path) -> None:
    benchmark = tmp_path / "benchmark.csv"
    benchmark.write_text(
        "\n".join(
            [
                "kind,name,workload,segment_size,result,rounds,best_ms,rate_per_second,baseline,best_speedup",
                "timing,base_prime_generation,1000000,0,78498,3,1.000,1000000000,,",
                "timing,next_prime_search,1000000000000,4096,1000000000039,3,0.050,81920000,,",
                "timing,enumerate_range_primes,1000000,262144,78498,3,1.500,666666666,,",
                "timing,segmented_range_count,10000000,262144,664579,3,2.000,5000000000,,",
                "timing,parallel_segmented_range_count_8t,10000000,131072,664579,3,0.600,16666666666,,",
                "timing,parallel_segmented_range_count_8t,10000000,196608,664579,3,0.650,15384615384,,",
                "timing,parallel_balanced_segmented_range_count_8t,10000000,131072,664579,3,0.700,14285714285,,",
                "timing,bitpacked_range_count,10000000,131072,664579,3,3.000,3333333333,,",
                "timing,cold_cli_parallel_default_range_count_8t,10000000,131072,664579,3,2.900,3448275862,,",
                "timing,cold_process_parallel_segmented_range_count_8t,10000000,131072,664579,3,3.100,3225806451,,",
                "timing,high_offset_segmented_range_count,10000000,4194304,361726,3,7.000,1428571428,,",
                "timing,parallel_high_offset_default_range_count_8t,10000000,3145728,361726,3,3.400,2941176470,,",
                "timing,parallel_high_offset_segmented_range_count_8t,10000000,3145728,361726,3,3.500,2857142857,,",
                "timing,parallel_high_offset_balanced_segmented_range_count_8t,10000000,3145728,361726,3,3.700,2702702702,,",
                "timing,cold_cli_parallel_high_offset_default_range_count_8t,10000000,3145728,361726,3,5.700,1754385965,,",
                "timing,cold_process_parallel_high_offset_segmented_range_count_8t,10000000,3145728,361726,3,6.000,1666666666,,",
                "timing,high_offset_bitpacked_range_count,10000000,3145728,361726,3,10.500,952380952,,",
            ]
        )
        + "\n"
    )
    external = tmp_path / "external.csv"
    external.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup",
                "timing,external_primesieve_count,0,10000000,10000000,0,664579,3,2.400,2.500,4166666666,4000000000,8,8,,,",
                "speedup,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,131072,664579,3,3.000,3.200,3333333333,3125000000,8,8,external_primesieve_count,0.800,0.781",
                "speedup,circle_prime_server_parallel_segmented_count_8t,0,10000000,10000000,131072,664579,3,1.200,1.250,8333333333,8000000000,8,8,external_primesieve_count,2.000,2.000",
                "timing,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,3,4.900,5.000,2040816326,2000000000,8,8,,,",
                "speedup,circle_prime_parallel_segmented_count_4t,1000000000000,1000010000000,10000000,3145728,361726,3,7.000,7.500,1428571428,1333333333,4,8,external_primesieve_count,0.700,0.667",
                "timing,external_primesieve_count_server,1000000000000,1000010000000,10000000,0,361726,3,4.200,4.600,2380952380,2173913043,8,8,,,",
                "speedup,circle_prime_parallel_segmented_count_4t,1000000000000,1000010000000,10000000,3145728,361726,3,7.000,7.500,1428571428,1333333333,4,8,external_primesieve_count_server,0.600,0.613",
                "timing,external_primecount_pi_diff,1000000000000,1000010000000,10000000,0,361726,3,17.500,18.000,571428571,555555555,0,0,,,",
                "speedup,circle_prime_parallel_segmented_count_4t,1000000000000,1000010000000,10000000,3145728,361726,3,7.000,7.500,1428571428,1333333333,4,8,external_primecount_pi_diff,2.500,2.400",
                "timing,external_primecount_pi_diff_server,1000000000000,1000010000000,10000000,0,361726,3,20.000,21.000,500000000,476190476,8,8,,,",
                "speedup,circle_prime_server_parallel_segmented_count_8t,1000000000000,1000010000000,10000000,131072,361726,3,2.000,2.100,5000000000,4761904761,8,8,external_primecount_pi_diff_server,10.000,10.000",
            ]
        )
        + "\n"
    )
    external_metadata = tmp_path / "external.json"
    external_metadata.write_text(
        json.dumps(
            {
                "started_at_utc": "2026-01-01T00:00:00Z",
                "finished_at_utc": "2026-01-01T00:01:00Z",
                "row_count": 6,
                "rounds": 3,
                "batch_size": 3,
                "warmup_rounds": 1,
                "required_external_tools": [
                    "primesieve",
                    "primecount",
                    "primesieve-library",
                    "primecount-library",
                ],
                "circle_count_modes": ["segmented"],
                "include_primesieve_count_server": True,
                "include_primecount_pi_server": True,
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                    "external_default_threads_when_zero": "tool default/all available CPU cores",
                },
                "ranges": [{"low": 0, "high": 10000000, "span": 10000000}],
                "tools": {
                    "circle_prime": {
                        "available": True,
                        "path": "/tmp/circle-prime",
                        "version": "0.1.0",
                    },
                    "circle_count_server": {
                        "available": True,
                        "path": "/tmp/circle-prime",
                        "method": "persistent count-server requests",
                        "small_prefix_pi_cache_limit": 2_000_000_000,
                        "small_prefix_pi_cache_default_limit": 2_000_000_000,
                        "small_prefix_pi_cache_max_limit": 3_000_000_000,
                        "small_prefix_pi_cache_limit_env": (
                            "CIRCLE_PRIME_SMALL_PREFIX_PI_CACHE_LIMIT"
                        ),
                        "small_prefix_pi_cache_estimated_bytes": 187_500_004,
                        "small_prefix_pi_cache_default_estimated_bytes": 187_500_004,
                        "small_prefix_pi_cache_max_estimated_bytes": 281_250_004,
                        "small_prefix_pi_cache_scope": (
                            "prefix-pi count-server ranges with HIGH-1 at or below the limit"
                        ),
                        "small_prefix_pi_cache_warmup": (
                            "eligible prefix-pi count-server rows pass --warm-prefix-pi-cache "
                            "before reading timed requests"
                        ),
                        "small_prefix_pi_cache_warmup_profiles": [
                            {
                                "name": "circle_prime_server_default_count",
                                "low": 0,
                                "high": 10000000,
                                "cache_limit": 2000000000,
                                "startup_warmup_ms": 4000.0,
                            },
                            {
                                "name": "circle_prime_server_default_count",
                                "low": 0,
                                "high": 100000000,
                                "cache_limit": 2000000000,
                                "startup_warmup_ms": 4200.0,
                            },
                        ],
                    },
                    "primesieve": {
                        "available": True,
                        "path": "/usr/local/bin/primesieve",
                        "version": "primesieve 12.14\nBSD 2-Clause License",
                    },
                    "primecount": {
                        "available": True,
                        "path": "/usr/local/bin/primecount",
                        "version": "primecount 8.5\nBSD 2-Clause License",
                    },
                    "primesieve_count_server": {
                        "available": True,
                        "path": "/tmp/primesieve-count-server",
                        "source": "/tmp/primesieve_count_server.c",
                        "method": "primesieve_count_primes(LOW, HIGH-1)",
                        "error": None,
                    },
                    "primecount_pi_server": {
                        "available": True,
                        "path": "/tmp/primecount-pi-server",
                        "source": "/tmp/primecount_pi_server.c",
                        "method": "primecount_pi(HIGH-1)-primecount_pi(LOW-1)",
                        "error": None,
                    },
                },
            }
        )
        + "\n"
    )
    external_correctness = tmp_path / "external-correctness.json"
    external_correctness.write_text(
        json.dumps(
            {
                "started_at_utc": "2026-01-01T00:00:00Z",
                "finished_at_utc": "2026-01-01T00:02:00Z",
                "passes": True,
                "count_check_count": 2,
                "count_server_check_count": 1,
                "enumeration_check_count": 2,
                "next_check_count": 1,
                "check_count": 6,
                "count_failure_count": 0,
                "count_server_failure_count": 0,
                "enumeration_failure_count": 0,
                "next_failure_count": 0,
                "failure_count": 0,
                "required_external_tools": ["primesieve", "primecount"],
                "missing_external_tools": [],
                "requested_segment_sizes": [0],
                "circle_count_modes": ["segmented", "hybrid-wheel30-mark"],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [{"low": 0, "high": 1000000, "span": 1000000}],
                "enumeration_ranges": [
                    {"low": 0, "high": 1000, "span": 1000},
                    {
                        "low": 18446744073709551515,
                        "high": 18446744073709551615,
                        "span": 100,
                    },
                ],
                "next_starts": [100],
                "tools": {
                    "circle_prime": {
                        "available": True,
                        "path": "/tmp/circle-prime",
                        "version": "0.1.0",
                    },
                    "primesieve": {
                        "available": True,
                        "path": "/usr/local/bin/primesieve",
                        "version": "primesieve 12.14",
                    },
                    "primecount": {
                        "available": True,
                        "path": "/usr/local/bin/primecount",
                        "version": "primecount 8.5",
                    },
                },
                "checks": [
                    {
                        "low": 0,
                        "high": 1000000,
                        "span": 1000000,
                        "count_mode": "segmented",
                        "segment_size": 65536,
                        "threads": 8,
                        "requested_threads": 8,
                        "circle_count": 78498,
                        "external_counts": {
                            "primesieve": 78498,
                            "primecount": 78498,
                        },
                        "matches": {
                            "primesieve": True,
                            "primecount": True,
                        },
                        "passes": True,
                    },
                    {
                        "low": 0,
                        "high": 1000000,
                        "span": 1000000,
                        "count_mode": "hybrid-wheel30-mark",
                        "segment_size": 65536,
                        "threads": 8,
                        "requested_threads": 8,
                        "circle_count": 78498,
                        "external_counts": {
                            "primesieve": 78498,
                            "primecount": 78498,
                        },
                        "matches": {
                            "primesieve": True,
                            "primecount": True,
                        },
                        "passes": True,
                    },
                ],
                "enumeration_checks": [
                    {
                        "low": 0,
                        "high": 1000,
                        "span": 1000,
                        "segment_size": 65536,
                        "threads": 1,
                        "requested_threads": 1,
                        "circle_count": 168,
                        "external_count": 168,
                        "first_mismatch": None,
                        "passes": True,
                    },
                    {
                        "low": 18446744073709551515,
                        "high": 18446744073709551615,
                        "span": 100,
                        "segment_size": 65536,
                        "threads": 1,
                        "requested_threads": 1,
                        "circle_count": 3,
                        "external_count": 3,
                        "first_mismatch": None,
                        "passes": True,
                    },
                ],
                "next_checks": [
                    {
                        "start": 100,
                        "search_window": 1000,
                        "circle_prime": 101,
                        "external_prime": 101,
                        "candidate_count": 1,
                        "passes": True,
                    }
                ],
            }
        )
        + "\n"
    )
    external_next = tmp_path / "external-next.csv"
    external_next.write_text(
        "\n".join(
            [
                "kind,name,start,batch_size,result,candidate_count,rounds,best_ms,median_ms,searches_per_second,median_searches_per_second,threads,requested_threads,baseline,best_speedup,median_speedup,sample_count,sample_noise_ms,sample_max_ms,sample_noise_over_median,sample_max_over_median,sample_ignored_single_high_outlier,sample_stability",
                "timing,circle_prime_next_prime,100,1,101,1,3,1.000,1.200,1000,833.333,1,1,,,",
                "timing,circle_prime_server_next_prime,100,1,101,1,3,0.250,0.300,4000,3333.333,1,1,,,",
                "timing,external_primesieve_generate_next_server,100,1,101,0,3,0.500,0.600,2000,1666.667,1,1,,,",
                "timing,external_primesieve_next_prime,100,1,101,0,3,2.000,2.400,500,416.667,8,8,,,",
                "timing,external_primecount_next_prime,100,1,101,0,3,4.000,4.800,250,208.333,8,8,,,",
                "timing,external_primecount_next_server,100,1,101,0,3,3.000,3.600,333.333,277.778,8,8,,,",
                "speedup,circle_prime_next_prime,100,1,101,1,3,1.000,1.200,1000,833.333,1,1,external_primesieve_generate_next_server,0.500,0.500,3,1.300000,1.500000,1.083333,1.250000,false,stable",
                "speedup,circle_prime_server_next_prime,100,1,101,1,3,0.250,0.300,4000,3333.333,1,1,external_primesieve_generate_next_server,2.000,2.000",
                "speedup,circle_prime_next_prime,100,1,101,1,3,1.000,1.200,1000,833.333,1,1,external_primesieve_next_prime,2.000,2.000",
                "speedup,circle_prime_server_next_prime,100,1,101,1,3,0.250,0.300,4000,3333.333,1,1,external_primesieve_next_prime,8.000,8.000",
                "speedup,circle_prime_next_prime,100,1,101,1,3,1.000,1.200,1000,833.333,1,1,external_primecount_next_prime,4.000,4.000",
                "speedup,circle_prime_server_next_prime,100,1,101,1,3,0.250,0.300,4000,3333.333,1,1,external_primecount_next_prime,16.000,16.000",
                "speedup,circle_prime_next_prime,100,1,101,1,3,1.000,1.200,1000,833.333,1,1,external_primecount_next_server,3.000,3.000",
                "speedup,circle_prime_server_next_prime,100,1,101,1,3,0.250,0.300,4000,3333.333,1,1,external_primecount_next_server,12.000,12.000",
            ]
        )
        + "\n"
    )
    external_next_metadata = tmp_path / "external-next.json"
    external_next_metadata.write_text(
        json.dumps(
            {
                "started_at_utc": "2026-01-01T00:00:00Z",
                "finished_at_utc": "2026-01-01T00:01:00Z",
                "row_count": 3,
                "rounds": 3,
                "batch_size": 1,
                "include_circle_server": True,
                "include_primecount": True,
                "primecount_max_start": 1000000000000,
                "include_primecount_library_server": True,
                "primecount_library_max_start": 1000000000000,
                "include_primesieve_library_server": True,
                "primesieve_library_max_start": 18446744073709551615,
                "starts": [100],
                "required_external_tools": [
                    "primesieve",
                    "primecount",
                    "primesieve-library",
                    "primecount-library",
                ],
                "sample_output": None,
                "thread_policy": {
                    "circle_requested_threads": 1,
                    "external_requested_threads": 8,
                },
                "tools": {
                    "circle_prime": {
                        "available": True,
                        "path": "/tmp/circle-prime",
                        "version": "0.1.0",
                    },
                        "primesieve": {
                            "available": True,
                            "path": "/usr/local/bin/primesieve",
                            "version": "primesieve 12.14",
                        },
                        "primecount": {
                            "available": True,
                            "path": "/usr/local/bin/primecount",
                            "version": "primecount 8.5",
                        },
                        "primesieve_library_server": {
                            "available": True,
                            "path": "/tmp/primesieve-next-server",
                            "source": "/tmp/primesieve_next_server.c",
                            "method": "primesieve_generate_n_primes(1, START, UINT64_PRIMES)",
                        },
                        "primecount_library_server": {
                            "available": True,
                            "path": "/tmp/primecount-next-server",
                            "source": "/tmp/primecount_next_server.c",
                            "method": "primecount_pi(START-1) then primecount_nth_prime(pi+1)",
                        },
                    },
                }
            )
        + "\n"
    )
    external_mode_sweep = tmp_path / "external-mode-sweep.csv"
    external_mode_sweep.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup",
                "timing,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,65536,664579,5,3.300,3.500,3030303030,2857142857,8,8,,,",
                "timing,circle_prime_parallel_hybrid_wheel30_mark_count_8t,0,10000000,10000000,65536,664579,5,3.000,3.100,3333333333,3225806451,8,8,,,",
                "timing,external_primesieve_count,0,10000000,10000000,0,664579,5,2.400,2.500,4166666666,4000000000,8,8,,,",
                "speedup,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,65536,664579,5,3.300,3.500,3030303030,2857142857,8,8,external_primesieve_count,0.727,0.714",
                "speedup,circle_prime_parallel_hybrid_wheel30_mark_count_8t,0,10000000,10000000,65536,664579,5,3.000,3.100,3333333333,3225806451,8,8,external_primesieve_count,0.800,0.806",
            ]
        )
        + "\n"
    )
    external_mode_sweep_metadata = tmp_path / "external-mode-sweep.json"
    external_mode_sweep_metadata.write_text(
        json.dumps(
            {
                "row_count": 5,
                "rounds": 5,
                "required_external_tools": ["primesieve", "primecount"],
                "circle_count_modes": ["segmented", "hybrid-wheel30-mark"],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [{"low": 0, "high": 10000000, "span": 10000000}],
                "tools": {},
            }
        )
        + "\n"
    )
    external_sweep = tmp_path / "external-sweep.csv"
    external_sweep.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup",
                "timing,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,32768,664579,5,3.100,3.100,3225806451,3225806451,8,8,,,",
                "timing,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,131072,664579,5,3.000,3.400,3333333333,2941176470,8,8,,,",
                "timing,external_primesieve_count,0,10000000,10000000,0,664579,5,2.400,2.500,4166666666,4000000000,8,8,,,",
                "speedup,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,32768,664579,5,3.100,3.100,3225806451,3225806451,8,8,external_primesieve_count,0.774,0.806",
                "speedup,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,131072,664579,5,3.000,3.400,3333333333,2941176470,8,8,external_primesieve_count,0.800,0.735",
                "timing,external_primecount_pi_diff,0,10000000,10000000,0,664579,5,3.500,3.600,2857142857,2777777777,8,8,,,",
                "speedup,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,32768,664579,5,3.100,3.100,3225806451,3225806451,8,8,external_primecount_pi_diff,1.129,1.161",
                "speedup,circle_prime_parallel_segmented_count_8t,0,10000000,10000000,131072,664579,5,3.000,3.400,3333333333,2941176470,8,8,external_primecount_pi_diff,1.167,1.059",
            ]
        )
        + "\n"
    )
    external_sweep_metadata = tmp_path / "external-sweep.json"
    external_sweep_metadata.write_text(
        json.dumps(
            {
                "row_count": 8,
                "rounds": 5,
                "required_external_tools": ["primesieve", "primecount"],
                "requested_segment_sizes": [0, 32768, 131072],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [{"low": 0, "high": 10000000, "span": 10000000}],
                "tools": {},
            }
        )
        + "\n"
    )
    external_throughput = tmp_path / "external-throughput.csv"
    external_throughput.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup",
                "timing,circle_prime_default_count,0,1000000000,1000000000,262144,50847534,5,45.000,46.000,22222222222,21739130434,1,8,,,",
                "timing,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,131072,50847534,5,40.000,42.000,25000000000,23809523809,8,8,,,",
                "timing,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,196608,50847534,5,39.000,41.000,25641025641,24390243902,8,8,,,",
                "timing,external_primesieve_count,0,1000000000,1000000000,0,50847534,5,18.000,19.000,55555555555,52631578947,8,8,,,",
                "timing,circle_prime_prefix_pi_count,1000000000,2000000000,1000000000,262144,47374753,5,14.000,15.000,71428571428,66666666666,1,1,,,",
                "timing,circle_prime_parallel_default_count_2t,1000000000,2000000000,1000000000,262144,47374753,5,10.000,12.000,100000000000,83333333333,2,8,,,",
                "timing,external_primesieve_count,1000000000,2000000000,1000000000,0,47374753,5,20.000,24.000,50000000000,41666666666,8,8,,,",
                "speedup,circle_prime_default_count,0,1000000000,1000000000,262144,50847534,5,45.000,46.000,22222222222,21739130434,1,8,external_primesieve_count,0.400,0.413",
                "speedup,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,131072,50847534,5,40.000,42.000,25000000000,23809523809,8,8,external_primesieve_count,0.450,0.452",
                "speedup,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,196608,50847534,5,39.000,41.000,25641025641,24390243902,8,8,external_primesieve_count,0.462,0.463",
                "speedup,circle_prime_prefix_pi_count,1000000000,2000000000,1000000000,262144,47374753,5,14.000,15.000,71428571428,66666666666,1,1,external_primesieve_count,1.429,1.600",
                "speedup,circle_prime_parallel_default_count_2t,1000000000,2000000000,1000000000,262144,47374753,5,10.000,12.000,100000000000,83333333333,2,8,external_primesieve_count,2.000,2.000",
            ]
        )
        + "\n"
    )
    external_throughput_metadata = tmp_path / "external-throughput.json"
    external_throughput_metadata.write_text(
        json.dumps(
            {
                "row_count": 12,
                "rounds": 5,
                "required_external_tools": ["primesieve", "primecount"],
                "requested_segment_sizes": [131072, 196608, 262144],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [
                    {"low": 0, "high": 1000000000, "span": 1000000000},
                    {"low": 1000000000, "high": 2000000000, "span": 1000000000},
                ],
                "tools": {},
            }
        )
        + "\n"
    )
    external_high_offset_quick = tmp_path / "high-offset-quick.csv"
    external_high_offset_quick.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup,count_mode",
                "timing,circle_prime_parallel_presieve13_count_8t,1000000000000,1000010000000,10000000,1310720,361726,13,5.100,5.700,1960784313,1754385964,8,8,,,,presieve13",
                "timing,circle_prime_parallel_presieve13_count_7t,1000000000000,1000010000000,10000000,1507328,361726,13,5.300,6.100,1886792452,1639344262,7,8,,,,presieve13",
                "timing,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,13,4.800,5.200,2083333333,1923076923,8,8,,,,",
                "speedup,circle_prime_parallel_presieve13_count_8t,1000000000000,1000010000000,10000000,1310720,361726,13,5.100,5.700,1960784313,1754385964,8,8,external_primesieve_count,0.941,0.912,presieve13",
                "speedup,circle_prime_parallel_presieve13_count_7t,1000000000000,1000010000000,10000000,1507328,361726,13,5.300,6.100,1886792452,1639344262,7,8,external_primesieve_count,0.906,0.852,presieve13",
            ]
        )
        + "\n"
    )
    external_high_offset_quick_metadata = tmp_path / "high-offset-quick.json"
    external_high_offset_quick_metadata.write_text(
        json.dumps(
            {
                "row_count": 5,
                "rounds": 13,
                "required_external_tools": ["primesieve", "primecount"],
                "requested_segment_sizes": [1310720, 1507328],
                "circle_count_modes": ["presieve13"],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "span": 10000000,
                    }
                ],
                "tools": {},
            }
        )
        + "\n"
    )
    external_high_offset_tight = tmp_path / "high-offset-tight.csv"
    external_high_offset_tight.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup,count_mode",
                "timing,circle_prime_parallel_presieve17_count_8t,1000000000000,1000010000000,10000000,1376256,361726,17,4.900,5.400,2040816326,1851851852,8,8,,,,presieve17",
                "timing,circle_prime_parallel_presieve13_count_7t,1000000000000,1000010000000,10000000,1507328,361726,17,4.850,5.600,2061855670,1785714285,7,8,,,,presieve13",
                "timing,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,17,4.500,4.800,2222222222,2083333333,8,8,,,,",
                "speedup,circle_prime_parallel_presieve17_count_8t,1000000000000,1000010000000,10000000,1376256,361726,17,4.900,5.400,2040816326,1851851852,8,8,external_primesieve_count,0.918,0.889,presieve17",
                "speedup,circle_prime_parallel_presieve13_count_7t,1000000000000,1000010000000,10000000,1507328,361726,17,4.850,5.600,2061855670,1785714285,7,8,external_primesieve_count,0.928,0.857,presieve13",
            ]
        )
        + "\n"
    )
    external_high_offset_tight_metadata = tmp_path / "high-offset-tight.json"
    external_high_offset_tight_metadata.write_text(
        json.dumps(
            {
                "row_count": 5,
                "rounds": 17,
                "required_external_tools": ["primesieve", "primecount"],
                "requested_segment_sizes": [1376256, 1507328],
                "circle_count_modes": ["presieve13", "presieve17"],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "span": 10000000,
                    }
                ],
                "tools": {},
            }
        )
        + "\n"
    )
    external_high_offset_hot_server = tmp_path / "high-offset-hot-server.csv"
    external_high_offset_hot_server.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup,count_mode",
                "timing,circle_prime_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,7,1.700,1.900,5882352941,5263157894,8,8,,,,presieve13",
                "timing,circle_prime_server_parallel_presieve17_count_8t,1000000000000,1000010000000,10000000,1310720,361726,7,1.600,1.800,6250000000,5555555555,8,8,,,,presieve17",
                "timing,external_primesieve_count_server,1000000000000,1000010000000,10000000,0,361726,7,2.000,2.100,5000000000,4761904761,8,8,,,,",
                "speedup,circle_prime_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,7,1.700,1.900,5882352941,5263157894,8,8,external_primesieve_count_server,1.176,1.105,presieve13",
                "speedup,circle_prime_server_parallel_presieve17_count_8t,1000000000000,1000010000000,10000000,1310720,361726,7,1.600,1.800,6250000000,5555555555,8,8,external_primesieve_count_server,1.250,1.167,presieve17",
            ]
        )
        + "\n"
    )
    external_high_offset_hot_server_metadata = tmp_path / "high-offset-hot-server.json"
    external_high_offset_hot_server_metadata.write_text(
        json.dumps(
            {
                "row_count": 5,
                "rounds": 7,
                "batch_size": 20,
                "batch_request_profile": "identical",
                "batch_shift": 0,
                "warmup_rounds": 2,
                "include_circle_server": True,
                "include_primesieve_count_server": True,
                "required_external_tools": ["primesieve-library"],
                "requested_segment_sizes": [0, 1310720],
                "circle_count_modes": ["default", "presieve17"],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "span": 10000000,
                    }
                ],
                "tools": {},
            }
        )
        + "\n"
    )
    external_high_offset_count_binary = tmp_path / "high-offset-count-binary.csv"
    external_high_offset_count_binary.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup,count_mode",
                "timing,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,5.100,5.600,1960784313,1785714285,8,8,,,,presieve13",
                "timing,circle_prime_count_binary_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.900,2.000,5263157894,5000000000,8,8,,,,presieve13",
                "timing,circle_prime_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.700,1.800,5882352941,5555555555,8,8,,,,presieve13",
                "timing,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,11,5.000,5.100,2000000000,1960784313,8,8,,,,",
                "timing,external_primecount_pi_diff,1000000000000,1000010000000,10000000,0,361726,11,29.000,31.000,344827586,322580645,8,8,,,,",
                "timing,external_primesieve_count_server,1000000000000,1000010000000,10000000,0,361726,11,2.100,2.250,4761904761,4444444444,8,8,,,,",
                "timing,external_primecount_pi_diff_server,1000000000000,1000010000000,10000000,0,361726,11,9.000,9.900,1111111111,1010101010,8,8,,,,",
                "speedup,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,5.100,5.600,1960784313,1785714285,8,8,external_primesieve_count,0.980,0.911,presieve13",
                "speedup,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,5.100,5.600,1960784313,1785714285,8,8,external_primecount_pi_diff,5.686,5.536,presieve13",
                "speedup,circle_prime_count_binary_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.900,2.000,5263157894,5000000000,8,8,external_primesieve_count,2.632,2.550,presieve13",
                "speedup,circle_prime_count_binary_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.900,2.000,5263157894,5000000000,8,8,external_primecount_pi_diff,15.263,15.500,presieve13",
                "speedup,circle_prime_count_binary_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.900,2.000,5263157894,5000000000,8,8,external_primesieve_count_server,1.105,1.125,presieve13",
                "speedup,circle_prime_count_binary_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.900,2.000,5263157894,5000000000,8,8,external_primecount_pi_diff_server,4.737,4.950,presieve13",
                "speedup,circle_prime_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.700,1.800,5882352941,5555555555,8,8,external_primesieve_count_server,1.235,1.250,presieve13",
                "speedup,circle_prime_server_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,11,1.700,1.800,5882352941,5555555555,8,8,external_primecount_pi_diff_server,5.294,5.500,presieve13",
            ]
        )
        + "\n"
    )
    external_high_offset_count_binary_metadata = (
        tmp_path / "high-offset-count-binary.json"
    )
    external_high_offset_count_binary_metadata.write_text(
        json.dumps(
            {
                "row_count": 15,
                "rounds": 11,
                "batch_size": 20,
                "batch_request_profile": "identical",
                "batch_shift": 0,
                "warmup_rounds": 2,
                "include_circle_count_binary": True,
                "include_circle_server": True,
                "include_primesieve_count_server": True,
                "include_primecount_pi_server": True,
                "required_external_tools": [
                    "primesieve",
                    "primecount",
                    "primesieve-library",
                    "primecount-library",
                ],
                "requested_segment_sizes": [1310720],
                "circle_count_modes": ["default"],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "span": 10000000,
                    }
                ],
                "tools": {
                    "circle_prime_count": {
                        "available": True,
                        "path": "/tmp/circle-prime-count",
                        "version": "0.1.0",
                        "binary": {
                            "sha256": "0123456789abcdef",
                            "size_bytes": 1372800,
                        },
                    }
                },
            }
        )
        + "\n"
    )
    external_high_offset_count_binary_candidate_confirm = (
        tmp_path / "high-offset-count-binary-candidate-confirm.csv"
    )
    external_high_offset_count_binary_candidate_confirm.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup,count_mode",
                "timing,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,17,5.100,5.600,1960784313,1785714285,8,8,,,,presieve13",
                "timing,circle_prime_count_binary_parallel_presieve13_count_6t,1000000000000,1000010000000,10000000,1835008,361726,17,5.200,5.000,1923076923,2000000000,6,6,,,,presieve13",
                "timing,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,17,5.000,5.100,2000000000,1960784313,8,8,,,,",
                "speedup,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,17,5.100,5.600,1960784313,1785714285,8,8,external_primesieve_count,0.980,0.911,presieve13",
                "speedup,circle_prime_count_binary_parallel_presieve13_count_6t,1000000000000,1000010000000,10000000,1835008,361726,17,5.200,5.000,1923076923,2000000000,6,6,external_primesieve_count,0.962,1.020,presieve13",
            ]
        )
        + "\n"
    )
    external_high_offset_count_binary_candidate_confirm_samples = (
        tmp_path / "high-offset-count-binary-candidate-confirm-samples.csv"
    )
    external_high_offset_count_binary_candidate_confirm_samples.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,sample_index,elapsed_ms,threads,requested_threads,count_mode",
                "sample,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,0,5.400,8,8,presieve13",
                "sample,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,1,5.500,8,8,presieve13",
                "sample,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,2,5.600,8,8,presieve13",
                "sample,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,3,5.700,8,8,presieve13",
                "sample,circle_prime_count_binary_parallel_default_count_8t,1000000000000,1000010000000,10000000,1310720,361726,4,5.800,8,8,presieve13",
                "sample,circle_prime_count_binary_parallel_presieve13_count_6t,1000000000000,1000010000000,10000000,1835008,361726,0,4.900,6,6,presieve13",
                "sample,circle_prime_count_binary_parallel_presieve13_count_6t,1000000000000,1000010000000,10000000,1835008,361726,1,5.000,6,6,presieve13",
                "sample,circle_prime_count_binary_parallel_presieve13_count_6t,1000000000000,1000010000000,10000000,1835008,361726,2,5.000,6,6,presieve13",
                "sample,circle_prime_count_binary_parallel_presieve13_count_6t,1000000000000,1000010000000,10000000,1835008,361726,3,5.100,6,6,presieve13",
                "sample,circle_prime_count_binary_parallel_presieve13_count_6t,1000000000000,1000010000000,10000000,1835008,361726,4,5.200,6,6,presieve13",
                "sample,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,0,5.000,8,8,",
                "sample,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,1,5.000,8,8,",
                "sample,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,2,5.100,8,8,",
                "sample,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,3,5.200,8,8,",
                "sample,external_primesieve_count,1000000000000,1000010000000,10000000,0,361726,4,5.200,8,8,",
            ]
        )
        + "\n"
    )
    external_high_offset_count_binary_candidate_confirm_metadata = (
        tmp_path / "high-offset-count-binary-candidate-confirm.json"
    )
    external_high_offset_count_binary_candidate_confirm_metadata.write_text(
        json.dumps(
            {
                "row_count": 5,
                "rounds": 17,
                "batch_size": 20,
                "batch_request_profile": "identical",
                "batch_shift": 0,
                "warmup_rounds": 2,
                "include_circle_count_binary": True,
                "include_circle_count_binary_server": False,
                "include_circle_server": False,
                "include_primesieve_count_server": False,
                "include_primecount_pi_server": False,
                "required_external_tools": ["primesieve"],
                "requested_segment_sizes": [0, 1835008],
                "circle_count_modes": ["default", "presieve13"],
                "sample_output": str(
                    external_high_offset_count_binary_candidate_confirm_samples
                ),
            }
        )
        + "\n"
    )
    external_competitive_smoke = tmp_path / "competitive-smoke.csv"
    external_competitive_smoke.write_text(
        "\n".join(
            [
                "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,rate_per_second,median_rate_per_second,threads,requested_threads,baseline,best_speedup,median_speedup,count_mode",
                "timing,circle_prime_count_binary_server_parallel_default_count_7t,1000000000000,1000010000000,10000000,1638400,361726,5,1.900,2.000,5263157894,5000000000,7,8,,,,presieve13",
                "timing,external_primesieve_count_server,1000000000000,1000010000000,10000000,0,361726,5,2.200,2.300,4545454545,4347826086,8,8,,,,",
                "timing,external_primecount_pi_diff_server,1000000000000,1000010000000,10000000,0,361726,5,8.900,9.100,1123595505,1098901098,8,8,,,,",
                "speedup,circle_prime_count_binary_server_parallel_default_count_7t,1000000000000,1000010000000,10000000,1638400,361726,5,1.900,2.000,5263157894,5000000000,7,8,external_primesieve_count_server,1.158,1.150,presieve13",
                "speedup,circle_prime_count_binary_server_parallel_default_count_7t,1000000000000,1000010000000,10000000,1638400,361726,5,1.900,2.000,5263157894,5000000000,7,8,external_primecount_pi_diff_server,4.684,4.550,presieve13",
            ]
        )
        + "\n"
    )
    external_competitive_smoke_metadata = tmp_path / "competitive-smoke.json"
    external_competitive_smoke_metadata.write_text(
        json.dumps(
            {
                "row_count": 5,
                "rounds": 5,
                "batch_size": 20,
                "batch_request_profile": "shifted",
                "batch_shift": 10000000,
                "warmup_rounds": 1,
                "include_circle_count_binary_server": True,
                "include_primesieve_count_server": True,
                "include_primecount_pi_server": True,
                "required_external_tools": [
                    "primesieve-library",
                    "primecount-library",
                ],
                "requested_segment_sizes": [0],
                "circle_count_modes": ["default"],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "span": 10000000,
                    }
                ],
                "tools": {},
            }
        )
        + "\n"
    )
    high_offset_hot_cold = tmp_path / "high-offset-hot-cold.csv"
    high_offset_hot_cold.write_text(
        "\n".join(
            [
                "kind,name,workload,segment_size,result,rounds,best_ms,rate_per_second,baseline,best_speedup",
                "timing,parallel_high_offset_default_range_count_8t,10000000,1376256,361726,7,2.200,4545454545,,",
                "timing,parallel_high_offset_presieve17_range_count_8t,10000000,1376256,361726,7,2.050,4878048780,,",
                "timing,hot_cli_count_server_parallel_high_offset_default_range_count_8t,10000000,1376256,361726,7,2.600,3846153846,,",
                "timing,hot_cli_count_server_parallel_high_offset_segmented_count_8t,10000000,1376256,361726,7,2.450,4081632653,,",
                "timing,hot_cli_count_server_parallel_high_offset_presieve13_count_8t,10000000,1376256,361726,7,2.500,4000000000,,",
                "timing,hot_cli_count_server_parallel_high_offset_presieve17_count_8t,10000000,1376256,361726,7,2.550,3921568627,,",
                "timing,cold_cli_parallel_high_offset_default_range_count_8t,10000000,1376256,361726,7,4.400,2272727273,,",
                "timing,cold_process_parallel_high_offset_segmented_range_count_8t,10000000,1376256,361726,7,4.100,2439024390,,",
            ]
        )
        + "\n"
    )
    tuning = tmp_path / "tuning.json"
    tuning.write_text(
        json.dumps(
            {
                "started_at_utc": "20260101T000000Z",
                "finished_at_utc": "20260101T010000Z",
                "elapsed_seconds": 3600.0,
                "rounds": 3,
                "sample_count": 12,
                "default_alignment": [
                    {
                        "low": 0,
                        "high": 10000000,
                        "span": 10000000,
                        "count": 664579,
                        "best_segment_size": 131072,
                        "best_threads": 8,
                        "best_requested_threads": 8,
                        "best_ms": 0.6,
                        "median_ms": 0.7,
                        "default_segment_size": 131072,
                        "default_threads": 8,
                        "default_requested_threads": 8,
                        "segment_size_aligned": True,
                        "threads_aligned": True,
                    },
                    {
                        "low": 0,
                        "high": 1000000,
                        "span": 1000000,
                        "count": 78498,
                        "best_segment_size": 16384,
                        "best_threads": 2,
                        "best_requested_threads": 2,
                        "best_ms": 0.2,
                        "median_ms": 0.25,
                        "default_segment_size": 262144,
                        "default_threads": 2,
                        "default_requested_threads": 2,
                        "segment_size_aligned": False,
                        "threads_aligned": True,
                    },
                ],
                "best_by_range": [
                    {
                        "low": 0,
                        "high": 10000000,
                        "span": 10000000,
                        "samples": 4,
                        "best": {
                            "segment_size": 131072,
                            "requested_threads": 8,
                            "threads": 8,
                            "best_ms": 0.6,
                            "median_ms": 0.7,
                            "rate_per_second": 16666666666.0,
                            "median_rate_per_second": 14285714285.0,
                            "count": 664579,
                        },
                    }
                ],
            }
        )
        + "\n"
    )
    calibration = tmp_path / "calibration.json"
    calibration.write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-01-01T00:00:00Z",
                "tolerance": 0.05,
                "recommendation_count": 1,
                "aligned_count": 0,
                "within_tolerance_count": 1,
                "drift_count": 0,
                "noisy_drift_count": 0,
                "missing_evidence_count": 0,
                "failing_recommendation_count": 0,
                "recommendations": [
                        {
                            "source": "external_segment_sweep",
                            "baseline": "external_primesieve_count",
                            "low": 0,
                            "high": 10000000,
                            "span": 10000000,
                            "selected_count_mode": "segmented",
                            "selected_segment_size": 32768,
                            "selected_threads": 8,
                            "selected_requested_threads": 8,
                            "selected_median_ms": 3.1,
                            "selected_sample_stability": "noisy",
                            "selected_effective_sample_stability": "stable",
                            "current_default_count_mode": "segmented",
                            "current_default_segment_size": 32768,
                            "current_default_threads": 8,
                            "current_default_requested_threads": 8,
                        "default_over_selected": 1.0,
                        "status": "within_tolerance",
                        "passes": True,
                    }
                ],
            }
        )
        + "\n"
    )
    mode_confirmation = tmp_path / "external-mode-confirmation.json"
    mode_confirmation.write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-01-01T00:03:00Z",
                "min_confirmations": 2,
                "require_stable_samples": True,
                "batch_size": 3,
                "observed_group_count": 1,
                "confirmed_count": 1,
                "unconfirmed_count": 0,
                "winners": [
                    {
                        "low": 0,
                        "high": 10000000,
                        "baseline": "external_primesieve_count",
                        "count_mode": "hybrid-wheel30-mark",
                        "segment_size": 65536,
                        "threads": 8,
                        "requested_threads": 8,
                        "confirmation_count": 2,
                        "observed_count": 3,
                        "stable_observed_count": 3,
                        "status": "confirmed",
                        "median_ms_values": [3.1, 3.2],
                        "median_speedup_values": [1.1, 1.2],
                    }
                ],
            }
        )
        + "\n"
    )
    high_offset_candidate_confirmation = (
        tmp_path / "high-offset-candidate-confirmation.json"
    )
    high_offset_candidate_confirmation.write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-01-01T00:04:00Z",
                "min_confirmations": 2,
                "require_stable_samples": True,
                "batch_size": 20,
                "observed_group_count": 1,
                "confirmed_count": 1,
                "unconfirmed_count": 0,
                "winners": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "baseline": "external_primesieve_count_server",
                        "count_mode": "presieve13",
                        "segment_size": 1310720,
                        "threads": 8,
                        "requested_threads": 8,
                        "confirmation_count": 2,
                        "observed_count": 3,
                        "stable_observed_count": 2,
                        "status": "confirmed",
                        "median_ms_values": [1.55, 1.87],
                        "median_speedup_values": [1.24, 1.08],
                    }
                ],
                "identity_summaries": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "baseline": "external_primesieve_count_server",
                        "count_mode": "presieve13",
                        "segment_size": 1310720,
                        "threads": 8,
                        "requested_threads": 8,
                        "confirmation_count": 2,
                        "observed_count": 3,
                        "stable_observed_count": 2,
                        "status": "confirmed",
                        "median_ms_values": [1.55, 1.87, 1.92],
                        "median_speedup_values": [1.24, 1.08, 1.03],
                    },
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "baseline": "external_primesieve_count_server",
                        "count_mode": "presieve17",
                        "segment_size": 1310720,
                        "threads": 8,
                        "requested_threads": 8,
                        "confirmation_count": 1,
                        "observed_count": 3,
                        "stable_observed_count": 1,
                        "status": "unconfirmed",
                        "median_ms_values": [1.80, 1.86, 1.84],
                        "median_speedup_values": [1.17, 1.13, 1.14],
                    },
                ],
            }
        )
        + "\n"
    )
    high_offset_promotion_focus = tmp_path / "high-offset-promotion-focus.json"
    high_offset_promotion_focus.write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-01-01T00:05:00Z",
                "min_confirmations": 2,
                "require_stable_samples": True,
                "batch_size": 40,
                "observed_group_count": 1,
                "confirmed_count": 0,
                "unconfirmed_count": 1,
                "winners": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "baseline": "external_primesieve_count_server",
                        "count_mode": "presieve13",
                        "segment_size": 1310720,
                        "threads": 8,
                        "requested_threads": 8,
                        "confirmation_count": 1,
                        "observed_count": 2,
                        "stable_observed_count": 2,
                        "status": "unconfirmed",
                        "median_ms_values": [1.79],
                        "median_speedup_values": [1.087],
                    }
                ],
                "identity_summaries": [
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "baseline": "external_primesieve_count_server",
                        "count_mode": "presieve13",
                        "segment_size": 1310720,
                        "threads": 8,
                        "requested_threads": 8,
                        "confirmation_count": 2,
                        "observed_count": 4,
                        "stable_observed_count": 4,
                        "status": "confirmed",
                        "median_ms_values": [1.79, 1.86, 1.95, 1.98],
                        "median_speedup_values": [1.087, 1.042, 0.995, 0.982],
                    },
                    {
                        "low": 1000000000000,
                        "high": 1000010000000,
                        "baseline": "external_primesieve_count_server",
                        "count_mode": "segmented",
                        "segment_size": 1310720,
                        "threads": 8,
                        "requested_threads": 8,
                        "confirmation_count": 1,
                        "observed_count": 2,
                        "stable_observed_count": 2,
                        "status": "unconfirmed",
                        "median_ms_values": [1.93, 1.95],
                        "median_speedup_values": [1.003, 0.999],
                    },
                ],
            }
        )
        + "\n"
    )

    report = build_report(
        benchmark_path=benchmark,
        external_path=external,
        external_metadata_path=external_metadata,
        external_correctness_path=external_correctness,
        external_next_path=external_next,
        external_next_metadata_path=external_next_metadata,
        external_throughput_path=external_throughput,
        external_throughput_metadata_path=external_throughput_metadata,
        external_segment_sweep_path=external_sweep,
        external_segment_sweep_metadata_path=external_sweep_metadata,
        external_mode_sweep_path=external_mode_sweep,
        external_mode_sweep_metadata_path=external_mode_sweep_metadata,
        external_mode_confirmation_path=mode_confirmation,
        external_high_offset_quick_path=external_high_offset_quick,
        external_high_offset_quick_metadata_path=external_high_offset_quick_metadata,
        external_high_offset_tight_path=external_high_offset_tight,
        external_high_offset_tight_metadata_path=external_high_offset_tight_metadata,
        external_high_offset_hot_server_path=external_high_offset_hot_server,
        external_high_offset_hot_server_metadata_path=(
            external_high_offset_hot_server_metadata
        ),
        external_high_offset_count_binary_path=external_high_offset_count_binary,
        external_high_offset_count_binary_metadata_path=(
            external_high_offset_count_binary_metadata
        ),
        external_high_offset_count_binary_candidate_confirm_path=(
            external_high_offset_count_binary_candidate_confirm
        ),
        external_high_offset_count_binary_candidate_confirm_metadata_path=(
            external_high_offset_count_binary_candidate_confirm_metadata
        ),
        external_competitive_smoke_path=external_competitive_smoke,
        external_competitive_smoke_metadata_path=external_competitive_smoke_metadata,
        external_high_offset_candidate_confirmation_path=(
            high_offset_candidate_confirmation
        ),
        external_high_offset_promotion_focus_path=high_offset_promotion_focus,
        high_offset_hot_cold_benchmark_path=high_offset_hot_cold,
        tuning_path=tuning,
        default_calibration_path=calibration,
        generated_at_utc="2026-01-01T00:00:00Z",
    )

    assert report["missing_inputs"] == []
    assert report["external"]["primesieve_wins"] == 1
    assert report["external"]["primesieve_median_wins"] == 1
    assert report["external"]["cold_cli"]["primesieve_wins"] == 0
    assert report["external"]["cold_cli"]["primesieve_rows"] == 2
    assert report["external"]["server"]["primesieve_wins"] == 1
    assert report["external"]["server"]["primesieve_rows"] == 1
    assert report["external"]["primesieve_count_server_wins"] == 0
    assert report["external"]["primesieve_count_server_median_wins"] == 0
    assert report["external"]["external_server"]["primesieve_count_server_rows"] == 1
    assert report["external"]["primecount_wins"] == 1
    assert report["external"]["primecount_median_wins"] == 1
    assert report["external"]["cold_cli"]["primecount_wins"] == 1
    assert report["external"]["server"]["primecount_rows"] == 0
    assert report["external"]["primecount_pi_server_wins"] == 1
    assert report["external"]["primecount_pi_server_median_wins"] == 1
    assert report["external"]["external_server"]["primecount_pi_server_rows"] == 1
    assert report["external"]["metadata"]["tools"]["primesieve"]["version"] == "primesieve 12.14"
    assert report["external"]["metadata"]["tools"]["primecount"]["version"] == "primecount 8.5"
    assert report["external"]["metadata"]["required_external_tools"] == [
        "primecount",
        "primecount-library",
        "primesieve",
        "primesieve-library",
    ]
    assert report["external"]["metadata"]["circle_count_modes"] == ["segmented"]
    assert report["external_correctness"]["available"] is True
    assert report["external_correctness"]["passes"] is True
    assert report["external_correctness"]["check_count"] == 6
    assert report["external_correctness"]["count_check_count"] == 2
    assert report["external_correctness"]["count_server_check_count"] == 1
    assert report["external_correctness"]["enumeration_check_count"] == 2
    assert report["external_correctness"]["next_check_count"] == 1
    assert report["external_correctness"]["failure_count"] == 0
    assert report["external_correctness"]["max_checked_high"] == 18446744073709551615
    assert report["external_correctness"]["circle_count_modes"] == [
        "segmented",
        "hybrid-wheel30-mark",
    ]
    external_next_summary = report["external_next"]
    assert external_next_summary["available"] is True
    assert external_next_summary["primesieve_wins"] == 2
    assert external_next_summary["primesieve_median_wins"] == 2
    assert external_next_summary["cold_cli"]["primesieve_wins"] == 1
    assert external_next_summary["cold_cli"]["primesieve_rows"] == 1
    assert external_next_summary["server"]["primesieve_wins"] == 1
    assert external_next_summary["server"]["primesieve_rows"] == 1
    assert external_next_summary["cold_cli"]["by_baseline"]["external_primecount_next_prime"][
        "wins"
    ] == 1
    assert external_next_summary["server"]["by_baseline"]["external_primecount_next_prime"][
        "wins"
    ] == 1
    assert external_next_summary["server"]["by_baseline"]["external_primecount_next_server"][
        "wins"
    ] == 1
    assert external_next_summary["cold_cli"]["by_baseline"][
        "external_primesieve_generate_next_server"
    ]["wins"] == 0
    assert external_next_summary["server"]["by_baseline"][
        "external_primesieve_generate_next_server"
    ]["wins"] == 1
    assert external_next_summary["metadata"]["starts"] == [100]
    assert external_next_summary["metadata"]["include_circle_server"] is True
    assert external_next_summary["metadata"]["include_primecount"] is True
    assert external_next_summary["metadata"]["primecount_max_start"] == 1000000000000
    assert external_next_summary["metadata"]["include_primecount_library_server"] is True
    assert (
        external_next_summary["metadata"]["primecount_library_max_start"]
        == 1000000000000
    )
    assert external_next_summary["metadata"]["include_primesieve_library_server"] is True
    assert (
        external_next_summary["metadata"]["tools"]["primesieve_library_server"]["method"]
        == "primesieve_generate_n_primes(1, START, UINT64_PRIMES)"
    )
    assert (
        external_next_summary["metadata"]["tools"]["primecount_library_server"]["method"]
        == "primecount_pi(START-1) then primecount_nth_prime(pi+1)"
    )
    assert external_next_summary["speedups"][0]["start"] == 100
    assert external_next_summary["speedups"][0]["result"] == 101
    assert external_next_summary["speedups"][0]["candidate_count"] == 1
    assert external_next_summary["speedups"][0]["baseline"] == (
        "external_primesieve_generate_next_server"
    )
    assert external_next_summary["speedups"][0]["circle_speedup"] == 0.5
    assert external_next_summary["speedups"][0]["sample_stability"] == "stable"
    assert report["default_calibration"]["available"] is True
    assert report["default_calibration"]["within_tolerance_count"] == 1
    assert report["default_calibration"]["noisy_drift_count"] == 0
    assert report["default_calibration"]["recommendations"][0][
        "selected_effective_sample_stability"
    ] == "stable"
    mode_sweep = report["external_mode_sweep"]
    assert mode_sweep["available"] is True
    assert mode_sweep["metadata"]["circle_count_modes"] == [
        "segmented",
        "hybrid-wheel30-mark",
    ]
    assert report["external_mode_confirmation"]["available"] is True
    assert report["external_mode_confirmation"]["confirmed_count"] == 1
    assert report["external_mode_confirmation"]["winners"][0]["count_mode"] == (
        "hybrid-wheel30-mark"
    )
    assert report["external_high_offset_candidate_confirmation"]["available"] is True
    assert report["external_high_offset_candidate_confirmation"]["confirmed_count"] == 1
    assert report["external_high_offset_candidate_confirmation"]["winners"][0][
        "count_mode"
    ] == "presieve13"
    assert report["external_high_offset_candidate_confirmation"]["winners"][0][
        "median_speedup_values"
    ] == [1.24, 1.08]
    assert report["external_high_offset_promotion_focus"]["available"] is True
    assert report["external_high_offset_promotion_focus"]["batch_size"] == 40
    assert report["external_high_offset_promotion_focus"]["confirmed_count"] == 0
    assert report["external_high_offset_promotion_focus"]["unconfirmed_count"] == 1
    assert report["external_high_offset_promotion_focus"]["winners"][0][
        "count_mode"
    ] == "presieve13"
    assert report["external_high_offset_promotion_focus"]["winners"][0][
        "median_speedup_values"
    ] == [1.087]
    assert mode_sweep["best_by_range_baseline"][0]["name"] == (
        "circle_prime_parallel_hybrid_wheel30_mark_count_8t"
    )
    assert mode_sweep["best_by_range_baseline"][0]["median_circle_speedup"] == 0.806
    sweep = report["external_segment_sweep"]
    assert sweep["available"] is True
    assert sweep["metadata"]["requested_segment_sizes"] == [0, 32768, 131072]
    assert sweep["best_by_range_baseline"][0]["segment_size"] == 32768
    assert sweep["best_by_range_baseline"][0]["baseline"] == "external_primecount_pi_diff"
    assert sweep["best_by_range_baseline"][0]["median_circle_speedup"] == 1.161
    assert sweep["best_by_range_baseline"][1]["segment_size"] == 32768
    assert sweep["best_by_range_baseline"][1]["baseline"] == "external_primesieve_count"
    assert sweep["candidate_spread"][0]["candidates"][1]["segment_size"] == 131072
    throughput = report["external_throughput"]
    assert throughput["available"] is True
    assert throughput["metadata"]["requested_segment_sizes"] == [131072, 196608, 262144]
    assert throughput["default_by_range_baseline"][0]["name"] == "circle_prime_default_count"
    assert throughput["default_by_range_baseline"][0]["median_circle_speedup"] == 0.413
    assert throughput["prefix_pi_thread_comparisons"][0]["thread_speedup"] == 1.25
    assert throughput["best_by_range_baseline"][0]["segment_size"] == 196608
    assert throughput["best_by_range_baseline"][0]["median_circle_speedup"] == 0.463
    high_offset_quick = report["external_high_offset_quick"]
    assert high_offset_quick["available"] is True
    assert high_offset_quick["metadata"]["requested_segment_sizes"] == [1310720, 1507328]
    assert high_offset_quick["metadata"]["circle_count_modes"] == ["presieve13"]
    assert high_offset_quick["best_by_range_baseline"][0]["segment_size"] == 1310720
    assert high_offset_quick["best_by_range_baseline"][0]["median_circle_speedup"] == 0.912
    assert high_offset_quick["candidate_spread"][0]["candidates"][1]["segment_size"] == 1507328
    high_offset_tight = report["external_high_offset_tight"]
    assert high_offset_tight["available"] is True
    assert high_offset_tight["metadata"]["requested_segment_sizes"] == [1376256, 1507328]
    assert high_offset_tight["metadata"]["circle_count_modes"] == ["presieve13", "presieve17"]
    assert high_offset_tight["best_by_range_baseline"][0]["segment_size"] == 1376256
    assert high_offset_tight["best_by_range_baseline"][0]["median_circle_speedup"] == 0.889
    assert high_offset_tight["candidate_spread"][0]["candidates"][1]["segment_size"] == 1507328
    high_offset_hot_server = report["external_high_offset_hot_server"]
    assert high_offset_hot_server["available"] is True
    assert high_offset_hot_server["metadata"]["batch_size"] == 20
    assert high_offset_hot_server["metadata"]["batch_request_profile"] == "identical"
    assert high_offset_hot_server["metadata"]["batch_shift"] == 0
    assert high_offset_hot_server["metadata"]["warmup_rounds"] == 2
    assert high_offset_hot_server["metadata"]["include_circle_server"] is True
    assert high_offset_hot_server["metadata"]["include_primesieve_count_server"] is True
    assert high_offset_hot_server["best_by_range_baseline"][0]["name"] == (
        "circle_prime_server_parallel_presieve17_count_8t"
    )
    assert high_offset_hot_server["best_by_range_baseline"][0][
        "median_circle_speedup"
    ] == 1.167
    assert high_offset_hot_server["default_by_range_baseline"][0]["name"] == (
        "circle_prime_server_parallel_default_count_8t"
    )
    high_offset_count_binary = report["external_high_offset_count_binary"]
    assert high_offset_count_binary["available"] is True
    assert high_offset_count_binary["focus_rows_count"] == 8
    assert high_offset_count_binary["focus_median_wins"] == 7
    assert high_offset_count_binary["focus_best_wins"] == 7
    assert high_offset_count_binary["metadata"]["batch_size"] == 20
    assert high_offset_count_binary["metadata"]["tools"]["circle_prime_count"][
        "binary"
    ]["sha256"] == "0123456789abcdef"
    assert high_offset_count_binary["focus_rows"][0]["role"] == (
        "cold_count_binary_vs_primesieve_cli"
    )
    assert high_offset_count_binary["focus_rows"][0]["median_circle_speedup"] == 0.911
    assert high_offset_count_binary["focus_rows"][4]["role"] == (
        "slim_server_vs_libprimesieve"
    )
    assert high_offset_count_binary["focus_rows"][4]["median_circle_speedup"] == 1.125
    assert high_offset_count_binary["focus_rows"][6]["role"] == (
        "hot_server_vs_libprimesieve"
    )
    assert high_offset_count_binary["focus_rows"][6]["median_circle_speedup"] == 1.25
    count_binary_overhead = high_offset_count_binary["cold_hot_overhead"][0]
    assert count_binary_overhead["cold_count_binary_median_ms"] == 5.6
    assert count_binary_overhead["hot_count_binary_server_median_ms"] == 2.0
    assert count_binary_overhead["circle_cold_over_hot_median"] == pytest.approx(
        5.6 / 2.0
    )
    assert count_binary_overhead["circle_cold_extra_ms"] == pytest.approx(3.6)
    assert count_binary_overhead["primesieve_cli_over_lib_median"] == pytest.approx(
        5.1 / 2.25
    )
    assert count_binary_overhead[
        "cold_count_binary_vs_primesieve_median_speedup"
    ] == 0.911
    assert (
        count_binary_overhead[
            "hot_count_binary_server_vs_libprimesieve_median_speedup"
        ]
        == 1.125
    )
    count_binary_candidate_confirm = report[
        "external_high_offset_count_binary_candidate_confirm"
    ]
    assert count_binary_candidate_confirm["available"] is True
    assert count_binary_candidate_confirm["metadata"]["rounds"] == 17
    assert count_binary_candidate_confirm["metadata"]["sample_output"] == str(
        external_high_offset_count_binary_candidate_confirm_samples
    )
    assert count_binary_candidate_confirm["cold_candidate_readout"][0]["action"] == (
        "hold_best_speedup_below_floor"
    )
    assert count_binary_candidate_confirm["cold_candidate_readout"][0]["best"][
        "circle_threads"
    ] == 6
    competitive_smoke = report["external_competitive_smoke"]
    assert competitive_smoke["available"] is True
    assert competitive_smoke["metadata"]["batch_request_profile"] == "shifted"
    assert competitive_smoke["metadata"]["batch_size"] == 20
    assert competitive_smoke["default_by_range_baseline"][0]["name"] == (
        "circle_prime_count_binary_server_parallel_default_count_7t"
    )
    assert competitive_smoke["default_by_range_baseline"][0][
        "median_circle_speedup"
    ] == 4.55
    assert competitive_smoke["default_by_range_baseline"][1][
        "median_circle_speedup"
    ] == 1.15
    promotion = report["external_high_offset_promotion_readout"]
    assert promotion["available"] is True
    assert promotion["rows"][0]["default"]["count_mode"] == "presieve13"
    assert promotion["rows"][0]["best"]["count_mode"] == "presieve17"
    assert promotion["rows"][0]["median_gain_over_default"] == pytest.approx(
        1.167 / 1.105
    )
    assert promotion["rows"][0]["candidate_confirmation_status"] == "missing"
    assert promotion["rows"][0]["candidate_confirmation_freshness"] == "missing"
    assert promotion["rows"][0]["action"] == "hold_unconfirmed_candidate"
    fastest = report["benchmark"]["fastest_primary_counts"]
    materialized = report["benchmark"]["materialized_generation"]
    assert materialized[0]["name"] == "enumerate_range_primes"
    assert materialized[0]["best_ms"] == 1.5
    next_searches = report["benchmark"]["next_prime_searches"]
    assert next_searches[0]["name"] == "next_prime_search"
    assert next_searches[0]["workload"] == 1000000000000
    assert next_searches[0]["segment_size"] == 4096
    assert next_searches[0]["result"] == 1000000000039
    assert next_searches[0]["best_ms"] == 0.05
    assert any(row["name"] == "parallel_segmented_range_count_8t" for row in fastest)
    assert any(
        row["name"] == "parallel_high_offset_default_range_count_8t"
        for row in fastest
    )
    cold_process = report["benchmark"]["cold_process_counts"]
    assert cold_process[0]["name"] == "cold_cli_parallel_default_range_count_8t"
    assert cold_process[0]["best_ms"] == 2.9
    assert any(row["name"] == "cold_process_parallel_segmented_range_count_8t" for row in cold_process)
    assert any(row["scope"] == "high_offset" for row in cold_process)
    hot_cold = report["benchmark"]["high_offset_hot_cold_rows"]
    assert hot_cold[0]["name"] == "parallel_high_offset_default_range_count_8t"
    assert hot_cold[0]["best_ms"] == 2.2
    assert report["benchmark"]["high_offset_cold_hot_overhead_source"] == (
        "high_offset_hot_cold"
    )
    overhead = report["benchmark"]["high_offset_cold_hot_overhead"][0]
    assert overhead["hot_name"] == "parallel_high_offset_presieve17_range_count_8t"
    assert overhead["hot_best_ms"] == 2.05
    assert overhead["hot_server_name"] == (
        "hot_cli_count_server_parallel_high_offset_segmented_count_8t"
    )
    assert overhead["hot_server_best_ms"] == 2.45
    assert overhead["hot_server_over_hot"] == pytest.approx(2.45 / 2.05)
    assert overhead["hot_server_over_cold_cli"] == pytest.approx(2.45 / 4.4)
    assert overhead["cold_cli_best_ms"] == 4.4
    assert overhead["cold_cli_over_hot"] == pytest.approx(4.4 / 2.05)
    assert overhead["cold_cli_extra_ms"] == pytest.approx(2.35)
    assert overhead["cold_process_best_ms"] == 4.1
    assert overhead["cold_process_over_hot"] == pytest.approx(4.1 / 2.05)
    server_external = report["benchmark"]["high_offset_server_external"]
    assert [row["baseline"] for row in server_external] == [
        "external_primecount_pi_diff",
        "external_primecount_pi_diff_server",
        "external_primesieve_count",
        "external_primesieve_count_server",
    ]
    assert server_external[0]["server_best_speedup"] == pytest.approx(17.5 / 2.45)
    assert server_external[1]["server_best_speedup"] == pytest.approx(20.0 / 2.45)
    assert server_external[2]["server_best_speedup"] == pytest.approx(4.9 / 2.45)
    assert server_external[2]["cold_cli_best_speedup"] == pytest.approx(0.7)
    assert server_external[3]["server_best_speedup"] == pytest.approx(4.2 / 2.45)
    assert server_external[3]["cold_cli_best_speedup"] == pytest.approx(0.6)
    spread = report["benchmark"]["primary_candidate_spread"]
    ten_m_candidates = [
        group for group in spread if group["scope"] == "prefix" and group["workload"] == 10000000
    ][0]["candidates"]
    assert ten_m_candidates[0]["segment_size"] == 131072
    assert ten_m_candidates[1]["segment_size"] == 196608
    assert ten_m_candidates[1]["slowdown_vs_fastest"] == 0.65 / 0.6
    experimental = report["benchmark"]["experimental_counts"]
    assert experimental[0]["name"] == "bitpacked_range_count"
    assert experimental[0]["slowdown_vs_primary"] == 5.0
    balanced_experimental = [
        row
        for row in experimental
        if row["name"] == "parallel_balanced_segmented_range_count_8t"
    ][0]
    assert balanced_experimental["slowdown_vs_primary"] == pytest.approx(7 / 6)
    high_offset_experimental = [
        row
        for row in experimental
        if row["name"] == "high_offset_bitpacked_range_count"
    ][0]
    assert high_offset_experimental["scope"] == "high_offset"
    assert high_offset_experimental["slowdown_vs_primary"] == pytest.approx(10.5 / 3.4)
    high_offset_balanced = [
        row
        for row in experimental
        if row["name"] == "parallel_high_offset_balanced_segmented_range_count_8t"
    ][0]
    assert high_offset_balanced["scope"] == "high_offset"
    assert high_offset_balanced["slowdown_vs_primary"] == pytest.approx(3.7 / 3.4)
    assert report["tuning"]["best_by_range"][0]["segment_size"] == 131072
    assert report["tuning"]["best_by_range"][0]["count_mode"] == "segmented"
    assert report["tuning"]["best_by_range"][0]["median_ms"] == 0.7
    assert report["tuning"]["default_alignment"][0]["count_mode_aligned"] is True
    assert report["tuning"]["default_alignment"][0]["segment_size_aligned"] is False
    assert report["tuning"]["default_alignment"][0]["default_source"] == "current_calibration"
    assert report["tuning"]["default_alignment"][0]["artifact_default_stale"] is True
    assert report["tuning"]["default_alignment"][0]["default_segment_size"] == 32768
    assert report["tuning"]["default_alignment"][0]["median_ms"] == 0.7
    assert report["tuning"]["default_alignment"][1]["segment_size_aligned"] is False

    markdown = render_markdown(report)
    assert "`primesieve` cold CLI: Circle faster on 0/2 rows" in markdown
    assert "`primesieve` server: Circle faster on 1/1 rows" in markdown
    assert (
        "`libprimesieve count server` external server: Circle faster on 0/1 rows"
        in markdown
    )
    assert "`primecount` cold CLI: Circle faster on 1/1 rows" in markdown
    assert (
        "`libprimecount pi server` external server: Circle faster on 1/1 rows"
        in markdown
    )
    assert "External Correctness" in markdown
    assert "Status: `passed`; checks: `6`; failures: `0`." in markdown
    assert (
        "Count checks: `2`; count-server checks: `1`; enumeration checks: `2`; "
        "next-prime checks: `1`."
    ) in markdown
    assert "External Next-Prime Search" in markdown
    assert "High-Offset Count-Binary Candidate Confirmation" in markdown
    assert "Focused cold candidate scorecard" in markdown
    assert "hold_best_speedup_below_floor" in markdown
    assert "High-Offset Candidate Confirmation" in markdown
    assert (
        "| [1000000000000, 1000010000000) | "
        "`external_primesieve_count_server` | `presieve13` | 1310720 | "
        "8 | 2/2 | 2/3 | 1.550, 1.870 | 1.240, 1.080 | `confirmed` |"
    ) in markdown
    assert (
        "`libprimesieve generate_n_primes server` cold CLI: "
        "Circle faster on 0/1 rows"
    ) in markdown
    assert (
        "`libprimesieve generate_n_primes server` server: Circle faster on 1/1 rows"
    ) in markdown
    assert "High-Offset Promotion Readout" in markdown
    assert (
        "| [1000000000000, 1000010000000) | "
        "`external_primesieve_count_server` | `presieve13` 1310720 (8) | "
        "1.105 | `presieve17` 1310720 (8) | 1.167 | 1.056x | `missing` | "
        "`missing` | `missing` | `hold_unconfirmed_candidate` |"
    ) in markdown
    assert "`primesieve --nth-prime` cold CLI: Circle faster on 1/1 rows" in markdown
    assert "`primesieve --nth-prime` server: Circle faster on 1/1 rows" in markdown
    assert "`primecount pi+nth-prime` cold CLI: Circle faster on 1/1 rows" in markdown
    assert "`primecount pi+nth-prime` server: Circle faster on 1/1 rows" in markdown
    assert (
        "| 100 | `libprimesieve generate_n_primes server` | 101 | 1 | 1 | "
        "1.000 | 0.500 | 0.500 | 0.500 | stable | baseline_faster |"
    ) in markdown
    assert (
        "| 100 | `primesieve --nth-prime` | 101 | 1 | 1 | 1.000 | 2.000 | "
        "2.000 | 2.000 | unknown | circle_faster |"
    ) in markdown
    assert (
        "| 100 | `primecount pi+nth-prime` | 101 | 1 | 1 | 1.000 | 4.000 | "
        "4.000 | 4.000 | unknown | circle_faster |"
    ) in markdown
    assert "Largest checked high: `18446744073709551615`." in markdown
    assert "Circle count modes checked: `segmented`, `hybrid-wheel30-mark`." in markdown
    assert "`parallel_high_offset_default_range_count_8t`" in markdown

    assert "Cold process count rows" in markdown
    assert "High-offset benchmark rows" in markdown
    assert "High-offset hot/cold rows" in markdown
    assert "High-offset cold/hot overhead" in markdown
    assert "High-offset cold/hot overhead (source: `high_offset_hot_cold`)" in markdown
    assert "| 10000000 | `parallel_high_offset_presieve17_range_count_8t` | 2.050 | `hot_cli_count_server_parallel_high_offset_segmented_count_8t` | 2.450 | 1.20x | 0.56x | 4.400 | 2.15x | 2.350 | 4.100 | 2.00x |" in markdown
    assert "High-offset server/external best-time comparison" in markdown
    assert "| 10000000 | `hot_cli_count_server_parallel_high_offset_segmented_count_8t` | 2.450 | `external_primesieve_count` | 4.900 | 2.000 | 7.000 | 0.700 |" in markdown
    assert (
        "| 10000000 | `parallel_high_offset_default_range_count_8t` | "
        "3145728 | 3.400 | 361726 |"
    ) in markdown
    assert "Materialized generation rows" in markdown
    assert "| 1000000 | `enumerate_range_primes` | 262144 | 1.500 | 78498 |" in markdown
    assert "Next-prime search rows" in markdown
    assert "| 1000000000000 | `next_prime_search` | 4096 | 0.050 | 1000000000039 |" in markdown
    assert "`circle_prime_parallel_segmented_count_8t` (threads: 8)" in markdown
    assert "`circle_prime_parallel_segmented_count_4t` (threads: 4/8)" in markdown
    assert "`external_primecount_pi_diff` (threads: tool default)" in markdown
    assert "`primesieve`: primesieve 12.14 (`/usr/local/bin/primesieve`)" in markdown
    assert (
        "`circle_count_server`: available (`/tmp/circle-prime`); "
        "method `persistent count-server requests`."
    ) in markdown
    assert (
        "`circle_count_server` small-prefix `pi` cache: limit `2000000000`; "
        "default `2000000000`; max `3000000000`; "
        "env `CIRCLE_PRIME_SMALL_PREFIX_PI_CACHE_LIMIT`; "
        "scope prefix-pi count-server ranges with HIGH-1 at or below the limit."
    ) in markdown
    assert (
        "`circle_count_server` small-prefix `pi` cache memory: estimated bytes "
        "`187500004`; default bytes `187500004`; max bytes `281250004`."
    ) in markdown
    assert (
        "`circle_count_server` small-prefix `pi` cache startup warmup: min "
        "`4000.000 ms`; median `4100.000 ms`; max `4200.000 ms`; samples `2`."
    ) in markdown
    assert (
        "`circle_count_server` small-prefix `pi` cache warmup: eligible prefix-pi "
        "count-server rows pass --warm-prefix-pi-cache before reading timed requests."
    ) in markdown
    assert (
        "`primesieve_count_server`: available (`/tmp/primesieve-count-server`); "
        "method `primesieve_count_primes(LOW, HIGH-1)`."
    ) in markdown
    assert (
        "`primecount_pi_server`: available (`/tmp/primecount-pi-server`); "
        "method `primecount_pi(HIGH-1)-primecount_pi(LOW-1)`."
    ) in markdown
    assert "requested threads: Circle `8`, external `8`" in markdown
    assert "warmup: `1` unrecorded interleaved pass(es)." in markdown
    assert (
        "repeated count requests per timed sample: `3` "
        "(reported timings are per-request averages)."
    ) in markdown
    assert "Circle count modes: `segmented`" in markdown
    assert (
        "required external controls: `primecount`, `primecount-library`, "
        "`primesieve`, `primesieve-library`"
        in markdown
    )
    assert "libprimesieve count-server rows included." in markdown
    assert "libprimecount pi-server rows included." in markdown
    assert "External Segment Sweep" in markdown
    assert "External Count Mode Sweep" in markdown
    assert "External Mode Confirmation" in markdown
    assert "Fresh-run count requests per timed sample: `3`." in markdown
    assert "External Throughput" in markdown
    assert "High-Offset Quick Scorecard" in markdown
    assert "High-offset quick candidate spread" in markdown
    assert "High-Offset Tight Scorecard" in markdown
    assert "High-offset tight candidate spread" in markdown
    assert "High-Offset Hot-Server Scorecard" in markdown
    assert "Adaptive default hot-server scorecard" in markdown
    assert "Best hot-server candidate scorecard" in markdown
    assert "High-offset hot-server candidate spread" in markdown
    assert "High-Offset Count Binary" in markdown
    assert "Focused rows: `8`; median wins: `7/8`; best-time wins: `7/8`." in markdown
    assert (
        "`circle-prime-count`: 0.1.0 (`/tmp/circle-prime-count`; "
        "sha `0123456789ab`, size `1372800` bytes)."
    ) in markdown
    assert (
        "| cold count binary vs primesieve CLI | "
        "[1000000000000, 1000010000000) | "
        "`circle_prime_count_binary_parallel_default_count_8t`<br>mode: "
        "`presieve13` | `primesieve CLI count` | 5.600 | 5.100 | "
        "0.980 | 0.911 | unknown | baseline_faster |"
    ) in markdown
    assert (
        "| slim count binary server vs libprimesieve | "
        "[1000000000000, 1000010000000) | "
        "`circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: "
        "`presieve13` | `libprimesieve count server` | 2.000 | 2.250 | "
        "1.105 | 1.125 | unknown | circle_faster |"
    ) in markdown
    assert (
        "| hot server vs libprimesieve | [1000000000000, 1000010000000) | "
        "`circle_prime_server_parallel_default_count_8t`<br>mode: "
        "`presieve13` | `libprimesieve count server` | 1.800 | 2.250 | "
        "1.235 | 1.250 | unknown | circle_faster |"
    ) in markdown
    assert "Cold-binary overhead diagnosis" in markdown
    assert (
        "| Range | Cold Count Binary Median ms | "
        "Hot Count Binary Server Median ms | Circle Cold/Hot | "
        "Circle Extra ms | primesieve CLI/lib | Cold vs primesieve | "
        "Hot count binary vs libprimesieve |"
    ) in markdown
    assert (
        "| [1000000000000, 1000010000000) | 5.600 | 2.000 | "
        "2.80x | 3.600 | 2.27x | 0.911 | 1.125 |"
    ) in markdown
    assert "Competitive Smoke Scorecard" in markdown
    assert "Fresh shifted count-binary smoke scorecard" in markdown
    assert (
        "| [1000000000000, 1000010000000) | "
        "`external_primesieve_count_server` | "
        "`circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: "
        "`presieve13` | 1638400 | 7/8 | 1.900 | 2.000 | 1.158 | "
        "1.150 | unknown | circle_faster |"
    ) in markdown
    assert "High-Offset Promotion Focus Confirmation" in markdown
    assert "Fresh-run count requests per timed sample: `40`." in markdown
    assert (
        "| [1000000000000, 1000010000000) | "
        "`external_primesieve_count_server` | `presieve13` | 1310720 | "
        "8 | 1/2 | 2/2 | 1.790 | 1.087 | `unconfirmed` |"
    ) in markdown
    assert "Requested Circle segment sizes: `1310720`, `1507328`." in markdown
    assert "Requested Circle segment sizes: `1376256`, `1507328`." in markdown
    assert "Requested Circle segment sizes: `0`, `1310720`." in markdown
    assert "Count mode candidate spread" in markdown
    assert "Throughput segment candidate spread" in markdown
    assert "Adaptive default scorecard" in markdown
    assert "Prefix-pi thread comparison" in markdown
    assert (
        "| [1000000000, 2000000000) | `external_primesieve_count` | "
        "`circle_prime_prefix_pi_count`<br>mode: `prefix-pi` (1) | "
        "`circle_prime_parallel_default_count_2t` (2/8) | "
        "15.000 | 12.000 | 1.250 | `default_faster` |"
    ) in markdown
    assert (
        "| [0, 1000000000) | `external_primesieve_count` | "
        "`circle_prime_default_count` | 262144 | 1/8 | "
        "45.000 | 46.000 | 0.400 | 0.413 | unknown | baseline_faster |"
    ) in markdown
    assert (
        "| [0, 1000000000) | `external_primesieve_count` | "
        "`circle_prime_parallel_segmented_count_8t` | 196608 | 8 | "
        "39.000 | 41.000 | 0.462 | 0.463 | unknown | baseline_faster |"
    ) in markdown
    assert "Circle count modes: `segmented`, `hybrid-wheel30-mark`." in markdown
    assert "Requested Circle segment sizes: `0`, `32768`, `131072`." in markdown
    assert "Requested Circle segment sizes: `131072`, `196608`, `262144`." in markdown
    assert "| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t` | 65536 | 8 | 3.000 | 3.100 | 0.800 | 0.806 | unknown | baseline_faster |" in markdown
    assert "| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t` | 65536 | 8 | 3.300 | 3.500 | 0.727 | 0.714 | unknown |" in markdown
    assert "| [0, 10000000) | `external_primesieve_count` | `hybrid-wheel30-mark` | 65536 | 8 | 2/2 | 3/3 | 3.100, 3.200 | 1.100, 1.200 | `confirmed` |" in markdown
    assert "| [0, 10000000) | `external_primesieve_count` | 32768 | 8 | 3.100 | 3.100 | 0.774 | 0.806 | unknown | baseline_faster |" in markdown
    assert "| [0, 10000000) | `external_primecount_pi_diff` | 32768 | 8 | 3.100 | 3.100 | 1.129 | 1.161 | unknown | circle_faster |" in markdown
    assert "Experimental count lanes" in markdown
    assert "Primary count candidate spread" in markdown
    assert "| prefix | 10000000 | `parallel_segmented_range_count_8t` | 196608 | 0.650 | 1.08x |" in markdown
    assert "5.00x" in markdown
    assert "Default alignment" in markdown
    assert "noisy drift: `0`" in markdown
    assert "noisy<br>effective stable" in markdown
    assert "Samples: `12`; rounds: `3`" in markdown
    assert "Default alignment uses current calibration defaults when available" in markdown
    assert "| Range | Source | Baseline | Selected Mode | Default Mode | Selected Segment | Default Segment | Threads | Median ms | Samples | Ratio | Status |" in markdown
    assert "| Range | Source | Baseline | Selected Segment | Default Segment | Threads | Median ms | Ratio | Status |" not in markdown
    assert (
        "| [0, 10000000) | `segmented` | `segmented` | 131072 | 32768 | "
        "8/8 | 8/8 | `current_calibration; stale artifact` | 0.700 | no |"
    ) in markdown
    assert (
        "| [0, 1000000) | `segmented` | `segmented` | 16384 | 262144 | "
        "2/2 | 2/2 | `tuning_artifact` | 0.250 | no |"
    ) in markdown


def test_high_offset_promotion_action_rejects_stale_confirmed_candidate() -> None:
    assert (
        high_offset_promotion_action(
            best_is_default=False,
            best_median_speedup=1.2,
            median_gain_over_default=1.05,
            candidate_status="confirmed",
            candidate_confirmation_freshness="stale",
        )
        == "hold_stale_candidate_confirmation"
    )


def test_high_offset_promotion_action_requires_known_fresh_confirmation() -> None:
    assert (
        high_offset_promotion_action(
            best_is_default=False,
            best_median_speedup=1.2,
            median_gain_over_default=1.05,
            candidate_status="confirmed",
            candidate_confirmation_freshness="unknown",
        )
        == "hold_unfresh_candidate_confirmation"
    )


def test_high_offset_promotion_action_allows_fresh_confirmed_material_gain() -> None:
    assert (
        high_offset_promotion_action(
            best_is_default=False,
            best_median_speedup=1.2,
            median_gain_over_default=1.05,
            candidate_status="confirmed",
            candidate_confirmation_freshness="fresh",
        )
        == "trial_candidate_default"
    )


def test_high_offset_promotion_readout_prefers_fresh_focus_confirmation() -> None:
    default = {
        "low": 1000000000000,
        "high": 1000010000000,
        "baseline": "external_primesieve_count_server",
        "name": "circle_prime_server_parallel_default_count_8t",
        "count_mode": "presieve13",
        "segment_size": 1310720,
        "circle_threads": 8,
        "circle_requested_threads": 8,
        "median_circle_speedup": 1.1,
    }
    best = {
        **default,
        "name": "circle_prime_server_parallel_segmented_count_8t",
        "count_mode": "segmented",
        "median_circle_speedup": 1.3,
    }
    stale_candidate_confirmation = {
        "available": True,
        "generated_at_utc": "2025-12-31T23:59:00Z",
        "winners": [
            {
                "low": 1000000000000,
                "high": 1000010000000,
                "baseline": "external_primesieve_count_server",
                "count_mode": "segmented",
                "segment_size": 1310720,
                "threads": 8,
                "requested_threads": 8,
                "status": "confirmed",
            }
        ],
        "identity_summaries": [
            {
                "low": 1000000000000,
                "high": 1000010000000,
                "baseline": "external_primesieve_count_server",
                "count_mode": "segmented",
                "segment_size": 1310720,
                "threads": 8,
                "requested_threads": 8,
                "status": "confirmed",
            }
        ],
    }
    fresh_focus_confirmation = {
        "available": True,
        "generated_at_utc": "2026-01-01T00:01:00Z",
        "winners": [
            {
                "low": 1000000000000,
                "high": 1000010000000,
                "baseline": "external_primesieve_count_server",
                "count_mode": "segmented",
                "segment_size": 1310720,
                "threads": 8,
                "requested_threads": 8,
                "status": "unconfirmed",
            }
        ],
        "identity_summaries": [
            {
                "low": 1000000000000,
                "high": 1000010000000,
                "baseline": "external_primesieve_count_server",
                "count_mode": "segmented",
                "segment_size": 1310720,
                "threads": 8,
                "requested_threads": 8,
                "status": "unconfirmed",
            }
        ],
    }

    readout = summarize_high_offset_promotion_readout(
        {
            "available": True,
            "metadata": {"finished_at_utc": "2026-01-01T00:00:00Z"},
            "default_by_range_baseline": [default],
            "best_by_range_baseline": [best],
        },
        {"available": False},
        stale_candidate_confirmation,
        fresh_focus_confirmation,
    )

    row = readout["rows"][0]
    assert row["candidate_confirmation_source"] == "promotion_focus"
    assert row["candidate_confirmation_status"] == "unconfirmed"
    assert row["candidate_confirmation_freshness"] == "fresh"
    assert row["action"] == "hold_unconfirmed_candidate"


def test_high_offset_shifted_candidate_action_holds_small_gain() -> None:
    assert (
        high_offset_shifted_candidate_action(
            best_is_default=False,
            best_median_speedup=1.224,
            median_gain_over_default=1.024,
        )
        == "hold_small_gain_candidate"
    )


def test_high_offset_shifted_candidate_action_allows_material_gain() -> None:
    assert (
        high_offset_shifted_candidate_action(
            best_is_default=False,
            best_median_speedup=1.31,
            median_gain_over_default=1.05,
        )
        == "trial_shifted_candidate"
    )


def test_shifted_candidate_readout_compares_best_against_default() -> None:
    summary = {
        "available": True,
        "metadata": {
            "batch_request_profile": "shifted",
            "batch_size": 80,
            "batch_shift": 10_000_000,
            "rounds": 13,
            "warmup_rounds": 2,
            "finished_at_utc": "2026-01-01T00:00:00Z",
        },
        "default_by_range_baseline": [
            shifted_speedup_row(
                name="circle_prime_server_parallel_default_count_8t",
                segment_size=1_310_720,
                threads=8,
                median_speedup=1.195,
            )
        ],
        "best_by_range_baseline": [
            shifted_speedup_row(
                name="circle_prime_server_parallel_presieve13_count_7t",
                segment_size=1_507_328,
                threads=7,
                median_speedup=1.224,
            )
        ],
    }

    readout = summarize_high_offset_shifted_candidate_readout(summary)

    assert readout["available"] is True
    assert readout["batch_request_profile"] == "shifted"
    assert readout["batch_size"] == 80
    assert readout["batch_shift"] == 10_000_000
    row = readout["rows"][0]
    assert row["best"]["segment_size"] == 1_507_328
    assert row["median_gain_over_default"] == pytest.approx(1.224 / 1.195)
    assert row["action"] == "hold_small_gain_candidate"


def test_shifted_candidate_readout_treats_same_effective_plan_as_default() -> None:
    summary = {
        "available": True,
        "metadata": {},
        "default_by_range_baseline": [
            shifted_speedup_row(
                name="circle_prime_server_parallel_default_count_7t",
                segment_size=1_638_400,
                threads=7,
                requested_threads=8,
                median_speedup=1.109,
            )
        ],
        "best_by_range_baseline": [
            shifted_speedup_row(
                name="circle_prime_server_parallel_presieve13_count_7t",
                segment_size=1_638_400,
                threads=7,
                requested_threads=7,
                median_speedup=1.237,
            )
        ],
    }

    readout = summarize_high_offset_shifted_candidate_readout(summary)

    row = readout["rows"][0]
    assert row["best_is_default"] is True
    assert row["median_gain_over_default"] == pytest.approx(1.237 / 1.109)
    assert row["action"] == "keep_default"


def shifted_speedup_row(
    *,
    name: str,
    segment_size: int,
    threads: int,
    requested_threads: int = 8,
    median_speedup: float,
) -> dict:
    return {
        "low": 1_000_000_000_000,
        "high": 1_000_010_000_000,
        "baseline": "external_primesieve_count_server",
        "name": name,
        "count_mode": "presieve13",
        "segment_size": segment_size,
        "circle_threads": threads,
        "circle_requested_threads": requested_threads,
        "median_circle_speedup": median_speedup,
    }


def test_report_sample_stats_ignore_one_high_outlier_for_stability() -> None:
    stats = sample_stats([1.0, 1.01, 1.02, 1.03, 9.0])

    assert stats["stability"] == "stable"
    assert stats["ignored_single_high_outlier"] is True
    assert stats["noise_over_median"] == pytest.approx(1.03 / 1.02)
    assert stats["max_over_median"] == pytest.approx(9.0 / 1.02)
    assert sample_spread_text(stats) == "n=5, robust/med=1.01, max/med=8.82"


def test_report_sample_stats_keep_repeated_high_samples_noisy() -> None:
    stats = sample_stats([1.0, 1.01, 1.02, 4.0, 9.0])

    assert stats["stability"] == "noisy"
    assert stats["ignored_single_high_outlier"] is True
    assert stats["noise_over_median"] == pytest.approx(4.0 / 1.02)


def test_circle_row_label_includes_resolved_count_mode() -> None:
    assert (
        circle_row_label(
            {
                "name": "circle_prime_parallel_default_count_3t",
                "count_mode": "balanced",
            }
        )
        == "`circle_prime_parallel_default_count_3t`<br>mode: `balanced`"
    )
    assert (
        circle_row_label({"name": "external_primesieve_count", "count_mode": None})
        == "`external_primesieve_count`"
    )


def test_prime_engine_report_tolerates_missing_inputs(tmp_path: Path) -> None:
    report = build_report(
        benchmark_path=tmp_path / "missing-benchmark.csv",
        external_path=tmp_path / "missing-external.csv",
        external_metadata_path=tmp_path / "missing-external.json",
        external_correctness_path=tmp_path / "missing-correctness.json",
        tuning_path=tmp_path / "missing-tuning.json",
        generated_at_utc="2026-01-01T00:00:00Z",
    )

    assert len(report["missing_inputs"]) == 4
    assert report["benchmark"]["fastest_primary_counts"] == []
    assert report["benchmark"]["primary_candidate_spread"] == []
    assert report["benchmark"]["experimental_counts"] == []
    assert report["external"]["speedups"] == []
    assert report["external"]["metadata"]["available"] is False
    assert report["external_correctness"]["available"] is False
    assert report["external"]["metadata"]["circle_count_modes"] == []
    assert report["external"]["metadata"]["required_external_tools"] == []
    assert report["external_mode_sweep"]["available"] is False
    assert report["tuning"]["available"] is False
    assert report["tuning"]["default_alignment"] == []
