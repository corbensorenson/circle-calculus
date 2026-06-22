from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CERTIFIER = ROOT / "scripts" / "circle_ai_certify.py"
SCRIPT = ROOT / "examples" / "downstream_ci_verify_circle_ai_artifacts.py"
BATCH_SCRIPT = ROOT / "examples" / "downstream_ci_verify_circle_ai_batch.py"
STANDARD_ROPE_MODEL_CONFIG = (
    ROOT / "examples" / "circle_ai_model_configs" / "standard_rope_config.json"
)
ARCHITECTURE_CONFIG = (
    ROOT
    / "examples"
    / "circle_ai_architecture_configs"
    / "basic_transformer_contract_config.json"
)
ROPE_MODEL_ONLY_ARCHITECTURE_CONFIG = (
    ROOT
    / "examples"
    / "circle_ai_architecture_configs"
    / "rope_model_only_contract_config.json"
)
BASE_REQUIRED_LABELS = {
    "request_json",
    "request_validation_report",
    "receipt_json",
    "compact_receipt_json",
    "receipt_check",
    "receipt_replay_check",
    "gate_report",
    "certification_bundle",
    "certification_bundle_check",
}
STANDARD_ARTIFACT_CASES = [
    (
        "rope",
        [
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
        ],
        "standard_rope_config",
        "rope_position_distinguishability",
        "mixed_theorem_and_computation",
        10,
        BASE_REQUIRED_LABELS | {"model_config_import_report"},
    ),
    (
        "kv_cache",
        [
            "kv-cache",
            "--cache-size",
            "16",
            "--current",
            "31",
            "--token",
            "31",
            "--batch-tokens",
            "20,24,29,31",
            "--sink-size",
            "4",
        ],
        "kv_cache",
        "kv_cache_ring_buffer",
        "theorem_backed",
        9,
        BASE_REQUIRED_LABELS,
    ),
    (
        "sparse_attention",
        [
            "sparse-attention",
            "--context",
            "32",
            "--strides",
            "5,11,17",
            "--path-length",
            "16",
            "--local-window",
            "9",
        ],
        "sparse_attention",
        "sparse_attention_coverage",
        "theorem_backed",
        9,
        BASE_REQUIRED_LABELS,
    ),
    (
        "recurrence",
        ["recurrence"],
        "recurrence",
        "recurrence_schedule",
        "mixed_theorem_and_computation",
        9,
        BASE_REQUIRED_LABELS,
    ),
]


def _emit_standard_artifacts(
    tmp_path: Path,
    *,
    slug: str,
    subcommand_args: list[str],
    prefix: str,
    required_assurance: str,
) -> tuple[Path, dict[str, Path]]:
    artifact_dir = tmp_path / f"{slug}_artifacts"
    subprocess.run(
        [
            sys.executable,
            str(CERTIFIER),
            *subcommand_args,
            "--artifact-dir",
            str(artifact_dir),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            required_assurance,
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return artifact_dir / f"{prefix}_artifact_manifest.json", {
        "request": artifact_dir / f"{prefix}_request.json",
        "model_config_import": artifact_dir / f"{prefix}_model_config_import.json",
        "architecture_config_import": (
            artifact_dir / f"{prefix}_architecture_config_import.json"
        ),
        "receipt": artifact_dir / f"{prefix}_receipt.json",
        "manifest_check": artifact_dir / f"{prefix}_artifact_manifest_check.json",
    }


def _emit_standard_rope_artifacts(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    return _emit_standard_artifacts(
        tmp_path,
        slug="rope",
        subcommand_args=[
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
        ],
        prefix="standard_rope_config",
        required_assurance="mixed_theorem_and_computation",
    )


def _emit_sparse_architecture_artifacts(
    tmp_path: Path,
) -> tuple[Path, dict[str, Path]]:
    return _emit_standard_artifacts(
        tmp_path,
        slug="sparse_architecture",
        subcommand_args=[
            "sparse-attention",
            "--architecture-config",
            str(ARCHITECTURE_CONFIG),
        ],
        prefix="sparse_attention",
        required_assurance="theorem_backed",
    )


def _emit_architecture_batch_artifacts(tmp_path: Path) -> Path:
    artifact_dir = tmp_path / "architecture_batch"
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "batch",
            "--architecture-config-file",
            str(ARCHITECTURE_CONFIG),
            "--artifact-dir",
            str(artifact_dir),
            "--artifact-prefix",
            "architecture-suite",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return artifact_dir / "architecture-suite_runner_check.json"


def _emit_rope_model_only_architecture_batch_artifacts(tmp_path: Path) -> Path:
    artifact_dir = tmp_path / "rope_model_only_architecture_batch"
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "batch",
            "--architecture-config-file",
            str(ROPE_MODEL_ONLY_ARCHITECTURE_CONFIG),
            "--artifact-dir",
            str(artifact_dir),
            "--artifact-prefix",
            "rope-model-only",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return artifact_dir / "rope-model-only_runner_check.json"


@pytest.mark.parametrize(
    (
        "slug",
        "subcommand_args",
        "prefix",
        "expected_kind",
        "expected_assurance",
        "expected_artifact_count",
        "expected_labels",
    ),
    STANDARD_ARTIFACT_CASES,
)
def test_standalone_artifact_verifier_accepts_standard_artifact_dirs(
    tmp_path: Path,
    slug: str,
    subcommand_args: list[str],
    prefix: str,
    expected_kind: str,
    expected_assurance: str,
    expected_artifact_count: int,
    expected_labels: set[str],
) -> None:
    manifest_path, paths = _emit_standard_artifacts(
        tmp_path,
        slug=slug,
        subcommand_args=subcommand_args,
        prefix=prefix,
        required_assurance=expected_assurance,
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            expected_assurance,
            "--require-passed",
            "--require-manifest-check",
            "--require-label",
            "request_json",
            "--require-label",
            "receipt_json",
            "--require-label",
            "certification_bundle",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.downstream_ci_artifact_acceptance.v0"
    assert payload["accepted"] is True
    assert payload["manifest_count"] == 1
    assert payload["failure_count"] == 0
    assert payload["require_manifest_check"] is True
    summary = payload["manifests"][0]
    assert summary["kind"] == expected_kind
    assert summary["status"] == "proved"
    assert summary["request_passed"] is True
    assert summary["decision_verdict"] == "passed"
    assert summary["decision_assurance"] == expected_assurance
    assert summary["artifact_count"] == expected_artifact_count
    assert summary["manifest_check_present"] is True
    assert summary["manifest_check_ok"] is True
    assert set(summary["artifact_labels"]) == expected_labels
    assert Path(summary["manifest_check_path"]) == paths["manifest_check"]
    if "model_config_import_report" in expected_labels:
        model_config_import = json.loads(
            paths["model_config_import"].read_text(encoding="utf-8")
        )
        assert summary["model_config_fingerprint"] == (
            model_config_import["model_config_fingerprint"]
        )
        assert summary["unsupported_model_config_fields"] == []
    else:
        assert summary["model_config_fingerprint"] is None
        assert summary["unsupported_model_config_fields"] == []
    assert summary["architecture_config_fingerprint"] is None
    assert summary["architecture_config_import_kind"] is None
    assert summary["receipt_content_fingerprint_short"]
    assert summary["receipt_replay_check_present"] is True
    assert summary["receipt_replay_check_ok"] is True
    assert summary["receipt_replay_check_all_replay_fields_match"] is True
    assert summary["receipt_replay_check_fingerprints_match_receipt"] is True
    assert summary["semantic_check_sidecar_count"] == 3
    assert summary["semantic_check_sidecar_labels"] == [
        "receipt_check",
        "gate_report",
        "certification_bundle_check",
    ]
    assert summary["semantic_check_sidecar_failure_count"] == 0
    expected_preflight_labels = ["request_validation_report"]
    if "model_config_import_report" in expected_labels:
        expected_preflight_labels.append("model_config_import_report")
    assert summary["preflight_sidecar_count"] == len(expected_preflight_labels)
    assert summary["preflight_sidecar_labels"] == expected_preflight_labels
    assert summary["preflight_sidecar_failure_count"] == 0
    assert "mathematical proof" in payload["not_claimed"]


def test_standalone_batch_artifact_verifier_accepts_architecture_batch(
    tmp_path: Path,
) -> None:
    runner_check_path = _emit_architecture_batch_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(BATCH_SCRIPT),
            str(runner_check_path),
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
            "--require-kind",
            "rope_position_distinguishability",
            "--require-kind",
            "kv_cache_ring_buffer",
            "--require-kind",
            "sparse_attention_coverage",
            "--require-kind",
            "recurrence_schedule",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == (
        "circle_calculus.downstream_ci_batch_artifact_acceptance.v0"
    )
    assert payload["accepted"] is True
    assert payload["source_count"] == 4
    assert payload["failure_count"] == 0
    assert payload["observed_kinds"] == [
        "kv_cache_ring_buffer",
        "recurrence_schedule",
        "rope_position_distinguishability",
        "sparse_attention_coverage",
    ]
    assert all(summary["failure_count"] == 0 for summary in payload["summaries"])
    assert "mathematical proof" in payload["not_claimed"]


def test_standalone_batch_artifact_verifier_accepts_rope_only_architecture_batch(
    tmp_path: Path,
) -> None:
    runner_check_path = _emit_rope_model_only_architecture_batch_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(BATCH_SCRIPT),
            str(runner_check_path),
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
            "--require-kind",
            "rope_position_distinguishability",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    runner_check = json.loads(runner_check_path.read_text(encoding="utf-8"))
    assert runner_check["example_count"] == 1
    assert runner_check["selected_kinds"] == ["rope_position_distinguishability"]
    summary = runner_check["summaries"][0]
    assert summary["source_type"] == "architecture_config"
    assert summary["unsupported_architecture_config_fields"] == ["model.model_type"]

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["source_count"] == 1
    assert payload["failure_count"] == 0
    assert payload["observed_kinds"] == ["rope_position_distinguishability"]
    assert payload["kind_counts"] == {"rope_position_distinguishability": 1}
    assert payload["summaries"][0]["failure_count"] == 0
    assert payload["summaries"][0]["source_type"] == "architecture_config"
    assert payload["summaries"][0]["kind"] == "rope_position_distinguishability"
    assert "mathematical proof" in payload["not_claimed"]


def test_standalone_batch_artifact_verifier_rejects_missing_sidecar(
    tmp_path: Path,
) -> None:
    runner_check_path = _emit_architecture_batch_artifacts(tmp_path)
    runner_check = json.loads(runner_check_path.read_text(encoding="utf-8"))
    first_receipt = Path(runner_check["summaries"][0]["receipt_path"])
    first_receipt.unlink()

    result = subprocess.run(
        [
            sys.executable,
            str(BATCH_SCRIPT),
            str(runner_check_path),
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    rejection = json.loads(result.stderr)
    assert rejection["accepted"] is False
    assert rejection["failure_count"] >= 1
    assert any(
        "receipt_path artifact is missing" in failure
        for failure in rejection["failures"]
    )


def test_standalone_artifact_verifier_accepts_architecture_config_artifact_dir(
    tmp_path: Path,
) -> None:
    manifest_path, paths = _emit_sparse_architecture_artifacts(tmp_path)
    architecture_config_import = json.loads(
        paths["architecture_config_import"].read_text(encoding="utf-8")
    )
    architecture_fingerprint = architecture_config_import[
        "architecture_config_fingerprint"
    ]

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "theorem_backed",
            "--require-passed",
            "--require-manifest-check",
            "--require-label",
            "architecture_config_import_report",
            "--require-architecture-config-fingerprint",
            architecture_fingerprint,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["failure_count"] == 0
    assert payload["required_architecture_config_fingerprints"] == [
        architecture_fingerprint
    ]
    assert payload["observed_architecture_config_fingerprint_count"] == 1
    assert payload["pin_policy"]["required_architecture_config_fingerprints"] == [
        architecture_fingerprint
    ]
    summary = payload["manifests"][0]
    assert summary["kind"] == "sparse_attention_coverage"
    assert summary["artifact_count"] == 10
    assert set(summary["artifact_labels"]) == (
        BASE_REQUIRED_LABELS | {"architecture_config_import_report"}
    )
    assert summary["architecture_config_fingerprint"] == architecture_fingerprint
    assert summary["architecture_config_fingerprint_short"] == (
        architecture_fingerprint[:12]
    )
    assert summary["architecture_config_import_kind"] == (
        "sparse_attention_coverage"
    )
    assert summary["model_config_fingerprint"] is None
    assert summary["unsupported_model_config_fields"] == []
    assert summary["preflight_sidecar_count"] == 2
    assert summary["preflight_sidecar_labels"] == [
        "request_validation_report",
        "architecture_config_import_report",
    ]
    assert summary["preflight_sidecar_failure_count"] == 0
    assert "mathematical proof" in payload["not_claimed"]


def test_standalone_artifact_verifier_accepts_multi_contract_kind_gate(
    tmp_path: Path,
) -> None:
    manifests: list[Path] = []
    expected_kinds: list[str] = []
    required_model_config_fingerprints: list[str] = []
    for (
        slug,
        subcommand_args,
        prefix,
        expected_kind,
        expected_assurance,
        _expected_artifact_count,
        _expected_labels,
    ) in STANDARD_ARTIFACT_CASES:
        manifest_path, paths = _emit_standard_artifacts(
            tmp_path,
            slug=slug,
            subcommand_args=subcommand_args,
            prefix=prefix,
            required_assurance=expected_assurance,
        )
        manifests.append(manifest_path)
        expected_kinds.append(expected_kind)
        receipt = json.loads(paths["receipt"].read_text(encoding="utf-8"))
        assert receipt["validation_commands"]
        if paths["model_config_import"].exists():
            model_config_import = json.loads(
                paths["model_config_import"].read_text(encoding="utf-8")
            )
            required_model_config_fingerprints.append(
                model_config_import["model_config_fingerprint"]
            )

    require_kind_args = [
        arg
        for kind in expected_kinds
        for arg in ("--require-kind", kind)
    ]
    required_theorem_ids = ["AIRA-T0239", "AIM-T0060", "AIT-T0016", "AIM-T0159"]
    require_theorem_args = [
        arg
        for theorem_id in required_theorem_ids
        for arg in ("--require-theorem-id", theorem_id)
    ]
    required_evidence_fields = [
        "real_phase_dirichlet_guardrail",
        "sink_window_certificate",
        "covered_lag_count",
        "fields",
    ]
    require_evidence_args = [
        arg
        for field in required_evidence_fields
        for arg in ("--require-evidence-field", field)
    ]
    required_recommendation_ids = [
        "ROPE-USE-D19-MARGIN-FRONTIER",
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
        "SPARSE-INTERVAL-REPAIR-PATH",
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
    ]
    require_recommendation_args = [
        arg
        for recommendation_id in required_recommendation_ids
        for arg in ("--require-recommendation-id", recommendation_id)
    ]
    required_validation_commands: list[str] = []
    for (
        slug,
        _subcommand_args,
        prefix,
        _expected_kind,
        _expected_assurance,
        _expected_artifact_count,
        _expected_labels,
    ) in STANDARD_ARTIFACT_CASES:
        receipt_path = tmp_path / f"{slug}_artifacts" / f"{prefix}_receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        required_validation_commands.append(receipt["validation_commands"][0])
    require_validation_args = [
        arg
        for command in required_validation_commands
        for arg in ("--require-validation-command", command)
    ]
    require_model_config_fingerprint_args = [
        arg
        for fingerprint in required_model_config_fingerprints
        for arg in ("--require-model-config-fingerprint", fingerprint)
    ]
    required_normalized_params = [
        ("head_dim", 128),
        ("cache_size", 16),
        ("sequence_length", 32),
        ("loop_period", 5),
    ]
    require_normalized_args = [
        arg
        for key, value in required_normalized_params
        for arg in ("--require-normalized-param", f"{key}={json.dumps(value)}")
    ]

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            *(str(path) for path in manifests),
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "theorem_backed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--require-manifest-check",
            *require_kind_args,
            *require_theorem_args,
            *require_evidence_args,
            *require_recommendation_args,
            *require_validation_args,
            *require_model_config_fingerprint_args,
            *require_normalized_args,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["manifest_count"] == 4
    assert payload["failure_count"] == 0
    assert payload["required_kinds"] == expected_kinds
    assert payload["observed_kinds"] == sorted(expected_kinds)
    assert payload["kind_counts"] == {kind: 1 for kind in sorted(expected_kinds)}
    assert payload["required_theorem_ids"] == required_theorem_ids
    assert payload["observed_theorem_id_count"] >= len(required_theorem_ids)
    assert payload["required_evidence_fields"] == required_evidence_fields
    assert payload["observed_evidence_field_count"] >= len(required_evidence_fields)
    assert payload["required_recommendation_ids"] == required_recommendation_ids
    assert payload["observed_recommendation_id_count"] >= len(
        required_recommendation_ids
    )
    assert payload["required_validation_commands"] == required_validation_commands
    assert payload["observed_validation_command_count"] >= len(
        required_validation_commands
    )
    assert payload["required_model_config_fingerprints"] == (
        required_model_config_fingerprints
    )
    assert payload["observed_model_config_fingerprint_count"] >= len(
        required_model_config_fingerprints
    )
    assert payload["required_architecture_config_fingerprints"] == []
    assert payload["observed_architecture_config_fingerprint_count"] == 0
    assert payload["required_normalized_params"] == [
        {"key": key, "value": value} for key, value in required_normalized_params
    ]
    expected_pin_policy = {
        "required_kinds": expected_kinds,
        "required_theorem_ids": required_theorem_ids,
        "required_evidence_fields": required_evidence_fields,
        "required_recommendation_ids": required_recommendation_ids,
        "required_validation_commands": required_validation_commands,
        "required_model_config_fingerprints": required_model_config_fingerprints,
        "required_architecture_config_fingerprints": [],
        "required_normalized_params": [
            {"key": key, "value": value} for key, value in required_normalized_params
        ],
    }
    assert payload["pin_policy"] == expected_pin_policy

    policy_path = tmp_path / "artifact_pin_policy.json"
    policy_path.write_text(
        json.dumps({"pin_policy": expected_pin_policy}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    policy_result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            *(str(path) for path in manifests),
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "theorem_backed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--require-manifest-check",
            "--pin-policy",
            str(policy_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    policy_payload = json.loads(policy_result.stdout)
    assert policy_payload["accepted"] is True
    assert policy_payload["pin_policy"] == expected_pin_policy


def test_standalone_artifact_verifier_rejects_stale_receipt_replay_sidecar(
    tmp_path: Path,
) -> None:
    manifest_path, _paths = _emit_standard_rope_artifacts(tmp_path)
    artifact_dir = manifest_path.parent
    replay_path = artifact_dir / "standard_rope_config_receipt_replay_check.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    replay_check = json.loads(replay_path.read_text(encoding="utf-8"))
    replay_check["replayed"]["receipt_content_fingerprint"] = "0" * 64
    replay_path.write_text(
        json.dumps(replay_check, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for artifact in manifest["artifacts"]:
        if artifact["label"] == "receipt_replay_check":
            artifact["sha256"] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    summary = payload["manifests"][0]
    assert summary["receipt_replay_check_present"] is True
    assert summary["receipt_replay_check_ok"] is True
    assert summary["receipt_replay_check_fingerprints_match_receipt"] is False
    assert "receipt_replay_check replayed receipt_content_fingerprint" in "\n".join(
        payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_stale_gate_report_sidecar(
    tmp_path: Path,
) -> None:
    manifest_path, _paths = _emit_standard_rope_artifacts(tmp_path)
    artifact_dir = manifest_path.parent
    gate_path = artifact_dir / "standard_rope_config_gate_report.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    gate_report = json.loads(gate_path.read_text(encoding="utf-8"))
    gate_report["summaries"][0]["receipt_content_fingerprint"] = "0" * 64
    gate_path.write_text(
        json.dumps(gate_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for artifact in manifest["artifacts"]:
        if artifact["label"] == "gate_report":
            artifact["sha256"] = hashlib.sha256(gate_path.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    summary = payload["manifests"][0]
    assert summary["semantic_check_sidecar_count"] == 3
    assert summary["semantic_check_sidecar_failure_count"] == 1
    assert "gate_report receipt_content_fingerprint" in "\n".join(
        payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_stale_model_config_import_sidecar(
    tmp_path: Path,
) -> None:
    manifest_path, _paths = _emit_standard_rope_artifacts(tmp_path)
    artifact_dir = manifest_path.parent
    import_path = artifact_dir / "standard_rope_config_model_config_import.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    import_report = json.loads(import_path.read_text(encoding="utf-8"))
    import_report["request_content_fingerprint"] = "0" * 64
    import_path.write_text(
        json.dumps(import_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for artifact in manifest["artifacts"]:
        if artifact["label"] == "model_config_import_report":
            artifact["sha256"] = hashlib.sha256(import_path.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    summary = payload["manifests"][0]
    assert summary["preflight_sidecar_count"] == 2
    assert summary["preflight_sidecar_failure_count"] == 1
    assert "model_config_import_report request_content_fingerprint" in "\n".join(
        payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_stale_architecture_config_import_sidecar(
    tmp_path: Path,
) -> None:
    manifest_path, paths = _emit_sparse_architecture_artifacts(tmp_path)
    import_path = paths["architecture_config_import"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    import_report = json.loads(import_path.read_text(encoding="utf-8"))
    import_report["request_content_fingerprint"] = "0" * 64
    import_path.write_text(
        json.dumps(import_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for artifact in manifest["artifacts"]:
        if artifact["label"] == "architecture_config_import_report":
            artifact["sha256"] = hashlib.sha256(import_path.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    summary = payload["manifests"][0]
    assert summary["preflight_sidecar_count"] == 2
    assert summary["preflight_sidecar_failure_count"] == 1
    assert "architecture_config_import_report request_content_fingerprint" in (
        "\n".join(payload["failures"])
    )


def test_standalone_artifact_verifier_rejects_missing_required_kind(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_standard_rope_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-kind",
            "kv_cache_ring_buffer",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["required_kinds"] == ["kv_cache_ring_buffer"]
    assert payload["observed_kinds"] == ["rope_position_distinguishability"]
    assert any(
        "required contract kind is missing" in failure
        for failure in payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_missing_required_theorem_id(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_standard_rope_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-theorem-id",
            "NONEXISTENT-T0000",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["required_theorem_ids"] == ["NONEXISTENT-T0000"]
    assert payload["observed_theorem_id_count"] > 0
    assert any(
        "required receipt theorem id is missing" in failure
        for failure in payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_missing_field_and_recommendation(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_standard_rope_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-evidence-field",
            "nonexistent_evidence_field",
            "--require-recommendation-id",
            "NONEXISTENT-RECOMMENDATION",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["required_evidence_fields"] == ["nonexistent_evidence_field"]
    assert payload["observed_evidence_field_count"] > 0
    assert payload["required_recommendation_ids"] == ["NONEXISTENT-RECOMMENDATION"]
    assert payload["observed_recommendation_id_count"] > 0
    assert any(
        "required receipt evidence field is missing" in failure
        for failure in payload["failures"]
    )
    assert any(
        "required receipt recommendation id is missing" in failure
        for failure in payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_missing_validation_command(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_standard_rope_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-validation-command",
            "python nonexistent_validation.py",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["required_validation_commands"] == [
        "python nonexistent_validation.py"
    ]
    assert payload["observed_validation_command_count"] > 0
    assert any(
        "required receipt validation command is missing" in failure
        for failure in payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_missing_normalized_param(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_standard_rope_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-normalized-param",
            "head_dim=256",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["required_normalized_params"] == [
        {"key": "head_dim", "value": 256}
    ]
    assert any(
        "required normalized request parameter is missing" in failure
        for failure in payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_missing_model_config_fingerprint(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_standard_rope_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-model-config-fingerprint",
            "0" * 64,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["required_model_config_fingerprints"] == ["0" * 64]
    assert payload["observed_model_config_fingerprint_count"] == 1
    assert any(
        "required model config fingerprint is missing" in failure
        for failure in payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_missing_architecture_config_fingerprint(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_sparse_architecture_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-architecture-config-fingerprint",
            "0" * 64,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["required_architecture_config_fingerprints"] == ["0" * 64]
    assert payload["observed_architecture_config_fingerprint_count"] == 1
    assert any(
        "required architecture config fingerprint is missing" in failure
        for failure in payload["failures"]
    )


def test_standalone_artifact_verifier_rejects_stale_artifact(
    tmp_path: Path,
) -> None:
    manifest_path, paths = _emit_standard_rope_artifacts(tmp_path)
    paths["request"].write_text(
        paths["request"].read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-manifest-check",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["accepted"] is False
    assert payload["failure_count"] >= 1
    assert any("sha256 mismatch" in failure for failure in payload["failures"])


def test_standalone_artifact_verifier_rejects_missing_required_label(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _emit_standard_rope_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(manifest_path),
            "--format",
            "json",
            "--require-label",
            "nonexistent_artifact",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    assert payload["schema_id"] == "circle_calculus.downstream_ci_artifact_acceptance.v0"
    assert any("required artifact label is missing" in failure for failure in payload["failures"])
