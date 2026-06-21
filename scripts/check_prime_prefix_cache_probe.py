from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_external_controls_2b_prefix_probe_latest.csv"
)
DEFAULT_METADATA = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_external_controls_2b_prefix_probe_latest.json"
)
DEFAULT_REQUIRED_BASELINES = (
    "external_primecount_pi_diff_server",
    "external_primesieve_count_server",
)
DEFAULT_REQUIRED_COLD_BASELINES = (
    "external_primecount_pi_diff",
    "external_primesieve_count",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail unless a warmed Circle prefix-pi count-server cache probe "
            "clears the promotion gate against persistent external controls."
        )
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--range", dest="range_text", default="1000000000:2000000000")
    parser.add_argument("--expected-limit", type=int, default=2_000_000_000)
    parser.add_argument("--max-estimated-bytes", type=int, default=200_000_000)
    parser.add_argument("--max-startup-warmup-ms", type=float, default=12_000.0)
    parser.add_argument("--min-median-speedup", type=float, default=50.0)
    parser.add_argument("--min-cold-median-speedup", type=float, default=1.0)
    parser.add_argument(
        "--required-baseline",
        action="append",
        default=[],
        help=(
            "External baseline that must be beaten by the warmed Circle server. "
            "May be repeated; defaults to libprimecount and libprimesieve servers."
        ),
    )
    parser.add_argument(
        "--allow-noisy",
        action="store_true",
        help="Do not require stable Circle speedup samples.",
    )
    parser.add_argument(
        "--required-cold-baseline",
        action="append",
        default=[],
        help=(
            "Cold external CLI baseline the Circle default row must beat. "
            "May be repeated; defaults to primecount and primesieve CLI controls."
        ),
    )
    parser.add_argument(
        "--allow-noisy-cold",
        action="store_true",
        help="Do not require stable cold Circle speedup samples.",
    )
    args = parser.parse_args()

    try:
        low, high = parse_range(args.range_text)
        metadata = load_metadata(args.metadata)
        rows = load_rows(args.csv)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    required_baselines = tuple(args.required_baseline) or DEFAULT_REQUIRED_BASELINES
    required_cold_baselines = (
        tuple(args.required_cold_baseline) or DEFAULT_REQUIRED_COLD_BASELINES
    )
    result = check_prefix_cache_probe(
        metadata=metadata,
        rows=rows,
        low=low,
        high=high,
        expected_limit=args.expected_limit,
        required_baselines=required_baselines,
        min_median_speedup=args.min_median_speedup,
        max_estimated_bytes=args.max_estimated_bytes,
        max_startup_warmup_ms=args.max_startup_warmup_ms,
        require_stable=not args.allow_noisy,
        required_cold_baselines=required_cold_baselines,
        min_cold_median_speedup=args.min_cold_median_speedup,
        require_cold_stable=not args.allow_noisy_cold,
    )

    if result["ok"]:
        print(format_success(result))
        return 0

    print("ERROR: prefix-cache promotion gate failed.", file=sys.stderr)
    for failure in result["failures"]:
        print(f"  - {failure}", file=sys.stderr)
    for row in result["baseline_rows"]:
        print(f"  - observed {format_baseline_row(row)}", file=sys.stderr)
    for row in result["cold_rows"]:
        print(f"  - observed cold {format_baseline_row(row)}", file=sys.stderr)
    return 1


def load_metadata(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"expected metadata object in {path}")
    return data


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def parse_range(value: str) -> tuple[int, int]:
    try:
        low_text, high_text = value.split(":", 1)
        low = int(low_text)
        high = int(high_text)
    except ValueError as exc:
        raise ValueError(f"invalid range {value!r}; expected LOW:HIGH") from exc
    if high <= low:
        raise ValueError(f"invalid range {value!r}; high must exceed low")
    return low, high


def check_prefix_cache_probe(
    *,
    metadata: dict[str, Any],
    rows: list[dict[str, str]],
    low: int,
    high: int,
    expected_limit: int,
    required_baselines: tuple[str, ...],
    min_median_speedup: float,
    max_estimated_bytes: int,
    max_startup_warmup_ms: float,
    require_stable: bool,
    required_cold_baselines: tuple[str, ...] = (),
    min_cold_median_speedup: float = 0.0,
    require_cold_stable: bool = True,
) -> dict[str, Any]:
    failures: list[str] = []
    server = metadata.get("tools", {}).get("circle_count_server", {})
    if not isinstance(server, dict):
        failures.append("metadata is missing tools.circle_count_server")
        server = {}

    cache_limit = maybe_int(server.get("small_prefix_pi_cache_limit"))
    estimated_bytes = maybe_int(server.get("small_prefix_pi_cache_estimated_bytes"))
    if cache_limit != expected_limit:
        failures.append(
            f"cache limit {cache_limit!r} did not match expected {expected_limit}"
        )
    if estimated_bytes is None:
        failures.append("metadata is missing small-prefix cache estimated bytes")
    elif estimated_bytes > max_estimated_bytes:
        failures.append(
            f"cache estimated bytes {estimated_bytes} exceeds ceiling "
            f"{max_estimated_bytes}"
        )

    warmup_rows = matching_warmup_rows(server, low, high, expected_limit)
    if not warmup_rows:
        failures.append(
            f"metadata has no warmup profile for [{low}, {high}) at limit "
            f"{expected_limit}"
        )
        startup_warmup_ms = None
    else:
        startup_warmup_ms = max(
            float(row["startup_warmup_ms"]) for row in warmup_rows
        )
        if startup_warmup_ms > max_startup_warmup_ms:
            failures.append(
                f"startup warmup {startup_warmup_ms:.3f} ms exceeds ceiling "
                f"{max_startup_warmup_ms:.3f} ms"
            )

    baseline_rows: list[dict[str, Any]] = []
    for baseline in required_baselines:
        row = best_speedup_row(rows, low, high, baseline)
        if row is None:
            failures.append(
                f"missing warmed Circle speedup row for baseline {baseline} "
                f"on [{low}, {high})"
            )
            continue
        median_speedup = parse_float(row.get("median_speedup"), "median_speedup")
        stability = row.get("sample_stability", "")
        if median_speedup < min_median_speedup:
            failures.append(
                f"{baseline} median speedup {median_speedup:.3f}x is below "
                f"{min_median_speedup:.3f}x"
            )
        if require_stable and stability != "stable":
            failures.append(
                f"{baseline} speedup samples are {stability or 'unknown'}, "
                "not stable"
            )
        baseline_rows.append(
            {
                "baseline": baseline,
                "name": row.get("name", ""),
                "median_speedup": median_speedup,
                "best_speedup": parse_float(row.get("best_speedup"), "best_speedup"),
                "sample_stability": stability,
            }
        )

    cold_rows: list[dict[str, Any]] = []
    for baseline in required_cold_baselines:
        row = best_cold_speedup_row(rows, low, high, baseline)
        if row is None:
            failures.append(
                f"missing cold Circle default speedup row for baseline {baseline} "
                f"on [{low}, {high})"
            )
            continue
        median_speedup = parse_float(row.get("median_speedup"), "median_speedup")
        stability = row.get("sample_stability", "")
        if median_speedup < min_cold_median_speedup:
            failures.append(
                f"cold {baseline} median speedup {median_speedup:.3f}x is below "
                f"{min_cold_median_speedup:.3f}x"
            )
        if require_cold_stable and stability != "stable":
            failures.append(
                f"cold {baseline} speedup samples are {stability or 'unknown'}, "
                "not stable"
            )
        cold_rows.append(
            {
                "baseline": baseline,
                "name": row.get("name", ""),
                "median_speedup": median_speedup,
                "best_speedup": parse_float(row.get("best_speedup"), "best_speedup"),
                "sample_stability": stability,
            }
        )

    return {
        "ok": not failures,
        "failures": failures,
        "low": low,
        "high": high,
        "cache_limit": cache_limit,
        "estimated_bytes": estimated_bytes,
        "startup_warmup_ms": startup_warmup_ms,
        "baseline_rows": baseline_rows,
        "cold_rows": cold_rows,
        "min_median_speedup": min_median_speedup,
        "min_cold_median_speedup": min_cold_median_speedup,
        "max_estimated_bytes": max_estimated_bytes,
        "max_startup_warmup_ms": max_startup_warmup_ms,
    }


def matching_warmup_rows(
    server: dict[str, Any],
    low: int,
    high: int,
    expected_limit: int,
) -> list[dict[str, Any]]:
    rows = server.get("small_prefix_pi_cache_warmup_profiles", [])
    if not isinstance(rows, list):
        return []
    matches: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if (
            maybe_int(row.get("low")) == low
            and maybe_int(row.get("high")) == high
            and maybe_int(row.get("cache_limit")) == expected_limit
            and row.get("count_mode") == "prefix-pi"
            and "startup_warmup_ms" in row
        ):
            matches.append(row)
    return matches


def best_speedup_row(
    rows: list[dict[str, str]],
    low: int,
    high: int,
    baseline: str,
) -> dict[str, str] | None:
    candidates = [
        row
        for row in rows
        if row.get("kind") == "speedup"
        and row.get("baseline") == baseline
        and row.get("count_mode") == "prefix-pi"
        and row.get("name", "").startswith("circle_prime_server_")
        and maybe_int(row.get("low")) == low
        and maybe_int(row.get("high")) == high
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: parse_float(row.get("median_speedup"), "median_speedup"),
    )


def best_cold_speedup_row(
    rows: list[dict[str, str]],
    low: int,
    high: int,
    baseline: str,
) -> dict[str, str] | None:
    candidates = [
        row
        for row in rows
        if row.get("kind") == "speedup"
        and row.get("baseline") == baseline
        and row.get("count_mode") == "prefix-pi"
        and row.get("name", "").startswith("circle_prime_")
        and not row.get("name", "").startswith("circle_prime_server_")
        and "_default_count" in row.get("name", "")
        and maybe_int(row.get("low")) == low
        and maybe_int(row.get("high")) == high
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: parse_float(row.get("median_speedup"), "median_speedup"),
    )


def maybe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}: {value!r}") from exc


def format_success(result: dict[str, Any]) -> str:
    baselines = ", ".join(
        format_baseline_row(row) for row in result["baseline_rows"]
    )
    cold = ", ".join(format_baseline_row(row) for row in result["cold_rows"])
    return (
        "OK: prefix-cache promotion gate passed for "
        f"[{result['low']}, {result['high']}) at limit {result['cache_limit']}; "
        f"bytes={result['estimated_bytes']}; "
        f"warmup={result['startup_warmup_ms']:.3f} ms; "
        f"{baselines}; cold {cold}."
    )


def format_baseline_row(row: dict[str, Any]) -> str:
    return (
        f"{row['baseline']} median={row['median_speedup']:.3f}x "
        f"best={row['best_speedup']:.3f}x "
        f"stability={row['sample_stability'] or 'unknown'}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
