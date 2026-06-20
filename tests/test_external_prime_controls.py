from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scripts import benchmark_prime_external_controls
from scripts.benchmark_prime_external_controls import (
    CircleVariant,
    ExternalBenchRow,
    Measurement,
    build_run_metadata,
    circle_measurement_name,
    circle_prime_command,
    circle_server_measurement_name,
    measure_interleaved,
    median,
    parse_circle_count_modes,
    parse_circle_variants,
    parse_segment_size_list,
    primecount_command,
    primesieve_command,
    required_external_tools_missing,
    speedup_row,
)


def test_circle_prime_command_records_requested_threads() -> None:
    command = circle_prime_command(
        Path("circle-prime"),
        0,
        1000,
        131072,
        8,
        json_output=True,
    )

    assert command == [
        "circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--json",
        "--segment-size",
        "131072",
        "--threads",
        "8",
        "--count-mode",
        "segmented",
    ]


def test_circle_prime_command_can_request_experimental_count_mode() -> None:
    command = circle_prime_command(
        Path("circle-prime"),
        0,
        1000,
        131072,
        8,
        "hybrid-wheel30-mark",
        json_output=True,
    )

    assert command == [
        "circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--json",
        "--segment-size",
        "131072",
        "--threads",
        "8",
        "--count-mode",
        "hybrid-wheel30-mark",
    ]


def test_circle_prime_command_explicit_segmented_mode_is_forced() -> None:
    command = circle_prime_command(
        Path("circle-prime"),
        0,
        1000,
        131072,
        8,
        "segmented",
        json_output=True,
    )

    assert command == [
        "circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--json",
        "--segment-size",
        "131072",
        "--threads",
        "8",
        "--count-mode",
        "segmented",
    ]


def test_circle_prime_command_default_mode_omits_count_mode_flag() -> None:
    command = circle_prime_command(
        Path("circle-prime"),
        0,
        1000,
        0,
        8,
        "default",
        json_output=True,
    )

    assert command == [
        "circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--json",
        "--threads",
        "8",
    ]


def test_circle_count_mode_parser_and_names() -> None:
    assert parse_circle_count_modes(
        "default,segmented,dynamic,prefix-pi,hybrid-wheel30-mark,segmented"
    ) == [
        "default",
        "segmented",
        "dynamic",
        "prefix-pi",
        "hybrid-wheel30-mark",
    ]
    assert circle_measurement_name("default", 1) == "circle_prime_default_count"
    assert circle_measurement_name("segmented", 1) == "circle_prime_segmented_count"
    assert circle_measurement_name("dynamic", 8) == "circle_prime_parallel_dynamic_count_8t"
    assert circle_measurement_name("prefix-pi", 1) == "circle_prime_prefix_pi_count"
    assert (
        circle_measurement_name("default", 8)
        == "circle_prime_parallel_default_count_8t"
    )
    assert (
        circle_measurement_name("hybrid-wheel30-mark", 8)
        == "circle_prime_parallel_hybrid_wheel30_mark_count_8t"
    )
    assert (
        circle_server_measurement_name("default", 7)
        == "circle_prime_server_parallel_default_count_7t"
    )
    assert (
        circle_server_measurement_name("presieve13", 4)
        == "circle_prime_server_parallel_presieve13_count_4t"
    )


def test_circle_variant_parser_can_avoid_cross_product() -> None:
    assert parse_circle_variants([], [0, 131072], ["default", "segmented"]) == [
        CircleVariant(segment_size=0, count_mode="default"),
        CircleVariant(segment_size=0, count_mode="segmented"),
        CircleVariant(segment_size=131072, count_mode="default"),
        CircleVariant(segment_size=131072, count_mode="segmented"),
    ]
    assert parse_circle_variants(
        ["default:0", "segmented:131072,segmented:196608", "prefix-pi:0:2"],
        [0],
        ["segmented"],
    ) == [
        CircleVariant(segment_size=0, count_mode="default"),
        CircleVariant(segment_size=131072, count_mode="segmented"),
        CircleVariant(segment_size=196608, count_mode="segmented"),
        CircleVariant(segment_size=0, count_mode="prefix-pi", threads=2),
    ]


def test_external_commands_can_request_threads() -> None:
    assert primesieve_command("primesieve", 0, 999, 8) == [
        "primesieve",
        "0",
        "999",
        "--count",
        "--quiet",
        "--threads=8",
    ]
    assert primecount_command("primecount", 999, 8) == [
        "primecount",
        "999",
        "--threads=8",
    ]


def test_external_commands_can_keep_tool_thread_defaults() -> None:
    assert primesieve_command("primesieve", 0, 999, 0) == [
        "primesieve",
        "0",
        "999",
        "--count",
        "--quiet",
    ]
    assert primecount_command("primecount", 999, 0) == ["primecount", "999"]


def test_segment_size_sweep_parser_preserves_order_and_deduplicates() -> None:
    assert parse_segment_size_list(None, 0) == [0]
    assert parse_segment_size_list("0,131072,98304,131072", 0) == [
        0,
        131072,
        98304,
    ]


def test_external_rows_record_median_speedup() -> None:
    assert median([3.0, 1.0, 2.0]) == 2.0
    assert median([4.0, 1.0, 2.0, 3.0]) == 2.5

    circle = ExternalBenchRow(
        kind="timing",
        name="circle_prime_parallel_segmented_count_8t",
        low=0,
        high=1000,
        span=1000,
        segment_size=32768,
        result=168,
        rounds=3,
        best_ms=2.0,
        median_ms=3.0,
        rate_per_second=500000.0,
        median_rate_per_second=333333.3,
        threads=8,
        requested_threads=8,
        baseline="",
        best_speedup="",
        median_speedup="",
        count_mode="balanced",
    )
    baseline = ExternalBenchRow(
        kind="timing",
        name="external_primesieve_count",
        low=0,
        high=1000,
        span=1000,
        segment_size=0,
        result=168,
        rounds=3,
        best_ms=1.0,
        median_ms=6.0,
        rate_per_second=1000000.0,
        median_rate_per_second=166666.7,
        threads=8,
        requested_threads=8,
        baseline="",
        best_speedup="",
        median_speedup="",
    )

    row = speedup_row(circle, baseline)

    assert row.best_speedup == "0.500"
    assert row.median_speedup == "2.000"
    assert row.median_ms == 3.0
    assert row.count_mode == "balanced"


def test_external_metadata_records_thread_policy_and_commands(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=5,
        segment_size=131072,
        circle_threads=8,
        external_threads=4,
        require_tool=["primesieve", "primecount"],
        include_circle_server=True,
    )

    metadata = build_run_metadata(
        args=args,
        ranges=[(0, 1000), (100, 200)],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        row_count=6,
    )

    assert metadata["rounds"] == 5
    assert metadata["row_count"] == 6
    assert metadata["interleaved"] is False
    assert metadata["include_circle_server"] is True
    assert metadata["requested_segment_sizes"] == [131072]
    assert metadata["thread_policy"]["circle_requested_threads"] == 8
    assert metadata["thread_policy"]["external_requested_threads"] == 4
    assert metadata["required_external_tools"] == ["primecount", "primesieve"]
    assert metadata["ranges"][0] == {"low": 0, "high": 1000, "span": 1000}
    first_commands = metadata["range_commands"][0]
    assert first_commands["circle_timing"] == [
        "target/release/circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--segment-size",
        "131072",
        "--threads",
        "8",
        "--count-mode",
        "segmented",
    ]
    assert first_commands["circle_count_server"] == [
        "target/release/circle-prime",
        "count-server",
    ]
    assert first_commands["primesieve"] == [
        "/opt/bin/primesieve",
        "0",
        "999",
        "--count",
        "--quiet",
        "--threads=4",
    ]
    assert first_commands["primecount_high"] == [
        "/opt/bin/primecount",
        "999",
        "--threads=4",
    ]
    assert "primecount_low" not in first_commands
    assert metadata["range_commands"][1]["primecount_low"] == [
        "/opt/bin/primecount",
        "99",
        "--threads=4",
    ]


def test_external_metadata_records_circle_sweep_commands(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=3,
        segment_size=0,
        segment_sizes="0,98304,131072",
        circle_count_modes="segmented,hybrid-wheel30-mark",
        circle_threads=8,
        external_threads=8,
        require_tool=[],
        include_circle_server=False,
    )

    metadata = build_run_metadata(
        args=args,
        ranges=[(0, 1000), (1000, 2000)],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount=None,
        row_count=8,
    )

    assert metadata["requested_segment_size"] == 0
    assert metadata["include_circle_server"] is False
    assert metadata["requested_segment_sizes"] == [0, 98304, 131072]
    assert metadata["circle_count_modes"] == ["segmented", "hybrid-wheel30-mark"]
    variants = metadata["range_commands"][0]["circle_variants"]
    assert [(variant["segment_size"], variant["count_mode"]) for variant in variants] == [
        (0, "segmented"),
        (0, "hybrid-wheel30-mark"),
        (98304, "segmented"),
        (98304, "hybrid-wheel30-mark"),
        (131072, "segmented"),
        (131072, "hybrid-wheel30-mark"),
    ]
    assert variants[0]["timing"] == [
        "target/release/circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--threads",
        "8",
        "--count-mode",
        "segmented",
    ]
    assert variants[3]["timing"] == [
        "target/release/circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--segment-size",
        "98304",
        "--threads",
        "8",
        "--count-mode",
        "hybrid-wheel30-mark",
    ]


def test_external_metadata_records_exact_circle_variants(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=3,
        segment_size=0,
        segment_sizes=None,
        circle_count_modes="segmented",
        circle_variant=[
            "default:0",
            "segmented:131072,segmented:196608",
            "prefix-pi:0:1",
        ],
        circle_threads=8,
        external_threads=8,
        require_tool=[],
        include_circle_server=False,
    )

    metadata = build_run_metadata(
        args=args,
        ranges=[(0, 1000)],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount=None,
        row_count=8,
    )

    assert metadata["requested_segment_sizes"] == [0, 131072, 196608]
    assert metadata["circle_count_modes"] == ["default", "segmented", "prefix-pi"]
    assert metadata["circle_variants"] == [
        {"segment_size": 0, "count_mode": "default"},
        {"segment_size": 131072, "count_mode": "segmented"},
        {"segment_size": 196608, "count_mode": "segmented"},
        {"segment_size": 0, "count_mode": "prefix-pi", "threads": 1},
    ]
    for command_set in metadata["range_commands"]:
        variants = command_set["circle_variants"]
        assert [
            (variant["segment_size"], variant["count_mode"], variant.get("threads"))
            for variant in variants
        ] == [
            (0, "default", None),
            (131072, "segmented", None),
            (196608, "segmented", None),
            (0, "prefix-pi", 1),
        ]
    variants = metadata["range_commands"][0]["circle_variants"]
    assert variants[0]["timing"] == [
        "target/release/circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--threads",
        "8",
    ]
    assert variants[3]["timing"] == [
        "target/release/circle-prime",
        "range",
        "0",
        "1000",
        "--count",
        "--count-mode",
        "prefix-pi",
    ]


def test_required_external_tools_reports_only_missing_tools() -> None:
    assert required_external_tools_missing(
        ["primesieve", "primecount"],
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
    ) == []
    assert required_external_tools_missing(
        ["primesieve", "primecount", "primesieve"],
        primesieve="/opt/bin/primesieve",
        primecount=None,
    ) == ["primecount"]
    assert required_external_tools_missing(
        ["primesieve", "primecount"],
        primesieve=None,
        primecount=None,
    ) == ["primecount", "primesieve"]


def test_interleaved_measurement_rotates_samples_and_summarizes_rows() -> None:
    calls: list[str] = []

    def runner(name: str, result: int):
        def run_once() -> int:
            calls.append(name)
            return result

        return run_once

    rows, samples = measure_interleaved(
        [
            Measurement(
                name="circle_prime_parallel_segmented_count_8t",
                low=0,
                high=1000,
                segment_size=32768,
                threads=8,
                requested_threads=8,
                run_once=runner("circle", 168),
            ),
            Measurement(
                name="external_primesieve_count",
                low=0,
                high=1000,
                segment_size=0,
                threads=8,
                requested_threads=8,
                run_once=runner("primesieve", 168),
            ),
        ],
        rounds=2,
    )

    assert calls == ["circle", "primesieve", "primesieve", "circle"]
    assert [row.name for row in rows] == [
        "circle_prime_parallel_segmented_count_8t",
        "external_primesieve_count",
    ]
    assert len(samples) == 4
    assert {sample.round_index for sample in samples} == {0, 1}
