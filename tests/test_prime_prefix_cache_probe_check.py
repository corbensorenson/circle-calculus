from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.check_prime_prefix_cache_probe import check_prefix_cache_probe, main


def test_prefix_cache_probe_check_passes_for_stable_2b_probe() -> None:
    result = check_prefix_cache_probe(
        metadata=metadata(),
        rows=rows(),
        low=1_000_000_000,
        high=2_000_000_000,
        expected_limit=2_000_000_000,
        required_baselines=(
            "external_primecount_pi_diff_server",
            "external_primesieve_count_server",
        ),
        min_median_speedup=50.0,
        max_estimated_bytes=200_000_000,
        max_startup_warmup_ms=8_000.0,
        require_stable=True,
    )

    assert result["ok"] is True
    assert result["failures"] == []
    assert result["startup_warmup_ms"] == 6620.003917


def test_prefix_cache_probe_check_rejects_noisy_rows() -> None:
    probe_rows = rows(stability="noisy")

    result = check_prefix_cache_probe(
        metadata=metadata(),
        rows=probe_rows,
        low=1_000_000_000,
        high=2_000_000_000,
        expected_limit=2_000_000_000,
        required_baselines=("external_primecount_pi_diff_server",),
        min_median_speedup=50.0,
        max_estimated_bytes=200_000_000,
        max_startup_warmup_ms=8_000.0,
        require_stable=True,
    )

    assert result["ok"] is False
    assert "not stable" in result["failures"][0]


def test_prefix_cache_probe_check_rejects_resource_overage() -> None:
    result = check_prefix_cache_probe(
        metadata=metadata(estimated_bytes=281_250_004, startup_warmup_ms=10_254.914),
        rows=rows(),
        low=1_000_000_000,
        high=2_000_000_000,
        expected_limit=2_000_000_000,
        required_baselines=("external_primecount_pi_diff_server",),
        min_median_speedup=50.0,
        max_estimated_bytes=200_000_000,
        max_startup_warmup_ms=8_000.0,
        require_stable=True,
    )

    assert result["ok"] is False
    assert any("estimated bytes" in failure for failure in result["failures"])
    assert any("startup warmup" in failure for failure in result["failures"])


def test_prefix_cache_probe_check_rejects_weak_speedup() -> None:
    result = check_prefix_cache_probe(
        metadata=metadata(),
        rows=rows(primecount_speedup=12.0),
        low=1_000_000_000,
        high=2_000_000_000,
        expected_limit=2_000_000_000,
        required_baselines=("external_primecount_pi_diff_server",),
        min_median_speedup=50.0,
        max_estimated_bytes=200_000_000,
        max_startup_warmup_ms=8_000.0,
        require_stable=True,
    )

    assert result["ok"] is False
    assert "below" in result["failures"][0]


def test_prefix_cache_probe_check_rejects_weak_cold_speedup() -> None:
    result = check_prefix_cache_probe(
        metadata=metadata(),
        rows=rows(cold_primecount_speedup=0.96),
        low=1_000_000_000,
        high=2_000_000_000,
        expected_limit=2_000_000_000,
        required_baselines=("external_primecount_pi_diff_server",),
        min_median_speedup=50.0,
        max_estimated_bytes=200_000_000,
        max_startup_warmup_ms=8_000.0,
        require_stable=True,
        required_cold_baselines=("external_primecount_pi_diff",),
        min_cold_median_speedup=1.0,
        require_cold_stable=True,
    )

    assert result["ok"] is False
    assert "cold external_primecount_pi_diff median speedup" in result["failures"][0]


def test_prefix_cache_probe_check_main_reports_success(
    tmp_path: Path,
    capsys,
) -> None:
    metadata_path = tmp_path / "metadata.json"
    csv_path = tmp_path / "probe.csv"
    metadata_path.write_text(json.dumps(metadata()))
    write_rows(csv_path, rows())

    status = main_with_args(
        "--metadata",
        str(metadata_path),
        "--csv",
        str(csv_path),
    )

    captured = capsys.readouterr()
    assert status == 0
    assert "prefix-cache promotion gate passed" in captured.out
    assert "external_primecount_pi_diff_server median=137.183x" in captured.out
    assert "cold external_primecount_pi_diff median=1.476x" in captured.out


def metadata(
    *,
    estimated_bytes: int = 187_500_004,
    startup_warmup_ms: float = 6620.003917,
) -> dict:
    return {
        "tools": {
            "circle_count_server": {
                "small_prefix_pi_cache_limit": 2_000_000_000,
                "small_prefix_pi_cache_estimated_bytes": estimated_bytes,
                "small_prefix_pi_cache_warmup_profiles": [
                    {
                        "cache_limit": 2_000_000_000,
                        "count_mode": "prefix-pi",
                        "estimated_bytes": estimated_bytes,
                        "high": 2_000_000_000,
                        "limit": 2_000_000_000,
                        "low": 1_000_000_000,
                        "name": "circle_prime_server_parallel_default_count_2t",
                        "startup_warmup_ms": startup_warmup_ms,
                    }
                ],
            }
        }
    }


def rows(
    *,
    stability: str = "stable",
    primecount_speedup: float = 137.183,
    primesieve_speedup: float = 4051.061,
    cold_primecount_speedup: float = 1.476,
    cold_primesieve_speedup: float = 3.099,
) -> list[dict[str, str]]:
    return [
        speedup_row(
            "external_primecount_pi_diff_server",
            primecount_speedup,
            stability,
            name="circle_prime_server_parallel_default_count_2t",
        ),
        speedup_row(
            "external_primesieve_count_server",
            primesieve_speedup,
            stability,
            name="circle_prime_server_parallel_default_count_2t",
        ),
        speedup_row(
            "external_primecount_pi_diff",
            cold_primecount_speedup,
            "stable",
            name="circle_prime_parallel_default_count_2t",
        ),
        speedup_row(
            "external_primesieve_count",
            cold_primesieve_speedup,
            "stable",
            name="circle_prime_parallel_default_count_2t",
        ),
    ]


def speedup_row(
    baseline: str,
    median_speedup: float,
    stability: str,
    *,
    name: str,
) -> dict[str, str]:
    return {
        "kind": "speedup",
        "name": name,
        "low": "1000000000",
        "high": "2000000000",
        "baseline": baseline,
        "best_speedup": f"{median_speedup + 1.0:.3f}",
        "median_speedup": f"{median_speedup:.3f}",
        "count_mode": "prefix-pi",
        "sample_stability": stability,
    }


def write_rows(path: Path, probe_rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(probe_rows[0]))
        writer.writeheader()
        writer.writerows(probe_rows)


def main_with_args(*args: str) -> int:
    import sys

    old_argv = sys.argv
    try:
        sys.argv = ["check_prime_prefix_cache_probe.py", *args]
        return main()
    finally:
        sys.argv = old_argv
