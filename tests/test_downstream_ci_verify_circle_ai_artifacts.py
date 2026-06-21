from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CERTIFIER = ROOT / "scripts" / "circle_ai_certify.py"
SCRIPT = ROOT / "examples" / "downstream_ci_verify_circle_ai_artifacts.py"
STANDARD_ROPE_MODEL_CONFIG = (
    ROOT / "examples" / "circle_ai_model_configs" / "standard_rope_config.json"
)
BASE_REQUIRED_LABELS = {
    "request_json",
    "request_validation_report",
    "receipt_json",
    "receipt_check",
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
        8,
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
        7,
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
        7,
        BASE_REQUIRED_LABELS,
    ),
    (
        "recurrence",
        ["recurrence"],
        "recurrence",
        "recurrence_schedule",
        "theorem_backed",
        7,
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
    assert summary["receipt_content_fingerprint_short"]
    assert "mathematical proof" in payload["not_claimed"]


def test_standalone_artifact_verifier_accepts_multi_contract_kind_gate(
    tmp_path: Path,
) -> None:
    manifests: list[Path] = []
    expected_kinds: list[str] = []
    for (
        slug,
        subcommand_args,
        prefix,
        expected_kind,
        expected_assurance,
        _expected_artifact_count,
        _expected_labels,
    ) in STANDARD_ARTIFACT_CASES:
        manifest_path, _paths = _emit_standard_artifacts(
            tmp_path,
            slug=slug,
            subcommand_args=subcommand_args,
            prefix=prefix,
            required_assurance=expected_assurance,
        )
        manifests.append(manifest_path)
        expected_kinds.append(expected_kind)

    require_kind_args = [
        arg
        for kind in expected_kinds
        for arg in ("--require-kind", kind)
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
