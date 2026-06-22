from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

from circle_math.applications.circle_ai_contract_consumer import (
    FINGERPRINT_ALGORITHM,
    _json_fingerprint,
)
from circle_math.applications.circle_ai_contracts import (
    build_acceptance_policy_report_json_schema,
    build_acceptance_receipt_json_schema,
    build_contract_pack,
)


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


def _policy_for(pack: dict) -> dict:
    return {
        "schema_id": "circle_calculus.ai_contract_acceptance_policy.v0",
        "policy_id": "standalone_ci_test_policy",
        "policy_name": "Standalone CI test policy",
        "expected_pack_fingerprint": pack["pack_content_fingerprint"],
        "contracts": [
            {
                "kind": "rope_position_distinguishability",
                "expected_contract_fingerprint": pack[
                    "contract_fingerprint_index"
                ]["rope_position_distinguishability"]["content_fingerprint"],
                "required_fields": [
                    "d19_context_range_min_exclusive",
                    "d19_context_range_max_inclusive",
                    "d19_proved_request_status",
                    "d19_impossible_obstruction_gap",
                    "d19_impossible_obstruction_turns",
                    "d19_undecided_margin_open_gap",
                    "d19_undecided_margin_interval_width",
                    "d19_undecided_request_relation",
                ],
                "required_theorem_ids": [
                    "AIRA-T0216",
                ],
                "required_recommendation_ids": [
                    "ROPE-USE-D19-MARGIN-FRONTIER",
                ],
                "required_recommendation_evidence_fields": {
                    "ROPE-USE-D19-MARGIN-FRONTIER": [
                        "d19_context_range_min_exclusive",
                        "d19_context_range_max_inclusive",
                        "d19_impossible_obstruction_gap",
                        "d19_impossible_obstruction_turns",
                        "d19_undecided_margin_interval_width",
                        "d19_undecided_request_relation",
                    ],
                },
                "required_recommendation_theorem_ids": {
                    "ROPE-USE-D19-MARGIN-FRONTIER": [
                        "AIRA-T0216",
                    ],
                },
                "required_recommendation_action_parameters": {
                    "ROPE-USE-D19-MARGIN-FRONTIER": [
                        "applicable_context_range",
                        "classifier_regions",
                        "impossible_obstruction_gap",
                        "impossible_obstruction_turns",
                        "undecided_interval",
                    ],
                },
                "required_recommendation_action_parameter_paths": {
                    "ROPE-USE-D19-MARGIN-FRONTIER": [
                        "applicable_context_range.min_exclusive",
                        "impossible_obstruction_gap",
                        "impossible_obstruction_turns",
                        "classifier_regions[region=proved].theorem_ids",
                        "classifier_regions[region=undecided_margin_gap].condition",
                        "undecided_interval.width",
                    ],
                },
            },
            {
                "kind": "sparse_attention_coverage",
                "expected_contract_fingerprint": pack[
                    "contract_fingerprint_index"
                ]["sparse_attention_coverage"]["content_fingerprint"],
                "required_fields": [
                    "first_uncovered_lag",
                    "first_uncovered_interval_start",
                ],
                "required_theorem_ids": [
                    "AIT-T0104",
                ],
                "required_recommendation_ids": [
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
                ],
                "required_recommendation_evidence_fields": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
                        "first_uncovered_interval_start",
                    ],
                },
                "required_recommendation_theorem_ids": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
                        "AIT-T0104",
                    ],
                },
            },
        ],
    }


def _write_pack_and_policy(tmp_path: Path, pack: dict) -> tuple[Path, Path]:
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(_policy_for(pack)))
    return pack_path, policy_path


def test_standalone_downstream_ci_accepts_policy_and_emits_action_plan(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["example_schema_id"] == (
        "circle_calculus.downstream_ci_acceptance_example.v0"
    )
    assert payload["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert payload["acceptance_policy_report_schema"] == (
        "circle_calculus.ai_contract_acceptance_policy_report.v0"
    )
    assert payload["policy_schema"] == (
        "circle_calculus.ai_contract_acceptance_policy.v0"
    )
    assert payload["accepted"] is True
    assert payload["policy_id"] == "standalone_ci_test_policy"
    assert payload["contract_count"] == 2
    assert payload["receipt_count"] == 2
    assert payload["receipts"] == payload["accepted_contracts"]
    assert payload["planner_includes_values"] is False
    assert payload["planner_recommendation_count"] == 6
    assert payload["policy_summary"]["schema_id"] == (
        "circle_calculus.downstream_ci_policy_summary.v0"
    )
    assert payload["policy_summary"]["accepted_contract_kinds"] == [
        "rope_position_distinguishability",
        "sparse_attention_coverage",
    ]
    assert payload["policy_summary"]["accepted_contract_count"] == 2
    assert payload["policy_summary"]["required_recommendation_count"] == 2
    assert payload["policy_summary"]["required_recommendation_theorem_count"] == 2
    assert payload["policy_summary"]["contract_summaries"][0] == {
        "kind": "rope_position_distinguishability",
        "contract_id": "CC-AI-CONTRACT-ROPE-001",
        "required_field_count": 8,
        "required_theorem_count": 1,
        "required_recommendation_ids": [
            "ROPE-USE-D19-MARGIN-FRONTIER",
        ],
        "required_recommendation_count": 1,
        "required_recommendation_theorem_count": 1,
        "required_recommendation_action_parameter_count": 5,
        "required_recommendation_action_parameter_path_count": 6,
        "content_fingerprint": pack["contract_fingerprint_index"][
            "rope_position_distinguishability"
        ]["content_fingerprint"],
    }
    assert payload["planner_summary"]["schema_id"] == (
        "circle_calculus.downstream_ci_planner_summary.v0"
    )
    assert payload["planner_summary"]["selected_recommendation_count"] == 6
    assert payload["planner_summary"]["includes_values"] is False
    assert payload["planner_summary"]["selected_recommendations_by_kind"][
        "rope_position_distinguishability"
    ] == [
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert [contract["kind"] for contract in payload["accepted_contracts"]] == [
        "rope_position_distinguishability",
        "sparse_attention_coverage",
    ]
    assert payload["accepted_contracts"][0]["required_theorem_ids"] == [
        "AIRA-T0216",
    ]
    assert payload["accepted_contracts"][0][
        "required_recommendation_theorem_ids"
    ] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": ["AIRA-T0216"],
    }
    assert payload["accepted_contracts"][0][
        "required_recommendation_action_parameters"
    ] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "applicable_context_range",
            "classifier_regions",
            "impossible_obstruction_gap",
            "impossible_obstruction_turns",
            "undecided_interval",
        ],
    }
    assert payload["accepted_contracts"][0][
        "required_recommendation_action_parameter_paths"
    ] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "applicable_context_range.min_exclusive",
            "impossible_obstruction_gap",
            "impossible_obstruction_turns",
            "classifier_regions[region=proved].theorem_ids",
            "classifier_regions[region=undecided_margin_gap].condition",
            "undecided_interval.width",
        ],
    }
    assert payload["accepted_contracts"][0]["receipt_schema"] == (
        "circle_calculus.ai_contract_acceptance_receipt.v0"
    )
    assert payload["accepted_contracts"][0]["accepted"] is True
    assert payload["accepted_contracts"][0]["schema_id"] == (
        "circle_calculus.ai_contract_pack.v0"
    )
    assert payload["accepted_contracts"][0]["pack_content_fingerprint"] == (
        pack["pack_content_fingerprint"]
    )
    assert payload["accepted_contracts"][0]["evidence_fields"][
        "d19_context_range_min_exclusive"
    ] == 103993
    assert payload["accepted_contracts"][0]["evidence_fields"][
        "d19_undecided_margin_interval_width"
    ] == "1/107884986222"
    assert payload["accepted_contracts"][0]["evidence_fields"][
        "d19_impossible_obstruction_gap"
    ] == 103993
    assert payload["accepted_contracts"][0]["evidence_fields"][
        "d19_impossible_obstruction_turns"
    ] == 16551
    assert payload["accepted_contracts"][0]["evidence_fields"][
        "d19_undecided_request_relation"
    ] == "strictly_between_thresholds"
    assert payload["accepted_contracts"][0]["planner_recommendations"][0]["id"] == (
        "ROPE-USE-D19-MARGIN-FRONTIER"
    )
    assert payload["accepted_contracts"][0]["dictionary_ids"]
    assert payload["accepted_contracts"][0]["validation_commands"]
    assert payload["accepted_contracts"][0]["source_paper"] == (
        "papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md"
    )
    rope_frontier = [
        action
        for action in payload["action_plan"]
        if action["recommendation_id"] == "ROPE-USE-D19-MARGIN-FRONTIER"
    ][0]
    assert rope_frontier["ready_for_downstream_fixture_use"] is True
    assert rope_frontier["source_paper"] == (
        "papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md"
    )
    assert "python scripts/rope_certify.py" in rope_frontier[
        "validation_commands"
    ][0]
    assert "evidence_values" not in rope_frontier
    assert "missing_evidence_fields" not in rope_frontier
    assert "action_parameters" not in rope_frontier


def test_standalone_downstream_ci_report_matches_generated_schema(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    report_schema = build_acceptance_policy_report_json_schema()
    receipt_schema = build_acceptance_receipt_json_schema()
    jsonschema.Draft202012Validator.check_schema(report_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.validate(payload, report_schema)
    for receipt in payload["receipts"]:
        jsonschema.validate(receipt, receipt_schema)


def test_standalone_downstream_ci_can_include_planner_values(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
            "--include-values",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    rope_frontier = [
        action
        for action in payload["action_plan"]
        if action["recommendation_id"] == "ROPE-USE-D19-MARGIN-FRONTIER"
    ][0]
    assert payload["planner_includes_values"] is True
    assert rope_frontier["evidence_values"]["d19_context_range_min_exclusive"] == (
        103993
    )
    assert rope_frontier["evidence_values"]["d19_context_range_max_inclusive"] == (
        196608
    )
    assert rope_frontier["evidence_values"][
        "d19_undecided_margin_interval_width"
    ] == "1/107884986222"
    assert rope_frontier["evidence_values"]["d19_impossible_obstruction_gap"] == (
        103993
    )
    assert rope_frontier["evidence_values"][
        "d19_impossible_obstruction_turns"
    ] == 16551
    assert rope_frontier["evidence_values"]["d19_undecided_request_relation"] == (
        "strictly_between_thresholds"
    )
    assert rope_frontier["missing_evidence_fields"] == []
    assert rope_frontier["action_parameters"]["request_context"] == 131072
    assert rope_frontier["action_parameters"]["proved_margin"] == "1/328459"
    assert rope_frontier["action_parameters"]["impossible_obstruction_gap"] == 103993
    assert rope_frontier["action_parameters"]["impossible_obstruction_turns"] == 16551
    assert rope_frontier["action_parameters"]["undecided_interval"] == {
        "lower_exclusive": "1/328459",
        "upper_exclusive": "1/328458",
        "width": "1/107884986222",
    }
    assert rope_frontier["action_parameters"]["classifier_regions"][1]["region"] == (
        "undecided_margin_gap"
    )
    sparse_first_interval = [
        action
        for action in payload["action_plan"]
        if action["recommendation_id"] == "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ][0]
    assert sparse_first_interval["missing_evidence_fields"] == []
    assert sparse_first_interval["action_parameters"] == {
        "proposed_local_window": 6,
        "additional_local_slots": 2,
        "target_interval_start": 5,
        "target_interval_stop": 6,
        "target_interval_length": 2,
        "next_uncovered_lag_after_repair": 8,
        "still_has_gap_after_repair": True,
    }


def test_standalone_downstream_ci_can_select_one_planner_recommendation(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
            "--planner-recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "--include-values",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["planner_requested_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
    ]
    assert payload["planner_selected_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
    ]
    assert payload["planner_summary"]["requested_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
    ]
    assert payload["planner_summary"]["selected_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
    ]
    assert payload["planner_recommendation_count"] == 1
    action = payload["action_plan"][0]
    assert action["recommendation_id"] == "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    assert action["kind"] == "sparse_attention_coverage"
    assert action["missing_evidence_fields"] == []
    assert action["action_parameters"]["proposed_local_window"] == 6


def test_standalone_downstream_ci_text_prints_selected_planner_ids(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "text",
            "--planner-recommendation",
            "ROPE-USE-D19-MARGIN-FRONTIER",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI downstream CI acceptance ok:" in result.stdout
    assert "planner.selected=ROPE-USE-D19-MARGIN-FRONTIER" in result.stdout
    assert "accepted.rope_position_distinguishability" in result.stdout


def test_standalone_downstream_ci_rejects_missing_selected_recommendation(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--planner-recommendation",
            "NOT-A-RECOMMENDATION",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "requested planner recommendations were not selected by the "
        "accepted policy: ['NOT-A-RECOMMENDATION']"
    ) in result.stderr


def test_standalone_downstream_ci_emits_json_rejection_report(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
            "--planner-recommendation",
            "NOT-A-RECOMMENDATION",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert result.stdout == ""
    payload = json.loads(result.stderr)
    assert payload["schema_id"] == (
        "circle_calculus.downstream_ci_rejection_report.v0"
    )
    assert payload["example_schema_id"] == (
        "circle_calculus.downstream_ci_acceptance_example.v0"
    )
    assert payload["accepted"] is False
    assert payload["planner_requested_recommendation_ids"] == [
        "NOT-A-RECOMMENDATION",
    ]
    assert payload["failure_count"] == 1
    assert payload["failures"] == [
        "requested planner recommendations were not selected by the "
        "accepted policy: ['NOT-A-RECOMMENDATION']"
    ]
    assert payload["pack_path"] == str(pack_path)
    assert payload["policy_path"] == str(policy_path)
    assert "not a mathematical proof" in payload["not_claimed"]


def test_standalone_downstream_ci_rejects_stale_policy(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["expected_pack_fingerprint"] = "0" * 64
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "policy expected pack fingerprint does not match pack" in result.stderr


def test_standalone_downstream_ci_json_rejection_reports_policy_drift(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["expected_pack_fingerprint"] = "0" * 64
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert "policy expected pack fingerprint does not match pack" in (
        payload["failures"]
    )


def test_standalone_downstream_ci_rejects_duplicate_policy_contract_kind(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"].append(json.loads(json.dumps(policy["contracts"][0])))
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "rope_position_distinguishability: "
        "policy selects contract kind more than once"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_duplicate_required_field_pin(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_fields"].append(
        "d19_context_range_min_exclusive"
    )
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "policy.contracts[0].required_fields repeats string "
        "'d19_context_range_min_exclusive'"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_duplicate_recommendation_pin(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_ids"].append(
        "ROPE-USE-D19-MARGIN-FRONTIER"
    )
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "policy.contracts[0].required_recommendation_ids repeats string "
        "'ROPE-USE-D19-MARGIN-FRONTIER'"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_duplicate_theorem_pin(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_theorem_ids"].append("AIRA-T0216")
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "policy.contracts[0].required_theorem_ids repeats string "
        "'AIRA-T0216'"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_duplicate_nested_policy_pin(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_evidence_fields"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ].append("d19_context_range_max_inclusive")
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "policy.contracts[0].required_recommendation_evidence_fields."
        "ROPE-USE-D19-MARGIN-FRONTIER repeats string "
        "'d19_context_range_max_inclusive'"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_duplicate_nested_theorem_pin(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_theorem_ids"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ].append("AIRA-T0216")
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "policy.contracts[0].required_recommendation_theorem_ids."
        "ROPE-USE-D19-MARGIN-FRONTIER repeats string 'AIRA-T0216'"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_missing_required_recommendation_index(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    del pack["planner_recommendation_index"]["ROPE-USE-D19-MARGIN-FRONTIER"]
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "rope_position_distinguishability: "
        "ROPE-USE-D19-MARGIN-FRONTIER is missing from index"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_required_index_evidence_drift(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    indexed = pack["planner_recommendation_index"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ]
    indexed["evidence_fields"] = [
        field
        for field in indexed["evidence_fields"]
        if field != "d19_context_range_max_inclusive"
    ]
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "rope_position_distinguishability: ROPE-USE-D19-MARGIN-FRONTIER "
        "index missing required evidence fields"
    ) in result.stderr
    assert "d19_context_range_max_inclusive" in result.stderr


def test_standalone_downstream_ci_rejects_required_theorem_drift(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_theorem_ids"] = ["NOT-A-THEOREM"]
    policy["contracts"][0]["required_recommendation_theorem_ids"] = {
        "ROPE-USE-D19-MARGIN-FRONTIER": ["NOT-A-REC-THEOREM"],
    }
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "rope_position_distinguishability: missing required theorem ids "
        "['NOT-A-THEOREM']"
    ) in result.stderr
    assert "missing recommendation theorem ids" in result.stderr
    assert "NOT-A-REC-THEOREM" in result.stderr


def test_standalone_downstream_ci_rejects_required_action_parameter_drift(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    for contract in pack["contracts"]:
        if contract["kind"] == "rope_position_distinguishability":
            for recommendation in contract["planner_recommendations"]:
                if recommendation["id"] == "ROPE-USE-D19-MARGIN-FRONTIER":
                    del recommendation["classifier_regions"]
                    break
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "rope_position_distinguishability: missing recommendation action "
        "parameters"
    ) in result.stderr
    assert "classifier_regions" in result.stderr


def test_standalone_downstream_ci_rejects_required_action_parameter_path_drift(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    for contract in pack["contracts"]:
        if contract["kind"] == "rope_position_distinguishability":
            for recommendation in contract["planner_recommendations"]:
                if recommendation["id"] == "ROPE-USE-D19-MARGIN-FRONTIER":
                    recommendation["classifier_regions"] = [
                        region
                        for region in recommendation["classifier_regions"]
                        if region["region"] != "undecided_margin_gap"
                    ]
                    break
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "rope_position_distinguishability: missing recommendation "
        "action-parameter paths"
    ) in result.stderr
    assert "classifier_regions[region=undecided_margin_gap].condition" in result.stderr


def test_standalone_downstream_ci_rejects_required_index_theorem_drift(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    indexed = pack["planner_recommendation_index"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ]
    indexed["theorem_ids"] = [
        theorem_id
        for theorem_id in indexed["theorem_ids"]
        if theorem_id != "AIRA-T0216"
    ]
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "rope_position_distinguishability: ROPE-USE-D19-MARGIN-FRONTIER "
        "index missing required theorem ids"
    ) in result.stderr
    assert "AIRA-T0216" in result.stderr


def test_standalone_downstream_ci_rejects_nonrequired_index_action_drift(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    recommendation_id = "SPARSE-REPAIR-LARGEST-GAP-INTERVAL"
    pack["planner_recommendation_index"][recommendation_id][
        "action_kind"
    ] = "not_the_source_action"
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "sparse_attention_coverage: "
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL index action_kind drifted"
    ) in result.stderr


def test_standalone_downstream_ci_rejects_duplicate_selected_recommendation_id(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    duplicate_id = "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    for contract in pack["contracts"]:
        if contract["kind"] == "sparse_attention_coverage":
            contract["planner_recommendations"][1]["id"] = duplicate_id
            break
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert (
        "sparse_attention_coverage: duplicate recommendation id "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ) in result.stderr


def test_standalone_downstream_ci_treats_evidence_pins_as_required_ids(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_ids"] = []
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted_contracts"][0]["required_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]


def test_standalone_downstream_ci_treats_theorem_pins_as_required_ids(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_ids"] = []
    policy["contracts"][0]["required_recommendation_evidence_fields"] = {}
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted_contracts"][0]["required_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]


def test_standalone_downstream_ci_rejects_unready_contract(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    for contract in pack["contracts"]:
        if contract["kind"] == "sparse_attention_coverage":
            contract["consumer_check"]["ready_for_downstream_fixture_use"] = False
            break
    pack["contract_readiness_index"]["sparse_attention_coverage"][
        "ready_for_downstream_fixture_use"
    ] = False
    _refresh_fingerprints(pack)
    pack_path, policy_path = _write_pack_and_policy(tmp_path, pack)

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "sparse_attention_coverage: consumer readiness is not true" in (
        result.stderr
    )
