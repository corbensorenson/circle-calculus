from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METADATA = (
    ROOT / "sidecars" / "PRIME_ENGINE" / "results" / "prime_engine_high_offset_hot_server_latest.json"
)
DEFAULT_CIRCLE_PRIME = ROOT / "target" / "release" / "circle-prime"
DEFAULT_CIRCLE_PRIME_COUNT = ROOT / "target" / "release" / "circle-prime-count"
DEFAULT_DEFAULTS = ROOT / "rust" / "circle-prime" / "prime_engine_defaults.json"
PERSISTENT_HELPER_TOOLS = (
    "primesieve_count_server",
    "primecount_pi_server",
    "primesieve_library_server",
    "primesieve_iterator_server",
    "primecount_library_server",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that a Circle prime benchmark metadata artifact was produced "
            "with the current circle-prime binary and prime-engine defaults."
        )
    )
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--circle-prime", type=Path, default=DEFAULT_CIRCLE_PRIME)
    parser.add_argument(
        "--circle-prime-count",
        type=Path,
        default=DEFAULT_CIRCLE_PRIME_COUNT,
    )
    parser.add_argument(
        "--max-circle-prime-count-size-bytes",
        type=int,
        help="Fail if the current circle-prime-count release binary exceeds this size.",
    )
    parser.add_argument("--defaults", type=Path, default=DEFAULT_DEFAULTS)
    parser.add_argument(
        "--expect",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Require a top-level or dotted metadata field to equal VALUE. "
            "VALUE is parsed as JSON when possible, otherwise as a string."
        ),
    )
    parser.add_argument(
        "--expect-ranges",
        help="Require metadata.ranges to equal comma-separated LOW:HIGH ranges.",
    )
    parser.add_argument(
        "--expect-starts",
        help="Require metadata.starts to equal comma-separated integer starts.",
    )
    parser.add_argument(
        "--require-tool-version-at-least",
        action="append",
        default=[],
        metavar="TOOL=VERSION",
        help=(
            "Require metadata.tools.TOOL.version to parse as at least VERSION. "
            "Use this for serious external controls, e.g. primesieve=12.14."
        ),
    )
    args = parser.parse_args()

    if not args.metadata.exists():
        print(f"ERROR: benchmark metadata is missing: {args.metadata}", file=sys.stderr)
        return 1
    metadata = json.loads(args.metadata.read_text())
    failures = benchmark_provenance_failures(
        metadata,
        circle_prime=args.circle_prime,
        circle_prime_count=args.circle_prime_count,
        defaults_path=args.defaults,
        max_circle_prime_count_size_bytes=args.max_circle_prime_count_size_bytes,
    )
    failures.extend(metadata_expectation_failures(metadata, args.expect))
    if args.expect_ranges:
        failures.extend(metadata_range_expectation_failures(metadata, args.expect_ranges))
    if args.expect_starts:
        failures.extend(metadata_start_expectation_failures(metadata, args.expect_starts))
    failures.extend(
        metadata_tool_version_expectation_failures(
            metadata,
            args.require_tool_version_at_least,
        )
    )
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(
        "prime benchmark provenance ok: "
        f"metadata={args.metadata}, "
        f"circle-prime={short_hash(file_sha256(args.circle_prime) or '')}, "
        f"defaults={short_hash(file_sha256(args.defaults) or '')}"
    )
    return 0


def benchmark_provenance_failures(
    metadata: dict[str, Any],
    *,
    circle_prime: Path,
    defaults_path: Path,
    circle_prime_count: Path = DEFAULT_CIRCLE_PRIME_COUNT,
    max_circle_prime_count_size_bytes: int | None = None,
) -> list[str]:
    current_binary = file_sha256(circle_prime)
    current_defaults = file_sha256(defaults_path)
    failures = []
    if current_binary is None:
        failures.append(f"current circle-prime binary is missing: {circle_prime}")
    if current_defaults is None:
        failures.append(f"current defaults file is missing: {defaults_path}")

    circle_prime_meta = metadata.get("tools", {}).get("circle_prime", {})
    binary_meta = circle_prime_meta.get("binary") or {}
    defaults_meta = metadata.get("circle_prime_defaults") or circle_prime_meta.get(
        "defaults"
    ) or {}
    recorded_binary = binary_meta.get("sha256")
    recorded_defaults = defaults_meta.get("sha256")

    if not recorded_binary:
        failures.append(
            "benchmark metadata lacks a circle-prime binary hash; rerun the benchmark target."
        )
    elif current_binary is not None and recorded_binary != current_binary:
        failures.append(
            "benchmark metadata was produced by circle-prime "
            f"{short_hash(recorded_binary)}, current binary is {short_hash(current_binary)}."
        )

    if not recorded_defaults:
        failures.append(
            "benchmark metadata lacks a prime-engine defaults hash; rerun the benchmark target."
        )
    elif current_defaults is not None and recorded_defaults != current_defaults:
        failures.append(
            "benchmark metadata used defaults "
            f"{short_hash(recorded_defaults)}, current defaults are {short_hash(current_defaults)}."
        )
    if metadata.get("include_circle_count_binary"):
        failures.extend(
            count_binary_provenance_failures(
                metadata,
                circle_prime_count,
                max_size_bytes=max_circle_prime_count_size_bytes,
            )
        )
    failures.extend(helper_tool_provenance_failures(metadata.get("tools", {})))
    return failures


def count_binary_provenance_failures(
    metadata: dict[str, Any],
    circle_prime_count: Path,
    *,
    max_size_bytes: int | None = None,
) -> list[str]:
    current_binary = file_sha256(circle_prime_count)
    failures = []
    if current_binary is None:
        failures.append(f"current circle-prime-count binary is missing: {circle_prime_count}")
    elif max_size_bytes is not None:
        current_size = circle_prime_count.stat().st_size
        if current_size > max_size_bytes:
            failures.append(
                "current circle-prime-count binary is "
                f"{current_size} bytes, exceeding max {max_size_bytes}; keep the "
                "cold count binary slim or rerun the benchmark with an explicit "
                "larger limit."
            )

    count_meta = metadata.get("tools", {}).get("circle_prime_count", {})
    binary_meta = count_meta.get("binary") if isinstance(count_meta, dict) else {}
    recorded_binary = binary_meta.get("sha256") if isinstance(binary_meta, dict) else None
    if not recorded_binary:
        failures.append(
            "benchmark metadata lacks a circle-prime-count binary hash; rerun the benchmark target."
        )
    elif current_binary is not None and recorded_binary != current_binary:
        failures.append(
            "benchmark metadata was produced by circle-prime-count "
            f"{short_hash(recorded_binary)}, current binary is {short_hash(current_binary)}."
        )
    return failures


def metadata_expectation_failures(
    metadata: dict[str, Any],
    expectations: list[str],
) -> list[str]:
    failures = []
    for expectation in expectations:
        if "=" not in expectation:
            failures.append(
                f"metadata expectation must be KEY=VALUE, got {expectation!r}."
            )
            continue
        key, raw_expected = expectation.split("=", 1)
        key = key.strip()
        if not key:
            failures.append(
                f"metadata expectation must name a field, got {expectation!r}."
            )
            continue
        expected = parse_expected_metadata_value(raw_expected)
        found = lookup_metadata_field(metadata, key)
        if found is MISSING:
            failures.append(f"metadata lacks expected field {key!r}.")
        elif found != expected:
            failures.append(
                f"metadata field {key!r} is {json.dumps(found, sort_keys=True)}, "
                f"expected {json.dumps(expected, sort_keys=True)}."
            )
    return failures


def metadata_range_expectation_failures(
    metadata: dict[str, Any],
    raw_ranges: str,
) -> list[str]:
    try:
        expected = parse_range_spec(raw_ranges)
    except ValueError as exc:
        return [str(exc)]
    found = metadata.get("ranges")
    if found != expected:
        return [
            "metadata field 'ranges' is "
            f"{json.dumps(found, sort_keys=True)}, expected "
            f"{json.dumps(expected, sort_keys=True)}."
        ]
    return []


def metadata_start_expectation_failures(
    metadata: dict[str, Any],
    raw_starts: str,
) -> list[str]:
    try:
        expected = parse_int_list(raw_starts, label="start")
    except ValueError as exc:
        return [str(exc)]
    found = metadata.get("starts")
    if found != expected:
        return [
            "metadata field 'starts' is "
            f"{json.dumps(found, sort_keys=True)}, expected "
            f"{json.dumps(expected, sort_keys=True)}."
        ]
    return []


def metadata_tool_version_expectation_failures(
    metadata: dict[str, Any],
    expectations: list[str],
) -> list[str]:
    failures = []
    tools = metadata.get("tools")
    if expectations and not isinstance(tools, dict):
        return ["benchmark metadata lacks tool provenance; rerun the benchmark target."]
    for expectation in expectations:
        if "=" not in expectation:
            failures.append(
                "tool version expectation must be TOOL=VERSION, "
                f"got {expectation!r}."
            )
            continue
        tool_name, raw_minimum = expectation.split("=", 1)
        tool_name = tool_name.strip()
        raw_minimum = raw_minimum.strip()
        if not tool_name or not raw_minimum:
            failures.append(
                "tool version expectation must be TOOL=VERSION, "
                f"got {expectation!r}."
            )
            continue
        minimum = parse_version_tuple(raw_minimum)
        if minimum is None:
            failures.append(
                f"tool version expectation for {tool_name!r} has invalid "
                f"minimum {raw_minimum!r}."
            )
            continue
        tool = tools.get(tool_name) if isinstance(tools, dict) else None
        if not isinstance(tool, dict) or not tool.get("available"):
            failures.append(
                f"benchmark metadata does not show required tool {tool_name!r} "
                "as available."
            )
            continue
        raw_found = tool.get("version")
        if not isinstance(raw_found, str) or not raw_found.strip():
            failures.append(
                f"benchmark metadata lacks a version string for tool {tool_name!r}."
            )
            continue
        found = parse_version_tuple(raw_found)
        if found is None:
            failures.append(
                f"benchmark metadata tool {tool_name!r} has unparseable version "
                f"{raw_found!r}."
            )
            continue
        if compare_versions(found, minimum) < 0:
            failures.append(
                f"benchmark metadata tool {tool_name!r} version "
                f"{format_version(found)} is below required {format_version(minimum)}."
            )
    return failures


MISSING = object()


def lookup_metadata_field(metadata: dict[str, Any], key: str) -> Any:
    current: Any = metadata
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return MISSING
        current = current[part]
    return current


def parse_expected_metadata_value(raw: str) -> Any:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def parse_range_spec(raw_ranges: str) -> list[dict[str, int]]:
    ranges = []
    for part in raw_ranges.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(f"range expectation must use LOW:HIGH, got {part!r}.")
        raw_low, raw_high = part.split(":", 1)
        try:
            low = int(raw_low)
            high = int(raw_high)
        except ValueError as exc:
            raise ValueError(f"range expectation contains non-integer bound: {part!r}.") from exc
        if high < low:
            raise ValueError(f"range expectation has high < low: {part!r}.")
        ranges.append({"low": low, "high": high, "span": high - low})
    if not ranges:
        raise ValueError("range expectation must include at least one LOW:HIGH range.")
    return ranges


def parse_int_list(raw_values: str, *, label: str) -> list[int]:
    values = []
    for part in raw_values.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            value = int(part)
        except ValueError as exc:
            raise ValueError(
                f"{label} expectation contains non-integer value: {part!r}."
            ) from exc
        values.append(value)
    if not values:
        raise ValueError(f"{label} expectation must include at least one integer.")
    return values


def parse_version_tuple(raw: str) -> tuple[int, ...] | None:
    digits = []
    current = ""
    for char in raw:
        if char.isdigit():
            current += char
        elif char == "." and current:
            digits.append(int(current))
            current = ""
        elif digits or current:
            break
    if current:
        digits.append(int(current))
    return tuple(digits) if digits else None


def compare_versions(found: tuple[int, ...], minimum: tuple[int, ...]) -> int:
    width = max(len(found), len(minimum))
    normalized_found = found + (0,) * (width - len(found))
    normalized_minimum = minimum + (0,) * (width - len(minimum))
    if normalized_found < normalized_minimum:
        return -1
    if normalized_found > normalized_minimum:
        return 1
    return 0


def format_version(version: tuple[int, ...]) -> str:
    return ".".join(str(part) for part in version)


def helper_tool_provenance_failures(tools: Any) -> list[str]:
    if not isinstance(tools, dict):
        return ["benchmark metadata lacks tool provenance; rerun the benchmark target."]
    failures = []
    for name in PERSISTENT_HELPER_TOOLS:
        tool = tools.get(name)
        if not isinstance(tool, dict) or not tool.get("available"):
            continue
        failures.extend(
            file_fingerprint_failures(
                tool.get("binary"),
                label=f"{name} helper binary",
            )
        )
        failures.extend(
            file_fingerprint_failures(
                tool.get("source_fingerprint"),
                label=f"{name} helper source",
            )
        )
    return failures


def file_fingerprint_failures(fingerprint: Any, *, label: str) -> list[str]:
    if not isinstance(fingerprint, dict):
        return [f"benchmark metadata lacks a {label} hash; rerun the benchmark target."]
    path = fingerprint.get("path")
    recorded = fingerprint.get("sha256")
    if not path:
        return [f"benchmark metadata lacks a {label} path; rerun the benchmark target."]
    if not recorded:
        return [f"benchmark metadata lacks a {label} hash; rerun the benchmark target."]
    current = file_sha256(Path(path))
    if current is None:
        return [f"current {label} is missing: {path}"]
    if current != recorded:
        return [
            f"benchmark metadata used {label} {short_hash(recorded)}, "
            f"current file is {short_hash(current)}."
        ]
    return []


def file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def short_hash(value: str) -> str:
    if not value:
        return "-"
    return value[:12]


if __name__ == "__main__":
    raise SystemExit(main())
