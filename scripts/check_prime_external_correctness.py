from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.benchmark_prime_external_controls import (
    DEFAULT_CIRCLE_COUNT_MODES,
    ROOT,
    build_circle_prime,
    circle_prime_command,
    circle_prime_metadata,
    external_tool_metadata,
    parse_circle_count_modes,
    parse_integer_output,
    parse_ranges,
    parse_segment_size_list,
    primecount_command,
    primesieve_command,
    require_cargo,
    required_external_tools_missing,
    run_primecount,
    utc_now,
)


RESULTS_DIR = ROOT / "sidecars" / "PRIME_ENGINE" / "results"
DEFAULT_RANGES = (
    "0:1000,"
    "529:5000,"
    "0:1000000,"
    "0:10000000,"
    "1000000:1010000,"
    "4294900000:4295100000,"
    "999999000000:1000001000000,"
    "1000000000000:1000010000000"
)
DEFAULT_ENUMERATION_RANGES = (
    "0:1000,"
    "529:1000,"
    "1000000:1001000,"
    "4294967000:4294968000,"
    "1000000000000:1000000001000,"
    "18446744073709551515:18446744073709551615"
)
DEFAULT_NEXT_STARTS = "0,2,90,1000000,4294967000,1000000000000"
DEFAULT_NEXT_SEARCH_WINDOW = 100_000
DEFAULT_OUTPUT = RESULTS_DIR / "prime_engine_external_correctness_latest.json"
DEFAULT_REQUIRED_TOOLS = ("primesieve", "primecount")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check Circle prime counts against external primesieve and primecount "
            "without collecting timing samples."
        )
    )
    parser.add_argument("--ranges", default=DEFAULT_RANGES)
    parser.add_argument(
        "--enumeration-ranges",
        default=DEFAULT_ENUMERATION_RANGES,
        help=(
            "Comma-separated LOW:HIGH ranges for exact prime-list checks "
            "against primesieve --print."
        ),
    )
    parser.add_argument(
        "--next-starts",
        default=DEFAULT_NEXT_STARTS,
        help="Comma-separated starts for next-prime checks against primesieve --print.",
    )
    parser.add_argument(
        "--next-search-window",
        type=int,
        default=DEFAULT_NEXT_SEARCH_WINDOW,
        help="Inclusive search window passed to primesieve for each next-prime check.",
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
            "Comma-separated Circle segment sizes to check. Use 0 to include the "
            "Rust CLI adaptive default. When set, this overrides --segment-size."
        ),
    )
    parser.add_argument(
        "--circle-count-modes",
        default=DEFAULT_CIRCLE_COUNT_MODES,
        help=(
            "Comma-separated Circle count modes to check. Use 'all' for every "
            "currently exposed count mode."
        ),
    )
    parser.add_argument("--circle-threads", type=int, default=8)
    parser.add_argument("--external-threads", type=int, default=8)
    parser.add_argument(
        "--require-tool",
        choices=DEFAULT_REQUIRED_TOOLS,
        action="append",
        default=[],
        help=(
            "External tool that must be available. Defaults to requiring both "
            "primesieve and primecount when this flag is omitted."
        ),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.segment_size < 0:
        parser.error("--segment-size must be nonnegative")
    if args.circle_threads <= 0:
        parser.error("--circle-threads must be positive")
    if args.external_threads < 0:
        parser.error("--external-threads must be nonnegative")
    if args.next_search_window <= 0:
        parser.error("--next-search-window must be positive")

    try:
        ranges = parse_ranges(args.ranges)
        enumeration_ranges = parse_ranges(args.enumeration_ranges)
        next_starts = parse_integer_list_argument(args.next_starts)
        segment_sizes = parse_segment_size_list(args.segment_sizes, args.segment_size)
        circle_count_modes = parse_count_modes_argument(args.circle_count_modes)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    required_tools = sorted(set(args.require_tool or DEFAULT_REQUIRED_TOOLS))
    started_at_utc = utc_now()
    primesieve = shutil.which("primesieve")
    primecount = shutil.which("primecount")
    missing_tools = required_external_tools_missing(
        required_tools,
        primesieve=primesieve,
        primecount=primecount,
    )
    if missing_tools:
        report = build_report(
            started_at_utc=started_at_utc,
            cargo=None,
            circle_prime=None,
            primesieve=primesieve,
            primecount=primecount,
            ranges=ranges,
            enumeration_ranges=enumeration_ranges,
            next_starts=next_starts,
            segment_sizes=segment_sizes,
            circle_count_modes=circle_count_modes,
            circle_threads=args.circle_threads,
            external_threads=args.external_threads,
            required_tools=required_tools,
            checks=[],
            missing_tools=missing_tools,
        )
        emit_report(report, args.output)
        tools = ", ".join(missing_tools)
        raise RuntimeError(
            f"required external control(s) unavailable: {tools}; "
            "install with `brew install primesieve primecount`"
        )

    cargo = require_cargo()
    circle_prime = build_circle_prime(cargo)
    checks = run_checks(
        circle_prime=circle_prime,
        primesieve=primesieve,
        primecount=primecount,
        ranges=ranges,
        segment_sizes=segment_sizes,
        circle_count_modes=circle_count_modes,
        circle_threads=args.circle_threads,
        external_threads=args.external_threads,
    )
    enumeration_checks = run_enumeration_checks(
        circle_prime=circle_prime,
        primesieve=primesieve,
        ranges=enumeration_ranges,
        segment_sizes=segment_sizes,
    )
    next_checks = run_next_checks(
        circle_prime=circle_prime,
        primesieve=primesieve,
        starts=next_starts,
        search_window=args.next_search_window,
    )
    report = build_report(
        started_at_utc=started_at_utc,
        cargo=cargo,
        circle_prime=circle_prime,
        primesieve=primesieve,
        primecount=primecount,
        ranges=ranges,
        enumeration_ranges=enumeration_ranges,
        next_starts=next_starts,
        segment_sizes=segment_sizes,
        circle_count_modes=circle_count_modes,
        circle_threads=args.circle_threads,
        external_threads=args.external_threads,
        required_tools=required_tools,
        checks=checks,
        enumeration_checks=enumeration_checks,
        next_checks=next_checks,
        missing_tools=[],
    )
    emit_report(report, args.output)
    if report["failure_count"]:
        raise AssertionError(
            f"external correctness check failed for {report['failure_count']} "
            f"of {report['check_count']} Circle variants"
        )
    print(
        "external prime correctness checks ok: "
        f"{report['check_count']} Circle variants matched {', '.join(required_tools)}"
    )
    return 0


def parse_count_modes_argument(raw: str) -> list[str]:
    if raw.strip() == "all":
        return parse_circle_count_modes(
            "segmented,balanced,dynamic,prefix-pi,presieve13,wheel30-mark,hybrid-wheel30-mark"
        )
    return parse_circle_count_modes(raw)


def parse_integer_list_argument(raw: str) -> list[int]:
    values = []
    for item in raw.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        try:
            value = int(stripped)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"expected comma-separated nonnegative integers, got {stripped!r}"
            ) from exc
        if value < 0:
            raise argparse.ArgumentTypeError(
                f"expected comma-separated nonnegative integers, got {stripped!r}"
            )
        values.append(value)
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def run_checks(
    *,
    circle_prime: Path,
    primesieve: str | None,
    primecount: str | None,
    ranges: list[tuple[int, int]],
    segment_sizes: list[int],
    circle_count_modes: list[str],
    circle_threads: int,
    external_threads: int,
) -> list[dict[str, Any]]:
    checks = []
    for low, high in ranges:
        external_counts = external_range_counts(
            primesieve=primesieve,
            primecount=primecount,
            low=low,
            high=high,
            external_threads=external_threads,
        )
        seen_variants: set[tuple[str, int, int]] = set()
        for segment_size in segment_sizes:
            for count_mode in circle_count_modes:
                requested_variant_key = requested_circle_variant_key(
                    count_mode,
                    segment_size,
                    circle_threads,
                )
                if requested_variant_key in seen_variants:
                    continue
                seen_variants.add(requested_variant_key)
                circle = circle_count(
                    circle_prime,
                    low,
                    high,
                    segment_size,
                    circle_threads,
                    count_mode,
                )
                variant_key = (
                    str(circle["count_mode"]),
                    int(circle["segment_size"]),
                    int(circle["threads"]),
                )
                if variant_key in seen_variants:
                    continue
                seen_variants.add(variant_key)
                matches = {
                    name: circle["count"] == count
                    for name, count in external_counts.items()
                }
                checks.append(
                    {
                        "low": low,
                        "high": high,
                        "span": high - low,
                        "count_mode": circle["count_mode"],
                        "segment_size": circle["segment_size"],
                        "threads": circle["threads"],
                        "requested_threads": circle["requested_threads"],
                        "circle_count": circle["count"],
                        "external_counts": external_counts,
                        "matches": matches,
                        "passes": all(matches.values()),
                    }
                )
    return checks


def requested_circle_variant_key(
    count_mode: str,
    segment_size: int,
    threads: int,
) -> tuple[str, int, int]:
    if count_mode in {"prefix-pi", "pi"}:
        return ("prefix-pi", 0, 1)
    return (count_mode, segment_size, threads)


def external_range_counts(
    *,
    primesieve: str | None,
    primecount: str | None,
    low: int,
    high: int,
    external_threads: int,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    stop = high - 1
    if primesieve is not None:
        completed = subprocess.run(
            primesieve_command(primesieve, low, stop, external_threads),
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        counts["primesieve"] = parse_integer_output(completed.stdout)
    if primecount is not None:
        high_count = run_primecount(primecount, stop, external_threads)
        low_count = run_primecount(primecount, low - 1, external_threads) if low > 0 else 0
        counts["primecount"] = high_count - low_count
    return counts


def run_enumeration_checks(
    *,
    circle_prime: Path,
    primesieve: str | None,
    ranges: list[tuple[int, int]],
    segment_sizes: list[int],
) -> list[dict[str, Any]]:
    if primesieve is None:
        return []
    checks = []
    for low, high in ranges:
        expected_primes = primesieve_primes(primesieve, low, high)
        seen_variants: set[int] = set()
        for segment_size in segment_sizes:
            circle = circle_primes(circle_prime, low, high, segment_size)
            resolved_segment_size = int(circle["segment_size"])
            if resolved_segment_size in seen_variants:
                continue
            seen_variants.add(resolved_segment_size)
            circle_values = circle["primes"]
            checks.append(
                {
                    "low": low,
                    "high": high,
                    "span": high - low,
                    "segment_size": resolved_segment_size,
                    "threads": circle["threads"],
                    "requested_threads": circle["requested_threads"],
                    "circle_count": len(circle_values),
                    "external_count": len(expected_primes),
                    "first_mismatch": first_mismatch(circle_values, expected_primes),
                    "passes": circle_values == expected_primes,
                }
            )
    return checks


def run_next_checks(
    *,
    circle_prime: Path,
    primesieve: str | None,
    starts: list[int],
    search_window: int,
) -> list[dict[str, Any]]:
    if primesieve is None:
        return []
    checks = []
    for start in starts:
        expected = primesieve_next_prime(primesieve, start, search_window)
        circle = circle_next_prime(circle_prime, start)
        checks.append(
            {
                "start": start,
                "search_window": search_window,
                "circle_prime": circle["prime"],
                "external_prime": expected,
                "candidate_count": circle["candidate_count"],
                "passes": circle["prime"] == expected,
            }
        )
    return checks


def primesieve_primes(binary: str, low: int, high: int) -> list[int]:
    stop = high - 1
    completed = subprocess.run(
        [binary, str(low), str(stop), "--print", "--quiet"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return parse_integer_list(completed.stdout)


def primesieve_next_prime(binary: str, start: int, search_window: int) -> int | None:
    high = start + search_window
    values = primesieve_primes(binary, start, high + 1)
    return values[0] if values else None


def circle_next_prime(binary: Path, start: int) -> dict[str, Any]:
    completed = subprocess.run(
        [str(binary), "next", str(start), "--json"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    return {
        "prime": payload["prime"],
        "candidate_count": int(payload["candidate_count"]),
    }


def circle_primes(
    binary: Path,
    low: int,
    high: int,
    segment_size: int,
) -> dict[str, Any]:
    command = [
        str(binary),
        "range",
        str(low),
        str(high),
        "--json",
    ]
    if segment_size > 0:
        command.extend(["--segment-size", str(segment_size)])
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    return {
        "primes": [int(value) for value in payload["primes"]],
        "segment_size": int(payload["segment_size"]),
        "threads": int(payload["threads"]),
        "requested_threads": int(payload["requested_threads"]),
    }


def parse_integer_list(output: str) -> list[int]:
    values: list[int] = []
    for line in output.splitlines():
        stripped = line.strip().replace(",", "")
        if stripped:
            values.append(int(stripped))
    return values


def first_mismatch(left: list[int], right: list[int]) -> dict[str, Any] | None:
    for index, (left_value, right_value) in enumerate(zip(left, right)):
        if left_value != right_value:
            return {
                "index": index,
                "circle": left_value,
                "external": right_value,
            }
    if len(left) != len(right):
        index = min(len(left), len(right))
        return {
            "index": index,
            "circle": left[index] if index < len(left) else None,
            "external": right[index] if index < len(right) else None,
        }
    return None


def circle_count(
    binary: Path,
    low: int,
    high: int,
    segment_size: int,
    threads: int,
    count_mode: str,
) -> dict[str, int | str]:
    command = circle_prime_command(
        binary,
        low,
        high,
        segment_size,
        threads,
        count_mode,
        json_output=True,
    )
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    return {
        "count": int(payload["count"]),
        "count_mode": str(payload.get("count_mode", "segmented")),
        "segment_size": int(payload["segment_size"]),
        "threads": int(payload["threads"]),
        "requested_threads": int(payload["requested_threads"]),
    }


def build_report(
    *,
    started_at_utc: str,
    cargo: str | None,
    circle_prime: Path | None,
    primesieve: str | None,
    primecount: str | None,
    ranges: list[tuple[int, int]],
    enumeration_ranges: list[tuple[int, int]] | None = None,
    next_starts: list[int] | None = None,
    segment_sizes: list[int],
    circle_count_modes: list[str],
    circle_threads: int,
    external_threads: int,
    required_tools: list[str],
    checks: list[dict[str, Any]],
    enumeration_checks: list[dict[str, Any]] | None = None,
    next_checks: list[dict[str, Any]] | None = None,
    missing_tools: list[str],
) -> dict[str, Any]:
    if enumeration_ranges is None:
        enumeration_ranges = []
    if next_starts is None:
        next_starts = []
    if enumeration_checks is None:
        enumeration_checks = []
    if next_checks is None:
        next_checks = []
    count_failure_count = sum(1 for check in checks if not check["passes"])
    enumeration_failure_count = sum(
        1 for check in enumeration_checks if not check["passes"]
    )
    next_failure_count = sum(1 for check in next_checks if not check["passes"])
    failure_count = count_failure_count + enumeration_failure_count + next_failure_count
    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": utc_now(),
        "ranges": [{"low": low, "high": high, "span": high - low} for low, high in ranges],
        "enumeration_ranges": [
            {"low": low, "high": high, "span": high - low}
            for low, high in enumeration_ranges
        ],
        "next_starts": next_starts,
        "requested_segment_sizes": segment_sizes,
        "circle_count_modes": circle_count_modes,
        "thread_policy": {
            "circle_requested_threads": circle_threads,
            "external_requested_threads": external_threads,
        },
        "required_external_tools": required_tools,
        "missing_external_tools": missing_tools,
        "tools": {
            "circle_prime": circle_prime_metadata(cargo, circle_prime),
            "primesieve": external_tool_metadata("primesieve", primesieve, ["--version"]),
            "primecount": external_tool_metadata("primecount", primecount, ["--version"]),
        },
        "count_check_count": len(checks),
        "enumeration_check_count": len(enumeration_checks),
        "next_check_count": len(next_checks),
        "check_count": len(checks) + len(enumeration_checks) + len(next_checks),
        "count_failure_count": count_failure_count,
        "enumeration_failure_count": enumeration_failure_count,
        "next_failure_count": next_failure_count,
        "failure_count": failure_count,
        "passes": not missing_tools and failure_count == 0,
        "checks": checks,
        "enumeration_checks": enumeration_checks,
        "next_checks": next_checks,
    }


def emit_report(report: dict[str, Any], output: Path | None) -> None:
    if output is None:
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"wrote external correctness JSON to {output}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
