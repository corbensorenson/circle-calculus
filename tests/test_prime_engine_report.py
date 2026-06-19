from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.report_prime_engine_results import build_report, circle_row_label, render_markdown


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
                "timing,external_primecount_pi_diff,1000000000000,1000010000000,10000000,0,361726,3,17.500,18.000,571428571,555555555,0,0,,,",
                "speedup,circle_prime_parallel_segmented_count_4t,1000000000000,1000010000000,10000000,3145728,361726,3,7.000,7.500,1428571428,1333333333,4,8,external_primecount_pi_diff,2.500,2.400",
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
                "row_count": 4,
                "rounds": 3,
                "required_external_tools": ["primesieve", "primecount"],
                "circle_count_modes": ["segmented"],
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
                "enumeration_check_count": 2,
                "next_check_count": 1,
                "check_count": 5,
                "count_failure_count": 0,
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
                "kind,name,start,batch_size,result,candidate_count,rounds,best_ms,median_ms,searches_per_second,median_searches_per_second,threads,requested_threads,baseline,best_speedup,median_speedup",
                "timing,circle_prime_next_prime,100,1,101,1,3,1.000,1.200,1000,833.333,1,1,,,",
                "timing,external_primesieve_next_prime,100,1,101,0,3,2.000,2.400,500,416.667,8,8,,,",
                "speedup,circle_prime_next_prime,100,1,101,1,3,1.000,1.200,1000,833.333,1,1,external_primesieve_next_prime,2.000,2.000",
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
                "starts": [100],
                "required_external_tools": ["primesieve"],
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
                "timing,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,131072,50847534,5,40.000,42.000,25000000000,23809523809,8,8,,,",
                "timing,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,196608,50847534,5,39.000,41.000,25641025641,24390243902,8,8,,,",
                "timing,external_primesieve_count,0,1000000000,1000000000,0,50847534,5,18.000,19.000,55555555555,52631578947,8,8,,,",
                "speedup,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,131072,50847534,5,40.000,42.000,25000000000,23809523809,8,8,external_primesieve_count,0.450,0.452",
                "speedup,circle_prime_parallel_segmented_count_8t,0,1000000000,1000000000,196608,50847534,5,39.000,41.000,25641025641,24390243902,8,8,external_primesieve_count,0.462,0.463",
            ]
        )
        + "\n"
    )
    external_throughput_metadata = tmp_path / "external-throughput.json"
    external_throughput_metadata.write_text(
        json.dumps(
            {
                "row_count": 5,
                "rounds": 5,
                "required_external_tools": ["primesieve", "primecount"],
                "requested_segment_sizes": [131072, 196608],
                "thread_policy": {
                    "circle_requested_threads": 8,
                    "external_requested_threads": 8,
                },
                "ranges": [{"low": 0, "high": 1000000000, "span": 1000000000}],
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
    high_offset_hot_cold = tmp_path / "high-offset-hot-cold.csv"
    high_offset_hot_cold.write_text(
        "\n".join(
            [
                "kind,name,workload,segment_size,result,rounds,best_ms,rate_per_second,baseline,best_speedup",
                "timing,parallel_high_offset_default_range_count_8t,10000000,1376256,361726,7,2.200,4545454545,,",
                "timing,parallel_high_offset_presieve17_range_count_8t,10000000,1376256,361726,7,2.050,4878048780,,",
                "timing,hot_cli_count_server_parallel_high_offset_default_range_count_8t,10000000,1376256,361726,7,2.600,3846153846,,",
                "timing,hot_cli_count_server_parallel_high_offset_presieve17_count_8t,10000000,1376256,361726,7,2.500,4000000000,,",
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
                    }
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
        high_offset_hot_cold_benchmark_path=high_offset_hot_cold,
        tuning_path=tuning,
        default_calibration_path=calibration,
        generated_at_utc="2026-01-01T00:00:00Z",
    )

    assert report["missing_inputs"] == []
    assert report["external"]["primesieve_wins"] == 0
    assert report["external"]["primesieve_median_wins"] == 0
    assert report["external"]["primecount_wins"] == 1
    assert report["external"]["primecount_median_wins"] == 1
    assert report["external"]["metadata"]["tools"]["primesieve"]["version"] == "primesieve 12.14"
    assert report["external"]["metadata"]["tools"]["primecount"]["version"] == "primecount 8.5"
    assert report["external"]["metadata"]["required_external_tools"] == [
        "primecount",
        "primesieve",
    ]
    assert report["external"]["metadata"]["circle_count_modes"] == ["segmented"]
    assert report["external_correctness"]["available"] is True
    assert report["external_correctness"]["passes"] is True
    assert report["external_correctness"]["check_count"] == 5
    assert report["external_correctness"]["count_check_count"] == 2
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
    assert external_next_summary["primesieve_wins"] == 1
    assert external_next_summary["primesieve_median_wins"] == 1
    assert external_next_summary["metadata"]["starts"] == [100]
    assert external_next_summary["speedups"][0]["start"] == 100
    assert external_next_summary["speedups"][0]["result"] == 101
    assert external_next_summary["speedups"][0]["candidate_count"] == 1
    assert external_next_summary["speedups"][0]["circle_speedup"] == 2.0
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
    assert throughput["metadata"]["requested_segment_sizes"] == [131072, 196608]
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
    assert overhead["hot_best_ms"] == 2.2
    assert overhead["hot_server_name"] == (
        "hot_cli_count_server_parallel_high_offset_presieve17_count_8t"
    )
    assert overhead["hot_server_best_ms"] == 2.5
    assert overhead["hot_server_over_hot"] == pytest.approx(2.5 / 2.2)
    assert overhead["hot_server_over_cold_cli"] == pytest.approx(2.5 / 4.4)
    assert overhead["cold_cli_best_ms"] == 4.4
    assert overhead["cold_cli_over_hot"] == pytest.approx(2.0)
    assert overhead["cold_cli_extra_ms"] == pytest.approx(2.2)
    assert overhead["cold_process_best_ms"] == 4.1
    assert overhead["cold_process_over_hot"] == pytest.approx(4.1 / 2.2)
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
    assert "Circle faster on 0/1 rows" in markdown
    assert "External Correctness" in markdown
    assert "Status: `passed`; checks: `5`; failures: `0`." in markdown
    assert "Count checks: `2`; enumeration checks: `2`; next-prime checks: `1`." in markdown
    assert "External Next-Prime Search" in markdown
    assert "`primesieve --nth-prime`: Circle faster on 1/1 rows" in markdown
    assert "| 100 | 101 | 1 | 1 | 1.000 | 2.000 | 2.000 | 2.000 | unknown | circle_faster |" in markdown
    assert "Largest checked high: `18446744073709551615`." in markdown
    assert "Circle count modes checked: `segmented`, `hybrid-wheel30-mark`." in markdown
    assert "`parallel_high_offset_default_range_count_8t`" in markdown
    assert "Cold process count rows" in markdown
    assert "High-offset benchmark rows" in markdown
    assert "High-offset hot/cold rows" in markdown
    assert "High-offset cold/hot overhead" in markdown
    assert "High-offset cold/hot overhead (source: `high_offset_hot_cold`)" in markdown
    assert "| 10000000 | `parallel_high_offset_default_range_count_8t` | 2.200 | `hot_cli_count_server_parallel_high_offset_presieve17_count_8t` | 2.500 | 1.14x | 0.57x | 4.400 | 2.00x | 2.200 | 4.100 | 1.86x |" in markdown
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
    assert "requested threads: Circle `8`, external `8`" in markdown
    assert "Circle count modes: `segmented`" in markdown
    assert "required external controls: `primecount`, `primesieve`" in markdown
    assert "External Segment Sweep" in markdown
    assert "External Count Mode Sweep" in markdown
    assert "External Mode Confirmation" in markdown
    assert "External Throughput" in markdown
    assert "High-Offset Quick Scorecard" in markdown
    assert "High-offset quick candidate spread" in markdown
    assert "High-Offset Tight Scorecard" in markdown
    assert "High-offset tight candidate spread" in markdown
    assert "Requested Circle segment sizes: `1310720`, `1507328`." in markdown
    assert "Requested Circle segment sizes: `1376256`, `1507328`." in markdown
    assert "Count mode candidate spread" in markdown
    assert "Throughput segment candidate spread" in markdown
    assert "Circle count modes: `segmented`, `hybrid-wheel30-mark`." in markdown
    assert "Requested Circle segment sizes: `0`, `32768`, `131072`." in markdown
    assert "Requested Circle segment sizes: `131072`, `196608`." in markdown
    assert "| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t` | 65536 | 8 | 3.000 | 3.100 | 0.800 | 0.806 | unknown | baseline_faster |" in markdown
    assert "| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t` | 65536 | 8 | 3.300 | 3.500 | 0.727 | 0.714 | unknown |" in markdown
    assert "| [0, 10000000) | `external_primesieve_count` | `hybrid-wheel30-mark` | 65536 | 8 | 2/2 | 3/3 | 3.100, 3.200 | `confirmed` |" in markdown
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
