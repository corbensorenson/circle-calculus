from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from scripts.check_prime_bigint_controls import BigIntRow
from scripts.confirm_prime_bigint_next_fuzzy import (
    RunSummary,
    build_summary,
    next_fuzzy_speedups_by_case,
    validate_next_fuzzy_rows,
)


def bigint_row(
    operation: str,
    case: str,
    engine: str,
    median_ms: float,
    *,
    agreed: bool = True,
) -> BigIntRow:
    return BigIntRow(
        operation=operation,
        case=case,
        bits=255,
        engine=engine,
        result="101",
        expected="101",
        agreed=agreed,
        mr_rounds=16,
        rounds=3,
        median_ms=median_ms,
        min_ms=median_ms * 0.9,
        max_ms=median_ms * 1.1,
    )


def complete_rows(*, weak_bpsw: bool = False, weak_fuzzy: bool = False) -> list[BigIntRow]:
    rows = []
    for case in ["next_at_2_127", "next_near_curve25519"]:
        rows.extend(
            [
                bigint_row(
                    "next_search",
                    case,
                    "circle_big_bpsw_next_server",
                    4.0 if weak_bpsw else 1.0,
                ),
                bigint_row("next_search", case, "sympy_nextprime", 3.0),
                bigint_row(
                    "fuzzy_any_search",
                    case,
                    "circle_big_fuzzy_any_server",
                    4.0 if weak_fuzzy else 2.0,
                ),
            ]
        )
    return rows


def test_next_fuzzy_speedups_by_case() -> None:
    speedups = next_fuzzy_speedups_by_case(complete_rows())

    assert speedups["bpsw_next_vs_sympy"] == {
        "next_at_2_127": 3.0,
        "next_near_curve25519": 3.0,
    }
    assert speedups["fuzzy_any_vs_sympy"] == {
        "next_at_2_127": 1.5,
        "next_near_curve25519": 1.5,
    }
    assert speedups["fuzzy_any_vs_bpsw_next"] == {
        "next_at_2_127": 0.5,
        "next_near_curve25519": 0.5,
    }


def test_validate_next_fuzzy_rows_enforces_configured_floors() -> None:
    failures = validate_next_fuzzy_rows(
        complete_rows(weak_bpsw=True, weak_fuzzy=True),
        min_bpsw_next_vs_sympy=1.1,
        min_fuzzy_any_vs_sympy=1.0,
        min_fuzzy_any_vs_bpsw_next=1.1,
    )

    assert any("bpsw_next_vs_sympy" in failure for failure in failures)
    assert any("fuzzy_any_vs_sympy" in failure for failure in failures)
    assert any("fuzzy_any_vs_bpsw_next" in failure for failure in failures)


def test_build_summary_records_weakest_speedups_by_group() -> None:
    args = Namespace(
        runs=2,
        bench_rounds=3,
        warmup_rounds=1,
        mr_rounds=16,
        max_candidates=4096,
        candidate_window=512,
        top_k=16,
        score_limit=128,
        server_batch_size=16,
        min_bpsw_next_vs_sympy=1.1,
        min_fuzzy_any_vs_sympy=0.0,
        min_fuzzy_any_vs_bpsw_next=0.0,
    )
    runs = [
        RunSummary(
            run=1,
            csv=Path("run1.csv"),
            metadata=Path("run1.json"),
            failures=[],
            speedups={
                "bpsw_next_vs_sympy": {
                    "next_at_2_127": 2.0,
                    "next_near_curve25519": 1.4,
                },
                "fuzzy_any_vs_sympy": {
                    "next_at_2_127": 0.8,
                    "next_near_curve25519": 1.2,
                },
                "fuzzy_any_vs_bpsw_next": {
                    "next_at_2_127": 0.4,
                    "next_near_curve25519": 0.9,
                },
            },
        ),
        RunSummary(
            run=2,
            csv=Path("run2.csv"),
            metadata=Path("run2.json"),
            failures=["fuzzy below target"],
            speedups={
                "bpsw_next_vs_sympy": {
                    "next_at_2_127": 1.8,
                    "next_near_curve25519": 1.5,
                },
                "fuzzy_any_vs_sympy": {
                    "next_at_2_127": 0.9,
                    "next_near_curve25519": 1.0,
                },
                "fuzzy_any_vs_bpsw_next": {
                    "next_at_2_127": 0.5,
                    "next_near_curve25519": 0.7,
                },
            },
        ),
    ]

    summary = build_summary(args=args, runs=runs)

    assert summary["all_runs_passed"] is False
    assert summary["min_speedup_by_group"]["bpsw_next_vs_sympy"] == {
        "next_at_2_127": 1.8,
        "next_near_curve25519": 1.4,
    }
    assert summary["min_speedup_by_group"]["fuzzy_any_vs_sympy"] == {
        "next_at_2_127": 0.8,
        "next_near_curve25519": 1.0,
    }
