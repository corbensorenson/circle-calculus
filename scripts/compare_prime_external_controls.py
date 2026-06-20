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
    / "prime_engine_external_controls_parallel_latest.csv"
)


@dataclass(frozen=True)
class ExternalSpeedupRow:
    name: str
    low: int
    high: int
    segment_size: int
    result: int
    threads: int
    requested_threads: int
    baseline: str
    best_speedup: float
    median_speedup: float
    count_mode: str = ""

    @property
    def key(self) -> tuple[str, int, int, int, int, int, str]:
        return (
            self.comparison_name,
            self.low,
            self.high,
            self.comparison_segment_size,
            self.comparison_threads,
            self.requested_threads,
            self.baseline,
        )

    @property
    def comparison_name(self) -> str:
        if not is_adaptive_default_row(self.name):
            return self.name
        if is_server_row(self.name):
            return "circle_prime_server_default_count"
        return "circle_prime_default_count"

    @property
    def comparison_segment_size(self) -> int:
        return 0 if is_adaptive_default_row(self.name) else self.segment_size

    @property
    def comparison_threads(self) -> int:
        return self.requested_threads if is_adaptive_default_row(self.name) else self.threads


@dataclass(frozen=True)
class ExternalComparison:
    key: tuple[str, int, int, int, int, int, str]
    baseline_result: int
    candidate_result: int
    baseline_best_speedup: float
    candidate_best_speedup: float
    baseline_median_speedup: float
    candidate_median_speedup: float
    baseline_segment_size: int = 0
    candidate_segment_size: int = 0
    baseline_count_mode: str = ""
    candidate_count_mode: str = ""

    @property
    def result_matches(self) -> bool:
        return self.baseline_result == self.candidate_result

    @property
    def best_speedup_ratio(self) -> float | None:
        return ratio_or_none(self.candidate_best_speedup, self.baseline_best_speedup)

    @property
    def median_speedup_ratio(self) -> float | None:
        return ratio_or_none(self.candidate_median_speedup, self.baseline_median_speedup)

    @property
    def count_mode_matches(self) -> bool:
        return self.baseline_count_mode == self.candidate_count_mode

    @property
    def segment_size_matches(self) -> bool:
        return self.baseline_segment_size == self.candidate_segment_size


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Circle external-control speedup rows against a baseline CSV "
            "and fail on result mismatches or serious-baseline speedup regressions."
        )
    )
    parser.add_argument(
        "candidate",
        type=Path,
        help="Candidate CSV produced by scripts/benchmark_prime_external_controls.py.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help=f"Baseline external-control CSV. Defaults to {DEFAULT_BASELINE}.",
    )
    parser.add_argument("--names", help="Optional comma-separated Circle row names.")
    parser.add_argument(
        "--baselines",
        help="Optional comma-separated external baseline row names.",
    )
    parser.add_argument(
        "--min-median-speedup-ratio",
        type=float,
        default=0.95,
        help=(
            "Fail when candidate median_speedup / baseline median_speedup is "
            "below this value. Lower values tolerate more timing noise."
        ),
    )
    parser.add_argument(
        "--min-best-speedup-ratio",
        type=float,
        default=0.90,
        help=(
            "Fail when candidate best_speedup / baseline best_speedup is below "
            "this value. Best timings are noisier than medians."
        ),
    )
    parser.add_argument(
        "--median-regression-best-speedup-ratio-floor",
        type=float,
        help=(
            "Do not fail a median-speedup regression when the same row's "
            "candidate best_speedup / baseline best_speedup is at or above "
            "this floor. This is useful for noisy command-level external rows."
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
        "--require-each-median-speedup-at-least",
        type=float,
        help=(
            "Fail when any compared row has candidate median_speedup below "
            "this threshold. Use with --names/--baselines for focused serious-control gates."
        ),
    )
    parser.add_argument(
        "--allow-candidate-subset",
        action="store_true",
        help=(
            "Allow the candidate CSV to omit selected baseline rows. By default "
            "every selected baseline speedup row must be present so partial "
            "external-control runs cannot silently pass regression gates."
        ),
    )
    parser.add_argument(
        "--fail-on-count-mode-change",
        action="store_true",
        help=(
            "Fail when the resolved Circle count_mode differs between baseline "
            "and candidate rows. By default mode changes are reported but allowed "
            "so adaptive default improvements can be compared as default behavior."
        ),
    )
    parser.add_argument(
        "--fail-on-segment-size-change",
        action="store_true",
        help=(
            "Fail when the resolved Circle segment_size differs between baseline "
            "and candidate rows. Adaptive default rows report segment changes but "
            "allow them by default."
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
        args.require_each_median_speedup_at_least is not None
        and args.require_each_median_speedup_at_least < 0.0
    ):
        parser.error("--require-each-median-speedup-at-least must be nonnegative")

    names = parse_csv_set(args.names, "--names")
    baselines = parse_csv_set(args.baselines, "--baselines")
    baseline_rows = read_speedup_rows(args.baseline)
    candidate_rows = read_speedup_rows(args.candidate)
    comparisons = compare_speedup_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
        names=names,
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
        require_any_median_speedup_at_least=args.require_any_median_speedup_at_least,
        require_each_median_speedup_at_least=args.require_each_median_speedup_at_least,
        fail_on_count_mode_change=args.fail_on_count_mode_change,
        fail_on_segment_size_change=args.fail_on_segment_size_change,
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


def read_speedup_rows(path: Path) -> dict[tuple[str, int, int, int, int, int, str], ExternalSpeedupRow]:
    with path.open(newline="") as handle:
        rows = csv.DictReader(handle)
        speedups = [
            ExternalSpeedupRow(
                name=row["name"],
                low=int(row["low"]),
                high=int(row["high"]),
                segment_size=int(row["segment_size"]),
                result=int(row["result"]),
                threads=int(row["threads"]),
                requested_threads=int(row["requested_threads"]),
                baseline=row["baseline"],
                best_speedup=float(row["best_speedup"]),
                median_speedup=float(row["median_speedup"]),
                count_mode=row.get("count_mode", ""),
            )
            for row in rows
            if row.get("kind") == "speedup"
        ]
    return {row.key: row for row in speedups}


def compare_speedup_rows(
    *,
    baseline_rows: dict[tuple[str, int, int, int, int, int, str], ExternalSpeedupRow],
    candidate_rows: dict[tuple[str, int, int, int, int, int, str], ExternalSpeedupRow],
    names: set[str] | None = None,
    baselines: set[str] | None = None,
    require_baseline_coverage: bool = True,
) -> list[ExternalComparison]:
    if require_baseline_coverage:
        missing = [
            key
            for key, baseline_row in sorted(baseline_rows.items())
            if row_selected(baseline_row, names, baselines) and key not in candidate_rows
        ]
        if missing:
            raise ValueError(
                "candidate CSV is missing selected baseline speedup row(s): "
                + "; ".join(format_speedup_key(key) for key in missing)
            )

    comparisons = []
    for key in sorted(candidate_rows):
        candidate = candidate_rows[key]
        if not row_selected(candidate, names, baselines):
            continue
        baseline = baseline_rows.get(key)
        if baseline is None:
            name, low, high, segment_size, threads, requested_threads, baseline_name = key
            raise ValueError(
                "candidate speedup row missing from baseline: "
                f"name={name}, range=[{low},{high}), segment_size={segment_size}, "
                f"threads={threads}, requested_threads={requested_threads}, "
                f"baseline={baseline_name}"
            )
        comparisons.append(
            ExternalComparison(
                key=key,
                baseline_result=baseline.result,
                candidate_result=candidate.result,
                baseline_best_speedup=baseline.best_speedup,
                candidate_best_speedup=candidate.best_speedup,
                baseline_median_speedup=baseline.median_speedup,
                candidate_median_speedup=candidate.median_speedup,
                baseline_segment_size=baseline.segment_size,
                candidate_segment_size=candidate.segment_size,
                baseline_count_mode=baseline.count_mode,
                candidate_count_mode=candidate.count_mode,
            )
        )
    if not comparisons:
        filters = []
        if names:
            filters.append(f"names={','.join(sorted(names))}")
        if baselines:
            filters.append(f"baselines={','.join(sorted(baselines))}")
        suffix = f" for requested filters ({'; '.join(filters)})" if filters else ""
        raise ValueError(f"candidate CSV had no external speedup rows{suffix}")
    return comparisons


def row_selected(
    row: ExternalSpeedupRow,
    names: set[str] | None,
    baselines: set[str] | None,
) -> bool:
    if names is not None and row.name not in names:
        return False
    if baselines is not None and row.baseline not in baselines:
        return False
    return True


def format_speedup_key(key: tuple[str, int, int, int, int, int, str]) -> str:
    name, low, high, segment_size, threads, requested_threads, baseline_name = key
    return (
        f"name={name}, range=[{low},{high}), segment_size={segment_size}, "
        f"threads={threads}, requested_threads={requested_threads}, "
        f"baseline={baseline_name}"
    )


def comparison_failures(
    comparisons: Iterable[ExternalComparison],
    *,
    min_median_speedup_ratio: float,
    min_best_speedup_ratio: float,
    median_regression_best_speedup_ratio_floor: float | None = None,
    require_any_median_speedup_at_least: float | None = None,
    require_each_median_speedup_at_least: float | None = None,
    fail_on_count_mode_change: bool = False,
    fail_on_segment_size_change: bool = False,
) -> list[str]:
    comparisons = list(comparisons)
    failures = []
    for row in comparisons:
        name, low, high, segment_size, threads, requested_threads, baseline = row.key
        label = (
            f"{name} range=[{low},{high}) segment={segment_size} threads={threads} "
            f"requested_threads={requested_threads} baseline={baseline}"
        )
        if not row.result_matches:
            failures.append(
                f"{label} result changed: baseline={row.baseline_result}, "
                f"candidate={row.candidate_result}"
            )
        if fail_on_count_mode_change and not row.count_mode_matches:
            failures.append(
                f"{label} count_mode changed: baseline={render_count_mode(row.baseline_count_mode)}, "
                f"candidate={render_count_mode(row.candidate_count_mode)}"
            )
        if fail_on_segment_size_change and not row.segment_size_matches:
            failures.append(
                f"{label} segment_size changed: baseline={row.baseline_segment_size}, "
                f"candidate={row.candidate_segment_size}"
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
            failures.append(
                f"{label} best speedup regressed: candidate/baseline="
                f"{best_ratio:.3f} < {min_best_speedup_ratio:.3f}"
            )
        if (
            require_each_median_speedup_at_least is not None
            and row.candidate_median_speedup < require_each_median_speedup_at_least
        ):
            failures.append(
                f"{label} median speedup below required floor: "
                f"{row.candidate_median_speedup:.3f} < "
                f"{require_each_median_speedup_at_least:.3f}"
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


def render_comparison_table(comparisons: Iterable[ExternalComparison]) -> str:
    lines = [
        "name,low,high,comparison_segment_size,baseline_segment_size,"
        "candidate_segment_size,segment_size_changed,threads,requested_threads,baseline,"
        "baseline_count_mode,candidate_count_mode,count_mode_changed,"
        "baseline_median_speedup,candidate_median_speedup,median_speedup_ratio,"
        "baseline_best_speedup,candidate_best_speedup,best_speedup_ratio,result"
    ]
    for row in comparisons:
        name, low, high, segment_size, threads, requested_threads, baseline = row.key
        result = "match" if row.result_matches else "mismatch"
        segment_size_changed = "no" if row.segment_size_matches else "yes"
        count_mode_changed = "no" if row.count_mode_matches else "yes"
        median_ratio = render_ratio(row.median_speedup_ratio)
        best_ratio = render_ratio(row.best_speedup_ratio)
        lines.append(
            f"{name},{low},{high},{segment_size},{row.baseline_segment_size},"
            f"{row.candidate_segment_size},{segment_size_changed},"
            f"{threads},{requested_threads},{baseline},"
            f"{render_count_mode(row.baseline_count_mode)},"
            f"{render_count_mode(row.candidate_count_mode)},{count_mode_changed},"
            f"{row.baseline_median_speedup:.3f},{row.candidate_median_speedup:.3f},"
            f"{median_ratio},{row.baseline_best_speedup:.3f},"
            f"{row.candidate_best_speedup:.3f},{best_ratio},{result}"
        )
    return "\n".join(lines)


def ratio_or_none(numerator: float, denominator: float) -> float | None:
    if denominator <= 0.0:
        return None
    return numerator / denominator


def render_ratio(ratio: float | None) -> str:
    return "n/a" if ratio is None else f"{ratio:.3f}"


def render_count_mode(count_mode: str) -> str:
    return count_mode or "unknown"


def is_adaptive_default_row(name: str) -> bool:
    return "_default_count" in name


def is_server_row(name: str) -> bool:
    return name.startswith("circle_prime_server_")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, argparse.ArgumentTypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
