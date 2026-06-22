from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

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
    architecture_config_contract_kind_hints,
    architecture_config_selected_contract_kinds,
    build_architecture_config_certification_bundle,
    build_architecture_config_import_json_schema,
    build_architecture_config_import_report,
    build_contract_certification_bundle,
    build_contract_certification_bundle_json_schema,
    build_contract_request_from_architecture_config,
    build_contract_pack,
    build_contract_runner_check_report,
    build_contract_runner_check_json_schema as build_facade_runner_check_json_schema,
    build_rope_model_config_certification_bundle,
    build_rope_model_config_import_report,
    build_rope_request_parameters_from_model_config,
    build_validated_contract_receipt_from_architecture_config,
    build_validated_contract_receipt_from_request,
    build_validated_rope_receipt_from_model_config,
)
from circle_math.applications import circle_ai_contracts as contract_pack_module
from circle_math.applications import (
    CIRCLE_AI_CONTRACT_COMPACT_RECEIPT_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_RECEIPT_SCHEMA_ID,
    build_contract_artifact_manifest,
    build_contract_artifact_manifest_file_check_report,
    build_contract_runner_check_json_schema,
    build_rope_model_config_import_json_schema,
)
from circle_math.contracts import contract_kinds, readiness_summary


ROOT = Path(__file__).resolve().parents[1]
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


def test_contract_pack_uses_packaged_theorem_status_index_without_repo_manifests(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(contract_pack_module, "ROOT", tmp_path)
    contract_pack_module._repo_manifest_entry_index.cache_clear()
    contract_pack_module._packaged_manifest_entry_index.cache_clear()
    contract_pack_module._manifest_entry_index.cache_clear()
    try:
        pack = contract_pack_module.build_contract_pack()
        sparse = readiness_summary(pack, "sparse_attention_coverage")
        sparse_contract = next(
            contract
            for contract in pack["contracts"]
            if contract["kind"] == "sparse_attention_coverage"
        )
        assert sparse.ready_for_downstream_fixture_use is True
        assert sparse.all_theorem_ids_proved is True
        assert sparse_contract["proof_status"]["source"] == (
            "circle_math/data/generated/theorem_status_index.json"
        )
    finally:
        contract_pack_module._repo_manifest_entry_index.cache_clear()
        contract_pack_module._packaged_manifest_entry_index.cache_clear()
        contract_pack_module._manifest_entry_index.cache_clear()


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

    bundle = build_rope_model_config_certification_bundle(
        model_config,
        pack=build_contract_pack(),
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
    )
    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is True
    assert bundle["model_config_import_report"]["request"] == receipt["request"]
    assert bundle["architecture_config_import_report"] is None


def test_rope_model_config_report_tracks_partial_rotary_head_dim_source() -> None:
    model_config = {
        "head_dim": 128,
        "partial_rotary_factor": 0.5,
        "max_position_embeddings": 8192,
        "rope_theta": 10000.0,
    }

    parameters = build_rope_request_parameters_from_model_config(model_config)
    assert parameters["head_dim"] == 64

    import_report = build_rope_model_config_import_report(model_config)
    jsonschema.validate(import_report, build_rope_model_config_import_json_schema())
    head_dim_source = import_report["parameter_sources"]["head_dim"]
    assert head_dim_source == {
        "source": "derived_config_fields",
        "fields": ["head_dim", "partial_rotary_factor"],
        "note": "head_dim adjusted by rotary fraction",
    }
    assert import_report["request"]["parameters"]["head_dim"] == 64


def test_rope_model_config_import_uses_explicit_rotary_dimension_alias() -> None:
    model_config = {
        "hidden_size": 4096,
        "num_attention_heads": 32,
        "qk_rope_head_dim": 64,
        "partial_rotary_factor": 0.5,
        "max_position_embeddings": 8192,
        "rope_theta": 10000.0,
    }

    parameters = build_rope_request_parameters_from_model_config(model_config)
    assert parameters["head_dim"] == 64

    import_report = build_rope_model_config_import_report(model_config)
    jsonschema.validate(import_report, build_rope_model_config_import_json_schema())
    assert import_report["parameter_sources"]["head_dim"] == {
        "source": "config_field",
        "field": "qk_rope_head_dim",
        "note": "explicit RoPE rotary dimension; rotary fraction was not reapplied",
    }
    assert import_report["request"]["parameters"]["head_dim"] == 64


def test_rope_model_config_import_uses_context_length_alias() -> None:
    model_config = {
        "hidden_size": 4096,
        "num_attention_heads": 32,
        "max_seq_len": 32768,
        "rotary_base": 500000.0,
    }

    parameters = build_rope_request_parameters_from_model_config(model_config)
    assert parameters["context"] == 32768
    assert parameters["base"] == 500000.0

    import_report = build_rope_model_config_import_report(model_config)
    jsonschema.validate(import_report, build_rope_model_config_import_json_schema())
    assert import_report["parameter_sources"]["base"] == {
        "source": "config_field",
        "field": "rotary_base",
    }
    assert import_report["parameter_sources"]["context"] == {
        "source": "config_field",
        "field": "max_seq_len",
    }
    assert import_report["request"]["parameters"]["context"] == 32768


def test_stable_request_api_builds_kv_cache_receipt() -> None:
    request = json.loads(
        (ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json").read_text()
    )

    receipt = build_validated_contract_receipt_from_request(request)
    assert receipt["kind"] == "kv_cache_ring_buffer"
    assert receipt["request"]["parameters"]["cache_size"] == 16
    assert receipt["request"]["parameters"]["request_id"] == "example_read_request"
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True

    bundle = build_contract_certification_bundle(
        request,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        require_passed=True,
    )
    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is True
    assert bundle["receipt"]["request"]["kind"] == "kv_cache_ring_buffer"
    assert bundle["receipt"]["request"]["parameters"] == request["parameters"]
    assert bundle["model_config_import_report"] is None
    assert bundle["architecture_config_import_report"] is None


def test_stable_architecture_config_api_builds_receipts() -> None:
    config = json.loads(ARCHITECTURE_CONFIG.read_text(encoding="utf-8"))

    rope_report = build_architecture_config_import_report(
        "rope",
        config,
    )
    jsonschema.validate(rope_report, build_architecture_config_import_json_schema())
    assert rope_report["ok"] is True
    assert rope_report["request"]["kind"] == "rope_position_distinguishability"
    rope_receipt = build_validated_contract_receipt_from_architecture_config(
        "rope",
        config,
    )
    assert rope_receipt["kind"] == "rope_position_distinguishability"
    assert rope_receipt["request_passed"] is True
    assert "rational_turn_ratio_finite_margin_certificate" in rope_receipt[
        "evidence"
    ]

    sparse_report = build_architecture_config_import_report(
        "sparse-attention",
        config,
    )
    jsonschema.validate(sparse_report, build_architecture_config_import_json_schema())
    assert sparse_report["ok"] is True

    sparse_request = build_contract_request_from_architecture_config(
        "sparse-attention",
        config,
    )
    assert sparse_request["kind"] == "sparse_attention_coverage"
    assert sparse_request["parameters"]["context"] == 9
    assert sparse_request["parameters"]["path_length"] == 2

    recurrence_receipt = build_validated_contract_receipt_from_architecture_config(
        "recurrence",
        config,
    )
    assert recurrence_receipt["kind"] == "recurrence_schedule"
    assert recurrence_receipt["request_passed"] is True
    assert recurrence_receipt["normalized_request"]["loop_period"] == 5

    sparse_bundle = build_architecture_config_certification_bundle(
        "sparse-attention",
        config,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        required_assurance_levels=("theorem_backed",),
        require_passed=True,
    )
    jsonschema.validate(sparse_bundle, build_contract_certification_bundle_json_schema())
    assert sparse_bundle["ok"] is True
    assert sparse_bundle["architecture_config_import_report"]["request"] == (
        sparse_request
    )
    assert sparse_bundle["model_config_import_report"] is None


def test_architecture_config_kind_hints_select_runner_contracts() -> None:
    architecture_config = json.loads(
        ROPE_MODEL_ONLY_ARCHITECTURE_CONFIG.read_text(encoding="utf-8")
    )

    assert architecture_config_selected_contract_kinds(
        architecture_config,
        ("rope", "kv-cache", "sparse-attention", "recurrence"),
    ) == ("rope_position_distinguishability",)
    assert architecture_config_contract_kind_hints(architecture_config) == (
        "rope_position_distinguishability",
    )

    report = build_contract_runner_check_report(
        architecture_configs=[architecture_config],
        architecture_config_source_paths=["configs/rope_model_only.json"],
    )

    jsonschema.validate(report, build_facade_runner_check_json_schema())
    assert report["ok"] is True
    assert report["example_count"] == 1
    assert report["gate_policy"]["require_no_unsupported_architecture_fields"] is False
    assert report["selected_kinds"] == ["rope_position_distinguishability"]
    summary = report["summaries"][0]
    assert summary["kind"] == "rope_position_distinguishability"
    assert summary["architecture_config_parameter_sources"]["head_dim"][
        "source"
    ] == "derived_architecture_config_field"
    assert summary["unsupported_architecture_config_fields"] == [
        "model.model_type"
    ]

    with pytest.raises(ValueError, match="must not be empty"):
        architecture_config_selected_contract_kinds(
            {"circle_ai_contract_kinds": []},
            ("rope",),
        )
    with pytest.raises(ValueError, match="not an architecture-config contract kind"):
        architecture_config_selected_contract_kinds(
            {"circle_ai_contract_kinds": ["seed-rule"]},
            ("rope",),
        )


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


def test_public_docs_show_architecture_config_runner_handoff() -> None:
    readme = (ROOT / "README.md").read_text()
    public_api = (ROOT / "docs" / "PUBLIC_API.md").read_text()
    use_as_library = (ROOT / "docs" / "USE_AS_LIBRARY.md").read_text()

    assert (
        "--architecture-config-file "
        "examples/circle_ai_architecture_configs/basic_transformer_contract_config.json"
    ) in readme
    assert "--artifact-dir reports/circle_ai_contract_batch" in readme
    assert "--artifact-prefix architecture-suite" in readme
    assert (
        "circle-ai-certify rope \\\n"
        "  --architecture-config-file "
        "examples/circle_ai_architecture_configs/basic_transformer_contract_config.json"
    ) in public_api
    assert "Architecture configs emit RoPE, KV-cache" in public_api.replace("\n", " ")
    assert "--artifact-dir /tmp/circle_ai_contract_batch" in public_api
    assert "circle-ai-certify rope --architecture-config-file" in use_as_library
    assert "--artifact-dir /tmp/circle_ai_contract_batch" in use_as_library


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


def test_package_cli_unified_certify_batch_request_files_writes_compact_receipts(
    tmp_path,
) -> None:
    receipt_dir = tmp_path / "receipts"
    compact_dir = tmp_path / "compact_receipts"
    report_path = tmp_path / "runner_report.json"
    request_dir = ROOT / "examples" / "circle_ai_requests"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "batch",
            "--request-file",
            str(request_dir / "kv_cache_request.json"),
            "--request-file",
            str(request_dir / "sparse_attention_request.json"),
            "--receipt-out-dir",
            str(receipt_dir),
            "--compact-receipt-out-dir",
            str(compact_dir),
            "--report-out",
            str(report_path),
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

    report = json.loads(result.stdout)
    saved_report = json.loads(report_path.read_text())
    assert saved_report == report
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    assert report["schema_id"] == "circle_calculus.ai_contract_runner_check.v0"
    assert report["ok"] is True
    assert report["example_count"] == 2
    assert report["failure_count"] == 0
    assert report["gate_policy"]["allowed_statuses"] == ["proved"]
    assert report["gate_policy"]["allowed_decision_verdicts"] == ["passed"]
    assert {summary["kind"] for summary in report["summaries"]} == {
        "kv_cache_ring_buffer",
        "sparse_attention_coverage",
    }

    for summary in report["summaries"]:
        receipt_path = Path(summary["receipt_path"])
        compact_path = Path(summary["compact_receipt_path"])
        assert receipt_path.exists()
        assert compact_path.exists()
        receipt = json.loads(receipt_path.read_text())
        compact = json.loads(compact_path.read_text())
        assert receipt["receipt_content_fingerprint"] == summary[
            "receipt_content_fingerprint"
        ]
        assert compact["schema_id"] == CIRCLE_AI_CONTRACT_COMPACT_RECEIPT_SCHEMA_ID
        assert compact["fingerprints"]["receipt_content_fingerprint"] == summary[
            "receipt_content_fingerprint"
        ]
        assert summary["compact_selected_evidence_count"] >= 1
        assert summary["compact_selected_evidence_unclassified_count"] == 0
        assert "unclassified" not in summary["compact_selected_evidence_labels"]


def test_package_cli_unified_certify_batch_model_configs_write_import_reports(
    tmp_path,
) -> None:
    receipt_dir = tmp_path / "receipts"
    compact_dir = tmp_path / "compact_receipts"
    import_dir = tmp_path / "imports"
    report_path = tmp_path / "runner_report.json"
    config_file = (
        ROOT / "examples" / "circle_ai_model_configs" / "standard_rope_config.json"
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
            "batch",
            "--model-config-file",
            str(config_file),
            "--model-config-import-report-out-dir",
            str(import_dir),
            "--receipt-out-dir",
            str(receipt_dir),
            "--compact-receipt-out-dir",
            str(compact_dir),
            "--report-out",
            str(report_path),
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

    report = json.loads(result.stdout)
    saved_report = json.loads(report_path.read_text())
    assert saved_report == report
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    assert report["ok"] is True
    assert report["example_count"] == 1
    assert report["gate_policy"]["require_no_unsupported_architecture_fields"] is False
    assert report["selected_kinds"] == ["rope_position_distinguishability"]
    summary = report["summaries"][0]
    assert summary["source_type"] == "model_config"
    assert summary["kind"] == "rope_position_distinguishability"
    assert summary["status"] == "proved"
    assert summary["decision_verdict"] == "passed"
    assert summary["model_config_parameter_sources"]["head_dim"]["source"] == (
        "derived_config_fields"
    )
    assert summary["model_config_parameter_sources"]["base"]["field"] == "rope_theta"
    assert summary["model_config_parameter_sources"]["context"]["field"] == (
        "max_position_embeddings"
    )
    import_report = json.loads(
        Path(summary["model_config_import_report_path"]).read_text()
    )
    assert import_report["schema_id"] == "circle_calculus.rope_model_config_import.v0"
    assert import_report["ok"] is True
    receipt = json.loads(Path(summary["receipt_path"]).read_text())
    compact = json.loads(Path(summary["compact_receipt_path"]).read_text())
    assert receipt["request"]["parameters"]["context"] == 131072
    assert compact["fingerprints"]["receipt_content_fingerprint"] == summary[
        "receipt_content_fingerprint"
    ]
    assert summary["compact_selected_evidence_unclassified_count"] == 0


def test_package_cli_unified_certify_batch_architecture_config_writes_import_reports(
    tmp_path,
) -> None:
    receipt_dir = tmp_path / "receipts"
    compact_dir = tmp_path / "compact_receipts"
    import_dir = tmp_path / "architecture_imports"
    report_path = tmp_path / "runner_report.json"

    result = subprocess.run(
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
            "--architecture-config-import-report-out-dir",
            str(import_dir),
            "--receipt-out-dir",
            str(receipt_dir),
            "--compact-receipt-out-dir",
            str(compact_dir),
            "--report-out",
            str(report_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )

    report = json.loads(result.stdout)
    saved_report = json.loads(report_path.read_text())
    assert saved_report == report
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    assert report["ok"] is True
    assert report["example_count"] == 4
    assert report["selected_kinds"] == [
        "kv_cache_ring_buffer",
        "recurrence_schedule",
        "rope_position_distinguishability",
        "sparse_attention_coverage",
    ]
    architecture_summaries = [
        summary
        for summary in report["summaries"]
        if summary["source_type"] == "architecture_config"
    ]
    assert len(architecture_summaries) == 4
    assert all(
        summary["unsupported_architecture_config_fields"] == []
        for summary in architecture_summaries
    )

    unsupported_architecture_report = build_contract_runner_check_report(
        architecture_configs=[
            {
                "recurrence": {
                    "period": 5,
                    "horizon_steps": 7,
                    "shift_amount": 15,
                    "adaptive_exit_policy": "entropy",
                }
            }
        ],
        architecture_config_kinds=("recurrence",),
    )
    jsonschema.validate(
        unsupported_architecture_report,
        build_facade_runner_check_json_schema(),
    )
    assert unsupported_architecture_report["ok"] is True
    assert unsupported_architecture_report["summaries"][0][
        "unsupported_architecture_config_fields"
    ] == ["recurrence.adaptive_exit_policy"]

    strict_unsupported_architecture_report = build_contract_runner_check_report(
        architecture_configs=[
            {
                "recurrence": {
                    "period": 5,
                    "horizon_steps": 7,
                    "shift_amount": 15,
                    "adaptive_exit_policy": "entropy",
                }
            }
        ],
        architecture_config_kinds=("recurrence",),
        require_no_unsupported_architecture_fields=True,
    )
    jsonschema.validate(
        strict_unsupported_architecture_report,
        build_facade_runner_check_json_schema(),
    )
    assert strict_unsupported_architecture_report["ok"] is False
    assert strict_unsupported_architecture_report["gate_policy"][
        "require_no_unsupported_architecture_fields"
    ] is True
    assert any(
        "unsupported architecture-config fields: recurrence.adaptive_exit_policy"
        in failure
        for failure in strict_unsupported_architecture_report["failures"]
    )
    assert {summary["source_type"] for summary in report["summaries"]} == {
        "architecture_config"
    }
    assert {summary["kind"] for summary in report["summaries"]} == {
        "kv_cache_ring_buffer",
        "rope_position_distinguishability",
        "sparse_attention_coverage",
        "recurrence_schedule",
    }

    for summary in report["summaries"]:
        import_report = json.loads(
            Path(summary["architecture_config_import_report_path"]).read_text()
        )
        jsonschema.validate(
            import_report,
            build_architecture_config_import_json_schema(),
        )
        assert import_report["ok"] is True
        assert summary["architecture_config_parameter_sources"] == (
            import_report["parameter_sources"]
        )
        assert summary["model_config_import_report_path"] is None
        assert summary["model_config_parameter_sources"] is None
        receipt = json.loads(Path(summary["receipt_path"]).read_text())
        compact = json.loads(Path(summary["compact_receipt_path"]).read_text())
        assert receipt["kind"] == summary["kind"]
        assert compact["fingerprints"]["receipt_content_fingerprint"] == summary[
            "receipt_content_fingerprint"
        ]
        assert summary["compact_selected_evidence_unclassified_count"] == 0


def test_package_cli_batch_honors_architecture_config_kind_hints(tmp_path) -> None:
    receipt_dir = tmp_path / "receipts"
    compact_dir = tmp_path / "compact_receipts"
    import_dir = tmp_path / "architecture_imports"

    result = subprocess.run(
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
            "--architecture-config-import-report-out-dir",
            str(import_dir),
            "--receipt-out-dir",
            str(receipt_dir),
            "--compact-receipt-out-dir",
            str(compact_dir),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )

    report = json.loads(result.stdout)
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    assert report["ok"] is True
    assert report["example_count"] == 1
    assert report["selected_kinds"] == ["rope_position_distinguishability"]
    summary = report["summaries"][0]
    assert summary["source_type"] == "architecture_config"
    assert summary["kind"] == "rope_position_distinguishability"
    assert summary["architecture_config_parameter_sources"]["head_dim"][
        "source"
    ] == "derived_architecture_config_field"
    assert summary["unsupported_architecture_config_fields"] == [
        "model.model_type"
    ]
    import_report = json.loads(
        Path(summary["architecture_config_import_report_path"]).read_text()
    )
    assert import_report["request"] == json.loads(
        Path(summary["receipt_path"]).read_text()
    )["request"]


def test_package_cli_batch_rejects_unsupported_architecture_fields_when_required(
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
            "batch",
            "--architecture-config-file",
            str(ROPE_MODEL_ONLY_ARCHITECTURE_CONFIG),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-passed",
            "--require-no-unsupported-architecture-fields",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    assert report["ok"] is False
    assert report["gate_policy"]["require_no_unsupported_architecture_fields"] is True
    assert report["failure_count"] == 1
    assert any(
        "unsupported architecture-config fields: model.model_type" in failure
        for failure in report["failures"]
    )
    assert report["summaries"][0]["unsupported_architecture_config_fields"] == [
        "model.model_type"
    ]


def test_package_cli_unified_certify_batch_artifact_dir_writes_portable_set(
    tmp_path,
) -> None:
    artifact_dir = tmp_path / "architecture_contracts"

    result = subprocess.run(
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
        text=True,
        capture_output=True,
        check=True,
    )

    report = json.loads(result.stdout)
    report_path = artifact_dir / "architecture-suite_runner_check.json"
    assert json.loads(report_path.read_text()) == report
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    assert report["ok"] is True
    assert report["example_count"] == 4
    assert report["selected_kinds"] == [
        "kv_cache_ring_buffer",
        "recurrence_schedule",
        "rope_position_distinguishability",
        "sparse_attention_coverage",
    ]

    expected_dirs = {
        "receipts",
        "compact_receipts",
        "architecture_config_import_reports",
        "request_validation_reports",
        "certification_bundles",
        "certification_bundle_checks",
    }
    assert expected_dirs.issubset(
        {path.name for path in artifact_dir.iterdir() if path.is_dir()}
    )

    for summary in report["summaries"]:
        for key in (
            "receipt_path",
            "compact_receipt_path",
            "architecture_config_import_report_path",
            "request_validation_report_path",
            "certification_bundle_path",
            "certification_bundle_check_path",
        ):
            assert summary[key] is not None
            assert Path(summary[key]).exists()

        request_validation = json.loads(
            Path(summary["request_validation_report_path"]).read_text()
        )
        assert request_validation["ok"] is True
        bundle = json.loads(Path(summary["certification_bundle_path"]).read_text())
        jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
        assert bundle["ok"] is True
        bundle_check = json.loads(
            Path(summary["certification_bundle_check_path"]).read_text()
        )
        assert bundle_check["ok"] is True
        assert summary["compact_selected_evidence_unclassified_count"] == 0


def test_package_cli_unified_certify_batch_gate_writes_report_on_failure(
    tmp_path,
) -> None:
    receipt_dir = tmp_path / "receipts"
    compact_dir = tmp_path / "compact_receipts"
    report_path = tmp_path / "runner_report.json"
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
            "batch",
            "--request-file",
            str(request_file),
            "--receipt-out-dir",
            str(receipt_dir),
            "--compact-receipt-out-dir",
            str(compact_dir),
            "--report-out",
            str(report_path),
            "--require-decision",
            "failed",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    saved_report = json.loads(report_path.read_text())
    assert saved_report == report
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    assert report["ok"] is False
    assert report["example_count"] == 1
    assert report["failure_count"] == 1
    assert "decision.verdict 'passed' is not in ('failed',)" in report["failures"][0]
    assert report["summaries"][0]["decision_verdict"] == "passed"
    assert Path(report["summaries"][0]["receipt_path"]).exists()
    assert Path(report["summaries"][0]["compact_receipt_path"]).exists()


def test_package_cli_unified_certify_batch_requires_a_source() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "batch",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert (
        "at least one --request-file, --model-config-file, or "
        "--architecture-config-file is required"
    ) in (
        result.stderr
    )


def test_public_api_runner_check_report_builds_from_in_memory_sources() -> None:
    request = json.loads(
        (ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json").read_text()
    )
    model_config = json.loads(
        (
            ROOT
            / "examples"
            / "circle_ai_model_configs"
            / "standard_rope_config.json"
        ).read_text()
    )
    architecture_config = json.loads(ARCHITECTURE_CONFIG.read_text())

    report = build_contract_runner_check_report(
        requests=[request],
        model_configs=[model_config],
        architecture_configs=[architecture_config],
        request_source_paths=["requests/kv_cache_request.json"],
        model_config_source_paths=["configs/standard_rope_config.json"],
        architecture_config_source_paths=["configs/basic_transformer.json"],
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        require_passed=True,
    )

    jsonschema.validate(report, build_facade_runner_check_json_schema())
    assert report["ok"] is True
    assert report["example_count"] == 6
    assert report["failure_count"] == 0
    assert report["gate_policy"]["allowed_statuses"] == ["proved"]
    assert report["gate_policy"]["allowed_decision_verdicts"] == ["passed"]
    assert report["gate_policy"]["require_passed"] is True
    assert report["gate_policy"]["require_no_unsupported_architecture_fields"] is False
    assert report["selected_kinds"] == [
        "kv_cache_ring_buffer",
        "recurrence_schedule",
        "rope_position_distinguishability",
        "sparse_attention_coverage",
    ]
    summaries_by_type = {
        summary["source_type"]: summary for summary in report["summaries"]
    }
    assert summaries_by_type["request"]["source_path"] == (
        "requests/kv_cache_request.json"
    )
    assert summaries_by_type["request"]["kind"] == "kv_cache_ring_buffer"
    model_summary = summaries_by_type["model_config"]
    assert model_summary["source_path"] == "configs/standard_rope_config.json"
    assert model_summary["kind"] == "rope_position_distinguishability"
    assert model_summary["model_config_parameter_sources"]["head_dim"]["source"] == (
        "derived_config_fields"
    )
    architecture_summaries = [
        summary
        for summary in report["summaries"]
        if summary["source_type"] == "architecture_config"
    ]
    assert len(architecture_summaries) == 4
    assert {summary["kind"] for summary in architecture_summaries} == {
        "kv_cache_ring_buffer",
        "rope_position_distinguishability",
        "sparse_attention_coverage",
        "recurrence_schedule",
    }
    for summary in architecture_summaries:
        assert summary["source_path"] == "configs/basic_transformer.json"
        assert summary["architecture_config_parameter_sources"]
        assert summary["model_config_parameter_sources"] is None
    assert model_summary["compact_selected_evidence_unclassified_count"] == 0


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


def test_package_cli_unified_certify_batch_rejects_artifact_prefix_without_dir() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "batch",
            "--request-file",
            str(ROOT / "examples" / "circle_ai_requests" / "kv_cache_request.json"),
            "--artifact-prefix",
            "bad-batch",
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


def test_package_cli_unified_certify_architecture_config(
    tmp_path: Path,
) -> None:
    rope_import_report_path = tmp_path / "rope_architecture_import.json"
    rope_bundle_path = tmp_path / "rope_bundle.json"
    rope_result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from circle_math.cli import contract_certify_main; "
                "sys.exit(contract_certify_main())"
            ),
            "rope",
            "--architecture-config-file",
            str(ARCHITECTURE_CONFIG),
            "--architecture-config-import-report-out",
            str(rope_import_report_path),
            "--certification-bundle-out",
            str(rope_bundle_path),
            "--format",
            "json",
            "--require-passed",
            "--require-status",
            "proved",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    rope_receipt = json.loads(rope_result.stdout)
    assert rope_receipt["kind"] == "rope_position_distinguishability"
    assert rope_receipt["request"]["parameters"]["turn_ratio_denominator"] == 4099
    assert rope_receipt["request_passed"] is True
    rope_import_report = json.loads(
        rope_import_report_path.read_text(encoding="utf-8")
    )
    rope_bundle = json.loads(rope_bundle_path.read_text(encoding="utf-8"))
    jsonschema.validate(
        rope_import_report,
        build_architecture_config_import_json_schema(),
    )
    jsonschema.validate(rope_bundle, build_contract_certification_bundle_json_schema())
    assert rope_import_report["request"]["kind"] == "rope_position_distinguishability"
    assert rope_bundle["architecture_config_import_report"] == rope_import_report
    assert rope_bundle["model_config_import_report"] is None

    sparse_import_report_path = tmp_path / "sparse_architecture_import.json"
    sparse_bundle_path = tmp_path / "sparse_bundle.json"
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
            "--architecture-config-file",
            str(ARCHITECTURE_CONFIG),
            "--architecture-config-import-report-out",
            str(sparse_import_report_path),
            "--certification-bundle-out",
            str(sparse_bundle_path),
            "--format",
            "json",
            "--require-passed",
            "--require-status",
            "proved",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    sparse_receipt = json.loads(sparse_result.stdout)
    assert sparse_receipt["kind"] == "sparse_attention_coverage"
    assert sparse_receipt["request"]["parameters"]["strides"] == [3, 4, 7]
    assert sparse_receipt["request_passed"] is True
    sparse_import_report = json.loads(
        sparse_import_report_path.read_text(encoding="utf-8")
    )
    sparse_bundle = json.loads(sparse_bundle_path.read_text(encoding="utf-8"))
    jsonschema.validate(
        sparse_import_report,
        build_architecture_config_import_json_schema(),
    )
    jsonschema.validate(sparse_bundle, build_contract_certification_bundle_json_schema())
    assert sparse_import_report["request"]["kind"] == "sparse_attention_coverage"
    assert sparse_bundle["architecture_config_import_report"] == sparse_import_report
    assert sparse_bundle["model_config_import_report"] is None

    recurrence_import_report_path = tmp_path / "recurrence_architecture_import.json"
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
            "--architecture-config-file",
            str(ARCHITECTURE_CONFIG),
            "--architecture-config-import-report-out",
            str(recurrence_import_report_path),
            "--sample-index",
            "9",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    recurrence_receipt = json.loads(recurrence_result.stdout)
    assert recurrence_receipt["kind"] == "recurrence_schedule"
    assert recurrence_receipt["normalized_request"]["sample_index"] == 9
    recurrence_import_report = json.loads(
        recurrence_import_report_path.read_text(encoding="utf-8")
    )
    jsonschema.validate(
        recurrence_import_report,
        build_architecture_config_import_json_schema(),
    )
    assert recurrence_import_report["request"]["parameters"]["sample_index"] == 9


@pytest.mark.parametrize(
    ("subcommand_args", "expected_kind"),
    [
        (["strided-fanout"], "strided_candidate_fanout"),
        (["cyclic-memory"], "cyclic_memory_residue_winding"),
        (["multicoil-phase"], "multicoil_phase_feature"),
        (["cyclic-mixer"], "circulant_block_cyclic_mixer"),
        (["seed-rule"], "seed_rule_exact_regeneration"),
    ],
)
def test_package_cli_unified_certify_extended_ready_contracts(
    subcommand_args: list[str],
    expected_kind: str,
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
            *subcommand_args,
            "--format",
            "compact-json",
            "--require-status",
            "proved",
            "--require-passed",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    compact_receipt = json.loads(result.stdout)
    assert compact_receipt["kind"] == expected_kind
    assert compact_receipt["status"] == "proved"
    assert compact_receipt["request_passed"] is True
    assert compact_receipt["proof_status_summary"]["all_theorem_ids_proved"] is True
    assert compact_receipt["recommendation_ids"]


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


def test_package_cli_contract_receipt_from_rope_model_config_directory(
    tmp_path,
) -> None:
    config_dir = tmp_path / "model"
    config_dir.mkdir()
    request_path = tmp_path / "request.json"
    import_report_path = tmp_path / "import_report.json"
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "qk_rope_head_dim": 64,
                "max_position_embeddings": 8192,
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
            str(config_dir),
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
    import_report = json.loads(import_report_path.read_text())
    assert receipt["request"]["parameters"]["head_dim"] == 64
    assert import_report["parameter_sources"]["head_dim"]["field"] == (
        "qk_rope_head_dim"
    )
    assert json.loads(request_path.read_text()) == receipt["request"]


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
