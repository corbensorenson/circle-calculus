from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFIER = ROOT / "scripts" / "circle_ai_certify.py"
SCRIPT = ROOT / "examples" / "downstream_ci_verify_circle_ai_artifacts.py"
STANDARD_ROPE_MODEL_CONFIG = (
    ROOT / "examples" / "circle_ai_model_configs" / "standard_rope_config.json"
)


def _emit_standard_rope_artifacts(tmp_path: Path) -> tuple[Path, dict[str, Path]]:
    artifact_dir = tmp_path / "artifacts"
    prefix = "standard_rope_config"
    subprocess.run(
        [
            sys.executable,
            str(CERTIFIER),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--artifact-dir",
            str(artifact_dir),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return artifact_dir / f"{prefix}_artifact_manifest.json", {
        "request": artifact_dir / f"{prefix}_request.json",
        "manifest_check": artifact_dir / f"{prefix}_artifact_manifest_check.json",
    }


def test_standalone_artifact_verifier_accepts_standard_artifact_dir(
    tmp_path: Path,
) -> None:
    manifest_path, paths = _emit_standard_rope_artifacts(tmp_path)

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
            "mixed_theorem_and_computation",
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
    assert summary["kind"] == "rope_position_distinguishability"
    assert summary["status"] == "proved"
    assert summary["request_passed"] is True
    assert summary["decision_verdict"] == "passed"
    assert summary["decision_assurance"] == "mixed_theorem_and_computation"
    assert summary["artifact_count"] == 8
    assert summary["manifest_check_present"] is True
    assert summary["manifest_check_ok"] is True
    assert set(summary["artifact_labels"]) == {
        "request_json",
        "request_validation_report",
        "model_config_import_report",
        "receipt_json",
        "receipt_check",
        "gate_report",
        "certification_bundle",
        "certification_bundle_check",
    }
    assert Path(summary["manifest_check_path"]) == paths["manifest_check"]
    assert summary["receipt_content_fingerprint_short"]
    assert "mathematical proof" in payload["not_claimed"]


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
