from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications import (
    build_validated_contract_receipt_from_request,
    validate_contract_receipt,
    validate_contract_request,
)
from circle_math.applications.circle_ai_contracts import build_contract_pack


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples" / "circle_ai_requests"


def _example_requests() -> list[Path]:
    return sorted(EXAMPLE_DIR.glob("*_request.json"))


def test_circle_ai_request_examples_are_public_api_ready() -> None:
    pack = build_contract_pack()
    paths = _example_requests()

    assert {path.name for path in paths} == {
        "cyclic_memory_request.json",
        "cyclic_mixer_request.json",
        "kv_cache_request.json",
        "multicoil_phase_request.json",
        "recurrence_request.json",
        "rope_request.json",
        "seed_rule_request.json",
        "sparse_attention_request.json",
        "strided_fanout_request.json",
    }

    for path in paths:
        request = json.loads(path.read_text(encoding="utf-8"))
        assert validate_contract_request(request) == []
        receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        assert validate_contract_receipt(receipt) == []
        assert receipt["request_schema_id"] == request["schema_id"]
        assert receipt["proof_status"]["all_theorem_ids_proved"] is True
        assert receipt["not_claimed"]


def test_circle_ai_request_example_runs_through_cli() -> None:
    request_path = EXAMPLE_DIR / "sparse_attention_request.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_certify.py",
            "request",
            "--request-json",
            str(request_path),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    receipt = json.loads(result.stdout)
    assert receipt["kind"] == "sparse_attention_coverage"
    assert receipt["request_passed"] is True
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
