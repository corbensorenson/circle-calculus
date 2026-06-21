#!/usr/bin/env python
"""Run parameterized Circle AI contract certifiers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications import (  # noqa: E402
    build_contract_certification_bundle,
    build_contract_certification_bundle_file_check_json_schema,
    build_contract_certification_bundle_file_check_report,
    build_contract_certification_bundle_json_schema,
    build_contract_receipt_file_check_json_schema,
    build_contract_receipt_file_check_report,
    build_contract_receipt_gate_report,
    build_contract_receipt_json_schema,
    build_contract_request,
    build_contract_request_validation_report,
    build_contract_request_validation_json_schema,
    build_rope_model_config_import_json_schema,
    build_rope_model_config_import_report,
    build_validated_contract_receipt_from_request,
    load_contract_pack,
    receipt_summary_lines,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH,
    CERTIFICATION_BUNDLE_SCHEMA_PATH,
    DECISION_ASSURANCE_LEVELS,
    DECISION_VERDICTS,
    RECEIPT_FILE_CHECK_SCHEMA_PATH,
    RECEIPT_SCHEMA_PATH,
    REQUEST_VALIDATION_SCHEMA_PATH,
    ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH,
)


RECEIPT_STATUS_VALUES = (
    "proved",
    "impossible",
    "undecided",
    "numerical_only",
    "outside_scope",
)
DEFAULT_REQUEST_VALIDATION_SCHEMA = ROOT / REQUEST_VALIDATION_SCHEMA_PATH
DEFAULT_ROPE_MODEL_CONFIG_IMPORT_SCHEMA = ROOT / ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH
DEFAULT_RECEIPT_SCHEMA = ROOT / RECEIPT_SCHEMA_PATH
DEFAULT_RECEIPT_CHECK_SCHEMA = ROOT / RECEIPT_FILE_CHECK_SCHEMA_PATH
DEFAULT_CERTIFICATION_BUNDLE_SCHEMA = ROOT / CERTIFICATION_BUNDLE_SCHEMA_PATH
DEFAULT_CERTIFICATION_BUNDLE_CHECK_SCHEMA = (
    ROOT / CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH
)
DEFAULT_PACK_PATH = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"


def parse_tokens(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    return tuple(int(part.strip()) for part in raw.replace(";", ",").split(",") if part.strip())


def parse_strides(raw: str) -> tuple[int, ...]:
    strides = parse_tokens(raw)
    if not strides:
        raise argparse.ArgumentTypeError("strides must contain at least one integer")
    if any(stride <= 0 for stride in strides):
        raise argparse.ArgumentTypeError("strides must be positive")
    return strides


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either a human summary or the full receipt JSON.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for the machine-readable receipt JSON.",
    )
    parser.add_argument(
        "--request-out",
        type=Path,
        help=(
            "Optional path for the exact versioned request JSON used by this "
            "run. For validate-only request files, this writes the loaded request."
        ),
    )
    parser.add_argument(
        "--request-validation-report-out",
        type=Path,
        help=(
            "Optional path for a schema-validated request preflight report for "
            "the exact request used by this run."
        ),
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        help=(
            "Optional directory where a standard audit artifact set is written. "
            "For receipt-producing runs this fills unset output paths for "
            "request, request-validation, receipt, receipt-check, gate, "
            "certification-bundle, and certification-bundle-check JSON files."
        ),
    )
    parser.add_argument(
        "--artifact-prefix",
        help=(
            "Optional filename prefix to use with --artifact-dir. Defaults to "
            "the request/model-config stem when available, otherwise the "
            "contract family name."
        ),
    )
    parser.add_argument(
        "--request-validation-schema",
        type=Path,
        default=DEFAULT_REQUEST_VALIDATION_SCHEMA,
        help=(
            "Generated JSON Schema used to validate request preflight reports. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_request_validation.schema.json."
        ),
    )
    parser.add_argument(
        "--receipt-check-out",
        type=Path,
        help=(
            "Optional path for a schema-validated receipt-check report for "
            "the emitted receipt."
        ),
    )
    parser.add_argument(
        "--gate-report-out",
        type=Path,
        help=(
            "Optional path for a schema-validated in-memory gate report for "
            "the emitted receipt. Unlike --receipt-check-out, this does not "
            "require --json-out."
        ),
    )
    parser.add_argument(
        "--certification-bundle-out",
        type=Path,
        help=(
            "Optional path for a schema-validated bundle containing request "
            "preflight, receipt, and gate report for this run."
        ),
    )
    parser.add_argument(
        "--certification-bundle-check-out",
        type=Path,
        help=(
            "Optional path for a schema-validated verification report for "
            "the emitted --certification-bundle-out file."
        ),
    )
    parser.add_argument(
        "--certification-bundle-schema",
        type=Path,
        default=DEFAULT_CERTIFICATION_BUNDLE_SCHEMA,
        help=(
            "Generated JSON Schema used to validate --certification-bundle-out. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_certification_bundle.schema.json."
        ),
    )
    parser.add_argument(
        "--certification-bundle-check-schema",
        type=Path,
        default=DEFAULT_CERTIFICATION_BUNDLE_CHECK_SCHEMA,
        help=(
            "Generated JSON Schema used to validate "
            "--certification-bundle-check-out. Defaults to "
            "site/data/generated/circle_ai_contract_certification_bundle_file_check.schema.json."
        ),
    )
    parser.add_argument(
        "--receipt-check-schema",
        type=Path,
        default=DEFAULT_RECEIPT_CHECK_SCHEMA,
        help=(
            "Generated JSON Schema used to validate --receipt-check-out and "
            "--gate-report-out reports. Defaults to "
            "site/data/generated/circle_ai_contract_receipt_file_check.schema.json."
        ),
    )
    parser.add_argument(
        "--pack",
        type=Path,
        default=DEFAULT_PACK_PATH,
        help=(
            "Generated contract-pack path used to issue receipts. Defaults "
            "to site/data/generated/circle_ai_contract_pack.json so emitted "
            "receipts match the public pack used by downstream verifiers."
        ),
    )
    parser.add_argument(
        "--receipt-schema",
        type=Path,
        default=DEFAULT_RECEIPT_SCHEMA,
        help=(
            "Generated JSON Schema used to validate emitted receipts. Defaults "
            "to site/data/generated/circle_ai_contract_receipt.schema.json."
        ),
    )
    parser.add_argument(
        "--require-status",
        action="append",
        choices=RECEIPT_STATUS_VALUES,
        default=[],
        help=(
            "Require the emitted receipt status to match this value. May be "
            "passed more than once to allow a small set."
        ),
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        choices=DECISION_VERDICTS,
        default=[],
        help=(
            "Require the emitted receipt decision.verdict to match this value. "
            "May be passed more than once to allow a small set."
        ),
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        choices=DECISION_ASSURANCE_LEVELS,
        default=[],
        help=(
            "Require the emitted receipt decision.assurance to match this value. "
            "May be passed more than once to allow a small set."
        ),
    )
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Exit nonzero unless the emitted receipt has request_passed=true.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Issue theorem-linked Circle AI contract receipts for user-supplied "
            "RoPE, KV-cache, sparse-attention, and recurrence parameters."
        ),
    )
    subparsers = parser.add_subparsers(dest="kind", required=True)

    request = subparsers.add_parser(
        "request",
        help=(
            "Certify a versioned Circle AI contract request JSON object with "
            "schema_id, kind, and parameters."
        ),
    )
    add_common_options(request)
    request.add_argument(
        "--request-json",
        required=True,
        type=Path,
        help="Path to a circle_calculus.ai_contract_request.v0 JSON request.",
    )
    request.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the request file and exit without issuing a receipt.",
    )

    rope = subparsers.add_parser(
        "rope",
        help="Certify a RoPE position-distinguishability configuration.",
    )
    add_common_options(rope)
    rope.add_argument(
        "--model-config",
        type=Path,
        help=(
            "Optional model config.json to infer standard-RoPE head_dim, base, "
            "and context. Explicit flags override inferred values."
        ),
    )
    rope.add_argument(
        "--model-config-import-report-out",
        type=Path,
        help=(
            "Optional path for a schema-validated report describing whether "
            "the model config converted into a standard-RoPE Circle request."
        ),
    )
    rope.add_argument(
        "--model-config-import-schema",
        type=Path,
        default=DEFAULT_ROPE_MODEL_CONFIG_IMPORT_SCHEMA,
        help=(
            "Generated JSON Schema used to validate --model-config-import-report-out. "
            "Defaults to "
            "site/data/generated/circle_ai_rope_model_config_import.schema.json."
        ),
    )
    rope.add_argument("--head-dim", type=int)
    rope.add_argument("--base", type=float)
    rope.add_argument("--context", type=int)
    rope.add_argument("--tolerance", type=float)
    rope.add_argument(
        "--discretization",
        choices=("round", "floor", "ceil"),
    )
    rope.add_argument(
        "--requested-margin",
        help=(
            "Optional real-phase margin request, for example 1/328459. "
            "Currently classified by the D19 channel-0 range theorem when in scope."
        ),
    )

    kv = subparsers.add_parser(
        "kv-cache",
        help="Certify a KV-cache ring-buffer freshness request.",
    )
    add_common_options(kv)
    kv.add_argument("--cache-size", required=True, type=int)
    kv.add_argument("--current", required=True, type=int)
    kv.add_argument("--token", required=True, type=int)
    kv.add_argument("--batch-tokens", type=parse_tokens, default=())
    kv.add_argument("--sink-size", type=int, default=0)
    kv.add_argument("--request-id", default="read_request")

    sparse = subparsers.add_parser(
        "sparse-attention",
        help="Certify a local-window plus stride-family sparse-attention plan.",
    )
    add_common_options(sparse)
    sparse.add_argument("--context", required=True, type=int)
    sparse.add_argument("--strides", required=True, type=parse_strides)
    sparse.add_argument("--path-length", required=True, type=int)
    sparse.add_argument("--local-window", required=True, type=int)

    recurrence = subparsers.add_parser(
        "recurrence",
        help="Certify a finite looped/recursive schedule.",
    )
    add_common_options(recurrence)
    recurrence.add_argument("--loop-period", type=int, default=5)
    recurrence.add_argument("--sample-index", type=int, default=8)
    recurrence.add_argument("--max-loops", type=int, default=7)
    recurrence.add_argument("--token-count", type=int, default=8)
    recurrence.add_argument("--selected-block-start", type=int, default=2)
    recurrence.add_argument("--selected-block-width", type=int, default=3)
    recurrence.add_argument("--shift-passes", type=int, default=3)

    return parser.parse_args()


def _pack_from_args(args: argparse.Namespace) -> dict[str, Any] | None:
    if args.pack is None:
        return None
    path = args.pack
    if not path.is_absolute():
        path = ROOT / path
    return load_contract_pack(path)


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    if not path.is_absolute():
        path = ROOT / path
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label} must be an object")
    return payload


def _load_request_json(path: Path) -> dict[str, Any]:
    return _load_json_object(path, label="request JSON")


def _display_path(path: Path | None) -> str:
    if path is None:
        return "<emitted-receipt>"
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _validated_request_validation_report(
    request: dict[str, Any],
    schema_path: Path,
) -> dict[str, Any]:
    report = build_contract_request_validation_report(request)
    _validate_request_validation_report(report, schema_path)
    return report


def _validate_request_validation_report(
    report: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="request validation schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_contract_request_validation_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "request validation schema drifted from application builder"
        )


def _validate_rope_model_config_import_report(
    report: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="RoPE model config import schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_rope_model_config_import_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "RoPE model config import schema drifted from application builder"
        )


def _validate_receipt_schema(receipt: dict[str, Any], schema_path: Path) -> None:
    schema = _load_json_object(schema_path, label="receipt schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)
    generated_schema = build_contract_receipt_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "receipt schema drifted from application builder"
        )


def _validate_receipt_check_report(
    report: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="receipt-check schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_contract_receipt_file_check_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "receipt-check schema drifted from application builder"
        )


def _validate_certification_bundle(
    bundle: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="certification-bundle schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(bundle, schema)
    generated_schema = build_contract_certification_bundle_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "certification-bundle schema drifted from application builder"
        )


def _validate_certification_bundle_check_report(
    report: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="certification-bundle check schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_contract_certification_bundle_file_check_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "certification-bundle check schema drifted from application builder"
        )


def _parameters_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if args.kind == "rope":
        return {
            "head_dim": 128 if args.head_dim is None else args.head_dim,
            "base": 10000.0 if args.base is None else args.base,
            "context": 32768 if args.context is None else args.context,
            "tolerance": 1e-6 if args.tolerance is None else args.tolerance,
            "discretization": "round"
            if args.discretization is None
            else args.discretization,
            "requested_margin": args.requested_margin,
        }
    if args.kind == "kv-cache":
        return {
            "cache_size": args.cache_size,
            "current": args.current,
            "token": args.token,
            "batch_tokens": args.batch_tokens,
            "sink_size": args.sink_size,
            "request_id": args.request_id,
        }
    if args.kind == "sparse-attention":
        return {
            "context": args.context,
            "strides": args.strides,
            "path_length": args.path_length,
            "local_window": args.local_window,
        }
    if args.kind == "recurrence":
        return {
            "loop_period": args.loop_period,
            "sample_index": args.sample_index,
            "max_loops": args.max_loops,
            "token_count": args.token_count,
            "selected_block_start": args.selected_block_start,
            "selected_block_width": args.selected_block_width,
            "shift_passes": args.shift_passes,
        }
    raise SystemExit(f"unsupported subcommand: {args.kind}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_artifact_prefix(raw: str) -> str:
    safe = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "_"
        for char in raw.strip()
    ).strip("._-")
    return safe or "circle_ai_contract"


def _default_artifact_prefix(args: argparse.Namespace) -> str:
    if args.artifact_prefix:
        return _safe_artifact_prefix(args.artifact_prefix)
    if args.kind == "request":
        return _safe_artifact_prefix(
            Path(args.request_json).stem.removesuffix("_request")
        )
    if args.kind == "rope" and args.model_config is not None:
        return _safe_artifact_prefix(Path(args.model_config).stem)
    return {
        "rope": "rope",
        "kv-cache": "kv_cache",
        "sparse-attention": "sparse_attention",
        "recurrence": "recurrence",
    }.get(args.kind, _safe_artifact_prefix(args.kind))


def _fill_artifact_path(
    args: argparse.Namespace,
    attr: str,
    artifact_dir: Path,
    prefix: str,
    suffix: str,
) -> None:
    if getattr(args, attr) is None:
        setattr(args, attr, artifact_dir / f"{prefix}_{suffix}.json")


def _apply_artifact_dir_defaults(args: argparse.Namespace) -> None:
    if args.artifact_prefix and args.artifact_dir is None:
        raise SystemExit("--artifact-prefix requires --artifact-dir")
    if args.artifact_dir is None:
        return
    prefix = _default_artifact_prefix(args)
    artifact_dir = args.artifact_dir
    _fill_artifact_path(args, "request_out", artifact_dir, prefix, "request")
    _fill_artifact_path(
        args,
        "request_validation_report_out",
        artifact_dir,
        prefix,
        "request_validation",
    )
    if args.kind == "request" and args.validate_only:
        return
    if args.kind == "rope" and args.model_config is not None:
        _fill_artifact_path(
            args,
            "model_config_import_report_out",
            artifact_dir,
            prefix,
            "model_config_import",
        )
    _fill_artifact_path(args, "json_out", artifact_dir, prefix, "receipt")
    _fill_artifact_path(args, "receipt_check_out", artifact_dir, prefix, "receipt_check")
    _fill_artifact_path(args, "gate_report_out", artifact_dir, prefix, "gate_report")
    _fill_artifact_path(
        args,
        "certification_bundle_out",
        artifact_dir,
        prefix,
        "certification_bundle",
    )
    _fill_artifact_path(
        args,
        "certification_bundle_check_out",
        artifact_dir,
        prefix,
        "certification_bundle_check",
    )


def _receipt_gate_failures(receipt: dict[str, Any], args: argparse.Namespace) -> list[str]:
    failures: list[str] = []
    if args.require_status and receipt.get("status") not in set(args.require_status):
        allowed = ", ".join(args.require_status)
        failures.append(
            f"receipt status {receipt.get('status')!r} did not match required "
            f"status set: {allowed}"
        )
    decision = receipt.get("decision")
    decision_verdict = decision.get("verdict") if isinstance(decision, dict) else None
    decision_assurance = (
        decision.get("assurance") if isinstance(decision, dict) else None
    )
    if args.require_decision and decision_verdict not in set(args.require_decision):
        allowed = ", ".join(args.require_decision)
        failures.append(
            f"receipt decision verdict {decision_verdict!r} did not match "
            f"required decision set: {allowed}"
        )
    if args.require_assurance and decision_assurance not in set(args.require_assurance):
        allowed = ", ".join(args.require_assurance)
        failures.append(
            f"receipt assurance {decision_assurance!r} did not match "
            f"required assurance set: {allowed}"
        )
    if args.require_passed and receipt.get("request_passed") is not True:
        failures.append(
            "receipt request_passed was not true "
            f"(got {receipt.get('request_passed')!r})"
        )
    return failures


def _artifact_summary_line(args: argparse.Namespace) -> str | None:
    artifacts = [
        ("request_json", args.request_out),
        ("request_validation_report", args.request_validation_report_out),
        ("receipt_json", args.json_out),
        ("receipt_check", args.receipt_check_out),
        ("gate_report", args.gate_report_out),
        ("certification_bundle", args.certification_bundle_out),
        ("certification_bundle_check", args.certification_bundle_check_out),
    ]
    model_config_import_report_out = getattr(
        args,
        "model_config_import_report_out",
        None,
    )
    artifacts.insert(2, ("model_config_import_report", model_config_import_report_out))
    written = [
        f"{label}={_display_path(path)}"
        for label, path in artifacts
        if path is not None
    ]
    if not written:
        return None
    return "artifacts=" + " ".join(written)


def main() -> int:
    args = parse_args()
    _apply_artifact_dir_defaults(args)
    if (
        getattr(args, "model_config_import_report_out", None) is not None
        and getattr(args, "model_config", None) is None
    ):
        raise SystemExit("--model-config-import-report-out requires --model-config")
    if args.receipt_check_out is not None and args.json_out is None:
        raise SystemExit(
            "--receipt-check-out requires --json-out so the report points at "
            "a saved receipt file"
        )
    if (
        args.certification_bundle_check_out is not None
        and args.certification_bundle_out is None
    ):
        raise SystemExit(
            "--certification-bundle-check-out requires --certification-bundle-out "
            "so the report points at a saved certification bundle"
        )
    request_for_bundle: dict[str, Any] | None = None
    model_config_import_report_for_bundle: dict[str, Any] | None = None
    if args.kind == "request":
        request_object = _load_request_json(args.request_json)
        if args.request_out is not None:
            write_json(args.request_out, request_object)
        if args.validate_only:
            if (
                args.require_status
                or args.require_decision
                or args.require_assurance
                or args.require_passed
                or args.receipt_check_out
                or args.gate_report_out
                or args.certification_bundle_out
                or args.certification_bundle_check_out
            ):
                raise SystemExit(
                    "--require-status, --require-decision, --require-assurance, "
                    "--require-passed, --receipt-check-out, --gate-report-out, "
                    "--certification-bundle-out, and "
                    "--certification-bundle-check-out require a receipt; omit "
                    "--validate-only"
                )
            report = _validated_request_validation_report(
                request_object,
                args.request_validation_schema,
            )
            if args.request_validation_report_out is not None:
                write_json(args.request_validation_report_out, report)
            if args.json_out is not None:
                write_json(args.json_out, report)
            if args.format == "json":
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(
                    "circle_ai_contract_request_validation="
                    f"{report['ok']} kind={report['kind']} "
                    f"canonical_kind={report['canonical_kind']} "
                    f"failures={report['failure_count']}"
                )
                artifact_line = _artifact_summary_line(args)
                if artifact_line is not None:
                    print(artifact_line)
                for failure in report["failures"]:
                    print(f"failure={failure}", file=sys.stderr)
            return 0 if report["ok"] else 1
        if args.request_validation_report_out is not None:
            report = _validated_request_validation_report(
                request_object,
                args.request_validation_schema,
            )
            write_json(args.request_validation_report_out, report)
        pack = _pack_from_args(args)
        request_for_bundle = request_object
        try:
            receipt = build_validated_contract_receipt_from_request(
                request_object,
                pack=pack,
            )
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    else:
        pack = _pack_from_args(args)
        try:
            request: dict[str, Any] | None = None
            if args.kind == "rope" and args.model_config is not None:
                config = _load_json_object(args.model_config, label="model config JSON")
                import_report = build_rope_model_config_import_report(
                    config,
                    head_dim=args.head_dim,
                    base=args.base,
                    context=args.context,
                    tolerance=args.tolerance,
                    discretization=args.discretization,
                    requested_margin=args.requested_margin,
                )
                if args.model_config_import_report_out is not None:
                    _validate_rope_model_config_import_report(
                        import_report,
                        args.model_config_import_schema,
                    )
                    write_json(args.model_config_import_report_out, import_report)
                model_config_import_report_for_bundle = import_report
                if not import_report["ok"]:
                    raise ValueError("; ".join(import_report["failures"]))
                if not isinstance(import_report["request"], dict):
                    raise ValueError("model config import report did not emit a request")
                request = import_report["request"]
            if request is None:
                request = build_contract_request(args.kind, _parameters_from_args(args))
            request_for_bundle = request
            if args.request_out is not None:
                write_json(args.request_out, request)
            if args.request_validation_report_out is not None:
                report = _validated_request_validation_report(
                    request,
                    args.request_validation_schema,
                )
                write_json(args.request_validation_report_out, report)
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    assert pack is not None
    _validate_receipt_schema(receipt, args.receipt_schema)
    gate_failures = _receipt_gate_failures(receipt, args)
    if args.json_out is not None:
        write_json(args.json_out, receipt)
    if args.receipt_check_out is not None:
        check_report = build_contract_receipt_file_check_report(
            receipt,
            pack=pack,
            receipt_path=_display_path(args.json_out),
            required_statuses=tuple(args.require_status),
            required_decision_verdicts=tuple(args.require_decision),
            required_assurance_levels=tuple(args.require_assurance),
            require_passed=args.require_passed,
        )
        _validate_receipt_check_report(check_report, args.receipt_check_schema)
        write_json(args.receipt_check_out, check_report)
    if args.gate_report_out is not None:
        gate_report = build_contract_receipt_gate_report(
            receipt,
            pack=pack,
            receipt_path=(
                _display_path(args.json_out)
                if args.json_out is not None
                else "<in-memory-receipt>"
            ),
            required_statuses=tuple(args.require_status),
            required_decision_verdicts=tuple(args.require_decision),
            required_assurance_levels=tuple(args.require_assurance),
            require_passed=args.require_passed,
        )
        _validate_receipt_check_report(gate_report, args.receipt_check_schema)
        write_json(args.gate_report_out, gate_report)
    if args.certification_bundle_out is not None:
        assert request_for_bundle is not None
        bundle = build_contract_certification_bundle(
            request_for_bundle,
            pack=pack,
            model_config_import_report=model_config_import_report_for_bundle,
            receipt_path=(
                _display_path(args.json_out)
                if args.json_out is not None
                else "<in-memory-receipt>"
            ),
            required_statuses=tuple(args.require_status),
            required_decision_verdicts=tuple(args.require_decision),
            required_assurance_levels=tuple(args.require_assurance),
            require_passed=args.require_passed,
        )
        _validate_certification_bundle(bundle, args.certification_bundle_schema)
        write_json(args.certification_bundle_out, bundle)
        if args.certification_bundle_check_out is not None:
            bundle_check_report = build_contract_certification_bundle_file_check_report(
                bundle,
                pack=pack,
                bundle_path=_display_path(args.certification_bundle_out),
                required_statuses=tuple(args.require_status),
                required_decision_verdicts=tuple(args.require_decision),
                required_assurance_levels=tuple(args.require_assurance),
                require_passed=args.require_passed,
            )
            _validate_certification_bundle_check_report(
                bundle_check_report,
                args.certification_bundle_check_schema,
            )
            write_json(args.certification_bundle_check_out, bundle_check_report)
    if args.format == "json":
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        for line in receipt_summary_lines(receipt):
            print(line)
        artifact_line = _artifact_summary_line(args)
        if artifact_line is not None:
            print(artifact_line)
    for failure in gate_failures:
        print(f"receipt_gate_failure={failure}", file=sys.stderr)
    return 0 if not gate_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
