from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_prime_benchmark_provenance import benchmark_provenance_failures


DEFAULT_CSV = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_high_offset_count_binary_probe_latest.csv"
)
DEFAULT_METADATA = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_high_offset_count_binary_probe_latest.json"
)
DEFAULT_CIRCLE_PRIME = ROOT / "target" / "release" / "circle-prime"
DEFAULT_CIRCLE_PRIME_COUNT = ROOT / "target" / "release" / "circle-prime-count"
DEFAULT_DEFAULTS = ROOT / "rust" / "circle-prime" / "prime_engine_defaults.json"


@dataclass(frozen=True)
class SpeedupRow:
    name: str
    low: int
    high: int
    baseline: str
    median_ms: float
    best_ms: float
    median_speedup: float
    best_speedup: float
    sample_stability: str

    @property
    def baseline_median_ms(self) -> float | None:
        if self.median_speedup <= 0:
            return None
        return self.median_ms * self.median_speedup

    @property
    def baseline_best_ms(self) -> float | None:
        if self.best_speedup <= 0:
            return None
        return self.best_ms * self.best_speedup


@dataclass(frozen=True)
class TimingRow:
    name: str
    workload: int
    segment_size: int
    result: int
    rounds: int
    best_ms: float


@dataclass(frozen=True)
class CountBinaryOverhead:
    low: int
    high: int
    cold_count_binary_median_ms: float
    hot_count_binary_server_median_ms: float
    primesieve_cli_median_ms: float
    libprimesieve_median_ms: float
    cold_vs_primesieve_speedup: float
    hot_vs_libprimesieve_speedup: float
    circle_cold_over_hot: float
    circle_cold_extra_ms: float
    primesieve_cli_over_libprimesieve: float
    primesieve_cli_extra_ms: float
    diagnosis: str


@dataclass(frozen=True)
class HotColdDecomposition:
    cold_count_binary_best_ms: float
    hot_count_server_best_ms: float
    cold_noop_best_ms: float
    cold_plan_best_ms: float
    cold_over_hot_best: float
    cold_extra_best_ms: float
    noop_share_of_cold_extra: float
    residual_after_noop_ms: float
    diagnosis: str
    next_action: str


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnose whether the high-offset count-binary cold gap is a "
            "cold-process/path issue or a hot algorithm issue."
        )
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument(
        "--hot-cold-csv",
        type=Path,
        default=None,
        help=(
            "Optional circle-prime-bench high-offset hot/cold artifact used to "
            "prove the local cold launch/thread/first-touch split."
        ),
    )
    parser.add_argument("--circle-prime", type=Path, default=DEFAULT_CIRCLE_PRIME)
    parser.add_argument(
        "--circle-prime-count",
        type=Path,
        default=DEFAULT_CIRCLE_PRIME_COUNT,
    )
    parser.add_argument("--defaults", type=Path, default=DEFAULT_DEFAULTS)
    parser.add_argument(
        "--min-hot-speedup",
        type=float,
        default=1.0,
        help="Minimum slim count-binary server speedup over libprimesieve required to pass.",
    )
    parser.add_argument(
        "--min-cold-speedup-floor",
        type=float,
        default=0.80,
        help="Minimum cold count-binary speedup floor required to pass.",
    )
    parser.add_argument(
        "--min-hot-cold-best-ratio",
        type=float,
        default=1.50,
        help=(
            "When --hot-cold-csv is provided, require cold count-binary best time "
            "to be at least this multiple of persistent count-server best time."
        ),
    )
    parser.add_argument(
        "--min-noop-share-of-cold-extra",
        type=float,
        default=0.20,
        help=(
            "When --hot-cold-csv is provided, require the no-op fresh-process "
            "floor to explain at least this share of the cold-over-hot best-time gap."
        ),
    )
    parser.add_argument(
        "--skip-provenance",
        action="store_true",
        help="Skip current-binary/defaults provenance checks. Intended for tests only.",
    )
    args = parser.parse_args()

    if args.min_hot_speedup < 0:
        parser.error("--min-hot-speedup must be nonnegative")
    if args.min_cold_speedup_floor < 0:
        parser.error("--min-cold-speedup-floor must be nonnegative")
    if args.min_hot_cold_best_ratio < 0:
        parser.error("--min-hot-cold-best-ratio must be nonnegative")
    if args.min_noop_share_of_cold_extra < 0:
        parser.error("--min-noop-share-of-cold-extra must be nonnegative")

    try:
        rows = load_speedup_rows(args.csv)
        hot_cold_rows = (
            load_timing_rows(args.hot_cold_csv) if args.hot_cold_csv is not None else None
        )
        provenance_failures = []
        if not args.skip_provenance:
            provenance_failures = current_provenance_failures(
                args.metadata,
                circle_prime=args.circle_prime,
                circle_prime_count=args.circle_prime_count,
                defaults_path=args.defaults,
            )
    except OSError as exc:
        print(f"ERROR: could not read count-binary overhead evidence: {exc}", file=sys.stderr)
        return 1
    except (csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: could not parse count-binary overhead evidence: {exc}", file=sys.stderr)
        return 1

    if provenance_failures:
        for failure in provenance_failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1

    result = check_count_binary_overhead(
        rows,
        hot_cold_rows=hot_cold_rows,
        min_hot_speedup=args.min_hot_speedup,
        min_cold_speedup_floor=args.min_cold_speedup_floor,
        min_hot_cold_best_ratio=args.min_hot_cold_best_ratio,
        min_noop_share_of_cold_extra=args.min_noop_share_of_cold_extra,
    )
    if result["ok"]:
        overhead: CountBinaryOverhead = result["overhead"]
        message = (
            "OK: high-offset count-binary overhead diagnosis: "
            f"{overhead.diagnosis}; cold={overhead.cold_vs_primesieve_speedup:.3f}x "
            f"vs primesieve CLI, hot={overhead.hot_vs_libprimesieve_speedup:.3f}x "
            f"vs libprimesieve, Circle cold/hot={overhead.circle_cold_over_hot:.2f}x "
            f"(+{overhead.circle_cold_extra_ms:.3f} ms)"
        )
        if result.get("hot_cold") is not None:
            hot_cold: HotColdDecomposition = result["hot_cold"]
            message += (
                "; hot/cold best-time split "
                f"cold={hot_cold.cold_count_binary_best_ms:.3f} ms, "
                f"hot={hot_cold.hot_count_server_best_ms:.3f} ms, "
                f"noop={hot_cold.cold_noop_best_ms:.3f} ms, "
                f"cold/hot={hot_cold.cold_over_hot_best:.2f}x, "
                f"noop-share={hot_cold.noop_share_of_cold_extra:.2f}x, "
                f"residual-after-noop={hot_cold.residual_after_noop_ms:.3f} ms, "
                f"next-action={hot_cold.next_action}"
            )
        print(message + ".")
        return 0

    print(result["message"], file=sys.stderr)
    overhead = result.get("overhead")
    if overhead is not None:
        print(
            "  "
            f"cold={overhead.cold_vs_primesieve_speedup:.3f}x, "
            f"hot={overhead.hot_vs_libprimesieve_speedup:.3f}x, "
            f"Circle cold/hot={overhead.circle_cold_over_hot:.2f}x",
            file=sys.stderr,
        )
    return 1


def current_provenance_failures(
    metadata_path: Path,
    *,
    circle_prime: Path,
    circle_prime_count: Path,
    defaults_path: Path,
) -> list[str]:
    if not metadata_path.exists():
        return [f"benchmark metadata is missing: {metadata_path}"]
    metadata = json.loads(metadata_path.read_text())
    if not isinstance(metadata, dict):
        return [f"expected metadata object in {metadata_path}"]
    return benchmark_provenance_failures(
        metadata,
        circle_prime=circle_prime,
        circle_prime_count=circle_prime_count,
        defaults_path=defaults_path,
    )


def load_speedup_rows(path: Path) -> list[SpeedupRow]:
    rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("kind") != "speedup":
                continue
            rows.append(
                SpeedupRow(
                    name=row.get("name", ""),
                    low=int(row["low"]),
                    high=int(row["high"]),
                    baseline=row.get("baseline", ""),
                    median_ms=float(row["median_ms"]),
                    best_ms=float(row["best_ms"]),
                    median_speedup=float(row["median_speedup"]),
                    best_speedup=float(row["best_speedup"]),
                    sample_stability=row.get("sample_stability", ""),
                )
            )
    return rows


def load_timing_rows(path: Path) -> list[TimingRow]:
    rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("kind") != "timing":
                continue
            rows.append(
                TimingRow(
                    name=row.get("name", ""),
                    workload=int(row.get("workload", "0")),
                    segment_size=int(row.get("segment_size", "0")),
                    result=int(row.get("result", "0")),
                    rounds=int(row.get("rounds", "0")),
                    best_ms=float(row["best_ms"]),
                )
            )
    return rows


def check_count_binary_overhead(
    rows: list[SpeedupRow],
    *,
    hot_cold_rows: list[TimingRow] | None = None,
    min_hot_speedup: float = 1.0,
    min_cold_speedup_floor: float = 0.80,
    min_hot_cold_best_ratio: float = 1.50,
    min_noop_share_of_cold_extra: float = 0.20,
) -> dict[str, Any]:
    try:
        overhead = summarize_count_binary_overhead(rows)
        hot_cold = (
            summarize_hot_cold_decomposition(hot_cold_rows)
            if hot_cold_rows is not None
            else None
        )
    except ValueError as exc:
        return {"ok": False, "message": f"ERROR: {exc}", "overhead": None, "hot_cold": None}

    failures = []
    if overhead.cold_vs_primesieve_speedup < min_cold_speedup_floor:
        failures.append(
            "cold count-binary speedup "
            f"{overhead.cold_vs_primesieve_speedup:.3f}x is below floor "
            f"{min_cold_speedup_floor:.3f}x"
        )
    if overhead.hot_vs_libprimesieve_speedup < min_hot_speedup:
        failures.append(
            "hot count-binary server speedup "
            f"{overhead.hot_vs_libprimesieve_speedup:.3f}x is below floor "
            f"{min_hot_speedup:.3f}x"
        )
    if hot_cold is not None:
        if hot_cold.cold_over_hot_best < min_hot_cold_best_ratio:
            failures.append(
                "hot/cold best-time ratio "
                f"{hot_cold.cold_over_hot_best:.3f}x is below floor "
                f"{min_hot_cold_best_ratio:.3f}x"
            )
        if hot_cold.noop_share_of_cold_extra < min_noop_share_of_cold_extra:
            failures.append(
                "fresh-process no-op share of cold-over-hot gap "
                f"{hot_cold.noop_share_of_cold_extra:.3f}x is below floor "
                f"{min_noop_share_of_cold_extra:.3f}x"
            )
    if failures:
        return {
            "ok": False,
            "message": "ERROR: " + "; ".join(failures) + ".",
            "overhead": overhead,
            "hot_cold": hot_cold,
        }
    return {"ok": True, "message": "OK", "overhead": overhead, "hot_cold": hot_cold}


def summarize_count_binary_overhead(rows: list[SpeedupRow]) -> CountBinaryOverhead:
    cold = find_row(
        rows,
        name_prefix="circle_prime_count_binary_",
        baseline="external_primesieve_count",
        reject_name_contains="_server_",
    )
    hot = find_row(
        rows,
        name_prefix="circle_prime_count_binary_server_",
        baseline="external_primesieve_count_server",
    )
    primesieve_cli_median = cold.baseline_median_ms
    libprimesieve_median = hot.baseline_median_ms
    if primesieve_cli_median is None or libprimesieve_median is None:
        raise ValueError("could not recover baseline medians from speedup rows")

    if hot.median_ms <= 0 or libprimesieve_median <= 0:
        raise ValueError("nonpositive median in count-binary overhead rows")

    if cold.median_speedup >= 1.0:
        diagnosis = "cold_one_shot_competitive"
    elif hot.median_speedup >= 1.0:
        diagnosis = "cold_process_or_startup_bound"
    else:
        diagnosis = "hot_algorithm_gap"

    return CountBinaryOverhead(
        low=cold.low,
        high=cold.high,
        cold_count_binary_median_ms=cold.median_ms,
        hot_count_binary_server_median_ms=hot.median_ms,
        primesieve_cli_median_ms=primesieve_cli_median,
        libprimesieve_median_ms=libprimesieve_median,
        cold_vs_primesieve_speedup=cold.median_speedup,
        hot_vs_libprimesieve_speedup=hot.median_speedup,
        circle_cold_over_hot=cold.median_ms / hot.median_ms,
        circle_cold_extra_ms=cold.median_ms - hot.median_ms,
        primesieve_cli_over_libprimesieve=primesieve_cli_median / libprimesieve_median,
        primesieve_cli_extra_ms=primesieve_cli_median - libprimesieve_median,
        diagnosis=diagnosis,
    )


def summarize_hot_cold_decomposition(rows: list[TimingRow]) -> HotColdDecomposition:
    cold_noop = find_timing_row(rows, "cold_count_binary_high_offset_noop")
    cold_plan = find_timing_row(rows, "cold_count_binary_high_offset_default_plan_8t")
    cold_count = find_timing_row(
        rows,
        "cold_count_binary_parallel_high_offset_default_range_count_8t",
    )
    hot_count = find_timing_row(
        rows,
        "hot_cli_count_server_parallel_high_offset_default_range_count_8t",
    )
    if cold_count.best_ms <= 0 or hot_count.best_ms <= 0:
        raise ValueError("nonpositive best time in high-offset hot/cold rows")
    cold_extra = cold_count.best_ms - hot_count.best_ms
    if cold_extra <= 0:
        raise ValueError(
            "high-offset hot/cold artifact does not show a cold-over-hot best-time gap"
        )
    residual_after_noop = max(0.0, cold_extra - cold_noop.best_ms)
    noop_share = cold_noop.best_ms / cold_extra
    return HotColdDecomposition(
        cold_count_binary_best_ms=cold_count.best_ms,
        hot_count_server_best_ms=hot_count.best_ms,
        cold_noop_best_ms=cold_noop.best_ms,
        cold_plan_best_ms=cold_plan.best_ms,
        cold_over_hot_best=cold_count.best_ms / hot_count.best_ms,
        cold_extra_best_ms=cold_extra,
        noop_share_of_cold_extra=noop_share,
        residual_after_noop_ms=residual_after_noop,
        diagnosis="cold_launch_thread_first_touch_bound",
        next_action=classify_hot_cold_next_action(noop_share, residual_after_noop),
    )


def classify_hot_cold_next_action(noop_share: float, residual_after_noop_ms: float) -> str:
    if noop_share >= 0.50:
        return "launch_amortization_required"
    if residual_after_noop_ms >= 0.50:
        return "thread_first_touch_reduction_required"
    return "cold_core_rebenchmark_required"


def find_timing_row(rows: list[TimingRow], name: str) -> TimingRow:
    matches = [row for row in rows if row.name == name]
    if not matches:
        raise ValueError(f"missing timing row {name!r} in high-offset hot/cold artifact")
    matches.sort(key=lambda row: row.best_ms)
    return matches[0]


def find_row(
    rows: list[SpeedupRow],
    *,
    name_prefix: str,
    baseline: str,
    reject_name_contains: str | None = None,
) -> SpeedupRow:
    matches = [
        row
        for row in rows
        if row.name.startswith(name_prefix)
        and row.baseline == baseline
        and (reject_name_contains is None or reject_name_contains not in row.name)
    ]
    if not matches:
        raise ValueError(
            f"missing speedup row with name prefix {name_prefix!r} and baseline {baseline!r}"
        )
    matches.sort(key=lambda row: row.median_speedup, reverse=True)
    return matches[0]


if __name__ == "__main__":
    raise SystemExit(main())
