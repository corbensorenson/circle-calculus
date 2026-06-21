from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications.circle_ai_contracts import (
    ACCEPTANCE_POLICY_SCHEMA_PATH,
    ACCEPTANCE_POLICY_REPORT_SCHEMA_PATH,
    ACCEPTANCE_RECEIPT_SCHEMA_PATH,
    DOWNSTREAM_REJECTION_REPORT_SCHEMA_PATH,
    build_acceptance_policy_report_json_schema,
    build_acceptance_policy_json_schema,
    build_acceptance_receipt_json_schema,
    build_contract_pack,
    build_contract_pack_json_schema,
    build_downstream_rejection_report_json_schema,
)
from circle_math.applications.circle_ai_contract_runner import (
    ARTIFACT_MANIFEST_SCHEMA_PATH as CONTRACT_ARTIFACT_MANIFEST_SCHEMA_PATH,
    CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH as CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH,
    CERTIFICATION_BUNDLE_SCHEMA_PATH as CONTRACT_CERTIFICATION_BUNDLE_SCHEMA_PATH,
    RECEIPT_SCHEMA_PATH as CONTRACT_RUNNER_RECEIPT_SCHEMA_PATH,
    RECEIPT_FILE_CHECK_SCHEMA_PATH as CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_PATH,
    REQUEST_SCHEMA_PATH as CONTRACT_RUNNER_REQUEST_SCHEMA_PATH,
    REQUEST_VALIDATION_SCHEMA_PATH as CONTRACT_RUNNER_REQUEST_VALIDATION_SCHEMA_PATH,
    ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH,
    RUNNER_CHECK_SCHEMA_PATH as CONTRACT_RUNNER_CHECK_SCHEMA_PATH,
    build_contract_artifact_manifest_json_schema,
    build_contract_certification_bundle_file_check_json_schema,
    build_contract_certification_bundle_json_schema,
    build_contract_runner_check_json_schema,
    build_contract_receipt_file_check_json_schema,
    build_contract_receipt_json_schema,
    build_contract_request_json_schema,
    build_contract_request_validation_json_schema,
    build_rope_model_config_import_json_schema,
)


DEFAULT_OUT = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_ACCEPTANCE_POLICY_SCHEMA_OUT = ROOT / ACCEPTANCE_POLICY_SCHEMA_PATH
DEFAULT_ACCEPTANCE_POLICY_REPORT_SCHEMA_OUT = ROOT / ACCEPTANCE_POLICY_REPORT_SCHEMA_PATH
DEFAULT_ACCEPTANCE_RECEIPT_SCHEMA_OUT = ROOT / ACCEPTANCE_RECEIPT_SCHEMA_PATH
DEFAULT_DOWNSTREAM_REJECTION_REPORT_SCHEMA_OUT = (
    ROOT / DOWNSTREAM_REJECTION_REPORT_SCHEMA_PATH
)
DEFAULT_CONTRACT_RUNNER_REQUEST_SCHEMA_OUT = ROOT / CONTRACT_RUNNER_REQUEST_SCHEMA_PATH
DEFAULT_CONTRACT_RUNNER_REQUEST_VALIDATION_SCHEMA_OUT = (
    ROOT / CONTRACT_RUNNER_REQUEST_VALIDATION_SCHEMA_PATH
)
DEFAULT_CONTRACT_RUNNER_RECEIPT_SCHEMA_OUT = ROOT / CONTRACT_RUNNER_RECEIPT_SCHEMA_PATH
DEFAULT_CONTRACT_RUNNER_CHECK_SCHEMA_OUT = ROOT / CONTRACT_RUNNER_CHECK_SCHEMA_PATH
DEFAULT_ROPE_MODEL_CONFIG_IMPORT_SCHEMA_OUT = ROOT / ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH
DEFAULT_CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_OUT = (
    ROOT / CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_PATH
)
DEFAULT_CONTRACT_CERTIFICATION_BUNDLE_SCHEMA_OUT = (
    ROOT / CONTRACT_CERTIFICATION_BUNDLE_SCHEMA_PATH
)
DEFAULT_CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_OUT = (
    ROOT / CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH
)
DEFAULT_CONTRACT_ARTIFACT_MANIFEST_SCHEMA_OUT = (
    ROOT / CONTRACT_ARTIFACT_MANIFEST_SCHEMA_PATH
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export the public standalone Circle AI contract pack.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output JSON path. Defaults to site/data/generated/circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--schema-out",
        help=(
            "Output JSON Schema path. Defaults to the pack output path with "
            ".schema.json suffix."
        ),
    )
    parser.add_argument(
        "--acceptance-policy-schema-out",
        default=str(DEFAULT_ACCEPTANCE_POLICY_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for acceptance-policy lockfiles. Defaults "
            "to site/data/generated/circle_ai_contract_acceptance_policy.schema.json."
        ),
    )
    parser.add_argument(
        "--acceptance-policy-report-schema-out",
        default=str(DEFAULT_ACCEPTANCE_POLICY_REPORT_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for acceptance-policy reports. Defaults "
            "to site/data/generated/circle_ai_contract_acceptance_policy_report.schema.json."
        ),
    )
    parser.add_argument(
        "--acceptance-receipt-schema-out",
        default=str(DEFAULT_ACCEPTANCE_RECEIPT_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for acceptance receipts. Defaults to "
            "site/data/generated/circle_ai_contract_acceptance_receipt.schema.json."
        ),
    )
    parser.add_argument(
        "--downstream-rejection-report-schema-out",
        default=str(DEFAULT_DOWNSTREAM_REJECTION_REPORT_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for standalone downstream rejection "
            "reports. Defaults to "
            "site/data/generated/circle_ai_downstream_rejection_report.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-runner-request-schema-out",
        default=str(DEFAULT_CONTRACT_RUNNER_REQUEST_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for parameterized contract-runner requests. "
            "Defaults to site/data/generated/circle_ai_contract_request.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-runner-receipt-schema-out",
        default=str(DEFAULT_CONTRACT_RUNNER_RECEIPT_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for parameterized contract-runner receipts. "
            "Defaults to site/data/generated/circle_ai_contract_receipt.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-runner-request-validation-schema-out",
        default=str(DEFAULT_CONTRACT_RUNNER_REQUEST_VALIDATION_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for contract-runner request validation "
            "reports. Defaults to "
            "site/data/generated/circle_ai_contract_request_validation.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-runner-check-schema-out",
        default=str(DEFAULT_CONTRACT_RUNNER_CHECK_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for contract-runner batch check reports. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_runner_check.schema.json."
        ),
    )
    parser.add_argument(
        "--rope-model-config-import-schema-out",
        default=str(DEFAULT_ROPE_MODEL_CONFIG_IMPORT_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for standard-RoPE model config import "
            "reports. Defaults to "
            "site/data/generated/circle_ai_rope_model_config_import.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-receipt-file-check-schema-out",
        default=str(DEFAULT_CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for saved receipt-file check reports. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_receipt_file_check.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-certification-bundle-schema-out",
        default=str(DEFAULT_CONTRACT_CERTIFICATION_BUNDLE_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for Python API certification bundles. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_certification_bundle.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-certification-bundle-file-check-schema-out",
        default=str(DEFAULT_CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for saved certification-bundle check "
            "reports. Defaults to "
            "site/data/generated/"
            "circle_ai_contract_certification_bundle_file_check.schema.json."
        ),
    )
    parser.add_argument(
        "--contract-artifact-manifest-schema-out",
        default=str(DEFAULT_CONTRACT_ARTIFACT_MANIFEST_SCHEMA_OUT),
        help=(
            "Output JSON Schema path for standard artifact-directory manifests. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_artifact_manifest.schema.json."
        ),
    )
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    schema_out = Path(args.schema_out) if args.schema_out else out.with_suffix(".schema.json")
    if not schema_out.is_absolute():
        schema_out = ROOT / schema_out
    policy_schema_out = Path(args.acceptance_policy_schema_out)
    if not policy_schema_out.is_absolute():
        policy_schema_out = ROOT / policy_schema_out
    policy_report_schema_out = Path(args.acceptance_policy_report_schema_out)
    if not policy_report_schema_out.is_absolute():
        policy_report_schema_out = ROOT / policy_report_schema_out
    receipt_schema_out = Path(args.acceptance_receipt_schema_out)
    if not receipt_schema_out.is_absolute():
        receipt_schema_out = ROOT / receipt_schema_out
    rejection_report_schema_out = Path(args.downstream_rejection_report_schema_out)
    if not rejection_report_schema_out.is_absolute():
        rejection_report_schema_out = ROOT / rejection_report_schema_out
    runner_request_schema_out = Path(args.contract_runner_request_schema_out)
    if not runner_request_schema_out.is_absolute():
        runner_request_schema_out = ROOT / runner_request_schema_out
    runner_receipt_schema_out = Path(args.contract_runner_receipt_schema_out)
    if not runner_receipt_schema_out.is_absolute():
        runner_receipt_schema_out = ROOT / runner_receipt_schema_out
    runner_request_validation_schema_out = Path(
        args.contract_runner_request_validation_schema_out
    )
    if not runner_request_validation_schema_out.is_absolute():
        runner_request_validation_schema_out = ROOT / runner_request_validation_schema_out
    runner_check_schema_out = Path(args.contract_runner_check_schema_out)
    if not runner_check_schema_out.is_absolute():
        runner_check_schema_out = ROOT / runner_check_schema_out
    rope_model_config_import_schema_out = Path(
        args.rope_model_config_import_schema_out
    )
    if not rope_model_config_import_schema_out.is_absolute():
        rope_model_config_import_schema_out = ROOT / rope_model_config_import_schema_out
    receipt_file_check_schema_out = Path(args.contract_receipt_file_check_schema_out)
    if not receipt_file_check_schema_out.is_absolute():
        receipt_file_check_schema_out = ROOT / receipt_file_check_schema_out
    certification_bundle_schema_out = Path(
        args.contract_certification_bundle_schema_out
    )
    if not certification_bundle_schema_out.is_absolute():
        certification_bundle_schema_out = ROOT / certification_bundle_schema_out
    certification_bundle_file_check_schema_out = Path(
        args.contract_certification_bundle_file_check_schema_out
    )
    if not certification_bundle_file_check_schema_out.is_absolute():
        certification_bundle_file_check_schema_out = (
            ROOT / certification_bundle_file_check_schema_out
        )
    artifact_manifest_schema_out = Path(args.contract_artifact_manifest_schema_out)
    if not artifact_manifest_schema_out.is_absolute():
        artifact_manifest_schema_out = ROOT / artifact_manifest_schema_out
    out.parent.mkdir(parents=True, exist_ok=True)
    schema_out.parent.mkdir(parents=True, exist_ok=True)
    policy_schema_out.parent.mkdir(parents=True, exist_ok=True)
    policy_report_schema_out.parent.mkdir(parents=True, exist_ok=True)
    receipt_schema_out.parent.mkdir(parents=True, exist_ok=True)
    rejection_report_schema_out.parent.mkdir(parents=True, exist_ok=True)
    runner_request_schema_out.parent.mkdir(parents=True, exist_ok=True)
    runner_receipt_schema_out.parent.mkdir(parents=True, exist_ok=True)
    runner_request_validation_schema_out.parent.mkdir(parents=True, exist_ok=True)
    runner_check_schema_out.parent.mkdir(parents=True, exist_ok=True)
    rope_model_config_import_schema_out.parent.mkdir(parents=True, exist_ok=True)
    receipt_file_check_schema_out.parent.mkdir(parents=True, exist_ok=True)
    certification_bundle_schema_out.parent.mkdir(parents=True, exist_ok=True)
    certification_bundle_file_check_schema_out.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    artifact_manifest_schema_out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_contract_pack(), indent=2, sort_keys=True) + "\n")
    schema_out.write_text(
        json.dumps(build_contract_pack_json_schema(), indent=2, sort_keys=True) + "\n"
    )
    policy_schema_out.write_text(
        json.dumps(build_acceptance_policy_json_schema(), indent=2, sort_keys=True)
        + "\n"
    )
    policy_report_schema_out.write_text(
        json.dumps(
            build_acceptance_policy_report_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    receipt_schema_out.write_text(
        json.dumps(build_acceptance_receipt_json_schema(), indent=2, sort_keys=True)
        + "\n"
    )
    rejection_report_schema_out.write_text(
        json.dumps(
            build_downstream_rejection_report_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    runner_request_schema_out.write_text(
        json.dumps(build_contract_request_json_schema(), indent=2, sort_keys=True)
        + "\n"
    )
    runner_request_validation_schema_out.write_text(
        json.dumps(
            build_contract_request_validation_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    runner_receipt_schema_out.write_text(
        json.dumps(build_contract_receipt_json_schema(), indent=2, sort_keys=True)
        + "\n"
    )
    runner_check_schema_out.write_text(
        json.dumps(
            build_contract_runner_check_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    rope_model_config_import_schema_out.write_text(
        json.dumps(
            build_rope_model_config_import_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    receipt_file_check_schema_out.write_text(
        json.dumps(
            build_contract_receipt_file_check_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    certification_bundle_schema_out.write_text(
        json.dumps(
            build_contract_certification_bundle_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    certification_bundle_file_check_schema_out.write_text(
        json.dumps(
            build_contract_certification_bundle_file_check_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    artifact_manifest_schema_out.write_text(
        json.dumps(
            build_contract_artifact_manifest_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    try:
        display_path = out.relative_to(ROOT)
    except ValueError:
        display_path = out
    try:
        display_schema_path = schema_out.relative_to(ROOT)
    except ValueError:
        display_schema_path = schema_out
    try:
        display_policy_schema_path = policy_schema_out.relative_to(ROOT)
    except ValueError:
        display_policy_schema_path = policy_schema_out
    try:
        display_policy_report_schema_path = policy_report_schema_out.relative_to(ROOT)
    except ValueError:
        display_policy_report_schema_path = policy_report_schema_out
    try:
        display_receipt_schema_path = receipt_schema_out.relative_to(ROOT)
    except ValueError:
        display_receipt_schema_path = receipt_schema_out
    try:
        display_rejection_report_schema_path = (
            rejection_report_schema_out.relative_to(ROOT)
        )
    except ValueError:
        display_rejection_report_schema_path = rejection_report_schema_out
    try:
        display_runner_request_schema_path = runner_request_schema_out.relative_to(ROOT)
    except ValueError:
        display_runner_request_schema_path = runner_request_schema_out
    try:
        display_runner_request_validation_schema_path = (
            runner_request_validation_schema_out.relative_to(ROOT)
        )
    except ValueError:
        display_runner_request_validation_schema_path = (
            runner_request_validation_schema_out
        )
    try:
        display_runner_receipt_schema_path = runner_receipt_schema_out.relative_to(ROOT)
    except ValueError:
        display_runner_receipt_schema_path = runner_receipt_schema_out
    try:
        display_runner_check_schema_path = runner_check_schema_out.relative_to(ROOT)
    except ValueError:
        display_runner_check_schema_path = runner_check_schema_out
    try:
        display_rope_model_config_import_schema_path = (
            rope_model_config_import_schema_out.relative_to(ROOT)
        )
    except ValueError:
        display_rope_model_config_import_schema_path = (
            rope_model_config_import_schema_out
        )
    try:
        display_receipt_file_check_schema_path = (
            receipt_file_check_schema_out.relative_to(ROOT)
        )
    except ValueError:
        display_receipt_file_check_schema_path = receipt_file_check_schema_out
    try:
        display_certification_bundle_schema_path = (
            certification_bundle_schema_out.relative_to(ROOT)
        )
    except ValueError:
        display_certification_bundle_schema_path = certification_bundle_schema_out
    try:
        display_certification_bundle_file_check_schema_path = (
            certification_bundle_file_check_schema_out.relative_to(ROOT)
        )
    except ValueError:
        display_certification_bundle_file_check_schema_path = (
            certification_bundle_file_check_schema_out
        )
    try:
        display_artifact_manifest_schema_path = (
            artifact_manifest_schema_out.relative_to(ROOT)
        )
    except ValueError:
        display_artifact_manifest_schema_path = artifact_manifest_schema_out
    print(f"wrote {display_path}")
    print(f"wrote {display_schema_path}")
    print(f"wrote {display_policy_schema_path}")
    print(f"wrote {display_policy_report_schema_path}")
    print(f"wrote {display_receipt_schema_path}")
    print(f"wrote {display_rejection_report_schema_path}")
    print(f"wrote {display_runner_request_schema_path}")
    print(f"wrote {display_runner_request_validation_schema_path}")
    print(f"wrote {display_runner_receipt_schema_path}")
    print(f"wrote {display_runner_check_schema_path}")
    print(f"wrote {display_rope_model_config_import_schema_path}")
    print(f"wrote {display_receipt_file_check_schema_path}")
    print(f"wrote {display_certification_bundle_schema_path}")
    print(f"wrote {display_certification_bundle_file_check_schema_path}")
    print(f"wrote {display_artifact_manifest_schema_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
