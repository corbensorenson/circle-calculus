from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from scripts.check_prime_bigint_controls import BigIntRow
from scripts.confirm_prime_bigint_raw_sympy import (
    RunSummary,
    bpsw_prime_speedups_by_case,
    build_summary,
    validate_raw_prime_rows,
)


def bigint_row(case: str, engine: str, median_ms: float) -> BigIntRow:
    return BigIntRow(
        operation="prime_test",
        case=case,
        bits=255,
        engine=engine,
        result="True",
        expected="True",
        agreed=True,
        mr_rounds=16,
        rounds=3,
        median_ms=median_ms,
        min_ms=median_ms * 0.9,
        max_ms=median_ms * 1.1,
    )


def test_bpsw_prime_speedups_by_case() -> None:
    rows = [
        bigint_row("curve25519_prime", "circle_big_bpsw_test_server", 0.5),
        bigint_row("curve25519_prime", "sympy_isprime", 0.625),
        bigint_row("secp256k1_prime", "circle_big_bpsw_test_server", 0.4),
        bigint_row("secp256k1_prime", "sympy_isprime", 0.5),
    ]

    speedups = bpsw_prime_speedups_by_case(
        rows,
        {"curve25519_prime", "secp256k1_prime"},
    )

    assert speedups == {
        "curve25519_prime": 1.25,
        "secp256k1_prime": 1.25,
    }


def test_build_summary_records_weakest_speedup_and_failures() -> None:
    args = Namespace(
        runs=2,
        bench_rounds=3,
        warmup_rounds=1,
        mr_rounds=16,
        server_batch_size=16,
        min_bpsw_prime_vs_sympy=1.0,
    )
    runs = [
        RunSummary(
            run=1,
            csv=Path("run1.csv"),
            metadata=Path("run1.json"),
            failures=[],
            speedups={"curve25519_prime": 1.2, "secp256k1_prime": 1.05},
        ),
        RunSummary(
            run=2,
            csv=Path("run2.csv"),
            metadata=Path("run2.json"),
            failures=["curve25519_prime fell below floor"],
            speedups={"curve25519_prime": 0.98, "secp256k1_prime": 1.1},
        ),
    ]

    summary = build_summary(
        args=args,
        cases={"curve25519_prime", "secp256k1_prime"},
        runs=runs,
    )

    assert summary["all_runs_passed"] is False
    assert summary["min_speedup_by_case"] == {
        "curve25519_prime": 0.98,
        "secp256k1_prime": 1.05,
    }
    assert summary["run_artifacts"][1]["failures"] == ["curve25519_prime fell below floor"]


def test_validate_raw_prime_rows_requires_agreement_and_speed_floor() -> None:
    rows = [
        bigint_row("curve25519_prime", "circle_big_bpsw_test_server", 0.8),
        bigint_row("curve25519_prime", "sympy_isprime", 0.72),
    ]

    failures = validate_raw_prime_rows(
        rows,
        cases={"curve25519_prime"},
        minimum=1.0,
    )

    assert failures == [
        "prime_test curve25519_prime circle_big_bpsw_test_server median speedup over "
        "sympy_isprime is 0.900, below required 1.000"
    ]
