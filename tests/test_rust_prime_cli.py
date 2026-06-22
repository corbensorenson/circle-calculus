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


@pytest.fixture(scope="session")
def circle_prime_count_bin() -> Path:
    cargo = cargo_or_skip()
    subprocess.run(
        [
            cargo,
            "build",
            "--quiet",
            "-p",
            "circle-prime",
            "--bin",
            "circle-prime-count",
        ],
        cwd=ROOT,
        check=True,
    )
    suffix = ".exe" if sys.platform == "win32" else ""
    binary = ROOT / "target" / "debug" / f"circle-prime-count{suffix}"
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


def assert_next_prime_proof_contract(payload: dict) -> None:
    contract = payload["next_proof_contract"]
    assert contract["name"] == "prime_horizon_next_search_spec"
    assert contract["lean_module"] == "Circle.Core.Horizon"
    assert contract["theorem_ids"] == ["CC-T0080", "CC-T0081"]
    assert "Circle.nextPrimeHorizonResultUpTo_some_iff" in contract["lean_names"]
    assert "Circle.nextPrimeHorizonResultUpTo_none_iff" in contract["lean_names"]
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
    assert_next_prime_proof_contract(payload)
    assert_prime_horizon_proof_contract(payload["decision"])


def test_rust_prime_cli_big_test_marks_large_prime_probable(
    circle_prime_bin: Path,
) -> None:
    mersenne_127 = str((1 << 127) - 1)
    payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "big-test",
            mersenne_127,
            "--rounds",
            "16",
            "--json",
        )
    )
    assert payload["n"] == mersenne_127
    assert payload["bit_length"] == 127
    assert payload["status"] == "probable_prime"
    assert payload["proof_contract"]["rust_domain"] == (
        "arbitrary_precision_biguint_probable_prime"
    )
    assert "certificate" in " ".join(payload["proof_contract"]["not_claimed"])


def test_rust_prime_cli_big_test_bpsw_profile_marks_large_prime_probable(
    circle_prime_bin: Path,
) -> None:
    mersenne_127 = str((1 << 127) - 1)
    payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "big-test",
            mersenne_127,
            "--profile",
            "bpsw",
            "--json",
        )
    )
    assert payload["status"] == "probable_prime"
    assert payload["method"] == "baillie_psw_biguint"
    assert payload["stage"] == "base2_miller_rabin_and_strong_lucas_selfridge_passed"


def test_rust_prime_cli_big_next_finds_probable_prime(
    circle_prime_bin: Path,
) -> None:
    start = str(1 << 128)
    payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "big-next",
            start,
            "--rounds",
            "16",
            "--max-candidates",
            "1024",
            "--json",
        )
    )
    assert payload["status"] == "found"
    assert int(payload["prime"]) >= int(start)
    assert payload["decision"]["status"] == "probable_prime"
    assert payload["exact_certified"] is False


def test_rust_prime_cli_big_next_bpsw_profile_matches_mr(
    circle_prime_bin: Path,
) -> None:
    start = str(1 << 128)
    mr = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "big-next",
            start,
            "--rounds",
            "16",
            "--max-candidates",
            "1024",
            "--json",
        )
    )
    bpsw = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "big-next",
            start,
            "--profile",
            "bpsw",
            "--max-candidates",
            "1024",
            "--json",
        )
    )
    assert bpsw["prime"] == mr["prime"]
    assert bpsw["decision"]["method"] == "baillie_psw_biguint"


def test_rust_prime_cli_big_fuzzy_search_uses_probable_verifier(
    circle_prime_bin: Path,
    tmp_path: Path,
) -> None:
    model = tmp_path / "big-model.txt"
    model.write_text(
        "\n".join(
            [
                "circle_fuzzy_model_v0",
                "bit_width 128",
                "residue_moduli 3,5,7",
                "weights " + ",".join(["0"] * 131),
                "bias 0",
                "",
            ]
        )
    )
    payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "big-fuzzy-search",
            str(model),
            str(1 << 127),
            "--candidate-window",
            "128",
            "--top-k",
            "8",
            "--score-limit",
            "32",
            "--rounds",
            "16",
            "--json",
        )
    )
    assert payload["reported_prime"] is not None
    assert payload["probable_prime_verified"] is True
    assert payload["deterministically_verified"] is False
    assert payload["hybrid_proof_contract"]["neural_role"] == "candidate_ordering_only"


def test_rust_prime_cli_big_servers_handle_repeated_requests(
    circle_prime_bin: Path,
    tmp_path: Path,
) -> None:
    mersenne_127 = str((1 << 127) - 1)
    completed = subprocess.run(
        [
            str(circle_prime_bin),
            "big-test-server",
            "--profile",
            "bpsw",
            "--rounds",
            "16",
        ],
        cwd=ROOT,
        input=f"{mersenne_127} 2\nquit\n",
        check=True,
        text=True,
        capture_output=True,
    )
    assert completed.stdout.splitlines() == ["probable_prime", "probable_prime"]

    completed = subprocess.run(
        [
            str(circle_prime_bin),
            "big-next-server",
            "--rounds",
            "16",
            "--max-candidates",
            "1024",
        ],
        cwd=ROOT,
        input=f"{1 << 128} 2\nquit\n",
        check=True,
        text=True,
        capture_output=True,
    )
    next_lines = completed.stdout.splitlines()
    assert len(next_lines) == 2
    assert next_lines[0] == next_lines[1]
    assert int(next_lines[0]) >= 1 << 128

    model = tmp_path / "big-model.txt"
    model.write_text(
        "\n".join(
            [
                "circle_fuzzy_model_v0",
                "bit_width 128",
                "residue_moduli 3,5,7",
                "weights " + ",".join(["0"] * 131),
                "bias 0",
                "",
            ]
        )
    )
    completed = subprocess.run(
        [
            str(circle_prime_bin),
            "big-fuzzy-server",
            str(model),
            "--candidate-window",
            "128",
            "--top-k",
            "8",
            "--score-limit",
            "32",
            "--rounds",
            "16",
        ],
        cwd=ROOT,
        input=f"{1 << 127} 2\nquit\n",
        check=True,
        text=True,
        capture_output=True,
    )
    fuzzy_lines = completed.stdout.splitlines()
    assert len(fuzzy_lines) == 2
    assert fuzzy_lines[0] == fuzzy_lines[1]
    assert int(fuzzy_lines[0]) >= 1 << 127


def test_rust_prime_cli_fuzzy_search_certifies_exact_next(
    circle_prime_bin: Path,
    tmp_path: Path,
) -> None:
    model = tmp_path / "tiny-model.txt"
    model.write_text(
        "\n".join(
            [
                "circle_fuzzy_model_v0",
                "bit_width 8",
                "residue_moduli none",
                "weights 0,0,0,0,0,0,0,0",
                "bias 0",
                "",
            ]
        )
    )

    payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "fuzzy-search",
            str(model),
            "100",
            "--mode",
            "exact-next",
            "--window",
            "32",
            "--top-k",
            "4",
            "--json",
        )
    )

    assert payload["search_kind"] == "rust_fuzzy_exact_next_prime_in_window"
    assert payload["reported_prime"] == 101
    assert payload["baseline_first_prime"] == 101
    assert payload["reported_prime_is_baseline_first_prime"] is True
    assert payload["exact_next_certified"] is True
    assert payload["hybrid_proof_contract"]["neural_role"] == "candidate_ordering_only"
    assert payload["hybrid_proof_contract"]["deterministic_prefilter"].startswith("2/3/5")
    assert_prime_horizon_proof_contract(payload)
    assert_next_prime_proof_contract(payload)


def test_rust_prime_cli_fuzzy_server_handles_repeated_exact_next(
    circle_prime_bin: Path,
    tmp_path: Path,
) -> None:
    model = tmp_path / "tiny-model.txt"
    model.write_text(
        "\n".join(
            [
                "circle_fuzzy_model_v0",
                "bit_width 8",
                "residue_moduli none",
                "weights 0,0,0,0,0,0,0,0",
                "bias 0",
                "",
            ]
        )
    )

    completed = subprocess.run(
        [
            str(circle_prime_bin),
            "fuzzy-server",
            str(model),
            "--mode",
            "exact-next",
            "--window",
            "32",
            "--top-k",
            "4",
        ],
        cwd=ROOT,
        input="100 3\nquit\n",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.splitlines() == ["101", "101", "101"]


def test_rust_prime_cli_fuzzy_server_handles_shifted_exact_next(
    circle_prime_bin: Path,
    tmp_path: Path,
) -> None:
    model = tmp_path / "tiny-model.txt"
    model.write_text(
        "\n".join(
            [
                "circle_fuzzy_model_v0",
                "bit_width 8",
                "residue_moduli none",
                "weights 0,0,0,0,0,0,0,0",
                "bias 0",
                "",
            ]
        )
    )

    completed = subprocess.run(
        [
            str(circle_prime_bin),
            "fuzzy-server",
            str(model),
            "--mode",
            "exact-next",
            "--window",
            "32",
            "--top-k",
            "4",
        ],
        cwd=ROOT,
        input="shifted 3 10 90\nquit\n",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.splitlines() == ["97", "101", "113"]


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


def test_rust_prime_cli_next_server_handles_shifted_batch_requests(
    circle_prime_bin: Path,
) -> None:
    completed = subprocess.run(
        [str(circle_prime_bin), "next-server"],
        cwd=ROOT,
        input="shifted 3 10 90\n",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.splitlines() == ["97", "101", "113"]


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
    assert_next_prime_proof_contract(payload)
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
    assert_next_prime_proof_contract(payload)


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
    assert payload["segment_size"] == DEFAULTS["parallel_edge_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_edge_high_offset_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_edge_high_offset_segment_size"],
        8,
        DEFAULTS["parallel_edge_high_offset_count_mode"],
    )
    assert payload["requested_threads"] == 8


def test_rust_prime_count_binary_matches_high_offset_default(
    circle_prime_bin: Path,
    circle_prime_count_bin: Path,
) -> None:
    full_payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "range",
            "1000000000000",
            "1000010000000",
            "--count",
            "--json",
            "--threads",
            "8",
        )
    )
    count_payload = json.loads(
        run_circle_prime(
            circle_prime_count_bin,
            "1000000000000",
            "1000010000000",
            "--json",
            "--threads",
            "8",
        )
    )
    assert count_payload["count"] == full_payload["count"] == 361726
    assert count_payload["segment_size"] == full_payload["segment_size"]
    assert count_payload["threads"] == full_payload["threads"]
    assert count_payload["requested_threads"] == full_payload["requested_threads"]
    assert count_payload["count_mode"] == full_payload["count_mode"]
    assert_prime_range_count_proof_contract(count_payload)


def test_rust_prime_count_binary_diagnostic_modes(circle_prime_count_bin: Path) -> None:
    assert run_circle_prime(circle_prime_count_bin, "--diagnostic-noop").strip() == "0"
    assert (
        run_circle_prime(
            circle_prime_count_bin,
            "--diagnostic-plan",
            "1000000000000",
            "1000010000000",
            "--segment-size",
            str(DEFAULTS["parallel_edge_high_offset_segment_size"]),
            "--threads",
            "8",
        ).strip()
        == "7"
    )
    assert (
        run_circle_prime(
            circle_prime_count_bin,
            "--diagnostic-spawn",
            "1000000000000",
            "1000010000000",
            "--segment-size",
            str(DEFAULTS["parallel_edge_high_offset_segment_size"]),
            "--threads",
            "8",
        ).strip()
        == "7"
    )


def test_rust_prime_count_binary_explicit_default_uses_adaptive_mode(
    circle_prime_count_bin: Path,
) -> None:
    omitted_payload = json.loads(
        run_circle_prime(
            circle_prime_count_bin,
            "1500000000000",
            "1500010000000",
            "--json",
            "--threads",
            "8",
        )
    )
    explicit_payload = json.loads(
        run_circle_prime(
            circle_prime_count_bin,
            "1500000000000",
            "1500010000000",
            "--json",
            "--threads",
            "8",
            "--count-mode",
            "default",
        )
    )
    assert omitted_payload["count"] == explicit_payload["count"]
    assert omitted_payload["segment_size"] == explicit_payload["segment_size"]
    assert omitted_payload["threads"] == explicit_payload["threads"]
    assert omitted_payload["count_mode"] == DEFAULTS["parallel_lower_high_offset_count_mode"]
    assert explicit_payload["count_mode"] == omitted_payload["count_mode"]
    assert_prime_range_count_proof_contract(explicit_payload)


def test_rust_prime_count_binary_supports_explicit_segmented_mode(
    circle_prime_bin: Path,
    circle_prime_count_bin: Path,
) -> None:
    full_payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "range",
            "1000000000000",
            "1000010000000",
            "--count",
            "--json",
            "--segment-size",
            "1310720",
            "--threads",
            "8",
            "--count-mode",
            "segmented",
        )
    )
    count_payload = json.loads(
        run_circle_prime(
            circle_prime_count_bin,
            "1000000000000",
            "1000010000000",
            "--json",
            "--segment-size",
            "1310720",
            "--threads",
            "8",
            "--count-mode",
            "segmented",
        )
    )

    assert count_payload["count"] == full_payload["count"] == 361726
    assert count_payload["segment_size"] == 1310720
    assert count_payload["threads"] == full_payload["threads"] == 8
    assert count_payload["requested_threads"] == full_payload["requested_threads"] == 8
    assert count_payload["count_mode"] == full_payload["count_mode"] == "segmented"
    assert_prime_range_count_proof_contract(count_payload)


@pytest.mark.parametrize("count_mode", ["balanced", "dynamic"])
def test_rust_prime_count_binary_matches_full_cli_split_modes(
    circle_prime_bin: Path,
    circle_prime_count_bin: Path,
    count_mode: str,
) -> None:
    full_payload = json.loads(
        run_circle_prime(
            circle_prime_bin,
            "range",
            "0",
            "1000000",
            "--count",
            "--json",
            "--segment-size",
            "65536",
            "--threads",
            "4",
            "--count-mode",
            count_mode,
        )
    )
    count_payload = json.loads(
        run_circle_prime(
            circle_prime_count_bin,
            "0",
            "1000000",
            "--json",
            "--segment-size",
            "65536",
            "--threads",
            "4",
            "--count-mode",
            count_mode,
        )
    )

    assert count_payload["count"] == full_payload["count"] == 78498
    assert count_payload["segment_size"] == 65536
    assert count_payload["threads"] == full_payload["threads"]
    assert count_payload["requested_threads"] == full_payload["requested_threads"] == 4
    assert count_payload["count_mode"] == full_payload["count_mode"] == count_mode
    assert_prime_range_count_proof_contract(count_payload)


def test_rust_prime_count_binary_server_handles_repeated_requests(
    circle_prime_count_bin: Path,
) -> None:
    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input=(
            "1000000000000 1000010000000\n"
            "repeat 2 1000000000000 1000010000000 1310720 8 presieve13\n"
            "quit\n"
        ),
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.splitlines() == ["361726", "361726", "361726"]


def test_rust_prime_count_binary_server_handles_segmented_requests(
    circle_prime_count_bin: Path,
) -> None:
    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--json",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input=(
            "1000000000000 1000010000000 1310720 8 segmented\n"
            "quit\n"
        ),
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["count"] == 361726
    assert payload["segment_size"] == 1310720
    assert payload["threads"] == 8
    assert payload["requested_threads"] == 8
    assert payload["count_mode"] == "segmented"
    assert_prime_range_count_proof_contract(payload)


def test_rust_prime_count_binary_server_handles_shifted_requests(
    circle_prime_count_bin: Path,
) -> None:
    low = 1_000_000_000_000
    high = 1_000_010_000_000
    shift = 10_000_000
    repetitions = 3
    segment_size = DEFAULTS["parallel_edge_high_offset_segment_size"]
    count_mode = DEFAULTS["parallel_edge_high_offset_count_mode"]
    expected = [
        run_circle_prime(
            circle_prime_count_bin,
            str(low + shift * index),
            str(high + shift * index),
            "--segment-size",
            str(segment_size),
            "--threads",
            "8",
            "--count-mode",
            count_mode,
        ).strip()
        for index in range(repetitions)
    ]

    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input=(
            f"shifted {repetitions} {shift} {low} {high} "
            f"{segment_size} 8 {count_mode}\n"
            "quit\n"
        ),
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.splitlines() == expected


def test_rust_prime_count_binary_server_handles_shifted_presieve17_requests(
    circle_prime_count_bin: Path,
) -> None:
    low = 1_500_000_000_000
    high = 1_500_010_000_000
    shift = 10_000_000
    repetitions = 3
    segment_size = 1_310_720
    count_mode = "presieve17"
    expected = [
        run_circle_prime(
            circle_prime_count_bin,
            str(low + shift * index),
            str(high + shift * index),
            "--segment-size",
            str(segment_size),
            "--threads",
            "8",
            "--count-mode",
            count_mode,
        ).strip()
        for index in range(repetitions)
    ]

    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input=(
            f"shifted {repetitions} {shift} {low} {high} "
            f"{segment_size} 8 {count_mode}\n"
            "quit\n"
        ),
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.splitlines() == expected


def test_rust_prime_count_binary_server_shifted_presieve17_json_reports_contract(
    circle_prime_count_bin: Path,
) -> None:
    low = 1_500_000_000_000
    high = 1_500_010_000_000
    shift = 10_000_000
    repetitions = 2
    segment_size = 1_310_720
    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--json",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input=(
            f"shifted {repetitions} {shift} {low} {high} "
            f"{segment_size} 8 presieve17\n"
            "quit\n"
        ),
        text=True,
        capture_output=True,
        check=True,
    )
    payloads = [json.loads(line) for line in completed.stdout.splitlines()]

    assert len(payloads) == repetitions
    assert [payload["low"] for payload in payloads] == [
        low + shift * index for index in range(repetitions)
    ]
    for payload in payloads:
        assert payload["segment_size"] == segment_size
        assert payload["threads"] == 8
        assert payload["requested_threads"] == 8
        assert payload["count_mode"] == "presieve17"
        assert_prime_range_count_proof_contract(payload)


def test_rust_prime_count_binary_server_shifted_default_uses_edge_plan(
    circle_prime_count_bin: Path,
) -> None:
    low = 1_000_000_000_000
    high = 1_000_010_000_000
    shift = 10_000_000
    repetitions = 2
    expected_counts = [
        int(
            run_circle_prime(
                circle_prime_count_bin,
                str(low + shift * index),
                str(high + shift * index),
                "--threads",
                "8",
            ).strip()
        )
        for index in range(repetitions)
    ]
    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--json",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input=f"shifted {repetitions} {shift} {low} {high}\nquit\n",
        text=True,
        capture_output=True,
        check=True,
    )
    payloads = [json.loads(line) for line in completed.stdout.splitlines()]

    assert [payload["low"] for payload in payloads] == [
        low + shift * index for index in range(repetitions)
    ]
    assert [payload["count"] for payload in payloads] == expected_counts
    for payload in payloads:
        assert payload["segment_size"] == 1_310_720
        assert payload["threads"] == 8
        assert payload["requested_threads"] == 8
        assert payload["count_mode"] == "presieve13"
        assert_prime_range_count_proof_contract(payload)


def test_rust_prime_count_binary_server_shifted_default_uses_lower_high_plan(
    circle_prime_count_bin: Path,
) -> None:
    low = 1_500_000_000_000
    high = 1_500_010_000_000
    shift = 10_000_000
    repetitions = 2
    expected_counts = [
        int(
            run_circle_prime(
                circle_prime_count_bin,
                str(low + shift * index),
                str(high + shift * index),
                "--segment-size",
                "1835008",
                "--threads",
                "8",
                "--count-mode",
                "presieve13",
            ).strip()
        )
        for index in range(repetitions)
    ]
    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--json",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input=f"shifted {repetitions} {shift} {low} {high}\nquit\n",
        text=True,
        capture_output=True,
        check=True,
    )
    payloads = [json.loads(line) for line in completed.stdout.splitlines()]

    assert [payload["low"] for payload in payloads] == [
        low + shift * index for index in range(repetitions)
    ]
    assert [payload["count"] for payload in payloads] == expected_counts
    for payload in payloads:
        assert payload["segment_size"] == 1_835_008
        assert payload["threads"] == 6
        assert payload["requested_threads"] == 8
        assert payload["count_mode"] == "presieve13"
        assert_prime_range_count_proof_contract(payload)


def test_rust_prime_count_binary_server_json_reports_count_contract(
    circle_prime_count_bin: Path,
) -> None:
    completed = subprocess.run(
        [
            str(circle_prime_count_bin),
            "count-server",
            "--json",
            "--threads",
            "8",
        ],
        cwd=ROOT,
        input="1000000000000 1000010000000\nquit\n",
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["count"] == 361726
    assert payload["segment_size"] == DEFAULTS["parallel_edge_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_edge_high_offset_count_mode"]
    assert_prime_range_count_proof_contract(payload)


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
    assert payload["segment_size"] == DEFAULTS["parallel_edge_high_offset_segment_size"]
    assert payload["count_mode"] == DEFAULTS["parallel_edge_high_offset_count_mode"]
    assert payload["threads"] == effective_threads_for_mode(
        10_000_000,
        DEFAULTS["parallel_edge_high_offset_segment_size"],
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
