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
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANGES = "0:10000000,0:100000000,1000000000000:1000010000000"
DEFAULT_CIRCLE_COUNT_MODES = "segmented"
VALID_CIRCLE_COUNT_MODES = {
    "default",
    "segmented",
    "balanced",
    "dynamic",
    "prefix-pi",
    "presieve13",
    "presieve17",
    "wheel30-mark",
    "hybrid-wheel30-mark",
}
VALID_EXTERNAL_BASELINES = {
    "external_primesieve_count",
    "external_primecount_pi_diff",
    "external_primesieve_count_server",
}
PRIMESIEVE_COUNT_SERVER_SOURCE = (
    ROOT / "sidecars" / "PRIME_ENGINE" / "controls" / "primesieve_count_server.c"
)
PRIMESIEVE_COUNT_SERVER_BINARY = ROOT / "target" / "prime-controls" / "primesieve-count-server"
SAMPLE_NOISY_MAX_OVER_MEDIAN = 1.5
SAMPLE_ROBUST_NOISE_MIN_COUNT = 5


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
    sample_count: int = 0
    sample_noise_ms: str = ""
    sample_max_ms: str = ""
    sample_noise_over_median: str = ""
    sample_max_over_median: str = ""
    sample_ignored_single_high_outlier: str = ""
    sample_stability: str = ""


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
    close: Callable[[], None] | None = None


@dataclass(frozen=True)
class CircleVariant:
    segment_size: int
    count_mode: str
    threads: int | None = None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark Circle prime counts against external primesieve/primecount controls."
    )
    parser.add_argument("--ranges", default=DEFAULT_RANGES)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help=(
            "Repeat each identical count request this many times inside one "
            "timed sample and report per-request average milliseconds. This "
            "keeps short runs useful for sub-10 ms persistent-server comparisons."
        ),
    )
    parser.add_argument(
        "--warmup-rounds",
        type=int,
        default=0,
        help=(
            "Run this many unrecorded interleaved warmup passes before timing. "
            "Useful for short competitive runs where first-call library/cache "
            "setup would otherwise dominate the median."
        ),
    )
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
            "balanced, dynamic, prefix-pi, presieve13, presieve17, wheel30-mark, and hybrid-wheel30-mark."
        ),
    )
    parser.add_argument(
        "--circle-variant",
        action="append",
        default=[],
        metavar="MODE:SEGMENT_SIZE[:THREADS]",
        help=(
            "Exact Circle variant to benchmark. Repeat to avoid the default "
            "segment-size by count-mode cross product, e.g. "
            "--circle-variant default:0 --circle-variant segmented:262144. "
            "Append :THREADS to override --circle-threads for that variant."
        ),
    )
    parser.add_argument(
        "--include-circle-server",
        action="store_true",
        help=(
            "Also benchmark persistent circle-prime count-server requests for "
            "the same Circle variants. Requires --interleaved."
        ),
    )
    parser.add_argument(
        "--circle-server-only",
        action="store_true",
        help=(
            "With --include-circle-server, time only persistent Circle "
            "count-server rows and skip cold circle-prime range subprocess rows. "
            "Use for focused hot-server comparisons."
        ),
    )
    parser.add_argument(
        "--include-primesieve-count-server",
        action="store_true",
        help=(
            "Also benchmark a persistent helper linked against libprimesieve "
            "and using primesieve_count_primes(LOW, HIGH-1). Requires --interleaved."
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
    parser.add_argument(
        "--external-baselines",
        help=(
            "Comma-separated external timing rows to include. Defaults to the "
            "legacy behavior: installed primesieve/primecount CLIs plus the "
            "libprimesieve count server when requested. Use "
            "external_primesieve_count_server for focused hot-server comparisons."
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
        choices=("primesieve", "primecount", "primesieve-library"),
        action="append",
        default=[],
        help=(
            "Fail if the named external control is unavailable. Repeat this "
            "flag to require both serious baselines."
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
    args = parser.parse_args()

    if args.rounds <= 0:
        parser.error("--rounds must be positive")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if args.warmup_rounds < 0:
        parser.error("--warmup-rounds must be nonnegative")
    if args.segment_size < 0:
        parser.error("--segment-size must be nonnegative")
    if args.circle_threads <= 0:
        parser.error("--circle-threads must be positive")
    if args.external_threads < 0:
        parser.error("--external-threads must be nonnegative")
    if args.sample_output is not None and not args.interleaved:
        parser.error("--sample-output requires --interleaved")
    if args.include_circle_server and not args.interleaved:
        parser.error("--include-circle-server requires --interleaved")
    if args.circle_server_only and not args.include_circle_server:
        parser.error("--circle-server-only requires --include-circle-server")
    if (
        args.include_primesieve_count_server or "primesieve-library" in args.require_tool
    ) and not args.interleaved:
        parser.error("--include-primesieve-count-server requires --interleaved")

    ranges = parse_ranges(args.ranges)
    try:
        segment_sizes = parse_segment_size_list(args.segment_sizes, args.segment_size)
        circle_count_modes = parse_circle_count_modes(args.circle_count_modes)
        circle_variants = parse_circle_variants(
            args.circle_variant,
            segment_sizes,
            circle_count_modes,
        )
        external_baselines = parse_external_baselines(args.external_baselines)
        segment_sizes = unique_preserving_order(
            variant.segment_size for variant in circle_variants
        )
        circle_count_modes = unique_preserving_order(
            variant.count_mode for variant in circle_variants
        )
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    started_at_utc = utc_now()
    primesieve = shutil.which("primesieve")
    primecount = shutil.which("primecount")
    include_primesieve_count_server = (
        args.include_primesieve_count_server
        or "primesieve-library" in args.require_tool
        or external_baseline_enabled(
            external_baselines,
            "external_primesieve_count_server",
        )
    )
    primesieve_count_server: Path | None = None
    primesieve_count_server_error: str | None = None
    if include_primesieve_count_server:
        try:
            primesieve_count_server = build_primesieve_count_server(args)
        except Exception as exc:
            primesieve_count_server_error = str(exc)
            if "primesieve-library" not in args.require_tool:
                print(
                    "skipping libprimesieve count helper: "
                    f"{primesieve_count_server_error}",
                    file=sys.stderr,
                )

    missing_required = required_external_tools_missing(
        args.require_tool,
        primesieve=primesieve,
        primecount=primecount,
        primesieve_library=primesieve_count_server,
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
            primesieve_count_server=primesieve_count_server,
            primesieve_count_server_error=primesieve_count_server_error,
            row_count=0,
        )
        emit_metadata(metadata, args.metadata_output)
        tools = ", ".join(missing_required)
        raise RuntimeError(
            f"required external control(s) unavailable: {tools}; "
            "install with `brew install primesieve primecount`"
        )

    missing_selected_baselines = selected_external_baselines_missing(
        external_baselines,
        primesieve=primesieve,
        primecount=primecount,
        primesieve_library=primesieve_count_server,
    )
    if missing_selected_baselines:
        metadata = build_run_metadata(
            args=args,
            segment_sizes=segment_sizes,
            circle_count_modes=circle_count_modes,
            circle_variants=circle_variants,
            external_baselines=external_baselines,
            ranges=ranges,
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=primesieve,
            primecount=primecount,
            primesieve_count_server=primesieve_count_server,
            primesieve_count_server_error=primesieve_count_server_error,
            row_count=0,
        )
        emit_metadata(metadata, args.metadata_output)
        baselines = ", ".join(missing_selected_baselines)
        raise RuntimeError(f"selected external baseline(s) unavailable: {baselines}")

    if not any_external_baseline_available(
        external_baselines,
        primesieve=primesieve,
        primecount=primecount,
        primesieve_library=primesieve_count_server,
    ):
        metadata = build_run_metadata(
            args=args,
            segment_sizes=segment_sizes,
            circle_count_modes=circle_count_modes,
            circle_variants=circle_variants,
            external_baselines=external_baselines,
            ranges=ranges,
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=None,
            primecount=None,
            primesieve_count_server=primesieve_count_server,
            primesieve_count_server_error=primesieve_count_server_error,
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
                external_baselines=external_baselines,
                circle_variants=circle_variants,
                circle_threads=args.circle_threads,
                external_threads=args.external_threads,
                rounds=args.rounds,
                batch_size=args.batch_size,
                warmup_rounds=args.warmup_rounds,
                include_circle_server=args.include_circle_server,
                circle_server_only=args.circle_server_only,
                primesieve_count_server=primesieve_count_server,
            )
            rows.extend(range_rows)
            samples.extend(range_samples)
        else:
            circle_rows: list[ExternalBenchRow] = []
            seen_circle_variants: set[tuple[str, int, int]] = set()
            for variant in circle_variants:
                variant_threads = variant.threads or args.circle_threads
                circle_row = measure_circle_prime(
                    circle_prime,
                    low,
                    high,
                    variant.segment_size,
                    variant_threads,
                    args.rounds,
                    args.batch_size,
                    variant.count_mode,
                )
                variant_key = (circle_row.name, circle_row.segment_size, circle_row.threads)
                if variant_key not in seen_circle_variants:
                    circle_rows.append(circle_row)
                    seen_circle_variants.add(variant_key)
            rows.extend(circle_rows)

            if (
                external_baseline_enabled(
                    external_baselines,
                    "external_primesieve_count",
                )
                and primesieve is not None
            ):
                row = measure_primesieve(
                    primesieve,
                    low,
                    high,
                    args.rounds,
                    args.batch_size,
                    args.external_threads,
                )
                rows.append(row)
                for circle_row in circle_rows:
                    verify_count(circle_row, row)
                    rows.append(speedup_row(circle_row, row))

            if (
                external_baseline_enabled(
                    external_baselines,
                    "external_primecount_pi_diff",
                )
                and primecount is not None
            ):
                row = measure_primecount(
                    primecount,
                    low,
                    high,
                    args.rounds,
                    args.batch_size,
                    args.external_threads,
                )
                rows.append(row)
                for circle_row in circle_rows:
                    verify_count(circle_row, row)
                    rows.append(speedup_row(circle_row, row))
            if external_baseline_enabled(
                external_baselines,
                "external_primesieve_count_server",
            ) and primesieve_count_server is not None:
                row = measure_primesieve_count_server(
                    primesieve_count_server,
                    low,
                    high,
                    args.rounds,
                    args.batch_size,
                    args.external_threads,
                )
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
        circle_variants=circle_variants,
        external_baselines=external_baselines,
        ranges=ranges,
        started_at_utc=started_at_utc,
        cargo=cargo,
        circle_prime=circle_prime,
        primesieve=primesieve,
        primecount=primecount,
        primesieve_count_server=primesieve_count_server,
        primesieve_count_server_error=primesieve_count_server_error,
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
    batch_size: int = 1,
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
        batch_size=batch_size,
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


class CountServerClient:
    def __init__(
        self,
        binary: Path,
        *,
        default_segment_size: int = 0,
        default_threads: int = 1,
        default_count_mode: str = "default",
    ) -> None:
        self.process = subprocess.Popen(
            count_server_command(
                binary,
                default_segment_size=default_segment_size,
                default_threads=default_threads,
                default_count_mode=default_count_mode,
            ),
            cwd=ROOT,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if self.process.stdin is None or self.process.stdout is None:
            self.close()
            raise RuntimeError("failed to open count-server pipes")

    def count(
        self,
        low: int,
        high: int,
        segment_size: int,
        threads: int,
        count_mode: str,
        *,
        use_request_defaults: bool = False,
    ) -> int:
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        request = count_server_request(
            low,
            high,
            segment_size,
            threads,
            count_mode,
            use_request_defaults=use_request_defaults,
        )
        self.process.stdin.write(request)
        self.process.stdin.flush()
        response = self.process.stdout.readline()
        if response == "":
            stderr = self._read_stderr()
            raise RuntimeError(f"count-server exited without a response: {stderr}")
        return parse_integer_output(response)

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


def circle_prime_server_measurement(
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
    metadata_count = int(metadata["count"])
    resolved_count_mode = str(metadata.get("count_mode", count_mode))
    use_request_defaults = count_mode == "default"
    client = CountServerClient(
        binary,
        default_segment_size=segment_size if use_request_defaults else 0,
        default_threads=threads if use_request_defaults else 1,
        default_count_mode=count_mode if use_request_defaults else "default",
    )

    def run_once() -> int:
        count = client.count(
            low,
            high,
            actual_segment_size,
            threads,
            resolved_count_mode,
            use_request_defaults=use_request_defaults,
        )
        if count != metadata_count:
            raise AssertionError(
                f"Circle count-server disagreed with JSON metadata for [{low},{high}): "
                f"metadata {metadata_count}, server {count}"
            )
        return count

    name = circle_server_measurement_name(count_mode, actual_threads)
    return Measurement(
        name=name,
        low=low,
        high=high,
        segment_size=actual_segment_size,
        threads=actual_threads,
        requested_threads=threads,
        run_once=run_once,
        count_mode=resolved_count_mode,
        close=client.close,
    )


def count_server_command(
    binary: Path,
    *,
    default_segment_size: int = 0,
    default_threads: int = 1,
    default_count_mode: str = "default",
) -> list[str]:
    command = [str(binary), "count-server"]
    if default_segment_size > 0:
        command.extend(["--segment-size", str(default_segment_size)])
    if default_threads != 1:
        command.extend(["--threads", str(default_threads)])
    if default_count_mode != "default":
        command.extend(["--count-mode", default_count_mode])
    return command


def count_server_request(
    low: int,
    high: int,
    segment_size: int,
    threads: int,
    count_mode: str,
    *,
    use_request_defaults: bool = False,
) -> str:
    if use_request_defaults:
        return f"{low} {high}\n"
    return f"{low} {high} {segment_size} {threads} {count_mode}\n"


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


def circle_server_measurement_name(count_mode: str, actual_threads: int) -> str:
    suffix = count_mode.replace("-", "_")
    name = f"circle_prime_server_{suffix}_count"
    if actual_threads != 1:
        name = f"circle_prime_server_parallel_{suffix}_count_{actual_threads}t"
    return name


def measure_primesieve(
    binary: str,
    low: int,
    high: int,
    rounds: int,
    batch_size: int,
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
        batch_size=batch_size,
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
    batch_size: int,
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
        batch_size=batch_size,
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


class PrimeRangeServerClient:
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

    def count(self, low: int, high: int, threads: int) -> int:
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.process.stdin.write(f"{low} {high} {threads}\n")
        self.process.stdin.flush()
        response = self.process.stdout.readline()
        if response == "":
            stderr = self._read_stderr()
            raise RuntimeError(f"{self.label} exited without a response: {stderr}")
        return parse_integer_output(response)

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


def measure_primesieve_count_server(
    binary: Path,
    low: int,
    high: int,
    rounds: int,
    batch_size: int,
    threads: int,
) -> ExternalBenchRow:
    measurement = primesieve_count_server_measurement(binary, low, high, threads)
    try:
        row = measure(
            measurement.name,
            low,
            high,
            0,
            rounds,
            measurement.run_once,
            batch_size=batch_size,
            threads=measurement.threads,
            requested_threads=measurement.requested_threads,
        )
        return row
    finally:
        if measurement.close is not None:
            measurement.close()


def primesieve_count_server_measurement(
    binary: Path,
    low: int,
    high: int,
    threads: int,
) -> Measurement:
    if high <= low:
        raise ValueError(f"empty range [{low},{high})")
    client = PrimeRangeServerClient(
        [str(binary)],
        "libprimesieve count helper",
    )
    expected_count: int | None = None

    def run_once() -> int:
        nonlocal expected_count
        count = client.count(low, high, threads)
        if expected_count is None:
            expected_count = count
        elif count != expected_count:
            raise AssertionError(
                "libprimesieve count result changed for "
                f"[{low},{high}): expected {expected_count}, got {count}"
            )
        return count

    return Measurement(
        name="external_primesieve_count_server",
        low=low,
        high=high,
        segment_size=0,
        threads=threads,
        requested_threads=threads,
        run_once=run_once,
        close=client.close,
    )


def measure_range_interleaved(
    *,
    circle_prime: Path,
    primesieve: str | None,
    primecount: str | None,
    primesieve_count_server: Path | None,
    low: int,
    high: int,
    external_baselines: set[str] | None,
    circle_variants: list[CircleVariant],
    circle_threads: int,
    external_threads: int,
    rounds: int,
    batch_size: int,
    warmup_rounds: int = 0,
    include_circle_server: bool = False,
    circle_server_only: bool = False,
) -> tuple[list[ExternalBenchRow], list[ExternalBenchSample]]:
    circle_measurements: list[Measurement] = []
    seen_circle_variants: set[tuple[str, int, int]] = set()
    for variant in circle_variants:
        variant_threads = variant.threads or circle_threads
        if not circle_server_only:
            measurement = circle_prime_measurement(
                circle_prime,
                low,
                high,
                variant.segment_size,
                variant_threads,
                variant.count_mode,
            )
            variant_key = (measurement.name, measurement.segment_size, measurement.threads)
            if variant_key not in seen_circle_variants:
                circle_measurements.append(measurement)
                seen_circle_variants.add(variant_key)
        if include_circle_server:
            server_measurement = circle_prime_server_measurement(
                circle_prime,
                low,
                high,
                variant.segment_size,
                variant_threads,
                variant.count_mode,
            )
            server_variant_key = (
                server_measurement.name,
                server_measurement.segment_size,
                server_measurement.threads,
            )
            if server_variant_key not in seen_circle_variants:
                circle_measurements.append(server_measurement)
                seen_circle_variants.add(server_variant_key)
            else:
                if server_measurement.close is not None:
                    server_measurement.close()

    baseline_measurements = []
    if (
        external_baseline_enabled(external_baselines, "external_primesieve_count")
        and primesieve is not None
    ):
        baseline_measurements.append(
            primesieve_measurement(primesieve, low, high, external_threads)
        )
    if (
        external_baseline_enabled(external_baselines, "external_primecount_pi_diff")
        and primecount is not None
    ):
        baseline_measurements.append(
            primecount_measurement(primecount, low, high, external_threads)
        )
    if (
        external_baseline_enabled(
            external_baselines,
            "external_primesieve_count_server",
        )
        and primesieve_count_server is not None
    ):
        baseline_measurements.append(
            primesieve_count_server_measurement(
                primesieve_count_server,
                low,
                high,
                external_threads,
            )
        )

    measurements = [*circle_measurements, *baseline_measurements]
    try:
        timing_rows, samples = measure_interleaved(
            measurements,
            rounds,
            batch_size=batch_size,
            warmup_rounds=warmup_rounds,
        )
    finally:
        for measurement in measurements:
            if measurement.close is not None:
                measurement.close()
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
    *,
    batch_size: int = 1,
    warmup_rounds: int = 0,
) -> tuple[list[ExternalBenchRow], list[ExternalBenchSample]]:
    if not measurements:
        return [], []
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    timings: dict[str, list[float]] = {measurement_key(m): [] for m in measurements}
    results: dict[str, int] = {}
    samples: list[ExternalBenchSample] = []
    for warmup_index in range(warmup_rounds):
        for measurement in rotated(measurements, warmup_index):
            key = measurement_key(measurement)
            result = run_batch(measurement, batch_size)
            expected = results.setdefault(key, result)
            if result != expected:
                raise AssertionError(
                    f"{measurement.name} result changed during warmup"
                )
    for round_index in range(rounds):
        order = rotated(measurements, round_index)
        for measurement in order:
            key = measurement_key(measurement)
            start = time.perf_counter()
            result = run_batch(measurement, batch_size)
            elapsed = (time.perf_counter() - start) / batch_size
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


def run_batch(measurement: Measurement, batch_size: int) -> int:
    result = measurement.run_once()
    for _ in range(1, batch_size):
        repeated = measurement.run_once()
        if repeated != result:
            raise AssertionError(
                f"{measurement.name} result changed inside a timed batch"
            )
    return result


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
        **sample_metric_fields(timings),
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
    batch_size: int = 1,
    threads: int,
    requested_threads: int,
) -> ExternalBenchRow:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    expected = None
    timings: list[float] = []
    for _ in range(rounds):
        start = time.perf_counter()
        result = run_once()
        for _ in range(1, batch_size):
            repeated = run_once()
            if repeated != result:
                raise AssertionError(f"{name} result changed inside a timed batch")
        elapsed = (time.perf_counter() - start) / batch_size
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
        **sample_metric_fields(timings),
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
        **speedup_sample_metric_fields(circle_row, baseline),
    )


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute median of empty values")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def sample_metric_fields(timings: list[float]) -> dict[str, Any]:
    if not timings:
        return {
            "sample_count": 0,
            "sample_noise_ms": "",
            "sample_max_ms": "",
            "sample_noise_over_median": "",
            "sample_max_over_median": "",
            "sample_ignored_single_high_outlier": "",
            "sample_stability": "",
        }
    ordered_ms = sorted(timing * 1000.0 for timing in timings)
    median_ms = median(ordered_ms)
    max_ms = ordered_ms[-1]
    noise_ms = (
        ordered_ms[-2]
        if len(ordered_ms) >= SAMPLE_ROBUST_NOISE_MIN_COUNT
        else max_ms
    )
    max_over_median = max_ms / median_ms if median_ms > 0 else None
    noise_over_median = noise_ms / median_ms if median_ms > 0 else None
    ignored_single_high_outlier = len(ordered_ms) >= SAMPLE_ROBUST_NOISE_MIN_COUNT
    stability = (
        "noisy"
        if noise_over_median is not None
        and noise_over_median > SAMPLE_NOISY_MAX_OVER_MEDIAN
        else "stable"
    )
    return {
        "sample_count": len(ordered_ms),
        "sample_noise_ms": f"{noise_ms:.6f}",
        "sample_max_ms": f"{max_ms:.6f}",
        "sample_noise_over_median": (
            f"{noise_over_median:.6f}" if noise_over_median is not None else ""
        ),
        "sample_max_over_median": (
            f"{max_over_median:.6f}" if max_over_median is not None else ""
        ),
        "sample_ignored_single_high_outlier": (
            "true" if ignored_single_high_outlier else "false"
        ),
        "sample_stability": stability,
    }


def speedup_sample_metric_fields(
    circle_row: ExternalBenchRow,
    baseline: ExternalBenchRow,
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
    circle_variants: list[CircleVariant] | None = None,
    external_baselines: set[str] | None = None,
    ranges: list[tuple[int, int]],
    started_at_utc: str,
    cargo: str | None,
    circle_prime: Path | None,
    primesieve: str | None,
    primecount: str | None,
    primesieve_count_server: Path | None = None,
    primesieve_count_server_error: str | None = None,
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
    if circle_variants is None:
        circle_variants = parse_circle_variants(
            getattr(args, "circle_variant", []),
            segment_sizes,
            circle_count_modes,
        )
        segment_sizes = unique_preserving_order(
            variant.segment_size for variant in circle_variants
        )
        circle_count_modes = unique_preserving_order(
            variant.count_mode for variant in circle_variants
        )
    if external_baselines is None and hasattr(args, "external_baselines"):
        external_baselines = parse_external_baselines(args.external_baselines)
    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": utc_now(),
        "row_count": row_count,
        "rounds": args.rounds,
        "batch_size": int(getattr(args, "batch_size", 1)),
        "warmup_rounds": int(getattr(args, "warmup_rounds", 0)),
        "interleaved": bool(getattr(args, "interleaved", False)),
        "include_circle_server": bool(getattr(args, "include_circle_server", False)),
        "circle_server_only": bool(getattr(args, "circle_server_only", False)),
        "include_primesieve_count_server": bool(
            getattr(args, "include_primesieve_count_server", False)
            or "primesieve-library" in getattr(args, "require_tool", [])
        ),
        "sample_output": (
            str(args.sample_output)
            if getattr(args, "sample_output", None) is not None
            else None
        ),
        "requested_segment_size": args.segment_size,
        "requested_segment_sizes": segment_sizes,
        "circle_count_modes": circle_count_modes,
        "circle_variants": [circle_variant_metadata(variant) for variant in circle_variants],
        "external_baselines": (
            sorted(external_baselines) if external_baselines is not None else None
        ),
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
            "primesieve_count_server": {
                "available": primesieve_count_server is not None,
                "path": (
                    str(primesieve_count_server)
                    if primesieve_count_server is not None
                    else None
                ),
                "source": str(PRIMESIEVE_COUNT_SERVER_SOURCE),
                "method": "primesieve_count_primes(LOW, HIGH-1)",
                "error": primesieve_count_server_error,
            },
        },
        "range_commands": range_command_metadata(
            circle_binary,
            primesieve,
            primecount,
            primesieve_count_server,
            ranges,
            circle_variants,
            external_baselines,
            args.circle_threads,
            args.external_threads,
            include_circle_server=bool(getattr(args, "include_circle_server", False)),
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


def circle_variant_metadata(variant: CircleVariant) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "segment_size": variant.segment_size,
        "count_mode": variant.count_mode,
    }
    if variant.threads is not None:
        metadata["threads"] = variant.threads
    return metadata


def circle_count_server_variant_metadata(
    circle_prime: Path,
    low: int,
    high: int,
    variant: CircleVariant,
    circle_threads: int,
) -> dict[str, Any]:
    variant_threads = variant.threads or circle_threads
    use_request_defaults = variant.count_mode == "default"
    metadata: dict[str, Any] = {
        "command": count_server_command(
            circle_prime,
            default_segment_size=variant.segment_size if use_request_defaults else 0,
            default_threads=variant_threads if use_request_defaults else 1,
            default_count_mode=variant.count_mode if use_request_defaults else "default",
        ),
        "uses_server_defaults": use_request_defaults,
    }
    if use_request_defaults or variant.segment_size > 0:
        metadata["request"] = count_server_request(
            low,
            high,
            variant.segment_size,
            variant_threads,
            variant.count_mode,
            use_request_defaults=use_request_defaults,
        ).strip()
    else:
        metadata["request_template"] = (
            f"{low} {high} <resolved_segment_size> {variant_threads} "
            f"{variant.count_mode}"
        )
        metadata["request_resolves_segment_size_from_json_probe"] = True
    return metadata


def external_tool_metadata(name: str, path: str | None, version_args: list[str]) -> dict[str, Any]:
    if path is None:
        return {"available": False, "path": None, "version": None}
    return {
        "available": True,
        "path": path,
        "version": command_output([path, *version_args]),
    }


def build_primesieve_count_server(args: argparse.Namespace) -> Path:
    compiler = shutil.which(args.cc)
    if compiler is None:
        raise RuntimeError(f"C compiler {args.cc!r} was not found")
    if not PRIMESIEVE_COUNT_SERVER_SOURCE.exists():
        raise RuntimeError(f"missing helper source: {PRIMESIEVE_COUNT_SERVER_SOURCE}")

    include_dir = args.primesieve_include_dir or autodetect_primesieve_include_dir()
    lib_dir = args.primesieve_lib_dir or autodetect_primesieve_lib_dir()
    PRIMESIEVE_COUNT_SERVER_BINARY.parent.mkdir(parents=True, exist_ok=True)

    command = [
        compiler,
        "-O3",
        "-std=c11",
        "-Wall",
        "-Wextra",
    ]
    if include_dir is not None:
        command.append(f"-I{include_dir}")
    command.extend(
        [
            str(PRIMESIEVE_COUNT_SERVER_SOURCE),
            "-o",
            str(PRIMESIEVE_COUNT_SERVER_BINARY),
        ]
    )
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
            "failed to build libprimesieve count helper"
            + (f": {detail}" if detail else "")
        )
    return PRIMESIEVE_COUNT_SERVER_BINARY


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
    primesieve_count_server: Path | None,
    ranges: list[tuple[int, int]],
    circle_variants: list[CircleVariant],
    external_baselines: set[str] | None,
    circle_threads: int,
    external_threads: int,
    *,
    include_circle_server: bool = False,
) -> list[dict[str, Any]]:
    commands = []
    for low, high in ranges:
        stop = high - 1
        circle_variant_commands = []
        for variant in circle_variants:
            variant_threads = variant.threads or circle_threads
            variant_metadata = {
                **circle_variant_metadata(variant),
                "json_probe": circle_prime_command(
                    circle_prime,
                    low,
                    high,
                    variant.segment_size,
                    variant_threads,
                    variant.count_mode,
                    json_output=True,
                ),
                "timing": circle_prime_command(
                    circle_prime,
                    low,
                    high,
                    variant.segment_size,
                    variant_threads,
                    variant.count_mode,
                    json_output=False,
                ),
            }
            if include_circle_server:
                variant_metadata["count_server"] = circle_count_server_variant_metadata(
                    circle_prime,
                    low,
                    high,
                    variant,
                    circle_threads,
                )
            circle_variant_commands.append(variant_metadata)
        first_variant = circle_variant_commands[0]
        entry: dict[str, Any] = {
            "low": low,
            "high": high,
            "circle_json_probe": first_variant["json_probe"],
            "circle_timing": first_variant["timing"],
            "circle_variants": circle_variant_commands,
        }
        if include_circle_server:
            entry["circle_count_server"] = [str(circle_prime), "count-server"]
        if (
            external_baseline_enabled(external_baselines, "external_primesieve_count")
            and primesieve is not None
        ):
            entry["primesieve"] = primesieve_command(primesieve, low, stop, external_threads)
        if (
            external_baseline_enabled(external_baselines, "external_primecount_pi_diff")
            and primecount is not None
        ):
            entry["primecount_high"] = primecount_command(primecount, stop, external_threads)
            if low > 0:
                entry["primecount_low"] = primecount_command(
                    primecount,
                    low - 1,
                    external_threads,
                )
        if (
            external_baseline_enabled(
                external_baselines,
                "external_primesieve_count_server",
            )
            and primesieve_count_server is not None
        ):
            entry["primesieve_count_server"] = [str(primesieve_count_server)]
        commands.append(entry)
    return commands


def required_external_tools_missing(
    required_tools: list[str],
    *,
    primesieve: str | None,
    primecount: str | None,
    primesieve_library: Path | None = None,
) -> list[str]:
    available = {
        "primesieve": primesieve is not None,
        "primecount": primecount is not None,
        "primesieve-library": primesieve_library is not None,
    }
    return sorted({tool for tool in required_tools if not available[tool]})


def selected_external_baselines_missing(
    selected_baselines: set[str] | None,
    *,
    primesieve: str | None,
    primecount: str | None,
    primesieve_library: Path | None,
) -> list[str]:
    if selected_baselines is None:
        return []
    available = {
        "external_primesieve_count": primesieve is not None,
        "external_primecount_pi_diff": primecount is not None,
        "external_primesieve_count_server": primesieve_library is not None,
    }
    return sorted(
        baseline
        for baseline in selected_baselines
        if not available[baseline]
    )


def any_external_baseline_available(
    selected_baselines: set[str] | None,
    *,
    primesieve: str | None,
    primecount: str | None,
    primesieve_library: Path | None,
) -> bool:
    return (
        (
            external_baseline_enabled(
                selected_baselines,
                "external_primesieve_count",
            )
            and primesieve is not None
        )
        or (
            external_baseline_enabled(
                selected_baselines,
                "external_primecount_pi_diff",
            )
            and primecount is not None
        )
        or (
            external_baseline_enabled(
                selected_baselines,
                "external_primesieve_count_server",
            )
            and primesieve_library is not None
        )
    )


def external_baseline_enabled(
    selected_baselines: set[str] | None,
    baseline: str,
) -> bool:
    return selected_baselines is None or baseline in selected_baselines


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


def parse_external_baselines(raw: str | None) -> set[str] | None:
    if raw is None:
        return None
    values: set[str] = set()
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        if item not in VALID_EXTERNAL_BASELINES:
            expected = ", ".join(sorted(VALID_EXTERNAL_BASELINES))
            raise argparse.ArgumentTypeError(
                f"unknown external baseline {item!r}; expected one of: {expected}"
            )
        values.add(item)
    if not values:
        raise argparse.ArgumentTypeError("at least one external baseline is required")
    return values


def parse_circle_variants(
    raw_variants: list[str] | None,
    segment_sizes: list[int],
    circle_count_modes: list[str],
) -> list[CircleVariant]:
    if not raw_variants:
        return [
            CircleVariant(segment_size=segment_size, count_mode=count_mode)
            for segment_size in segment_sizes
            for count_mode in circle_count_modes
        ]

    variants: list[CircleVariant] = []
    seen: set[CircleVariant] = set()
    for raw in raw_variants:
        for item in [part.strip() for part in raw.split(",") if part.strip()]:
            if ":" not in item:
                raise argparse.ArgumentTypeError(
                    f"Circle variant must be MODE:SEGMENT_SIZE[:THREADS], got {item!r}"
                )
            parts = item.split(":")
            if len(parts) not in {2, 3}:
                raise argparse.ArgumentTypeError(
                    f"Circle variant must be MODE:SEGMENT_SIZE[:THREADS], got {item!r}"
                )
            count_mode, segment_size_raw = parts[0], parts[1]
            if count_mode not in VALID_CIRCLE_COUNT_MODES:
                expected = ", ".join(sorted(VALID_CIRCLE_COUNT_MODES))
                raise argparse.ArgumentTypeError(
                    f"unknown Circle count mode {count_mode!r}; expected one of: {expected}"
                )
            segment_size = parse_nonnegative_int(segment_size_raw, "segment size")
            threads = (
                parse_positive_int(parts[2], "Circle variant threads")
                if len(parts) == 3
                else None
            )
            variant = CircleVariant(
                segment_size=segment_size,
                count_mode=count_mode,
                threads=threads,
            )
            if variant not in seen:
                variants.append(variant)
                seen.add(variant)
    if not variants:
        raise argparse.ArgumentTypeError("at least one Circle variant is required")
    return variants


def unique_preserving_order(values: Iterable[Any]) -> list[Any]:
    result = []
    seen = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def parse_nonnegative_int(raw: str, label: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be an integer: {raw!r}") from exc
    if value < 0:
        raise argparse.ArgumentTypeError(f"{label} must be nonnegative: {raw!r}")
    return value


def parse_positive_int(raw: str, label: str) -> int:
    value = parse_nonnegative_int(raw, label)
    if value == 0:
        raise argparse.ArgumentTypeError(f"{label} must be positive: {raw!r}")
    return value


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"external prime benchmark failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
