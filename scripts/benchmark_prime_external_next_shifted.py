from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.benchmark_prime_external_controls import (
    PRIME_ENGINE_DEFAULTS,
    ROOT,
    build_circle_prime,
    circle_prime_metadata,
    external_tool_metadata,
    file_fingerprint,
    median,
    require_cargo,
    rotated,
    sample_metric_fields,
    utc_now,
)
from scripts.benchmark_prime_external_next import (
    PRIMECOUNT_NEXT_SERVER_SOURCE,
    PRIMESIEVE_ITERATOR_NEXT_SERVER_SOURCE,
    PRIMESIEVE_NEXT_SERVER_SOURCE,
    NextBenchRow,
    NextBenchSample,
    NextServerClient,
    PrimeLineServerClient,
    build_primecount_next_server,
    build_primesieve_iterator_next_server,
    build_primesieve_next_server,
    emit_csv,
    emit_metadata,
    emit_samples,
    next_speedup_sample_metric_fields,
    parse_starts,
    speedup_row,
)


DEFAULT_STARTS = "90,1000000,4294967000,1000000000000"
U64_MAX = 2**64 - 1


@dataclass(frozen=True)
class ShiftedNextMeasurement:
    name: str
    start: int
    batch_size: int
    batch_shift: int
    threads: int
    requested_threads: int
    candidate_count: int
    run_shifted: Callable[[int], list[int]]
    close: Callable[[], None] | None = None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark hot Circle next-server searches against hot external "
            "next-prime controls using fresh shifted starts inside each timed batch."
        )
    )
    parser.add_argument("--starts", default=DEFAULT_STARTS)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--batch-shift", type=int, default=4096)
    parser.add_argument("--warmup-rounds", type=int, default=1)
    parser.add_argument(
        "--external-threads",
        type=int,
        default=0,
        help="Thread count for libprimecount when that optional helper is enabled.",
    )
    parser.add_argument(
        "--include-primesieve-library-server",
        action="store_true",
        help="Benchmark the persistent libprimesieve generate_n_primes helper.",
    )
    parser.add_argument(
        "--include-primesieve-iterator-server",
        action="store_true",
        help="Benchmark the persistent libprimesieve iterator helper.",
    )
    parser.add_argument(
        "--include-primecount-library-server",
        action="store_true",
        help="Benchmark the persistent libprimecount pi+nth-prime helper.",
    )
    parser.add_argument(
        "--primecount-library-max-start",
        type=int,
        default=1_000_000_000,
        help="Largest shifted START eligible for the optional libprimecount helper.",
    )
    parser.add_argument(
        "--primesieve-library-max-start",
        type=int,
        default=U64_MAX,
        help="Largest shifted START eligible for optional libprimesieve helpers.",
    )
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--cxx", default="c++")
    parser.add_argument("--primesieve-include-dir", type=Path)
    parser.add_argument("--primesieve-lib-dir", type=Path)
    parser.add_argument("--primecount-include-dir", type=Path)
    parser.add_argument("--primecount-lib-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sample-output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument(
        "--require-tool",
        choices=(
            "primesieve-library",
            "primesieve-iterator-library",
            "primecount-library",
        ),
        action="append",
        default=[],
        help="Fail if the named external shifted next-prime control is unavailable.",
    )
    args = parser.parse_args()

    validate_args(parser, args)
    starts = parse_starts(args.starts)
    validate_shifted_start_space(
        starts,
        batch_size=args.batch_size,
        batch_shift=args.batch_shift,
        sample_passes=args.rounds + args.warmup_rounds,
    )
    started_at_utc = utc_now()
    primesieve = shutil.which("primesieve")
    primecount = shutil.which("primecount")

    include_primesieve_library_server = (
        args.include_primesieve_library_server
        or "primesieve-library" in args.require_tool
    )
    include_primesieve_iterator_server = (
        args.include_primesieve_iterator_server
        or "primesieve-iterator-library" in args.require_tool
    )
    include_primecount_library_server = (
        args.include_primecount_library_server
        or "primecount-library" in args.require_tool
    )

    primesieve_library_server, primesieve_library_error = optional_build(
        include_primesieve_library_server,
        "primesieve-library",
        args.require_tool,
        lambda: build_primesieve_next_server(args),
    )
    primesieve_iterator_server, primesieve_iterator_error = optional_build(
        include_primesieve_iterator_server,
        "primesieve-iterator-library",
        args.require_tool,
        lambda: build_primesieve_iterator_next_server(args),
    )
    primecount_library_server, primecount_library_error = optional_build(
        include_primecount_library_server,
        "primecount-library",
        args.require_tool,
        lambda: build_primecount_next_server(args),
    )

    missing_required = [
        tool
        for tool, path in [
            ("primesieve-library", primesieve_library_server),
            ("primesieve-iterator-library", primesieve_iterator_server),
            ("primecount-library", primecount_library_server),
        ]
        if tool in args.require_tool and path is None
    ]
    if missing_required:
        emit_metadata(
            build_run_metadata(
                args=args,
                starts=starts,
                started_at_utc=started_at_utc,
                cargo=None,
                circle_prime=None,
                primesieve=primesieve,
                primecount=primecount,
                primesieve_library_server=primesieve_library_server,
                primesieve_iterator_server=primesieve_iterator_server,
                primecount_library_server=primecount_library_server,
                primesieve_library_error=primesieve_library_error,
                primesieve_iterator_error=primesieve_iterator_error,
                primecount_library_error=primecount_library_error,
                row_count=0,
            ),
            args.metadata_output,
        )
        raise RuntimeError(
            "required shifted next-prime control unavailable: "
            + ", ".join(missing_required)
        )

    if (
        primesieve_library_server is None
        and primesieve_iterator_server is None
        and primecount_library_server is None
    ):
        emit_metadata(
            build_run_metadata(
                args=args,
                starts=starts,
                started_at_utc=started_at_utc,
                cargo=None,
                circle_prime=None,
                primesieve=primesieve,
                primecount=primecount,
                primesieve_library_server=None,
                primesieve_iterator_server=None,
                primecount_library_server=None,
                primesieve_library_error=primesieve_library_error,
                primesieve_iterator_error=primesieve_iterator_error,
                primecount_library_error=primecount_library_error,
                row_count=0,
            ),
            args.metadata_output,
        )
        print(
            "no shifted next-prime external controls available; install libprimesieve "
            "or libprimecount helpers",
            file=sys.stderr,
        )
        return 0

    cargo = require_cargo()
    circle_prime = build_circle_prime(cargo)
    rows: list[NextBenchRow] = []
    samples: list[NextBenchSample] = []
    for start in starts:
        start_rows, start_samples = measure_shifted_start_interleaved(
            circle_prime=circle_prime,
            primesieve_library_server=primesieve_library_server,
            primesieve_iterator_server=primesieve_iterator_server,
            primecount_library_server=primecount_library_server,
            start=start,
            batch_size=args.batch_size,
            batch_shift=args.batch_shift,
            rounds=args.rounds,
            warmup_rounds=args.warmup_rounds,
            external_threads=args.external_threads,
            primesieve_library_max_start=args.primesieve_library_max_start,
            primecount_library_max_start=args.primecount_library_max_start,
        )
        rows.extend(start_rows)
        samples.extend(start_samples)

    emit_csv(rows, args.output)
    emit_samples(samples, args.sample_output)
    emit_metadata(
        build_run_metadata(
            args=args,
            starts=starts,
            started_at_utc=started_at_utc,
            cargo=cargo,
            circle_prime=circle_prime,
            primesieve=primesieve,
            primecount=primecount,
            primesieve_library_server=primesieve_library_server,
            primesieve_iterator_server=primesieve_iterator_server,
            primecount_library_server=primecount_library_server,
            primesieve_library_error=primesieve_library_error,
            primesieve_iterator_error=primesieve_iterator_error,
            primecount_library_error=primecount_library_error,
            row_count=len(rows),
        ),
        args.metadata_output,
    )
    return 0


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.rounds <= 0:
        parser.error("--rounds must be positive")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if args.batch_shift <= 0:
        parser.error("--batch-shift must be positive for fresh shifted starts")
    if args.warmup_rounds < 0:
        parser.error("--warmup-rounds must be nonnegative")
    if args.external_threads < 0:
        parser.error("--external-threads must be nonnegative")
    if args.primecount_library_max_start < 0:
        parser.error("--primecount-library-max-start must be nonnegative")
    if args.primesieve_library_max_start < 0:
        parser.error("--primesieve-library-max-start must be nonnegative")


def optional_build(
    enabled: bool,
    label: str,
    required_tools: list[str],
    builder: Callable[[], Path],
) -> tuple[Path | None, str | None]:
    if not enabled:
        return None, None
    try:
        return builder(), None
    except Exception as exc:
        error = str(exc)
        if label not in required_tools:
            print(f"skipping {label} shifted next-prime helper: {error}", file=sys.stderr)
        return None, error


def measure_shifted_start_interleaved(
    *,
    circle_prime: Path,
    primesieve_library_server: Path | None,
    primesieve_iterator_server: Path | None,
    primecount_library_server: Path | None,
    start: int,
    batch_size: int,
    batch_shift: int,
    rounds: int,
    warmup_rounds: int,
    external_threads: int,
    primesieve_library_max_start: int,
    primecount_library_max_start: int,
) -> tuple[list[NextBenchRow], list[NextBenchSample]]:
    measurements: list[ShiftedNextMeasurement] = [
        circle_shifted_next_measurement(circle_prime, start, batch_size, batch_shift)
    ]
    max_shifted = max_shifted_start(
        start,
        batch_size=batch_size,
        batch_shift=batch_shift,
        sample_passes=rounds + warmup_rounds,
    )
    if primesieve_library_server is not None and max_shifted <= primesieve_library_max_start:
        measurements.append(
            primesieve_generate_shifted_measurement(
                primesieve_library_server,
                start,
                batch_size,
                batch_shift,
            )
        )
    if primesieve_iterator_server is not None and max_shifted <= primesieve_library_max_start:
        measurements.append(
            primesieve_iterator_shifted_measurement(
                primesieve_iterator_server,
                start,
                batch_size,
                batch_shift,
            )
        )
    if primecount_library_server is not None and max_shifted <= primecount_library_max_start:
        measurements.append(
            primecount_shifted_measurement(
                primecount_library_server,
                start,
                batch_size,
                batch_shift,
                external_threads,
            )
        )
    if not any(measurement.name.startswith("external_") for measurement in measurements):
        raise ValueError(f"no external shifted next-prime control selected for start={start}")
    try:
        timing_rows, samples = measure_interleaved_shifted_next(
            measurements,
            rounds=rounds,
            warmup_rounds=warmup_rounds,
        )
    finally:
        for measurement in measurements:
            if measurement.close is not None:
                measurement.close()

    baseline_rows = [row for row in timing_rows if row.name.startswith("external_")]
    circle_rows = [row for row in timing_rows if not row.name.startswith("external_")]
    rows: list[NextBenchRow] = []
    rows.extend(circle_rows)
    rows.extend(baseline_rows)
    for circle_row in circle_rows:
        for baseline_row in baseline_rows:
            if circle_row.result != baseline_row.result:
                raise AssertionError(
                    f"{baseline_row.name} shifted next-prime checksum mismatch "
                    f"for start={circle_row.start}: Circle {circle_row.result}, "
                    f"baseline {baseline_row.result}"
                )
            rows.append(shifted_speedup_row(circle_row, baseline_row))
    return rows, samples


def circle_shifted_next_measurement(
    binary: Path,
    start: int,
    batch_size: int,
    batch_shift: int,
) -> ShiftedNextMeasurement:
    client = NextServerClient(binary)

    def run_shifted(batch_start: int) -> list[int]:
        return client.next_primes_shifted(batch_start, batch_size, batch_shift)

    return ShiftedNextMeasurement(
        name="circle_prime_server_shifted_next_prime",
        start=start,
        batch_size=batch_size,
        batch_shift=batch_shift,
        threads=1,
        requested_threads=1,
        candidate_count=0,
        run_shifted=run_shifted,
        close=client.close,
    )


def primesieve_generate_shifted_measurement(
    binary: Path,
    start: int,
    batch_size: int,
    batch_shift: int,
) -> ShiftedNextMeasurement:
    client = PrimeLineServerClient([str(binary)], "libprimesieve shifted generate helper")

    def run_shifted(batch_start: int) -> list[int]:
        return client.next_primes_shifted(batch_start, batch_size, batch_shift)

    return ShiftedNextMeasurement(
        name="external_primesieve_generate_shifted_next_server",
        start=start,
        batch_size=batch_size,
        batch_shift=batch_shift,
        threads=1,
        requested_threads=1,
        candidate_count=0,
        run_shifted=run_shifted,
        close=client.close,
    )


def primesieve_iterator_shifted_measurement(
    binary: Path,
    start: int,
    batch_size: int,
    batch_shift: int,
) -> ShiftedNextMeasurement:
    client = PrimeLineServerClient([str(binary)], "libprimesieve shifted iterator helper")

    def run_shifted(batch_start: int) -> list[int]:
        return client.next_primes_shifted(batch_start, batch_size, batch_shift)

    return ShiftedNextMeasurement(
        name="external_primesieve_iterator_shifted_next_server",
        start=start,
        batch_size=batch_size,
        batch_shift=batch_shift,
        threads=1,
        requested_threads=1,
        candidate_count=0,
        run_shifted=run_shifted,
        close=client.close,
    )


def primecount_shifted_measurement(
    binary: Path,
    start: int,
    batch_size: int,
    batch_shift: int,
    threads: int,
) -> ShiftedNextMeasurement:
    command = [str(binary)]
    if threads > 0:
        command.append(str(threads))
    client = PrimeLineServerClient(command, "libprimecount shifted pi+nth-prime helper")

    def run_shifted(batch_start: int) -> list[int]:
        return client.next_primes_shifted(batch_start, batch_size, batch_shift)

    return ShiftedNextMeasurement(
        name="external_primecount_shifted_next_server",
        start=start,
        batch_size=batch_size,
        batch_shift=batch_shift,
        threads=threads,
        requested_threads=threads,
        candidate_count=0,
        run_shifted=run_shifted,
        close=client.close,
    )


def measure_interleaved_shifted_next(
    measurements: list[ShiftedNextMeasurement],
    *,
    rounds: int,
    warmup_rounds: int,
) -> tuple[list[NextBenchRow], list[NextBenchSample]]:
    timings: dict[str, list[float]] = {measurement_key(m): [] for m in measurements}
    first_timed_results: dict[str, int] = {}
    samples: list[NextBenchSample] = []
    total_passes = warmup_rounds + rounds
    for pass_index in range(total_passes):
        timed = pass_index >= warmup_rounds
        round_index = pass_index - warmup_rounds
        expected_primes: tuple[int, ...] | None = None
        for measurement in rotated(measurements, pass_index):
            batch_start = shifted_batch_start(
                measurement.start,
                batch_size=measurement.batch_size,
                batch_shift=measurement.batch_shift,
                sample_index=pass_index,
            )
            sample_start = time.perf_counter()
            primes = tuple(measurement.run_shifted(batch_start))
            elapsed = time.perf_counter() - sample_start
            if len(primes) != measurement.batch_size:
                raise AssertionError(
                    f"{measurement.name} returned {len(primes)} shifted primes, "
                    f"expected {measurement.batch_size}"
                )
            if expected_primes is None:
                expected_primes = primes
            elif primes != expected_primes:
                raise AssertionError(
                    f"{measurement.name} disagreed on shifted next-prime batch "
                    f"for base start={measurement.start}, pass={pass_index}"
                )
            if timed:
                key = measurement_key(measurement)
                result = result_checksum(primes)
                first_timed_results.setdefault(key, result)
                timings[key].append(elapsed)
                samples.append(sample_row(measurement, result, round_index, elapsed))

    rows = []
    for measurement in measurements:
        key = measurement_key(measurement)
        rows.append(
            timing_row_from_samples(
                measurement,
                first_timed_results[key],
                rounds=rounds,
                timings=timings[key],
            )
        )
    return rows, samples


def shifted_batch_start(
    start: int,
    *,
    batch_size: int,
    batch_shift: int,
    sample_index: int,
) -> int:
    shifted = start + sample_index * batch_size * batch_shift
    if shifted > U64_MAX:
        raise ValueError(f"shifted START overflowed u64 for base start={start}")
    return shifted


def max_shifted_start(
    start: int,
    *,
    batch_size: int,
    batch_shift: int,
    sample_passes: int,
) -> int:
    max_index = sample_passes * batch_size - 1
    if max_index < 0:
        return start
    return start + max_index * batch_shift


def validate_shifted_start_space(
    starts: list[int],
    *,
    batch_size: int,
    batch_shift: int,
    sample_passes: int,
) -> None:
    for start in starts:
        if max_shifted_start(
            start,
            batch_size=batch_size,
            batch_shift=batch_shift,
            sample_passes=sample_passes,
        ) > U64_MAX:
            raise ValueError(
                f"shifted START range overflows u64 for base start={start}; "
                "lower --batch-size, --batch-shift, --rounds, or --warmup-rounds"
            )


def result_checksum(primes: tuple[int, ...]) -> int:
    encoded = ",".join(str(prime) for prime in primes).encode("ascii")
    digest = hashlib.sha256(encoded).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def measurement_key(measurement: ShiftedNextMeasurement) -> str:
    return (
        f"{measurement.name}:{measurement.start}:{measurement.batch_size}:"
        f"{measurement.batch_shift}:{measurement.threads}:{measurement.requested_threads}"
    )


def sample_row(
    measurement: ShiftedNextMeasurement,
    result: int,
    round_index: int,
    elapsed_seconds: float,
) -> NextBenchSample:
    return NextBenchSample(
        kind="sample",
        name=measurement.name,
        start=measurement.start,
        batch_size=measurement.batch_size,
        result=result,
        candidate_count=measurement.candidate_count,
        round_index=round_index,
        elapsed_ms=elapsed_seconds * 1000.0,
        threads=measurement.threads,
        requested_threads=measurement.requested_threads,
    )


def timing_row_from_samples(
    measurement: ShiftedNextMeasurement,
    result: int,
    *,
    rounds: int,
    timings: list[float],
) -> NextBenchRow:
    best_seconds = min(timings)
    median_seconds = median(timings)
    return NextBenchRow(
        kind="timing",
        name=measurement.name,
        start=measurement.start,
        batch_size=measurement.batch_size,
        result=result,
        candidate_count=measurement.candidate_count,
        rounds=rounds,
        best_ms=best_seconds * 1000.0,
        median_ms=median_seconds * 1000.0,
        searches_per_second=(
            measurement.batch_size / best_seconds if best_seconds > 0 else float("inf")
        ),
        median_searches_per_second=(
            measurement.batch_size / median_seconds if median_seconds > 0 else float("inf")
        ),
        threads=measurement.threads,
        requested_threads=measurement.requested_threads,
        baseline="",
        best_speedup="",
        median_speedup="",
        **sample_metric_fields(timings),
    )


def shifted_speedup_row(circle_row: NextBenchRow, baseline: NextBenchRow) -> NextBenchRow:
    row = speedup_row(circle_row, baseline)
    return NextBenchRow(
        **{
            **asdict(row),
            **next_speedup_sample_metric_fields(circle_row, baseline),
        }
    )


def build_run_metadata(
    *,
    args: argparse.Namespace,
    starts: list[int],
    started_at_utc: str,
    cargo: str | None,
    circle_prime: Path | None,
    primesieve: str | None,
    primecount: str | None,
    primesieve_library_server: Path | None,
    primesieve_iterator_server: Path | None,
    primecount_library_server: Path | None,
    primesieve_library_error: str | None,
    primesieve_iterator_error: str | None,
    primecount_library_error: str | None,
    row_count: int,
) -> dict[str, Any]:
    circle_binary = circle_prime or ROOT / "target" / "release" / "circle-prime"
    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": utc_now(),
        "row_count": row_count,
        "rounds": args.rounds,
        "batch_size": args.batch_size,
        "batch_request_profile": "shifted",
        "batch_shift": args.batch_shift,
        "warmup_rounds": args.warmup_rounds,
        "server_only": True,
        "include_circle_server": True,
        "include_primesieve_library_server": bool(
            args.include_primesieve_library_server
            or "primesieve-library" in args.require_tool
        ),
        "include_primesieve_iterator_server": bool(
            args.include_primesieve_iterator_server
            or "primesieve-iterator-library" in args.require_tool
        ),
        "include_primecount_library_server": bool(
            args.include_primecount_library_server
            or "primecount-library" in args.require_tool
        ),
        "primecount_library_max_start": args.primecount_library_max_start,
        "primesieve_library_max_start": args.primesieve_library_max_start,
        "starts": starts,
        "sample_output": str(args.sample_output) if args.sample_output is not None else None,
        "circle_prime_defaults": file_fingerprint(PRIME_ENGINE_DEFAULTS),
        "thread_policy": {
            "circle_requested_threads": 1,
            "external_requested_threads": args.external_threads,
            "external_default_threads_when_zero": "tool default/all available CPU cores",
        },
        "required_external_tools": sorted(set(args.require_tool)),
        "tools": {
            "circle_prime": circle_prime_metadata(cargo, circle_prime),
            "primesieve": external_tool_metadata("primesieve", primesieve, ["--version"]),
            "primecount": external_tool_metadata("primecount", primecount, ["--version"]),
            "primesieve_library_server": {
                "available": primesieve_library_server is not None,
                "path": (
                    str(primesieve_library_server)
                    if primesieve_library_server is not None
                    else None
                ),
                "binary": file_fingerprint(primesieve_library_server),
                "source": str(PRIMESIEVE_NEXT_SERVER_SOURCE),
                "source_fingerprint": file_fingerprint(PRIMESIEVE_NEXT_SERVER_SOURCE),
                "method": (
                    "shifted COUNT SHIFT START requests using "
                    "primesieve_generate_n_primes(1, START, UINT64_PRIMES)"
                ),
                "error": primesieve_library_error,
            },
            "primesieve_iterator_server": {
                "available": primesieve_iterator_server is not None,
                "path": (
                    str(primesieve_iterator_server)
                    if primesieve_iterator_server is not None
                    else None
                ),
                "binary": file_fingerprint(primesieve_iterator_server),
                "source": str(PRIMESIEVE_ITERATOR_NEXT_SERVER_SOURCE),
                "source_fingerprint": file_fingerprint(PRIMESIEVE_ITERATOR_NEXT_SERVER_SOURCE),
                "method": (
                    "shifted COUNT SHIFT START requests using "
                    "primesieve::iterator.jump_to(START).next_prime()"
                ),
                "error": primesieve_iterator_error,
            },
            "primecount_library_server": {
                "available": primecount_library_server is not None,
                "path": (
                    str(primecount_library_server)
                    if primecount_library_server is not None
                    else None
                ),
                "binary": file_fingerprint(primecount_library_server),
                "source": str(PRIMECOUNT_NEXT_SERVER_SOURCE),
                "source_fingerprint": file_fingerprint(PRIMECOUNT_NEXT_SERVER_SOURCE),
                "method": (
                    "shifted COUNT SHIFT START requests using "
                    "primecount_pi(START-1) then primecount_nth_prime(pi+1)"
                ),
                "error": primecount_library_error,
            },
        },
        "commands": [
            {
                "start": start,
                "max_shifted_start": max_shifted_start(
                    start,
                    batch_size=args.batch_size,
                    batch_shift=args.batch_shift,
                    sample_passes=args.rounds + args.warmup_rounds,
                ),
                "request_template": (
                    f"shifted {args.batch_size} {args.batch_shift} SHIFTED_START"
                ),
                "circle_server": [str(circle_binary), "next-server"],
                "primesieve_library_server": (
                    [str(primesieve_library_server)]
                    if primesieve_library_server is not None
                    else None
                ),
                "primesieve_iterator_server": (
                    [str(primesieve_iterator_server)]
                    if primesieve_iterator_server is not None
                    else None
                ),
                "primecount_library_server": (
                    [str(primecount_library_server)]
                    + (
                        [str(args.external_threads)]
                        if args.external_threads > 0
                        else []
                    )
                    if primecount_library_server is not None
                    else None
                ),
            }
            for start in starts
        ],
    }


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"shifted external next-prime benchmark failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
