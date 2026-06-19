from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "sidecars" / "PRIME_ENGINE" / "results"
DEFAULT_RANGES = "0:1000000,0:10000000,1000000000:1010000000"
DEFAULT_SEGMENT_SIZES = "4096,8192,16384,32768,65536,131072,196608,262144,524288,1048576,2097152,3145728"
DEFAULT_THREAD_COUNTS = "1,2,4,8"
DEFAULT_COUNT_MODES = "segmented"
COUNT_MODE_PRIORITY = {
    "segmented": 0,
    "balanced": 1,
    "dynamic": 2,
    "prefix-pi": 3,
    "hybrid-wheel30-mark": 4,
    "wheel30-mark": 5,
    "presieve13": 6,
}


@dataclass(frozen=True)
class TuneSample:
    kind: str
    timestamp_utc: str
    timestamp_unix: int
    pass_index: int
    count_mode: str
    low: int
    high: int
    span: int
    segment_size: int
    requested_threads: int
    threads: int
    rounds: int
    count: int
    best_ms: float
    median_ms: float
    rate_per_second: float
    median_rate_per_second: float


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sweep Circle prime-engine count modes, segment sizes, and thread "
            "counts to record the fastest range-count configuration."
        )
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=0.0,
        help="Run duration. Use 0 for one complete sweep.",
    )
    parser.add_argument("--rounds", type=int, default=3, help="Timing rounds per candidate.")
    parser.add_argument(
        "--ranges",
        default=DEFAULT_RANGES,
        help="Comma-separated LOW:HIGH half-open ranges.",
    )
    parser.add_argument(
        "--segment-sizes",
        default=DEFAULT_SEGMENT_SIZES,
        help="Comma-separated segment sizes to sweep.",
    )
    parser.add_argument(
        "--thread-counts",
        default=DEFAULT_THREAD_COUNTS,
        help="Comma-separated requested thread counts to sweep.",
    )
    parser.add_argument(
        "--count-modes",
        default=DEFAULT_COUNT_MODES,
        help=(
            "Comma-separated count modes to sweep: segmented, balanced, "
            "dynamic, prefix-pi, presieve13, wheel30-mark, hybrid-wheel30-mark."
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument(
        "--output-prefix",
        help="Filename prefix for CSV and JSON outputs. Defaults to a UTC timestamp.",
    )
    parser.add_argument(
        "--no-latest",
        action="store_true",
        help="Do not refresh prime_engine_tuning_latest.csv/json.",
    )
    args = parser.parse_args()

    if args.seconds < 0:
        parser.error("--seconds must be nonnegative")
    if args.rounds <= 0:
        parser.error("--rounds must be positive")

    ranges = parse_ranges(args.ranges)
    segment_sizes = parse_segment_sizes(args.segment_sizes)
    thread_counts = parse_thread_counts(args.thread_counts)
    count_modes = parse_count_modes(args.count_modes)
    cargo = require_cargo()
    binary = build_release_binary(cargo)
    cli_binary = build_release_cli(cargo)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started_at_utc = utc_stamp()
    prefix = args.output_prefix or f"prime_engine_tuning_{started_at_utc}"
    csv_path = args.output_dir / f"{prefix}.csv"
    summary_path = args.output_dir / f"{prefix}.json"

    started = time.perf_counter()
    print(f"tuning output: {csv_path}")
    samples = stream_rust_tuner(
        binary=binary,
        csv_path=csv_path,
        timestamp_utc=started_at_utc,
        seconds=args.seconds,
        rounds=args.rounds,
        ranges=args.ranges,
        segment_sizes=args.segment_sizes,
        thread_counts=args.thread_counts,
        count_modes=args.count_modes,
    )

    if not samples:
        raise RuntimeError("tuner produced no samples")

    finished_at_utc = utc_stamp()
    summary = build_summary(
        samples=samples,
        ranges=ranges,
        segment_sizes=segment_sizes,
        thread_counts=thread_counts,
        count_modes=count_modes,
        rounds=args.rounds,
        sample_output=relative_to_root(csv_path),
        started_at_utc=started_at_utc,
        finished_at_utc=finished_at_utc,
        elapsed_seconds=time.perf_counter() - started,
        cli_binary=cli_binary,
    )
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"wrote tuning summary: {summary_path}")

    if not args.no_latest:
        latest_csv = args.output_dir / "prime_engine_tuning_latest.csv"
        latest_json = args.output_dir / "prime_engine_tuning_latest.json"
        latest_csv.write_text(csv_path.read_text())
        latest_json.write_text(summary_path.read_text())
        print(f"refreshed latest tuning files: {latest_csv}, {latest_json}")

    print_best_summary(summary)
    return 0


def stream_rust_tuner(
    *,
    binary: Path,
    csv_path: Path,
    timestamp_utc: str,
    seconds: float,
    rounds: int,
    ranges: str,
    segment_sizes: str,
    thread_counts: str,
    count_modes: str,
) -> list[TuneSample]:
    command = [
        str(binary),
        "--seconds",
        str(seconds),
        "--rounds",
        str(rounds),
        "--ranges",
        ranges,
        "--segment-sizes",
        segment_sizes,
        "--thread-counts",
        thread_counts,
        "--count-modes",
        count_modes,
    ]
    print("+ " + " ".join(command))
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
    )
    assert process.stdout is not None

    samples: list[TuneSample] = []
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(TuneSample.__dataclass_fields__))
        writer.writeheader()
        reader = csv.DictReader(process.stdout)
        for row in reader:
            sample = rust_row_to_sample(row, timestamp_utc)
            samples.append(sample)
            writer.writerow(asdict(sample))
            handle.flush()
            print_sample(sample, best_for_range(samples, sample.low, sample.high))

    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"Rust tuner exited with status {return_code}")
    return samples


def rust_row_to_sample(row: dict[str, str], timestamp_utc: str) -> TuneSample:
    best_ms = float(row["best_ms"])
    rate_per_second = float(row["rate_per_second"])
    median_ms = float(row.get("median_ms") or best_ms)
    median_rate_per_second = float(row.get("median_rate_per_second") or rate_per_second)
    return TuneSample(
        kind=row["kind"],
        timestamp_utc=timestamp_utc,
        timestamp_unix=int(row["timestamp_unix"]),
        pass_index=int(row["pass"]),
        count_mode=row.get("count_mode") or "segmented",
        low=int(row["low"]),
        high=int(row["high"]),
        span=int(row["span"]),
        segment_size=int(row["segment_size"]),
        requested_threads=int(row.get("requested_threads", "1")),
        threads=int(row.get("threads", row.get("requested_threads", "1"))),
        rounds=int(row["rounds"]),
        count=int(row["count"]),
        best_ms=best_ms,
        median_ms=median_ms,
        rate_per_second=rate_per_second,
        median_rate_per_second=median_rate_per_second,
    )


def build_summary(
    *,
    samples: list[TuneSample],
    ranges: list[tuple[int, int]],
    segment_sizes: list[int],
    thread_counts: list[int],
    count_modes: list[str],
    rounds: int,
    sample_output: str,
    started_at_utc: str,
    finished_at_utc: str,
    elapsed_seconds: float,
    cli_binary: Path,
) -> dict[str, object]:
    best_ranges = []
    for low, high in ranges:
        best = best_for_range(samples, low, high)
        if best is not None:
            best_ranges.append(
                {
                    "low": low,
                    "high": high,
                    "span": high - low,
                    "best": asdict(best),
                    "samples": sum(1 for sample in samples if sample.low == low and sample.high == high),
                }
            )

    best_overall = max(
        samples,
        key=lambda sample: (sample.median_rate_per_second, sample.rate_per_second),
        default=None,
    )
    default_alignment = [
        default_alignment_for_best_range(row["best"], cli_binary)
        for row in best_ranges
    ]
    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "elapsed_seconds": elapsed_seconds,
        "rounds": rounds,
        "sample_output": sample_output,
        "ranges": [{"low": low, "high": high, "span": high - low} for low, high in ranges],
        "segment_sizes": segment_sizes,
        "thread_counts": thread_counts,
        "count_modes": count_modes,
        "sample_count": len(samples),
        "best_by_range": best_ranges,
        "best_overall": asdict(best_overall) if best_overall is not None else None,
        "default_alignment": default_alignment,
    }


def build_release_binary(cargo: str) -> Path:
    print("+ " + " ".join([cargo, "build", "--release", "-p", "circle-prime", "--bin", "circle-prime-tune"]))
    subprocess.run(
        [cargo, "build", "--release", "-p", "circle-prime", "--bin", "circle-prime-tune"],
        cwd=ROOT,
        check=True,
    )
    suffix = ".exe" if sys.platform == "win32" else ""
    return ROOT / "target" / "release" / f"circle-prime-tune{suffix}"


def build_release_cli(cargo: str) -> Path:
    print("+ " + " ".join([cargo, "build", "--release", "-p", "circle-prime", "--bin", "circle-prime"]))
    subprocess.run(
        [cargo, "build", "--release", "-p", "circle-prime", "--bin", "circle-prime"],
        cwd=ROOT,
        check=True,
    )
    suffix = ".exe" if sys.platform == "win32" else ""
    return ROOT / "target" / "release" / f"circle-prime{suffix}"


def default_alignment_for_best_range(best: dict[str, object], cli_binary: Path) -> dict[str, object]:
    low = int(best["low"])
    high = int(best["high"])
    requested_threads = int(best["requested_threads"])
    recommendation = recommend_count_default(cli_binary, low, high, requested_threads)
    return {
        "low": low,
        "high": high,
        "span": int(best["span"]),
        "count": int(best["count"]),
        "best_count_mode": str(best.get("count_mode", "segmented")),
        "best_segment_size": int(best["segment_size"]),
        "best_threads": int(best["threads"]),
        "best_requested_threads": requested_threads,
        "best_ms": float(best["best_ms"]),
        "median_ms": float(best.get("median_ms", best["best_ms"])),
        "default_count_mode": str(recommendation.get("count_mode", "segmented")),
        "default_segment_size": int(recommendation["segment_size"]),
        "default_threads": int(recommendation["threads"]),
        "default_requested_threads": int(recommendation["requested_threads"]),
        "count_mode_aligned": str(best.get("count_mode", "segmented"))
        == str(recommendation.get("count_mode", "segmented")),
        "segment_size_aligned": int(best["segment_size"]) == int(recommendation["segment_size"]),
        "threads_aligned": int(best["threads"]) == int(recommendation["threads"]),
    }


def recommend_count_default(
    cli_binary: Path,
    low: int,
    high: int,
    requested_threads: int,
) -> dict[str, object]:
    completed = subprocess.run(
        [
            str(cli_binary),
            "recommend",
            str(low),
            str(high),
            "--count",
            "--json",
            "--threads",
            str(requested_threads),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def best_for_range(samples: list[TuneSample], low: int, high: int) -> TuneSample | None:
    candidates = [sample for sample in samples if sample.low == low and sample.high == high]
    return min(candidates, key=robust_sample_key, default=None)


def robust_sample_key(sample: TuneSample) -> tuple[float, float, int, int, int]:
    return (
        sample.median_ms,
        sample.best_ms,
        COUNT_MODE_PRIORITY.get(sample.count_mode, 99),
        sample.segment_size,
        sample.requested_threads,
    )


def print_sample(sample: TuneSample, best: TuneSample | None) -> None:
    best_note = ""
    if (
        best is not None
        and best.segment_size == sample.segment_size
        and best.requested_threads == sample.requested_threads
        and best.count_mode == sample.count_mode
        and best.median_ms == sample.median_ms
    ):
        best_note = " best"
    print(
        f"[{sample.low},{sample.high}) mode={sample.count_mode} seg={sample.segment_size} "
        f"threads={sample.threads}/{sample.requested_threads} "
        f"count={sample.count} best={sample.best_ms:.3f}ms "
        f"median={sample.median_ms:.3f}ms "
        f"rate={sample.median_rate_per_second:.0f}/s{best_note}"
    )


def print_best_summary(summary: dict[str, object]) -> None:
    print("median-selected count configurations:")
    for row in summary["best_by_range"]:  # type: ignore[index]
        best = row["best"]
        print(
            f"  [{row['low']},{row['high']}) -> seg={best['segment_size']} "
            f"mode={best.get('count_mode', 'segmented')} "
            f"threads={best['threads']}/{best['requested_threads']} "
            f"best={best['best_ms']:.3f}ms median={best['median_ms']:.3f}ms "
            f"rate={best['median_rate_per_second']:.0f}/s"
        )


def require_cargo() -> str:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("cargo is required to tune the Rust prime engine")
    return cargo


def parse_ranges(raw: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for item in split_csv(raw):
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


def parse_segment_sizes(raw: str) -> list[int]:
    values = [parse_nonnegative_int(item, "segment size") for item in split_csv(raw)]
    values = sorted(set(values))
    if not values:
        raise argparse.ArgumentTypeError("at least one segment size is required")
    if values[0] == 0:
        raise argparse.ArgumentTypeError("segment sizes must be positive")
    return values


def parse_thread_counts(raw: str) -> list[int]:
    values = [parse_nonnegative_int(item, "thread count") for item in split_csv(raw)]
    values = sorted(set(values))
    if not values:
        raise argparse.ArgumentTypeError("at least one thread count is required")
    if values[0] == 0:
        raise argparse.ArgumentTypeError("thread counts must be positive")
    return values


def parse_count_modes(raw: str) -> list[str]:
    values = split_csv(raw)
    unknown = [value for value in values if value not in COUNT_MODE_PRIORITY]
    if unknown:
        expected = ", ".join(COUNT_MODE_PRIORITY)
        raise argparse.ArgumentTypeError(
            f"unknown count mode(s): {', '.join(unknown)}; expected one of {expected}"
        )
    values = sorted(set(values), key=lambda mode: COUNT_MODE_PRIORITY[mode])
    if not values:
        raise argparse.ArgumentTypeError("at least one count mode is required")
    return values


def parse_nonnegative_int(raw: str, label: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be an integer: {raw!r}") from exc
    if value < 0:
        raise argparse.ArgumentTypeError(f"{label} must be nonnegative: {raw!r}")
    return value


def split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def relative_to_root(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"prime engine tuning failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
