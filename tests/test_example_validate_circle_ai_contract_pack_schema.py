from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications.circle_ai_contracts import (
    build_acceptance_policy_report_json_schema,
    build_acceptance_policy_json_schema,
    build_acceptance_receipt_json_schema,
    build_contract_pack,
    build_contract_pack_json_schema,
    build_downstream_rejection_report_json_schema,
)
from circle_math.applications.circle_ai_contract_consumer import (
    contract_acceptance_policy_report,
)


ROOT = Path(__file__).resolve().parents[1]


def _write_pack_and_schema(tmp_path: Path) -> tuple[Path, Path]:
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    schema_path = tmp_path / "circle_ai_contract_pack.schema.json"
    pack_path.write_text(json.dumps(build_contract_pack()))
    schema_path.write_text(json.dumps(build_contract_pack_json_schema()))
    return pack_path, schema_path


def _write_policy_schema(tmp_path: Path) -> Path:
    policy_schema_path = tmp_path / "circle_ai_contract_acceptance_policy.schema.json"
    policy_schema_path.write_text(json.dumps(build_acceptance_policy_json_schema()))
    return policy_schema_path


def _write_report_and_schemas(tmp_path: Path) -> tuple[Path, Path, Path]:
    pack = build_contract_pack()
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["expected_pack_fingerprint"] = pack["pack_content_fingerprint"]
    for spec in policy["contracts"]:
        spec["expected_contract_fingerprint"] = pack["contract_fingerprint_index"][
            spec["kind"]
        ]["content_fingerprint"]
    report_path = tmp_path / "circle_ai_contract_acceptance_policy_report.json"
    report_schema_path = (
        tmp_path / "circle_ai_contract_acceptance_policy_report.schema.json"
    )
    receipt_schema_path = tmp_path / "circle_ai_contract_acceptance_receipt.schema.json"
    report_path.write_text(json.dumps(contract_acceptance_policy_report(pack, policy)))
    report_schema_path.write_text(json.dumps(build_acceptance_policy_report_json_schema()))
    receipt_schema_path.write_text(json.dumps(build_acceptance_receipt_json_schema()))
    return report_path, report_schema_path, receipt_schema_path


def _write_rejection_report_and_schema(tmp_path: Path) -> tuple[Path, Path]:
    rejection_report_path = tmp_path / "circle_ai_downstream_rejection_report.json"
    rejection_report_schema_path = (
        tmp_path / "circle_ai_downstream_rejection_report.schema.json"
    )
    rejection_report_path.write_text(json.dumps({
        "schema_id": "circle_calculus.downstream_ci_rejection_report.v0",
        "example_schema_id": "circle_calculus.downstream_ci_acceptance_example.v0",
        "accepted": False,
        "error": "policy expected pack fingerprint does not match pack",
        "failure_count": 1,
        "failures": ["policy expected pack fingerprint does not match pack"],
        "pack_path": "site/data/generated/circle_ai_contract_pack.json",
        "policy_path": "examples/circle_ai_contract_acceptance_policy.json",
        "planner_requested_recommendation_ids": [],
        "not_claimed": (
            "This is an artifact-consumption rejection report, not a proof or "
            "model-quality claim."
        ),
    }))
    rejection_report_schema_path.write_text(
        json.dumps(build_downstream_rejection_report_json_schema())
    )
    return rejection_report_path, rejection_report_schema_path


def test_example_schema_validator_accepts_generated_pack(tmp_path: Path) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    policy_schema_path = _write_policy_schema(tmp_path)
    report_path, report_schema_path, receipt_schema_path = _write_report_and_schemas(
        tmp_path
    )
    rejection_report_path, rejection_report_schema_path = (
        _write_rejection_report_and_schema(tmp_path)
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--policy-schema",
            str(policy_schema_path),
            "--policy-report",
            str(report_path),
            "--policy-report-schema",
            str(report_schema_path),
            "--receipt-schema",
            str(receipt_schema_path),
            "--rejection-report",
            str(rejection_report_path),
            "--rejection-report-schema",
            str(rejection_report_schema_path),
            "--summary",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract schema ok:" in result.stdout
    assert "schema_id=circle_calculus.ai_contract_pack.v0" in result.stdout
    assert (
        "policy_schema_id=circle_calculus.ai_contract_acceptance_policy.v0"
        in result.stdout
    )
    assert (
        "policy_report_schema_id="
        "circle_calculus.ai_contract_acceptance_policy_report.v0"
        in result.stdout
    )
    assert (
        "rejection_report_schema_id="
        "circle_calculus.downstream_ci_rejection_report.v0"
        in result.stdout
    )
    assert "contracts=9" in result.stdout
    assert "rope_position_distinguishability" in result.stdout


def test_example_schema_validator_rejects_missing_minimum_field(
    tmp_path: Path,
) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    pack = json.loads(pack_path.read_text())
    for contract in pack["contracts"]:
        if contract["kind"] == "strided_candidate_fanout":
            del contract["fields"]["effective_candidate_budget"]
            break
    pack_path.write_text(json.dumps(pack))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--skip-policy",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "effective_candidate_budget" in result.stderr


def test_example_schema_validator_rejects_missing_source_paper(
    tmp_path: Path,
) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    pack = json.loads(pack_path.read_text())
    del pack["contracts"][0]["source_paper"]
    pack_path.write_text(json.dumps(pack))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--skip-policy",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "source_paper" in result.stderr


def test_example_schema_validator_rejects_empty_source_trail_array(
    tmp_path: Path,
) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    pack = json.loads(pack_path.read_text())
    pack["contracts"][0]["living_book_pages"] = []
    pack_path.write_text(json.dumps(pack))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--skip-policy",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "non-empty" in result.stderr


def test_example_schema_validator_rejects_malformed_policy(
    tmp_path: Path,
) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    policy_schema_path = _write_policy_schema(tmp_path)
    policy_path = tmp_path / "policy.json"
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["contracts"][0]["kind"] = "not_a_contract_kind"
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--policy",
            str(policy_path),
            "--policy-schema",
            str(policy_schema_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "not_a_contract_kind" in result.stderr


def test_example_schema_validator_rejects_duplicate_policy_pin(
    tmp_path: Path,
) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    policy_schema_path = _write_policy_schema(tmp_path)
    policy_path = tmp_path / "policy.json"
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["contracts"][0]["required_fields"] = [
        "d19_request_context",
        "d19_request_context",
    ]
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--policy",
            str(policy_path),
            "--policy-schema",
            str(policy_schema_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "non-unique" in result.stderr


def test_example_schema_validator_rejects_empty_policy_pin(
    tmp_path: Path,
) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    policy_schema_path = _write_policy_schema(tmp_path)
    policy_path = tmp_path / "policy.json"
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["contracts"][0]["required_fields"] = []
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--policy",
            str(policy_path),
            "--policy-schema",
            str(policy_schema_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "non-empty" in result.stderr
