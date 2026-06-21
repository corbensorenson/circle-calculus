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

from scripts.check_prime_benchmark_provenance import (
    metadata_tool_version_expectation_failures,
)
from scripts.prime_fuzzy_hybrid import is_prime_u64_mr


DEFAULT_CSV = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_fuzzy_hybrid_any_latest.csv"
)
DEFAULT_METADATA = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_fuzzy_hybrid_any_latest.json"
)
SCHEMA_ID = "circle_calculus.prime_fuzzy_hybrid_any_benchmark.v0"
REQUIRED_TIMING_NAMES = {
    "circle_fuzzy_hybrid_python_any_prime",
    "circle_fuzzy_hybrid_rust_server_any_prime",
    "deterministic_python_mr64_any_prime",
    "circle_prime_server_next_prime",
    "external_primesieve_generate_next_server",
    "external_primesieve_iterator_next_server",
    "external_primecount_next_server",
}
REQUIRED_RUST_SPEEDUP_BASELINES = {
    "circle_fuzzy_hybrid_python_any_prime",
    "deterministic_python_mr64_any_prime",
    "circle_prime_server_next_prime",
    "external_primesieve_generate_next_server",
    "external_primesieve_iterator_next_server",
    "external_primecount_next_server",
}


@dataclass(frozen=True)
class TimingRow:
    name: str
    start: int
    result: int
    median_ms: float
    best_ms: float


@dataclass(frozen=True)
class SpeedupRow:
    name: str
    start: int
    baseline: str
    median_speedup: float
    best_speedup: float


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the fuzzy hybrid any-prime benchmark artifact."
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--expect-starts")
    parser.add_argument("--expect-rounds", type=int)
    parser.add_argument("--expect-batch-size", type=int)
    parser.add_argument("--expect-warmup-rounds", type=int)
    parser.add_argument("--expect-search-window", type=int)
    parser.add_argument("--expect-top-k", type=int)
    parser.add_argument("--expect-score-limit", type=int)
    parser.add_argument(
        "--min-rust-median-speedup",
        action="append",
        default=[],
        metavar="BASELINE=VALUE",
        help=(
            "Require the Rust hybrid speedup row against BASELINE to have "
            "median_speedup at least VALUE for every checked start."
        ),
    )
    parser.add_argument(
        "--require-tool-version-at-least",
        action="append",
        default=[],
        metavar="TOOL=VERSION",
    )
    args = parser.parse_args()

    failures = validate_artifact(
        csv_path=args.csv,
        metadata_path=args.metadata,
        expect_starts=parse_optional_ints(args.expect_starts),
        expect_rounds=args.expect_rounds,
        expect_batch_size=args.expect_batch_size,
        expect_warmup_rounds=args.expect_warmup_rounds,
        expect_search_window=args.expect_search_window,
        expect_top_k=args.expect_top_k,
        expect_score_limit=args.expect_score_limit,
        min_rust_median_speedups=parse_speedup_requirements(
            args.min_rust_median_speedup
        ),
        tool_version_requirements=args.require_tool_version_at_least,
    )
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(
        "prime fuzzy hybrid any artifact ok: "
        f"csv={args.csv}, metadata={args.metadata}"
    )
    return 0


def validate_artifact(
    *,
    csv_path: Path,
    metadata_path: Path,
    expect_starts: set[int] | None = None,
    expect_rounds: int | None = None,
    expect_batch_size: int | None = None,
    expect_warmup_rounds: int | None = None,
    expect_search_window: int | None = None,
    expect_top_k: int | None = None,
    expect_score_limit: int | None = None,
    min_rust_median_speedups: dict[str, float] | None = None,
    tool_version_requirements: list[str] | None = None,
) -> list[str]:
    failures: list[str] = []
    if not csv_path.exists():
        failures.append(f"CSV artifact is missing: {csv_path}")
        return failures
    if not metadata_path.exists():
        failures.append(f"metadata artifact is missing: {metadata_path}")
        return failures

    metadata = json.loads(metadata_path.read_text())
    timing_rows, speedup_rows = read_rows(csv_path)
    starts = {row.start for row in timing_rows}
    if expect_starts is not None and starts != expect_starts:
        failures.append(
            f"starts mismatch: expected {sorted(expect_starts)}, got {sorted(starts)}"
        )
    failures.extend(validate_metadata(metadata, starts))
    failures.extend(
        validate_metadata_expectations(
            metadata,
            expect_rounds=expect_rounds,
            expect_batch_size=expect_batch_size,
            expect_warmup_rounds=expect_warmup_rounds,
            expect_search_window=expect_search_window,
            expect_top_k=expect_top_k,
            expect_score_limit=expect_score_limit,
        )
    )
    failures.extend(
        validate_timing_rows(
            timing_rows,
            starts,
            search_window=int(metadata.get("search_window") or 0),
        )
    )
    failures.extend(validate_speedup_rows(speedup_rows, starts))
    failures.extend(
        validate_speedup_requirements(
            speedup_rows,
            starts,
            min_rust_median_speedups or {},
        )
    )
    failures.extend(
        metadata_tool_version_expectation_failures(
            metadata,
            tool_version_requirements or [],
        )
    )
    return failures


def validate_metadata(metadata: dict[str, Any], starts: set[int]) -> list[str]:
    failures = []
    if metadata.get("schema_id") != SCHEMA_ID:
        failures.append(
            f"metadata schema_id mismatch: expected {SCHEMA_ID}, got {metadata.get('schema_id')!r}"
        )
    metadata_starts = set(metadata.get("starts") or [])
    if metadata_starts != starts:
        failures.append(
            f"metadata starts {sorted(metadata_starts)} do not match CSV starts {sorted(starts)}"
        )
    if metadata.get("search_mode") != "any-prime":
        failures.append("metadata search_mode must be any-prime")
    if not isinstance(metadata.get("search_window"), int) or metadata["search_window"] <= 0:
        failures.append("metadata search_window must be positive")
    if not isinstance(metadata.get("score_limit"), int) or metadata["score_limit"] <= 0:
        failures.append("metadata score_limit must be positive")
    contract = metadata.get("hybrid_proof_contract") or {}
    if contract.get("name") != "prime_fuzzy_hybrid_verified_prime_search_v0":
        failures.append("hybrid proof contract is missing or has wrong name")
    if contract.get("neural_role") != "candidate_ordering_only":
        failures.append("hybrid proof contract must mark neural_role=candidate_ordering_only")
    if "deterministic" not in contract.get("deterministic_prefilter", ""):
        failures.append("hybrid proof contract must describe the deterministic prefilter")
    if "deterministic verification" not in contract.get("acceptance_rule", ""):
        failures.append("hybrid proof contract acceptance_rule must require deterministic verification")
    not_claimed = metadata.get("not_claimed") or []
    if not any("next prime" in item for item in not_claimed):
        failures.append("metadata must state any-prime rows do not claim next-prime")
    model_fingerprint = metadata.get("rust_model_fingerprint") or {}
    if not model_fingerprint.get("available"):
        failures.append("metadata lacks an available Rust model fingerprint")
    tools = metadata.get("tools") or {}
    for tool in [
        "circle_prime",
        "primesieve",
        "primecount",
        "primesieve_library_server",
        "primesieve_iterator_server",
        "primecount_library_server",
    ]:
        tool_metadata = tools.get(tool) or {}
        if not tool_metadata.get("available"):
            failures.append(f"required tool metadata is unavailable: {tool}")
    return failures


def validate_metadata_expectations(
    metadata: dict[str, Any],
    *,
    expect_rounds: int | None,
    expect_batch_size: int | None,
    expect_warmup_rounds: int | None,
    expect_search_window: int | None,
    expect_top_k: int | None,
    expect_score_limit: int | None,
) -> list[str]:
    failures = []
    for key, expected in [
        ("rounds", expect_rounds),
        ("batch_size", expect_batch_size),
        ("warmup_rounds", expect_warmup_rounds),
        ("search_window", expect_search_window),
        ("top_k", expect_top_k),
        ("score_limit", expect_score_limit),
    ]:
        if expected is not None and metadata.get(key) != expected:
            failures.append(
                f"metadata {key} mismatch: expected {expected}, got {metadata.get(key)!r}"
            )
    return failures


def validate_timing_rows(
    timing_rows: list[TimingRow],
    starts: set[int],
    *,
    search_window: int,
) -> list[str]:
    failures = []
    if search_window <= 0:
        return failures
    timing_by_start: dict[int, list[TimingRow]] = {
        start: [row for row in timing_rows if row.start == start] for start in starts
    }
    for start, rows in timing_by_start.items():
        names = {row.name for row in rows}
        missing = REQUIRED_TIMING_NAMES - names
        if missing:
            failures.append(f"start {start} missing timing rows: {sorted(missing)}")
        for row in rows:
            if row.median_ms <= 0.0 or row.best_ms <= 0.0:
                failures.append(f"start {start} row {row.name} has nonpositive timing")
            if row.result < start or row.result >= start + search_window:
                failures.append(
                    f"start {start} row {row.name} result {row.result} "
                    f"is outside [{start}, {start + search_window})"
                )
            if not is_prime_u64_mr(row.result):
                failures.append(
                    f"start {start} row {row.name} result {row.result} is not prime"
                )
    return failures


def validate_speedup_rows(speedup_rows: list[SpeedupRow], starts: set[int]) -> list[str]:
    failures = []
    for start in starts:
        rows = [
            row
            for row in speedup_rows
            if row.start == start
            and row.name == "circle_fuzzy_hybrid_rust_server_any_prime"
        ]
        baselines = {row.baseline for row in rows}
        missing = REQUIRED_RUST_SPEEDUP_BASELINES - baselines
        if missing:
            failures.append(f"start {start} missing Rust speedup baselines: {sorted(missing)}")
    return failures


def validate_speedup_requirements(
    speedup_rows: list[SpeedupRow],
    starts: set[int],
    requirements: dict[str, float],
) -> list[str]:
    failures = []
    for baseline, minimum in requirements.items():
        for start in starts:
            row = next(
                (
                    row
                    for row in speedup_rows
                    if row.start == start
                    and row.name == "circle_fuzzy_hybrid_rust_server_any_prime"
                    and row.baseline == baseline
                ),
                None,
            )
            if row is None:
                failures.append(f"start {start} missing Rust speedup row vs {baseline}")
                continue
            if row.median_speedup < minimum:
                failures.append(
                    f"start {start} Rust median speedup vs {baseline} is "
                    f"{row.median_speedup:.3f}, below required {minimum:.3f}"
                )
    return failures


def read_rows(path: Path) -> tuple[list[TimingRow], list[SpeedupRow]]:
    timing_rows = []
    speedup_rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row["kind"] == "timing":
                timing_rows.append(
                    TimingRow(
                        name=row["name"],
                        start=int(row["start"]),
                        result=int(row["result"]),
                        median_ms=float(row["median_ms"]),
                        best_ms=float(row["best_ms"]),
                    )
                )
            elif row["kind"] == "speedup":
                speedup_rows.append(
                    SpeedupRow(
                        name=row["name"],
                        start=int(row["start"]),
                        baseline=row["baseline"],
                        median_speedup=float(row["median_speedup"]),
                        best_speedup=float(row["best_speedup"]),
                    )
                )
    return timing_rows, speedup_rows


def parse_optional_ints(raw: str | None) -> set[int] | None:
    if raw is None:
        return None
    return {int(item.strip()) for item in raw.split(",") if item.strip()}


def parse_speedup_requirements(raw_requirements: list[str]) -> dict[str, float]:
    requirements = {}
    for raw in raw_requirements:
        if "=" not in raw:
            raise SystemExit(f"speedup requirement must be BASELINE=VALUE, got {raw!r}")
        baseline, raw_value = raw.split("=", 1)
        requirements[baseline.strip()] = float(raw_value)
    return requirements


if __name__ == "__main__":
    raise SystemExit(main())
