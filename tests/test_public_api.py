from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.core import (
    circular_convolution,
    circulant_matrix,
    finite_fourier_coefficients,
    finite_orbit,
    finite_period,
    inverse_finite_fourier,
    is_full_coil,
    spectral_aliasing_report,
    spectral_convolution_report,
)
from circle_math.ai_contracts import (
    CONTRACT_PACK_SCHEMA_ID,
    build_contract_pack,
    build_rope_request_parameters_from_model_config,
    build_validated_contract_receipt_from_request,
    build_validated_rope_receipt_from_model_config,
)
from circle_math.applications import (
    CIRCLE_AI_CONTRACT_COMPACT_RECEIPT_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_RECEIPT_SCHEMA_ID,
    build_contract_artifact_manifest,
    build_contract_artifact_manifest_file_check_report,
)
from circle_math.contracts import contract_kinds, readiness_summary


ROOT = Path(__file__).resolve().parents[1]


def test_stable_core_api_examples() -> None:
    assert finite_orbit(12, 5) == [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7]
    assert finite_period(12, 4) == 3
    assert is_full_coil(13, 5) is True
    assert is_full_coil(12, 4) is False


def test_stable_harmonic_api_examples() -> None:
    signal = [1, 2, 0, -1]
    kernel = [2, 0, 1, 0]

    coefficients = finite_fourier_coefficients(signal)
    reconstructed = inverse_finite_fourier(coefficients)
    assert all(abs(left - right) < 1e-9 for left, right in zip(signal, reconstructed))

    assert circular_convolution(kernel, signal) == [2 + 0j, 3 + 0j, 1 + 0j, 0 + 0j]
    assert circulant_matrix(kernel)[1] == [0 + 0j, 2 + 0j, 0 + 0j, 1 + 0j]

    report = spectral_convolution_report(kernel, signal)
    assert report.passed is True
    assert report.max_abs_error < 1e-9

    assert spectral_aliasing_report(4, [-1, 0, 3, 4, 7]) == {
        0: [0, 4],
        3: [-1, 3, 7],
    }


def test_stable_contract_api_pack_readiness() -> None:
    pack = build_contract_pack()
    assert pack["schema_id"] == CONTRACT_PACK_SCHEMA_ID
    kinds = contract_kinds(pack)
    assert "rope_position_distinguishability" in kinds
    assert "sparse_attention_coverage" in kinds
    sparse = readiness_summary(pack, "sparse_attention_coverage")
    assert sparse.ready_for_downstream_fixture_use is True
    assert sparse.all_theorem_ids_proved is True


def test_stable_rope_model_config_api_builds_receipt() -> None:
    model_config = {
        "hidden_size": 4096,
        "num_attention_heads": 32,
        "max_position_embeddings": 4096,
        "rope_theta": 10000.0,
    }

    parameters = build_rope_request_parameters_from_model_config(model_config)
    assert parameters["head_dim"] == 128
    assert parameters["base"] == 10000.0
    assert parameters["context"] == 4096

    receipt = build_validated_rope_receipt_from_model_config(model_config)
    assert receipt["kind"] == "rope_position_distinguishability"
    assert receipt["request"]["parameters"]["context"] == 4096
    assert receipt["normalized_request"]["head_dim"] == 128
    assert receipt["normalized_request"]["context_length"] == 4096
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True


def test_stable_request_api_builds_kv_cache_receipt() -> None:
    request = json.loads(
        (ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json").read_text()
    )

    receipt = build_validated_contract_receipt_from_request(request)
    assert receipt["kind"] == "kv_cache_ring_buffer"
    assert receipt["request"]["parameters"]["cache_size"] == 16
    assert receipt["request"]["parameters"]["request_id"] == "example_read_request"
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True


def test_stable_artifact_manifest_public_api(tmp_path) -> None:
    request = json.loads(
        (ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json").read_text()
    )
    receipt = build_validated_contract_receipt_from_request(request)
    receipt_path = tmp_path / "receipt.json"
    manifest_path = tmp_path / "artifact_manifest.json"
    receipt_path.write_text(json.dumps(receipt))

    manifest = build_contract_artifact_manifest(
        [("receipt_json", receipt_path, CIRCLE_AI_CONTRACT_RECEIPT_SCHEMA_ID)],
        artifact_prefix="kv_cache_ring_buffer",
        receipt=receipt,
        required_statuses=("proved",),
        require_passed=True,
    )
    manifest_path.write_text(json.dumps(manifest))
    report = build_contract_artifact_manifest_file_check_report(
        manifest,
        manifest_path=manifest_path,
    )

    assert manifest["schema_id"] == "circle_calculus.ai_contract_artifact_manifest.v0"
    assert manifest["artifact_count"] == 1
    assert manifest["artifacts"][0]["sha256"]
    assert report["schema_id"] == (
        "circle_calculus.ai_contract_artifact_manifest_file_check.v0"
    )
    assert report["ok"] is True


def test_package_cli_contract_ready_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "circle_math.cli",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0


def test_package_console_script_target_functions() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from circle_math.cli import contract_certify_main, contract_ready_main, "
                "contract_receipt_main, rope_certify_main, "
                "sparse_attention_certify_main; "
                "print(callable(contract_certify_main), callable(contract_ready_main), "
                "callable(rope_certify_main), "
                "callable(sparse_attention_certify_main), "
                "callable(contract_receipt_main))"
            ),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == "True True True True True"


def test_package_metadata_exposes_unified_ai_certifier() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    assert 'circle-ai-certify = "circle_math.cli:contract_certify_main"' in pyproject


def test_generated_public_api_reference_lists_console_scripts() -> None:
    reference = (ROOT / "docs" / "generated" / "PUBLIC_API_REFERENCE.md").read_text()
    assert "## Package Console Scripts" in reference
    assert "| `circle-ai-certify` | `circle_math.cli:contract_certify_main` |" in reference
    assert (
        "| `circle-ai-contract-receipt` | `circle_math.cli:contract_receipt_main` |"
        in reference
    )


def test_package_cli_contract_receipt_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_receipt_main; "
                "sys.exit(contract_receipt_main())"
            ),
            "--kind",
            "sparse-attention",
            "--parameters",
            json.dumps(
                {
                    "context": 9,
                    "strides": [3, 4, 7],
                    "path_length": 2,
                    "local_window": 2,
                }
            ),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
    assert receipt["kind"] == "sparse_attention_coverage"
    assert receipt["status"] == "proved"
    assert receipt["request_passed"] is True
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True


def test_package_cli_unified_certify_rope_model_config(
    tmp_path,
) -> None:
    config_path = tmp_path / "config.json"
    request_path = tmp_path / "request.json"
    request_validation_path = tmp_path / "request_validation.json"
    import_report_path = tmp_path / "import_report.json"
    bundle_path = tmp_path / "bundle.json"
    config_path.write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "max_position_embeddings": 4096,
                "rope_theta": 10000.0,
            }
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "rope",
            "--model-config-file",
            str(config_path),
            "--request-out",
            str(request_path),
            "--request-validation-report-out",
            str(request_validation_path),
            "--model-config-import-report-out",
            str(import_report_path),
            "--certification-bundle-out",
            str(bundle_path),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["kind"] == "rope_position_distinguishability"
    assert receipt["request"]["parameters"]["head_dim"] == 128
    assert receipt["request"]["parameters"]["context"] == 4096
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
    assert json.loads(request_path.read_text()) == receipt["request"]
    request_validation_report = json.loads(request_validation_path.read_text())
    assert (
        request_validation_report["schema_id"]
        == "circle_calculus.ai_contract_request_validation.v0"
    )
    assert request_validation_report["ok"] is True
    assert request_validation_report["request_content_fingerprint"] == receipt[
        "request_content_fingerprint"
    ]
    import_report = json.loads(import_report_path.read_text())
    assert import_report["ok"] is True
    assert import_report["request"] == receipt["request"]
    bundle = json.loads(bundle_path.read_text())
    assert bundle["schema_id"] == "circle_calculus.ai_contract_certification_bundle.v0"
    assert bundle["ok"] is True
    assert bundle["receipt"]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]
    assert bundle["model_config_import_report"]["request"] == receipt["request"]


def test_package_cli_unified_certify_request_file_gate() -> None:
    request_file = ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "request",
            "--request-file",
            str(request_file),
            "--require-passed",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["kind"] == "kv_cache_ring_buffer"
    assert receipt["request_passed"] is True


def test_package_cli_unified_certify_compact_json(tmp_path) -> None:
    compact_path = tmp_path / "compact_receipt.json"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "sparse-attention",
            "--context",
            "9",
            "--strides",
            "3,4,7",
            "--path-length",
            "2",
            "--local-window",
            "2",
            "--format",
            "compact-json",
            "--compact-json-out",
            str(compact_path),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    compact = json.loads(result.stdout)
    saved = json.loads(compact_path.read_text())
    assert compact == saved
    assert compact["schema_id"] == "circle_calculus.ai_contract_compact_receipt.v0"
    assert compact["kind"] == "sparse_attention_coverage"
    assert compact["status"] == "proved"
    assert compact["request_passed"] is True
    assert compact["proof_status_summary"]["all_theorem_ids_proved"] is True
    assert "evidence" not in compact
    assert compact["selected_evidence"]["coverage_complete"] is True
    assert compact["fingerprints"]["receipt_content_fingerprint"]


def test_package_cli_unified_certify_writes_gate_and_replay_reports(tmp_path) -> None:
    receipt_path = tmp_path / "receipt.json"
    gate_path = tmp_path / "gate.json"
    check_path = tmp_path / "receipt_check.json"
    replay_path = tmp_path / "replay.json"
    bundle_path = tmp_path / "bundle.json"
    bundle_check_path = tmp_path / "bundle_check.json"
    manifest_path = tmp_path / "artifact_manifest.json"
    manifest_check_path = tmp_path / "artifact_manifest_check.json"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "sparse-attention",
            "--context",
            "9",
            "--strides",
            "3,4,7",
            "--path-length",
            "2",
            "--local-window",
            "2",
            "--json-out",
            str(receipt_path),
            "--gate-report-out",
            str(gate_path),
            "--receipt-check-out",
            str(check_path),
            "--receipt-replay-check-out",
            str(replay_path),
            "--certification-bundle-out",
            str(bundle_path),
            "--certification-bundle-check-out",
            str(bundle_check_path),
            "--artifact-manifest-out",
            str(manifest_path),
            "--artifact-manifest-check-out",
            str(manifest_check_path),
            "--require-passed",
            "--require-status",
            "proved",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    saved_receipt = json.loads(receipt_path.read_text())
    gate_report = json.loads(gate_path.read_text())
    check_report = json.loads(check_path.read_text())
    replay_report = json.loads(replay_path.read_text())
    bundle = json.loads(bundle_path.read_text())
    bundle_check = json.loads(bundle_check_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    manifest_check = json.loads(manifest_check_path.read_text())

    assert receipt == saved_receipt
    assert gate_report["schema_id"] == "circle_calculus.ai_contract_receipt_file_check.v0"
    assert gate_report["ok"] is True
    assert gate_report["gate_policy"]["require_passed"] is True
    assert gate_report["summaries"][0]["path"] == str(receipt_path)
    assert check_report["ok"] is True
    assert check_report["summaries"][0]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]
    assert replay_report["schema_id"] == "circle_calculus.ai_contract_receipt_replay_check.v0"
    assert replay_report["ok"] is True
    assert replay_report["comparison"]["all_replay_fields_match"] is True
    assert bundle["schema_id"] == "circle_calculus.ai_contract_certification_bundle.v0"
    assert bundle["ok"] is True
    assert bundle["request_validation_report"]["ok"] is True
    assert bundle["receipt"]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]
    assert (
        bundle_check["schema_id"]
        == "circle_calculus.ai_contract_certification_bundle_file_check.v0"
    )
    assert bundle_check["ok"] is True
    assert manifest["schema_id"] == "circle_calculus.ai_contract_artifact_manifest.v0"
    assert manifest["kind"] == "sparse_attention_coverage"
    assert manifest["status"] == "proved"
    assert manifest["gate_policy"]["require_passed"] is True
    artifact_labels = {artifact["label"] for artifact in manifest["artifacts"]}
    assert {
        "receipt_json",
        "receipt_check",
        "receipt_replay_check",
        "gate_report",
        "certification_bundle",
        "certification_bundle_check",
    } <= artifact_labels
    assert (
        manifest_check["schema_id"]
        == "circle_calculus.ai_contract_artifact_manifest_file_check.v0"
    )
    assert manifest_check["ok"] is True


def test_package_cli_unified_certify_rejects_bundle_check_without_bundle(
    tmp_path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "recurrence",
            "--certification-bundle-check-out",
            str(tmp_path / "bundle_check.json"),
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 2
    assert (
        "--certification-bundle-check-out requires --certification-bundle-out"
        in result.stderr
    )


def test_package_cli_unified_certify_rejects_manifest_check_without_manifest(
    tmp_path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "recurrence",
            "--artifact-manifest-check-out",
            str(tmp_path / "artifact_manifest_check.json"),
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 2
    assert (
        "--artifact-manifest-check-out requires --artifact-manifest-out"
        in result.stderr
    )


def test_package_cli_unified_certify_artifact_dir_writes_full_bundle(
    tmp_path,
) -> None:
    artifact_dir = tmp_path / "artifacts"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "recurrence",
            "--artifact-dir",
            str(artifact_dir),
            "--artifact-prefix",
            "loop-check",
            "--require-passed",
            "--require-status",
            "proved",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["kind"] == "recurrence_schedule"

    expected_paths = {
        "request": artifact_dir / "loop-check_request.json",
        "request_validation": artifact_dir / "loop-check_request_validation.json",
        "receipt": artifact_dir / "loop-check_receipt.json",
        "compact_receipt": artifact_dir / "loop-check_compact_receipt.json",
        "receipt_check": artifact_dir / "loop-check_receipt_check.json",
        "receipt_replay_check": artifact_dir / "loop-check_receipt_replay_check.json",
        "gate_report": artifact_dir / "loop-check_gate_report.json",
        "certification_bundle": artifact_dir / "loop-check_certification_bundle.json",
        "certification_bundle_check": (
            artifact_dir / "loop-check_certification_bundle_check.json"
        ),
        "artifact_manifest": artifact_dir / "loop-check_artifact_manifest.json",
        "artifact_manifest_check": (
            artifact_dir / "loop-check_artifact_manifest_check.json"
        ),
    }
    assert all(path.exists() for path in expected_paths.values())
    manifest = json.loads(expected_paths["artifact_manifest"].read_text())
    compact_receipt = json.loads(expected_paths["compact_receipt"].read_text())
    manifest_check = json.loads(expected_paths["artifact_manifest_check"].read_text())
    assert manifest["artifact_prefix"] == "loop-check"
    assert manifest["artifact_dir"] == str(artifact_dir)
    assert manifest["artifact_count"] == 9
    assert compact_receipt["schema_id"] == CIRCLE_AI_CONTRACT_COMPACT_RECEIPT_SCHEMA_ID
    assert compact_receipt["fingerprints"]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]
    assert manifest_check["ok"] is True


def test_package_cli_unified_certify_rejects_artifact_prefix_without_dir() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "recurrence",
            "--artifact-prefix",
            "loop-check",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 2
    assert "--artifact-prefix requires --artifact-dir" in result.stderr


def test_package_cli_unified_certify_writes_failed_gate_report(tmp_path) -> None:
    gate_path = tmp_path / "failed_gate.json"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "rope",
            "--head-dim",
            "128",
            "--base",
            "10000",
            "--context",
            "1000",
            "--requested-margin",
            "1/999",
            "--gate-report-out",
            str(gate_path),
            "--require-passed",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )
    receipt = json.loads(result.stdout)
    gate_report = json.loads(gate_path.read_text())
    assert result.returncode == 2
    assert receipt["request_passed"] is False
    assert gate_report["ok"] is False
    assert gate_report["failure_count"] >= 1
    assert any("request_passed" in failure for failure in gate_report["failures"])


def test_package_cli_unified_certify_sparse_and_recurrence() -> None:
    sparse_result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "sparse-attention",
            "--context",
            "9",
            "--strides",
            "3,4,7",
            "--path-length",
            "2",
            "--local-window",
            "2",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    sparse_receipt = json.loads(sparse_result.stdout)
    assert sparse_receipt["kind"] == "sparse_attention_coverage"
    assert sparse_receipt["request_passed"] is True

    recurrence_result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "recurrence",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    recurrence_receipt = json.loads(recurrence_result.stdout)
    assert recurrence_receipt["kind"] == "recurrence_schedule"
    assert recurrence_receipt["request_passed"] is True


def test_package_cli_contract_receipt_from_request_file(tmp_path) -> None:
    request_out = tmp_path / "request.json"
    request_file = ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_receipt_main; "
                "sys.exit(contract_receipt_main())"
            ),
            "--request-file",
            str(request_file),
            "--request-out",
            str(request_out),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    request = json.loads(request_file.read_text())
    saved_request = json.loads(request_out.read_text())
    assert receipt["kind"] == "kv_cache_ring_buffer"
    assert receipt["request"] == saved_request
    assert saved_request["kind"] == "kv_cache_ring_buffer"
    assert saved_request["parameters"] == request["parameters"]
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True


def test_package_cli_contract_receipt_gate_accepts_ready_request_file() -> None:
    request_file = ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_receipt_main; "
                "sys.exit(contract_receipt_main())"
            ),
            "--request-file",
            str(request_file),
            "--require-passed",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "theorem_backed",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["kind"] == "kv_cache_ring_buffer"
    assert receipt["request_passed"] is True


def test_package_cli_contract_receipt_gate_rejects_failed_request() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_receipt_main; "
                "sys.exit(contract_receipt_main())"
            ),
            "--kind",
            "rope",
            "--parameters",
            json.dumps(
                {
                    "head_dim": 128,
                    "base": 10000.0,
                    "context": 1000,
                    "tolerance": 1e-6,
                    "discretization": "round",
                    "requested_margin": "1/999",
                }
            ),
            "--require-passed",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 2
    assert "contract receipt gate failed" in result.stderr
    receipt = json.loads(result.stdout)
    assert receipt["kind"] == "rope_position_distinguishability"
    assert receipt["status"] == "impossible"
    assert receipt["request_passed"] is False


def test_package_cli_contract_receipt_from_rope_model_config_json(
    tmp_path,
) -> None:
    config_path = tmp_path / "config.json"
    request_path = tmp_path / "request.json"
    import_report_path = tmp_path / "import_report.json"
    config_path.write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "max_position_embeddings": 4096,
                "rope_theta": 10000.0,
            }
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_receipt_main; "
                "sys.exit(contract_receipt_main())"
            ),
            "--kind",
            "rope",
            "--model-config-file",
            str(config_path),
            "--request-out",
            str(request_path),
            "--model-config-import-report-out",
            str(import_report_path),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["kind"] == "rope_position_distinguishability"
    assert receipt["request"]["parameters"]["head_dim"] == 128
    assert receipt["request"]["parameters"]["context"] == 4096
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
    request = json.loads(request_path.read_text())
    import_report = json.loads(import_report_path.read_text())
    assert request == receipt["request"]
    assert import_report["schema_id"] == "circle_calculus.rope_model_config_import.v0"
    assert import_report["ok"] is True
    assert import_report["request"] == request
    assert import_report["request_content_fingerprint"] == receipt[
        "request_content_fingerprint"
    ]


def test_package_cli_rejects_scaled_rope_model_config_with_report(
    tmp_path,
) -> None:
    config_path = tmp_path / "scaled_config.json"
    import_report_path = tmp_path / "scaled_import_report.json"
    config_path.write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "max_position_embeddings": 4096,
                "rope_theta": 10000.0,
                "rope_scaling": {"type": "linear", "factor": 4.0},
            }
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_receipt_main; "
                "sys.exit(contract_receipt_main())"
            ),
            "--kind",
            "rope",
            "--model-config-file",
            str(config_path),
            "--model-config-import-report-out",
            str(import_report_path),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 2
    assert "rope_scaling is outside the standard-RoPE importer" in result.stderr
    import_report = json.loads(import_report_path.read_text())
    assert import_report["schema_id"] == "circle_calculus.rope_model_config_import.v0"
    assert import_report["ok"] is False
    assert import_report["request"] is None
    assert import_report["unsupported_model_config_fields"] == ["rope_scaling"]
