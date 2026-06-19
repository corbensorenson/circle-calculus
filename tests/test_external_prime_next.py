from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scripts import benchmark_prime_external_next as next_bench
from scripts.benchmark_prime_external_next import (
    NextBenchRow,
    NextMeasurement,
    build_run_metadata,
    measure_interleaved_next,
    parse_starts,
    primesieve_next_command,
    speedup_row,
)


def test_next_starts_parser_preserves_order_and_deduplicates() -> None:
    assert parse_starts("90,1000000,90,4294967000") == [
        90,
        1000000,
        4294967000,
    ]


def test_primesieve_next_command_uses_predecessor_for_inclusive_start() -> None:
    assert primesieve_next_command("primesieve", 97, 8) == [
        "primesieve",
        "1",
        "96",
        "--nth-prime",
        "--quiet",
        "--threads=8",
    ]
    assert primesieve_next_command("primesieve", 2, 0) == [
        "primesieve",
        "1",
        "1",
        "--nth-prime",
        "--quiet",
    ]


def test_next_interleaved_measurement_rotates_and_summarizes_samples() -> None:
    calls: list[str] = []

    def runner(name: str, result: int):
        def run_once() -> int:
            calls.append(name)
            return result

        return run_once

    rows, samples = measure_interleaved_next(
        [
            NextMeasurement(
                name="circle_prime_next_prime",
                start=100,
                batch_size=4,
                threads=1,
                requested_threads=1,
                candidate_count=1,
                run_once=runner("circle", 101),
            ),
            NextMeasurement(
                name="external_primesieve_next_prime",
                start=100,
                batch_size=4,
                threads=8,
                requested_threads=8,
                candidate_count=0,
                run_once=runner("primesieve", 101),
            ),
        ],
        rounds=2,
    )

    assert calls == ["circle", "primesieve", "primesieve", "circle"]
    assert [row.name for row in rows] == [
        "circle_prime_next_prime",
        "external_primesieve_next_prime",
    ]
    assert rows[0].result == 101
    assert rows[0].candidate_count == 1
    assert len(samples) == 4
    assert {sample.round_index for sample in samples} == {0, 1}


def test_next_speedup_row_uses_primesieve_baseline_time() -> None:
    circle = NextBenchRow(
        kind="timing",
        name="circle_prime_next_prime",
        start=100,
        batch_size=4,
        result=101,
        candidate_count=1,
        rounds=3,
        best_ms=2.0,
        median_ms=3.0,
        searches_per_second=2000.0,
        median_searches_per_second=1333.3,
        threads=1,
        requested_threads=1,
        baseline="",
        best_speedup="",
        median_speedup="",
    )
    baseline = NextBenchRow(
        kind="timing",
        name="external_primesieve_next_prime",
        start=100,
        batch_size=4,
        result=101,
        candidate_count=0,
        rounds=3,
        best_ms=8.0,
        median_ms=9.0,
        searches_per_second=500.0,
        median_searches_per_second=444.4,
        threads=8,
        requested_threads=8,
        baseline="",
        best_speedup="",
        median_speedup="",
    )

    row = speedup_row(circle, baseline)

    assert row.kind == "speedup"
    assert row.baseline == "external_primesieve_next_prime"
    assert row.best_speedup == "4.000"
    assert row.median_speedup == "3.000"
    assert row.candidate_count == 1


def test_next_metadata_records_commands_and_tools(monkeypatch) -> None:
    monkeypatch.setattr(
        next_bench,
        "circle_prime_metadata",
        lambda cargo, circle_prime: {
            "available": True,
            "path": str(circle_prime),
            "package_name": "circle-prime",
            "version": "0.1.0",
        },
    )
    monkeypatch.setattr(
        next_bench,
        "external_tool_metadata",
        lambda name, path, version_args: {
            "available": True,
            "path": path,
            "version": "primesieve 12.14",
        },
    )
    args = SimpleNamespace(
        rounds=5,
        batch_size=2,
        sample_output=Path("samples.csv"),
        external_threads=8,
        require_tool=["primesieve"],
    )

    metadata = build_run_metadata(
        args=args,
        starts=[97, 100],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        row_count=6,
    )

    assert metadata["rounds"] == 5
    assert metadata["batch_size"] == 2
    assert metadata["row_count"] == 6
    assert metadata["starts"] == [97, 100]
    assert metadata["sample_output"] == "samples.csv"
    assert metadata["required_external_tools"] == ["primesieve"]
    assert metadata["thread_policy"]["external_requested_threads"] == 8
    assert metadata["commands"][0]["circle"] == [
        "target/release/circle-prime",
        "next",
        "97",
    ]
    assert metadata["commands"][0]["primesieve"] == [
        "/opt/bin/primesieve",
        "1",
        "96",
        "--nth-prime",
        "--quiet",
        "--threads=8",
    ]
