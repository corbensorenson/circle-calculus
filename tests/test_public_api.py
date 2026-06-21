from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.core import finite_orbit, finite_period, is_full_coil
from circle_math.ai_contracts import (
    CONTRACT_PACK_SCHEMA_ID,
    build_contract_pack,
    build_rope_request_parameters_from_model_config,
    build_validated_contract_receipt_from_request,
    build_validated_rope_receipt_from_model_config,
)
from circle_math.contracts import contract_kinds, readiness_summary


ROOT = Path(__file__).resolve().parents[1]


def test_stable_core_api_examples() -> None:
    assert finite_orbit(12, 5) == [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7]
    assert finite_period(12, 4) == 3
    assert is_full_coil(13, 5) is True
    assert is_full_coil(12, 4) is False


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
                "from circle_math.cli import contract_ready_main, "
                "contract_receipt_main, rope_certify_main, "
                "sparse_attention_certify_main; "
                "print(callable(contract_ready_main), callable(rope_certify_main), "
                "callable(sparse_attention_certify_main), "
                "callable(contract_receipt_main))"
            ),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == "True True True True"


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
