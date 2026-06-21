from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from types import SimpleNamespace

from scripts import benchmark_prime_external_next as next_bench
from scripts.benchmark_prime_external_next import (
    NextBenchRow,
    NextMeasurement,
    PrimeLineServerClient,
    build_run_metadata,
    measure_start_interleaved,
    measure_interleaved_next,
    next_server_request_line,
    parse_starts,
    primecount_nth_prime_command,
    primecount_pi_command,
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


def test_primecount_next_commands_use_pi_then_nth_prime() -> None:
    assert primecount_pi_command("primecount", 97, 8) == [
        "primecount",
        "96",
        "--threads=8",
    ]
    assert primecount_pi_command("primecount", 2, 8) is None
    assert primecount_nth_prime_command("primecount", 26, 8) == [
        "primecount",
        "26",
        "--nth-prime",
        "--threads=8",
    ]
    assert primecount_nth_prime_command("primecount", 1, 0) == [
        "primecount",
        "1",
        "--nth-prime",
    ]


def test_prime_line_server_client_batches_repeated_requests() -> None:
    client = PrimeLineServerClient(
        [
            sys.executable,
            "-c",
            (
                "import sys\n"
                "for line in sys.stdin:\n"
                "    parts = line.strip().split()\n"
                "    request = parts[0] if parts else ''\n"
                "    if request in {'quit', 'exit'}:\n"
                "        break\n"
                "    count = int(parts[1]) if len(parts) > 1 else 1\n"
                "    for _ in range(count):\n"
                "        print(int(request) + 1)\n"
                "    sys.stdout.flush()\n"
            ),
        ],
        "test line server",
    )
    try:
        assert client.next_primes(100, 3) == [101, 101, 101]
        assert client.next_prime(40) == 41
        assert client.next_primes(5, 0) == []
    finally:
        client.close()


def test_next_server_request_line_uses_batch_protocol() -> None:
    assert next_server_request_line(100, 1) == "100\n"
    assert next_server_request_line(100, 3) == "100 3\n"


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
    assert rows[0].sample_count == 2


def test_next_interleaved_warmup_is_unrecorded() -> None:
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
    assert len(samples) == 4
    assert rows[0].sample_count == 2
    assert rows[0].sample_stability in {"stable", "noisy"}
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
    assert row.sample_count == 0


def test_measure_start_interleaved_can_include_circle_server(monkeypatch) -> None:
    def measurement(name: str, result: int) -> NextMeasurement:
        return NextMeasurement(
            name=name,
            start=100,
            batch_size=2,
            threads=1,
            requested_threads=1,
            candidate_count=1 if name.startswith("circle_prime") else 0,
            run_once=lambda: result,
        )

    monkeypatch.setattr(
        next_bench,
        "circle_next_measurement",
        lambda circle_prime, start, batch_size: measurement("circle_prime_next_prime", 101),
    )
    monkeypatch.setattr(
        next_bench,
        "circle_next_server_measurement",
        lambda circle_prime, start, batch_size: measurement(
            "circle_prime_server_next_prime", 101
        ),
    )
    monkeypatch.setattr(
        next_bench,
        "primesieve_next_measurement",
        lambda primesieve, start, batch_size, external_threads: measurement(
            "external_primesieve_next_prime", 101
        ),
    )

    rows, samples = measure_start_interleaved(
        circle_prime=Path("circle-prime"),
        primesieve="primesieve",
        primecount=None,
        primesieve_library_server=None,
        start=100,
        batch_size=2,
        external_threads=8,
        rounds=2,
        include_circle_server=True,
    )

    speedup_names = [row.name for row in rows if row.kind == "speedup"]
    assert speedup_names == ["circle_prime_next_prime", "circle_prime_server_next_prime"]
    assert len(samples) == 6


def test_measure_start_interleaved_can_use_primesieve_library_server(monkeypatch) -> None:
    def measurement(name: str, result: int) -> NextMeasurement:
        return NextMeasurement(
            name=name,
            start=100,
            batch_size=2,
            threads=1,
            requested_threads=1,
            candidate_count=1 if name.startswith("circle_prime") else 0,
            run_once=lambda: result,
        )

    monkeypatch.setattr(
        next_bench,
        "circle_next_measurement",
        lambda circle_prime, start, batch_size: measurement("circle_prime_next_prime", 101),
    )
    monkeypatch.setattr(
        next_bench,
        "primesieve_generate_server_measurement",
        lambda server, start, batch_size: measurement(
            "external_primesieve_generate_next_server", 101
        ),
    )

    rows, samples = measure_start_interleaved(
        circle_prime=Path("circle-prime"),
        primesieve=None,
        primecount=None,
        primesieve_library_server=Path("primesieve-next-server"),
        start=100,
        batch_size=2,
        external_threads=8,
        rounds=2,
    )

    assert [row.baseline for row in rows if row.kind == "speedup"] == [
        "external_primesieve_generate_next_server"
    ]
    assert len(samples) == 4


def test_measure_start_interleaved_can_use_primesieve_iterator_server(monkeypatch) -> None:
    def measurement(name: str, result: int) -> NextMeasurement:
        return NextMeasurement(
            name=name,
            start=100,
            batch_size=2,
            threads=1,
            requested_threads=1,
            candidate_count=1 if name.startswith("circle_prime") else 0,
            run_once=lambda: result,
        )

    monkeypatch.setattr(
        next_bench,
        "circle_next_measurement",
        lambda circle_prime, start, batch_size: measurement("circle_prime_next_prime", 101),
    )
    monkeypatch.setattr(
        next_bench,
        "primesieve_iterator_server_measurement",
        lambda server, start, batch_size: measurement(
            "external_primesieve_iterator_next_server", 101
        ),
    )

    rows, samples = measure_start_interleaved(
        circle_prime=Path("circle-prime"),
        primesieve=None,
        primecount=None,
        primesieve_library_server=None,
        primesieve_iterator_server=Path("primesieve-iterator-next-server"),
        start=100,
        batch_size=2,
        external_threads=8,
        rounds=2,
    )

    assert [row.baseline for row in rows if row.kind == "speedup"] == [
        "external_primesieve_iterator_next_server"
    ]
    assert len(samples) == 4


def test_measure_start_interleaved_can_use_primecount_library_server(monkeypatch) -> None:
    def measurement(name: str, result: int) -> NextMeasurement:
        return NextMeasurement(
            name=name,
            start=100,
            batch_size=2,
            threads=1,
            requested_threads=1,
            candidate_count=1 if name.startswith("circle_prime") else 0,
            run_once=lambda: result,
        )

    monkeypatch.setattr(
        next_bench,
        "circle_next_measurement",
        lambda circle_prime, start, batch_size: measurement("circle_prime_next_prime", 101),
    )
    monkeypatch.setattr(
        next_bench,
        "primecount_next_server_measurement",
        lambda server, start, batch_size, external_threads: measurement(
            "external_primecount_next_server", 101
        ),
    )

    rows, samples = measure_start_interleaved(
        circle_prime=Path("circle-prime"),
        primesieve=None,
        primecount=None,
        primesieve_library_server=None,
        primecount_library_server=Path("primecount-next-server"),
        start=100,
        batch_size=2,
        external_threads=8,
        rounds=2,
    )

    assert [row.baseline for row in rows if row.kind == "speedup"] == [
        "external_primecount_next_server"
    ]
    assert len(samples) == 4


def test_measure_start_interleaved_can_skip_cold_cli_rows_for_server_lane(
    monkeypatch,
) -> None:
    def measurement(name: str, result: int) -> NextMeasurement:
        return NextMeasurement(
            name=name,
            start=100,
            batch_size=2,
            threads=1,
            requested_threads=1,
            candidate_count=1 if name.startswith("circle_prime") else 0,
            run_once=lambda: result,
        )

    monkeypatch.setattr(
        next_bench,
        "circle_next_measurement",
        lambda *_: (_ for _ in ()).throw(
            AssertionError("cold Circle next-prime row should be skipped")
        ),
    )
    monkeypatch.setattr(
        next_bench,
        "primesieve_next_measurement",
        lambda *_: (_ for _ in ()).throw(
            AssertionError("cold primesieve next-prime row should be skipped")
        ),
    )
    monkeypatch.setattr(
        next_bench,
        "circle_next_server_measurement",
        lambda circle_prime, start, batch_size: measurement(
            "circle_prime_server_next_prime", 101
        ),
    )
    monkeypatch.setattr(
        next_bench,
        "primesieve_generate_server_measurement",
        lambda server, start, batch_size: measurement(
            "external_primesieve_generate_next_server", 101
        ),
    )

    rows, samples = measure_start_interleaved(
        circle_prime=Path("circle-prime"),
        primesieve="primesieve",
        primecount=None,
        primesieve_library_server=Path("primesieve-next-server"),
        start=100,
        batch_size=2,
        external_threads=8,
        rounds=2,
        include_circle_server=True,
        include_circle_cli=False,
        include_primesieve_cli=False,
    )

    assert [row.name for row in rows if row.kind == "timing"] == [
        "circle_prime_server_next_prime",
        "external_primesieve_generate_next_server",
    ]
    assert [row.baseline for row in rows if row.kind == "speedup"] == [
        "external_primesieve_generate_next_server"
    ]
    assert len(samples) == 4


def test_next_metadata_records_commands_tools_and_fingerprints(
    monkeypatch, tmp_path: Path
) -> None:
    defaults_path = tmp_path / "prime_engine_defaults.json"
    defaults_path.write_text('{"next": true}\n')
    defaults_hash = hashlib.sha256(defaults_path.read_bytes()).hexdigest()
    monkeypatch.setattr(next_bench, "PRIME_ENGINE_DEFAULTS", defaults_path)
    monkeypatch.setattr(
        next_bench,
        "circle_prime_metadata",
        lambda cargo, circle_prime: {
            "available": True,
            "path": str(circle_prime),
            "package_name": "circle-prime",
            "version": "0.1.0",
            "binary": {"sha256": "a" * 64},
            "defaults": {"sha256": defaults_hash},
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
        warmup_rounds=1,
        sample_output=Path("samples.csv"),
        external_threads=8,
        require_tool=[
            "primesieve",
            "primecount",
            "primesieve-library",
            "primesieve-iterator-library",
            "primecount-library",
        ],
        include_circle_server=True,
        server_only=False,
        include_primecount=True,
        include_primecount_library_server=True,
        include_primesieve_library_server=True,
        include_primesieve_iterator_server=True,
        primecount_max_start=1_000_000_000_000,
        primecount_library_max_start=1_000_000_000_000,
        primesieve_library_max_start=2**64 - 1,
    )

    metadata = build_run_metadata(
        args=args,
        starts=[97, 100],
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=Path("target/release/circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        primesieve_library_server=Path("target/prime-controls/primesieve-next-server"),
        primesieve_iterator_server=Path(
            "target/prime-controls/primesieve-iterator-next-server"
        ),
        primecount_library_server=Path("target/prime-controls/primecount-next-server"),
        row_count=6,
    )

    assert metadata["rounds"] == 5
    assert metadata["batch_size"] == 2
    assert metadata["warmup_rounds"] == 1
    assert metadata["server_only"] is False
    assert metadata["include_circle_server"] is True
    assert metadata["include_primecount"] is True
    assert metadata["primecount_max_start"] == 1_000_000_000_000
    assert metadata["include_primecount_library_server"] is True
    assert metadata["primecount_library_max_start"] == 1_000_000_000_000
    assert metadata["include_primesieve_library_server"] is True
    assert metadata["include_primesieve_iterator_server"] is True
    assert metadata["primesieve_library_max_start"] == 2**64 - 1
    assert metadata["row_count"] == 6
    assert metadata["starts"] == [97, 100]
    assert metadata["sample_output"] == "samples.csv"
    assert metadata["circle_prime_defaults"]["sha256"] == defaults_hash
    assert metadata["tools"]["circle_prime"]["binary"]["sha256"] == "a" * 64
    assert metadata["tools"]["circle_prime"]["defaults"]["sha256"] == defaults_hash
    assert metadata["required_external_tools"] == [
        "primecount",
        "primecount-library",
        "primesieve",
        "primesieve-iterator-library",
        "primesieve-library",
    ]
    assert metadata["tools"]["primesieve_library_server"]["available"] is True
    assert metadata["tools"]["primesieve_iterator_server"]["available"] is True
    assert metadata["tools"]["primecount_library_server"]["available"] is True
    assert (
        metadata["tools"]["primesieve_library_server"]["method"]
        == "primesieve_generate_n_primes(1, START, UINT64_PRIMES)"
    )
    assert metadata["tools"]["primesieve_iterator_server"]["method"] == (
        "primesieve::iterator.jump_to(START).next_prime()"
    )
    assert metadata["tools"]["primecount_library_server"]["method"] == (
        "primecount_pi(START-1) then primecount_nth_prime(pi+1)"
    )
    assert metadata["thread_policy"]["external_requested_threads"] == 8
    assert metadata["commands"][0]["circle"] == [
        "target/release/circle-prime",
        "next",
        "97",
    ]
    assert metadata["commands"][0]["circle_server"] == [
        "target/release/circle-prime",
        "next-server",
    ]
    assert metadata["commands"][0]["primesieve"] == [
        "/opt/bin/primesieve",
        "1",
        "96",
        "--nth-prime",
        "--quiet",
        "--threads=8",
    ]
    assert metadata["commands"][0]["primesieve_library_server"] == [
        "target/prime-controls/primesieve-next-server"
    ]
    assert metadata["commands"][0]["primesieve_iterator_server"] == [
        "target/prime-controls/primesieve-iterator-next-server"
    ]
    assert metadata["commands"][0]["primecount_library_server"] == [
        "target/prime-controls/primecount-next-server",
        "8",
    ]
    assert metadata["commands"][0]["primecount_pi"] == [
        "/opt/bin/primecount",
        "96",
        "--threads=8",
    ]
    assert metadata["commands"][0]["primecount_nth_prime"] == [
        "/opt/bin/primecount",
        "pi(START-1)+1",
        "--nth-prime",
        "--threads=8",
    ]
