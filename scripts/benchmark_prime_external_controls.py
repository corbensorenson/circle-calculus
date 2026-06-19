from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANGES = "0:10000000,0:100000000,1000000000000:1000010000000"
DEFAULT_CIRCLE_COUNT_MODES = "segmented"
VALID_CIRCLE_COUNT_MODES = {
    "default",
    "segmented",
    "balanced",
    "dynamic",
    "presieve13",
    "wheel30-mark",
    "hybrid-wheel30-mark",
}


@dataclass(frozen=True)
class ExternalBenchRow:
    kind: str
    name: str
    low: int
    high: int
    span: int
    segment_size: int
    result: int
    rounds: int
    best_ms: float
    median_ms: float
    rate_per_second: float
    median_rate_per_second: float
    threads: int
    requested_threads: int
    baseline: str
    best_speedup: str
    median_speedup: str
    count_mode: str = ""


@dataclass(frozen=True)
class ExternalBenchSample:
    kind: str
    name: str
    low: int
    high: int
    span: int
    segment_size: int
    result: int
    round_index: int
    elapsed_ms: float
    threads: int
    requested_threads: int
    count_mode: str = ""


@dataclass(frozen=True)
class Measurement:
    name: str
    low: int
    high: int
    segment_size: int
    threads: int
    requested_threads: int
    run_once: Callable[[], int]
    count_mode: str = ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark Circle prime counts against external primesieve/primecount controls."
    )
    parser.add_argument("--ranges", default=DEFAULT_RANGES)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument(
        "--segment-size",
        type=int,
        default=0,
        help="Circle segment size. Use 0 to let the Rust CLI choose its adaptive default.",
    )
    parser.add_argument(
        "--segment-sizes",
        help=(
            "Comma-separated Circle segment sizes to sweep. Use 0 to include the "
            "Rust CLI adaptive default. When set, this overrides --segment-size."
        ),
    )
    parser.add_argument(
        "--circle-threads",
        type=int,
        default=1,
        help="Thread count for the Circle range counter.",
    )
    parser.add_argument(
        "--circle-count-modes",
        default=DEFAULT_CIRCLE_COUNT_MODES,
        help=(
            "Comma-separated Circle count modes to benchmark. The default "
            "is segmented; use default to omit --count-mode and follow the "
            "current CLI adaptive default. Experimental modes include "
            "balanced, dynamic, presieve13, wheel30-mark, and hybrid-wheel30-mark."
        ),
    )
    parser.add_argument(
        "--external-threads",
        type=int,
        default=0,
        help=(
            "Thread count for external controls. Use 0 to keep each tool's "
            "default; primesieve and primecount default to all available cores."
        ),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--sample-output",
        type=Path,
        help="Optional per-round sample CSV. Requires --interleaved.",
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        help="Optional JSON sidecar that records tool versions, paths, thread policy, and commands.",
    )
    parser.add_argument(
        "--interleaved",
        action="store_true",
        help=(
            "Measure each range in a rotated round-robin schedule across Circle "
            "variants and external baselines. This reduces phase bias in segment sweeps."
        ),
    )
    parser.add_argument(
        "--require-external",
        action="store_true",
        help="Fail if neither primesieve nor primecount is installed.",
    )
    parser.add_argument(
        "--require-tool",
        choices=("primesieve", "primecount"),
        action="append",
        default=[],
        help=(
            "Fail if the named external control is unavailable. Repeat this "
            "flag to require both serious baselines."
        ),
    )
    args = parser.parse_args()

    if args.rounds <= 0:
        parser.error("--rounds must be positive")
    if args.segment_size < 0:
        parser.error("--segment-size must be nonnegative")
    if args.circle_threads <= 0:
        parser.error("--circle-threads must be positive")
    if args.external_threads < 0:
        parser.error("--external-threads must be nonnegative")
    if args.sample_output is not None and not args.interleaved:
        parser.error("--sample-output requires --interleaved")

    ranges = parse_ranges(args.ranges)
    try:
        segment_sizes = parse_segment_size_list(args.segment_sizes, args.segment_size)
        circle_count_modes = parse_circle_count_modes(args.circle_count_modes)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    started_at_utc = utc_now()
    primesieve = shutil.which("primesieve")
    primecount = shutil.which("primecount")

    missing_required = required_external_tools_missing(
        args.require_tool,
        primesieve=primesieve,
        primecount=primecount,
    )
    if missing_required:
        metadata = build_run_metadata(
            args=args,
            ranges=ranges,
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=primesieve,
            primecount=primecount,
            row_count=0,
        )
        emit_metadata(metadata, args.metadata_output)
        tools = ", ".join(missing_required)
        raise RuntimeError(
            f"required external control(s) unavailable: {tools}; "
            "install with `brew install primesieve primecount`"
        )

    if primesieve is None and primecount is None:
        metadata = build_run_metadata(
            args=args,
            ranges=ranges,
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=None,
            primecount=None,
            row_count=0,
        )
        emit_metadata(metadata, args.metadata_output)
        message = (
            "external controls unavailable: install primesieve and/or primecount "
            "to run the strongest local comparisons"
        )
        if args.require_external:
            raise RuntimeError(message)
        print(message, file=sys.stderr)
        return 0

    cargo = require_cargo()
    circle_prime = build_circle_prime(cargo)

    rows: list[ExternalBenchRow] = []
    samples: list[ExternalBenchSample] = []
    for low, high in ranges:
        if args.interleaved:
            range_rows, range_samples = measure_range_interleaved(
                circle_prime=circle_prime,
                primesieve=primesieve,
                primecount=primecount,
                low=low,
                high=high,
                segment_sizes=segment_sizes,
                circle_count_modes=circle_count_modes,
                circle_threads=args.circle_threads,
                external_threads=args.external_threads,
                rounds=args.rounds,
            )
            rows.extend(range_rows)
            samples.extend(range_samples)
        else:
            circle_rows: list[ExternalBenchRow] = []
            seen_circle_variants: set[tuple[str, int, int]] = set()
            for segment_size in segment_sizes:
                for count_mode in circle_count_modes:
                    circle_row = measure_circle_prime(
                        circle_prime,
                        low,
                        high,
                        segment_size,
                        args.circle_threads,
                        args.rounds,
                        count_mode,
                    )
                    variant_key = (circle_row.name, circle_row.segment_size, circle_row.threads)
                    if variant_key not in seen_circle_variants:
                        circle_rows.append(circle_row)
                        seen_circle_variants.add(variant_key)
            rows.extend(circle_rows)

            if primesieve is not None:
                row = measure_primesieve(primesieve, low, high, args.rounds, args.external_threads)
                rows.append(row)
                for circle_row in circle_rows:
                    verify_count(circle_row, row)
                    rows.append(speedup_row(circle_row, row))

            if primecount is not None:
                row = measure_primecount(primecount, low, high, args.rounds, args.external_threads)
                rows.append(row)
                for circle_row in circle_rows:
                    verify_count(circle_row, row)
                    rows.append(speedup_row(circle_row, row))

    emit_csv(rows, args.output)
    emit_samples(samples, args.sample_output)
    metadata = build_run_metadata(
        args=args,
        segment_sizes=segment_sizes,
        circle_count_modes=circle_count_modes,
        ranges=ranges,
        started_at_utc=started_at_utc,
        cargo=cargo,
        circle_prime=circle_prime,
        primesieve=primesieve,
        primecount=primecount,
        row_count=len(rows),
    )
    emit_metadata(metadata, args.metadata_output)
    return 0


def measure_circle_prime(
    binary: Path,
    low: int,
    high: int,
    segment_size: int,
    threads: int,
    rounds: int,
    count_mode: str = "segmented",
) -> ExternalBenchRow:
    metadata_command = circle_prime_command(
        binary,
        low,
        high,
        segment_size,
        threads,
        count_mode,
        json_output=True,
    )
    metadata_completed = subprocess.run(
        metadata_command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    metadata = json.loads(metadata_completed.stdout)
    actual_segment_size = int(metadata["segment_size"])
    actual_threads = int(metadata["threads"])
    metadata_count = int(metadata["count"])
    resolved_count_mode = str(metadata.get("count_mode", count_mode))
    timing_command = circle_prime_command(
        binary,
        low,
        high,
        segment_size,
        threads,
        count_mode,
        json_output=False,
    )

    def run_once() -> int:
        completed = subprocess.run(
            timing_command,
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        return parse_integer_output(completed.stdout)

    row = measure(
        "circle_prime_segmented_count",
        low,
        high,
        segment_size,
        rounds,
        run_once,
        threads=actual_threads,
        requested_threads=threads,
    )
    if row.result != metadata_count:
        raise AssertionError(
            f"Circle plain count disagreed with JSON metadata for [{low},{high}): "
            f"metadata {metadata_count}, plain {row.result}"
        )
    actual_name = circle_measurement_name(count_mode, actual_threads)
    return replace(
        row,
        name=actual_name,
        segment_size=actual_segment_size,
        count_mode=resolved_count_mode,
    )


def circle_prime_measurement(
    binary: Path,
    low: int,
    high: int,
    segment_size: int,
    threads: int,
    count_mode: str = "segmented",
) -> Measurement:
    metadata_command = circle_prime_command(
        binary,
        low,
        high,
        segment_size,
        threads,
        count_mode,
        json_output=True,
    )
    metadata_completed = subprocess.run(
        metadata_command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    metadata = json.loads(metadata_completed.stdout)
    actual_segment_size = int(metadata["segment_size"])
    actual_threads = int(metadata["threads"])
    resolved_count_mode = str(metadata.get("count_mode", count_mode))
    timing_command = circle_prime_command(
        binary,
        low,
        high,
        segment_size,
        threads,
        count_mode,
        json_output=False,
    )

    def run_once() -> int:
        completed = subprocess.run(
            timing_command,
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        return parse_integer_output(completed.stdout)

    name = circle_measurement_name(count_mode, actual_threads)
    return Measurement(
        name=name,
        low=low,
        high=high,
        segment_size=actual_segment_size,
        threads=actual_threads,
        requested_threads=threads,
        run_once=run_once,
        count_mode=resolved_count_mode,
    )


def circle_prime_command(
    binary: Path,
    low: int,
    high: int,
    segment_size: int,
    threads: int,
    count_mode: str = "segmented",
    *,
    json_output: bool,
) -> list[str]:
    command = [
        str(binary),
        "range",
        str(low),
        str(high),
        "--count",
    ]
    if json_output:
        command.append("--json")
    if segment_size > 0:
        command.extend(["--segment-size", str(segment_size)])
    if threads != 1:
        command.extend(["--threads", str(threads)])
    if count_mode != "default":
        command.extend(["--count-mode", count_mode])
    return command


def circle_measurement_name(count_mode: str, actual_threads: int) -> str:
    suffix = count_mode.replace("-", "_")
    name = f"circle_prime_{suffix}_count"
    if actual_threads != 1:
        name = f"circle_prime_parallel_{suffix}_count_{actual_threads}t"
    return name


def measure_primesieve(
    binary: str,
    low: int,
    high: int,
    rounds: int,
    threads: int,
) -> ExternalBenchRow:
    stop = high - 1
    if stop < low:
        raise ValueError(f"empty range [{low},{high})")
    command = primesieve_command(binary, low, stop, threads)

    def run_once() -> int:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        return parse_integer_output(completed.stdout)

    return measure(
        "external_primesieve_count",
        low,
        high,
        0,
        rounds,
        run_once,
        threads=threads,
        requested_threads=threads,
    )


def primesieve_measurement(
    binary: str,
    low: int,
    high: int,
    threads: int,
) -> Measurement:
    stop = high - 1
    if stop < low:
        raise ValueError(f"empty range [{low},{high})")
    command = primesieve_command(binary, low, stop, threads)

    def run_once() -> int:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        return parse_integer_output(completed.stdout)

    return Measurement(
        name="external_primesieve_count",
        low=low,
        high=high,
        segment_size=0,
        threads=threads,
        requested_threads=threads,
        run_once=run_once,
    )


def measure_primecount(
    binary: str,
    low: int,
    high: int,
    rounds: int,
    threads: int,
) -> ExternalBenchRow:
    def run_once() -> int:
        high_count = run_primecount(binary, high - 1, threads)
        low_count = run_primecount(binary, low - 1, threads) if low > 0 else 0
        return high_count - low_count

    return measure(
        "external_primecount_pi_diff",
        low,
        high,
        0,
        rounds,
        run_once,
        threads=threads,
        requested_threads=threads,
    )


def primecount_measurement(
    binary: str,
    low: int,
    high: int,
    threads: int,
) -> Measurement:
    def run_once() -> int:
        high_count = run_primecount(binary, high - 1, threads)
        low_count = run_primecount(binary, low - 1, threads) if low > 0 else 0
        return high_count - low_count

    return Measurement(
        name="external_primecount_pi_diff",
        low=low,
        high=high,
        segment_size=0,
        threads=threads,
        requested_threads=threads,
        run_once=run_once,
    )


def measure_range_interleaved(
    *,
    circle_prime: Path,
    primesieve: str | None,
    primecount: str | None,
    low: int,
    high: int,
    segment_sizes: list[int],
    circle_count_modes: list[str],
    circle_threads: int,
    external_threads: int,
    rounds: int,
) -> tuple[list[ExternalBenchRow], list[ExternalBenchSample]]:
    circle_measurements: list[Measurement] = []
    seen_circle_variants: set[tuple[str, int, int]] = set()
    for segment_size in segment_sizes:
        for count_mode in circle_count_modes:
            measurement = circle_prime_measurement(
                circle_prime,
                low,
                high,
                segment_size,
                circle_threads,
                count_mode,
            )
            variant_key = (measurement.name, measurement.segment_size, measurement.threads)
            if variant_key not in seen_circle_variants:
                circle_measurements.append(measurement)
                seen_circle_variants.add(variant_key)

    baseline_measurements = []
    if primesieve is not None:
        baseline_measurements.append(
            primesieve_measurement(primesieve, low, high, external_threads)
        )
    if primecount is not None:
        baseline_measurements.append(
            primecount_measurement(primecount, low, high, external_threads)
        )

    timing_rows, samples = measure_interleaved(
        [*circle_measurements, *baseline_measurements],
        rounds,
    )
    circle_names = {measurement.name for measurement in circle_measurements}
    baseline_names = {measurement.name for measurement in baseline_measurements}
    circle_rows = [row for row in timing_rows if row.name in circle_names]
    baseline_rows = [row for row in timing_rows if row.name in baseline_names]

    rows: list[ExternalBenchRow] = []
    rows.extend(circle_rows)
    for baseline_row in baseline_rows:
        rows.append(baseline_row)
        for circle_row in circle_rows:
            verify_count(circle_row, baseline_row)
            rows.append(speedup_row(circle_row, baseline_row))
    return rows, samples


def measure_interleaved(
    measurements: list[Measurement],
    rounds: int,
) -> tuple[list[ExternalBenchRow], list[ExternalBenchSample]]:
    if not measurements:
        return [], []
    timings: dict[str, list[float]] = {measurement_key(m): [] for m in measurements}
    results: dict[str, int] = {}
    samples: list[ExternalBenchSample] = []
    for round_index in range(rounds):
        order = rotated(measurements, round_index)
        for measurement in order:
            key = measurement_key(measurement)
            start = time.perf_counter()
            result = measurement.run_once()
            elapsed = time.perf_counter() - start
            expected = results.setdefault(key, result)
            if result != expected:
                raise AssertionError(f"{measurement.name} result changed between rounds")
            timings[key].append(elapsed)
            samples.append(sample_row(measurement, result, round_index, elapsed))

    rows = []
    for measurement in measurements:
        key = measurement_key(measurement)
        row = timing_row_from_samples(measurement, results[key], rounds, timings[key])
        rows.append(row)
    return rows, samples


def rotated(values: list[Measurement], offset: int) -> list[Measurement]:
    if not values:
        return []
    start = offset % len(values)
    return values[start:] + values[:start]


def measurement_key(measurement: Measurement) -> str:
    return (
        f"{measurement.name}:{measurement.low}:{measurement.high}:"
        f"{measurement.segment_size}:{measurement.threads}:{measurement.requested_threads}"
    )


def sample_row(
    measurement: Measurement,
    result: int,
    round_index: int,
    elapsed_seconds: float,
) -> ExternalBenchSample:
    return ExternalBenchSample(
        kind="sample",
        name=measurement.name,
        low=measurement.low,
        high=measurement.high,
        span=measurement.high - measurement.low,
        segment_size=measurement.segment_size,
        result=result,
        round_index=round_index,
        elapsed_ms=elapsed_seconds * 1000.0,
        threads=measurement.threads,
        requested_threads=measurement.requested_threads,
        count_mode=measurement.count_mode,
    )


def timing_row_from_samples(
    measurement: Measurement,
    result: int,
    rounds: int,
    timings: list[float],
) -> ExternalBenchRow:
    best_seconds = min(timings)
    median_seconds = median(timings)
    span = measurement.high - measurement.low
    return ExternalBenchRow(
        kind="timing",
        name=measurement.name,
        low=measurement.low,
        high=measurement.high,
        span=span,
        segment_size=measurement.segment_size,
        result=result,
        rounds=rounds,
        best_ms=best_seconds * 1000.0,
        median_ms=median_seconds * 1000.0,
        rate_per_second=(span / best_seconds) if best_seconds > 0 else float("inf"),
        median_rate_per_second=(
            (span / median_seconds) if median_seconds > 0 else float("inf")
        ),
        threads=measurement.threads,
        requested_threads=measurement.requested_threads,
        baseline="",
        best_speedup="",
        median_speedup="",
        count_mode=measurement.count_mode,
    )


def primesieve_command(binary: str, low: int, stop: int, threads: int) -> list[str]:
    command = [binary, str(low), str(stop), "--count", "--quiet"]
    if threads > 0:
        command.append(f"--threads={threads}")
    return command


def primecount_command(binary: str, n: int, threads: int) -> list[str]:
    command = [binary, str(n)]
    if threads > 0:
        command.append(f"--threads={threads}")
    return command


def run_primecount(binary: str, n: int, threads: int) -> int:
    completed = subprocess.run(
        primecount_command(binary, n, threads),
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return parse_integer_output(completed.stdout)


def measure(
    name: str,
    low: int,
    high: int,
    segment_size: int,
    rounds: int,
    run_once,
    *,
    threads: int,
    requested_threads: int,
) -> ExternalBenchRow:
    expected = None
    timings: list[float] = []
    for _ in range(rounds):
        start = time.perf_counter()
        result = run_once()
        elapsed = time.perf_counter() - start
        if expected is None:
            expected = result
        elif result != expected:
            raise AssertionError(f"{name} result changed between rounds")
        timings.append(elapsed)

    assert expected is not None
    best_seconds = min(timings)
    median_seconds = median(timings)
    span = high - low
    return ExternalBenchRow(
        kind="timing",
        name=name,
        low=low,
        high=high,
        span=span,
        segment_size=segment_size,
        result=expected,
        rounds=rounds,
        best_ms=best_seconds * 1000.0,
        median_ms=median_seconds * 1000.0,
        rate_per_second=(span / best_seconds) if best_seconds > 0 else float("inf"),
        median_rate_per_second=(
            (span / median_seconds) if median_seconds > 0 else float("inf")
        ),
        threads=threads,
        requested_threads=requested_threads,
        baseline="",
        best_speedup="",
        median_speedup="",
    )


def speedup_row(circle_row: ExternalBenchRow, baseline: ExternalBenchRow) -> ExternalBenchRow:
    circle_seconds = circle_row.best_ms / 1000.0
    baseline_seconds = baseline.best_ms / 1000.0
    speedup = baseline_seconds / circle_seconds if circle_seconds > 0 else float("inf")
    circle_median_seconds = circle_row.median_ms / 1000.0
    baseline_median_seconds = baseline.median_ms / 1000.0
    median_speedup = (
        baseline_median_seconds / circle_median_seconds
        if circle_median_seconds > 0
        else float("inf")
    )
    return ExternalBenchRow(
        kind="speedup",
        name=circle_row.name,
        low=circle_row.low,
        high=circle_row.high,
        span=circle_row.span,
        segment_size=circle_row.segment_size,
        result=circle_row.result,
        rounds=circle_row.rounds,
        best_ms=circle_row.best_ms,
        median_ms=circle_row.median_ms,
        rate_per_second=circle_row.rate_per_second,
        median_rate_per_second=circle_row.median_rate_per_second,
        threads=circle_row.threads,
        requested_threads=circle_row.requested_threads,
        baseline=baseline.name,
        best_speedup=f"{speedup:.3f}",
        median_speedup=f"{median_speedup:.3f}",
        count_mode=circle_row.count_mode,
    )


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute median of empty values")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def verify_count(expected: ExternalBenchRow, actual: ExternalBenchRow) -> None:
    if expected.result != actual.result:
        raise AssertionError(
            f"{actual.name} count mismatch for [{expected.low},{expected.high}): "
            f"expected {expected.result}, got {actual.result}"
        )


def emit_csv(rows: list[ExternalBenchRow], output: Path | None) -> None:
    fieldnames = list(ExternalBenchRow.__dataclass_fields__)
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
    print(f"wrote external benchmark CSV to {output}")


def emit_samples(samples: list[ExternalBenchSample], output: Path | None) -> None:
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ExternalBenchSample.__dataclass_fields__))
        writer.writeheader()
        for row in samples:
            writer.writerow(asdict(row))
    print(f"wrote external benchmark sample CSV to {output}")


def emit_metadata(metadata: dict[str, Any], output: Path | None) -> None:
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(f"wrote external benchmark metadata JSON to {output}")


def build_run_metadata(
    *,
    args: argparse.Namespace,
    segment_sizes: list[int] | None = None,
    circle_count_modes: list[str] | None = None,
    ranges: list[tuple[int, int]],
    started_at_utc: str,
    cargo: str | None,
    circle_prime: Path | None,
    primesieve: str | None,
    primecount: str | None,
    row_count: int,
) -> dict[str, Any]:
    circle_binary = circle_prime or ROOT / "target" / "release" / "circle-prime"
    if segment_sizes is None:
        segment_sizes = parse_segment_size_list(
            getattr(args, "segment_sizes", None),
            args.segment_size,
        )
    if circle_count_modes is None:
        circle_count_modes = parse_circle_count_modes(
            getattr(args, "circle_count_modes", DEFAULT_CIRCLE_COUNT_MODES)
        )
    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": utc_now(),
        "row_count": row_count,
        "rounds": args.rounds,
        "interleaved": bool(getattr(args, "interleaved", False)),
        "sample_output": (
            str(args.sample_output)
            if getattr(args, "sample_output", None) is not None
            else None
        ),
        "requested_segment_size": args.segment_size,
        "requested_segment_sizes": segment_sizes,
        "circle_count_modes": circle_count_modes,
        "thread_policy": {
            "circle_requested_threads": args.circle_threads,
            "external_requested_threads": args.external_threads,
            "external_default_threads_when_zero": "tool default/all available CPU cores",
        },
        "required_external_tools": sorted(set(getattr(args, "require_tool", []))),
        "ranges": [{"low": low, "high": high, "span": high - low} for low, high in ranges],
        "tools": {
            "circle_prime": circle_prime_metadata(cargo, circle_prime),
            "primesieve": external_tool_metadata("primesieve", primesieve, ["--version"]),
            "primecount": external_tool_metadata("primecount", primecount, ["--version"]),
        },
        "range_commands": range_command_metadata(
            circle_binary,
            primesieve,
            primecount,
            ranges,
            segment_sizes,
            circle_count_modes,
            args.circle_threads,
            args.external_threads,
        ),
    }


def circle_prime_metadata(cargo: str | None, circle_prime: Path | None) -> dict[str, Any]:
    package = circle_prime_package_metadata(cargo)
    return {
        "available": circle_prime is not None and circle_prime.exists(),
        "path": str(circle_prime) if circle_prime is not None else None,
        "package_name": package.get("name"),
        "version": package.get("version"),
    }


def circle_prime_package_metadata(cargo: str | None) -> dict[str, str | None]:
    if cargo is None:
        cargo = shutil.which("cargo")
    if cargo is None:
        return {"name": None, "version": None}
    try:
        completed = subprocess.run(
            [cargo, "metadata", "--no-deps", "--format-version", "1"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return {"name": None, "version": None}
    try:
        metadata = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"name": None, "version": None}
    for package in metadata.get("packages", []):
        if package.get("name") == "circle-prime":
            return {"name": "circle-prime", "version": package.get("version")}
    return {"name": None, "version": None}


def external_tool_metadata(name: str, path: str | None, version_args: list[str]) -> dict[str, Any]:
    if path is None:
        return {"available": False, "path": None, "version": None}
    return {
        "available": True,
        "path": path,
        "version": command_output([path, *version_args]),
    }


def command_output(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"unavailable: {exc}"
    return completed.stdout.strip()


def range_command_metadata(
    circle_prime: Path,
    primesieve: str | None,
    primecount: str | None,
    ranges: list[tuple[int, int]],
    segment_sizes: list[int],
    circle_count_modes: list[str],
    circle_threads: int,
    external_threads: int,
) -> list[dict[str, Any]]:
    commands = []
    for low, high in ranges:
        stop = high - 1
        circle_variants = [
            {
                "segment_size": segment_size,
                "count_mode": count_mode,
                "json_probe": circle_prime_command(
                    circle_prime,
                    low,
                    high,
                    segment_size,
                    circle_threads,
                    count_mode,
                    json_output=True,
                ),
                "timing": circle_prime_command(
                    circle_prime,
                    low,
                    high,
                    segment_size,
                    circle_threads,
                    count_mode,
                    json_output=False,
                ),
            }
            for segment_size in segment_sizes
            for count_mode in circle_count_modes
        ]
        first_variant = circle_variants[0]
        entry: dict[str, Any] = {
            "low": low,
            "high": high,
            "circle_json_probe": first_variant["json_probe"],
            "circle_timing": first_variant["timing"],
            "circle_variants": circle_variants,
        }
        if primesieve is not None:
            entry["primesieve"] = primesieve_command(primesieve, low, stop, external_threads)
        if primecount is not None:
            entry["primecount_high"] = primecount_command(primecount, stop, external_threads)
            if low > 0:
                entry["primecount_low"] = primecount_command(
                    primecount,
                    low - 1,
                    external_threads,
                )
        commands.append(entry)
    return commands


def required_external_tools_missing(
    required_tools: list[str],
    *,
    primesieve: str | None,
    primecount: str | None,
) -> list[str]:
    available = {
        "primesieve": primesieve is not None,
        "primecount": primecount is not None,
    }
    return sorted({tool for tool in required_tools if not available[tool]})


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_integer_output(output: str) -> int:
    matches = re.findall(r"\d+", output.replace(",", ""))
    if not matches:
        raise ValueError(f"could not parse integer from output: {output!r}")
    return int(matches[-1])


def build_circle_prime(cargo: str) -> Path:
    print("+ " + " ".join([cargo, "build", "--release", "-p", "circle-prime", "--bin", "circle-prime"]), file=sys.stderr)
    subprocess.run(
        [cargo, "build", "--release", "-p", "circle-prime", "--bin", "circle-prime"],
        cwd=ROOT,
        check=True,
    )
    suffix = ".exe" if sys.platform == "win32" else ""
    return ROOT / "target" / "release" / f"circle-prime{suffix}"


def require_cargo() -> str:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("cargo is required for external prime benchmarks")
    return cargo


def parse_ranges(raw: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        if ":" not in item:
            raise argparse.ArgumentTypeError(f"range must be LOW:HIGH, got {item!r}")
        low_raw, high_raw = item.split(":", 1)
        low = parse_nonnegative_int(low_raw, "LOW")
        high = parse_nonnegative_int(high_raw, "HIGH")
        if high <= low:
            raise argparse.ArgumentTypeError(f"HIGH must be greater than LOW in {item!r}")
        ranges.append((low, high))
    if not ranges:
        raise argparse.ArgumentTypeError("at least one range is required")
    return ranges


def parse_segment_size_list(raw: str | None, fallback: int) -> list[int]:
    if raw is None:
        return [fallback]
    values: list[int] = []
    seen: set[int] = set()
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        value = parse_nonnegative_int(item, "segment size")
        if value not in seen:
            values.append(value)
            seen.add(value)
    if not values:
        raise argparse.ArgumentTypeError("at least one segment size is required")
    return values


def parse_circle_count_modes(raw: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        if item not in VALID_CIRCLE_COUNT_MODES:
            expected = ", ".join(sorted(VALID_CIRCLE_COUNT_MODES))
            raise argparse.ArgumentTypeError(
                f"unknown Circle count mode {item!r}; expected one of: {expected}"
            )
        if item not in seen:
            values.append(item)
            seen.add(item)
    if not values:
        raise argparse.ArgumentTypeError("at least one Circle count mode is required")
    return values


def parse_nonnegative_int(raw: str, label: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be an integer: {raw!r}") from exc
    if value < 0:
        raise argparse.ArgumentTypeError(f"{label} must be nonnegative: {raw!r}")
    return value


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"external prime benchmark failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
