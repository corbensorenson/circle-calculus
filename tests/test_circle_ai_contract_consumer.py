from __future__ import annotations

from copy import deepcopy

import pytest

from circle_math.applications.circle_ai_contract_consumer import (
    FINGERPRINT_ALGORITHM,
    ContractAcceptanceError,
    ContractConsumerError,
    ContractNotReadyError,
    ContractFingerprintMismatchError,
    ContractPackSchemaError,
    contract_acceptance_receipt,
    contract_digest,
    contract_fingerprint_summary,
    contract_recommendations,
    contract_kinds,
    find_planner_recommendation,
    planner_action_plan,
    planner_recommendation_index,
    planner_recommendations_for_kind,
    readiness_report,
    readiness_summary,
    require_fingerprint_expectations,
    require_ready_contract,
    validate_consumer_pack,
    verify_fingerprint_expectations,
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


def test_consumer_adapter_reads_ready_sparse_attention_contract() -> None:
    pack = build_contract_pack()

    assert validate_consumer_pack(pack) == []
    assert "sparse_attention_coverage" in contract_kinds(pack)

    contract = require_ready_contract(pack, "sparse_attention_coverage")
    summary = readiness_summary(pack, "sparse_attention_coverage")

    assert contract["id"] == "CC-AI-CONTRACT-SPARSE-001"
    assert summary.ready is True
    assert summary.failure_reasons() == ()
    assert summary.theorem_count == len(summary.theorem_ids)
    assert "AIT-T0155" in summary.theorem_ids
    assert "docs/SPARSE_ATTENTION_CERTIFIER_QUICKSTART.md" in summary.quickstart_docs
    assert "site/chapters/applications/sparse_attention_contract.qmd" in (
        summary.living_book_pages
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage"
        in summary.validation_commands
    )
    assert summary.planner_recommendation_count == 4
    assert summary.planner_recommendation_ids == (
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
    )
    assert "model quality" in summary.not_claimed


def test_consumer_adapter_emits_all_contract_readiness_report() -> None:
    pack = build_contract_pack()

    report = readiness_report(pack)

    assert report["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert report["readiness_schema"] == "circle_calculus.ai_contract_readiness.v0"
    assert report["contract_count"] == len(contract_kinds(pack))
    assert report["ready_contract_count"] == report["contract_count"]
    assert report["all_ready"] is True
    assert "kv_cache_ring_buffer" in report["selected_kinds"]
    assert all(
        summary["ready_for_downstream_fixture_use"] is True
        for summary in report["summaries"]
    )


def test_consumer_adapter_readiness_report_handles_unready_contract() -> None:
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

    report = readiness_report(pack, [kind])

    assert report["selected_kinds"] == [kind]
    assert report["contract_count"] == 1
    assert report["ready_contract_count"] == 0
    assert report["all_ready"] is False
    assert report["summaries"][0]["failure_reasons"] == ["contract_passed is false"]


def test_consumer_adapter_exposes_fingerprint_summary_and_expectations() -> None:
    pack = build_contract_pack()

    summary = contract_fingerprint_summary(pack)

    assert summary["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert summary["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(summary["pack_content_fingerprint"]) == 64
    assert set(summary["pack_content_fingerprint"]) <= set("0123456789abcdef")
    sparse = summary["contract_fingerprint_index"]["sparse_attention_coverage"]
    assert sparse == {
        "id": "CC-AI-CONTRACT-SPARSE-001",
        "content_fingerprint_algorithm": "sha256-json-v1",
        "content_fingerprint": sparse["content_fingerprint"],
    }
    assert verify_fingerprint_expectations(
        pack,
        expected_pack_fingerprint=summary["pack_content_fingerprint"],
        expected_contract_fingerprints={
            "sparse_attention_coverage": sparse["content_fingerprint"],
        },
    ) == ()
    assert require_fingerprint_expectations(
        pack,
        expected_pack_fingerprint=summary["pack_content_fingerprint"],
        expected_contract_fingerprints={
            "sparse_attention_coverage": sparse["content_fingerprint"],
        },
    ) == summary


def test_consumer_adapter_reports_fingerprint_expectation_failures() -> None:
    pack = build_contract_pack()
    wrong_hash = "0" * 64

    failures = verify_fingerprint_expectations(
        pack,
        expected_pack_fingerprint=wrong_hash,
        expected_contract_fingerprints={
            "sparse_attention_coverage": wrong_hash,
            "not_a_contract": wrong_hash,
            "rope_position_distinguishability": "not-a-sha",
        },
    )

    assert any("pack fingerprint mismatch" in failure for failure in failures)
    assert any(
        "sparse_attention_coverage fingerprint mismatch" in failure
        for failure in failures
    )
    assert any(
        "unknown contract kind for fingerprint expectation: not_a_contract"
        in failure
        for failure in failures
    )
    assert any(
        "expected contract fingerprint for rope_position_distinguishability"
        in failure
        for failure in failures
    )
    with pytest.raises(
        ContractFingerprintMismatchError,
        match="fingerprint expectation failed",
    ):
        require_fingerprint_expectations(
            pack,
            expected_pack_fingerprint=wrong_hash,
        )


def test_consumer_adapter_detects_fingerprint_drift() -> None:
    pack = build_contract_pack()
    broken = deepcopy(pack)
    broken["contracts"][0]["fields"]["exact_discrete_pass"] = "changed"

    failures = validate_consumer_pack(broken)

    assert any("pack_content_fingerprint drifted" in failure for failure in failures)
    assert any("content_fingerprint drifted" in failure for failure in failures)


def test_consumer_digest_defaults_to_minimum_evidence_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(pack, "kv_cache_ring_buffer")

    assert digest["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert digest["contract_id"] == "CC-AI-CONTRACT-KV-001"
    assert digest["ready_for_downstream_fixture_use"] is True
    assert digest["missing_requested_fields"] == []
    assert digest["evidence_fields"]["adapter_request_pass"] is True
    assert digest["evidence_fields"]["stale_requested_count"] == 0
    assert digest["evidence_fields"]["stale_probe_requested_tokens"] == [12, 20]
    assert digest["evidence_fields"]["stale_probe_requested_slots"] == [12, 4]
    assert digest["evidence_fields"]["stale_probe_pass"] is False
    assert digest["evidence_fields"]["stale_probe_first_stale_token"] == 12
    assert (
        digest["evidence_fields"]["stale_probe_first_stale_next_overwrite_token"]
        == 28
    )
    assert digest["evidence_fields"]["stale_probe_stale_requested_count"] == 1
    assert digest["evidence_fields"]["stale_probe_stale_member_blocks_pass"] is True
    assert (
        digest["evidence_fields"][
            "stale_probe_fail_iff_stale_count_positive_under_nonfuture_nodup"
        ]
        is True
    )
    assert digest["evidence_fields"]["sink_window_token_count"] == 20
    assert (
        digest["evidence_fields"]["sink_prefix_disjoint_from_live_window"]
        is True
    )
    assert digest["evidence_fields"]["sink_tokens_non_future"] is True
    assert digest["evidence_fields"]["sink_tokens_retained_by_policy"] is True
    assert (
        digest["evidence_fields"]["sink_tokens_outside_ordinary_rolling_window"]
        is True
    )
    assert "AIM-T0110" in digest["theorem_ids"]
    assert "AIM-T0136" in digest["theorem_ids"]
    assert "AIM-T0137" in digest["theorem_ids"]
    assert "AIM-T0148" in digest["theorem_ids"]
    assert "AIM-T0149" in digest["theorem_ids"]
    assert digest["entrypoints"]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer"
        in digest["validation_commands"]
    )


def test_consumer_digest_accepts_selected_fields_and_reports_missing() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "rope_position_distinguishability",
        fields=("exact_discrete_pass", "not_a_field"),
    )

    assert digest["evidence_fields"] == {"exact_discrete_pass": True}
    assert digest["missing_requested_fields"] == ["not_a_field"]


def test_consumer_acceptance_receipt_requires_fields_and_recommendations() -> None:
    pack = build_contract_pack()

    receipt = contract_acceptance_receipt(
        pack,
        "sparse_attention_coverage",
        required_fields=(
            "first_uncovered_lag",
            "first_uncovered_interval_start",
        ),
        required_theorem_ids=("AIT-T0104",),
        required_recommendation_ids=("SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",),
        required_recommendation_evidence_fields={
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": (
                "first_uncovered_interval_start",
                "first_uncovered_interval_stop",
            ),
        },
        required_recommendation_theorem_ids={
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ("AIT-T0104",),
        },
        include_field_metadata=True,
    )

    assert receipt["receipt_schema"] == (
        "circle_calculus.ai_contract_acceptance_receipt.v0"
    )
    assert receipt["accepted"] is True
    assert receipt["kind"] == "sparse_attention_coverage"
    assert receipt["contract_id"] == "CC-AI-CONTRACT-SPARSE-001"
    assert len(receipt["pack_content_fingerprint"]) == 64
    assert len(receipt["contract_content_fingerprint"]) == 64
    assert receipt["required_fields"] == [
        "first_uncovered_lag",
        "first_uncovered_interval_start",
    ]
    assert receipt["evidence_fields"] == {
        "first_uncovered_lag": 5,
        "first_uncovered_interval_start": 5,
    }
    assert receipt["required_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ]
    assert receipt["required_recommendation_evidence_fields"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
            "first_uncovered_interval_start",
            "first_uncovered_interval_stop",
        ],
    }
    assert receipt["required_theorem_ids"] == ["AIT-T0104"]
    assert receipt["required_recommendation_theorem_ids"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["AIT-T0104"],
    }
    assert receipt["planner_recommendations"][0]["id"] == (
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    )
    assert receipt["field_catalog"]["first_uncovered_lag"]["value_kind"] == (
        "integer"
    )
    assert "AIT-T0104" in receipt["theorem_ids"]
    assert "model quality" in receipt["not_claimed"]


def test_consumer_acceptance_receipt_can_pin_action_parameters() -> None:
    pack = build_contract_pack()

    receipt = contract_acceptance_receipt(
        pack,
        "rope_position_distinguishability",
        required_fields=("d19_undecided_request_status",),
        required_recommendation_action_parameters={
            "ROPE-USE-D19-MARGIN-FRONTIER": (
                "applicable_context_range",
                "classifier_regions",
            ),
        },
    )

    assert receipt["required_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ]
    assert receipt["required_recommendation_action_parameters"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "applicable_context_range",
            "classifier_regions",
        ],
    }
    rope_frontier = receipt["planner_recommendations"][0]
    assert rope_frontier["classifier_regions"][1]["region"] == (
        "undecided_margin_gap"
    )
    assert rope_frontier["applicable_context_range"] == {
        "min_exclusive": 103993,
        "max_inclusive": 196608,
    }


def test_consumer_acceptance_receipt_can_pin_action_parameter_paths() -> None:
    pack = build_contract_pack()

    receipt = contract_acceptance_receipt(
        pack,
        "rope_position_distinguishability",
        required_recommendation_action_parameter_paths={
            "ROPE-USE-D19-MARGIN-FRONTIER": (
                "applicable_context_range.min_exclusive",
                "classifier_regions[region=proved].theorem_ids",
                "classifier_regions[region=undecided_margin_gap].condition",
                "classifier_regions[2].theorem_ids",
            ),
        },
    )

    assert receipt["required_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ]
    assert receipt["required_recommendation_action_parameter_paths"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "applicable_context_range.min_exclusive",
            "classifier_regions[region=proved].theorem_ids",
            "classifier_regions[region=undecided_margin_gap].condition",
            "classifier_regions[2].theorem_ids",
        ],
    }


def test_consumer_acceptance_receipt_rejects_missing_requirements() -> None:
    pack = build_contract_pack()

    with pytest.raises(
        ContractAcceptanceError,
        match="missing requested evidence fields: not_a_field",
    ):
        contract_acceptance_receipt(
            pack,
            "sparse_attention_coverage",
            required_fields=("not_a_field",),
        )

    with pytest.raises(
        ContractAcceptanceError,
        match="missing requested planner recommendations: NOT-A-REC",
    ):
        contract_acceptance_receipt(
            pack,
            "sparse_attention_coverage",
            required_recommendation_ids=("NOT-A-REC",),
        )

    with pytest.raises(
        ContractAcceptanceError,
        match="missing requested theorem ids: NOT-A-THEOREM",
    ):
        contract_acceptance_receipt(
            pack,
            "sparse_attention_coverage",
            required_theorem_ids=("NOT-A-THEOREM",),
        )

    with pytest.raises(
        ContractAcceptanceError,
        match="missing required recommendation evidence fields",
    ):
        contract_acceptance_receipt(
            pack,
            "sparse_attention_coverage",
            required_recommendation_evidence_fields={
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": (
                    "not_recommendation_evidence",
                ),
            },
        )

    with pytest.raises(
        ContractAcceptanceError,
        match="missing required recommendation theorem ids",
    ):
        contract_acceptance_receipt(
            pack,
            "sparse_attention_coverage",
            required_recommendation_theorem_ids={
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": (
                    "NOT-A-REC-THEOREM",
                ),
            },
        )

    with pytest.raises(
        ContractAcceptanceError,
        match="missing required recommendation action parameters",
    ):
        contract_acceptance_receipt(
            pack,
            "rope_position_distinguishability",
            required_recommendation_action_parameters={
                "ROPE-USE-D19-MARGIN-FRONTIER": (
                    "not_an_action_parameter",
                ),
            },
        )

    with pytest.raises(
        ContractAcceptanceError,
        match="missing required recommendation action-parameter paths",
    ):
        contract_acceptance_receipt(
            pack,
            "rope_position_distinguishability",
            required_recommendation_action_parameter_paths={
                "ROPE-USE-D19-MARGIN-FRONTIER": (
                    "classifier_regions[region=not_a_region].theorem_ids",
                ),
            },
        )

    with pytest.raises(
        ContractAcceptanceError,
        match="invalid recommendation action-parameter paths",
    ):
        contract_acceptance_receipt(
            pack,
            "rope_position_distinguishability",
            required_recommendation_action_parameter_paths={
                "ROPE-USE-D19-MARGIN-FRONTIER": (
                    "theorem_ids[0]",
                ),
            },
        )


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        (
            {"required_fields": ("first_uncovered_lag", "first_uncovered_lag")},
            "required_fields must not contain duplicate strings",
        ),
        (
            {"required_theorem_ids": ("AIT-T0104", "AIT-T0104")},
            "required_theorem_ids must not contain duplicate strings",
        ),
        (
            {
                "required_recommendation_ids": (
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
                ),
            },
            "required_recommendation_ids must not contain duplicate strings",
        ),
        (
            {
                "required_recommendation_evidence_fields": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": (
                        "first_uncovered_interval_start",
                        "first_uncovered_interval_start",
                    ),
                },
            },
            (
                "required_recommendation_evidence_fields"
                ".*must not contain duplicate strings"
            ),
        ),
        (
            {
                "required_recommendation_theorem_ids": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": (
                        "AIT-T0104",
                        "AIT-T0104",
                    ),
                },
            },
            (
                "required_recommendation_theorem_ids"
                ".*must not contain duplicate strings"
            ),
        ),
        (
            {
                "required_recommendation_action_parameters": {
                    "ROPE-USE-D19-MARGIN-FRONTIER": (
                        "classifier_regions",
                        "classifier_regions",
                    ),
                },
            },
            (
                "required_recommendation_action_parameters"
                ".*must not contain duplicate strings"
            ),
        ),
    ],
)
def test_consumer_acceptance_receipt_rejects_duplicate_requirement_pins(
    kwargs: dict,
    match: str,
) -> None:
    pack = build_contract_pack()

    with pytest.raises(ContractAcceptanceError, match=match):
        contract_acceptance_receipt(
            pack,
            "sparse_attention_coverage",
            **kwargs,
        )


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        (
            {"required_fields": ("",)},
            "required_fields must contain only non-empty strings",
        ),
        (
            {
                "required_recommendation_theorem_ids": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ("",),
                },
            },
            (
                "required_recommendation_theorem_ids"
                ".*must contain only non-empty strings"
            ),
        ),
        (
            {
                "required_recommendation_action_parameters": {
                    "ROPE-USE-D19-MARGIN-FRONTIER": ("",),
                },
            },
            (
                "required_recommendation_action_parameters"
                ".*must contain only non-empty strings"
            ),
        ),
    ],
)
def test_consumer_acceptance_receipt_rejects_empty_requirement_pins(
    kwargs: dict,
    match: str,
) -> None:
    pack = build_contract_pack()

    with pytest.raises(ContractAcceptanceError, match=match):
        contract_acceptance_receipt(
            pack,
            "sparse_attention_coverage",
            **kwargs,
        )


def test_consumer_digest_can_include_field_metadata() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "strided_candidate_fanout",
        fields=("effective_candidate_budget", "candidate_budget_accounting"),
        include_field_metadata=True,
    )

    assert digest["evidence_fields"] == {
        "effective_candidate_budget": 12,
        "candidate_budget_accounting": True,
    }
    assert digest["field_catalog"]["effective_candidate_budget"] == {
        "description": (
            "Duplicate-collapsed candidate budget available after cyclic "
            "residue deduplication in the strided fanout contract."
        ),
        "proof_role": "finite_quantity_or_bound",
        "value_kind": "integer",
    }
    assert digest["field_catalog"]["candidate_budget_accounting"][
        "value_kind"
    ] == "boolean"
    assert "not_a_field" not in digest["field_catalog"]


def test_consumer_digest_exposes_rope_d19_request_classifier_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "rope_position_distinguishability",
        fields=(
            "d19_request_context",
            "d19_context_range_min_exclusive",
            "d19_context_range_max_inclusive",
            "d19_proved_margin",
            "d19_impossible_margin_floor",
            "d19_proved_request_status",
            "d19_proved_request_theorem_backed_classification",
            "d19_impossible_request_status",
            "d19_impossible_request_theorem_backed_classification",
            "d19_undecided_request_status",
            "d19_undecided_margin_open_gap",
            "d19_undecided_margin_interval_width",
            "d19_undecided_request_relation",
            "d19_margin_thresholds_ordered",
            "d19_proved_impossible_branches_disjoint",
            "d19_margin_status_exhaustive",
            "d19_in_range_semantic_trichotomy",
            "d19_proved_first_channel_bank_transfer",
            "d19_proved_first_channel_bank_shape",
            "d19_proved_first_channel_pair_scope",
            "d19_proved_first_channel_context_wide_contract",
            "d19_proved_first_channel_bank_tolerance_rule",
        ),
    )

    assert digest["evidence_fields"] == {
        "d19_request_context": 131072,
        "d19_context_range_min_exclusive": 103993,
        "d19_context_range_max_inclusive": 196608,
        "d19_proved_margin": "1/328459",
        "d19_impossible_margin_floor": "1/328458",
        "d19_proved_request_status": "proved",
        "d19_proved_request_theorem_backed_classification": True,
        "d19_impossible_request_status": "impossible",
        "d19_impossible_request_theorem_backed_classification": True,
        "d19_undecided_request_status": "undecided_margin_gap",
        "d19_undecided_margin_open_gap": True,
        "d19_undecided_margin_interval_width": "1/107884986222",
        "d19_undecided_request_relation": "strictly_between_thresholds",
        "d19_margin_thresholds_ordered": True,
        "d19_proved_impossible_branches_disjoint": True,
        "d19_margin_status_exhaustive": True,
        "d19_in_range_semantic_trichotomy": True,
        "d19_proved_first_channel_bank_transfer": True,
        "d19_proved_first_channel_bank_shape": "standard_channel0_first",
        "d19_proved_first_channel_pair_scope": (
            "all ordered unequal pairs left < right < requested_context"
        ),
        "d19_proved_first_channel_context_wide_contract": True,
        "d19_proved_first_channel_bank_tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
    }
    assert "AIRA-T0216" in digest["theorem_ids"]
    assert "AIRA-T0221" in digest["theorem_ids"]
    assert "AIRA-T0214" in digest["theorem_ids"]
    assert "AIRA-T0231" in digest["theorem_ids"]
    assert "AIRA-T0234" in digest["theorem_ids"]
    assert "AIRA-T0235" in digest["theorem_ids"]
    assert "AIRA-T0236" in digest["theorem_ids"]
    assert "AIRA-T0237" in digest["theorem_ids"]
    assert "AIRA-T0238" in digest["theorem_ids"]


def test_consumer_exposes_rope_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "rope_position_distinguishability")

    assert len(recommendations) == 2
    exact_bank = recommendations[0]
    assert exact_bank["id"] == "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK"
    assert exact_bank["coverage_scope"] == (
        "declared_integer_period_phase_bank_fixture"
    )
    assert exact_bank["preset"] == "llama_style_10000_4k"
    assert exact_bank["context_length"] == 4096
    assert exact_bank["exact_discrete_pass"] is True
    assert exact_bank["collision_pair_count"] == 0
    assert exact_bank["theorem_ids"] == [
        "AIRA-T0024",
        "AIRA-T0036",
        "AIRA-T0179",
        "AIRA-T0180",
        "AIRA-T0184",
    ]
    assert "not a proof of all-channel" in exact_bank["not_claimed"]

    d19_frontier = recommendations[1]
    assert d19_frontier["id"] == "ROPE-USE-D19-MARGIN-FRONTIER"
    assert d19_frontier["coverage_scope"] == (
        "standard_channel0_d19_context_range_fixture"
    )
    assert d19_frontier["request_context"] == 131072
    assert d19_frontier["proved_margin"] == "1/328459"
    assert d19_frontier["impossible_margin_floor"] == "1/328458"
    assert d19_frontier["proved_status"] == "proved"
    assert d19_frontier["impossible_status"] == "impossible"
    assert d19_frontier["undecided_probe_margin_in_open_gap"] is True
    assert d19_frontier["proved_branch_bank_transfer"] == {
        "applies": True,
        "bank_shape": "standard_channel0_first",
        "pair_scope": "all ordered unequal pairs left < right < requested_context",
        "context_wide_contract": True,
        "radian_bank_form": True,
        "tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
        "theorem_ids": [
            "AIRA-T0171",
            "AIRA-T0172",
            "AIRA-T0234",
            "AIRA-T0235",
            "AIRA-T0236",
            "AIRA-T0237",
        ],
    }
    assert d19_frontier["theorem_ids"] == [
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0216",
        "AIRA-T0217",
        "AIRA-T0218",
        "AIRA-T0219",
        "AIRA-T0220",
        "AIRA-T0221",
        "AIRA-T0232",
        "AIRA-T0233",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
        "AIRA-T0238",
        "AIRA-T0230",
        "AIRA-T0231",
    ]
    assert "does not transfer the impossible branch" in d19_frontier["not_claimed"]


def test_consumer_exposes_top_level_planner_recommendation_index() -> None:
    pack = build_contract_pack()

    index = planner_recommendation_index(pack)

    assert len(index) == 20
    assert sorted(index) == sorted(
        recommendation["id"]
        for contract in pack["contracts"]
        for recommendation in contract["planner_recommendations"]
    )
    rope_frontier = index["ROPE-USE-D19-MARGIN-FRONTIER"]
    assert rope_frontier == find_planner_recommendation(
        pack,
        "ROPE-USE-D19-MARGIN-FRONTIER",
    )
    assert rope_frontier["kind"] == "rope_position_distinguishability"
    assert rope_frontier["contract_id"] == "CC-AI-CONTRACT-ROPE-001"
    assert rope_frontier["ready_for_downstream_fixture_use"] is True
    assert rope_frontier["evidence_fields"] == [
        "d19_context_range_min_exclusive",
        "d19_context_range_max_inclusive",
        "d19_request_context",
        "d19_proved_margin",
        "d19_impossible_margin_floor",
        "d19_proved_request_status",
        "d19_proved_request_theorem_backed_classification",
        "d19_impossible_request_status",
        "d19_impossible_request_theorem_backed_classification",
        "d19_undecided_request_margin",
        "d19_undecided_request_status",
        "d19_undecided_margin_open_gap",
        "d19_undecided_probe_margin_in_open_gap",
        "d19_undecided_margin_interval_width",
        "d19_undecided_request_relation",
        "d19_margin_thresholds_ordered",
        "d19_proved_impossible_branches_disjoint",
        "d19_margin_status_exhaustive",
        "d19_in_range_semantic_trichotomy",
        "d19_proved_first_channel_bank_transfer",
        "d19_proved_first_channel_bank_shape",
        "d19_proved_first_channel_pair_scope",
        "d19_proved_first_channel_context_wide_contract",
        "d19_proved_first_channel_radian_bank_form",
        "d19_proved_first_channel_bank_tolerance_rule",
    ]
    assert "AIRA-T0216" in rope_frontier["theorem_ids"]
    assert "AIRA-T0234" in rope_frontier["theorem_ids"]
    assert "AIRA-T0235" in rope_frontier["theorem_ids"]
    assert "AIRA-T0236" in rope_frontier["theorem_ids"]
    assert "AIRA-T0237" in rope_frontier["theorem_ids"]
    assert "AIRA-T0238" in rope_frontier["theorem_ids"]
    assert "docs/ROPE_CERTIFIER_QUICKSTART.md" in rope_frontier["quickstart_docs"]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability"
        in rope_frontier["validation_commands"]
    )

    sparse_records = planner_recommendations_for_kind(
        pack,
        "sparse_attention_coverage",
    )
    assert [record["id"] for record in sparse_records] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
    ]
    assert find_planner_recommendation(pack, "not-a-recommendation") is None


def test_consumer_planner_action_plan_defaults_to_field_names_only() -> None:
    pack = build_contract_pack()

    plan = planner_action_plan(pack, ["sparse_attention_coverage"])

    assert plan["planner_schema"] == "circle_calculus.ai_contract_planner.v0"
    assert plan["planner_includes_values"] is False
    assert plan["selected_kinds"] == ["sparse_attention_coverage"]
    assert plan["planner_recommendation_count"] == 4
    assert plan["ready_recommendation_count"] == 4
    first_action = plan["action_plan"][0]
    assert first_action["recommendation_id"] == "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    assert first_action["theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0171",
        "AIT-T0166",
        "AIT-T0167",
    ]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage"
        in first_action["validation_commands"]
    )
    assert "evidence_values" not in first_action
    assert "action_parameters" not in first_action


def test_consumer_planner_action_plan_can_include_values() -> None:
    pack = build_contract_pack()

    plan = planner_action_plan(
        pack,
        ["sparse_attention_coverage"],
        include_values=True,
    )

    assert plan["planner_includes_values"] is True
    assert plan["planner_recommendation_count"] == 4
    first_action = plan["action_plan"][0]
    assert first_action["recommendation_id"] == "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    assert first_action["evidence_values"] == {
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
    assert first_action["missing_evidence_fields"] == []
    assert first_action["action_parameters"] == {
        "proposed_local_window": 6,
        "additional_local_slots": 2,
        "target_interval_start": 5,
        "target_interval_stop": 6,
        "target_interval_length": 2,
        "next_uncovered_lag_after_repair": 8,
        "still_has_gap_after_repair": True,
    }

    largest_gap = plan["action_plan"][1]
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
    assert largest_gap["missing_evidence_fields"] == []
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

    fallback = plan["action_plan"][2]
    assert fallback["recommendation_id"] == "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK"
    assert fallback["evidence_values"] == {
        "complete_repair_window": 119,
        "complete_repair_window_additional_local_slots": 115,
        "complete_repair_window_covers_context": True,
        "complete_repair_window_uses_dense_threshold": True,
        "local_window_complete_threshold_is_exact_local_minimum": True,
        "complete_repair_window_minimal_for_declared_stride_family": True,
        "complete_repair_window_minimal_witness_lag": 119,
    }
    assert fallback["action_parameters"] == {
        "proposed_local_window": 119,
        "additional_local_slots": 115,
    }

    interval_path = plan["action_plan"][3]
    assert interval_path["recommendation_id"] == "SPARSE-INTERVAL-REPAIR-PATH"
    assert interval_path["evidence_values"]["interval_repair_plan_step_count"] == 6
    assert interval_path["evidence_values"]["interval_repair_plan_final_window"] == 119
    assert interval_path["evidence_values"]["interval_repair_plan_covers_context"] is True
    assert (
        interval_path["evidence_values"]["interval_repair_plan_strictly_progresses"]
        is True
    )
    assert interval_path["action_parameters"] == {
        "step_count": 6,
        "final_local_window": 119,
        "covers_context_after_final_step": True,
        "strictly_progresses": True,
    }


def test_consumer_planner_action_plan_filters_recommendation_ids() -> None:
    pack = build_contract_pack()

    plan = planner_action_plan(
        pack,
        ["sparse_attention_coverage", "rope_position_distinguishability"],
        recommendation_ids=(
            "ROPE-USE-D19-MARGIN-FRONTIER",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        ),
        include_values=True,
    )

    assert plan["selected_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER",
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
    ]
    assert [action["recommendation_id"] for action in plan["action_plan"]] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert plan["planner_recommendation_count"] == 2
    assert plan["ready_recommendation_count"] == 2
    assert plan["action_plan"][0]["evidence_values"]["first_uncovered_interval_start"] == 5
    assert plan["action_plan"][1]["evidence_values"]["d19_request_context"] == 131072
    rope_action_parameters = plan["action_plan"][1]["action_parameters"]
    assert rope_action_parameters["applicable_context_range"] == {
        "min_exclusive": 103993,
        "max_inclusive": 196608,
    }
    assert rope_action_parameters["undecided_interval"] == {
        "lower_exclusive": "1/328459",
        "upper_exclusive": "1/328458",
        "width": "1/107884986222",
    }
    assert [
        region["region"]
        for region in rope_action_parameters["classifier_regions"]
    ] == ["proved", "undecided_margin_gap", "impossible"]
    assert rope_action_parameters["classifier_regions"][0]["theorem_ids"] == [
        "AIRA-T0216",
        "AIRA-T0217",
        "AIRA-T0233",
    ]
    assert rope_action_parameters["classifier_regions"][1][
        "theorem_backed_classification"
    ] is False
    assert rope_action_parameters["classifier_regions"][1][
        "theorem_backed_region"
    ] is True
    assert rope_action_parameters["classifier_regions"][2]["condition"] == (
        "1/328458 <= requested_margin"
    )


def test_consumer_planner_action_plan_rejects_missing_recommendation_id() -> None:
    pack = build_contract_pack()

    try:
        planner_action_plan(
            pack,
            ["sparse_attention_coverage"],
            recommendation_ids=("ROPE-USE-D19-MARGIN-FRONTIER",),
        )
    except ContractConsumerError as exc:
        assert "missing requested planner recommendations" in str(exc)
        assert "ROPE-USE-D19-MARGIN-FRONTIER" in str(exc)
    else:
        raise AssertionError("expected missing recommendation id to fail")


def test_consumer_digest_exposes_recurrence_work_budget_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "recurrence_schedule",
        fields=(
            "total_active_token_work",
            "total_inactive_token_work",
            "full_loop_token_work",
            "scheduled_work_saving",
            "scheduled_work_saving_accounting",
            "active_inactive_work_accounting",
            "scheduled_work_saving_matches_inactive_work",
            "scheduled_work_saving_positive",
            "active_work_below_full_loop_work",
            "scheduled_work_saving_positive_iff_active_work_shortfall",
            "scheduled_work_saving_zero",
            "active_work_equals_full_loop_work",
            "scheduled_work_saving_zero_iff_no_active_work_shortfall",
            "default_fixture_5_8_5_total_active_token_work",
            "default_fixture_5_8_5_total_inactive_token_work",
            "default_fixture_8_5_full_loop_token_work",
            "default_fixture_5_8_5_scheduled_work_saving",
            "default_fixture_5_8_5_work_saving_accounting",
            "default_fixture_5_8_5_active_inactive_work_accounting",
            "default_fixture_5_8_5_work_saving_matches_inactive_work",
            "post_period_extension_horizon_steps",
            "post_period_extension_total_active_token_work",
            "post_period_extension_total_inactive_token_work",
            "post_period_extension_full_loop_token_work",
            "post_period_extension_scheduled_work_saving",
            "post_period_extension_active_work_unchanged",
            "post_period_extension_inactive_work_added_token_count",
            "post_period_extension_saving_added_token_count",
            "default_fixture_5_8_6_total_active_token_work",
            "default_fixture_5_8_6_scheduled_work_saving",
            "default_fixture_5_8_6_active_work_unchanged",
            "default_fixture_5_8_6_saving_added_token_count",
            "post_period_extra_steps",
            "post_period_multi_extension_horizon_steps",
            "post_period_multi_extension_total_active_token_work",
            "post_period_multi_extension_total_inactive_token_work",
            "post_period_multi_extension_full_loop_token_work",
            "post_period_multi_extension_scheduled_work_saving",
            "post_period_multi_extension_active_work_unchanged",
            "post_period_multi_extension_inactive_work_added_extra_token_count",
            "post_period_multi_extension_saving_added_extra_token_count",
            "default_fixture_5_8_8_total_active_token_work",
            "default_fixture_5_8_8_scheduled_work_saving",
            "default_fixture_5_8_8_active_work_unchanged",
            "default_fixture_5_8_8_saving_added_extra_token_count",
            "periodic_shift_base_token",
            "periodic_shift_passes",
            "periodic_shift_amount",
            "periodic_shifted_token",
            "periodic_shift_required_steps_invariant",
            "periodic_shift_recurrence_budget_invariant",
            "periodic_shift_training_free_budget_invariant",
            "periodic_shift_exit_step_invariant",
            "periodic_shift_overthinking_boundary_invariant",
            "periodic_shift_active_step",
            "periodic_shift_active_at_step_invariant",
        ),
    )

    assert digest["evidence_fields"] == {
        "total_active_token_work": 21,
        "total_inactive_token_work": 19,
        "full_loop_token_work": 40,
        "scheduled_work_saving": 19,
        "scheduled_work_saving_accounting": True,
        "active_inactive_work_accounting": True,
        "scheduled_work_saving_matches_inactive_work": True,
        "scheduled_work_saving_positive": True,
        "active_work_below_full_loop_work": True,
        "scheduled_work_saving_positive_iff_active_work_shortfall": True,
        "scheduled_work_saving_zero": False,
        "active_work_equals_full_loop_work": False,
        "scheduled_work_saving_zero_iff_no_active_work_shortfall": True,
        "default_fixture_5_8_5_total_active_token_work": 21,
        "default_fixture_5_8_5_total_inactive_token_work": 19,
        "default_fixture_8_5_full_loop_token_work": 40,
        "default_fixture_5_8_5_scheduled_work_saving": 19,
        "default_fixture_5_8_5_work_saving_accounting": True,
        "default_fixture_5_8_5_active_inactive_work_accounting": True,
        "default_fixture_5_8_5_work_saving_matches_inactive_work": True,
        "post_period_extension_horizon_steps": 6,
        "post_period_extension_total_active_token_work": 21,
        "post_period_extension_total_inactive_token_work": 27,
        "post_period_extension_full_loop_token_work": 48,
        "post_period_extension_scheduled_work_saving": 27,
        "post_period_extension_active_work_unchanged": True,
        "post_period_extension_inactive_work_added_token_count": True,
        "post_period_extension_saving_added_token_count": True,
        "default_fixture_5_8_6_total_active_token_work": 21,
        "default_fixture_5_8_6_scheduled_work_saving": 27,
        "default_fixture_5_8_6_active_work_unchanged": True,
        "default_fixture_5_8_6_saving_added_token_count": True,
        "post_period_extra_steps": 3,
        "post_period_multi_extension_horizon_steps": 8,
        "post_period_multi_extension_total_active_token_work": 21,
        "post_period_multi_extension_total_inactive_token_work": 43,
        "post_period_multi_extension_full_loop_token_work": 64,
        "post_period_multi_extension_scheduled_work_saving": 43,
        "post_period_multi_extension_active_work_unchanged": True,
        "post_period_multi_extension_inactive_work_added_extra_token_count": True,
        "post_period_multi_extension_saving_added_extra_token_count": True,
        "default_fixture_5_8_8_total_active_token_work": 21,
        "default_fixture_5_8_8_scheduled_work_saving": 43,
        "default_fixture_5_8_8_active_work_unchanged": True,
        "default_fixture_5_8_8_saving_added_extra_token_count": True,
        "periodic_shift_base_token": 7,
        "periodic_shift_passes": 3,
        "periodic_shift_amount": 15,
        "periodic_shifted_token": 22,
        "periodic_shift_required_steps_invariant": True,
        "periodic_shift_recurrence_budget_invariant": True,
        "periodic_shift_training_free_budget_invariant": True,
        "periodic_shift_exit_step_invariant": True,
        "periodic_shift_overthinking_boundary_invariant": True,
        "periodic_shift_active_step": 2,
        "periodic_shift_active_at_step_invariant": True,
    }
    assert "AIM-T0026" in digest["theorem_ids"]
    assert "AIM-T0027" in digest["theorem_ids"]
    assert "AIM-T0028" in digest["theorem_ids"]
    assert "AIM-T0029" in digest["theorem_ids"]
    assert "AIM-T0030" in digest["theorem_ids"]
    assert "AIM-T0033" in digest["theorem_ids"]
    assert "AIM-T0034" in digest["theorem_ids"]
    assert "AIM-T0130" in digest["theorem_ids"]
    assert "AIM-T0135" in digest["theorem_ids"]
    assert "AIM-T0138" in digest["theorem_ids"]
    assert "AIM-T0139" in digest["theorem_ids"]
    assert "AIM-T0144" in digest["theorem_ids"]
    assert "AIM-T0145" in digest["theorem_ids"]
    assert "AIM-T0146" in digest["theorem_ids"]
    assert "AIM-T0147" in digest["theorem_ids"]
    assert "AIM-T0140" in digest["theorem_ids"]
    assert "AIM-T0141" in digest["theorem_ids"]
    assert "AIM-T0142" in digest["theorem_ids"]
    assert "AIM-T0143" in digest["theorem_ids"]
    assert "AIM-T0150" in digest["theorem_ids"]
    assert "AIM-T0151" in digest["theorem_ids"]
    assert "AIM-T0152" in digest["theorem_ids"]
    assert "AIM-T0153" in digest["theorem_ids"]
    assert "AIM-T0154" in digest["theorem_ids"]
    assert "AIM-T0155" in digest["theorem_ids"]
    assert "AIM-T0156" in digest["theorem_ids"]
    assert "AIM-T0157" in digest["theorem_ids"]
    assert "AIM-T0158" in digest["theorem_ids"]
    assert "AIM-T0159" in digest["theorem_ids"]


def test_consumer_digest_exposes_sparse_first_gap_repair_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "sparse_attention_coverage",
        fields=(
            "first_uncovered_lag",
            "first_uncovered_interval_start",
            "first_uncovered_interval_stop",
            "first_uncovered_interval_length",
            "local_window_needed_to_cover_first_uncovered_interval",
            "first_uncovered_interval_additional_local_slots",
            "first_uncovered_interval_repair_reaches_interval",
            "first_interval_repair_next_uncovered_lag",
            "first_interval_repair_still_has_gap",
            "first_interval_repair_covers_context",
            "largest_uncovered_interval_start",
            "largest_uncovered_interval_stop",
            "largest_uncovered_interval_length",
            "local_window_needed_to_cover_largest_uncovered_interval",
            "largest_uncovered_interval_additional_local_slots",
            "largest_uncovered_interval_repair_reaches_interval",
            "largest_interval_repair_next_uncovered_lag",
            "largest_interval_repair_still_has_gap",
            "largest_interval_repair_covers_context",
            "largest_uncovered_interval_is_tail",
            "first_gap_local_window_shortfall",
            "local_window_needed_to_cover_first_gap",
            "current_window_below_first_gap",
            "first_gap_repair_window_reaches",
            "first_gap_repair_window_covers_context",
            "first_gap_repair_window_is_final_positive_lag",
            "first_gap_repair_threshold_matches_final_lag",
            "local_window_complete_coverage_threshold",
            "local_window_complete_coverage_shortfall",
            "local_window_reaches_complete_coverage_threshold",
            "local_window_threshold_certifies_complete",
            "local_window_complete_threshold_is_exact_local_minimum",
            "complete_repair_window",
            "complete_repair_window_additional_local_slots",
            "complete_repair_window_covers_context",
            "complete_repair_window_uses_dense_threshold",
            "complete_repair_window_minimal_for_declared_stride_family",
            "complete_repair_window_minimal_witness_lag",
            "first_gap_repair_window_reaches_complete_threshold",
        ),
    )

    assert digest["evidence_fields"] == {
        "first_uncovered_lag": 5,
        "first_uncovered_interval_start": 5,
        "first_uncovered_interval_stop": 6,
        "first_uncovered_interval_length": 2,
        "local_window_needed_to_cover_first_uncovered_interval": 6,
        "first_uncovered_interval_additional_local_slots": 2,
        "first_uncovered_interval_repair_reaches_interval": True,
        "first_interval_repair_next_uncovered_lag": 8,
        "first_interval_repair_still_has_gap": True,
        "first_interval_repair_covers_context": False,
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
        "first_gap_local_window_shortfall": 1,
        "local_window_needed_to_cover_first_gap": 5,
        "current_window_below_first_gap": True,
        "first_gap_repair_window_reaches": True,
        "first_gap_repair_window_covers_context": False,
        "first_gap_repair_window_is_final_positive_lag": False,
        "first_gap_repair_threshold_matches_final_lag": True,
        "local_window_complete_coverage_threshold": 119,
        "local_window_complete_coverage_shortfall": 115,
        "local_window_reaches_complete_coverage_threshold": False,
        "local_window_threshold_certifies_complete": False,
        "local_window_complete_threshold_is_exact_local_minimum": True,
        "complete_repair_window": 119,
        "complete_repair_window_additional_local_slots": 115,
        "complete_repair_window_covers_context": True,
        "complete_repair_window_uses_dense_threshold": True,
        "complete_repair_window_minimal_for_declared_stride_family": True,
        "complete_repair_window_minimal_witness_lag": 119,
        "first_gap_repair_window_reaches_complete_threshold": False,
    }
    assert "AIT-T0161" in digest["theorem_ids"]
    assert "AIT-T0162" in digest["theorem_ids"]
    assert "AIT-T0163" in digest["theorem_ids"]
    assert "AIT-T0164" in digest["theorem_ids"]
    assert "AIT-T0165" in digest["theorem_ids"]
    assert "AIT-T0166" in digest["theorem_ids"]
    assert "AIT-T0167" in digest["theorem_ids"]
    assert "AIT-T0168" in digest["theorem_ids"]
    assert "AIT-T0169" in digest["theorem_ids"]
    assert "AIT-T0170" in digest["theorem_ids"]
    assert "AIT-T0171" in digest["theorem_ids"]
    assert "AIT-T0172" in digest["theorem_ids"]


def test_consumer_exposes_sparse_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "sparse_attention_coverage")

    assert len(recommendations) == 4
    first_interval = recommendations[0]
    assert first_interval["id"] == "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    assert first_interval["coverage_scope"] == "first_uncovered_interval_only"
    assert first_interval["proposed_local_window"] == 6
    assert first_interval["additional_local_slots"] == 2
    assert first_interval["target_interval_start"] == 5
    assert first_interval["target_interval_stop"] == 6
    assert first_interval["next_uncovered_lag_after_repair"] == 8
    assert first_interval["still_has_gap_after_repair"] is True
    assert first_interval["theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0171",
        "AIT-T0166",
        "AIT-T0167",
    ]
    assert "not a complete" in first_interval["not_claimed"]

    largest_gap = recommendations[1]
    assert largest_gap["id"] == "SPARSE-REPAIR-LARGEST-GAP-INTERVAL"
    assert largest_gap["coverage_scope"] == "largest_uncovered_interval"
    assert largest_gap["proposed_local_window"] == 119
    assert largest_gap["additional_local_slots"] == 115
    assert largest_gap["target_interval_start"] == 40
    assert largest_gap["target_interval_stop"] == 119
    assert largest_gap["target_interval_length"] == 80
    assert largest_gap["next_uncovered_lag_after_repair"] is None
    assert largest_gap["still_has_gap_after_repair"] is False
    assert largest_gap["covers_context_after_repair"] is True
    assert largest_gap["largest_interval_is_tail"] is True
    assert largest_gap["theorem_ids"] == ["AIT-T0094", "AIT-T0104", "AIT-T0171"]
    assert "largest reported gap interval" in largest_gap["not_claimed"]

    fallback = recommendations[2]
    assert fallback["id"] == "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK"
    assert fallback["coverage_scope"] == "all_positive_lags"
    assert fallback["proposed_local_window"] == 119
    assert fallback["additional_local_slots"] == 115
    assert fallback["theorem_ids"] == [
        "AIT-T0023",
        "AIT-T0034",
        "AIT-T0172",
        "AIT-T0168",
        "AIT-T0169",
        "AIT-T0170",
    ]
    assert "not a claim" in fallback["not_claimed"]

    interval_path = recommendations[3]
    assert interval_path["id"] == "SPARSE-INTERVAL-REPAIR-PATH"
    assert interval_path["coverage_scope"] == "successive_first_uncovered_intervals"
    assert interval_path["step_count"] == 6
    assert interval_path["final_local_window"] == 119
    assert interval_path["covers_context_after_final_step"] is True
    assert interval_path["strictly_progresses"] is True
    assert interval_path["theorem_ids"] == ["AIT-T0094", "AIT-T0104", "AIT-T0171"]
    assert "not a search over all sparse layouts" in interval_path["not_claimed"]


def test_consumer_exposes_kv_cache_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "kv_cache_ring_buffer")

    assert len(recommendations) == 2
    stale = recommendations[0]
    assert stale["id"] == "KV-DROP-STALE-REQUEST-TOKEN"
    assert stale["coverage_scope"] == "modeled_adapter_request_stale_probe"
    assert stale["target_token"] == 12
    assert stale["next_same_slot_overwrite_token"] == 28
    assert stale["stale_requested_count"] == 1
    assert stale["theorem_ids"] == ["AIM-T0097", "AIM-T0103"]
    assert "not a kernel" in stale["not_claimed"]

    sink = recommendations[1]
    assert sink["id"] == "KV-USE-SINK-ROLLING-WINDOW-REQUEST"
    assert sink["coverage_scope"] == "pinned_seen_prefix_plus_rolling_live_window"
    assert sink["sink_size"] == 4
    assert sink["cache_size"] == 16
    assert sink["current"] == 31
    assert sink["request_token_count"] == 20
    assert sink["theorem_ids"] == [
        "AIM-T0104",
        "AIM-T0110",
        "AIM-T0117",
        "AIM-T0136",
        "AIM-T0137",
        "AIM-T0148",
        "AIM-T0149",
    ]
    assert "does not prove" in sink["not_claimed"]


def test_consumer_exposes_recurrence_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "recurrence_schedule")

    assert len(recommendations) == 2
    work_schedule = recommendations[0]
    assert work_schedule["id"] == "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE"
    assert work_schedule["coverage_scope"] == "finite_default_loop_schedule_fixture"
    assert work_schedule["loop_period"] == 5
    assert work_schedule["token_count"] == 8
    assert work_schedule["horizon_steps"] == 5
    assert work_schedule["active_token_count_trace"] == [8, 6, 4, 2, 1]
    assert work_schedule["inactive_token_count_trace"] == [0, 2, 4, 6, 7]
    assert work_schedule["active_token_work"] == 21
    assert work_schedule["inactive_token_work"] == 19
    assert work_schedule["full_loop_token_work"] == 40
    assert work_schedule["scheduled_work_saving"] == 19
    assert work_schedule["post_period_extension_horizon_steps"] == 6
    assert work_schedule["post_period_extension_scheduled_work_saving"] == 27
    assert work_schedule["post_period_extra_steps"] == 3
    assert work_schedule["post_period_multi_extension_horizon_steps"] == 8
    assert work_schedule["post_period_multi_extension_scheduled_work_saving"] == 43
    assert "AIM-T0138" in work_schedule["theorem_ids"]
    assert "AIM-T0150" in work_schedule["theorem_ids"]
    assert "AIM-T0154" in work_schedule["theorem_ids"]
    assert "AIM-T0155" in work_schedule["theorem_ids"]
    assert "AIM-T0159" in work_schedule["theorem_ids"]
    assert "not a runtime" in work_schedule["not_claimed"]

    shift_reuse = recommendations[1]
    assert shift_reuse["id"] == "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT"
    assert shift_reuse["coverage_scope"] == "whole_loop_period_token_shift_fixture"
    assert shift_reuse["base_token"] == 7
    assert shift_reuse["shift_passes"] == 3
    assert shift_reuse["shift_amount"] == 15
    assert shift_reuse["shifted_token"] == 22
    assert shift_reuse["active_step"] == 2
    assert shift_reuse["theorem_ids"] == [
        "AIM-T0026",
        "AIM-T0027",
        "AIM-T0028",
        "AIM-T0029",
        "AIM-T0030",
        "AIM-T0033",
        "AIM-T0034",
        "AIM-T0036",
    ]
    assert "not a proof" in shift_reuse["not_claimed"]


def test_consumer_exposes_seed_rule_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "seed_rule_exact_regeneration")

    assert len(recommendations) == 2
    exact_recipe = recommendations[0]
    assert exact_recipe["id"] == "SEED-RULE-USE-EXACT-REGENERATION-RECIPE"
    assert exact_recipe["coverage_scope"] == "public_finite_circle_fixture"
    assert exact_recipe["artifact_id"] == "finite_circle"
    assert exact_recipe["fixture_n"] == 128
    assert exact_recipe["rule_ids"] == ["enumerate_nodes"]
    assert exact_recipe["generated_object_length"] == 128
    assert exact_recipe["theorem_ids"] == [
        "GEN-T0040",
        "GEN-T0041",
        "GEN-T0043",
    ]
    assert "not a universal generator" in exact_recipe["not_claimed"]

    shorter_candidate = recommendations[1]
    assert shorter_candidate["id"] == (
        "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE"
    )
    assert shorter_candidate["coverage_scope"] == "declared_finite_candidate_search"
    assert shorter_candidate["search_id"] == "public_seed_rule_finite_circle_search"
    assert shorter_candidate["candidate_count"] == 3
    assert shorter_candidate["exact_candidate_count"] == 2
    assert shorter_candidate["best_shorter_artifact_id"] == "finite_circle"
    assert shorter_candidate["best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert shorter_candidate["candidate_ids_by_generator_length"] == [
        "finite_circle_unit_fixture",
        "finite_circle_broken_fixture",
        "finite_circle_public_fixture",
    ]
    assert shorter_candidate["storage_saving"] == 71
    assert "GEN-T0046" in shorter_candidate["theorem_ids"]
    assert "not a global optimality" in shorter_candidate["not_claimed"]


def test_consumer_exposes_cyclic_memory_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "cyclic_memory_residue_winding")

    assert len(recommendations) == 2
    alias_provenance = recommendations[0]
    assert alias_provenance["id"] == "MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE"
    assert alias_provenance["coverage_scope"] == (
        "finite_same_residue_alias_class_fixture"
    )
    assert alias_provenance["bank_size"] == 8
    assert alias_provenance["event_index"] == 23
    assert alias_provenance["residue_slot"] == 7
    assert alias_provenance["winding"] == 2
    assert alias_provenance["alias_count"] == 4
    assert alias_provenance["theorem_ids"] == [
        "AIM-T0001",
        "AIM-T0002",
        "AIM-T0004",
    ]
    assert "not a retrieval-quality" in alias_provenance["not_claimed"]

    alias_load = recommendations[1]
    assert alias_load["id"] == "MEMORY-AUDIT-FINITE-ALIAS-LOAD"
    assert alias_load["coverage_scope"] == "declared_finite_trace_slot_loads"
    assert alias_load["bank_size"] == 8
    assert alias_load["event_count"] == 32
    assert alias_load["max_alias_load"] == 4
    assert alias_load["slot_loads"] == [4, 4, 4, 4, 4, 4, 4, 4]
    assert alias_load["theorem_ids"] == ["AIM-T0001", "AIM-T0005"]
    assert "not a throughput" in alias_load["not_claimed"]


def test_consumer_digest_can_include_sparse_recommendations() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "sparse_attention_coverage",
        fields=("first_uncovered_lag",),
        include_recommendations=True,
    )

    assert digest["evidence_fields"] == {"first_uncovered_lag": 5}
    assert [
        recommendation["id"]
        for recommendation in digest["planner_recommendations"]
    ] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
    ]


def test_consumer_rejects_recommendation_with_unknown_evidence_field() -> None:
    pack = build_contract_pack()
    contract = require_ready_contract(pack, "sparse_attention_coverage")
    contract["planner_recommendations"][0]["evidence_fields"].append("missing_field")

    failures = validate_consumer_pack(pack)

    assert any("unknown evidence fields" in failure for failure in failures)


def test_consumer_digest_exposes_strided_candidate_fanout_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "strided_candidate_fanout",
        fields=(
            "context_length",
            "stride",
            "gcd",
            "predicted_reach",
            "full_coverage",
            "candidate_budget",
            "unique_candidate_count",
            "effective_candidate_budget",
            "duplicate_count",
            "candidate_budget_accounting",
            "effective_budget_matches_unique_candidates",
            "candidate_budget_shortfall",
            "effective_budget_reaches_predicted_reach",
        ),
    )

    assert digest["evidence_fields"] == {
        "context_length": 12,
        "stride": 5,
        "gcd": 1,
        "predicted_reach": 12,
        "full_coverage": True,
        "candidate_budget": 12,
        "unique_candidate_count": 12,
        "effective_candidate_budget": 12,
        "duplicate_count": 0,
        "candidate_budget_accounting": True,
        "effective_budget_matches_unique_candidates": True,
        "candidate_budget_shortfall": 0,
        "effective_budget_reaches_predicted_reach": True,
    }
    assert "AIT-T0001" in digest["theorem_ids"]
    assert "AIT-T0002" in digest["theorem_ids"]
    assert "AIT-T0003" in digest["theorem_ids"]
    assert "AIT-T0173" in digest["theorem_ids"]


def test_consumer_exposes_strided_fanout_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "strided_candidate_fanout")

    assert len(recommendations) == 2
    full_cycle = recommendations[0]
    assert full_cycle["id"] == "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE"
    assert full_cycle["coverage_scope"] == "finite_coprime_stride_orbit_fixture"
    assert full_cycle["context_length"] == 12
    assert full_cycle["stride"] == 5
    assert full_cycle["gcd"] == 1
    assert full_cycle["predicted_reach"] == 12
    assert full_cycle["full_coverage"] is True
    assert full_cycle["theorem_ids"] == [
        "AIT-T0001",
        "AIT-T0002",
        "AIT-T0003",
    ]
    assert "not a search" in full_cycle["not_claimed"]

    budget_audit = recommendations[1]
    assert budget_audit["id"] == "FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET"
    assert budget_audit["coverage_scope"] == "declared_fixed_budget_candidate_path"
    assert budget_audit["candidate_budget"] == 12
    assert budget_audit["unique_candidate_count"] == 12
    assert budget_audit["effective_candidate_budget"] == 12
    assert budget_audit["duplicate_count"] == 0
    assert budget_audit["candidate_budget_shortfall"] == 0
    assert budget_audit["theorem_ids"] == [
        "AIT-T0001",
        "AIT-T0002",
        "AIT-T0173",
    ]
    assert "not a ranking" in budget_audit["not_claimed"]


def test_consumer_digest_exposes_seed_rule_bounded_search_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "seed_rule_exact_regeneration",
        fields=(
            "bounded_search_candidate_count",
            "bounded_search_exact_candidate_count",
            "bounded_search_exact_candidate_count_le_candidate_count",
            "bounded_search_has_best_exact",
            "bounded_search_best_exact_exists_iff_exact_count_positive",
            "bounded_search_best_exact_implies_candidate_count_positive",
            "bounded_search_best_exact_candidate_id",
            "bounded_search_best_exact_regenerates",
            "bounded_search_has_best_shorter",
            "bounded_search_best_shorter_candidate_id",
            "bounded_search_best_shorter_generator_shorter",
            "bounded_search_candidate_ids_by_generator_length",
            "bounded_search_exact_candidate_ids_by_generator_length",
            "bounded_search_shorter_candidate_ids_by_generator_length",
        ),
    )

    assert digest["evidence_fields"] == {
        "bounded_search_candidate_count": 3,
        "bounded_search_exact_candidate_count": 2,
        "bounded_search_exact_candidate_count_le_candidate_count": True,
        "bounded_search_has_best_exact": True,
        "bounded_search_best_exact_exists_iff_exact_count_positive": True,
        "bounded_search_best_exact_implies_candidate_count_positive": True,
        "bounded_search_best_exact_candidate_id": "finite_circle_unit_fixture",
        "bounded_search_best_exact_regenerates": True,
        "bounded_search_has_best_shorter": True,
        "bounded_search_best_shorter_candidate_id": (
            "finite_circle_public_fixture"
        ),
        "bounded_search_best_shorter_generator_shorter": True,
        "bounded_search_candidate_ids_by_generator_length": [
            "finite_circle_unit_fixture",
            "finite_circle_broken_fixture",
            "finite_circle_public_fixture",
        ],
        "bounded_search_exact_candidate_ids_by_generator_length": [
            "finite_circle_unit_fixture",
            "finite_circle_public_fixture",
        ],
        "bounded_search_shorter_candidate_ids_by_generator_length": [
            "finite_circle_public_fixture"
        ],
    }
    assert "GEN-T0037" in digest["theorem_ids"]
    assert "GEN-T0044" in digest["theorem_ids"]
    assert "GEN-T0045" in digest["theorem_ids"]


def test_consumer_digest_exposes_cyclic_memory_alias_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "cyclic_memory_residue_winding",
        fields=(
            "bank_size",
            "event_index",
            "event_count",
            "residue_slot",
            "winding",
            "same_residue_events",
            "same_residue_windings",
            "max_alias_load",
        ),
    )

    assert digest["evidence_fields"] == {
        "bank_size": 8,
        "event_index": 23,
        "event_count": 32,
        "residue_slot": 7,
        "winding": 2,
        "same_residue_events": [7, 15, 23, 31],
        "same_residue_windings": [0, 1, 2, 3],
        "max_alias_load": 4,
    }
    assert "AIM-T0001" in digest["theorem_ids"]
    assert "AIM-T0002" in digest["theorem_ids"]
    assert "AIM-T0004" in digest["theorem_ids"]
    assert "AIM-T0005" in digest["theorem_ids"]


def test_consumer_digest_exposes_multicoil_phase_feature_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "multicoil_phase_feature",
        fields=(
            "periods",
            "position",
            "phase_tuple",
            "joint_repeat_horizon",
            "shifted_position",
            "shifted_phase_tuple",
            "relative_period",
            "relative_phase",
            "shifted_relative_phase",
        ),
    )

    assert digest["evidence_fields"] == {
        "periods": [5, 7],
        "position": 37,
        "phase_tuple": [2, 2],
        "joint_repeat_horizon": 35,
        "shifted_position": 72,
        "shifted_phase_tuple": [2, 2],
        "relative_period": 5,
        "relative_phase": 3,
        "shifted_relative_phase": 3,
    }
    assert "AIA-T0001" in digest["theorem_ids"]
    assert "AIA-T0002" in digest["theorem_ids"]
    assert "AIA-T0004" in digest["theorem_ids"]
    assert "AIT-T0004" in digest["theorem_ids"]
    assert "AIT-T0005" in digest["theorem_ids"]


def test_consumer_exposes_multicoil_phase_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "multicoil_phase_feature")

    assert len(recommendations) == 2
    joint_repeat = recommendations[0]
    assert joint_repeat["id"] == "PHASE-USE-JOINT-REPEAT-HORIZON"
    assert joint_repeat["coverage_scope"] == "declared_finite_period_bank_fixture"
    assert joint_repeat["periods"] == [5, 7]
    assert joint_repeat["position"] == 37
    assert joint_repeat["phase_tuple"] == [2, 2]
    assert joint_repeat["joint_repeat_horizon"] == 35
    assert joint_repeat["shifted_position"] == 72
    assert joint_repeat["shifted_phase_tuple"] == [2, 2]
    assert joint_repeat["theorem_ids"] == [
        "AIA-T0001",
        "AIA-T0002",
        "AIA-T0004",
    ]
    assert "not a learned-embedding" in joint_repeat["not_claimed"]

    relative = recommendations[1]
    assert relative["id"] == "PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT"
    assert relative["coverage_scope"] == "declared_query_key_relative_phase_fixture"
    assert relative["query_position"] == 41
    assert relative["key_position"] == 18
    assert relative["relative_period"] == 5
    assert relative["relative_phase"] == 3
    assert relative["shifted_relative_phase"] == 3
    assert relative["theorem_ids"] == [
        "AIT-T0004",
        "AIT-T0005",
    ]
    assert "not an attention quality" in relative["not_claimed"]


def test_consumer_digest_exposes_circulant_block_cyclic_mixer_fields() -> None:
    pack = build_contract_pack()

    digest = contract_digest(
        pack,
        "circulant_block_cyclic_mixer",
        fields=(
            "period",
            "circulant_output",
            "dense_output",
            "max_abs_dense_delta",
            "circulant_parameters",
            "dense_parameters",
            "block_cyclic_parameters",
            "block_to_dense_ratio",
            "block_loads",
        ),
    )

    assert digest["evidence_fields"] == {
        "period": 8,
        "circulant_output": [5, -2, -8, 9, -1, 6, -1, -8],
        "dense_output": [5, -2, -8, 9, -1, 6, -1, -8],
        "max_abs_dense_delta": 0,
        "circulant_parameters": 8,
        "dense_parameters": 64,
        "block_cyclic_parameters": 128,
        "block_to_dense_ratio": 0.0625,
        "block_loads": [16, 16, 16, 16, 16, 16, 16, 16],
    }
    assert "AIT-T0006" in digest["theorem_ids"]
    assert "AIT-T0007" in digest["theorem_ids"]
    assert "AIT-T0008" in digest["theorem_ids"]
    assert "AIT-T0009" in digest["theorem_ids"]
    assert "AIRA-T0001" in digest["theorem_ids"]
    assert "AIRA-T0002" in digest["theorem_ids"]
    assert "AIRA-T0004" in digest["theorem_ids"]


def test_consumer_exposes_circulant_mixer_planner_recommendations() -> None:
    pack = build_contract_pack()

    recommendations = contract_recommendations(pack, "circulant_block_cyclic_mixer")

    assert len(recommendations) == 2
    dense_parity = recommendations[0]
    assert dense_parity["id"] == "MIXER-AUDIT-CIRCULANT-DENSE-PARITY"
    assert dense_parity["coverage_scope"] == "deterministic_circulant_fixture"
    assert dense_parity["period"] == 8
    assert dense_parity["max_abs_dense_delta"] == 0
    assert dense_parity["circulant_parameters"] == 8
    assert dense_parity["dense_parameters"] == 64
    assert dense_parity["circulant_parameter_ratio"] == 0.125
    assert dense_parity["theorem_ids"] == [
        "AIT-T0006",
        "AIT-T0007",
        "AIT-T0008",
        "AIT-T0009",
    ]
    assert "not a speed" in dense_parity["not_claimed"]

    block_budget = recommendations[1]
    assert block_budget["id"] == "MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET"
    assert block_budget["coverage_scope"] == "declared_block_cyclic_adapter_fixture"
    assert block_budget["channel_count"] == 128
    assert block_budget["block_size"] == 8
    assert block_budget["dense_adapter_parameters"] == 2048
    assert block_budget["lora_parameters"] == 576
    assert block_budget["block_cyclic_parameters"] == 128
    assert block_budget["block_to_dense_ratio"] == 0.0625
    assert block_budget["theorem_ids"] == [
        "AIRA-T0001",
        "AIRA-T0002",
        "AIRA-T0004",
    ]
    assert "not a LoRA replacement" in block_budget["not_claimed"]


def test_consumer_adapter_rejects_not_ready_contract() -> None:
    pack = build_contract_pack()
    contract = next(
        item for item in pack["contracts"]
        if item["kind"] == "seed_rule_exact_regeneration"
    )
    contract["contract_passed"] = False
    contract["consumer_check"]["ready_for_downstream_fixture_use"] = False
    readiness = pack["contract_readiness_index"]["seed_rule_exact_regeneration"]
    readiness["ready_for_downstream_fixture_use"] = False
    readiness["contract_passed"] = False
    for recommendation in contract["planner_recommendations"]:
        pack["planner_recommendation_index"][recommendation["id"]][
            "ready_for_downstream_fixture_use"
        ] = False
    _refresh_fingerprints(pack)

    with pytest.raises(ContractNotReadyError, match="contract_passed is false"):
        require_ready_contract(pack, "seed_rule_exact_regeneration")


def test_consumer_adapter_detects_readiness_index_drift() -> None:
    pack = build_contract_pack()
    broken = deepcopy(pack)
    broken["contract_readiness_index"]["kv_cache_ring_buffer"][
        "all_theorem_ids_proved"
    ] = False

    failures = validate_consumer_pack(broken)

    assert any("readiness index all_theorem_ids_proved drifted" in failure for failure in failures)
    with pytest.raises(ContractPackSchemaError, match="invalid Circle AI contract pack"):
        readiness_summary(broken, "kv_cache_ring_buffer")


def test_consumer_adapter_rejects_duplicate_recommendation_ids() -> None:
    pack = build_contract_pack()
    duplicate_id = pack["contracts"][0]["planner_recommendations"][0]["id"]
    for contract in pack["contracts"]:
        if contract["kind"] == "sparse_attention_coverage":
            contract["planner_recommendations"][0]["id"] = duplicate_id
            break
    _refresh_fingerprints(pack)

    failures = validate_consumer_pack(pack)

    assert any(
        "duplicate planner recommendation id" in failure
        and duplicate_id in failure
        for failure in failures
    )
    with pytest.raises(
        ContractPackSchemaError,
        match="duplicate planner recommendation id",
    ):
        planner_recommendation_index(pack)


def test_consumer_adapter_detects_recommendation_index_drift() -> None:
    pack = build_contract_pack()
    broken = deepcopy(pack)
    broken["contract_readiness_index"]["sparse_attention_coverage"][
        "planner_recommendation_count"
    ] = 0

    failures = validate_consumer_pack(broken)

    assert any(
        "readiness index planner_recommendation_count drifted" in failure
        for failure in failures
    )


def test_consumer_adapter_detects_field_catalog_drift() -> None:
    pack = build_contract_pack()
    broken = deepcopy(pack)
    broken["contract_schema"]["minimum_field_catalog_by_kind"][
        "strided_candidate_fanout"
    ]["effective_candidate_budget"]["value_kind"] = "string"

    failures = validate_consumer_pack(broken)

    assert any(
        "catalog entry effective_candidate_budget.value_kind drifted" in failure
        for failure in failures
    )
    with pytest.raises(ContractPackSchemaError, match="invalid Circle AI contract pack"):
        contract_digest(
            broken,
            "strided_candidate_fanout",
            fields=("effective_candidate_budget",),
            include_field_metadata=True,
        )


def test_consumer_adapter_rejects_unknown_kind() -> None:
    pack = build_contract_pack()

    with pytest.raises(ContractPackSchemaError, match="unknown contract kind"):
        readiness_summary(pack, "missing_contract_kind")
