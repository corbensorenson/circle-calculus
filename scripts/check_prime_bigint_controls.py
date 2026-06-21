from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "sidecars" / "PRIME_ENGINE" / "results" / "prime_bigint_controls_latest.csv"
DEFAULT_METADATA = (
    ROOT / "sidecars" / "PRIME_ENGINE" / "results" / "prime_bigint_controls_latest.json"
)
SCHEMA_ID = "circle_calculus.prime_bigint_controls.v0"

PRIME_CASES = {
    "mersenne_127_prime",
    "mersenne_127_composite",
    "curve25519_prime",
    "secp256k1_prime",
    "two256_composite",
    "mersenne_521_prime",
}
PRIME_LIKE_CASES = {
    "mersenne_127_prime",
    "curve25519_prime",
    "secp256k1_prime",
    "mersenne_521_prime",
}
NEXT_CASES = {"next_at_2_127", "next_near_curve25519"}
PRIME_TEST_ENGINES = {
    "circle_big_test",
    "circle_big_test_server",
    "circle_big_bpsw_test_server",
    "openssl_prime",
    "sympy_isprime",
}
NEXT_SEARCH_ENGINES = {
    "circle_big_next",
    "circle_big_next_server",
    "circle_big_bpsw_next_server",
    "sympy_nextprime",
}
FUZZY_ANY_ENGINES = {"circle_big_fuzzy_any", "circle_big_fuzzy_any_server"}


@dataclass(frozen=True)
class BigIntRow:
    operation: str
    case: str
    bits: int
    engine: str
    result: str
    expected: str
    agreed: bool
    mr_rounds: int
    rounds: int
    median_ms: float
    min_ms: float
    max_ms: float

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.operation, self.case, self.engine)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the arbitrary-precision prime benchmark artifact."
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--expect-bench-rounds", type=int)
    parser.add_argument("--expect-warmup-rounds", type=int)
    parser.add_argument("--expect-mr-rounds", type=int)
    parser.add_argument("--expect-server-batch-size", type=int)
    parser.add_argument(
        "--min-hot-test-vs-openssl",
        type=float,
        default=1.5,
        help=(
            "Require circle_big_test_server median speedup over OpenSSL prime "
            "on every prime_test case."
        ),
    )
    parser.add_argument(
        "--min-bpsw-test-vs-openssl",
        type=float,
        default=1.5,
        help=(
            "Require circle_big_bpsw_test_server median speedup over OpenSSL "
            "prime on every prime_test case."
        ),
    )
    parser.add_argument(
        "--min-bpsw-next-vs-sympy",
        type=float,
        default=1.1,
        help=(
            "Require circle_big_bpsw_next_server median speedup over SymPy "
            "nextprime on every next_search case."
        ),
    )
    parser.add_argument(
        "--min-bpsw-prime-vs-sympy",
        type=float,
        default=0.0,
        help=(
            "Require circle_big_bpsw_test_server median speedup over SymPy "
            "isprime on the selected raw prime_test cases. Disabled at 0."
        ),
    )
    parser.add_argument(
        "--bpsw-prime-vs-sympy-cases",
        default=",".join(sorted(PRIME_LIKE_CASES)),
        help=(
            "Comma-separated prime_test cases for --min-bpsw-prime-vs-sympy. "
            "Defaults to the selected prime-like cases."
        ),
    )
    parser.add_argument(
        "--require-bpsw-profile",
        dest="require_bpsw_profile",
        action="store_true",
        default=True,
        help="Require BPSW test and next-search rows in the artifact.",
    )
    parser.add_argument(
        "--skip-bpsw-profile",
        dest="require_bpsw_profile",
        action="store_false",
        help="Do not require BPSW test and next-search rows.",
    )
    parser.add_argument(
        "--require-fuzzy-any",
        dest="require_fuzzy_any",
        action="store_true",
        default=True,
        help="Require BigUint fuzzy any-prime rows for every next-search case.",
    )
    parser.add_argument(
        "--skip-fuzzy-any",
        dest="require_fuzzy_any",
        action="store_false",
        help="Do not require BigUint fuzzy any-prime rows.",
    )
    args = parser.parse_args()

    failures = validate_artifact(
        csv_path=args.csv,
        metadata_path=args.metadata,
        expect_bench_rounds=args.expect_bench_rounds,
        expect_warmup_rounds=args.expect_warmup_rounds,
        expect_mr_rounds=args.expect_mr_rounds,
        expect_server_batch_size=args.expect_server_batch_size,
        min_hot_test_vs_openssl=args.min_hot_test_vs_openssl,
        min_bpsw_test_vs_openssl=args.min_bpsw_test_vs_openssl,
        min_bpsw_next_vs_sympy=args.min_bpsw_next_vs_sympy,
        min_bpsw_prime_vs_sympy=args.min_bpsw_prime_vs_sympy,
        bpsw_prime_vs_sympy_cases=parse_case_list(
            args.bpsw_prime_vs_sympy_cases,
            allowed_cases=PRIME_CASES,
            label="--bpsw-prime-vs-sympy-cases",
        ),
        require_bpsw_profile=args.require_bpsw_profile,
        require_fuzzy_any=args.require_fuzzy_any,
    )
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(f"prime BigUint controls artifact ok: csv={args.csv}, metadata={args.metadata}")
    return 0


def validate_artifact(
    *,
    csv_path: Path,
    metadata_path: Path,
    expect_bench_rounds: int | None = None,
    expect_warmup_rounds: int | None = None,
    expect_mr_rounds: int | None = None,
    expect_server_batch_size: int | None = None,
    min_hot_test_vs_openssl: float = 1.5,
    min_bpsw_test_vs_openssl: float = 1.5,
    min_bpsw_next_vs_sympy: float = 1.1,
    min_bpsw_prime_vs_sympy: float = 0.0,
    bpsw_prime_vs_sympy_cases: set[str] | None = None,
    require_bpsw_profile: bool = True,
    require_fuzzy_any: bool = True,
) -> list[str]:
    failures: list[str] = []
    if not csv_path.exists():
        return [f"CSV artifact is missing: {csv_path}"]
    if not metadata_path.exists():
        return [f"metadata artifact is missing: {metadata_path}"]

    rows = read_rows(csv_path)
    row_by_key = {row.key: row for row in rows}
    metadata = json.loads(metadata_path.read_text())

    failures.extend(validate_metadata(metadata, rows))
    failures.extend(
        validate_metadata_expectations(
            metadata,
            expect_bench_rounds=expect_bench_rounds,
            expect_warmup_rounds=expect_warmup_rounds,
            expect_mr_rounds=expect_mr_rounds,
            expect_server_batch_size=expect_server_batch_size,
        )
    )
    failures.extend(validate_required_rows(row_by_key, require_bpsw_profile, require_fuzzy_any))
    failures.extend(validate_row_agreement_and_timings(rows))
    failures.extend(
        validate_speed_floor(
            row_by_key,
            operation="prime_test",
            cases=PRIME_CASES,
            candidate_engine="circle_big_test_server",
            baseline_engine="openssl_prime",
            minimum=min_hot_test_vs_openssl,
        )
    )
    failures.extend(
        validate_speed_floor(
            row_by_key,
            operation="prime_test",
            cases=PRIME_CASES,
            candidate_engine="circle_big_bpsw_test_server",
            baseline_engine="openssl_prime",
            minimum=min_bpsw_test_vs_openssl,
        )
    )
    failures.extend(
        validate_speed_floor(
            row_by_key,
            operation="next_search",
            cases=NEXT_CASES,
            candidate_engine="circle_big_bpsw_next_server",
            baseline_engine="sympy_nextprime",
            minimum=min_bpsw_next_vs_sympy,
        )
    )
    failures.extend(
        validate_speed_floor(
            row_by_key,
            operation="prime_test",
            cases=bpsw_prime_vs_sympy_cases or PRIME_LIKE_CASES,
            candidate_engine="circle_big_bpsw_test_server",
            baseline_engine="sympy_isprime",
            minimum=min_bpsw_prime_vs_sympy,
        )
    )
    return failures


def validate_metadata(metadata: dict[str, Any], rows: list[BigIntRow]) -> list[str]:
    failures = []
    if metadata.get("schema") != SCHEMA_ID:
        failures.append(
            f"metadata schema mismatch: expected {SCHEMA_ID}, got {metadata.get('schema')!r}"
        )
    recorded_row_count = metadata.get("row_count")
    if recorded_row_count is not None and recorded_row_count != len(rows):
        failures.append(
            f"metadata row_count {recorded_row_count!r} does not match CSV row count {len(rows)}"
        )
    if metadata.get("failures"):
        failures.append(f"metadata records benchmark failures: {metadata.get('failures')!r}")
    circle_prime = metadata.get("circle_prime") or {}
    if not circle_prime.get("exists"):
        failures.append("metadata does not show an available circle-prime binary")
    model = metadata.get("big_fuzzy_model") or {}
    if not model.get("exists"):
        failures.append("metadata does not show an available BigUint fuzzy model")
    tools = metadata.get("tools") or {}
    for tool in ["openssl", "sympy"]:
        version = tools.get(tool)
        if not isinstance(version, str) or not version or version.startswith("unavailable"):
            failures.append(f"metadata does not show an available {tool} control")
    return failures


def validate_metadata_expectations(
    metadata: dict[str, Any],
    *,
    expect_bench_rounds: int | None,
    expect_warmup_rounds: int | None,
    expect_mr_rounds: int | None,
    expect_server_batch_size: int | None,
) -> list[str]:
    failures = []
    for key, expected in [
        ("bench_rounds", expect_bench_rounds),
        ("warmup_rounds", expect_warmup_rounds),
        ("mr_rounds", expect_mr_rounds),
        ("server_batch_size", expect_server_batch_size),
    ]:
        if expected is not None and metadata.get(key) != expected:
            failures.append(
                f"metadata {key} mismatch: expected {expected}, got {metadata.get(key)!r}"
            )
    return failures


def validate_required_rows(
    row_by_key: dict[tuple[str, str, str], BigIntRow],
    require_bpsw_profile: bool,
    require_fuzzy_any: bool,
) -> list[str]:
    failures = []
    prime_engines = set(PRIME_TEST_ENGINES)
    next_engines = set(NEXT_SEARCH_ENGINES)
    if not require_bpsw_profile:
        prime_engines.discard("circle_big_bpsw_test_server")
        next_engines.discard("circle_big_bpsw_next_server")

    for case in PRIME_CASES:
        for engine in prime_engines:
            if ("prime_test", case, engine) not in row_by_key:
                failures.append(f"missing prime_test row: case={case}, engine={engine}")
    for case in NEXT_CASES:
        for engine in next_engines:
            if ("next_search", case, engine) not in row_by_key:
                failures.append(f"missing next_search row: case={case}, engine={engine}")
        if require_fuzzy_any:
            for engine in FUZZY_ANY_ENGINES:
                if ("fuzzy_any_search", case, engine) not in row_by_key:
                    failures.append(
                        f"missing fuzzy_any_search row: case={case}, engine={engine}"
                    )
    return failures


def validate_row_agreement_and_timings(rows: list[BigIntRow]) -> list[str]:
    failures = []
    for row in rows:
        if not row.agreed:
            failures.append(
                f"{row.operation} {row.case} {row.engine} disagreed: "
                f"result={row.result}, expected={row.expected}"
            )
        if row.rounds <= 0:
            failures.append(f"{row.operation} {row.case} {row.engine} has no samples")
        if row.median_ms <= 0.0 or row.min_ms <= 0.0 or row.max_ms <= 0.0:
            failures.append(f"{row.operation} {row.case} {row.engine} has nonpositive timing")
        if row.min_ms > row.median_ms or row.median_ms > row.max_ms:
            failures.append(
                f"{row.operation} {row.case} {row.engine} timing order is invalid"
            )
    return failures


def validate_speed_floor(
    row_by_key: dict[tuple[str, str, str], BigIntRow],
    *,
    operation: str,
    cases: set[str],
    candidate_engine: str,
    baseline_engine: str,
    minimum: float,
) -> list[str]:
    failures = []
    if minimum <= 0.0:
        return failures
    for case in sorted(cases):
        candidate = row_by_key.get((operation, case, candidate_engine))
        baseline = row_by_key.get((operation, case, baseline_engine))
        if candidate is None or baseline is None:
            continue
        speedup = baseline.median_ms / candidate.median_ms
        if speedup < minimum:
            failures.append(
                f"{operation} {case} {candidate_engine} median speedup over "
                f"{baseline_engine} is {speedup:.3f}, below required {minimum:.3f}"
            )
    return failures


def read_rows(path: Path) -> list[BigIntRow]:
    rows = []
    with path.open(newline="") as handle:
        for raw in csv.DictReader(handle):
            rows.append(
                BigIntRow(
                    operation=raw["operation"],
                    case=raw["case"],
                    bits=int(raw["bits"]),
                    engine=raw["engine"],
                    result=raw["result"],
                    expected=raw["expected"],
                    agreed=parse_bool(raw["agreed"]),
                    mr_rounds=int(raw["mr_rounds"]),
                    rounds=int(raw["rounds"]),
                    median_ms=float(raw["median_ms"]),
                    min_ms=float(raw["min_ms"]),
                    max_ms=float(raw["max_ms"]),
                )
            )
    return rows


def parse_bool(raw: str) -> bool:
    if raw == "True":
        return True
    if raw == "False":
        return False
    raise ValueError(f"expected True or False, got {raw!r}")


def parse_case_list(raw: str, *, allowed_cases: set[str], label: str) -> set[str]:
    cases = {item.strip() for item in raw.split(",") if item.strip()}
    unknown = cases - allowed_cases
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise SystemExit(f"{label} includes unknown case(s): {joined}")
    return cases


if __name__ == "__main__":
    raise SystemExit(main())
