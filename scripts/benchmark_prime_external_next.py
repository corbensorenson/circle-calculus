from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.benchmark_prime_external_controls import (
    ROOT,
    build_circle_prime,
    circle_prime_metadata,
    external_tool_metadata,
    median,
    parse_integer_output,
    require_cargo,
    rotated,
    sample_metric_fields,
    utc_now,
)


DEFAULT_STARTS = "90,1000000,4294967000,1000000000000,18446744073709551500"
PRIMESIEVE_NEXT_SERVER_SOURCE = (
    ROOT / "sidecars" / "PRIME_ENGINE" / "controls" / "primesieve_next_server.c"
)
PRIMESIEVE_NEXT_SERVER_BINARY = ROOT / "target" / "prime-controls" / "primesieve-next-server"


@dataclass(frozen=True)
class NextBenchRow:
    kind: str
    name: str
    start: int
    batch_size: int
    result: int
    candidate_count: int
    rounds: int
    best_ms: float
    median_ms: float
    searches_per_second: float
    median_searches_per_second: float
    threads: int
    requested_threads: int
    baseline: str
    best_speedup: str
    median_speedup: str
    sample_count: int = 0
    sample_noise_ms: str = ""
    sample_max_ms: str = ""
    sample_noise_over_median: str = ""
    sample_max_over_median: str = ""
    sample_ignored_single_high_outlier: str = ""
    sample_stability: str = ""


@dataclass(frozen=True)
class NextBenchSample:
    kind: str
    name: str
    start: int
    batch_size: int
    result: int
    candidate_count: int
    round_index: int
    elapsed_ms: float
    threads: int
    requested_threads: int


@dataclass(frozen=True)
class NextMeasurement:
    name: str
    start: int
    batch_size: int
    threads: int
    requested_threads: int
    candidate_count: int
    run_once: Callable[[], int]
    close: Callable[[], None] | None = None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark Circle next-prime search against external next-prime controls."
        )
    )
    parser.add_argument("--starts", default=DEFAULT_STARTS)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help=(
            "Repeat each next-prime query inside one timing sample. Keep this "
            "small for high-u64 starts because primesieve can spend real time there."
        ),
    )
    parser.add_argument(
        "--external-threads",
        type=int,
        default=0,
        help=(
            "Thread count for external controls. Use 0 for the tool default/all cores "
            "where supported."
        ),
    )
    parser.add_argument(
        "--include-primecount",
        action="store_true",
        help=(
            "Also benchmark primecount as pi(START-1) followed by --nth-prime. "
            "This is capped by --primecount-max-start because near-u64 pi(x) is "
            "not a short-run next-prime control."
        ),
    )
    parser.add_argument(
        "--primecount-max-start",
        type=int,
        default=1_000_000_000_000,
        help="Largest START value eligible for the optional primecount next-prime control.",
    )
    parser.add_argument(
        "--include-primesieve-library-server",
        action="store_true",
        help=(
            "Also benchmark a persistent repo helper linked against libprimesieve "
            "and using primesieve_generate_n_primes(1, START)."
        ),
    )
    parser.add_argument(
        "--primesieve-library-max-start",
        type=int,
        default=2**64 - 1,
        help=(
            "Largest START value eligible for the optional libprimesieve helper. "
            "Lower this if near-u64 library probes are too slow for a quick run."
        ),
    )
    parser.add_argument(
        "--cc",
        default="cc",
        help="C compiler used to build the optional libprimesieve helper.",
    )
    parser.add_argument(
        "--primesieve-include-dir",
        type=Path,
        help="Optional include directory containing primesieve.h.",
    )
    parser.add_argument(
        "--primesieve-lib-dir",
        type=Path,
        help="Optional library directory containing libprimesieve.",
    )
    parser.add_argument(
        "--include-circle-server",
        action="store_true",
        help="Also benchmark persistent circle-prime next-server requests.",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sample-output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument(
        "--require-tool",
        choices=("primesieve", "primecount", "primesieve-library"),
        action="append",
        default=[],
        help="Fail if the named external next-prime control is unavailable.",
    )
    args = parser.parse_args()

    if args.rounds <= 0:
        parser.error("--rounds must be positive")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if args.external_threads < 0:
        parser.error("--external-threads must be nonnegative")
    if args.primecount_max_start < 0:
        parser.error("--primecount-max-start must be nonnegative")
    if args.primesieve_library_max_start < 0:
        parser.error("--primesieve-library-max-start must be nonnegative")

    starts = parse_starts(args.starts)
    started_at_utc = utc_now()
    primesieve = shutil.which("primesieve")
    include_primecount = args.include_primecount or "primecount" in args.require_tool
    primecount = shutil.which("primecount") if include_primecount else None
    include_primesieve_library_server = (
        args.include_primesieve_library_server
        or "primesieve-library" in args.require_tool
    )
    primesieve_library_server: Path | None = None
    primesieve_library_error: str | None = None
    if include_primesieve_library_server:
        try:
            primesieve_library_server = build_primesieve_next_server(args)
        except Exception as exc:
            primesieve_library_error = str(exc)
            if "primesieve-library" not in args.require_tool:
                print(
                    "skipping libprimesieve next-prime helper: "
                    f"{primesieve_library_error}",
                    file=sys.stderr,
                )
    missing_required = [
        tool
        for tool, path in [
            ("primesieve", primesieve),
            ("primecount", primecount),
            ("primesieve-library", primesieve_library_server),
        ]
        if tool in args.require_tool and path is None
    ]
    if missing_required:
        metadata = build_run_metadata(
            args=args,
            starts=starts,
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=primesieve,
            primecount=primecount,
            primesieve_library_server=primesieve_library_server,
            primesieve_library_error=primesieve_library_error,
            row_count=0,
        )
        emit_metadata(metadata, args.metadata_output)
        message = (
            "required external next-prime control unavailable: "
            + ", ".join(missing_required)
            + "; install with `brew install primesieve primecount`"
        )
        raise RuntimeError(message)
    if primesieve is None and primecount is None and primesieve_library_server is None:
        metadata = build_run_metadata(
            args=args,
            starts=starts,
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=None,
            primecount=None,
            primesieve_library_server=None,
            primesieve_library_error=primesieve_library_error,
            row_count=0,
        )
        emit_metadata(metadata, args.metadata_output)
        print(
            "no external next-prime controls available; install `primesieve` "
            "or run with `--include-primecount` after installing `primecount`",
            file=sys.stderr,
        )
        return 0

    cargo = require_cargo()
    circle_prime = build_circle_prime(cargo)
    rows: list[NextBenchRow] = []
    samples: list[NextBenchSample] = []
    for start in starts:
        start_rows, start_samples = measure_start_interleaved(
            circle_prime=circle_prime,
            primesieve=primesieve,
            primecount=primecount,
            primesieve_library_server=primesieve_library_server,
            start=start,
            batch_size=args.batch_size,
            external_threads=args.external_threads,
            rounds=args.rounds,
            include_circle_server=args.include_circle_server,
            primecount_max_start=args.primecount_max_start,
            primesieve_library_max_start=args.primesieve_library_max_start,
        )
        rows.extend(start_rows)
        samples.extend(start_samples)

    emit_csv(rows, args.output)
    emit_samples(samples, args.sample_output)
    metadata = build_run_metadata(
        args=args,
        starts=starts,
        started_at_utc=started_at_utc,
        cargo=cargo,
        circle_prime=circle_prime,
        primesieve=primesieve,
        primecount=primecount,
        primesieve_library_server=primesieve_library_server,
        primesieve_library_error=primesieve_library_error,
        row_count=len(rows),
    )
    emit_metadata(metadata, args.metadata_output)
    return 0


def parse_starts(raw: str) -> list[int]:
    starts = []
    seen = set()
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        try:
            start = int(item)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"start must be an integer, got {item!r}") from exc
        if start < 0 or start > 2**64 - 1:
            raise argparse.ArgumentTypeError(f"start must fit in u64, got {start}")
        if start not in seen:
            starts.append(start)
            seen.add(start)
    if not starts:
        raise argparse.ArgumentTypeError("--starts must include at least one value")
    return starts


def build_primesieve_next_server(args: argparse.Namespace) -> Path:
    compiler = shutil.which(args.cc)
    if compiler is None:
        raise RuntimeError(f"C compiler {args.cc!r} was not found")
    if not PRIMESIEVE_NEXT_SERVER_SOURCE.exists():
        raise RuntimeError(f"missing helper source: {PRIMESIEVE_NEXT_SERVER_SOURCE}")

    include_dir = args.primesieve_include_dir or autodetect_primesieve_include_dir()
    lib_dir = args.primesieve_lib_dir or autodetect_primesieve_lib_dir()
    PRIMESIEVE_NEXT_SERVER_BINARY.parent.mkdir(parents=True, exist_ok=True)

    command = [
        compiler,
        "-O3",
        "-std=c11",
        "-Wall",
        "-Wextra",
    ]
    if include_dir is not None:
        command.append(f"-I{include_dir}")
    command.extend([str(PRIMESIEVE_NEXT_SERVER_SOURCE), "-o", str(PRIMESIEVE_NEXT_SERVER_BINARY)])
    if lib_dir is not None:
        command.append(f"-L{lib_dir}")
    command.append("-lprimesieve")
    if lib_dir is not None:
        command.append(f"-Wl,-rpath,{lib_dir}")

    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(
            "failed to build libprimesieve next-prime helper"
            + (f": {detail}" if detail else "")
        )
    return PRIMESIEVE_NEXT_SERVER_BINARY


def autodetect_primesieve_include_dir() -> Path | None:
    for directory in [
        Path("/opt/homebrew/opt/primesieve/include"),
        Path("/opt/homebrew/include"),
        Path("/usr/local/opt/primesieve/include"),
        Path("/usr/local/include"),
        Path("/usr/include"),
    ]:
        if (directory / "primesieve.h").exists():
            return directory
    return None


def autodetect_primesieve_lib_dir() -> Path | None:
    names = [
        "libprimesieve.dylib",
        "libprimesieve.so",
        "libprimesieve.a",
    ]
    for directory in [
        Path("/opt/homebrew/opt/primesieve/lib"),
        Path("/opt/homebrew/lib"),
        Path("/usr/local/opt/primesieve/lib"),
        Path("/usr/local/lib"),
        Path("/usr/lib"),
    ]:
        if any((directory / name).exists() for name in names):
            return directory
    return None


def measure_start_interleaved(
    *,
    circle_prime: Path,
    primesieve: str | None,
    primecount: str | None,
    primesieve_library_server: Path | None,
    start: int,
    batch_size: int,
    external_threads: int,
    rounds: int,
    include_circle_server: bool = False,
    primecount_max_start: int = 1_000_000_000_000,
    primesieve_library_max_start: int = 2**64 - 1,
) -> tuple[list[NextBenchRow], list[NextBenchSample]]:
    measurements = [circle_next_measurement(circle_prime, start, batch_size)]
    if include_circle_server:
        measurements.append(circle_next_server_measurement(circle_prime, start, batch_size))
    if primesieve is not None:
        measurements.append(
            primesieve_next_measurement(primesieve, start, batch_size, external_threads)
        )
    if primesieve_library_server is not None and start <= primesieve_library_max_start:
        measurements.append(
            primesieve_generate_server_measurement(
                primesieve_library_server,
                start,
                batch_size,
            )
        )
    if primecount is not None and start <= primecount_max_start:
        measurements.append(
            primecount_next_measurement(primecount, start, batch_size, external_threads)
        )
    if not any(measurement.name.startswith("external_") for measurement in measurements):
        raise ValueError(f"no external next-prime control selected for start={start}")
    try:
        timing_rows, samples = measure_interleaved_next(measurements, rounds)
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
            verify_next_prime(circle_row, baseline_row)
            rows.append(speedup_row(circle_row, baseline_row))
    return rows, samples


def circle_next_measurement(binary: Path, start: int, batch_size: int) -> NextMeasurement:
    metadata_command = [str(binary), "next", str(start), "--json"]
    metadata_completed = subprocess.run(
        metadata_command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    metadata = json.loads(metadata_completed.stdout)
    prime = metadata.get("prime")
    if prime is None:
        raise ValueError(f"circle-prime next did not find a u64 prime at or above {start}")
    candidate_count = int(metadata["candidate_count"])
    command = [str(binary), "next", str(start)]

    def run_once() -> int:
        result = 0
        for _ in range(batch_size):
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            result = parse_integer_output(completed.stdout)
        return result

    return NextMeasurement(
        name="circle_prime_next_prime",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=candidate_count,
        run_once=run_once,
    )


class NextServerClient:
    def __init__(self, binary: Path) -> None:
        self.process = subprocess.Popen(
            [str(binary), "next-server"],
            cwd=ROOT,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if self.process.stdin is None or self.process.stdout is None:
            self.close()
            raise RuntimeError("failed to open next-server pipes")

    def next_prime(self, start: int) -> int:
        return self.next_primes(start, 1)[-1]

    def next_primes(self, start: int, count: int) -> list[int]:
        if count <= 0:
            return []
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.process.stdin.write(f"{start}\n" * count)
        self.process.stdin.flush()
        results = []
        for _ in range(count):
            response = self.process.stdout.readline()
            if response == "":
                stderr = self._read_stderr()
                raise RuntimeError(f"next-server exited without a response: {stderr}")
            stripped = response.strip()
            if stripped == "none":
                raise ValueError(f"circle-prime next-server did not find a prime for {start}")
            results.append(parse_integer_output(stripped))
        return results

    def close(self) -> None:
        if self.process.poll() is not None:
            return
        try:
            if self.process.stdin is not None:
                self.process.stdin.write("quit\n")
                self.process.stdin.flush()
        except OSError:
            pass
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def _read_stderr(self) -> str:
        if self.process.stderr is None:
            return ""
        try:
            return self.process.stderr.read()
        except OSError:
            return ""


def circle_next_server_measurement(
    binary: Path,
    start: int,
    batch_size: int,
) -> NextMeasurement:
    metadata_command = [str(binary), "next", str(start), "--json"]
    metadata_completed = subprocess.run(
        metadata_command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    metadata = json.loads(metadata_completed.stdout)
    prime = metadata.get("prime")
    if prime is None:
        raise ValueError(f"circle-prime next did not find a u64 prime at or above {start}")
    expected_prime = int(prime)
    candidate_count = int(metadata["candidate_count"])
    client = NextServerClient(binary)

    def run_once() -> int:
        results = client.next_primes(start, batch_size)
        for result in results:
            if result != expected_prime:
                raise AssertionError(
                    f"Circle next-server disagreed with JSON metadata for start={start}: "
                    f"metadata {expected_prime}, server {result}"
                )
        return results[-1] if results else 0

    return NextMeasurement(
        name="circle_prime_server_next_prime",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=candidate_count,
        run_once=run_once,
        close=client.close,
    )


def primesieve_next_measurement(
    binary: str,
    start: int,
    batch_size: int,
    threads: int,
) -> NextMeasurement:
    command = primesieve_next_command(binary, start, threads)

    def run_once() -> int:
        result = 0
        for _ in range(batch_size):
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            result = parse_integer_output(completed.stdout)
        return result

    return NextMeasurement(
        name="external_primesieve_next_prime",
        start=start,
        batch_size=batch_size,
        threads=threads,
        requested_threads=threads,
        candidate_count=0,
        run_once=run_once,
    )


def primecount_next_measurement(
    binary: str,
    start: int,
    batch_size: int,
    threads: int,
) -> NextMeasurement:
    expected_prime = run_primecount_next_prime(binary, start, threads)

    def run_once() -> int:
        result = 0
        for _ in range(batch_size):
            result = run_primecount_next_prime(binary, start, threads)
            if result != expected_prime:
                raise AssertionError(
                    f"primecount next-prime result changed for start={start}: "
                    f"expected {expected_prime}, got {result}"
                )
        return result

    return NextMeasurement(
        name="external_primecount_next_prime",
        start=start,
        batch_size=batch_size,
        threads=threads,
        requested_threads=threads,
        candidate_count=0,
        run_once=run_once,
    )


class PrimeLineServerClient:
    def __init__(self, command: list[str], label: str) -> None:
        self.label = label
        self.process = subprocess.Popen(
            command,
            cwd=ROOT,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if self.process.stdin is None or self.process.stdout is None:
            self.close()
            raise RuntimeError(f"failed to open {self.label} pipes")

    def next_prime(self, start: int) -> int:
        return self.next_primes(start, 1)[-1]

    def next_primes(self, start: int, count: int) -> list[int]:
        if count <= 0:
            return []
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.process.stdin.write(f"{start}\n" * count)
        self.process.stdin.flush()
        results = []
        for _ in range(count):
            response = self.process.stdout.readline()
            if response == "":
                stderr = self._read_stderr()
                raise RuntimeError(f"{self.label} exited without a response: {stderr}")
            results.append(parse_integer_output(response))
        return results

    def close(self) -> None:
        if self.process.poll() is not None:
            return
        try:
            if self.process.stdin is not None:
                self.process.stdin.write("quit\n")
                self.process.stdin.flush()
        except OSError:
            pass
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def _read_stderr(self) -> str:
        if self.process.stderr is None:
            return ""
        try:
            return self.process.stderr.read()
        except OSError:
            return ""


def primesieve_generate_server_measurement(
    binary: Path,
    start: int,
    batch_size: int,
) -> NextMeasurement:
    client = PrimeLineServerClient(
        [str(binary)],
        "libprimesieve generate_n_primes next-prime helper",
    )
    expected_prime: int | None = None

    def run_once() -> int:
        nonlocal expected_prime
        results = client.next_primes(start, batch_size)
        for result in results:
            if expected_prime is None:
                expected_prime = result
            elif result != expected_prime:
                raise AssertionError(
                    "libprimesieve generate_n_primes result changed for "
                    f"start={start}: expected {expected_prime}, got {result}"
                )
        return results[-1] if results else 0

    return NextMeasurement(
        name="external_primesieve_generate_next_server",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=0,
        run_once=run_once,
        close=client.close,
    )


def primesieve_next_command(binary: str, start: int, threads: int) -> list[str]:
    predecessor = max(start - 1, 1)
    command = [binary, "1", str(predecessor), "--nth-prime", "--quiet"]
    if threads > 0:
        command.append(f"--threads={threads}")
    return command


def primecount_pi_command(binary: str, start: int, threads: int) -> list[str] | None:
    if start <= 2:
        return None
    command = [binary, str(start - 1)]
    if threads > 0:
        command.append(f"--threads={threads}")
    return command


def primecount_nth_prime_command(binary: str, nth: int, threads: int) -> list[str]:
    command = [binary, str(nth), "--nth-prime"]
    if threads > 0:
        command.append(f"--threads={threads}")
    return command


def run_primecount_next_prime(binary: str, start: int, threads: int) -> int:
    pi_command = primecount_pi_command(binary, start, threads)
    if pi_command is None:
        pi_before_start = 0
    else:
        completed = subprocess.run(
            pi_command,
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        pi_before_start = parse_integer_output(completed.stdout)

    completed = subprocess.run(
        primecount_nth_prime_command(binary, pi_before_start + 1, threads),
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return parse_integer_output(completed.stdout)


def measure_interleaved_next(
    measurements: list[NextMeasurement],
    rounds: int,
) -> tuple[list[NextBenchRow], list[NextBenchSample]]:
    timings: dict[str, list[float]] = {measurement_key(m): [] for m in measurements}
    results: dict[str, int] = {}
    samples: list[NextBenchSample] = []
    for round_index in range(rounds):
        for measurement in rotated(measurements, round_index):
            key = measurement_key(measurement)
            sample_start = time.perf_counter()
            result = measurement.run_once()
            elapsed = time.perf_counter() - sample_start
            expected = results.setdefault(key, result)
            if result != expected:
                raise AssertionError(f"{measurement.name} result changed between rounds")
            timings[key].append(elapsed)
            samples.append(sample_row(measurement, result, round_index, elapsed))

    rows = []
    for measurement in measurements:
        key = measurement_key(measurement)
        rows.append(timing_row_from_samples(measurement, results[key], rounds, timings[key]))
    return rows, samples


def measurement_key(measurement: NextMeasurement) -> str:
    return (
        f"{measurement.name}:{measurement.start}:{measurement.batch_size}:"
        f"{measurement.threads}:{measurement.requested_threads}"
    )


def sample_row(
    measurement: NextMeasurement,
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
    measurement: NextMeasurement,
    result: int,
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


def speedup_row(circle_row: NextBenchRow, baseline: NextBenchRow) -> NextBenchRow:
    best_speedup = baseline.best_ms / circle_row.best_ms if circle_row.best_ms > 0 else float("inf")
    median_speedup = (
        baseline.median_ms / circle_row.median_ms if circle_row.median_ms > 0 else float("inf")
    )
    return NextBenchRow(
        kind="speedup",
        name=circle_row.name,
        start=circle_row.start,
        batch_size=circle_row.batch_size,
        result=circle_row.result,
        candidate_count=circle_row.candidate_count,
        rounds=circle_row.rounds,
        best_ms=circle_row.best_ms,
        median_ms=circle_row.median_ms,
        searches_per_second=circle_row.searches_per_second,
        median_searches_per_second=circle_row.median_searches_per_second,
        threads=circle_row.threads,
        requested_threads=circle_row.requested_threads,
        baseline=baseline.name,
        best_speedup=f"{best_speedup:.3f}",
        median_speedup=f"{median_speedup:.3f}",
        **next_speedup_sample_metric_fields(circle_row, baseline),
    )


def next_speedup_sample_metric_fields(
    circle_row: NextBenchRow,
    baseline: NextBenchRow,
) -> dict[str, Any]:
    stability = (
        "noisy"
        if "noisy" in {circle_row.sample_stability, baseline.sample_stability}
        else circle_row.sample_stability or baseline.sample_stability
    )
    return {
        "sample_count": circle_row.sample_count,
        "sample_noise_ms": circle_row.sample_noise_ms,
        "sample_max_ms": circle_row.sample_max_ms,
        "sample_noise_over_median": circle_row.sample_noise_over_median,
        "sample_max_over_median": circle_row.sample_max_over_median,
        "sample_ignored_single_high_outlier": (
            circle_row.sample_ignored_single_high_outlier
        ),
        "sample_stability": stability,
    }


def verify_next_prime(circle_row: NextBenchRow, baseline: NextBenchRow) -> None:
    if circle_row.result != baseline.result:
        raise AssertionError(
            f"{baseline.name} next-prime mismatch for start={circle_row.start}: "
            f"Circle {circle_row.result}, baseline {baseline.result}"
        )


def emit_csv(rows: list[NextBenchRow], output: Path | None) -> None:
    fieldnames = list(NextBenchRow.__dataclass_fields__)
    if output is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    print(f"wrote external next-prime benchmark CSV to {output}")


def emit_samples(samples: list[NextBenchSample], output: Path | None) -> None:
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(NextBenchSample.__dataclass_fields__))
        writer.writeheader()
        for row in samples:
            writer.writerow(asdict(row))
    print(f"wrote external next-prime benchmark sample CSV to {output}")


def emit_metadata(metadata: dict[str, Any], output: Path | None) -> None:
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(f"wrote external next-prime benchmark metadata JSON to {output}")


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
    row_count: int,
    primesieve_library_error: str | None = None,
) -> dict[str, Any]:
    circle_binary = circle_prime or ROOT / "target" / "release" / "circle-prime"
    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": utc_now(),
        "row_count": row_count,
        "rounds": args.rounds,
        "batch_size": args.batch_size,
        "include_circle_server": bool(getattr(args, "include_circle_server", False)),
        "include_primecount": bool(
            getattr(args, "include_primecount", False) or "primecount" in args.require_tool
        ),
        "primecount_max_start": int(getattr(args, "primecount_max_start", 0)),
        "include_primesieve_library_server": bool(
            getattr(args, "include_primesieve_library_server", False)
            or "primesieve-library" in args.require_tool
        ),
        "primesieve_library_max_start": int(
            getattr(args, "primesieve_library_max_start", 0)
        ),
        "starts": starts,
        "sample_output": str(args.sample_output) if args.sample_output is not None else None,
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
                "source": str(PRIMESIEVE_NEXT_SERVER_SOURCE),
                "method": "primesieve_generate_n_primes(1, START, UINT64_PRIMES)",
                "error": primesieve_library_error,
            },
        },
        "commands": [
            {
                "start": start,
                "circle": [str(circle_binary), "next", str(start)],
                "circle_server": [str(circle_binary), "next-server"],
                "circle_json_probe": [str(circle_binary), "next", str(start), "--json"],
                "primesieve": (
                    primesieve_next_command(primesieve, start, args.external_threads)
                    if primesieve is not None
                    else None
                ),
                "primesieve_library_server": (
                    [str(primesieve_library_server)]
                    if primesieve_library_server is not None
                    and start <= args.primesieve_library_max_start
                    else None
                ),
                "primecount_pi": (
                    primecount_pi_command(primecount, start, args.external_threads)
                    if primecount is not None and start <= args.primecount_max_start
                    else None
                ),
                "primecount_nth_prime": (
                    [str(primecount), "pi(START-1)+1", "--nth-prime"]
                    + (
                        [f"--threads={args.external_threads}"]
                        if args.external_threads > 0
                        else []
                    )
                    if primecount is not None and start <= args.primecount_max_start
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
        print(f"external next-prime benchmark failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
