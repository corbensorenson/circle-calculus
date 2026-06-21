from __future__ import annotations

import json
import subprocess
import sys

from circle_math.core import finite_orbit, finite_period, is_full_coil
from circle_math.ai_contracts import CONTRACT_PACK_SCHEMA_ID, build_contract_pack
from circle_math.contracts import contract_kinds, readiness_summary


def test_stable_core_api_examples() -> None:
    assert finite_orbit(12, 5) == [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7]
    assert finite_period(12, 4) == 3
    assert is_full_coil(13, 5) is True
    assert is_full_coil(12, 4) is False


def test_stable_contract_api_pack_readiness() -> None:
    pack = build_contract_pack()
    assert pack["schema_id"] == CONTRACT_PACK_SCHEMA_ID
    kinds = contract_kinds(pack)
    assert "rope_position_distinguishability" in kinds
    assert "sparse_attention_coverage" in kinds
    sparse = readiness_summary(pack, "sparse_attention_coverage")
    assert sparse.ready_for_downstream_fixture_use is True
    assert sparse.all_theorem_ids_proved is True


def test_package_cli_contract_ready_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "circle_math.cli",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0


def test_package_console_script_target_functions() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from circle_math.cli import contract_ready_main, "
                "rope_certify_main, sparse_attention_certify_main; "
                "print(callable(contract_ready_main), callable(rope_certify_main), "
                "callable(sparse_attention_certify_main))"
            ),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == "True True True"
