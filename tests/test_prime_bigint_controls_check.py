from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from scripts.check_prime_bigint_controls import (
    FUZZY_ANY_ENGINES,
    NEXT_CASES,
    NEXT_SEARCH_ENGINES,
    PRIME_CASES,
    PRIME_TEST_ENGINES,
    validate_artifact,
)


ROOT = Path(__file__).resolve().parents[1]


def write_bigint_artifacts(
    tmp_path: Path,
    *,
    omit_bpsw: bool = False,
    weak_bpsw_prime: bool = False,
    weak_bpsw_next: bool = False,
) -> tuple[Path, Path]:
    csv_path = tmp_path / "bigint.csv"
    metadata_path = tmp_path / "bigint.json"
    rows = []
    for case in sorted(PRIME_CASES):
        for engine in sorted(PRIME_TEST_ENGINES):
            if omit_bpsw and engine == "circle_big_bpsw_test_server":
                continue
            median = {
                "openssl_prime": 10.0,
                "sympy_isprime": 2.0,
                "circle_big_test": 4.0,
                "circle_big_test_server": 2.0,
                "circle_big_bpsw_test_server": 3.0 if weak_bpsw_prime else 1.0,
            }[engine]
            rows.append(row("prime_test", case, engine, median))
    for case in sorted(NEXT_CASES):
        for engine in sorted(NEXT_SEARCH_ENGINES):
            if omit_bpsw and engine == "circle_big_bpsw_next_server":
                continue
            median = {
                "sympy_nextprime": 3.0,
                "circle_big_next": 5.0,
                "circle_big_next_server": 2.0,
                "circle_big_bpsw_next_server": 4.0 if weak_bpsw_next else 1.0,
            }[engine]
            rows.append(row("next_search", case, engine, median))
        for engine in sorted(FUZZY_ANY_ENGINES):
            rows.append(row("fuzzy_any_search", case, engine, 2.5))

    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "operation",
                "case",
                "bits",
                "engine",
                "result",
                "expected",
                "agreed",
                "mr_rounds",
                "rounds",
                "median_ms",
                "min_ms",
                "max_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    metadata_path.write_text(
        json.dumps(
            {
                "schema": "circle_calculus.prime_bigint_controls.v0",
                "row_count": len(rows),
                "bench_rounds": 3,
                "warmup_rounds": 1,
                "mr_rounds": 16,
                "server_batch_size": 16,
                "circle_prime": {"exists": True},
                "big_fuzzy_model": {"exists": True},
                "tools": {
                    "openssl": "OpenSSL 3.6.3",
                    "sympy": "1.14.0",
                },
                "failures": [],
            }
        )
    )
    return csv_path, metadata_path


def row(operation: str, case: str, engine: str, median_ms: float) -> dict[str, object]:
    return {
        "operation": operation,
        "case": case,
        "bits": 127,
        "engine": engine,
        "result": "True",
        "expected": "True",
        "agreed": "True",
        "mr_rounds": 16,
        "rounds": 3,
        "median_ms": f"{median_ms:.6f}",
        "min_ms": f"{median_ms * 0.9:.6f}",
        "max_ms": f"{median_ms * 1.1:.6f}",
    }


def test_bigint_controls_checker_accepts_complete_artifact(tmp_path: Path) -> None:
    csv_path, metadata_path = write_bigint_artifacts(tmp_path)

    failures = validate_artifact(
        csv_path=csv_path,
        metadata_path=metadata_path,
        expect_bench_rounds=3,
        expect_warmup_rounds=1,
        expect_mr_rounds=16,
        expect_server_batch_size=16,
        min_hot_test_vs_openssl=1.5,
        min_bpsw_test_vs_openssl=1.5,
        min_bpsw_next_vs_sympy=1.1,
    )

    assert failures == []


def test_bigint_controls_checker_requires_bpsw_rows(tmp_path: Path) -> None:
    csv_path, metadata_path = write_bigint_artifacts(tmp_path, omit_bpsw=True)

    failures = validate_artifact(
        csv_path=csv_path,
        metadata_path=metadata_path,
        require_bpsw_profile=True,
    )

    assert any("circle_big_bpsw_test_server" in failure for failure in failures)
    assert any("circle_big_bpsw_next_server" in failure for failure in failures)


def test_bigint_controls_checker_cli_requires_bpsw_rows_by_default(
    tmp_path: Path,
) -> None:
    csv_path, metadata_path = write_bigint_artifacts(tmp_path, omit_bpsw=True)

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_prime_bigint_controls.py"),
            "--csv",
            str(csv_path),
            "--metadata",
            str(metadata_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "circle_big_bpsw_test_server" in completed.stderr
    assert "circle_big_bpsw_next_server" in completed.stderr


def test_bigint_controls_checker_enforces_bpsw_next_speed_floor(
    tmp_path: Path,
) -> None:
    csv_path, metadata_path = write_bigint_artifacts(tmp_path, weak_bpsw_next=True)

    failures = validate_artifact(
        csv_path=csv_path,
        metadata_path=metadata_path,
        min_bpsw_next_vs_sympy=1.1,
    )

    assert any("circle_big_bpsw_next_server" in failure for failure in failures)
    assert any("below required" in failure for failure in failures)


def test_bigint_controls_checker_enforces_bpsw_prime_sympy_promotion_floor(
    tmp_path: Path,
) -> None:
    csv_path, metadata_path = write_bigint_artifacts(tmp_path, weak_bpsw_prime=True)

    failures = validate_artifact(
        csv_path=csv_path,
        metadata_path=metadata_path,
        min_bpsw_prime_vs_sympy=1.0,
        bpsw_prime_vs_sympy_cases={"curve25519_prime", "secp256k1_prime"},
    )

    assert any("circle_big_bpsw_test_server" in failure for failure in failures)
    assert any("sympy_isprime" in failure for failure in failures)
    assert any("curve25519_prime" in failure for failure in failures)
