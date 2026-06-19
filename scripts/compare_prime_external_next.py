from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_BASELINE = (
    Path(__file__).resolve().parents[1]
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_external_next_latest.csv"
)


@dataclass(frozen=True)
class NextSpeedupRow:
    name: str
    start: int
    batch_size: int
    result: int
    candidate_count: int
    threads: int
    requested_threads: int
    baseline: str
    best_speedup: float
    median_speedup: float

    @property
    def key(self) -> tuple[str, int, int, int, int, str]:
        return (
            self.name,
            self.start,
            self.batch_size,
            self.threads,
            self.requested_threads,
            self.baseline,
        )


@dataclass(frozen=True)
class NextComparison:
    key: tuple[str, int, int, int, int, str]
    baseline_result: int
    candidate_result: int
    baseline_candidate_count: int
    candidate_candidate_count: int
    baseline_best_speedup: float
    candidate_best_speedup: float
    baseline_median_speedup: float
    candidate_median_speedup: float

    @property
    def result_matches(self) -> bool:
        return self.baseline_result == self.candidate_result

    @property
    def best_speedup_ratio(self) -> float | None:
        return ratio_or_none(self.candidate_best_speedup, self.baseline_best_speedup)

    @property
    def median_speedup_ratio(self) -> float | None:
        return ratio_or_none(self.candidate_median_speedup, self.baseline_median_speedup)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Circle external next-prime speedup rows against a baseline "
            "CSV and fail on result mismatches or primesieve speedup regressions."
        )
    )
    parser.add_argument(
        "candidate",
        type=Path,
        help="Candidate CSV produced by scripts/benchmark_prime_external_next.py.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help=f"Baseline external next-prime CSV. Defaults to {DEFAULT_BASELINE}.",
    )
    parser.add_argument("--names", help="Optional comma-separated Circle row names.")
    parser.add_argument("--starts", help="Optional comma-separated start values.")
    parser.add_argument("--baselines", help="Optional comma-separated external baseline row names.")
    parser.add_argument(
        "--min-median-speedup-ratio",
        type=float,
        default=0.85,
        help=(
            "Fail when candidate median_speedup / baseline median_speedup is "
            "below this value. Next-prime command-level rows can be noisy."
        ),
    )
    parser.add_argument(
        "--min-best-speedup-ratio",
        type=float,
        default=0.85,
        help="Fail when candidate best_speedup / baseline best_speedup is below this value.",
    )
    parser.add_argument(
        "--median-regression-best-speedup-ratio-floor",
        type=float,
        help=(
            "Do not fail a median-speedup regression when the same row's "
            "candidate best_speedup / baseline best_speedup is at or above this floor."
        ),
    )
    parser.add_argument(
        "--best-regression-median-speedup-ratio-floor",
        type=float,
        help=(
            "Do not fail a best-speedup regression when the same row's "
            "candidate median_speedup / baseline median_speedup is at or above this floor."
        ),
    )
    parser.add_argument(
        "--require-any-median-speedup-at-least",
        type=float,
        help=(
            "Fail unless at least one compared row has candidate median_speedup "
            "at or above this threshold. Use 1.0 to require a serious-control win."
        ),
    )
    parser.add_argument(
        "--allow-candidate-subset",
        action="store_true",
        help=(
            "Allow the candidate CSV to omit selected baseline rows. By default "
            "every selected baseline speedup row must be present."
        ),
    )
    args = parser.parse_args()

    if args.min_median_speedup_ratio < 0.0:
        parser.error("--min-median-speedup-ratio must be nonnegative")
    if args.min_best_speedup_ratio < 0.0:
        parser.error("--min-best-speedup-ratio must be nonnegative")
    if (
        args.median_regression_best_speedup_ratio_floor is not None
        and args.median_regression_best_speedup_ratio_floor < 0.0
    ):
        parser.error("--median-regression-best-speedup-ratio-floor must be nonnegative")
    if (
        args.best_regression_median_speedup_ratio_floor is not None
        and args.best_regression_median_speedup_ratio_floor < 0.0
    ):
        parser.error("--best-regression-median-speedup-ratio-floor must be nonnegative")

    names = parse_csv_set(args.names, "--names")
    starts = parse_int_set(args.starts, "--starts")
    baselines = parse_csv_set(args.baselines, "--baselines")
    baseline_rows = read_speedup_rows(args.baseline)
    candidate_rows = read_speedup_rows(args.candidate)
    comparisons = compare_speedup_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
        names=names,
        starts=starts,
        baselines=baselines,
        require_baseline_coverage=not args.allow_candidate_subset,
    )
    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=args.min_median_speedup_ratio,
        min_best_speedup_ratio=args.min_best_speedup_ratio,
        median_regression_best_speedup_ratio_floor=(
            args.median_regression_best_speedup_ratio_floor
        ),
        best_regression_median_speedup_ratio_floor=(
            args.best_regression_median_speedup_ratio_floor
        ),
        require_any_median_speedup_at_least=args.require_any_median_speedup_at_least,
    )

    print(render_comparison_table(comparisons))
    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1
    return 0


def parse_csv_set(raw: str | None, label: str) -> set[str] | None:
    if raw is None:
        return None
    values = {item.strip() for item in raw.split(",") if item.strip()}
    if not values:
        raise argparse.ArgumentTypeError(f"{label} must include at least one value")
    return values


def parse_int_set(raw: str | None, label: str) -> set[int] | None:
    if raw is None:
        return None
    values = set()
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        try:
            values.add(int(item))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"{label} must contain only integer values"
            ) from exc
    if not values:
        raise argparse.ArgumentTypeError(f"{label} must include at least one value")
    return values


def read_speedup_rows(path: Path) -> dict[tuple[str, int, int, int, int, str], NextSpeedupRow]:
    with path.open(newline="") as handle:
        rows = csv.DictReader(handle)
        speedups = [
            NextSpeedupRow(
                name=row["name"],
                start=int(row["start"]),
                batch_size=int(row["batch_size"]),
                result=int(row["result"]),
                candidate_count=int(row["candidate_count"]),
                threads=int(row["threads"]),
                requested_threads=int(row["requested_threads"]),
                baseline=row["baseline"],
                best_speedup=float(row["best_speedup"]),
                median_speedup=float(row["median_speedup"]),
            )
            for row in rows
            if row.get("kind") == "speedup"
        ]
    return {row.key: row for row in speedups}


def compare_speedup_rows(
    *,
    baseline_rows: dict[tuple[str, int, int, int, int, str], NextSpeedupRow],
    candidate_rows: dict[tuple[str, int, int, int, int, str], NextSpeedupRow],
    names: set[str] | None = None,
    starts: set[int] | None = None,
    baselines: set[str] | None = None,
    require_baseline_coverage: bool = True,
) -> list[NextComparison]:
    if require_baseline_coverage:
        missing = [
            key
            for key, baseline_row in sorted(baseline_rows.items())
            if row_selected(baseline_row, names, starts, baselines) and key not in candidate_rows
        ]
        if missing:
            raise ValueError(
                "candidate CSV is missing selected baseline next-prime speedup row(s): "
                + "; ".join(format_speedup_key(key) for key in missing)
            )

    comparisons = []
    for key in sorted(candidate_rows):
        candidate = candidate_rows[key]
        if not row_selected(candidate, names, starts, baselines):
            continue
        baseline = baseline_rows.get(key)
        if baseline is None:
            name, start, batch_size, threads, requested_threads, baseline_name = key
            raise ValueError(
                "candidate next-prime speedup row missing from baseline: "
                f"name={name}, start={start}, batch_size={batch_size}, "
                f"threads={threads}, requested_threads={requested_threads}, "
                f"baseline={baseline_name}"
            )
        comparisons.append(
            NextComparison(
                key=key,
                baseline_result=baseline.result,
                candidate_result=candidate.result,
                baseline_candidate_count=baseline.candidate_count,
                candidate_candidate_count=candidate.candidate_count,
                baseline_best_speedup=baseline.best_speedup,
                candidate_best_speedup=candidate.best_speedup,
                baseline_median_speedup=baseline.median_speedup,
                candidate_median_speedup=candidate.median_speedup,
            )
        )
    if not comparisons:
        filters = []
        if names:
            filters.append(f"names={','.join(sorted(names))}")
        if starts:
            filters.append(f"starts={','.join(str(start) for start in sorted(starts))}")
        if baselines:
            filters.append(f"baselines={','.join(sorted(baselines))}")
        suffix = f" for requested filters ({'; '.join(filters)})" if filters else ""
        raise ValueError(f"candidate CSV had no external next-prime speedup rows{suffix}")
    return comparisons


def row_selected(
    row: NextSpeedupRow,
    names: set[str] | None,
    starts: set[int] | None,
    baselines: set[str] | None,
) -> bool:
    if names is not None and row.name not in names:
        return False
    if starts is not None and row.start not in starts:
        return False
    if baselines is not None and row.baseline not in baselines:
        return False
    return True


def format_speedup_key(key: tuple[str, int, int, int, int, str]) -> str:
    name, start, batch_size, threads, requested_threads, baseline_name = key
    return (
        f"name={name}, start={start}, batch_size={batch_size}, "
        f"threads={threads}, requested_threads={requested_threads}, "
        f"baseline={baseline_name}"
    )


def comparison_failures(
    comparisons: Iterable[NextComparison],
    *,
    min_median_speedup_ratio: float,
    min_best_speedup_ratio: float,
    median_regression_best_speedup_ratio_floor: float | None = None,
    best_regression_median_speedup_ratio_floor: float | None = None,
    require_any_median_speedup_at_least: float | None = None,
) -> list[str]:
    comparisons = list(comparisons)
    failures = []
    for row in comparisons:
        name, start, batch_size, threads, requested_threads, baseline = row.key
        label = (
            f"{name} start={start} batch_size={batch_size} threads={threads} "
            f"requested_threads={requested_threads} baseline={baseline}"
        )
        if not row.result_matches:
            failures.append(
                f"{label} result changed: baseline={row.baseline_result}, "
                f"candidate={row.candidate_result}"
            )
        median_ratio = row.median_speedup_ratio
        best_ratio = row.best_speedup_ratio
        if median_ratio is None:
            failures.append(
                f"{label} cannot compare median speedup ratio because baseline "
                f"median_speedup={row.baseline_median_speedup:.3f}"
            )
        elif median_ratio < min_median_speedup_ratio:
            best_floor_allows_median_drift = (
                median_regression_best_speedup_ratio_floor is not None
                and best_ratio is not None
                and best_ratio >= median_regression_best_speedup_ratio_floor
            )
            if not best_floor_allows_median_drift:
                failures.append(
                    f"{label} median speedup regressed: candidate/baseline="
                    f"{median_ratio:.3f} < {min_median_speedup_ratio:.3f}"
                )
        if best_ratio is None:
            failures.append(
                f"{label} cannot compare best speedup ratio because baseline "
                f"best_speedup={row.baseline_best_speedup:.3f}"
            )
        elif best_ratio < min_best_speedup_ratio:
            median_floor_allows_best_drift = (
                best_regression_median_speedup_ratio_floor is not None
                and median_ratio is not None
                and median_ratio >= best_regression_median_speedup_ratio_floor
            )
            if not median_floor_allows_best_drift:
                failures.append(
                    f"{label} best speedup regressed: candidate/baseline="
                    f"{best_ratio:.3f} < {min_best_speedup_ratio:.3f}"
                )

    if require_any_median_speedup_at_least is not None and not any(
        row.candidate_median_speedup >= require_any_median_speedup_at_least
        for row in comparisons
    ):
        failures.append(
            "no compared row met required candidate median speedup "
            f"{require_any_median_speedup_at_least:.3f}"
        )
    return failures


def render_comparison_table(comparisons: Iterable[NextComparison]) -> str:
    lines = [
        "name,start,batch_size,threads,requested_threads,baseline,"
        "baseline_candidate_count,candidate_candidate_count,"
        "baseline_median_speedup,candidate_median_speedup,median_speedup_ratio,"
        "baseline_best_speedup,candidate_best_speedup,best_speedup_ratio,result"
    ]
    for row in comparisons:
        name, start, batch_size, threads, requested_threads, baseline = row.key
        result = "match" if row.result_matches else "mismatch"
        lines.append(
            f"{name},{start},{batch_size},{threads},{requested_threads},{baseline},"
            f"{row.baseline_candidate_count},{row.candidate_candidate_count},"
            f"{row.baseline_median_speedup:.3f},{row.candidate_median_speedup:.3f},"
            f"{render_ratio(row.median_speedup_ratio)},"
            f"{row.baseline_best_speedup:.3f},{row.candidate_best_speedup:.3f},"
            f"{render_ratio(row.best_speedup_ratio)},{result}"
        )
    return "\n".join(lines)


def ratio_or_none(numerator: float, denominator: float) -> float | None:
    if denominator <= 0.0:
        return None
    return numerator / denominator


def render_ratio(ratio: float | None) -> str:
    return "n/a" if ratio is None else f"{ratio:.3f}"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, argparse.ArgumentTypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
