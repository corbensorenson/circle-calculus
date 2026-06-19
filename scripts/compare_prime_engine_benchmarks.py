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
    / "prime_engine_benchmark_latest.csv"
)


@dataclass(frozen=True)
class TimingRow:
    name: str
    workload: int
    segment_size: int
    result: int
    best_ms: float

    @property
    def key(self) -> tuple[str, int, int]:
        return (self.name, self.workload, self.segment_size)


@dataclass(frozen=True)
class Comparison:
    key: tuple[str, int, int]
    baseline_result: int
    candidate_result: int
    baseline_best_ms: float
    candidate_best_ms: float

    @property
    def ratio(self) -> float | None:
        if self.baseline_best_ms <= 0.0:
            return None
        return self.candidate_best_ms / self.baseline_best_ms

    @property
    def result_matches(self) -> bool:
        return self.baseline_result == self.candidate_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a candidate Circle prime-engine benchmark CSV against a "
            "baseline CSV and fail on result mismatches or timing regressions."
        )
    )
    parser.add_argument(
        "candidate",
        type=Path,
        help="Candidate benchmark CSV, often produced by circle-prime-bench --only.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help=f"Baseline benchmark CSV. Defaults to {DEFAULT_BASELINE}.",
    )
    parser.add_argument(
        "--names",
        help="Optional comma-separated row names to compare.",
    )
    parser.add_argument(
        "--max-regression-ratio",
        type=float,
        default=1.05,
        help="Fail when candidate best_ms / baseline best_ms exceeds this value.",
    )
    parser.add_argument(
        "--require-improvement-ratio",
        type=float,
        help=(
            "Fail unless at least one compared row is at or below this ratio. "
            "Use 1.0 to require any measured improvement."
        ),
    )
    parser.add_argument(
        "--allow-candidate-subset",
        action="store_true",
        help=(
            "Allow the candidate CSV to omit selected baseline rows. By default "
            "every selected baseline row must be present so partial benchmark "
            "runs cannot silently pass regression gates."
        ),
    )
    args = parser.parse_args()

    if args.max_regression_ratio < 1.0:
        parser.error("--max-regression-ratio must be at least 1.0")
    if args.require_improvement_ratio is not None and args.require_improvement_ratio > 1.0:
        parser.error("--require-improvement-ratio must be at most 1.0")

    names = parse_names(args.names)
    baseline_rows = read_timing_rows(args.baseline)
    candidate_rows = read_timing_rows(args.candidate)
    comparisons = compare_timing_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
        names=names,
        require_baseline_coverage=not args.allow_candidate_subset,
    )
    failures = comparison_failures(
        comparisons,
        max_regression_ratio=args.max_regression_ratio,
        require_improvement_ratio=args.require_improvement_ratio,
    )

    print(render_comparison_table(comparisons))
    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1
    return 0


def parse_names(raw: str | None) -> set[str] | None:
    if raw is None:
        return None
    names = {item.strip() for item in raw.split(",") if item.strip()}
    if not names:
        raise argparse.ArgumentTypeError("--names must include at least one row name")
    return names


def read_timing_rows(path: Path) -> dict[tuple[str, int, int], TimingRow]:
    with path.open(newline="") as handle:
        rows = csv.DictReader(handle)
        timings = [
            TimingRow(
                name=row["name"],
                workload=int(row["workload"]),
                segment_size=int(row["segment_size"]),
                result=int(row["result"]),
                best_ms=float(row["best_ms"]),
            )
            for row in rows
            if row.get("kind") == "timing"
        ]
    return {row.key: row for row in timings}


def compare_timing_rows(
    *,
    baseline_rows: dict[tuple[str, int, int], TimingRow],
    candidate_rows: dict[tuple[str, int, int], TimingRow],
    names: set[str] | None = None,
    require_baseline_coverage: bool = True,
) -> list[Comparison]:
    if require_baseline_coverage:
        missing = [
            key
            for key, baseline in sorted(baseline_rows.items())
            if (names is None or baseline.name in names) and key not in candidate_rows
        ]
        if missing:
            raise ValueError(
                "candidate CSV is missing selected baseline row(s): "
                + "; ".join(format_timing_key(key) for key in missing)
            )

    comparisons = []
    for key in sorted(candidate_rows):
        candidate = candidate_rows[key]
        if names is not None and candidate.name not in names:
            continue
        baseline = baseline_rows.get(key)
        if baseline is None:
            raise ValueError(
                "candidate row missing from baseline: "
                f"name={candidate.name}, workload={candidate.workload}, "
                f"segment_size={candidate.segment_size}"
            )
        comparisons.append(
            Comparison(
                key=key,
                baseline_result=baseline.result,
                candidate_result=candidate.result,
                baseline_best_ms=baseline.best_ms,
                candidate_best_ms=candidate.best_ms,
            )
        )
    if not comparisons:
        if names:
            wanted = ", ".join(sorted(names))
            raise ValueError(f"candidate CSV had no timing rows for requested names: {wanted}")
        raise ValueError("candidate CSV had no timing rows that can be compared")
    return comparisons


def format_timing_key(key: tuple[str, int, int]) -> str:
    name, workload, segment_size = key
    return f"name={name}, workload={workload}, segment_size={segment_size}"


def comparison_failures(
    comparisons: Iterable[Comparison],
    *,
    max_regression_ratio: float,
    require_improvement_ratio: float | None = None,
) -> list[str]:
    comparisons = list(comparisons)
    failures = []
    for row in comparisons:
        name, workload, segment_size = row.key
        label = f"{name} workload={workload} segment={segment_size}"
        if not row.result_matches:
            failures.append(
                f"{label} result changed: baseline={row.baseline_result}, "
                f"candidate={row.candidate_result}"
            )
        ratio = row.ratio
        if ratio is None:
            failures.append(
                f"{label} cannot compare timing ratio because baseline best_ms="
                f"{row.baseline_best_ms:.3f}; rerun with a larger workload or "
                "higher timing precision"
            )
            continue
        if ratio > max_regression_ratio:
            failures.append(
                f"{label} regressed: candidate/baseline={ratio:.3f} "
                f"> {max_regression_ratio:.3f}"
            )
    comparable_ratios = [row.ratio for row in comparisons if row.ratio is not None]
    if require_improvement_ratio is not None and not any(
        ratio <= require_improvement_ratio for ratio in comparable_ratios
    ):
        failures.append(
            "no compared row met required improvement ratio "
            f"{require_improvement_ratio:.3f}"
        )
    return failures


def render_comparison_table(comparisons: Iterable[Comparison]) -> str:
    lines = [
        "name,workload,segment_size,baseline_best_ms,candidate_best_ms,ratio,result"
    ]
    for row in comparisons:
        name, workload, segment_size = row.key
        result = "match" if row.result_matches else "mismatch"
        ratio = row.ratio
        rendered_ratio = "n/a" if ratio is None else f"{ratio:.3f}"
        lines.append(
            f"{name},{workload},{segment_size},"
            f"{row.baseline_best_ms:.3f},{row.candidate_best_ms:.3f},"
            f"{rendered_ratio},{result}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, argparse.ArgumentTypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
