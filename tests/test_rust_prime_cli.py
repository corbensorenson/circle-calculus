from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = json.loads(
    (ROOT / "rust" / "circle-prime" / "prime_engine_defaults.json").read_text()
)
MR64_BASES = [2, 325, 9_375, 28_178, 450_775, 9_780_504, 1_795_265_022]


def cargo_or_skip() -> str:
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is not available")
    return cargo


@pytest.fixture(scope="session")
def circle_prime_bin() -> Path:
    cargo = cargo_or_skip()
    subprocess.run(
        [
            cargo,
            "build",
            "--quiet",
            "-p",
            "circle-prime",
            "--bin",
            "circle-prime",
        ],
        cwd=ROOT,
        check=True,
    )
    suffix = ".exe" if sys.platform == "win32" else ""
    binary = ROOT / "target" / "debug" / f"circle-prime{suffix}"
    if not binary.exists():
        raise AssertionError(f"expected built binary at {binary}")
    return binary


def run_circle_prime(binary: Path, *args: str) -> str:
    completed = subprocess.run(
        [str(binary), *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout


def run_circle_prime_error(binary: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def effective_threads(span: int, segment_size: int, requested_threads: int) -> int:
    segment_count = max(1, (span + segment_size - 1) // segment_size)
    return min(requested_threads, segment_count)


def effective_threads_for_mode(
    span: int,
    segment_size: int,
    requested_threads: int,
    count_mode: str,
) -> int:
    if count_mode == "prefix-pi":
        return 1
    return effective_threads(span, segment_size, requested_threads)


def is_prime_u64_reference(n: int) -> bool:
    if n < 2:
        return False
    for prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if n == prime:
            return True
        if n % prime == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for base in MR64_BASES:
        a = base % n
        if a == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(1, s):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def assert_prime_horizon_proof_contract(payload: dict) -> None:
    contract = payload["proof_contract"]
    assert contract["name"] == "prime_horizon_sqrt_containment"
    assert contract["lean_module"] == "Circle.Core.Horizon"
    assert contract["theorem_ids"] == [
        "CC-T0073",
        "CC-T0074",
        "CC-T0075",
        "CC-T0076",
        "CC-T0077",
    ]
    assert "Circle.primeHorizon_iff_no_sqrt_contained" in contract["lean_names"]
    assert contract["rust_domain"] == "u64_exact_arithmetic"


def assert_prime_range_count_proof_contract(payload: dict) -> None:
    contract = payload["count_proof_contract"]
    assert contract["name"] == "prime_horizon_range_count_spec"
    assert contract["lean_module"] == "Circle.Core.Horizon"
    assert contract["theorem_ids"] == ["CC-T0078", "CC-T0079"]
    assert "Circle.mem_primeHorizonsInRange_iff" in contract["lean_names"]
    assert "Circle.primeHorizonRangeCount_eq_filter_card" in contract["lean_names"]
    assert contract["rust_domain"] == "u64_exact_arithmetic"


def test_rust_prime_cli_classifies_known_values(circle_prime_bin: Path) -> None:
    prime = json.loads(run_circle_prime(circle_prime_bin, "test", "97", "--json"))
    assert prime["status"] == "prime"
    assert_prime_horizon_proof_contract(prime)
    composite = run_circle_prime(circle_prime_bin, "test", "561", "--json")
    assert '"status":"composite"' in composite


def test_rust_prime_cli_finds_next_prime(circle_prime_bin: Path) -> None:
    assert run_circle_prime(circle_prime_bin, "next", "100").strip() == "101"
    payload = json.loads(run_circle_prime(circle_prime_bin, "next", "100", "--json"))
    assert payload["status"] == "found"
    assert payload["prime"] == 101
    assert payload["candidate_count"] == 1
    assert payload["decision"]["status"] == "prime"
    assert_prime_horizon_proof_contract(payload)
    assert_prime_horizon_proof_contract(payload["decision"])


def test_rust_prime_cli_next_server_handles_repeated_requests(
    circle_prime_bin: Path,
) -> None:
    completed = subprocess.run(
        [str(circle_prime_bin), "next-server"],
        cwd=ROOT,
        input="90\n1000000\n",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.splitlines() == ["97", "1000003"]


def test_rust_prime_cli_next_server_json_reports_proof_contract(
    circle_prime_bin: Path,
) -> None:
    completed = subprocess.run(
        [str(circle_prime_bin), "next-server", "--json"],
        cwd=ROOT,
        input="100\n",
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "found"
    assert payload["prime"] == 101
    assert_prime_horizon_proof_contract(payload)
    assert_prime_horizon_proof_contract(payload["decision"])


def test_rust_prime_cli_reports_no_next_prime_in_u64_domain(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "next",
        "18446744073709551558",
        "--json",
    )
    payload = json.loads(output)
    assert payload["status"] == "not_found"
    assert payload["prime"] is None
    assert payload["decision"] is None
    assert_prime_horizon_proof_contract(payload)


def test_rust_prime_cli_counts_reference_range(circle_prime_bin: Path) -> None:
    assert run_circle_prime(circle_prime_bin, "range", "0", "1000", "--count").strip() == "168"


def test_rust_prime_cli_count_server_handles_repeated_requests(
    circle_prime_bin: Path,
) -> None:
    completed = subprocess.run(
        [
            str(circle_prime_bin),
            "count-server",
            "--segment-size",
            "65536",
            "--threads",
            "4",
            "--count-mode",
            "presieve13",
        ],
        cwd=ROOT,
        input="0 1000\n0 100000\n",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.splitlines() == ["168", "9592"]


def test_rust_prime_cli_count_server_json_reports_proof_contracts(
    circle_prime_bin: Path,
) -> None:
    completed = subprocess.run(
        [
            str(circle_prime_bin),
            "count-server",
            "--segment-size",
            "65536",
            "--threads",
            "4",
            "--count-mode",
            "presieve13",
            "--json",
        ],
        cwd=ROOT,
        input="0 1000\n",
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["count"] == 168
    assert payload["segment_size"] == 65536
    assert payload["threads"] == 1
    assert payload["requested_threads"] == 4
    assert payload["count_mode"] == "presieve13"
    assert_prime_horizon_proof_contract(payload)
    assert_prime_range_count_proof_contract(payload)


def test_rust_prime_cli_counts_reference_range_in_parallel(circle_prime_bin: Path) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "range",
        "0",
        "1000000",
        "--count",
        "--json",
        "--threads",
        "4",
    )
    payload = json.loads(output)
    assert payload["count"] == 78498
    assert_prime_range_count_proof_contract(payload)
    assert payload["threads"] == effective_threads_for_mode(
        1_000_000,
        DEFAULTS["parallel_tiny_prefix_segment_size"],
        4,
        DEFAULTS["parallel_tiny_prefix_count_mode"],
    )
    assert_prime_horizon_proof_contract(payload)


@pytest.mark.parametrize(
    "count_mode",
    [
        "balanced",
        "dynamic",
        "prefix-pi",
        "presieve13",
        "presieve17",
        "wheel30-mark",
        "hybrid-wheel30-mark",
    ],
)
def test_rust_prime_cli_count_modes_match_reference(
    circle_prime_bin: Path,
    count_mode: str,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "range",
        "0",
        "1000000",
        "--count",
        "--json",
        "--threads",
        "4",
        "--count-mode",
        count_mode,
    )
    payload = json.loads(output)
    assert payload["count"] == 78498
    assert payload["count_mode"] == count_mode
    assert_prime_range_count_proof_contract(payload)
    assert payload["threads"] == (1 if count_mode == "prefix-pi" else 4)


def test_rust_prime_cli_rejects_count_mode_without_count(circle_prime_bin: Path) -> None:
    completed = run_circle_prime_error(
        circle_prime_bin,
        "range",
        "0",
        "100",
        "--count-mode",
        "hybrid-wheel30-mark",
    )
    assert completed.returncode != 0
    assert "--count-mode is currently supported only with --count" in completed.stderr


def test_rust_prime_cli_uses_threaded_count_segment_default(circle_prime_bin: Path) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "range",
        "0",
        "10000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] == 664579
    assert payload["segment_size"] == DEFAULTS["parallel_small_prefix_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_small_prefix_count_mode"]
    assert_prime_range_count_proof_contract(payload)
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_small_prefix_segment_size"],
        8,
        DEFAULTS["parallel_small_prefix_count_mode"],
    )


def test_rust_prime_cli_uses_threaded_high_offset_segment_default(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "range",
        "1000000000000",
        "1000010000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] == 361726
    assert payload["segment_size"] == DEFAULTS["parallel_very_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_very_high_offset_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_very_high_offset_segment_size"],
        8,
        DEFAULTS["parallel_very_high_offset_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_count_defaults(circle_prime_bin: Path) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "0",
        "10000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == DEFAULTS["parallel_small_prefix_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_small_prefix_count_mode"]
    assert_prime_horizon_proof_contract(payload)
    assert_prime_range_count_proof_contract(payload)
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_small_prefix_segment_size"],
        8,
        DEFAULTS["parallel_small_prefix_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_tiny_threaded_prefix_default(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "0",
        "1000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == DEFAULTS["parallel_tiny_prefix_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_tiny_prefix_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        1_000_000,
        DEFAULTS["parallel_tiny_prefix_segment_size"],
        8,
        DEFAULTS["parallel_tiny_prefix_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_100m_threaded_prefix_default(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "0",
        "100000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == DEFAULTS["parallel_medium_prefix_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_medium_prefix_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        100_000_000,
        DEFAULTS["parallel_medium_prefix_segment_size"],
        8,
        DEFAULTS["parallel_medium_prefix_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_low_absolute_prefix_pi_range_default(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "1000000000",
        "2000000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == 262144
    assert payload["count_mode"] == "prefix-pi"
    assert payload["threads"] == 2
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_high_offset_count_defaults(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "1000000000000",
        "1000010000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == DEFAULTS["parallel_very_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_edge_high_offset_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_very_high_offset_segment_size"],
        8,
        DEFAULTS["parallel_edge_high_offset_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_mid_high_offset_count_defaults(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "1500000000000",
        "1500010000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == DEFAULTS["parallel_very_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_lower_high_offset_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_very_high_offset_segment_size"],
        8,
        DEFAULTS["parallel_lower_high_offset_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_middle_upper_high_offset_count_defaults(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "10000000000000",
        "10000010000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == DEFAULTS["parallel_very_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_very_high_offset_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_very_high_offset_segment_size"],
        8,
        DEFAULTS["parallel_very_high_offset_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_recommends_upper_high_offset_count_defaults(
    circle_prime_bin: Path,
) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "recommend",
        "100000000000000",
        "100000010000000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] is True
    assert payload["segment_size"] == DEFAULTS["parallel_upper_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_upper_high_offset_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_upper_high_offset_segment_size"],
        8,
        DEFAULTS["parallel_upper_high_offset_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_reports_effective_thread_cap(circle_prime_bin: Path) -> None:
    output = run_circle_prime(
        circle_prime_bin,
        "range",
        "0",
        "1000",
        "--count",
        "--json",
        "--threads",
        "8",
    )
    payload = json.loads(output)
    assert payload["count"] == 168
    assert payload["threads"] == 1
    assert payload["requested_threads"] == 8


def test_rust_prime_cli_counts_near_u64_ceiling(circle_prime_bin: Path) -> None:
    low = 2**64 - 101
    high = 2**64 - 1
    output = run_circle_prime(
        circle_prime_bin,
        "range",
        str(low),
        str(high),
        "--count",
        "--json",
        "--threads",
        "4",
    )
    payload = json.loads(output)
    expected = sum(1 for candidate in range(low, high) if is_prime_u64_reference(candidate))
    assert payload["count"] == expected
    assert payload["low"] == low
    assert payload["high"] == high
    assert payload["threads"] == 1
    assert payload["requested_threads"] == 4
    assert_prime_horizon_proof_contract(payload)


def test_rust_prime_cli_rejects_u64_overflow(circle_prime_bin: Path) -> None:
    completed = run_circle_prime_error(
        circle_prime_bin,
        "range",
        "0",
        str(2**64),
        "--count",
    )
    assert completed.returncode != 0
    assert "HIGH must fit in u64" in completed.stderr


def test_rust_prime_cli_inspects_horizon(circle_prime_bin: Path) -> None:
    output = run_circle_prime(circle_prime_bin, "inspect", "16", "--json")
    payload = json.loads(output)
    assert payload["unique_skip_count"] == 8
    assert payload["contained_primitive_horizons"] == [2, 4, 8]
    assert_prime_horizon_proof_contract(payload)
