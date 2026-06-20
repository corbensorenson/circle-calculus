from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from circle_math.applications import (
    build_contract_receipt,
    build_kv_cache_receipt,
    build_recurrence_receipt,
    build_rope_receipt,
    build_sparse_attention_receipt,
    validate_contract_receipt,
)
from circle_math.applications.circle_ai_contracts import build_contract_pack


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "circle_ai_certify.py"


@pytest.fixture(scope="module")
def contract_pack() -> dict:
    return build_contract_pack()


def test_rope_receipt_classifies_d19_margin_request(contract_pack: dict) -> None:
    receipt = build_rope_receipt(
        head_dim=128,
        base=10000.0,
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    assert validate_contract_receipt(receipt) == []
    assert receipt["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
    assert receipt["kind"] == "rope_position_distinguishability"
    assert receipt["status"] == "proved"
    assert receipt["request_passed"] is True
    classifier = receipt["evidence"]["standard_channel0_d19_request_classifier"]
    assert classifier["request_status"] == "proved"
    assert classifier["theorem_backed_classification"] is True
    assert "AIRA-T0238" in receipt["proof_status"]["theorem_ids"]
    guardrail = receipt["evidence"]["real_phase_dirichlet_guardrail"]
    assert guardrail["applies"] is True
    assert guardrail["inv_context_margin"] == "1/131072"
    assert guardrail["requested_margin_relation_to_ceiling"] == (
        "below_dirichlet_ceiling"
    )
    assert guardrail["requested_margin_exceeds_ceiling"] is False
    assert "AIRA-T0240" in receipt["proof_status"]["theorem_ids"]
    assert "real_phase_dirichlet_guardrail" in receipt["proof_layers"][
        "proved_fields"
    ]
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
    assert "real_phase_numerical_worst_gap" in receipt["proof_layers"][
        "numerical_only_fields"
    ]
    assert any(
        "full all-channel" in field
        for field in receipt["proof_layers"]["unsupported_fields"]
    )
    assert len(receipt["receipt_content_fingerprint"]) == 64


def test_rope_receipt_distinguishes_impossible_and_undecided_margins(
    contract_pack: dict,
) -> None:
    impossible = build_rope_receipt(
        context=131072,
        requested_margin="1/328458",
        pack=contract_pack,
    )
    undecided = build_rope_receipt(
        context=131072,
        requested_margin="2/656917",
        pack=contract_pack,
    )

    assert impossible["status"] == "impossible"
    assert impossible["request_passed"] is False
    assert impossible["evidence"]["standard_channel0_d19_request_classifier"][
        "request_status"
    ] == "impossible"
    assert impossible["proof_status"]["all_theorem_ids_proved"] is True
    assert undecided["status"] == "undecided"
    assert undecided["request_passed"] is None
    assert undecided["evidence"]["standard_channel0_d19_request_classifier"][
        "request_status"
    ] == "undecided_margin_gap"
    assert validate_contract_receipt(undecided) == []

    above_ceiling = build_rope_receipt(
        context=1000,
        requested_margin="1/999",
        pack=contract_pack,
    )
    assert above_ceiling["status"] == "impossible"
    assert above_ceiling["request_passed"] is False
    guardrail = above_ceiling["evidence"]["real_phase_dirichlet_guardrail"]
    assert guardrail["requested_margin_relation_to_ceiling"] == (
        "above_dirichlet_ceiling"
    )
    assert guardrail["requested_margin_exceeds_ceiling"] is True
    assert "AIRA-T0240" in guardrail["theorem_ids"]
    assert above_ceiling["proof_status"]["all_theorem_ids_proved"] is True


def test_kv_sparse_and_recurrence_receipts_preserve_family_semantics(
    contract_pack: dict,
) -> None:
    stale_kv = build_kv_cache_receipt(
        cache_size=16,
        current=31,
        token=20,
        batch_tokens=(12, 20),
        request_id="stale_read",
        pack=contract_pack,
    )
    sparse = build_sparse_attention_receipt(
        context=120,
        strides=(7, 13),
        path_length=3,
        local_window=4,
        pack=contract_pack,
    )
    recurrence = build_recurrence_receipt(pack=contract_pack)

    assert stale_kv["status"] == "proved"
    assert stale_kv["request_passed"] is False
    adapter = stale_kv["evidence"]["adapter_request_trace_certificate"]
    assert adapter["first_stale_token"] == 12
    assert adapter["stale_member_blocks_pass"] is True
    assert stale_kv["proof_status"]["all_theorem_ids_proved"] is True

    assert sparse["status"] == "proved"
    assert sparse["request_passed"] is False
    assert sparse["evidence"]["coverage_complete"] is False
    assert sparse["evidence"]["first_uncovered_lag"] == 5
    assert sparse["proof_status"]["all_theorem_ids_proved"] is True

    assert recurrence["status"] == "proved"
    assert recurrence["request_passed"] is True
    fields = recurrence["evidence"]["fields"]
    assert fields["scheduled_work_saving"] > 0
    assert fields["periodic_shift_required_steps_invariant"] is True
    assert recurrence["proof_status"]["all_theorem_ids_proved"] is True


def test_dispatcher_aliases_and_fingerprint_validation(contract_pack: dict) -> None:
    receipt = build_contract_receipt(
        "sparse-attention",
        {
            "context": 9,
            "strides": (2, 5),
            "path_length": 4,
            "local_window": 8,
        },
        pack=contract_pack,
    )

    assert receipt["kind"] == "sparse_attention_coverage"
    assert receipt["request_passed"] is True
    assert validate_contract_receipt(receipt) == []

    broken = dict(receipt)
    broken["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(broken)
    assert any("drifted" in failure for failure in failures)


def test_circle_ai_certify_cli_emits_json_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--head-dim",
            "128",
            "--base",
            "10000",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
    assert payload["status"] == "proved"
    assert payload["request_passed"] is True
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    assert payload["evidence"]["standard_channel0_d19_request_classifier"][
        "request_status"
    ] == "proved"


def test_circle_ai_certify_cli_accepts_request_json(tmp_path: Path) -> None:
    request_path = tmp_path / "rope_request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "rope_position_distinguishability",
                "parameters": {
                    "head_dim": 128,
                    "base": 10000.0,
                    "context": 1000,
                    "requested_margin": "1/999",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "request",
            "--request-json",
            str(request_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["status"] == "impossible"
    assert payload["request_passed"] is False
    guardrail = payload["evidence"]["real_phase_dirichlet_guardrail"]
    assert guardrail["requested_margin_relation_to_ceiling"] == (
        "above_dirichlet_ceiling"
    )
