from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import benchmark_prime_external_controls
from scripts.benchmark_prime_external_controls import (
    CircleVariant,
    CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_DEFAULT_LIMIT,
    CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV,
    CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_MAX_LIMIT,
    ExternalBenchRow,
    Measurement,
    any_external_baseline_available,
    build_run_metadata,
    circle_count_server_small_prefix_pi_cache_limit,
    circle_measurement_name,
    count_server_command,
    count_server_request,
    circle_prime_command,
    circle_server_measurement_name,
    external_baseline_enabled,
    external_baseline_selected,
    measure_interleaved,
    median,
    parse_circle_count_modes,
    parse_external_baselines,
    parse_circle_variants,
    parse_segment_size_list,
    primecount_pi_server_measurement,
    primecount_command,
    primesieve_count_server_measurement,
    primesieve_command,
    required_external_tools_missing,
    sample_metric_fields,
    selected_circle_prime_binary,
    selected_circle_prime_count_binary,
    selected_external_baselines_missing,
    small_prefix_pi_cache_profile,
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


def test_count_server_default_command_and_request_use_server_defaults() -> None:
    assert count_server_command(
        Path("circle-prime"),
        default_threads=8,
        default_count_mode="default",
    ) == ["circle-prime", "count-server", "--threads", "8"]
    assert count_server_command(
        Path("circle-prime"),
        default_threads=8,
        warm_prefix_pi_cache=True,
    ) == [
        "circle-prime",
        "count-server",
        "--threads",
        "8",
        "--warm-prefix-pi-cache",
    ]
    assert (
        count_server_request(
            1_000_000_000_000,
            1_000_010_000_000,
            1_310_720,
            8,
            "presieve13",
            use_request_defaults=True,
        )
        == "1000000000000 1000010000000\n"
    )


def test_count_server_small_prefix_cache_limit_env_policy(monkeypatch) -> None:
    monkeypatch.delenv(CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV, raising=False)
    assert (
        circle_count_server_small_prefix_pi_cache_limit()
        == CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_DEFAULT_LIMIT
    )

    monkeypatch.setenv(CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV, "bad")
    assert (
        circle_count_server_small_prefix_pi_cache_limit()
        == CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_DEFAULT_LIMIT
    )

    monkeypatch.setenv(CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV, "-1")
    assert (
        circle_count_server_small_prefix_pi_cache_limit()
        == CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_DEFAULT_LIMIT
    )

    monkeypatch.setenv(CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV, "0")
    assert circle_count_server_small_prefix_pi_cache_limit() == 0

    monkeypatch.setenv(CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV, "2000000000")
    assert circle_count_server_small_prefix_pi_cache_limit() == 2_000_000_000

    monkeypatch.setenv(CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV, "999999999999")
    assert (
        circle_count_server_small_prefix_pi_cache_limit()
        == CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_MAX_LIMIT
    )


def test_small_prefix_cache_profile_estimates_memory() -> None:
    assert small_prefix_pi_cache_profile(1_000_000_000) == {
        "limit": 1_000_000_000,
        "odd_count": 499_999_999,
        "word_count": 7_812_500,
        "estimated_bytes": 93_750_004,
    }
    assert small_prefix_pi_cache_profile(2_000_000_000)["estimated_bytes"] == 187_500_004
    assert small_prefix_pi_cache_profile(3_000_000_000)["estimated_bytes"] == 281_250_004


def test_count_server_explicit_request_keeps_variant_fields() -> None:
    assert count_server_command(Path("circle-prime")) == [
        "circle-prime",
        "count-server",
    ]
    assert (
        count_server_request(
            1_000_000_000_000,
            1_000_010_000_000,
            1_310_720,
            8,
            "presieve13",
        )
        == "1000000000000 1000010000000 1310720 8 presieve13\n"
    )


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


def test_sample_metric_fields_ignore_one_high_outlier_for_stability() -> None:
    metrics = sample_metric_fields([0.001, 0.00101, 0.00102, 0.00103, 0.009])

    assert metrics["sample_count"] == 5
    assert metrics["sample_stability"] == "stable"
    assert metrics["sample_noise_ms"] == "1.030000"
    assert metrics["sample_max_ms"] == "9.000000"
    assert metrics["sample_noise_over_median"] == "1.009804"
    assert metrics["sample_max_over_median"] == "8.823529"
    assert metrics["sample_ignored_single_high_outlier"] == "true"


def test_speedup_row_combines_sample_stability_with_baseline() -> None:
    circle = ExternalBenchRow(
        kind="timing",
        name="circle_prime_parallel_segmented_count_8t",
        low=0,
        high=1000,
        span=1000,
        segment_size=32768,
        result=168,
        rounds=5,
        best_ms=2.0,
        median_ms=3.0,
        rate_per_second=500000.0,
        median_rate_per_second=333333.3,
        threads=8,
        requested_threads=8,
        baseline="",
        best_speedup="",
        median_speedup="",
        count_mode="segmented",
        sample_count=5,
        sample_noise_ms="3.000000",
        sample_max_ms="4.000000",
        sample_noise_over_median="1.000000",
        sample_max_over_median="1.333333",
        sample_ignored_single_high_outlier="true",
        sample_stability="stable",
    )
    baseline = ExternalBenchRow(
        kind="timing",
        name="external_primesieve_count",
        low=0,
        high=1000,
        span=1000,
        segment_size=0,
        result=168,
        rounds=5,
        best_ms=1.0,
        median_ms=6.0,
        rate_per_second=1000000.0,
        median_rate_per_second=166666.7,
        threads=8,
        requested_threads=8,
        baseline="",
        best_speedup="",
        median_speedup="",
        sample_stability="noisy",
    )

    row = speedup_row(circle, baseline)

    assert row.sample_count == 5
    assert row.sample_noise_ms == "3.000000"
    assert row.sample_ignored_single_high_outlier == "true"
    assert row.sample_stability == "noisy"


def test_external_metadata_records_thread_policy_and_commands(monkeypatch) -> None:
    monkeypatch.delenv(CIRCLE_COUNT_SERVER_SMALL_PREFIX_PI_CACHE_LIMIT_ENV, raising=False)
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=5,
        batch_size=3,
        batch_request_profile="shifted",
        batch_shift=1000,
        warmup_rounds=1,
        segment_size=131072,
        circle_threads=8,
        external_threads=4,
        require_tool=["primesieve", "primecount", "primesieve-library"],
        include_circle_server=True,
        circle_server_only=False,
        include_primesieve_count_server=True,
        include_primecount_pi_server=True,
    )

    metadata = build_run_metadata(
        args=args,
        ranges=[(0, 1000), (100, 200)],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        primesieve_count_server=Path("target/prime-controls/primesieve-count-server"),
        primecount_pi_server=Path("target/prime-controls/primecount-pi-server"),
        row_count=6,
    )

    assert metadata["rounds"] == 5
    assert metadata["batch_size"] == 3
    assert metadata["batch_request_profile"] == "shifted"
    assert metadata["batch_shift"] == 1000
    assert metadata["warmup_rounds"] == 1
    assert metadata["row_count"] == 6
    assert metadata["interleaved"] is False
    assert metadata["include_circle_server"] is True
    assert metadata["circle_server_only"] is False
    assert metadata["include_primesieve_count_server"] is True
    assert metadata["include_primecount_pi_server"] is True
    assert metadata["requested_segment_sizes"] == [131072]
    assert metadata["thread_policy"]["circle_requested_threads"] == 8
    assert metadata["thread_policy"]["external_requested_threads"] == 4
    assert metadata["required_external_tools"] == [
        "primecount",
        "primesieve",
        "primesieve-library",
    ]
    assert metadata["tools"]["circle_count_server"] == {
        "available": True,
        "path": "target/release/circle-prime",
        "method": "persistent count-server requests",
        "small_prefix_pi_cache_limit": 2_000_000_000,
        "small_prefix_pi_cache_default_limit": 2_000_000_000,
        "small_prefix_pi_cache_max_limit": 3_000_000_000,
        "small_prefix_pi_cache_limit_env": "CIRCLE_PRIME_SMALL_PREFIX_PI_CACHE_LIMIT",
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
        "small_prefix_pi_cache_warmup_profiles": [],
    }
    assert metadata["tools"]["primesieve_count_server"]["available"] is True
    assert (
        metadata["tools"]["primesieve_count_server"]["method"]
        == "primesieve_count_primes(LOW, HIGH-1)"
    )
    assert metadata["tools"]["primecount_pi_server"]["available"] is True
    assert (
        metadata["tools"]["primecount_pi_server"]["method"]
        == "primecount_pi(HIGH-1)-primecount_pi(LOW-1)"
    )
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
    assert first_commands["circle_variants"][0]["count_server"] == {
        "command": ["target/release/circle-prime", "count-server"],
        "uses_server_defaults": False,
        "request": "0 1000 131072 8 segmented",
    }
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
    assert first_commands["primesieve_count_server"] == [
        "target/prime-controls/primesieve-count-server"
    ]
    assert first_commands["primecount_pi_server"] == [
        "target/prime-controls/primecount-pi-server"
    ]
    assert "primecount_low" not in first_commands
    assert metadata["range_commands"][1]["primecount_low"] == [
        "/opt/bin/primecount",
        "99",
        "--threads=4",
    ]


def test_external_metadata_fingerprints_circle_binary_and_defaults(
    monkeypatch, tmp_path: Path
) -> None:
    defaults_path = tmp_path / "prime_engine_defaults.json"
    defaults_path.write_text('{"parallel_segment_size": 131072}\n')
    circle_prime = tmp_path / "circle-prime"
    circle_prime.write_bytes(b"circle-prime-test-binary")
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "PRIME_ENGINE_DEFAULTS",
        defaults_path,
    )
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=1,
        batch_size=1,
        warmup_rounds=0,
        segment_size=131072,
        circle_threads=8,
        external_threads=8,
        require_tool=[],
        include_circle_server=False,
        circle_server_only=False,
        include_primesieve_count_server=False,
        include_primecount_pi_server=False,
    )

    metadata = build_run_metadata(
        args=args,
        ranges=[(0, 1000)],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=circle_prime,
        primesieve=None,
        primecount=None,
        row_count=1,
    )

    assert metadata["circle_prime_defaults"]["sha256"] == hashlib.sha256(
        defaults_path.read_bytes()
    ).hexdigest()
    binary = metadata["tools"]["circle_prime"]["binary"]
    assert binary["sha256"] == hashlib.sha256(circle_prime.read_bytes()).hexdigest()
    assert metadata["tools"]["circle_prime"]["defaults"]["sha256"] == metadata[
        "circle_prime_defaults"
    ]["sha256"]


def test_circle_binary_overrides_use_selected_files(tmp_path: Path) -> None:
    circle_prime = tmp_path / "circle-prime"
    circle_prime_count = tmp_path / "circle-prime-count"
    circle_prime.write_bytes(b"circle-prime")
    circle_prime_count.write_bytes(b"circle-prime-count")

    assert selected_circle_prime_binary(None, circle_prime) == circle_prime
    assert selected_circle_prime_count_binary(None, circle_prime_count) == circle_prime_count

    with pytest.raises(FileNotFoundError):
        selected_circle_prime_binary(None, tmp_path / "missing-circle-prime")
    with pytest.raises(FileNotFoundError):
        selected_circle_prime_count_binary(None, tmp_path / "missing-circle-prime-count")


def test_external_baseline_selection_filters_metadata_commands(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=3,
        batch_size=2,
        warmup_rounds=0,
        segment_size=0,
        segment_sizes="0",
        circle_count_modes="segmented",
        circle_variant=None,
        circle_threads=8,
        external_threads=4,
        require_tool=[],
        include_circle_server=False,
        circle_server_only=False,
        include_primesieve_count_server=True,
        include_primecount_pi_server=False,
        external_baselines="external_primesieve_count_server",
    )

    metadata = build_run_metadata(
        args=args,
        ranges=[(100, 200)],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        primesieve_count_server=Path("target/prime-controls/primesieve-count-server"),
        primecount_pi_server=Path("target/prime-controls/primecount-pi-server"),
        external_baselines={"external_primesieve_count_server"},
        row_count=2,
    )

    assert metadata["external_baselines"] == ["external_primesieve_count_server"]
    commands = metadata["range_commands"][0]
    assert commands["primesieve_count_server"] == [
        "target/prime-controls/primesieve-count-server"
    ]
    assert "primesieve" not in commands
    assert "primecount_high" not in commands
    assert "primecount_low" not in commands
    assert "primecount_pi_server" not in commands


def test_external_metadata_records_count_server_request_shape(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=3,
        batch_size=1,
        warmup_rounds=0,
        segment_size=0,
        segment_sizes=None,
        circle_count_modes="segmented",
        circle_variant=[
            "default:0",
            "default:131072",
            "presieve13:131072",
            "presieve13:0",
        ],
        circle_threads=8,
        external_threads=8,
        require_tool=[],
        include_circle_server=True,
        circle_server_only=True,
        include_primesieve_count_server=True,
    )

    metadata = build_run_metadata(
        args=args,
        ranges=[(1_000_000_000_000, 1_000_010_000_000)],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        primesieve_count_server=Path("target/prime-controls/primesieve-count-server"),
        row_count=4,
    )

    variants = metadata["range_commands"][0]["circle_variants"]
    assert variants[0]["count_server"] == {
        "command": [
            "target/release/circle-prime",
            "count-server",
            "--threads",
            "8",
        ],
        "uses_server_defaults": True,
        "request": "1000000000000 1000010000000",
    }
    assert variants[1]["count_server"] == {
        "command": [
            "target/release/circle-prime",
            "count-server",
            "--segment-size",
            "131072",
            "--threads",
            "8",
        ],
        "uses_server_defaults": True,
        "request": "1000000000000 1000010000000",
    }
    assert variants[2]["count_server"] == {
        "command": ["target/release/circle-prime", "count-server"],
        "uses_server_defaults": False,
        "request": "1000000000000 1000010000000 131072 8 presieve13",
    }
    assert variants[3]["count_server"] == {
        "command": ["target/release/circle-prime", "count-server"],
        "uses_server_defaults": False,
        "request_template": (
            "1000000000000 1000010000000 <resolved_segment_size> 8 presieve13"
        ),
        "request_resolves_segment_size_from_json_probe": True,
    }


def test_external_metadata_records_circle_sweep_commands(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "circle_prime_package_metadata",
        lambda cargo: {"name": "circle-prime", "version": "0.1.0"},
    )
    args = SimpleNamespace(
        rounds=3,
        batch_size=1,
        segment_size=0,
        segment_sizes="0,98304,131072",
        circle_count_modes="segmented,hybrid-wheel30-mark",
        circle_threads=8,
        external_threads=8,
        require_tool=[],
        include_circle_server=False,
        circle_server_only=False,
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
        batch_size=1,
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
        circle_server_only=False,
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
        primesieve_library=Path("target/prime-controls/primesieve-count-server"),
        primecount_library=Path("target/prime-controls/primecount-pi-server"),
    ) == []
    assert required_external_tools_missing(
        [
            "primesieve",
            "primecount",
            "primesieve",
            "primesieve-library",
            "primecount-library",
        ],
        primesieve="/opt/bin/primesieve",
        primecount=None,
        primesieve_library=None,
        primecount_library=None,
    ) == ["primecount", "primecount-library", "primesieve-library"]
    assert required_external_tools_missing(
        ["primesieve", "primecount", "primesieve-library", "primecount-library"],
        primesieve=None,
        primecount=None,
        primesieve_library=None,
        primecount_library=None,
    ) == ["primecount", "primecount-library", "primesieve", "primesieve-library"]


def test_primesieve_count_server_measurement_uses_half_open_range(monkeypatch) -> None:
    requests: list[tuple[int, int, int]] = []
    closed = False

    class FakePrimeRangeServerClient:
        def __init__(self, command: list[str], label: str) -> None:
            assert command == ["target/prime-controls/primesieve-count-server"]
            assert label == "libprimesieve count helper"

        def count(self, low: int, high: int, threads: int) -> int:
            requests.append((low, high, threads))
            return 168

        def count_many(
            self,
            low: int,
            high: int,
            threads: int,
            repetitions: int,
        ) -> list[int]:
            requests.extend((low, high, threads) for _ in range(repetitions))
            return [168] * repetitions

        def count_shifted_many(
            self,
            low: int,
            high: int,
            threads: int,
            repetitions: int,
            shift: int,
        ) -> list[int]:
            span = high - low
            requests.extend(
                (low + index * shift, low + index * shift + span, threads)
                for index in range(repetitions)
            )
            return [168, 169, 170][:repetitions]

        def close(self) -> None:
            nonlocal closed
            closed = True

    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "PrimeRangeServerClient",
        FakePrimeRangeServerClient,
    )

    measurement = primesieve_count_server_measurement(
        Path("target/prime-controls/primesieve-count-server"),
        10,
        1000,
        8,
    )

    assert measurement.name == "external_primesieve_count_server"
    assert measurement.run_once() == 168
    assert measurement.run_once() == 168
    assert requests == [(10, 1000, 8), (10, 1000, 8)]
    assert measurement.run_batch is not None
    assert measurement.run_batch(3) == 168
    assert requests == [
        (10, 1000, 8),
        (10, 1000, 8),
        (10, 1000, 8),
        (10, 1000, 8),
        (10, 1000, 8),
    ]
    assert measurement.run_shifted_batch is not None
    assert measurement.run_shifted_batch(3, 1000) == 170
    assert requests[-3:] == [
        (10, 1000, 8),
        (1010, 2000, 8),
        (2010, 3000, 8),
    ]
    assert measurement.close is not None
    measurement.close()
    assert closed is True


def test_primecount_pi_server_measurement_uses_half_open_range(monkeypatch) -> None:
    requests: list[tuple[int, int, int]] = []
    closed = False

    class FakePrimeRangeServerClient:
        def __init__(self, command: list[str], label: str) -> None:
            assert command == ["target/prime-controls/primecount-pi-server"]
            assert label == "libprimecount pi helper"

        def count(self, low: int, high: int, threads: int) -> int:
            requests.append((low, high, threads))
            return 168

        def count_many(
            self,
            low: int,
            high: int,
            threads: int,
            repetitions: int,
        ) -> list[int]:
            requests.extend((low, high, threads) for _ in range(repetitions))
            return [168] * repetitions

        def count_shifted_many(
            self,
            low: int,
            high: int,
            threads: int,
            repetitions: int,
            shift: int,
        ) -> list[int]:
            span = high - low
            requests.extend(
                (low + index * shift, low + index * shift + span, threads)
                for index in range(repetitions)
            )
            return [168, 169, 170][:repetitions]

        def close(self) -> None:
            nonlocal closed
            closed = True

    monkeypatch.setattr(
        benchmark_prime_external_controls,
        "PrimeRangeServerClient",
        FakePrimeRangeServerClient,
    )

    measurement = primecount_pi_server_measurement(
        Path("target/prime-controls/primecount-pi-server"),
        10,
        1000,
        8,
    )

    assert measurement.name == "external_primecount_pi_diff_server"
    assert measurement.run_once() == 168
    assert measurement.run_once() == 168
    assert requests == [(10, 1000, 8), (10, 1000, 8)]
    assert measurement.run_batch is not None
    assert measurement.run_batch(3) == 168
    assert requests == [
        (10, 1000, 8),
        (10, 1000, 8),
        (10, 1000, 8),
        (10, 1000, 8),
        (10, 1000, 8),
    ]
    assert measurement.run_shifted_batch is not None
    assert measurement.run_shifted_batch(3, 1000) == 170
    assert requests[-3:] == [
        (10, 1000, 8),
        (1010, 2000, 8),
        (2010, 3000, 8),
    ]
    assert measurement.close is not None
    measurement.close()
    assert closed is True


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


def test_interleaved_measurement_warmups_are_unrecorded() -> None:
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
        warmup_rounds=1,
    )

    assert calls == [
        "circle",
        "primesieve",
        "circle",
        "primesieve",
        "primesieve",
        "circle",
    ]
    assert [row.rounds for row in rows] == [2, 2]
    assert len(samples) == 4
    assert {sample.round_index for sample in samples} == {0, 1}


def test_interleaved_measurement_batches_and_reports_per_request_samples() -> None:
    calls: list[str] = []

    def run_once() -> int:
        calls.append("circle")
        return 168

    rows, samples = measure_interleaved(
        [
            Measurement(
                name="circle_prime_parallel_segmented_count_8t",
                low=0,
                high=1000,
                segment_size=32768,
                threads=8,
                requested_threads=8,
                run_once=run_once,
            )
        ],
        rounds=2,
        batch_size=3,
        warmup_rounds=1,
    )

    assert calls == ["circle"] * 9
    assert len(samples) == 2
    assert rows[0].rounds == 2
    assert rows[0].result == 168
    assert all(sample.result == 168 for sample in samples)


def test_measure_interleaved_shifted_batches_use_shifted_runner() -> None:
    calls: list[tuple[int, int]] = []

    def run_shifted_batch(batch_size: int, shift: int) -> int:
        calls.append((batch_size, shift))
        return 1_000 + (batch_size - 1) * shift

    rows, samples = measure_interleaved(
        [
            Measurement(
                name="circle_prime_server_default_count",
                low=1_000_000,
                high=1_010_000,
                segment_size=131072,
                threads=8,
                requested_threads=8,
                run_once=lambda: 0,
                run_shifted_batch=run_shifted_batch,
                count_mode="segmented",
            )
        ],
        rounds=2,
        batch_size=3,
        batch_request_profile="shifted",
        batch_shift=10_000,
    )

    assert calls == [(3, 10_000), (3, 10_000)]
    assert rows[0].result == 21_000
    assert [sample.result for sample in samples] == [21_000, 21_000]


def test_measure_interleaved_shifted_batches_default_to_span_shift() -> None:
    shifts: list[int] = []

    rows, _ = measure_interleaved(
        [
            Measurement(
                name="external_primesieve_count_server",
                low=100,
                high=150,
                segment_size=0,
                threads=8,
                requested_threads=8,
                run_once=lambda: 0,
                run_shifted_batch=lambda batch_size, shift: shifts.append(shift) or 7,
            )
        ],
        rounds=1,
        batch_size=2,
        batch_request_profile="shifted",
    )

    assert shifts == [50]
    assert rows[0].result == 7


def test_measure_interleaved_shifted_requires_shifted_runner() -> None:
    measurement = Measurement(
        name="external_primesieve_count",
        low=100,
        high=150,
        segment_size=0,
        threads=8,
        requested_threads=8,
        run_once=lambda: 7,
    )

    with pytest.raises(ValueError, match="does not support shifted batch"):
        measure_interleaved(
            [measurement],
            rounds=1,
            batch_size=2,
            batch_request_profile="shifted",
        )


def test_parse_external_baselines_validates_and_deduplicates() -> None:
    assert parse_external_baselines(None) is None
    assert parse_external_baselines(
        "external_primesieve_count_server, external_primesieve_count_server"
    ) == {"external_primesieve_count_server"}
    assert parse_external_baselines(
        "external_primesieve_count,external_primecount_pi_diff"
    ) == {"external_primesieve_count", "external_primecount_pi_diff"}
    assert parse_external_baselines(
        "external_primecount_pi_diff_server,external_primesieve_count_server"
    ) == {"external_primecount_pi_diff_server", "external_primesieve_count_server"}

    with pytest.raises(argparse.ArgumentTypeError):
        parse_external_baselines("external_unknown")


def test_external_baseline_availability_helpers_are_explicit() -> None:
    selected = {
        "external_primecount_pi_diff",
        "external_primecount_pi_diff_server",
        "external_primesieve_count_server",
    }

    assert selected_external_baselines_missing(
        selected,
        primesieve="/opt/bin/primesieve",
        primecount=None,
        primesieve_library=None,
        primecount_library=None,
    ) == [
        "external_primecount_pi_diff",
        "external_primecount_pi_diff_server",
        "external_primesieve_count_server",
    ]
    assert any_external_baseline_available(
        {"external_primesieve_count"},
        primesieve="/opt/bin/primesieve",
        primecount=None,
        primesieve_library=None,
        primecount_library=None,
    )
    assert not any_external_baseline_available(
        {"external_primesieve_count_server"},
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        primesieve_library=None,
        primecount_library=None,
    )
    assert any_external_baseline_available(
        {"external_primecount_pi_diff_server"},
        primesieve=None,
        primecount=None,
        primesieve_library=None,
        primecount_library=Path("target/prime-controls/primecount-pi-server"),
    )
    assert external_baseline_enabled(None, "external_primesieve_count")
    assert not external_baseline_selected(None, "external_primecount_pi_diff_server")
    assert external_baseline_selected(
        {"external_primecount_pi_diff_server"},
        "external_primecount_pi_diff_server",
    )
    assert not external_baseline_enabled(
        {"external_primesieve_count_server"},
        "external_primesieve_count",
    )
