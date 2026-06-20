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
    utc_now,
)


DEFAULT_STARTS = "90,1000000,4294967000,1000000000000,18446744073709551500"


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
        description="Benchmark Circle next-prime search against primesieve --nth-prime."
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
        help="Thread count for primesieve. Use 0 for primesieve's default/all cores.",
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
        choices=("primesieve",),
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

    starts = parse_starts(args.starts)
    started_at_utc = utc_now()
    primesieve = shutil.which("primesieve")
    if primesieve is None:
        metadata = build_run_metadata(
            args=args,
            starts=starts,
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=None,
            row_count=0,
        )
        emit_metadata(metadata, args.metadata_output)
        message = (
            "required external next-prime control unavailable: primesieve; "
            "install with `brew install primesieve`"
        )
        if args.require_tool:
            raise RuntimeError(message)
        print(message, file=sys.stderr)
        return 0

    cargo = require_cargo()
    circle_prime = build_circle_prime(cargo)
    rows: list[NextBenchRow] = []
    samples: list[NextBenchSample] = []
    for start in starts:
        start_rows, start_samples = measure_start_interleaved(
            circle_prime=circle_prime,
            primesieve=primesieve,
            start=start,
            batch_size=args.batch_size,
            external_threads=args.external_threads,
            rounds=args.rounds,
            include_circle_server=args.include_circle_server,
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


def measure_start_interleaved(
    *,
    circle_prime: Path,
    primesieve: str,
    start: int,
    batch_size: int,
    external_threads: int,
    rounds: int,
    include_circle_server: bool = False,
) -> tuple[list[NextBenchRow], list[NextBenchSample]]:
    measurements = [circle_next_measurement(circle_prime, start, batch_size)]
    if include_circle_server:
        measurements.append(circle_next_server_measurement(circle_prime, start, batch_size))
    baseline = primesieve_next_measurement(primesieve, start, batch_size, external_threads)
    measurements.append(baseline)
    try:
        timing_rows, samples = measure_interleaved_next(measurements, rounds)
    finally:
        for measurement in measurements:
            if measurement.close is not None:
                measurement.close()

    baseline_row = next(row for row in timing_rows if row.name == "external_primesieve_next_prime")
    circle_rows = [row for row in timing_rows if row.name != "external_primesieve_next_prime"]
    rows: list[NextBenchRow] = []
    rows.extend(circle_rows)
    rows.append(baseline_row)
    for circle_row in circle_rows:
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
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.process.stdin.write(f"{start}\n")
        self.process.stdin.flush()
        response = self.process.stdout.readline()
        if response == "":
            stderr = self._read_stderr()
            raise RuntimeError(f"next-server exited without a response: {stderr}")
        stripped = response.strip()
        if stripped == "none":
            raise ValueError(f"circle-prime next-server did not find a prime for {start}")
        return parse_integer_output(stripped)

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
        result = 0
        for _ in range(batch_size):
            result = client.next_prime(start)
            if result != expected_prime:
                raise AssertionError(
                    f"Circle next-server disagreed with JSON metadata for start={start}: "
                    f"metadata {expected_prime}, server {result}"
                )
        return result

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


def primesieve_next_command(binary: str, start: int, threads: int) -> list[str]:
    predecessor = max(start - 1, 1)
    command = [binary, "1", str(predecessor), "--nth-prime", "--quiet"]
    if threads > 0:
        command.append(f"--threads={threads}")
    return command


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
    )


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
    row_count: int,
) -> dict[str, Any]:
    circle_binary = circle_prime or ROOT / "target" / "release" / "circle-prime"
    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": utc_now(),
        "row_count": row_count,
        "rounds": args.rounds,
        "batch_size": args.batch_size,
        "include_circle_server": bool(getattr(args, "include_circle_server", False)),
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
