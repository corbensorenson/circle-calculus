from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from circle_math.applications import (
    build_contract_receipt,
    build_contract_receipt_json_schema,
    build_contract_receipt_from_request,
    build_contract_request,
    build_contract_runner_check_json_schema,
    build_contract_request_json_schema,
    build_contract_request_validation_report,
    build_contract_request_validation_json_schema,
    build_kv_cache_receipt,
    build_recurrence_receipt,
    build_rope_request_parameters_from_model_config,
    build_rope_receipt,
    build_sparse_attention_receipt,
    validate_contract_request,
    validate_contract_receipt,
)
from circle_math.applications.circle_ai_contracts import build_contract_pack


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "circle_ai_certify.py"
STANDARD_ROPE_MODEL_CONFIG = (
    ROOT / "examples" / "circle_ai_model_configs" / "standard_rope_config.json"
)


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
    assert len(receipt["request_content_fingerprint"]) == 64
    assert len(receipt["normalized_request_fingerprint"]) == 64
    assert receipt["recommendations"]
    assert receipt["recommendations"] == receipt["support"]["planner_recommendations"]
    assert receipt["validation_commands"]
    assert receipt["validation_commands"] == receipt["support"]["validation_commands"]
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

    missing_metadata = dict(receipt)
    missing_metadata["recommendations"] = []
    missing_metadata["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(missing_metadata)
    assert any("recommendations must be a non-empty list" in failure for failure in failures)

    broken_request = dict(receipt)
    broken_request["request"] = {
        **receipt["request"],
        "parameters": {**receipt["request"]["parameters"], "context": 10},
    }
    broken_request["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(broken_request)
    assert any("request_content_fingerprint drifted" in failure for failure in failures)

    broken_normalized = dict(receipt)
    broken_normalized["normalized_request"] = {
        **receipt["normalized_request"],
        "sequence_length": 10,
    }
    broken_normalized["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(broken_normalized)
    assert any(
        "normalized_request_fingerprint drifted" in failure
        for failure in failures
    )


def test_request_api_validates_and_builds_receipts(contract_pack: dict) -> None:
    request = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse-attention",
        "parameters": {
            "context": 9,
            "strides": (2, 5),
            "path_length": 4,
            "local_window": 8,
        },
    }

    assert validate_contract_request(request) == []
    receipt = build_contract_receipt_from_request(request, pack=contract_pack)
    assert receipt["kind"] == "sparse_attention_coverage"
    assert receipt["request_passed"] is True
    assert validate_contract_receipt(receipt) == []


def test_request_api_builds_canonical_json_safe_requests() -> None:
    request = build_contract_request(
        "sparse-attention",
        {
            "context": 9,
            "strides": (2, 5),
            "path_length": 4,
            "local_window": 8,
        },
    )

    assert request == {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse_attention_coverage",
        "parameters": {
            "context": 9,
            "strides": [2, 5],
            "path_length": 4,
            "local_window": 8,
        },
    }
    assert validate_contract_request(request) == []


def test_rope_model_config_import_builds_standard_request_parameters() -> None:
    parameters = build_rope_request_parameters_from_model_config(
        {
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "rope_theta": 500000.0,
            "max_position_embeddings": 131072,
        },
        requested_margin="1/328459",
    )

    assert parameters == {
        "head_dim": 128,
        "base": 500000.0,
        "context": 131072,
        "tolerance": 1e-6,
        "discretization": "round",
        "requested_margin": "1/328459",
    }
    assert validate_contract_request(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "rope",
            "parameters": parameters,
        }
    ) == []


def test_rope_model_config_import_handles_partial_rotary_factor() -> None:
    parameters = build_rope_request_parameters_from_model_config(
        {
            "hidden_size": 1024,
            "num_attention_heads": 8,
            "max_position_embeddings": 2048,
            "partial_rotary_factor": 0.5,
        },
        base=10000.0,
        context=4096,
    )

    assert parameters["head_dim"] == 64
    assert parameters["base"] == 10000.0
    assert parameters["context"] == 4096


def test_rope_model_config_import_rejects_unproved_scaling_metadata() -> None:
    with pytest.raises(ValueError, match="rope_scaling"):
        build_rope_request_parameters_from_model_config(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "rope_theta": 500000.0,
                "max_position_embeddings": 131072,
                "rope_scaling": {"rope_type": "llama3", "factor": 8.0},
            }
        )


def test_request_api_reports_malformed_requests() -> None:
    missing_parameters = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
    }
    wrong_schema = {
        "schema_id": "wrong",
        "kind": "rope",
        "parameters": {},
    }
    unsupported = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "unknown",
        "parameters": {},
    }
    missing_kv_parameters = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "kv-cache",
        "parameters": {},
    }
    invalid_rope_margin = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
        "parameters": {"requested_margin": "not-a-fraction"},
    }
    invalid_sparse_stride = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse-attention",
        "parameters": {
            "context": 32,
            "strides": [5, 0],
            "path_length": 16,
            "local_window": 9,
        },
    }
    typo_parameter = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"shift_presses": 3},
    }

    assert "parameters must be an object" in validate_contract_request(
        missing_parameters
    )
    assert any("schema_id" in failure for failure in validate_contract_request(wrong_schema))
    assert any(
        "supported Circle AI contract kind" in failure
        for failure in validate_contract_request(unsupported)
    )
    assert any(
        "missing required keys" in failure
        for failure in validate_contract_request(missing_kv_parameters)
    )
    assert any(
        "parse as a Fraction" in failure
        for failure in validate_contract_request(invalid_rope_margin)
    )
    assert any(
        "positive integers" in failure
        for failure in validate_contract_request(invalid_sparse_stride)
    )
    assert any(
        "unsupported keys" in failure
        for failure in validate_contract_request(typo_parameter)
    )
    assert build_contract_request_validation_report(typo_parameter) == {
        "schema_id": "circle_calculus.ai_contract_request_validation.v0",
        "request_schema_id": "circle_calculus.ai_contract_request.v0",
        "ok": False,
        "kind": "recurrence",
        "canonical_kind": "recurrence_schedule",
        "failure_count": 1,
        "failures": ["parameters contains unsupported keys: shift_presses"],
    }
    non_string_kind_report = build_contract_request_validation_report(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": 12,
            "parameters": {},
        }
    )
    assert non_string_kind_report["kind"] is None
    assert non_string_kind_report["canonical_kind"] is None
    with pytest.raises(ValueError, match="invalid Circle AI contract request"):
        build_contract_receipt_from_request(unsupported)
    with pytest.raises(ValueError, match="invalid Circle AI contract request"):
        build_contract_receipt_from_request(missing_kv_parameters)
    with pytest.raises(ValueError, match="invalid Circle AI contract request"):
        build_contract_receipt_from_request(invalid_rope_margin)


def test_request_schema_accepts_public_aliases() -> None:
    schema = build_contract_request_json_schema()

    assert schema["properties"]["schema_id"]["const"] == (
        "circle_calculus.ai_contract_request.v0"
    )
    assert "rope" in schema["properties"]["kind"]["enum"]
    assert "rope_position_distinguishability" in schema["properties"]["kind"]["enum"]
    assert schema["properties"]["parameters"]["type"] == "object"


def test_request_schema_validates_public_parameter_shapes() -> None:
    schema = build_contract_request_json_schema()

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "rope",
            "parameters": {},
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "kv-cache",
            "parameters": {
                "cache_size": 16,
                "current": 31,
                "token": 20,
                "batch_tokens": [20, 24],
                "sink_size": 4,
            },
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "sparse-attention",
            "parameters": {
                "context": 32,
                "strides": [5, 11, 17],
                "path_length": 16,
                "local_window": 9,
            },
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "recurrence",
            "parameters": {},
        },
        schema,
    )

    missing_sparse_field = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse-attention",
        "parameters": {
            "context": 32,
            "strides": [5, 11, 17],
            "path_length": 16,
        },
    }
    typo_parameter = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"shift_presses": 3},
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(missing_sparse_field, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(typo_parameter, schema)


def test_receipt_schema_exposes_runner_metadata() -> None:
    schema = build_contract_receipt_json_schema()

    assert "recommendations" in schema["required"]
    assert "validation_commands" in schema["required"]
    assert "request_content_fingerprint" in schema["required"]
    assert "normalized_request_fingerprint" in schema["required"]
    assert schema["properties"]["recommendations"]["minItems"] == 1
    assert schema["properties"]["validation_commands"]["minItems"] == 1


def test_request_validation_report_schema_accepts_public_reports() -> None:
    schema = build_contract_request_validation_json_schema()
    good_report = build_contract_request_validation_report(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "rope",
            "parameters": {},
        }
    )
    bad_report = build_contract_request_validation_report(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "sparse-attention",
            "parameters": {
                "context": 32,
                "strides": [5, 0],
                "path_length": 16,
                "local_window": 9,
            },
        }
    )

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(good_report, schema)
    jsonschema.validate(bad_report, schema)
    assert good_report["ok"] is True
    assert bad_report["ok"] is False


def test_runner_check_report_schema_accepts_public_report() -> None:
    schema = build_contract_runner_check_json_schema()
    report = {
        "schema_id": "circle_calculus.ai_contract_runner_check.v0",
        "ok": True,
        "example_count": 1,
        "failure_count": 0,
        "failures": [],
        "gate_policy": {
            "allowed_statuses": ["proved"],
            "require_passed": True,
        },
        "summaries": [
            {
                "source_type": "request",
                "source_path": "examples/circle_ai_requests/rope_request.json",
                "request_path": "examples/circle_ai_requests/rope_request.json",
                "receipt_path": None,
                "kind": "rope_position_distinguishability",
                "status": "proved",
                "request_passed": True,
                "theorem_count": 43,
                "recommendation_count": 2,
                "validation_command_count": 2,
                "request_content_fingerprint": "0" * 64,
                "normalized_request_fingerprint": "1" * 64,
                "receipt_content_fingerprint": "2" * 64,
            }
        ],
    }

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)


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


def test_circle_ai_certify_cli_imports_standard_rope_model_config(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    request_path = tmp_path / "circle_request.json"
    config_path.write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "rope_theta": 10000.0,
                "max_position_embeddings": 131072,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(config_path),
            "--requested-margin",
            "1/328459",
            "--format",
            "json",
            "--request-out",
            str(request_path),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["status"] == "proved"
    assert payload["normalized_request"]["head_dim"] == 128
    assert payload["normalized_request"]["base"] == 10000.0
    assert payload["normalized_request"]["context_length"] == 131072
    assert payload["request"]["parameters"]["requested_margin"] == "1/328459"
    saved_request = json.loads(request_path.read_text())
    assert saved_request == payload["request"]
    assert validate_contract_request(saved_request) == []


def test_circle_ai_certify_cli_imports_checked_in_model_config(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "request.json"
    receipt_path = tmp_path / "receipt.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--request-out",
            str(request_path),
            "--json-out",
            str(receipt_path),
            "--require-status",
            "proved",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    saved_request = json.loads(request_path.read_text())
    saved_receipt = json.loads(receipt_path.read_text())
    assert payload == saved_receipt
    assert saved_request == saved_receipt["request"]
    assert saved_receipt["normalized_request"]["head_dim"] == 128
    assert saved_receipt["normalized_request"]["base"] == 10000.0
    assert saved_receipt["normalized_request"]["context_length"] == 131072


def test_circle_ai_certify_cli_rejects_scaled_rope_model_config(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "rope_theta": 500000.0,
                "max_position_embeddings": 131072,
                "rope_scaling": {"rope_type": "llama3", "factor": 8.0},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(config_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "rope_scaling is outside" in result.stderr


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


def test_circle_ai_certify_cli_receipt_gate_accepts_passing_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["status"] == "proved"
    assert payload["request_passed"] is True
    assert result.stderr == ""


def test_circle_ai_certify_cli_receipt_gate_rejects_failed_request() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "1000",
            "--requested-margin",
            "1/999",
            "--format",
            "json",
            "--require-status",
            "impossible",
            "--require-passed",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "impossible"
    assert payload["request_passed"] is False
    assert "receipt_gate_failure=" in result.stderr
    assert "request_passed was not true" in result.stderr


def test_circle_ai_certify_cli_validates_request_without_receipt(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "sparse_request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "sparse-attention",
                "parameters": {
                    "context": 32,
                    "strides": [5, 11, 17],
                    "path_length": 16,
                    "local_window": 9,
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
            "--validate-only",
            "--format",
            "json",
            "--pack",
            str(tmp_path / "missing_contract_pack.json"),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload == {
        "schema_id": "circle_calculus.ai_contract_request_validation.v0",
        "request_schema_id": "circle_calculus.ai_contract_request.v0",
        "ok": True,
        "kind": "sparse-attention",
        "canonical_kind": "sparse_attention_coverage",
        "failure_count": 0,
        "failures": [],
    }


def test_circle_ai_certify_cli_validate_only_rejects_receipt_gate_options(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "sparse_request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "sparse-attention",
                "parameters": {
                    "context": 32,
                    "strides": [5, 11, 17],
                    "path_length": 16,
                    "local_window": 9,
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
            "--validate-only",
            "--require-status",
            "proved",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "require a receipt" in result.stderr


def test_circle_ai_certify_cli_validate_only_rejects_bad_request(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "bad_sparse_request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "sparse-attention",
                "parameters": {
                    "context": 32,
                    "strides": [5, 0],
                    "path_length": 16,
                    "local_window": 9,
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
            "--validate-only",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["canonical_kind"] == "sparse_attention_coverage"
    assert any("positive integers" in failure for failure in payload["failures"])
