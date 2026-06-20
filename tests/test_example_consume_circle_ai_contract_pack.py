from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications.circle_ai_contract_consumer import (
    FINGERPRINT_ALGORITHM,
    _json_fingerprint,
)
from circle_math.applications.circle_ai_contracts import build_contract_pack


def _refresh_fingerprints(pack: dict) -> None:
    for contract in pack["contracts"]:
        contract["content_fingerprint_algorithm"] = FINGERPRINT_ALGORITHM
        contract["content_fingerprint"] = _json_fingerprint(contract)
    pack["contract_fingerprint_index"] = {
        contract["kind"]: {
            "id": contract["id"],
            "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
            "content_fingerprint": contract["content_fingerprint"],
        }
        for contract in pack["contracts"]
    }
    pack["content_fingerprint_algorithm"] = FINGERPRINT_ALGORITHM
    pack["pack_content_fingerprint"] = _json_fingerprint(pack)


def _write_pack(tmp_path: Path) -> Path:
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    pack_path.write_text(json.dumps(build_contract_pack()))
    return pack_path


def _write_pack_with_payload(tmp_path: Path) -> tuple[Path, dict]:
    pack = build_contract_pack()
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    pack_path.write_text(json.dumps(pack))
    return pack_path, pack


def _write_unready_sparse_pack(tmp_path: Path) -> Path:
    pack = build_contract_pack()
    kind = "sparse_attention_coverage"
    recommendation_ids: list[str] = []
    for contract in pack["contracts"]:
        if contract["kind"] == kind:
            contract["contract_passed"] = False
            contract["consumer_check"]["ready_for_downstream_fixture_use"] = False
            recommendation_ids = [
                recommendation["id"]
                for recommendation in contract["planner_recommendations"]
            ]
            break
    pack["contract_readiness_index"][kind]["contract_passed"] = False
    pack["contract_readiness_index"][kind][
        "ready_for_downstream_fixture_use"
    ] = False
    for recommendation_id in recommendation_ids:
        pack["planner_recommendation_index"][recommendation_id][
            "ready_for_downstream_fixture_use"
        ] = False
    _refresh_fingerprints(pack)
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    pack_path.write_text(json.dumps(pack))
    return pack_path


def test_example_consumer_emits_selected_rope_digest(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "rope_position_distinguishability",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
            "--field",
            "d19_undecided_request_status",
            "--field",
            "d19_proved_first_channel_bank_transfer",
            "--field",
            "d19_proved_first_channel_bank_shape",
            "--field",
            "d19_proved_first_channel_pair_scope",
            "--field",
            "d19_proved_first_channel_context_wide_contract",
            "--field",
            "d19_proved_first_channel_radian_bank_form",
            "--field",
            "d19_proved_first_channel_bank_tolerance_rule",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["ready_for_downstream_fixture_use"] is True
    assert payload["evidence_fields"] == {
        "d19_impossible_request_status": "impossible",
        "d19_proved_request_status": "proved",
        "d19_undecided_request_status": "undecided_margin_gap",
        "d19_proved_first_channel_bank_transfer": True,
        "d19_proved_first_channel_bank_shape": "standard_channel0_first",
        "d19_proved_first_channel_pair_scope": (
            "all ordered unequal pairs left < right < requested_context"
        ),
        "d19_proved_first_channel_context_wide_contract": True,
        "d19_proved_first_channel_radian_bank_form": True,
        "d19_proved_first_channel_bank_tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
    }
    assert "AIRA-T0214" in payload["theorem_ids"]
    assert "AIRA-T0231" in payload["theorem_ids"]
    assert "AIRA-T0234" in payload["theorem_ids"]
    assert "AIRA-T0235" in payload["theorem_ids"]
    assert "AIRA-T0236" in payload["theorem_ids"]
    assert "model quality" in payload["not_claimed"]


def test_example_consumer_emits_ready_readiness_summary(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "kv_cache_ring_buffer",
            "--readiness",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "kv_cache_ring_buffer"
    assert payload["ready_for_downstream_fixture_use"] is True
    assert payload["failure_reasons"] == []
    assert payload["planner_recommendation_count"] == 2


def test_example_consumer_readiness_summary_fails_for_unready_contract(
    tmp_path: Path,
) -> None:
    pack_path = _write_unready_sparse_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--readiness",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["kind"] == "sparse_attention_coverage"
    assert payload["ready_for_downstream_fixture_use"] is False
    assert payload["failure_reasons"] == ["contract_passed is false"]


def test_example_consumer_emits_all_readiness_report(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--all-readiness",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["readiness_schema"] == "circle_calculus.ai_contract_readiness.v0"
    assert payload["all_ready"] is True
    assert payload["contract_count"] == 9
    assert payload["ready_contract_count"] == 9
    assert "rope_position_distinguishability" in payload["selected_kinds"]
    assert all(
        summary["ready_for_downstream_fixture_use"] is True
        for summary in payload["summaries"]
    )


def test_example_consumer_all_readiness_fails_for_unready_contract(
    tmp_path: Path,
) -> None:
    pack_path = _write_unready_sparse_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--all-readiness",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    sparse = [
        summary
        for summary in payload["summaries"]
        if summary["kind"] == "sparse_attention_coverage"
    ][0]
    assert result.returncode == 2
    assert payload["all_ready"] is False
    assert payload["ready_contract_count"] == 8
    assert sparse["failure_reasons"] == ["contract_passed is false"]


def test_example_consumer_accepts_matching_fingerprint_expectations(
    tmp_path: Path,
) -> None:
    pack_path, pack = _write_pack_with_payload(tmp_path)
    sparse_fingerprint = pack["contract_fingerprint_index"][
        "sparse_attention_coverage"
    ]["content_fingerprint"]

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--field",
            "first_uncovered_lag",
            "--expect-pack-fingerprint",
            pack["pack_content_fingerprint"],
            "--expect-contract-fingerprint",
            f"sparse_attention_coverage={sparse_fingerprint}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "sparse_attention_coverage"
    assert payload["evidence_fields"] == {"first_uncovered_lag": 5}


def test_example_consumer_emits_strict_acceptance_receipt(
    tmp_path: Path,
) -> None:
    pack_path, pack = _write_pack_with_payload(tmp_path)
    sparse_fingerprint = pack["contract_fingerprint_index"][
        "sparse_attention_coverage"
    ]["content_fingerprint"]

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--field",
            "first_uncovered_lag",
            "--require-theorem",
            "AIT-T0104",
            "--require-recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop",
            "--require-recommendation-theorem",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104",
            "--require-recommendation-action-parameter",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
            "--require-recommendation-action-parameter-path",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
            "--include-field-metadata",
            "--expect-pack-fingerprint",
            pack["pack_content_fingerprint"],
            "--expect-contract-fingerprint",
            f"sparse_attention_coverage={sparse_fingerprint}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["receipt_schema"] == (
        "circle_calculus.ai_contract_acceptance_receipt.v0"
    )
    assert payload["accepted"] is True
    assert payload["kind"] == "sparse_attention_coverage"
    assert payload["pack_content_fingerprint"] == pack["pack_content_fingerprint"]
    assert payload["contract_content_fingerprint"] == sparse_fingerprint
    assert payload["evidence_fields"] == {"first_uncovered_lag": 5}
    assert payload["required_theorem_ids"] == ["AIT-T0104"]
    assert payload["required_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ]
    assert payload["required_recommendation_evidence_fields"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
            "first_uncovered_interval_start",
            "first_uncovered_interval_stop",
        ]
    }
    assert payload["required_recommendation_theorem_ids"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["AIT-T0104"],
    }
    assert payload["required_recommendation_action_parameters"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
    }
    assert payload["required_recommendation_action_parameter_paths"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
    }
    assert payload["planner_recommendations"][0]["id"] == (
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    )
    assert payload["field_catalog"]["first_uncovered_lag"]["value_kind"] == (
        "integer"
    )


def test_example_consumer_emits_rope_bank_transfer_receipt(
    tmp_path: Path,
) -> None:
    pack_path, pack = _write_pack_with_payload(tmp_path)
    rope_fingerprint = pack["contract_fingerprint_index"][
        "rope_position_distinguishability"
    ]["content_fingerprint"]

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "rope_position_distinguishability",
            "--receipt",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
            "--field",
            "d19_undecided_request_status",
            "--field",
            "d19_proved_first_channel_bank_transfer",
            "--field",
            "d19_proved_first_channel_bank_shape",
            "--field",
            "d19_proved_first_channel_pair_scope",
            "--field",
            "d19_proved_first_channel_context_wide_contract",
            "--field",
            "d19_proved_first_channel_radian_bank_form",
            "--field",
            "d19_proved_first_channel_bank_tolerance_rule",
            "--require-theorem",
            "AIRA-T0171",
            "--require-theorem",
            "AIRA-T0172",
            "--require-theorem",
            "AIRA-T0234",
            "--require-theorem",
            "AIRA-T0235",
            "--require-theorem",
            "AIRA-T0236",
            "--require-theorem",
            "AIRA-T0237",
            "--require-recommendation",
            "ROPE-USE-D19-MARGIN-FRONTIER",
            "--require-recommendation-evidence-field",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_proved_first_channel_bank_transfer"
            ),
            "--require-recommendation-evidence-field",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_proved_first_channel_context_wide_contract"
            ),
            "--require-recommendation-evidence-field",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_proved_first_channel_radian_bank_form"
            ),
            "--require-recommendation-theorem",
            "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234",
            "--require-recommendation-theorem",
            "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235",
            "--require-recommendation-theorem",
            "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0236",
            "--require-recommendation-theorem",
            "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0237",
            "--require-recommendation-action-parameter",
            "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer",
            "--require-recommendation-action-parameter-path",
            "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.applies",
            "--require-recommendation-action-parameter-path",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "proved_branch_bank_transfer.context_wide_contract"
            ),
            "--require-recommendation-action-parameter-path",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "proved_branch_bank_transfer.radian_bank_form"
            ),
            "--require-recommendation-action-parameter-path",
            "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.theorem_ids",
            "--expect-pack-fingerprint",
            pack["pack_content_fingerprint"],
            "--expect-contract-fingerprint",
            f"rope_position_distinguishability={rope_fingerprint}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["pack_content_fingerprint"] == pack["pack_content_fingerprint"]
    assert payload["contract_content_fingerprint"] == rope_fingerprint
    assert payload["required_theorem_ids"] == [
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
    ]
    assert payload["evidence_fields"]["d19_proved_first_channel_bank_transfer"] is True
    assert (
        payload["evidence_fields"]["d19_proved_first_channel_context_wide_contract"]
        is True
    )
    assert (
        payload["evidence_fields"]["d19_proved_first_channel_radian_bank_form"]
        is True
    )
    assert payload["required_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ]
    assert payload["required_recommendation_theorem_ids"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "AIRA-T0234",
            "AIRA-T0235",
            "AIRA-T0236",
            "AIRA-T0237",
        ],
    }
    assert payload["required_recommendation_action_parameters"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": ["proved_branch_bank_transfer"],
    }
    assert payload["required_recommendation_action_parameter_paths"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "proved_branch_bank_transfer.applies",
            "proved_branch_bank_transfer.context_wide_contract",
            "proved_branch_bank_transfer.radian_bank_form",
            "proved_branch_bank_transfer.theorem_ids",
        ],
    }
    assert (
        payload["planner_recommendations"][0]["proved_branch_bank_transfer"][
            "radian_bank_form"
        ]
        is True
    )
    recommendation = payload["planner_recommendations"][0]
    assert recommendation["proved_branch_bank_transfer"]["theorem_ids"] == [
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
    ]


def test_example_consumer_receipt_rejects_missing_field(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--field",
            "not_a_field",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "missing requested evidence fields: not_a_field" in result.stderr


def test_example_consumer_receipt_rejects_missing_recommendation(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation",
            "NOT-A-REC",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "missing requested planner recommendations: NOT-A-REC" in result.stderr


def test_example_consumer_receipt_rejects_missing_theorem(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-theorem",
            "NOT-A-THEOREM",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "missing requested theorem ids: NOT-A-THEOREM" in result.stderr


def test_example_consumer_receipt_rejects_duplicate_requirement_pin(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-theorem",
            "AIT-T0104",
            "--require-theorem",
            "AIT-T0104",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "required_theorem_ids must not contain duplicate strings" in (
        result.stderr
    )


def test_example_consumer_receipt_rejects_missing_recommendation_evidence_field(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=not_recommendation_evidence",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "not_recommendation_evidence" in result.stderr


def test_example_consumer_receipt_rejects_missing_recommendation_theorem(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation-theorem",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=NOT-A-REC-THEOREM",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "missing required recommendation theorem ids" in result.stderr
    assert "NOT-A-REC-THEOREM" in result.stderr


def test_example_consumer_receipt_rejects_missing_recommendation_action_parameter(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation-action-parameter",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=not_an_action_parameter",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "missing required recommendation action parameters" in result.stderr
    assert "not_an_action_parameter" in result.stderr


def test_example_consumer_receipt_rejects_missing_recommendation_action_parameter_path(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "rope_position_distinguishability",
            "--receipt",
            "--require-recommendation-action-parameter-path",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "classifier_regions[region=not_a_region].theorem_ids"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance failed" in result.stderr
    assert "missing required recommendation action-parameter paths" in result.stderr
    assert "classifier_regions[region=not_a_region].theorem_ids" in result.stderr


def test_example_consumer_recommendation_evidence_field_requires_receipt(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "--require-recommendation-evidence-field requires --receipt" in (
        result.stderr
    )


def test_example_consumer_theorem_pins_require_receipt(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--require-theorem",
            "AIT-T0104",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "--require-theorem requires --receipt" in result.stderr

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-theorem",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "--require-recommendation-theorem requires --receipt" in result.stderr

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-action-parameter",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "--require-recommendation-action-parameter requires --receipt" in (
        result.stderr
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-action-parameter-path",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "--require-recommendation-action-parameter-path requires --receipt" in (
        result.stderr
    )


def test_example_consumer_rejects_mismatched_fingerprint_expectation(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--expect-pack-fingerprint",
            "0" * 64,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3
    assert "fingerprint expectation failed" in result.stderr
    assert "pack fingerprint mismatch" in result.stderr


def test_example_consumer_emits_fingerprint_summary(tmp_path: Path) -> None:
    pack_path, pack = _write_pack_with_payload(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--fingerprints",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert payload["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert payload["pack_content_fingerprint"] == pack["pack_content_fingerprint"]
    assert payload["contract_fingerprint_index"]["kv_cache_ring_buffer"] == (
        pack["contract_fingerprint_index"]["kv_cache_ring_buffer"]
    )


def test_example_consumer_fingerprint_summary_accepts_expectations(
    tmp_path: Path,
) -> None:
    pack_path, pack = _write_pack_with_payload(tmp_path)
    kv_fingerprint = pack["contract_fingerprint_index"]["kv_cache_ring_buffer"][
        "content_fingerprint"
    ]

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--fingerprints",
            "--expect-pack-fingerprint",
            pack["pack_content_fingerprint"],
            "--expect-contract-fingerprint",
            f"kv_cache_ring_buffer={kv_fingerprint}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["pack_content_fingerprint"] == pack["pack_content_fingerprint"]
    assert payload["contract_fingerprint_index"]["kv_cache_ring_buffer"][
        "content_fingerprint"
    ] == kv_fingerprint


def test_example_consumer_can_emit_field_metadata(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "strided_candidate_fanout",
            "--field",
            "effective_candidate_budget",
            "--include-field-metadata",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"effective_candidate_budget": 12}
    assert payload["field_catalog"]["effective_candidate_budget"]["value_kind"] == (
        "integer"
    )
    assert "Duplicate-collapsed" in payload["field_catalog"][
        "effective_candidate_budget"
    ]["description"]


def test_example_consumer_can_emit_sparse_recommendations(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--field",
            "first_uncovered_lag",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"first_uncovered_lag": 5}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
    ]
    assert payload["planner_recommendations"][0]["proposed_local_window"] == 6
    assert payload["planner_recommendations"][1]["proposed_local_window"] == 119
    assert payload["planner_recommendations"][1]["target_interval_start"] == 40


def test_example_consumer_can_emit_planner_action_plan(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
            "--planner-kind",
            "sparse_attention_coverage",
            "--planner-kind",
            "rope_position_distinguishability",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert payload["planner_schema"] == "circle_calculus.ai_contract_planner.v0"
    assert payload["planner_includes_values"] is False
    assert payload["selected_kinds"] == [
        "sparse_attention_coverage",
        "rope_position_distinguishability",
    ]
    assert payload["planner_recommendation_count"] == 6
    assert payload["ready_recommendation_count"] == 6
    assert [action["recommendation_id"] for action in payload["action_plan"]] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert payload["action_plan"][0]["action_kind"] == "increase_local_window"
    assert payload["action_plan"][0]["evidence_fields"] == [
        "first_uncovered_interval_start",
        "first_uncovered_interval_stop",
        "first_uncovered_interval_length",
        "local_window_needed_to_cover_first_uncovered_interval",
        "first_uncovered_interval_additional_local_slots",
        "first_uncovered_interval_repair_reaches_interval",
        "first_interval_repair_next_uncovered_lag",
        "first_interval_repair_still_has_gap",
        "first_interval_repair_covers_context",
    ]
    assert payload["action_plan"][0]["theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0171",
        "AIT-T0166",
        "AIT-T0167",
    ]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage"
        in payload["action_plan"][0]["validation_commands"]
    )
    assert payload["action_plan"][1]["coverage_scope"] == "largest_uncovered_interval"
    assert "efficient" in payload["action_plan"][2]["not_claimed"]
    assert payload["action_plan"][3]["action_kind"] == "increase_local_window_sequence"
    assert "AIRA-T0216" in payload["action_plan"][5]["theorem_ids"]
    assert "d19_context_range_min_exclusive" in payload["action_plan"][5][
        "evidence_fields"
    ]
    assert "d19_context_range_max_inclusive" in payload["action_plan"][5][
        "evidence_fields"
    ]
    assert "d19_undecided_margin_open_gap" in payload["action_plan"][5][
        "evidence_fields"
    ]
    assert "evidence_values" not in payload["action_plan"][0]


def test_example_consumer_filters_planner_action_plan_by_recommendation(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
            "--planner-kind",
            "sparse_attention_coverage",
            "--planner-recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "--planner-include-values",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["selected_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ]
    assert [action["recommendation_id"] for action in payload["action_plan"]] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ]
    assert payload["planner_recommendation_count"] == 1
    assert payload["action_plan"][0]["evidence_values"][
        "first_uncovered_interval_start"
    ] == 5


def test_example_consumer_emits_rope_classifier_regions_in_action_plan(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
            "--planner-kind",
            "rope_position_distinguishability",
            "--planner-recommendation",
            "ROPE-USE-D19-MARGIN-FRONTIER",
            "--planner-include-values",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["selected_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ]
    assert payload["planner_recommendation_count"] == 1
    action = payload["action_plan"][0]
    assert action["recommendation_id"] == "ROPE-USE-D19-MARGIN-FRONTIER"
    assert action["evidence_values"]["d19_request_context"] == 131072
    assert action["action_parameters"]["applicable_context_range"] == {
        "min_exclusive": 103993,
        "max_inclusive": 196608,
    }
    assert action["action_parameters"]["undecided_interval"] == {
        "lower_exclusive": "1/328459",
        "upper_exclusive": "1/328458",
        "width": "1/107884986222",
    }
    assert [
        region["request_status"]
        for region in action["action_parameters"]["classifier_regions"]
    ] == ["proved", "undecided_margin_gap", "impossible"]
    assert action["action_parameters"]["classifier_regions"][1][
        "theorem_backed_classification"
    ] is False
    assert action["action_parameters"]["classifier_regions"][1][
        "theorem_backed_region"
    ] is True


def test_example_consumer_rejects_missing_planner_recommendation(
    tmp_path: Path,
) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
            "--planner-kind",
            "sparse_attention_coverage",
            "--planner-recommendation",
            "ROPE-USE-D19-MARGIN-FRONTIER",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Circle AI contract pack consumer failed" in result.stderr
    assert "ROPE-USE-D19-MARGIN-FRONTIER" in result.stderr


def test_example_consumer_planner_recommendation_requires_planner() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--planner-recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "--planner-recommendation requires --planner" in result.stderr


def test_example_consumer_planner_can_include_evidence_values(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
            "--planner-kind",
            "sparse_attention_coverage",
            "--planner-include-values",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["planner_includes_values"] is True
    assert payload["planner_recommendation_count"] == 4

    first_interval = payload["action_plan"][0]
    assert first_interval["recommendation_id"] == (
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    )
    assert first_interval["evidence_values"] == {
        "first_uncovered_interval_start": 5,
        "first_uncovered_interval_stop": 6,
        "first_uncovered_interval_length": 2,
        "local_window_needed_to_cover_first_uncovered_interval": 6,
        "first_uncovered_interval_additional_local_slots": 2,
        "first_uncovered_interval_repair_reaches_interval": True,
        "first_interval_repair_next_uncovered_lag": 8,
        "first_interval_repair_still_has_gap": True,
        "first_interval_repair_covers_context": False,
    }
    assert first_interval["missing_evidence_fields"] == []
    assert first_interval["action_parameters"] == {
        "proposed_local_window": 6,
        "additional_local_slots": 2,
        "target_interval_start": 5,
        "target_interval_stop": 6,
        "target_interval_length": 2,
        "next_uncovered_lag_after_repair": 8,
        "still_has_gap_after_repair": True,
    }

    largest_gap = payload["action_plan"][1]
    assert largest_gap["recommendation_id"] == "SPARSE-REPAIR-LARGEST-GAP-INTERVAL"
    assert largest_gap["evidence_values"] == {
        "largest_uncovered_interval_start": 40,
        "largest_uncovered_interval_stop": 119,
        "largest_uncovered_interval_length": 80,
        "local_window_needed_to_cover_largest_uncovered_interval": 119,
        "largest_uncovered_interval_additional_local_slots": 115,
        "largest_uncovered_interval_repair_reaches_interval": True,
        "largest_interval_repair_next_uncovered_lag": None,
        "largest_interval_repair_still_has_gap": False,
        "largest_interval_repair_covers_context": True,
        "largest_uncovered_interval_is_tail": True,
        "uncovered_lag_intervals": [
            {"start": 5, "stop": 6},
            {"start": 8, "stop": 12},
            {"start": 15, "stop": 20},
            {"start": 22, "stop": 25},
            {"start": 27, "stop": 38},
            {"start": 40, "stop": 119},
        ],
    }
    assert largest_gap["action_parameters"] == {
        "proposed_local_window": 119,
        "additional_local_slots": 115,
        "target_interval_start": 40,
        "target_interval_stop": 119,
        "target_interval_length": 80,
        "next_uncovered_lag_after_repair": None,
        "still_has_gap_after_repair": False,
        "covers_context_after_repair": True,
        "largest_interval_is_tail": True,
    }

    complete_fallback = payload["action_plan"][2]
    assert complete_fallback["recommendation_id"] == (
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK"
    )
    assert complete_fallback["evidence_values"] == {
        "complete_repair_window": 119,
        "complete_repair_window_additional_local_slots": 115,
        "complete_repair_window_covers_context": True,
        "complete_repair_window_uses_dense_threshold": True,
        "local_window_complete_threshold_is_exact_local_minimum": True,
        "complete_repair_window_minimal_for_declared_stride_family": True,
        "complete_repair_window_minimal_witness_lag": 119,
    }
    assert complete_fallback["action_parameters"] == {
        "proposed_local_window": 119,
        "additional_local_slots": 115,
    }

    interval_path = payload["action_plan"][3]
    assert interval_path["recommendation_id"] == "SPARSE-INTERVAL-REPAIR-PATH"
    assert interval_path["evidence_values"]["interval_repair_plan_step_count"] == 6
    assert interval_path["evidence_values"]["interval_repair_plan_final_window"] == 119
    assert interval_path["evidence_values"]["interval_repair_plan_covers_context"] is True
    assert interval_path["evidence_values"]["interval_repair_plan_strictly_progresses"] is True
    assert interval_path["action_parameters"] == {
        "covers_context_after_final_step": True,
        "final_local_window": 119,
        "step_count": 6,
        "strictly_progresses": True,
    }


def test_example_consumer_planner_defaults_to_all_kinds(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["planner_recommendation_count"] == 20
    assert payload["ready_recommendation_count"] == 20
    assert "kv_cache_ring_buffer" in payload["selected_kinds"]
    assert "seed_rule_exact_regeneration" in payload["selected_kinds"]


def test_example_consumer_lists_contract_kinds(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--list-kinds",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert "rope_position_distinguishability" in payload["kinds"]
    assert "kv_cache_ring_buffer" in payload["kinds"]
    assert "seed_rule_exact_regeneration" in payload["kinds"]
