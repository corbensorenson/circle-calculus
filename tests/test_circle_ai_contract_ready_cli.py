from __future__ import annotations

import json
import subprocess
import sys


def test_contract_ready_cli_accepts_ready_kind_text() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract readiness ok: sparse_attention_coverage" in result.stdout
    assert "ready=True" in result.stdout
    assert "proof_proved=True" in result.stdout
    assert "unresolved=0" in result.stdout
    assert "unproved=0" in result.stdout
    assert "recommendations=4" in result.stdout
    assert (
        "planner_recommendations=SPARSE-LOCAL-FIRST-INTERVAL-REPAIR,"
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL,"
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK,SPARSE-INTERVAL-REPAIR-PATH"
    ) in result.stdout
    assert (
        "validation_commands=python scripts/stride_family_certify.py --context 120 "
        "--strides 7,13 --path-length 3 --local-window 4 --format json"
    ) in result.stdout
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage"
        in result.stdout
    )


def test_contract_ready_cli_accepts_ready_kind_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "seed_rule_exact_regeneration",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "seed_rule_exact_regeneration"
    assert payload["ready_for_downstream_fixture_use"] is True
    assert payload["readiness"]["theorem_count"] == 32
    assert payload["readiness"]["all_theorem_ids_proved"] is True
    assert payload["contract"]["id"] == "CC-AI-CONTRACT-SEED-RULE-001"
    assert "GEN-T0050" in payload["contract"]["theorem_ids"]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration"
        in payload["contract"]["validation_commands"]
    )


def test_contract_ready_cli_emits_text_digest_fields() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "kv_cache_ring_buffer",
            "--digest",
            "--field",
            "stale_probe_first_stale_token",
            "--field",
            "stale_probe_stale_requested_count",
            "--include-field-metadata",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract digest ok: kv_cache_ring_buffer" in result.stdout
    assert "fields=2" in result.stdout
    assert "missing=0" in result.stdout
    assert "evidence.stale_probe_first_stale_token=12" in result.stdout
    assert "evidence.stale_probe_stale_requested_count=1" in result.stdout
    assert "field.stale_probe_first_stale_token.value_kind=integer" in result.stdout
    assert "proof_role=fixture_parameter_or_observation" in result.stdout
    assert (
        "validation_commands=python scripts/kv_cache_certify.py --cache-size 16"
        in result.stdout
    )


def test_contract_ready_cli_emits_json_digest_fields() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "rope_position_distinguishability",
            "--digest",
            "--format",
            "json",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["ready_for_downstream_fixture_use"] is True
    assert payload["evidence_fields"] == {
        "d19_proved_request_status": "proved",
        "d19_impossible_request_status": "impossible",
    }
    assert "AIRA-T0216" in payload["theorem_ids"]
    assert "AIRA-T0214" in payload["theorem_ids"]
    assert "AIRA-T0231" in payload["theorem_ids"]


def test_contract_ready_cli_emits_rope_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "rope_position_distinguishability",
            "--digest",
            "--format",
            "json",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "d19_proved_request_status": "proved",
        "d19_impossible_request_status": "impossible",
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert payload["planner_recommendations"][0]["exact_discrete_pass"] is True
    assert payload["planner_recommendations"][0]["collision_pair_count"] == 0
    assert payload["planner_recommendations"][1]["proved_margin"] == "1/328459"
    assert (
        payload["planner_recommendations"][1]["impossible_margin_floor"]
        == "1/328458"
    )


def test_contract_ready_cli_emits_json_digest_field_metadata() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "strided_candidate_fanout",
            "--digest",
            "--format",
            "json",
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


def test_contract_ready_cli_emits_json_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--digest",
            "--format",
            "json",
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
    assert payload["planner_recommendations"][1]["target_interval_stop"] == 119


def test_contract_ready_cli_emits_text_fingerprints() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract fingerprints ok:" in result.stdout
    assert "algorithm=sha256-json-v1" in result.stdout
    assert "fingerprint.sparse_attention_coverage" in result.stdout
    assert "fingerprint.seed_rule_exact_regeneration" in result.stdout


def test_contract_ready_cli_emits_json_fingerprints() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(payload["pack_content_fingerprint"]) == 64
    assert "sparse_attention_coverage" in payload["contract_fingerprint_index"]
    sparse = payload["contract_fingerprint_index"]["sparse_attention_coverage"]
    assert sparse["id"] == "CC-AI-CONTRACT-SPARSE-001"
    assert len(sparse["content_fingerprint"]) == 64


def test_contract_ready_cli_accepts_matching_fingerprint_expectations() -> None:
    fingerprint_result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    fingerprints = json.loads(fingerprint_result.stdout)
    sparse = fingerprints["contract_fingerprint_index"]["sparse_attention_coverage"]

    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--expect-pack-fingerprint",
            fingerprints["pack_content_fingerprint"],
            "--expect-contract-fingerprint",
            f"sparse_attention_coverage={sparse['content_fingerprint']}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract fingerprints ok:" in result.stdout


def test_contract_ready_cli_rejects_mismatched_fingerprint_expectation() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--expect-pack-fingerprint",
            "0" * 64,
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3
    assert "fingerprint expectation failed" in result.stderr
    assert "pack fingerprint mismatch" in result.stderr


def test_contract_ready_cli_emits_kv_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "kv_cache_ring_buffer",
            "--digest",
            "--format",
            "json",
            "--field",
            "stale_probe_first_stale_token",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"stale_probe_first_stale_token": 12}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "KV-DROP-STALE-REQUEST-TOKEN",
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
    ]
    assert payload["planner_recommendations"][0]["target_token"] == 12
    assert (
        payload["planner_recommendations"][0]["next_same_slot_overwrite_token"]
        == 28
    )
    assert payload["planner_recommendations"][1]["request_token_count"] == 20


def test_contract_ready_cli_emits_recurrence_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "recurrence_schedule",
            "--digest",
            "--format",
            "json",
            "--field",
            "scheduled_work_saving",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"scheduled_work_saving": 19}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
    ]
    assert payload["planner_recommendations"][0]["active_token_work"] == 21
    assert payload["planner_recommendations"][0]["scheduled_work_saving"] == 19
    assert (
        payload["planner_recommendations"][0]["post_period_extension_scheduled_work_saving"]
        == 27
    )
    assert payload["planner_recommendations"][0]["post_period_extra_steps"] == 3
    assert (
        payload["planner_recommendations"][0][
            "post_period_multi_extension_scheduled_work_saving"
        ]
        == 43
    )
    assert payload["planner_recommendations"][1]["shifted_token"] == 22
    assert payload["planner_recommendations"][1]["active_step"] == 2


def test_contract_ready_cli_emits_seed_rule_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "seed_rule_exact_regeneration",
            "--digest",
            "--format",
            "json",
            "--field",
            "storage_saving",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"storage_saving": 71}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "SEED-RULE-USE-EXACT-REGENERATION-RECIPE",
        "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE",
    ]
    assert payload["planner_recommendations"][0]["generated_object_length"] == 128
    assert payload["planner_recommendations"][1]["candidate_count"] == 3
    assert payload["planner_recommendations"][1]["storage_saving"] == 71


def test_contract_ready_cli_emits_cyclic_memory_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "cyclic_memory_residue_winding",
            "--digest",
            "--format",
            "json",
            "--field",
            "max_alias_load",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"max_alias_load": 4}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE",
        "MEMORY-AUDIT-FINITE-ALIAS-LOAD",
    ]
    assert payload["planner_recommendations"][0]["alias_count"] == 4
    assert payload["planner_recommendations"][0]["residue_slot"] == 7
    assert payload["planner_recommendations"][1]["slot_loads"] == [
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
    ]


def test_contract_ready_cli_emits_strided_fanout_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "strided_candidate_fanout",
            "--digest",
            "--format",
            "json",
            "--field",
            "full_coverage",
            "--field",
            "effective_candidate_budget",
            "--field",
            "duplicate_count",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "full_coverage": True,
        "effective_candidate_budget": 12,
        "duplicate_count": 0,
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE",
        "FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET",
    ]
    assert payload["planner_recommendations"][0]["full_coverage"] is True
    assert payload["planner_recommendations"][0]["predicted_reach"] == 12
    assert payload["planner_recommendations"][1]["effective_candidate_budget"] == 12
    assert payload["planner_recommendations"][1]["duplicate_count"] == 0


def test_contract_ready_cli_emits_multicoil_phase_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "multicoil_phase_feature",
            "--digest",
            "--format",
            "json",
            "--field",
            "joint_repeat_horizon",
            "--field",
            "relative_phase",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "joint_repeat_horizon": 35,
        "relative_phase": 3,
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "PHASE-USE-JOINT-REPEAT-HORIZON",
        "PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT",
    ]
    assert payload["planner_recommendations"][0]["phase_tuple"] == [2, 2]
    assert payload["planner_recommendations"][0]["joint_repeat_horizon"] == 35
    assert payload["planner_recommendations"][1]["relative_phase"] == 3
    assert payload["planner_recommendations"][1]["shifted_relative_phase"] == 3


def test_contract_ready_cli_emits_circulant_mixer_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "circulant_block_cyclic_mixer",
            "--digest",
            "--format",
            "json",
            "--field",
            "max_abs_dense_delta",
            "--field",
            "block_to_dense_ratio",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "max_abs_dense_delta": 0,
        "block_to_dense_ratio": 0.0625,
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "MIXER-AUDIT-CIRCULANT-DENSE-PARITY",
        "MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET",
    ]
    assert payload["planner_recommendations"][0]["max_abs_dense_delta"] == 0
    assert payload["planner_recommendations"][0]["circulant_parameters"] == 8
    assert payload["planner_recommendations"][1]["block_cyclic_parameters"] == 128
    assert payload["planner_recommendations"][1]["block_to_dense_ratio"] == 0.0625


def test_contract_ready_cli_emits_text_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--digest",
            "--field",
            "first_uncovered_lag",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract digest ok: sparse_attention_coverage" in result.stdout
    assert (
        "recommendation.SPARSE-LOCAL-FIRST-INTERVAL-REPAIR "
        "action=increase_local_window scope=first_uncovered_interval_only"
    ) in result.stdout
    assert "recommendation.SPARSE-REPAIR-LARGEST-GAP-INTERVAL" in result.stdout
    assert "theorems=AIT-T0104" in result.stdout
    assert "recommendation.SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK" in result.stdout
    assert "theorems=AIT-T0023,AIT-T0034" in result.stdout


def test_contract_ready_cli_lists_kinds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--list-kinds",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "kind=rope_position_distinguishability" in result.stdout
    assert "kind=sparse_attention_coverage" in result.stdout
    assert "ready=True" in result.stdout
    assert "recommendations=2" in result.stdout


def test_contract_ready_cli_lists_recommendations_text() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--list-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        "recommendation=ROPE-USE-D19-MARGIN-FRONTIER "
        "kind=rope_position_distinguishability"
    ) in result.stdout
    assert "contract=CC-AI-CONTRACT-ROPE-001" in result.stdout
    assert "recommendation=FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE" in result.stdout
    assert "recommendation=MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET" in result.stdout
    assert "ready=True" in result.stdout
    assert "theorems=" in result.stdout


def test_contract_ready_cli_lists_recommendations_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--list-recommendations",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert len(payload) == 20
    assert payload["ROPE-USE-D19-MARGIN-FRONTIER"]["kind"] == (
        "rope_position_distinguishability"
    )
    assert payload["ROPE-USE-D19-MARGIN-FRONTIER"]["contract_id"] == (
        "CC-AI-CONTRACT-ROPE-001"
    )
    assert payload["ROPE-USE-D19-MARGIN-FRONTIER"][
        "ready_for_downstream_fixture_use"
    ] is True
    assert "AIRA-T0216" in payload["ROPE-USE-D19-MARGIN-FRONTIER"]["theorem_ids"]
    assert payload["MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET"]["kind"] == (
        "circulant_block_cyclic_mixer"
    )


def test_contract_ready_cli_emits_action_plan_json_with_values() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "seed_rule_exact_regeneration",
            "--action-plan",
            "--include-values",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["planner_schema"] == "circle_calculus.ai_contract_planner.v0"
    assert payload["planner_includes_values"] is True
    assert payload["selected_kinds"] == ["seed_rule_exact_regeneration"]
    assert payload["planner_recommendation_count"] == 2
    assert payload["ready_recommendation_count"] == 2
    actions = payload["action_plan"]
    assert [action["recommendation_id"] for action in actions] == [
        "SEED-RULE-USE-EXACT-REGENERATION-RECIPE",
        "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE",
    ]
    assert actions[0]["evidence_values"]["fixture_n"] == 128
    assert actions[0]["evidence_values"]["exact_regeneration"] is True
    assert actions[1]["evidence_values"]["bounded_search_best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert actions[1]["action_parameters"]["best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert "GEN-T0046" in actions[1]["theorem_ids"]
    assert actions[1]["missing_evidence_fields"] == []


def test_contract_ready_cli_emits_action_plan_text_for_all_kinds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--action-plan",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI action plan ok:" in result.stdout
    assert "actions=20" in result.stdout
    assert "ready_actions=20" in result.stdout
    assert "includes_values=False" in result.stdout
    assert "action.ROPE-USE-D19-MARGIN-FRONTIER" in result.stdout
    assert "action.SPARSE-INTERVAL-REPAIR-PATH" in result.stdout
    assert "action.SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE" in result.stdout


def test_contract_ready_cli_rejects_unknown_kind() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "not_a_contract",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "unknown contract kind: not_a_contract" in result.stderr


def test_contract_ready_make_target_checks_flagship_kinds() -> None:
    result = subprocess.run(
        ["make", "circle-ai-contracts-ready"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "kind=rope_position_distinguishability" in result.stdout
    assert "recommendation=ROPE-USE-D19-MARGIN-FRONTIER" in result.stdout
    assert "circle AI action plan ok:" in result.stdout
    assert "actions=20" in result.stdout
    assert "ready_actions=20" in result.stdout
    assert '"planner_schema": "circle_calculus.ai_contract_planner.v0"' in result.stdout
    assert '"best_shorter_candidate_id": "finite_circle_public_fixture"' in result.stdout
    assert "circle AI contract readiness ok: rope_position_distinguishability" in result.stdout
    assert '"d19_proved_request_status": "proved"' in result.stdout
    assert '"d19_impossible_request_status": "impossible"' in result.stdout
    assert "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK" in result.stdout
    assert "ROPE-USE-D19-MARGIN-FRONTIER" in result.stdout
    assert "circle AI contract readiness ok: kv_cache_ring_buffer" in result.stdout
    assert "circle AI contract digest ok: kv_cache_ring_buffer" in result.stdout
    assert "evidence.stale_probe_first_stale_token=12" in result.stdout
    assert "circle AI contract digest ok: strided_candidate_fanout" in result.stdout
    assert "recommendation.FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE" in result.stdout
    assert (
        "recommendation.FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET"
        in result.stdout
    )
    assert "circle AI contract digest ok: multicoil_phase_feature" in result.stdout
    assert "recommendation.PHASE-USE-JOINT-REPEAT-HORIZON" in result.stdout
    assert (
        "recommendation.PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT"
        in result.stdout
    )
    assert "circle AI contract digest ok: circulant_block_cyclic_mixer" in result.stdout
    assert "recommendation.MIXER-AUDIT-CIRCULANT-DENSE-PARITY" in result.stdout
    assert (
        "recommendation.MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET"
        in result.stdout
    )
    assert "circle AI contract digest ok: cyclic_memory_residue_winding" in result.stdout
    assert "evidence.max_alias_load=4" in result.stdout
    assert (
        "recommendation.MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE"
        in result.stdout
    )
    assert "circle AI contract readiness ok: sparse_attention_coverage" in result.stdout
    assert "circle AI contract readiness ok: recurrence_schedule" in result.stdout
    assert "circle AI contract digest ok: recurrence_schedule" in result.stdout
    assert "evidence.scheduled_work_saving=19" in result.stdout
    assert "evidence.post_period_multi_extension_scheduled_work_saving=43" in result.stdout
    assert (
        "recommendation.RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE"
        in result.stdout
    )
    assert "circle AI contract digest ok: seed_rule_exact_regeneration" in result.stdout
    assert "evidence.storage_saving=71" in result.stdout
    assert (
        "recommendation.SEED-RULE-USE-EXACT-REGENERATION-RECIPE"
        in result.stdout
    )
