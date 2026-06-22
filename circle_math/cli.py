"""Small package-native command-line entry points.

The repository keeps richer maintenance CLIs under ``scripts/``. The functions
here are intentionally narrow public commands that work from the installed
Python package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .ai_contracts import (
    CONTRACT_PACK_SCHEMA_ID,
    SUPPORTED_CONTRACT_KINDS,
    build_contract_pack,
    build_architecture_config_import_report,
    build_contract_request,
    build_contract_request_from_architecture_config,
    build_rope_model_config_import_report,
    build_validated_contract_receipt,
    build_validated_contract_receipt_from_request,
    build_validated_rope_receipt_from_model_config,
    canonical_contract_kind,
    receipt_summary_lines,
)
from .applications import (
    CIRCLE_AI_CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_CERTIFICATION_BUNDLE_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_COMPACT_RECEIPT_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_RECEIPT_REPLAY_CHECK_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_RECEIPT_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_REQUEST_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_REQUEST_VALIDATION_SCHEMA_ID,
    CIRCLE_AI_CONTRACT_RUNNER_CHECK_SCHEMA_ID,
    CIRCLE_AI_ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID,
    CIRCLE_AI_ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID,
    build_contract_artifact_manifest,
    build_contract_artifact_manifest_file_check_report,
    build_contract_certification_bundle,
    build_contract_certification_bundle_file_check_report,
    build_contract_receipt_file_check_report,
    build_contract_receipt_gate_report,
    build_contract_request_validation_report,
    build_contract_receipt_replay_check_report,
    build_compact_contract_receipt,
)
from .applications.circle_ai import certify_stride_family_coverage
from .applications.rope_certifier import (
    ROPE_CERTIFIER_PRESETS,
    RoPEConfig,
    certificate_summary_lines,
    certify_rope_positions,
)
from .contracts import contract_kinds, load_contract_pack, readiness_summary


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def contract_ready_main() -> int:
    """Print public contract readiness for the generated pack or a fresh pack."""
    parser = argparse.ArgumentParser(
        description="Inspect Circle AI contract readiness from the public API."
    )
    parser.add_argument("--pack", type=Path, default=None)
    parser.add_argument("--kind", default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    if args.pack is None:
        pack = build_contract_pack()
    else:
        pack = load_contract_pack(args.pack)

    kinds = contract_kinds(pack)
    selected = (args.kind,) if args.kind else kinds
    rows = []
    for kind in selected:
        summary = readiness_summary(pack, kind)
        rows.append(
            {
                "kind": summary.kind,
                "contract_id": summary.contract_id,
                "ready_for_downstream_fixture_use": summary.ready_for_downstream_fixture_use,
                "contract_passed": summary.contract_passed,
                "required_fields_present": summary.required_fields_present,
                "all_theorem_ids_resolved": summary.all_theorem_ids_resolved,
                "all_theorem_ids_proved": summary.all_theorem_ids_proved,
                "missing_minimum_fields": summary.missing_minimum_fields,
                "unresolved_theorem_ids": summary.unresolved_theorem_ids,
                "unproved_theorem_ids": summary.unproved_theorem_ids,
            }
        )
    payload = {"schema_id": CONTRACT_PACK_SCHEMA_ID, "contracts": rows}
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for row in rows:
            status = "ready" if row["ready_for_downstream_fixture_use"] else "not-ready"
            print(
                " ".join(
                    [
                        f"kind={row['kind']}",
                        f"id={row['contract_id']}",
                        f"status={status}",
                        f"proved={row['all_theorem_ids_proved']}",
                        f"missing_fields={len(row['missing_minimum_fields'])}",
                    ]
                )
            )
    return 0 if all(row["ready_for_downstream_fixture_use"] for row in rows) else 2


def rope_certify_main() -> int:
    """Run the public RoPE position certifier."""
    parser = argparse.ArgumentParser(description="Run a Circle RoPE certificate.")
    parser.add_argument("--preset", choices=sorted(ROPE_CERTIFIER_PRESETS), default=None)
    parser.add_argument("--head-dim", type=int, default=128)
    parser.add_argument("--base", type=float, default=10000.0)
    parser.add_argument("--context", type=int, default=4096)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    if args.preset:
        config = ROPE_CERTIFIER_PRESETS[args.preset]
    else:
        config = RoPEConfig(
            head_dim=args.head_dim,
            base=args.base,
            context_length=args.context,
            tolerance=args.tolerance,
        )
    certificate = certify_rope_positions(config)
    if args.format == "json":
        print(json.dumps(certificate.to_dict(), indent=2, sort_keys=True))
    else:
        for line in certificate_summary_lines(certificate):
            print(line)
    return 0


def sparse_attention_certify_main() -> int:
    """Run the public sparse-attention coverage certifier."""
    parser = argparse.ArgumentParser(
        description="Run a Circle sparse-attention coverage certificate."
    )
    parser.add_argument("--context", required=True, type=int)
    parser.add_argument(
        "--strides",
        required=True,
        type=lambda text: tuple(int(part) for part in text.split(",") if part),
    )
    parser.add_argument("--path-length", required=True, type=int)
    parser.add_argument("--local-window", required=True, type=int)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    certificate = certify_stride_family_coverage(
        sequence_length=args.context,
        strides=args.strides,
        path_length=args.path_length,
        local_window=args.local_window,
    )
    payload = _jsonable(certificate)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"context={payload['sequence_length']}")
        print(f"strides={tuple(payload['strides'])}")
        print(f"covered_count={payload['covered_count']}")
        print(f"uncovered_count={payload['uncovered_count']}")
        print(f"coverage_complete={payload['coverage_complete']}")
        print(f"first_uncovered_lag={payload['first_uncovered_lag']}")
    return 0


def _load_json_object_from_args(
    parser: argparse.ArgumentParser,
    *,
    inline_json: str | None,
    json_file: Path | None,
    label: str,
    allow_config_dir: bool = False,
) -> dict[str, Any]:
    if inline_json is not None and json_file is not None:
        parser.error(f"use either --{label} or --{label}-file, not both")
    if json_file is not None:
        if json_file.is_dir():
            if not allow_config_dir:
                parser.error(f"{label}-file must be a JSON file, not a directory")
            json_file = json_file / "config.json"
        if not json_file.exists():
            parser.error(f"{label}-file does not exist: {json_file}")
        raw = json_file.read_text()
    else:
        raw = inline_json or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        parser.error(f"{label} must be valid JSON: {exc}")
    if not isinstance(payload, dict):
        parser.error(f"{label} must be a JSON object")
    return payload


def _write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _receipt_gate_failures(receipt: dict[str, Any], args: argparse.Namespace) -> list[str]:
    failures: list[str] = []
    if args.require_passed and receipt.get("request_passed") is not True:
        failures.append("receipt request_passed is not true")
    if args.require_status and receipt.get("status") not in args.require_status:
        failures.append(
            "receipt status "
            f"{receipt.get('status')!r} is not in {tuple(args.require_status)!r}"
        )
    decision = receipt.get("decision", {})
    if not isinstance(decision, dict):
        decision = {}
    if args.require_decision and decision.get("verdict") not in args.require_decision:
        failures.append(
            "receipt decision.verdict "
            f"{decision.get('verdict')!r} is not in {tuple(args.require_decision)!r}"
        )
    if args.require_assurance and decision.get("assurance") not in args.require_assurance:
        failures.append(
            "receipt decision.assurance "
            f"{decision.get('assurance')!r} is not in {tuple(args.require_assurance)!r}"
        )
    return failures


def _parse_int_csv(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    return tuple(
        int(part.strip())
        for part in raw.replace(";", ",").split(",")
        if part.strip()
    )


def _parse_positive_int_csv(raw: str) -> tuple[int, ...]:
    values = _parse_int_csv(raw)
    if not values:
        raise argparse.ArgumentTypeError("value must contain at least one integer")
    if any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("all values must be positive")
    return values


_STATUS_CHOICES = (
    "proved",
    "impossible",
    "undecided",
    "numerical_only",
    "outside_scope",
)
_DECISION_CHOICES = (
    "passed",
    "failed",
    "undecided",
    "numerical_only",
    "outside_scope",
)
_ASSURANCE_CHOICES = (
    "theorem_backed",
    "mixed_theorem_and_computation",
    "numerical_only",
    "unsupported",
    "undecided",
)


def _add_receipt_gate_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Return nonzero unless each emitted receipt has request_passed=true.",
    )
    parser.add_argument(
        "--require-status",
        action="append",
        choices=_STATUS_CHOICES,
        default=[],
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        choices=_DECISION_CHOICES,
        default=[],
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        choices=_ASSURANCE_CHOICES,
        default=[],
    )


def _add_certify_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--pack", type=Path, default=None)
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        help=(
            "Optional directory where the package certifier writes the request, "
            "receipt, diagnostics, certification bundle, and manifest sidecars "
            "using stable names."
        ),
    )
    parser.add_argument(
        "--artifact-prefix",
        help=(
            "Optional filename prefix for --artifact-dir outputs. Requires "
            "--artifact-dir."
        ),
    )
    parser.add_argument("--request-out", type=Path)
    parser.add_argument(
        "--request-validation-report-out",
        type=Path,
        help=(
            "Optional JSON report validating the exact contract request used "
            "to build the receipt."
        ),
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument(
        "--compact-json-out",
        type=Path,
        help=(
            "Optional compact downstream-consumer receipt JSON. --json-out "
            "continues to write the full audit receipt."
        ),
    )
    parser.add_argument(
        "--gate-report-out",
        type=Path,
        help=(
            "Optional compact JSON gate report for the emitted receipt. This "
            "does not require saving the full receipt."
        ),
    )
    parser.add_argument(
        "--receipt-check-out",
        type=Path,
        help=(
            "Optional JSON report validating the emitted receipt against the "
            "contract pack and gate policy."
        ),
    )
    parser.add_argument(
        "--receipt-replay-check-out",
        type=Path,
        help=(
            "Optional JSON report rebuilding the emitted receipt from its "
            "embedded request and comparing stable fingerprints."
        ),
    )
    parser.add_argument(
        "--certification-bundle-out",
        type=Path,
        help=(
            "Optional JSON bundle containing request validation, receipt, "
            "gate report, and RoPE model-config provenance when present."
        ),
    )
    parser.add_argument(
        "--certification-bundle-check-out",
        type=Path,
        help=(
            "Optional JSON report validating the emitted certification bundle."
        ),
    )
    parser.add_argument(
        "--artifact-manifest-out",
        type=Path,
        help=(
            "Optional JSON manifest fingerprinting the sidecar files emitted "
            "by this certifier invocation."
        ),
    )
    parser.add_argument(
        "--artifact-manifest-check-out",
        type=Path,
        help=(
            "Optional JSON report validating the emitted artifact manifest and "
            "the files it names."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "compact-json"),
        default="text",
    )
    _add_receipt_gate_options(parser)


def _certify_pack_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return build_contract_pack() if args.pack is None else load_contract_pack(args.pack)


def _contract_request_from_architecture_config_args(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    kind: str,
    overrides: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    config = _load_json_object_from_args(
        parser,
        inline_json=None,
        json_file=args.architecture_config_file,
        label="architecture-config",
    )
    try:
        report = build_architecture_config_import_report(
            kind,
            config,
            overrides=overrides,
        )
        if args.architecture_config_import_report_out is not None:
            _write_json_file(args.architecture_config_import_report_out, report)
        if not report["ok"]:
            raise ValueError("; ".join(report["failures"]))
        request = report["request"]
        if not isinstance(request, dict):
            raise ValueError("architecture config import report did not emit a request")
        return request, report
    except ValueError as exc:
        parser.error(str(exc))
    raise AssertionError("parser.error should exit")


def _safe_certify_artifact_prefix(raw: str) -> str:
    cleaned = "".join(
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in raw.strip()
    ).strip("_-")
    return cleaned or "circle_ai_contract"


def _default_certify_artifact_prefix(args: argparse.Namespace) -> str:
    explicit = getattr(args, "artifact_prefix", None)
    if explicit:
        return _safe_certify_artifact_prefix(explicit)
    command = str(getattr(args, "command", "circle_ai_contract"))
    if command == "request":
        request_file = getattr(args, "request_file", None)
        if request_file is not None:
            return _safe_certify_artifact_prefix(
                Path(request_file).stem.removesuffix("_request")
            )
    if command == "rope":
        model_config_file = getattr(args, "model_config_file", None)
        if model_config_file is not None:
            return _safe_certify_artifact_prefix(Path(model_config_file).stem)
    if command in {"kv-cache", "sparse-attention", "recurrence"}:
        architecture_config_file = getattr(args, "architecture_config_file", None)
        if architecture_config_file is not None:
            return _safe_certify_artifact_prefix(Path(architecture_config_file).stem)
    return _safe_certify_artifact_prefix(command.replace("-", "_"))


def _fill_certify_artifact_path(
    args: argparse.Namespace,
    attr: str,
    artifact_dir: Path,
    prefix: str,
    suffix: str,
) -> None:
    if getattr(args, attr, None) is None:
        setattr(args, attr, artifact_dir / f"{prefix}_{suffix}.json")


def _apply_certify_artifact_dir_defaults(args: argparse.Namespace) -> None:
    artifact_dir = getattr(args, "artifact_dir", None)
    if getattr(args, "artifact_prefix", None) and artifact_dir is None:
        raise ValueError("--artifact-prefix requires --artifact-dir")
    if artifact_dir is None:
        return
    prefix = _default_certify_artifact_prefix(args)
    args._artifact_prefix_value = prefix
    _fill_certify_artifact_path(args, "request_out", artifact_dir, prefix, "request")
    _fill_certify_artifact_path(
        args,
        "request_validation_report_out",
        artifact_dir,
        prefix,
        "request_validation",
    )
    if (
        getattr(args, "command", None) == "rope"
        and getattr(args, "model_config_file", None) is not None
    ):
        _fill_certify_artifact_path(
            args,
            "model_config_import_report_out",
            artifact_dir,
            prefix,
            "model_config_import",
        )
    if (
        getattr(args, "command", None) in {"kv-cache", "sparse-attention", "recurrence"}
        and getattr(args, "architecture_config_file", None) is not None
    ):
        _fill_certify_artifact_path(
            args,
            "architecture_config_import_report_out",
            artifact_dir,
            prefix,
            "architecture_config_import",
        )
    _fill_certify_artifact_path(args, "json_out", artifact_dir, prefix, "receipt")
    _fill_certify_artifact_path(
        args,
        "compact_json_out",
        artifact_dir,
        prefix,
        "compact_receipt",
    )
    _fill_certify_artifact_path(
        args,
        "receipt_check_out",
        artifact_dir,
        prefix,
        "receipt_check",
    )
    _fill_certify_artifact_path(
        args,
        "receipt_replay_check_out",
        artifact_dir,
        prefix,
        "receipt_replay_check",
    )
    _fill_certify_artifact_path(
        args,
        "gate_report_out",
        artifact_dir,
        prefix,
        "gate_report",
    )
    _fill_certify_artifact_path(
        args,
        "certification_bundle_out",
        artifact_dir,
        prefix,
        "certification_bundle",
    )
    _fill_certify_artifact_path(
        args,
        "certification_bundle_check_out",
        artifact_dir,
        prefix,
        "certification_bundle_check",
    )
    _fill_certify_artifact_path(
        args,
        "artifact_manifest_out",
        artifact_dir,
        prefix,
        "artifact_manifest",
    )
    _fill_certify_artifact_path(
        args,
        "artifact_manifest_check_out",
        artifact_dir,
        prefix,
        "artifact_manifest_check",
    )


def _certify_artifact_paths(
    args: argparse.Namespace,
) -> list[tuple[str, Path, str | None]]:
    artifacts = [
        ("request_json", args.request_out, CIRCLE_AI_CONTRACT_REQUEST_SCHEMA_ID),
        (
            "request_validation_report",
            args.request_validation_report_out,
            CIRCLE_AI_CONTRACT_REQUEST_VALIDATION_SCHEMA_ID,
        ),
        ("receipt_json", args.json_out, CIRCLE_AI_CONTRACT_RECEIPT_SCHEMA_ID),
        (
            "compact_receipt_json",
            args.compact_json_out,
            CIRCLE_AI_CONTRACT_COMPACT_RECEIPT_SCHEMA_ID,
        ),
        (
            "receipt_check",
            args.receipt_check_out,
            CIRCLE_AI_CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_ID,
        ),
        (
            "receipt_replay_check",
            args.receipt_replay_check_out,
            CIRCLE_AI_CONTRACT_RECEIPT_REPLAY_CHECK_SCHEMA_ID,
        ),
        ("gate_report", args.gate_report_out, CIRCLE_AI_CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_ID),
        (
            "certification_bundle",
            args.certification_bundle_out,
            CIRCLE_AI_CONTRACT_CERTIFICATION_BUNDLE_SCHEMA_ID,
        ),
        (
            "certification_bundle_check",
            args.certification_bundle_check_out,
            CIRCLE_AI_CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID,
        ),
    ]
    model_config_import_report_out = getattr(
        args,
        "model_config_import_report_out",
        None,
    )
    artifacts.insert(
        2,
        (
            "model_config_import_report",
            model_config_import_report_out,
            CIRCLE_AI_ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID,
        ),
    )
    architecture_config_import_report_out = getattr(
        args,
        "architecture_config_import_report_out",
        None,
    )
    artifacts.insert(
        3,
        (
            "architecture_config_import_report",
            architecture_config_import_report_out,
            CIRCLE_AI_ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID,
        ),
    )
    return [
        (label, path, schema_id)
        for label, path, schema_id in artifacts
        if path is not None
    ]


def _certify_artifact_prefix(args: argparse.Namespace, receipt: dict[str, Any]) -> str:
    artifact_prefix_value = getattr(args, "_artifact_prefix_value", None)
    if isinstance(artifact_prefix_value, str) and artifact_prefix_value:
        return artifact_prefix_value
    kind = receipt.get("kind")
    if isinstance(kind, str) and kind:
        return kind
    command = getattr(args, "command", "circle_ai_contract")
    return str(command).replace("-", "_")


def _certify_print_and_gate(
    receipt: dict[str, Any],
    pack: dict[str, Any],
    args: argparse.Namespace,
    *,
    request: dict[str, Any],
    model_config_import_report: dict[str, Any] | None = None,
    architecture_config_import_report: dict[str, Any] | None = None,
) -> int:
    if args.request_out is not None:
        _write_json_file(args.request_out, receipt["request"])
    request_validation_report: dict[str, Any] | None = None
    if args.request_validation_report_out is not None:
        request_validation_report = build_contract_request_validation_report(request)
        _write_json_file(
            args.request_validation_report_out,
            request_validation_report,
        )
    if args.json_out is not None:
        _write_json_file(args.json_out, receipt)
    compact_receipt = None
    if args.format == "compact-json" or args.compact_json_out is not None:
        compact_receipt = build_compact_contract_receipt(receipt)
        if args.compact_json_out is not None:
            _write_json_file(args.compact_json_out, compact_receipt)
    receipt_path = (
        str(args.json_out) if args.json_out is not None else "<in-memory-receipt>"
    )
    if args.gate_report_out is not None:
        gate_report = build_contract_receipt_gate_report(
            receipt,
            pack,
            receipt_path=receipt_path,
            required_statuses=tuple(args.require_status),
            required_decision_verdicts=tuple(args.require_decision),
            required_assurance_levels=tuple(args.require_assurance),
            require_passed=args.require_passed,
        )
        _write_json_file(args.gate_report_out, gate_report)
    if args.receipt_check_out is not None:
        receipt_check = build_contract_receipt_file_check_report(
            receipt,
            pack,
            receipt_path=receipt_path,
            required_statuses=tuple(args.require_status),
            required_decision_verdicts=tuple(args.require_decision),
            required_assurance_levels=tuple(args.require_assurance),
            require_passed=args.require_passed,
        )
        _write_json_file(args.receipt_check_out, receipt_check)
    if args.receipt_replay_check_out is not None:
        replay_check = build_contract_receipt_replay_check_report(
            receipt,
            pack,
            receipt_path=receipt_path,
        )
        _write_json_file(args.receipt_replay_check_out, replay_check)
    if args.certification_bundle_out is not None:
        bundle = build_contract_certification_bundle(
            request,
            pack=pack,
            model_config_import_report=model_config_import_report,
            architecture_config_import_report=architecture_config_import_report,
            receipt_path=receipt_path,
            required_statuses=tuple(args.require_status),
            required_decision_verdicts=tuple(args.require_decision),
            required_assurance_levels=tuple(args.require_assurance),
            require_passed=args.require_passed,
        )
        _write_json_file(args.certification_bundle_out, bundle)
        if args.certification_bundle_check_out is not None:
            bundle_check = build_contract_certification_bundle_file_check_report(
                bundle,
                pack=pack,
                bundle_path=str(args.certification_bundle_out),
                required_statuses=tuple(args.require_status),
                required_decision_verdicts=tuple(args.require_decision),
                required_assurance_levels=tuple(args.require_assurance),
                require_passed=args.require_passed,
            )
            _write_json_file(args.certification_bundle_check_out, bundle_check)
    if args.artifact_manifest_out is not None:
        manifest = build_contract_artifact_manifest(
            _certify_artifact_paths(args),
            artifact_prefix=_certify_artifact_prefix(args, receipt),
            artifact_dir=getattr(args, "artifact_dir", None),
            receipt=receipt,
            request_validation_report=request_validation_report,
            required_statuses=tuple(args.require_status),
            required_decision_verdicts=tuple(args.require_decision),
            required_assurance_levels=tuple(args.require_assurance),
            require_passed=args.require_passed,
        )
        _write_json_file(args.artifact_manifest_out, manifest)
        if args.artifact_manifest_check_out is not None:
            manifest_check = build_contract_artifact_manifest_file_check_report(
                manifest,
                manifest_path=str(args.artifact_manifest_out),
            )
            _write_json_file(args.artifact_manifest_check_out, manifest_check)
    gate_failures = _receipt_gate_failures(receipt, args)
    if args.format == "json":
        print(json.dumps(receipt, indent=2, sort_keys=True))
    elif args.format == "compact-json":
        assert compact_receipt is not None
        print(json.dumps(compact_receipt, indent=2, sort_keys=True))
    else:
        for line in receipt_summary_lines(receipt):
            print(line)
    for failure in gate_failures:
        print(f"contract receipt gate failed: {failure}", file=sys.stderr)
    return 2 if gate_failures else 0


def _certify_json_fingerprint(value: Any) -> str:
    payload = json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _certify_batch_output_path(
    out_dir: Path,
    *,
    index: int,
    source_path: Path,
    suffix: str,
) -> Path:
    prefix = _safe_certify_artifact_prefix(
        source_path.stem.removesuffix("_request")
    )
    return out_dir / f"{index:03d}_{prefix}_{suffix}.json"


def _certify_batch_summary_from_receipt(
    *,
    source_type: str,
    source_path: Path,
    source: dict[str, Any],
    receipt: dict[str, Any],
    compact_receipt: dict[str, Any],
    request_path: Path | None = None,
    model_config_import_report_path: Path | None = None,
    model_config_parameter_sources: dict[str, Any] | None = None,
    receipt_path: Path | None = None,
    compact_receipt_path: Path | None = None,
) -> dict[str, Any]:
    decision = receipt["decision"]
    selected_evidence_layers = compact_receipt[
        "selected_evidence_proof_layers"
    ]
    return {
        "source_type": source_type,
        "source_path": str(source_path),
        "source_content_fingerprint": _certify_json_fingerprint(source),
        "request_path": None if request_path is None else str(request_path),
        "model_config_import_report_path": (
            None
            if model_config_import_report_path is None
            else str(model_config_import_report_path)
        ),
        "model_config_parameter_sources": model_config_parameter_sources,
        "request_validation_report_path": None,
        "certification_bundle_path": None,
        "certification_bundle_check_path": None,
        "receipt_path": None if receipt_path is None else str(receipt_path),
        "compact_receipt_path": (
            None if compact_receipt_path is None else str(compact_receipt_path)
        ),
        "kind": receipt["kind"],
        "status": receipt["status"],
        "request_passed": receipt["request_passed"],
        "decision_verdict": decision["verdict"],
        "decision_assurance": decision["assurance"],
        "theorem_count": receipt["proof_status"]["theorem_count"],
        "recommendation_count": len(receipt["recommendations"]),
        "validation_command_count": len(receipt["validation_commands"]),
        "normalized_request": receipt["normalized_request"],
        "request_content_fingerprint": receipt["request_content_fingerprint"],
        "normalized_request_fingerprint": receipt[
            "normalized_request_fingerprint"
        ],
        "receipt_content_fingerprint": receipt["receipt_content_fingerprint"],
        "compact_selected_evidence_count": len(
            compact_receipt["selected_evidence"]
        ),
        "compact_selected_evidence_unclassified_count": sum(
            1
            for label in selected_evidence_layers.values()
            if label == "unclassified"
        ),
        "compact_selected_evidence_labels": sorted(
            set(selected_evidence_layers.values())
        ),
    }


def _certify_batch_requests(args: argparse.Namespace) -> int:
    pack = _certify_pack_from_args(args)
    failures: list[str] = []
    summaries: list[dict[str, Any]] = []
    selected_kinds: set[str] = set()
    request_files = tuple(args.request_file or ())
    model_config_files = tuple(args.model_config_file or ())

    for index, source_path in enumerate(request_files, start=1):
        try:
            source = _load_json_object_from_args(
                argparse.ArgumentParser(prog="circle-ai-certify batch"),
                inline_json=None,
                json_file=source_path,
                label="request",
            )
            receipt = build_validated_contract_receipt_from_request(
                source,
                pack=pack,
            )
            compact_receipt = build_compact_contract_receipt(receipt)
            selected_kinds.add(receipt["kind"])

            receipt_path = None
            if args.receipt_out_dir is not None:
                receipt_path = _certify_batch_output_path(
                    args.receipt_out_dir,
                    index=index,
                    source_path=source_path,
                    suffix="receipt",
                )
                _write_json_file(receipt_path, receipt)

            compact_receipt_path = None
            if args.compact_receipt_out_dir is not None:
                compact_receipt_path = _certify_batch_output_path(
                    args.compact_receipt_out_dir,
                    index=index,
                    source_path=source_path,
                    suffix="compact_receipt",
                )
                _write_json_file(compact_receipt_path, compact_receipt)

            summaries.append(
                _certify_batch_summary_from_receipt(
                    source_type="request",
                    source_path=source_path,
                    source=source,
                    receipt=receipt,
                    compact_receipt=compact_receipt,
                    receipt_path=receipt_path,
                    compact_receipt_path=compact_receipt_path,
                )
            )
            for failure in _receipt_gate_failures(receipt, args):
                failures.append(f"{source_path}: {failure}")
        except SystemExit as exc:
            failures.append(f"{source_path}: request JSON could not be loaded ({exc})")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append(f"{source_path}: {exc}")

    model_config_start_index = len(request_files) + 1
    for index, source_path in enumerate(
        model_config_files,
        start=model_config_start_index,
    ):
        try:
            source = _load_json_object_from_args(
                argparse.ArgumentParser(prog="circle-ai-certify batch"),
                inline_json=None,
                json_file=source_path,
                label="model-config",
                allow_config_dir=True,
            )
            import_report = build_rope_model_config_import_report(
                source,
                head_dim=args.head_dim,
                base=args.base,
                context=args.context,
                tolerance=args.tolerance,
                discretization=args.discretization,
                requested_margin=args.requested_margin,
            )
            model_config_import_report_path = None
            if args.model_config_import_report_out_dir is not None:
                model_config_import_report_path = _certify_batch_output_path(
                    args.model_config_import_report_out_dir,
                    index=index,
                    source_path=source_path,
                    suffix="model_config_import",
                )
                _write_json_file(model_config_import_report_path, import_report)
            if not import_report["ok"]:
                failures.append(
                    f"{source_path}: " + "; ".join(import_report["failures"])
                )
                continue
            receipt = build_validated_rope_receipt_from_model_config(
                source,
                head_dim=args.head_dim,
                base=args.base,
                context=args.context,
                tolerance=args.tolerance,
                discretization=args.discretization,
                requested_margin=args.requested_margin,
                pack=pack,
            )
            compact_receipt = build_compact_contract_receipt(receipt)
            selected_kinds.add(receipt["kind"])

            receipt_path = None
            if args.receipt_out_dir is not None:
                receipt_path = _certify_batch_output_path(
                    args.receipt_out_dir,
                    index=index,
                    source_path=source_path,
                    suffix="receipt",
                )
                _write_json_file(receipt_path, receipt)

            compact_receipt_path = None
            if args.compact_receipt_out_dir is not None:
                compact_receipt_path = _certify_batch_output_path(
                    args.compact_receipt_out_dir,
                    index=index,
                    source_path=source_path,
                    suffix="compact_receipt",
                )
                _write_json_file(compact_receipt_path, compact_receipt)

            summaries.append(
                _certify_batch_summary_from_receipt(
                    source_type="model_config",
                    source_path=source_path,
                    source=source,
                    receipt=receipt,
                    compact_receipt=compact_receipt,
                    model_config_import_report_path=model_config_import_report_path,
                    model_config_parameter_sources=import_report["parameter_sources"],
                    receipt_path=receipt_path,
                    compact_receipt_path=compact_receipt_path,
                )
            )
            for failure in _receipt_gate_failures(receipt, args):
                failures.append(f"{source_path}: {failure}")
        except SystemExit as exc:
            failures.append(
                f"{source_path}: model config JSON could not be loaded ({exc})"
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append(f"{source_path}: {exc}")

    report = {
        "schema_id": CIRCLE_AI_CONTRACT_RUNNER_CHECK_SCHEMA_ID,
        "ok": not failures,
        "example_count": len(summaries),
        "failure_count": len(failures),
        "failures": failures,
        "selected_kinds": sorted(selected_kinds),
        "gate_policy": {
            "allowed_statuses": list(args.require_status),
            "allowed_decision_verdicts": list(args.require_decision),
            "allowed_assurance_levels": list(args.require_assurance),
            "require_passed": args.require_passed,
        },
        "summaries": summaries,
    }
    if args.report_out is not None:
        _write_json_file(args.report_out, report)

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            " ".join(
                [
                    f"schema_id={report['schema_id']}",
                    f"ok={report['ok']}",
                    f"source_count={report['example_count']}",
                    f"failure_count={report['failure_count']}",
                ]
            )
        )
        for summary in summaries:
            print(
                " ".join(
                    [
                        f"source={summary['source_path']}",
                        f"kind={summary['kind']}",
                        f"type={summary['source_type']}",
                        f"status={summary['status']}",
                        f"decision={summary['decision_verdict']}",
                        f"compact_receipt={summary['compact_receipt_path']}",
                    ]
                )
            )
        for failure in failures:
            print(f"contract batch gate failed: {failure}", file=sys.stderr)
    return 0 if report["ok"] else 2


def contract_certify_main() -> int:
    """Issue theorem-linked AI contract receipts from package-native subcommands."""
    parser = argparse.ArgumentParser(
        description=(
            "Issue theorem-linked Circle AI contract receipts from user "
            "parameters, model configs, or versioned request JSON. For the "
            "full repository audit bundle generator, use scripts/circle_ai_certify.py."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    request_parser = subparsers.add_parser(
        "request",
        help="Issue a receipt from a circle_calculus.ai_contract_request.v0 file.",
    )
    _add_certify_common_options(request_parser)
    request_parser.add_argument(
        "--request-file",
        "--request-json",
        dest="request_file",
        required=True,
        type=Path,
        help="Path to a versioned Circle AI contract request JSON object.",
    )

    batch_parser = subparsers.add_parser(
        "batch",
        help=(
            "Issue receipts for several versioned request JSON files or "
            "standard RoPE model configs and write a runner-check summary."
        ),
    )
    batch_parser.add_argument("--pack", type=Path, default=None)
    batch_parser.add_argument(
        "--request-file",
        "--request-json",
        dest="request_file",
        action="append",
        default=[],
        type=Path,
        help=(
            "Path to a versioned Circle AI contract request JSON object. "
            "May be passed more than once."
        ),
    )
    batch_parser.add_argument(
        "--model-config-file",
        "--model-config",
        dest="model_config_file",
        action="append",
        default=[],
        type=Path,
        help=(
            "Path to a standard RoPE model config JSON object, or a model "
            "directory containing config.json. May be passed more than once."
        ),
    )
    batch_parser.add_argument(
        "--model-config-import-report-out-dir",
        type=Path,
        help=(
            "Optional directory where standard-RoPE model-config import "
            "reports are written."
        ),
    )
    batch_parser.add_argument("--head-dim", type=int, default=None)
    batch_parser.add_argument("--base", type=float, default=None)
    batch_parser.add_argument("--context", type=int, default=None)
    batch_parser.add_argument("--tolerance", type=float, default=None)
    batch_parser.add_argument(
        "--discretization",
        choices=("round", "floor", "ceil"),
        default=None,
    )
    batch_parser.add_argument("--requested-margin", default=None)
    batch_parser.add_argument(
        "--receipt-out-dir",
        type=Path,
        help="Optional directory where full audit receipts are written.",
    )
    batch_parser.add_argument(
        "--compact-receipt-out-dir",
        type=Path,
        help="Optional directory where compact downstream receipts are written.",
    )
    batch_parser.add_argument(
        "--report-out",
        type=Path,
        help="Optional path for the batch runner-check JSON report.",
    )
    batch_parser.add_argument("--format", choices=("text", "json"), default="text")
    _add_receipt_gate_options(batch_parser)

    rope_parser = subparsers.add_parser(
        "rope",
        help="Issue a RoPE position-distinguishability receipt.",
    )
    _add_certify_common_options(rope_parser)
    rope_parser.add_argument(
        "--model-config-file",
        "--model-config",
        type=Path,
        help=(
            "Path to a standard RoPE model config JSON object, or a model "
            "directory containing config.json."
        ),
    )
    rope_parser.add_argument("--model-config-import-report-out", type=Path)
    rope_parser.add_argument("--head-dim", type=int, default=None)
    rope_parser.add_argument("--base", type=float, default=None)
    rope_parser.add_argument("--context", type=int, default=None)
    rope_parser.add_argument("--tolerance", type=float, default=None)
    rope_parser.add_argument(
        "--discretization",
        choices=("round", "floor", "ceil"),
        default=None,
    )
    rope_parser.add_argument("--requested-margin", default=None)

    kv_parser = subparsers.add_parser(
        "kv-cache",
        help="Issue a KV-cache ring-buffer freshness receipt.",
    )
    _add_certify_common_options(kv_parser)
    kv_parser.add_argument(
        "--architecture-config-file",
        "--architecture-config",
        type=Path,
        help=(
            "Optional AI architecture config JSON. Reads kv_cache/cache aliases "
            "and lets explicit flags override imported values."
        ),
    )
    kv_parser.add_argument("--architecture-config-import-report-out", type=Path)
    kv_parser.add_argument("--cache-size", type=int)
    kv_parser.add_argument("--current", type=int)
    kv_parser.add_argument("--token", type=int)
    kv_parser.add_argument("--batch-tokens", type=_parse_int_csv)
    kv_parser.add_argument("--sink-size", type=int)
    kv_parser.add_argument("--request-id")

    sparse_parser = subparsers.add_parser(
        "sparse-attention",
        help="Issue a sparse-attention local-window plus stride-family receipt.",
    )
    _add_certify_common_options(sparse_parser)
    sparse_parser.add_argument(
        "--architecture-config-file",
        "--architecture-config",
        type=Path,
        help=(
            "Optional AI architecture config JSON. Reads sparse_attention/"
            "attention aliases and lets explicit flags override imported values."
        ),
    )
    sparse_parser.add_argument("--architecture-config-import-report-out", type=Path)
    sparse_parser.add_argument("--context", type=int)
    sparse_parser.add_argument("--strides", type=_parse_positive_int_csv)
    sparse_parser.add_argument("--path-length", type=int)
    sparse_parser.add_argument("--local-window", type=int)

    recurrence_parser = subparsers.add_parser(
        "recurrence",
        help="Issue a finite looped/recursive schedule receipt.",
    )
    _add_certify_common_options(recurrence_parser)
    recurrence_parser.add_argument(
        "--architecture-config-file",
        "--architecture-config",
        type=Path,
        help=(
            "Optional AI architecture config JSON. Reads recurrence/loop aliases "
            "and lets explicit flags override imported values."
        ),
    )
    recurrence_parser.add_argument("--architecture-config-import-report-out", type=Path)
    recurrence_parser.add_argument("--loop-period", type=int)
    recurrence_parser.add_argument("--sample-index", type=int)
    recurrence_parser.add_argument("--max-loops", type=int)
    recurrence_parser.add_argument("--token-count", type=int)
    recurrence_parser.add_argument("--selected-block-start", type=int)
    recurrence_parser.add_argument("--selected-block-width", type=int)
    recurrence_parser.add_argument("--shift-passes", type=int)

    fanout_parser = subparsers.add_parser(
        "strided-fanout",
        help="Issue a finite strided candidate-fanout receipt.",
    )
    _add_certify_common_options(fanout_parser)
    fanout_parser.add_argument("--context-length", type=int, default=12)
    fanout_parser.add_argument("--stride", type=int, default=5)
    fanout_parser.add_argument("--start-index", type=int, default=0)
    fanout_parser.add_argument("--path-length", type=int, default=12)

    memory_parser = subparsers.add_parser(
        "cyclic-memory",
        help="Issue a cyclic memory residue/winding receipt.",
    )
    _add_certify_common_options(memory_parser)
    memory_parser.add_argument("--bank-size", type=int, default=8)
    memory_parser.add_argument("--event-index", type=int, default=23)
    memory_parser.add_argument("--event-count", type=int, default=32)

    phase_parser = subparsers.add_parser(
        "multicoil-phase",
        help="Issue a MultiCoil phase-feature receipt.",
    )
    _add_certify_common_options(phase_parser)
    phase_parser.add_argument("--periods", type=_parse_positive_int_csv, default=(5, 7))
    phase_parser.add_argument("--position", type=int, default=37)
    phase_parser.add_argument("--query-position", type=int, default=41)
    phase_parser.add_argument("--key-position", type=int, default=18)

    mixer_parser = subparsers.add_parser(
        "cyclic-mixer",
        help="Issue a circulant/block-cyclic mixer receipt.",
    )
    _add_certify_common_options(mixer_parser)
    mixer_parser.add_argument("--period", type=int, default=8)
    mixer_parser.add_argument("--channel-count", type=int, default=128)
    mixer_parser.add_argument("--block-size", type=int, default=8)

    seed_rule_parser = subparsers.add_parser(
        "seed-rule",
        help="Issue a finite seed/rule exact-regeneration receipt.",
    )
    _add_certify_common_options(seed_rule_parser)
    seed_rule_parser.add_argument("--n", type=int, default=128)

    args = parser.parse_args()
    if args.command == "batch":
        if not args.request_file and not args.model_config_file:
            batch_parser.error(
                "at least one --request-file or --model-config-file is required"
            )
        return _certify_batch_requests(args)
    try:
        _apply_certify_artifact_dir_defaults(args)
    except ValueError as exc:
        parser.error(str(exc))
    if (
        args.certification_bundle_check_out is not None
        and args.certification_bundle_out is None
    ):
        parser.error(
            "--certification-bundle-check-out requires --certification-bundle-out"
        )
    if (
        args.artifact_manifest_check_out is not None
        and args.artifact_manifest_out is None
    ):
        parser.error(
            "--artifact-manifest-check-out requires --artifact-manifest-out"
        )
    if (
        getattr(args, "architecture_config_import_report_out", None) is not None
        and getattr(args, "architecture_config_file", None) is None
    ):
        parser.error(
            "--architecture-config-import-report-out requires "
            "--architecture-config-file"
        )
    pack = _certify_pack_from_args(args)
    model_config_import_report: dict[str, Any] | None = None
    architecture_config_import_report: dict[str, Any] | None = None
    try:
        if args.command == "request":
            request = _load_json_object_from_args(
                request_parser,
                inline_json=None,
                json_file=args.request_file,
                label="request",
            )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "rope":
            if args.model_config_file is not None:
                config = _load_json_object_from_args(
                    rope_parser,
                    inline_json=None,
                    json_file=args.model_config_file,
                    label="model-config",
                )
                import_report = build_rope_model_config_import_report(
                    config,
                    head_dim=args.head_dim,
                    base=args.base,
                    context=args.context,
                    tolerance=args.tolerance,
                    discretization=args.discretization,
                    requested_margin=args.requested_margin,
                )
                model_config_import_report = import_report
                if args.model_config_import_report_out is not None:
                    _write_json_file(args.model_config_import_report_out, import_report)
                if not import_report["ok"]:
                    rope_parser.error("; ".join(import_report["failures"]))
                request = import_report["request"]
                receipt = build_validated_rope_receipt_from_model_config(
                    config,
                    head_dim=args.head_dim,
                    base=args.base,
                    context=args.context,
                    tolerance=args.tolerance,
                    discretization=args.discretization,
                    requested_margin=args.requested_margin,
                    pack=pack,
                )
            else:
                request = build_contract_request(
                    "rope",
                    {
                        "head_dim": 128 if args.head_dim is None else args.head_dim,
                        "base": 10000.0 if args.base is None else args.base,
                        "context": 32768 if args.context is None else args.context,
                        "tolerance": 1e-6 if args.tolerance is None else args.tolerance,
                        "discretization": (
                            "round"
                            if args.discretization is None
                            else args.discretization
                        ),
                        "requested_margin": args.requested_margin,
                    },
                )
                receipt = build_validated_contract_receipt_from_request(
                    request,
                    pack=pack,
                )
        elif args.command == "kv-cache":
            kv_parameters = {
                "cache_size": args.cache_size,
                "current": args.current,
                "token": args.token,
                "batch_tokens": args.batch_tokens,
                "sink_size": args.sink_size,
                "request_id": args.request_id,
            }
            if args.architecture_config_file is not None:
                (
                    request,
                    architecture_config_import_report,
                ) = _contract_request_from_architecture_config_args(
                    kv_parser,
                    args,
                    "kv-cache",
                    kv_parameters,
                )
            else:
                request = build_contract_request(
                    "kv-cache",
                    {
                        "cache_size": args.cache_size,
                        "current": args.current,
                        "token": args.token,
                        "batch_tokens": ()
                        if args.batch_tokens is None
                        else args.batch_tokens,
                        "sink_size": 0 if args.sink_size is None else args.sink_size,
                        "request_id": (
                            "read_request"
                            if args.request_id is None
                            else args.request_id
                        ),
                    },
                )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "sparse-attention":
            sparse_parameters = {
                "context": args.context,
                "strides": args.strides,
                "path_length": args.path_length,
                "local_window": args.local_window,
            }
            if args.architecture_config_file is not None:
                (
                    request,
                    architecture_config_import_report,
                ) = _contract_request_from_architecture_config_args(
                    sparse_parser,
                    args,
                    "sparse-attention",
                    sparse_parameters,
                )
            else:
                request = build_contract_request(
                    "sparse-attention",
                    sparse_parameters,
                )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "recurrence":
            recurrence_parameters = {
                "loop_period": args.loop_period,
                "sample_index": args.sample_index,
                "max_loops": args.max_loops,
                "token_count": args.token_count,
                "selected_block_start": args.selected_block_start,
                "selected_block_width": args.selected_block_width,
                "shift_passes": args.shift_passes,
            }
            if args.architecture_config_file is not None:
                (
                    request,
                    architecture_config_import_report,
                ) = _contract_request_from_architecture_config_args(
                    recurrence_parser,
                    args,
                    "recurrence",
                    recurrence_parameters,
                )
            else:
                request = build_contract_request(
                    "recurrence",
                    {
                        "loop_period": (
                            5 if args.loop_period is None else args.loop_period
                        ),
                        "sample_index": (
                            8 if args.sample_index is None else args.sample_index
                        ),
                        "max_loops": 7 if args.max_loops is None else args.max_loops,
                        "token_count": (
                            8 if args.token_count is None else args.token_count
                        ),
                        "selected_block_start": (
                            2
                            if args.selected_block_start is None
                            else args.selected_block_start
                        ),
                        "selected_block_width": (
                            3
                            if args.selected_block_width is None
                            else args.selected_block_width
                        ),
                        "shift_passes": (
                            3 if args.shift_passes is None else args.shift_passes
                        ),
                    },
                )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "strided-fanout":
            request = build_contract_request(
                "strided-fanout",
                {
                    "context_length": args.context_length,
                    "stride": args.stride,
                    "start_index": args.start_index,
                    "path_length": args.path_length,
                },
            )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "cyclic-memory":
            request = build_contract_request(
                "cyclic-memory",
                {
                    "bank_size": args.bank_size,
                    "event_index": args.event_index,
                    "event_count": args.event_count,
                },
            )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "multicoil-phase":
            request = build_contract_request(
                "multicoil-phase",
                {
                    "periods": args.periods,
                    "position": args.position,
                    "query_position": args.query_position,
                    "key_position": args.key_position,
                },
            )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "cyclic-mixer":
            request = build_contract_request(
                "cyclic-mixer",
                {
                    "period": args.period,
                    "channel_count": args.channel_count,
                    "block_size": args.block_size,
                },
            )
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        elif args.command == "seed-rule":
            request = build_contract_request("seed-rule", {"n": args.n})
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        else:
            parser.error(f"unsupported command: {args.command}")
    except ValueError as exc:
        parser.error(str(exc))
    return _certify_print_and_gate(
        receipt,
        pack,
        args,
        request=request,
        model_config_import_report=model_config_import_report,
        architecture_config_import_report=architecture_config_import_report,
    )


def contract_receipt_main() -> int:
    """Build a theorem-linked public contract receipt from JSON parameters."""
    parser = argparse.ArgumentParser(
        description=(
            "Build a Circle AI contract receipt for one public contract kind. "
            "The receipt carries proof-status fields and explicit non-claims; "
            "it is not a benchmark result."
        )
    )
    parser.add_argument(
        "--kind",
        help=(
            "Contract kind or alias. Public kinds: "
            + ", ".join(SUPPORTED_CONTRACT_KINDS)
        ),
    )
    parser.add_argument(
        "--parameters",
        help="Inline JSON object containing contract parameters.",
    )
    parser.add_argument(
        "--parameters-file",
        type=Path,
        help="Path to a JSON object containing contract parameters.",
    )
    parser.add_argument(
        "--request-file",
        type=Path,
        help=(
            "Path to a versioned circle_calculus.ai_contract_request.v0 JSON "
            "object. When present, kind and parameters are read from the file."
        ),
    )
    parser.add_argument(
        "--model-config-file",
        type=Path,
        help=(
            "Path to a model config JSON object, or a model directory "
            "containing config.json. Currently supported for standard RoPE "
            "receipts only."
        ),
    )
    parser.add_argument(
        "--head-dim",
        type=int,
        default=None,
        help="Optional RoPE head-dimension override for --model-config-file.",
    )
    parser.add_argument(
        "--base",
        type=float,
        default=None,
        help="Optional RoPE base/theta override for --model-config-file.",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=None,
        help="Optional context-length override for --model-config-file.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=None,
        help="Optional numerical tolerance override for --model-config-file.",
    )
    parser.add_argument(
        "--discretization",
        default=None,
        help="Optional discretization override for --model-config-file.",
    )
    parser.add_argument(
        "--requested-margin",
        default=None,
        help="Optional real-phase margin request for --model-config-file.",
    )
    parser.add_argument(
        "--pack",
        type=Path,
        default=None,
        help="Optional exported contract pack path. Defaults to a fresh public pack.",
    )
    parser.add_argument(
        "--request-out",
        type=Path,
        help="Optional path for the exact versioned request JSON used by the receipt.",
    )
    parser.add_argument(
        "--model-config-import-report-out",
        type=Path,
        help=(
            "Optional path for the standard-RoPE model-config import report. "
            "Only valid with --model-config-file."
        ),
    )
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Return nonzero unless the emitted receipt has request_passed=true.",
    )
    parser.add_argument(
        "--require-status",
        action="append",
        choices=("proved", "impossible", "undecided", "numerical_only", "outside_scope"),
        default=[],
        help="Allowed receipt status. May be passed more than once.",
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        choices=("passed", "failed", "undecided", "numerical_only", "outside_scope"),
        default=[],
        help="Allowed decision.verdict. May be passed more than once.",
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        choices=(
            "theorem_backed",
            "mixed_theorem_and_computation",
            "numerical_only",
            "unsupported",
            "undecided",
        ),
        default=[],
        help="Allowed decision.assurance. May be passed more than once.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    pack = build_contract_pack() if args.pack is None else load_contract_pack(args.pack)
    if args.request_file is not None:
        if args.parameters is not None or args.parameters_file is not None:
            parser.error("use either --request-file or parameter JSON, not both")
        if args.model_config_file is not None:
            parser.error("use either --request-file or --model-config-file, not both")
        if args.model_config_import_report_out is not None:
            parser.error("--model-config-import-report-out requires --model-config-file")
        request = _load_json_object_from_args(
            parser,
            inline_json=None,
            json_file=args.request_file,
            label="request",
        )
        if args.kind is not None:
            try:
                requested_kind = canonical_contract_kind(str(request.get("kind", "")))
                cli_kind = canonical_contract_kind(args.kind)
            except ValueError as exc:
                parser.error(str(exc))
            if requested_kind != cli_kind:
                parser.error(
                    f"--kind {args.kind!r} does not match request kind "
                    f"{request.get('kind')!r}"
                )
        try:
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        except ValueError as exc:
            parser.error(str(exc))
    elif args.model_config_file is not None:
        if args.kind is None:
            parser.error("--kind is required unless --request-file is used")
        if args.parameters is not None or args.parameters_file is not None:
            parser.error(
                "use either --model-config-file or parameter JSON, not both"
            )
        if canonical_contract_kind(args.kind) != "rope_position_distinguishability":
            parser.error("--model-config-file is currently supported only for RoPE")
        model_config = _load_json_object_from_args(
            parser,
            inline_json=None,
            json_file=args.model_config_file,
            label="model-config",
            allow_config_dir=True,
        )
        import_report = build_rope_model_config_import_report(
            model_config,
            head_dim=args.head_dim,
            base=args.base,
            context=args.context,
            tolerance=args.tolerance,
            discretization=args.discretization,
            requested_margin=args.requested_margin,
        )
        if args.model_config_import_report_out is not None:
            _write_json_file(args.model_config_import_report_out, import_report)
        if not import_report["ok"]:
            parser.error("; ".join(import_report["failures"]))
        try:
            receipt = build_validated_rope_receipt_from_model_config(
                model_config,
                head_dim=args.head_dim,
                base=args.base,
                context=args.context,
                tolerance=args.tolerance,
                discretization=args.discretization,
                requested_margin=args.requested_margin,
                pack=pack,
            )
        except ValueError as exc:
            parser.error(str(exc))
    else:
        if args.kind is None:
            parser.error("--kind is required unless --request-file is used")
        if args.model_config_import_report_out is not None:
            parser.error("--model-config-import-report-out requires --model-config-file")
        parameters = _load_json_object_from_args(
            parser,
            inline_json=args.parameters,
            json_file=args.parameters_file,
            label="parameters",
        )
        try:
            receipt = build_validated_contract_receipt(args.kind, parameters, pack=pack)
        except ValueError as exc:
            parser.error(str(exc))
    if args.request_out is not None:
        _write_json_file(args.request_out, receipt["request"])
    gate_failures = _receipt_gate_failures(receipt, args)
    if args.format == "json":
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        for line in receipt_summary_lines(receipt):
            print(line)
    for failure in gate_failures:
        print(f"contract receipt gate failed: {failure}", file=sys.stderr)
    return 2 if gate_failures else 0


__all__ = [
    "contract_certify_main",
    "contract_ready_main",
    "contract_receipt_main",
    "rope_certify_main",
    "sparse_attention_certify_main",
]


if __name__ == "__main__":
    raise SystemExit(contract_ready_main())
