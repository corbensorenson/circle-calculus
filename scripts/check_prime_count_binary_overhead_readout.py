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


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnose whether the high-offset count-binary cold gap is a "
            "cold-process/path issue or a hot algorithm issue."
        )
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
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
        "--skip-provenance",
        action="store_true",
        help="Skip current-binary/defaults provenance checks. Intended for tests only.",
    )
    args = parser.parse_args()

    if args.min_hot_speedup < 0:
        parser.error("--min-hot-speedup must be nonnegative")
    if args.min_cold_speedup_floor < 0:
        parser.error("--min-cold-speedup-floor must be nonnegative")

    try:
        rows = load_speedup_rows(args.csv)
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
        min_hot_speedup=args.min_hot_speedup,
        min_cold_speedup_floor=args.min_cold_speedup_floor,
    )
    if result["ok"]:
        overhead: CountBinaryOverhead = result["overhead"]
        print(
            "OK: high-offset count-binary overhead diagnosis: "
            f"{overhead.diagnosis}; cold={overhead.cold_vs_primesieve_speedup:.3f}x "
            f"vs primesieve CLI, hot={overhead.hot_vs_libprimesieve_speedup:.3f}x "
            f"vs libprimesieve, Circle cold/hot={overhead.circle_cold_over_hot:.2f}x "
            f"(+{overhead.circle_cold_extra_ms:.3f} ms)."
        )
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


def check_count_binary_overhead(
    rows: list[SpeedupRow],
    *,
    min_hot_speedup: float = 1.0,
    min_cold_speedup_floor: float = 0.80,
) -> dict[str, Any]:
    try:
        overhead = summarize_count_binary_overhead(rows)
    except ValueError as exc:
        return {"ok": False, "message": f"ERROR: {exc}", "overhead": None}

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
    if failures:
        return {
            "ok": False,
            "message": "ERROR: " + "; ".join(failures) + ".",
            "overhead": overhead,
        }
    return {"ok": True, "message": "OK", "overhead": overhead}


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
