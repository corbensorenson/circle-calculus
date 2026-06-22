#!/usr/bin/env python
"""Run parameterized Circle AI contract certifiers."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications import (  # noqa: E402
    build_contract_artifact_manifest_file_check_json_schema,
    build_contract_artifact_manifest_file_check_report,
    build_contract_artifact_manifest_json_schema,
    build_contract_certification_bundle,
    build_contract_certification_bundle_file_check_json_schema,
    build_contract_certification_bundle_file_check_report,
    build_contract_certification_bundle_json_schema,
    build_contract_receipt_file_check_json_schema,
    build_contract_receipt_file_check_report,
    build_contract_receipt_gate_report,
    build_contract_receipt_replay_check_json_schema,
    build_contract_receipt_replay_check_report,
    build_contract_receipt_json_schema,
    build_architecture_config_import_json_schema,
    build_architecture_config_import_report,
    build_contract_request,
    build_contract_request_from_architecture_config,
    build_contract_request_validation_report,
    build_contract_request_validation_json_schema,
    build_compact_contract_receipt,
    build_compact_contract_receipt_json_schema,
    build_rope_model_config_import_json_schema,
    build_rope_model_config_import_report,
    build_validated_contract_receipt_from_request,
    load_contract_pack,
    receipt_summary_lines,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_PATH,
    ARTIFACT_MANIFEST_SCHEMA_ID,
    ARTIFACT_MANIFEST_SCHEMA_PATH,
    CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH,
    CERTIFICATION_BUNDLE_SCHEMA_PATH,
    CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID,
    CERTIFICATION_BUNDLE_SCHEMA_ID,
    COMPACT_RECEIPT_SCHEMA_ID,
    COMPACT_RECEIPT_SCHEMA_PATH,
    DECISION_ASSURANCE_LEVELS,
    DECISION_VERDICTS,
    RECEIPT_FILE_CHECK_SCHEMA_ID,
    RECEIPT_FILE_CHECK_SCHEMA_PATH,
    RECEIPT_REPLAY_CHECK_SCHEMA_ID,
    RECEIPT_REPLAY_CHECK_SCHEMA_PATH,
    RECEIPT_SCHEMA_ID,
    RECEIPT_SCHEMA_PATH,
    REQUEST_SCHEMA_ID,
    REQUEST_VALIDATION_SCHEMA_PATH,
    REQUEST_VALIDATION_SCHEMA_ID,
    ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID,
    ARCHITECTURE_CONFIG_IMPORT_SCHEMA_PATH,
    ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID,
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
DEFAULT_ARCHITECTURE_CONFIG_IMPORT_SCHEMA = ROOT / ARCHITECTURE_CONFIG_IMPORT_SCHEMA_PATH
DEFAULT_ROPE_MODEL_CONFIG_IMPORT_SCHEMA = ROOT / ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH
DEFAULT_RECEIPT_SCHEMA = ROOT / RECEIPT_SCHEMA_PATH
DEFAULT_COMPACT_RECEIPT_SCHEMA = ROOT / COMPACT_RECEIPT_SCHEMA_PATH
DEFAULT_RECEIPT_CHECK_SCHEMA = ROOT / RECEIPT_FILE_CHECK_SCHEMA_PATH
DEFAULT_RECEIPT_REPLAY_CHECK_SCHEMA = ROOT / RECEIPT_REPLAY_CHECK_SCHEMA_PATH
DEFAULT_CERTIFICATION_BUNDLE_SCHEMA = ROOT / CERTIFICATION_BUNDLE_SCHEMA_PATH
DEFAULT_CERTIFICATION_BUNDLE_CHECK_SCHEMA = (
    ROOT / CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH
)
DEFAULT_ARTIFACT_MANIFEST_SCHEMA = ROOT / ARTIFACT_MANIFEST_SCHEMA_PATH
DEFAULT_ARTIFACT_MANIFEST_CHECK_SCHEMA = ROOT / ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_PATH
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
        choices=("text", "json", "compact-json"),
        default="text",
        help=(
            "Print a human summary, the full receipt JSON, or a compact "
            "downstream-consumer receipt view."
        ),
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for the machine-readable receipt JSON.",
    )
    parser.add_argument(
        "--compact-json-out",
        type=Path,
        help=(
            "Optional path for the compact downstream-consumer receipt JSON. "
            "--json-out remains the full audit receipt."
        ),
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
            "receipt-replay-check, certification-bundle, "
            "certification-bundle-check, artifact-manifest, and "
            "artifact-manifest-check JSON files."
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
        "--artifact-manifest-out",
        type=Path,
        help=(
            "Optional path for a schema-validated JSON manifest indexing "
            "the artifact files written by this invocation."
        ),
    )
    parser.add_argument(
        "--artifact-manifest-schema",
        type=Path,
        default=DEFAULT_ARTIFACT_MANIFEST_SCHEMA,
        help=(
            "Generated JSON Schema used to validate --artifact-manifest-out. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_artifact_manifest.schema.json."
        ),
    )
    parser.add_argument(
        "--artifact-manifest-check-out",
        type=Path,
        help=(
            "Optional path for a schema-validated verification report for "
            "the emitted --artifact-manifest-out file."
        ),
    )
    parser.add_argument(
        "--artifact-manifest-check-schema",
        type=Path,
        default=DEFAULT_ARTIFACT_MANIFEST_CHECK_SCHEMA,
        help=(
            "Generated JSON Schema used to validate "
            "--artifact-manifest-check-out. Defaults to "
            "site/data/generated/"
            "circle_ai_contract_artifact_manifest_file_check.schema.json."
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
        "--receipt-replay-check-out",
        type=Path,
        help=(
            "Optional path for a schema-validated report that rebuilds the "
            "emitted receipt from its embedded request and compares replay "
            "fingerprints."
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
        "--receipt-replay-check-schema",
        type=Path,
        default=DEFAULT_RECEIPT_REPLAY_CHECK_SCHEMA,
        help=(
            "Generated JSON Schema used to validate "
            "--receipt-replay-check-out reports. Defaults to "
            "site/data/generated/circle_ai_contract_receipt_replay_check.schema.json."
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
        "--compact-receipt-schema",
        type=Path,
        default=DEFAULT_COMPACT_RECEIPT_SCHEMA,
        help=(
            "Generated JSON Schema used to validate compact receipt views. "
            "Defaults to "
            "site/data/generated/circle_ai_contract_compact_receipt.schema.json."
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
    parser.add_argument(
        "--require-kind",
        action="append",
        default=[],
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "contract kind. Requires --artifact-manifest-check-out or "
            "--artifact-dir."
        ),
    )
    parser.add_argument(
        "--require-theorem-id",
        action="append",
        default=[],
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "theorem id. Requires --artifact-manifest-check-out or "
            "--artifact-dir."
        ),
    )
    parser.add_argument(
        "--require-evidence-field",
        action="append",
        default=[],
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "receipt evidence field. Requires --artifact-manifest-check-out or "
            "--artifact-dir."
        ),
    )
    parser.add_argument(
        "--require-recommendation-id",
        action="append",
        default=[],
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "planner recommendation id. Requires --artifact-manifest-check-out "
            "or --artifact-dir."
        ),
    )
    parser.add_argument(
        "--require-validation-command",
        action="append",
        default=[],
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "exact validation command. Requires --artifact-manifest-check-out "
            "or --artifact-dir."
        ),
    )
    parser.add_argument(
        "--require-model-config-fingerprint",
        action="append",
        default=[],
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "RoPE model-config SHA-256 fingerprint. Requires "
            "--artifact-manifest-check-out or --artifact-dir."
        ),
    )
    parser.add_argument(
        "--require-architecture-config-fingerprint",
        action="append",
        default=[],
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "architecture-config SHA-256 fingerprint. Requires "
            "--artifact-manifest-check-out or --artifact-dir."
        ),
    )
    parser.add_argument(
        "--require-normalized-param",
        action="append",
        default=[],
        metavar="KEY=JSON_VALUE",
        help=(
            "Require the emitted artifact-manifest check report to include this "
            "top-level normalized_request parameter value. Requires "
            "--artifact-manifest-check-out or --artifact-dir."
        ),
    )
    parser.add_argument(
        "--pin-policy",
        type=Path,
        help=(
            "Load artifact dependency pins from a JSON object shaped like a "
            "check report pin_policy block. A whole prior check report is also "
            "accepted. Explicit --require-* flags are merged with loaded pins. "
            "Requires --artifact-manifest-check-out or --artifact-dir when the "
            "loaded policy is non-empty."
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Issue theorem-linked Circle AI contract receipts for user-supplied "
            "RoPE, KV-cache, sparse-attention, recurrence, and other ready "
            "Circle AI contract parameters."
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
            "Optional model config.json, or model directory containing "
            "config.json, to infer standard-RoPE head_dim, base, and context. "
            "Explicit flags override inferred values."
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
    rope.add_argument(
        "--architecture-config",
        "--architecture-config-file",
        dest="architecture_config",
        type=Path,
        help=(
            "Optional project-level AI architecture config JSON. Reads explicit "
            "rope/rotary aliases and lets explicit flags override imported values. "
            "Use --model-config for standard model config.json files."
        ),
    )
    rope.add_argument("--architecture-config-import-report-out", type=Path)
    rope.add_argument(
        "--architecture-config-import-schema",
        type=Path,
        default=DEFAULT_ARCHITECTURE_CONFIG_IMPORT_SCHEMA,
        help=(
            "Generated JSON Schema used to validate "
            "--architecture-config-import-report-out. Defaults to "
            "site/data/generated/circle_ai_architecture_config_import.schema.json."
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
    rope.add_argument(
        "--turn-ratio-numerator",
        type=int,
        help=(
            "Optional numerator for an explicitly declared rational/discretized "
            "turn-ratio finite-margin certificate. Must be paired with "
            "--turn-ratio-denominator."
        ),
    )
    rope.add_argument(
        "--turn-ratio-denominator",
        type=int,
        help=(
            "Optional positive denominator for an explicitly declared "
            "rational/discretized turn-ratio finite-margin certificate."
        ),
    )

    kv = subparsers.add_parser(
        "kv-cache",
        help="Certify a KV-cache ring-buffer freshness request.",
    )
    add_common_options(kv)
    kv.add_argument(
        "--architecture-config",
        "--architecture-config-file",
        dest="architecture_config",
        type=Path,
        help=(
            "Optional AI architecture config JSON. Reads kv_cache/cache aliases "
            "and lets explicit flags override imported values."
        ),
    )
    kv.add_argument("--architecture-config-import-report-out", type=Path)
    kv.add_argument(
        "--architecture-config-import-schema",
        type=Path,
        default=DEFAULT_ARCHITECTURE_CONFIG_IMPORT_SCHEMA,
    )
    kv.add_argument("--cache-size", type=int)
    kv.add_argument("--current", type=int)
    kv.add_argument("--token", type=int)
    kv.add_argument("--batch-tokens", type=parse_tokens)
    kv.add_argument("--sink-size", type=int)
    kv.add_argument("--request-id")

    sparse = subparsers.add_parser(
        "sparse-attention",
        help="Certify a local-window plus stride-family sparse-attention plan.",
    )
    add_common_options(sparse)
    sparse.add_argument(
        "--architecture-config",
        "--architecture-config-file",
        dest="architecture_config",
        type=Path,
        help=(
            "Optional AI architecture config JSON. Reads sparse_attention/"
            "attention aliases and lets explicit flags override imported values."
        ),
    )
    sparse.add_argument("--architecture-config-import-report-out", type=Path)
    sparse.add_argument(
        "--architecture-config-import-schema",
        type=Path,
        default=DEFAULT_ARCHITECTURE_CONFIG_IMPORT_SCHEMA,
    )
    sparse.add_argument("--context", type=int)
    sparse.add_argument("--strides", type=parse_strides)
    sparse.add_argument("--path-length", type=int)
    sparse.add_argument("--local-window", type=int)

    recurrence = subparsers.add_parser(
        "recurrence",
        help="Certify a finite looped/recursive schedule.",
    )
    add_common_options(recurrence)
    recurrence.add_argument(
        "--architecture-config",
        "--architecture-config-file",
        dest="architecture_config",
        type=Path,
        help=(
            "Optional AI architecture config JSON. Reads recurrence/loop aliases "
            "and lets explicit flags override imported values."
        ),
    )
    recurrence.add_argument("--architecture-config-import-report-out", type=Path)
    recurrence.add_argument(
        "--architecture-config-import-schema",
        type=Path,
        default=DEFAULT_ARCHITECTURE_CONFIG_IMPORT_SCHEMA,
    )
    recurrence.add_argument("--loop-period", "--period", dest="loop_period", type=int)
    recurrence.add_argument(
        "--sample-index",
        "--position",
        dest="sample_index",
        type=int,
    )
    recurrence.add_argument(
        "--max-loops",
        "--horizon-steps",
        "--loop-budget",
        dest="max_loops",
        type=int,
    )
    recurrence.add_argument(
        "--token-count",
        "--sequence-length",
        "--seq-len",
        "--tokens",
        dest="token_count",
        type=int,
    )
    recurrence.add_argument(
        "--selected-block-start",
        "--block-start",
        dest="selected_block_start",
        type=int,
    )
    recurrence.add_argument(
        "--selected-block-width",
        "--block-width",
        dest="selected_block_width",
        type=int,
    )
    recurrence.add_argument(
        "--shift-passes",
        "--shift-periods",
        dest="shift_passes",
        type=int,
    )
    recurrence.add_argument(
        "--shift-amount",
        type=int,
        help=(
            "Whole-token shift amount for the periodic-shift check. Must be "
            "a nonnegative multiple of the loop period; converted to "
            "--shift-passes in the emitted canonical request."
        ),
    )

    fanout = subparsers.add_parser(
        "strided-fanout",
        help="Certify finite strided candidate-fanout reach and budget facts.",
    )
    add_common_options(fanout)
    fanout.add_argument("--context-length", type=int, default=12)
    fanout.add_argument("--stride", type=int, default=5)
    fanout.add_argument("--start-index", type=int, default=0)
    fanout.add_argument("--path-length", type=int, default=12)

    memory = subparsers.add_parser(
        "cyclic-memory",
        help="Certify cyclic memory residue/winding and finite alias-load facts.",
    )
    add_common_options(memory)
    memory.add_argument("--bank-size", type=int, default=8)
    memory.add_argument("--event-index", type=int, default=23)
    memory.add_argument("--event-count", type=int, default=32)

    phase = subparsers.add_parser(
        "multicoil-phase",
        help="Certify MultiCoil phase tags and relative-phase invariants.",
    )
    add_common_options(phase)
    phase.add_argument("--periods", type=parse_strides, default=(5, 7))
    phase.add_argument("--position", type=int, default=37)
    phase.add_argument("--query-position", type=int, default=41)
    phase.add_argument("--key-position", type=int, default=18)

    mixer = subparsers.add_parser(
        "cyclic-mixer",
        help="Certify circulant parity and block-cyclic mixer accounting facts.",
    )
    add_common_options(mixer)
    mixer.add_argument("--period", type=int, default=8)
    mixer.add_argument("--channel-count", type=int, default=128)
    mixer.add_argument("--block-size", type=int, default=8)

    seed_rule = subparsers.add_parser(
        "seed-rule",
        help="Certify finite seed/rule exact-regeneration and storage facts.",
    )
    add_common_options(seed_rule)
    seed_rule.add_argument("--n", type=int, default=128)

    return parser.parse_args()


def _pack_from_args(args: argparse.Namespace) -> dict[str, Any] | None:
    if args.pack is None:
        return None
    path = args.pack
    if not path.is_absolute():
        path = ROOT / path
    return load_contract_pack(path)


def _load_json_object(
    path: Path,
    *,
    label: str,
    allow_config_dir: bool = False,
) -> dict[str, Any]:
    if not path.is_absolute():
        path = ROOT / path
    if path.is_dir():
        if not allow_config_dir:
            raise SystemExit(f"{label} path must be a JSON file, not a directory")
        path = path / "config.json"
    if not path.exists():
        raise SystemExit(f"{label} path does not exist: {path}")
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


def _validate_architecture_config_import_report(
    report: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(
        schema_path,
        label="architecture config import schema",
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_architecture_config_import_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "architecture config import schema drifted from application builder"
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


def _validate_compact_receipt_schema(
    compact_receipt: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="compact receipt schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(compact_receipt, schema)
    generated_schema = build_compact_contract_receipt_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "compact receipt schema drifted from application builder"
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


def _validate_receipt_replay_check_report(
    report: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="receipt-replay-check schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_contract_receipt_replay_check_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "receipt-replay-check schema drifted from application builder"
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


def _architecture_overrides_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if args.kind == "rope":
        return {
            "head_dim": args.head_dim,
            "base": args.base,
            "context": args.context,
            "tolerance": args.tolerance,
            "discretization": args.discretization,
            "requested_margin": args.requested_margin,
            "turn_ratio_numerator": args.turn_ratio_numerator,
            "turn_ratio_denominator": args.turn_ratio_denominator,
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
            "shift_amount": args.shift_amount,
        }
    raise ValueError(f"{args.kind} does not support --architecture-config")


def _recurrence_shift_passes_from_amount(
    *,
    loop_period: int,
    shift_amount: int,
) -> int:
    if loop_period <= 0:
        raise SystemExit("--shift-amount requires a positive loop period")
    if shift_amount < 0:
        raise SystemExit("--shift-amount must be nonnegative")
    if shift_amount % loop_period != 0:
        raise SystemExit(
            "--shift-amount must be an exact multiple of the loop period "
            f"({shift_amount} is not divisible by {loop_period})"
        )
    return shift_amount // loop_period


def _recurrence_shift_passes_from_args(
    args: argparse.Namespace,
    *,
    loop_period: int,
    default_shift_passes: int | None = None,
) -> int | None:
    if args.shift_amount is None:
        if args.shift_passes is None:
            return default_shift_passes
        return args.shift_passes
    derived = _recurrence_shift_passes_from_amount(
        loop_period=loop_period,
        shift_amount=args.shift_amount,
    )
    if args.shift_passes is not None and args.shift_passes != derived:
        raise SystemExit(
            "--shift-passes and --shift-amount disagree "
            f"({args.shift_passes} passes != {derived} passes from shift amount)"
        )
    return derived


def _architecture_parameters_from_args(
    args: argparse.Namespace,
    kind: str,
) -> dict[str, Any]:
    config = _load_json_object(
        args.architecture_config,
        label="architecture config JSON",
    )
    request = build_contract_request_from_architecture_config(
        kind,
        config,
        overrides=_architecture_overrides_from_args(args),
    )
    parameters = request["parameters"]
    assert isinstance(parameters, dict)
    return parameters


def _parameters_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if args.kind == "rope":
        if args.architecture_config is not None:
            return _architecture_parameters_from_args(
                args,
                "rope",
            )
        parameters = {
            "head_dim": 128 if args.head_dim is None else args.head_dim,
            "base": 10000.0 if args.base is None else args.base,
            "context": 32768 if args.context is None else args.context,
            "tolerance": 1e-6 if args.tolerance is None else args.tolerance,
            "discretization": "round"
            if args.discretization is None
            else args.discretization,
            "requested_margin": args.requested_margin,
        }
        if args.turn_ratio_numerator is not None:
            parameters["turn_ratio_numerator"] = args.turn_ratio_numerator
        if args.turn_ratio_denominator is not None:
            parameters["turn_ratio_denominator"] = args.turn_ratio_denominator
        return parameters
    if args.kind == "kv-cache":
        if args.architecture_config is not None:
            return _architecture_parameters_from_args(
                args,
                "kv-cache",
            )
        return {
            "cache_size": args.cache_size,
            "current": args.current,
            "token": args.token,
            "batch_tokens": () if args.batch_tokens is None else args.batch_tokens,
            "sink_size": 0 if args.sink_size is None else args.sink_size,
            "request_id": "read_request" if args.request_id is None else args.request_id,
        }
    if args.kind == "sparse-attention":
        if args.architecture_config is not None:
            return _architecture_parameters_from_args(
                args,
                "sparse-attention",
            )
        return {
            "context": args.context,
            "strides": args.strides,
            "path_length": args.path_length,
            "local_window": args.local_window,
        }
    if args.kind == "recurrence":
        if args.architecture_config is not None:
            parameters = _architecture_parameters_from_args(
                args,
                "recurrence",
            )
            if args.shift_amount is not None:
                loop_period = int(parameters["loop_period"])
                parameters["shift_passes"] = _recurrence_shift_passes_from_args(
                    args,
                    loop_period=loop_period,
                    default_shift_passes=None,
                )
            return parameters
        loop_period = 5 if args.loop_period is None else args.loop_period
        shift_passes = _recurrence_shift_passes_from_args(
            args,
            loop_period=loop_period,
            default_shift_passes=3,
        )
        return {
            "loop_period": loop_period,
            "sample_index": 8 if args.sample_index is None else args.sample_index,
            "max_loops": 7 if args.max_loops is None else args.max_loops,
            "token_count": 8 if args.token_count is None else args.token_count,
            "selected_block_start": 2
            if args.selected_block_start is None
            else args.selected_block_start,
            "selected_block_width": 3
            if args.selected_block_width is None
            else args.selected_block_width,
            "shift_passes": shift_passes,
        }
    if args.kind == "strided-fanout":
        return {
            "context_length": args.context_length,
            "stride": args.stride,
            "start_index": args.start_index,
            "path_length": args.path_length,
        }
    if args.kind == "cyclic-memory":
        return {
            "bank_size": args.bank_size,
            "event_index": args.event_index,
            "event_count": args.event_count,
        }
    if args.kind == "multicoil-phase":
        return {
            "periods": args.periods,
            "position": args.position,
            "query_position": args.query_position,
            "key_position": args.key_position,
        }
    if args.kind == "cyclic-mixer":
        return {
            "period": args.period,
            "channel_count": args.channel_count,
            "block_size": args.block_size,
        }
    if args.kind == "seed-rule":
        return {"n": args.n}
    raise SystemExit(f"unsupported subcommand: {args.kind}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    if args.kind == "rope" and getattr(args, "architecture_config", None) is not None:
        return _safe_artifact_prefix(Path(args.architecture_config).stem)
    return {
        "rope": "rope",
        "kv-cache": "kv_cache",
        "sparse-attention": "sparse_attention",
        "recurrence": "recurrence",
        "strided-fanout": "strided_fanout",
        "cyclic-memory": "cyclic_memory",
        "multicoil-phase": "multicoil_phase",
        "cyclic-mixer": "cyclic_mixer",
        "seed-rule": "seed_rule",
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
        _fill_artifact_path(
            args,
            "artifact_manifest_out",
            artifact_dir,
            prefix,
            "artifact_manifest",
        )
        _fill_artifact_path(
            args,
            "artifact_manifest_check_out",
            artifact_dir,
            prefix,
            "artifact_manifest_check",
        )
        return
    if args.kind == "rope" and args.model_config is not None:
        _fill_artifact_path(
            args,
            "model_config_import_report_out",
            artifact_dir,
            prefix,
            "model_config_import",
        )
    if (
        args.kind in {"rope", "kv-cache", "sparse-attention", "recurrence"}
        and getattr(args, "architecture_config", None) is not None
    ):
        _fill_artifact_path(
            args,
            "architecture_config_import_report_out",
            artifact_dir,
            prefix,
            "architecture_config_import",
        )
    _fill_artifact_path(args, "json_out", artifact_dir, prefix, "receipt")
    _fill_artifact_path(
        args,
        "compact_json_out",
        artifact_dir,
        prefix,
        "compact_receipt",
    )
    _fill_artifact_path(args, "receipt_check_out", artifact_dir, prefix, "receipt_check")
    _fill_artifact_path(
        args,
        "receipt_replay_check_out",
        artifact_dir,
        prefix,
        "receipt_replay_check",
    )
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
    _fill_artifact_path(
        args,
        "artifact_manifest_out",
        artifact_dir,
        prefix,
        "artifact_manifest",
    )
    _fill_artifact_path(
        args,
        "artifact_manifest_check_out",
        artifact_dir,
        prefix,
        "artifact_manifest_check",
    )


def _artifact_paths_for_manifest(args: argparse.Namespace) -> list[tuple[str, Path, str]]:
    artifacts = [
        ("request_json", args.request_out, REQUEST_SCHEMA_ID),
        (
            "request_validation_report",
            args.request_validation_report_out,
            REQUEST_VALIDATION_SCHEMA_ID,
        ),
        ("receipt_json", args.json_out, RECEIPT_SCHEMA_ID),
        ("compact_receipt_json", args.compact_json_out, COMPACT_RECEIPT_SCHEMA_ID),
        ("receipt_check", args.receipt_check_out, RECEIPT_FILE_CHECK_SCHEMA_ID),
        (
            "receipt_replay_check",
            args.receipt_replay_check_out,
            RECEIPT_REPLAY_CHECK_SCHEMA_ID,
        ),
        ("gate_report", args.gate_report_out, RECEIPT_FILE_CHECK_SCHEMA_ID),
        (
            "certification_bundle",
            args.certification_bundle_out,
            CERTIFICATION_BUNDLE_SCHEMA_ID,
        ),
        (
            "certification_bundle_check",
            args.certification_bundle_check_out,
            CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID,
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
            ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID,
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
            ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID,
        ),
    )
    return [
        (label, path, schema_id)
        for label, path, schema_id in artifacts
        if path is not None
    ]


def _artifact_gate_policy(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "allowed_statuses": list(args.require_status),
        "allowed_decision_verdicts": list(args.require_decision),
        "allowed_assurance_levels": list(args.require_assurance),
        "require_passed": args.require_passed,
    }


def _parse_normalized_param_pin(raw: str) -> tuple[str, Any]:
    if "=" not in raw:
        raise ValueError(
            "--require-normalized-param must be KEY=JSON_VALUE, for example "
            "head_dim=128"
        )
    key, raw_value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise ValueError("--require-normalized-param key must be non-empty")
    raw_value = raw_value.strip()
    if not raw_value:
        raise ValueError("--require-normalized-param value must be non-empty")
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        value = raw_value
    return key, value


def _load_artifact_pin_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = _load_json_object(path, label="artifact pin policy")
    if "pin_policy" in payload:
        policy = payload["pin_policy"]
        if not isinstance(policy, dict):
            raise ValueError(f"{path} pin_policy must be a JSON object")
        return policy
    return payload


def _policy_string_tuple(policy: dict[str, Any], key: str) -> tuple[str, ...]:
    values = policy.get(key, [])
    if not isinstance(values, list) or not all(
        isinstance(value, str) for value in values
    ):
        raise ValueError(f"pin policy {key} must be a list of strings")
    return tuple(values)


def _policy_normalized_params(
    policy: dict[str, Any],
) -> tuple[tuple[str, Any], ...]:
    values = policy.get("required_normalized_params", [])
    if not isinstance(values, list):
        raise ValueError(
            "pin policy required_normalized_params must be a list of objects"
        )
    pins: list[tuple[str, Any]] = []
    for item in values:
        if not isinstance(item, dict):
            raise ValueError(
                "pin policy required_normalized_params must be a list of objects"
            )
        key = item.get("key")
        if not isinstance(key, str) or not key:
            raise ValueError(
                "pin policy required_normalized_params entries need a string key"
            )
        if "value" not in item:
            raise ValueError(
                "pin policy required_normalized_params entries need a value"
            )
        pins.append((key, item["value"]))
    return tuple(pins)


def _merge_strings(*groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                merged.append(value)
    return tuple(merged)


def _value_marker(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    except TypeError:
        return repr(value)


def _merge_normalized_params(
    *groups: tuple[tuple[str, Any], ...],
) -> tuple[tuple[str, Any], ...]:
    merged: list[tuple[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for group in groups:
        for key, value in group:
            marker = (key, _value_marker(value))
            if marker not in seen:
                seen.add(marker)
                merged.append((key, value))
    return tuple(merged)


def _merge_artifact_pin_policy(
    args: argparse.Namespace,
    cli_normalized_params: tuple[tuple[str, Any], ...],
) -> None:
    policy = _load_artifact_pin_policy(args.pin_policy)
    args.require_kind = list(
        _merge_strings(
            _policy_string_tuple(policy, "required_kinds"),
            tuple(args.require_kind),
        )
    )
    args.require_theorem_id = list(
        _merge_strings(
            _policy_string_tuple(policy, "required_theorem_ids"),
            tuple(args.require_theorem_id),
        )
    )
    args.require_evidence_field = list(
        _merge_strings(
            _policy_string_tuple(policy, "required_evidence_fields"),
            tuple(args.require_evidence_field),
        )
    )
    args.require_recommendation_id = list(
        _merge_strings(
            _policy_string_tuple(policy, "required_recommendation_ids"),
            tuple(args.require_recommendation_id),
        )
    )
    args.require_validation_command = list(
        _merge_strings(
            _policy_string_tuple(policy, "required_validation_commands"),
            tuple(args.require_validation_command),
        )
    )
    args.require_model_config_fingerprint = list(
        _merge_strings(
            _policy_string_tuple(policy, "required_model_config_fingerprints"),
            tuple(args.require_model_config_fingerprint),
        )
    )
    args.require_architecture_config_fingerprint = list(
        _merge_strings(
            _policy_string_tuple(
                policy,
                "required_architecture_config_fingerprints",
            ),
            tuple(args.require_architecture_config_fingerprint),
        )
    )
    args.required_normalized_params = _merge_normalized_params(
        _policy_normalized_params(policy),
        cli_normalized_params,
    )


def _artifact_pin_policy(args: argparse.Namespace) -> dict[str, Any]:
    normalized_params = [
        {"key": key, "value": value}
        for key, value in getattr(args, "required_normalized_params", ())
    ]
    return {
        "required_kinds": list(args.require_kind),
        "required_theorem_ids": list(args.require_theorem_id),
        "required_evidence_fields": list(args.require_evidence_field),
        "required_recommendation_ids": list(args.require_recommendation_id),
        "required_validation_commands": list(args.require_validation_command),
        "required_model_config_fingerprints": list(
            args.require_model_config_fingerprint
        ),
        "required_architecture_config_fingerprints": list(
            args.require_architecture_config_fingerprint
        ),
        "required_normalized_params": normalized_params,
    }


def _has_artifact_pin_requirements(args: argparse.Namespace) -> bool:
    return any(
        (
            args.require_kind,
            args.require_theorem_id,
            args.require_evidence_field,
            args.require_recommendation_id,
            args.require_validation_command,
            args.require_model_config_fingerprint,
            args.require_architecture_config_fingerprint,
            getattr(args, "required_normalized_params", ()),
        )
    )


def _artifact_pin_failures(
    summaries: list[dict[str, Any]],
    args: argparse.Namespace,
) -> list[str]:
    failures: list[str] = []
    observed_kinds = {
        summary["kind"] for summary in summaries if isinstance(summary.get("kind"), str)
    }
    observed_theorem_ids = {
        theorem_id
        for summary in summaries
        for theorem_id in summary.get("theorem_ids", [])
        if isinstance(theorem_id, str)
    }
    observed_evidence_fields = {
        field
        for summary in summaries
        for field in summary.get("evidence_fields", [])
        if isinstance(field, str)
    }
    observed_recommendation_ids = {
        recommendation_id
        for summary in summaries
        for recommendation_id in summary.get("recommendation_ids", [])
        if isinstance(recommendation_id, str)
    }
    observed_validation_commands = {
        command
        for summary in summaries
        for command in summary.get("validation_commands", [])
        if isinstance(command, str)
    }
    observed_model_config_fingerprints = {
        fingerprint
        for summary in summaries
        for fingerprint in (summary.get("model_config_fingerprint"),)
        if isinstance(fingerprint, str)
    }
    observed_architecture_config_fingerprints = {
        fingerprint
        for summary in summaries
        for fingerprint in (summary.get("architecture_config_fingerprint"),)
        if isinstance(fingerprint, str)
    }

    for kind in args.require_kind:
        if kind not in observed_kinds:
            failures.append(f"required contract kind is missing: {kind}")
    for theorem_id in args.require_theorem_id:
        if theorem_id not in observed_theorem_ids:
            failures.append(f"required receipt theorem id is missing: {theorem_id}")
    for field in args.require_evidence_field:
        if field not in observed_evidence_fields:
            failures.append(f"required receipt evidence field is missing: {field}")
    for recommendation_id in args.require_recommendation_id:
        if recommendation_id not in observed_recommendation_ids:
            failures.append(
                f"required receipt recommendation id is missing: {recommendation_id}"
            )
    for command in args.require_validation_command:
        if command not in observed_validation_commands:
            failures.append(f"required receipt validation command is missing: {command}")
    for fingerprint in args.require_model_config_fingerprint:
        if fingerprint not in observed_model_config_fingerprints:
            failures.append(
                f"required model config fingerprint is missing: {fingerprint}"
            )
    for fingerprint in args.require_architecture_config_fingerprint:
        if fingerprint not in observed_architecture_config_fingerprints:
            failures.append(
                "required architecture config fingerprint is missing: "
                f"{fingerprint}"
            )
    for key, value in getattr(args, "required_normalized_params", ()):
        if not any(
            isinstance(summary.get("normalized_request"), dict)
            and summary["normalized_request"].get(key) == value
            for summary in summaries
        ):
            failures.append(
                f"required normalized request parameter is missing: {key}={value!r}"
            )
    return failures


def _apply_artifact_pin_policy(
    report: dict[str, Any],
    args: argparse.Namespace,
) -> list[str]:
    report["pin_policy"] = _artifact_pin_policy(args)
    summaries = report.get("summaries")
    pin_failures = _artifact_pin_failures(
        summaries if isinstance(summaries, list) else [],
        args,
    )
    if pin_failures:
        failures = report.setdefault("failures", [])
        failures.extend(pin_failures)
        report["failure_count"] = len(failures)
        report["ok"] = False
    return pin_failures


def _artifact_status_fields(
    *,
    receipt: dict[str, Any] | None,
    request_validation_report: dict[str, Any] | None,
) -> dict[str, Any]:
    if receipt is not None:
        decision = receipt.get("decision")
        decision_dict = decision if isinstance(decision, dict) else {}
        return {
            "kind": receipt.get("kind"),
            "status": receipt.get("status"),
            "request_passed": receipt.get("request_passed"),
            "decision_verdict": decision_dict.get("verdict"),
            "decision_assurance": decision_dict.get("assurance"),
            "request_content_fingerprint": receipt.get("request_content_fingerprint"),
            "normalized_request_fingerprint": receipt.get(
                "normalized_request_fingerprint"
            ),
            "receipt_content_fingerprint": receipt.get("receipt_content_fingerprint"),
        }
    if request_validation_report is not None:
        return {
            "kind": request_validation_report.get("canonical_kind"),
            "status": None,
            "request_passed": None,
            "decision_verdict": None,
            "decision_assurance": None,
            "request_content_fingerprint": request_validation_report.get(
                "request_content_fingerprint"
            ),
            "normalized_request_fingerprint": None,
            "receipt_content_fingerprint": None,
        }
    return {
        "kind": None,
        "status": None,
        "request_passed": None,
        "decision_verdict": None,
        "decision_assurance": None,
        "request_content_fingerprint": None,
        "normalized_request_fingerprint": None,
        "receipt_content_fingerprint": None,
    }


def _build_artifact_manifest(
    args: argparse.Namespace,
    *,
    receipt: dict[str, Any] | None,
    request_validation_report: dict[str, Any] | None,
) -> dict[str, Any]:
    artifacts = [
        {
            "label": label,
            "path": _display_path(path),
            "exists": path.exists(),
            "sha256": _file_sha256(path),
            "content_schema_id": schema_id,
        }
        for label, path, schema_id in _artifact_paths_for_manifest(args)
    ]
    status_fields = _artifact_status_fields(
        receipt=receipt,
        request_validation_report=request_validation_report,
    )
    return {
        "schema_id": ARTIFACT_MANIFEST_SCHEMA_ID,
        "artifact_fingerprint_algorithm": "sha256-file-v1",
        "artifact_prefix": _default_artifact_prefix(args),
        "artifact_dir": (
            None if args.artifact_dir is None else _display_path(args.artifact_dir)
        ),
        "gate_policy": _artifact_gate_policy(args),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        **status_fields,
    }


def _validate_artifact_manifest(manifest: dict[str, Any], schema_path: Path) -> None:
    schema = _load_json_object(schema_path, label="artifact manifest schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(manifest, schema)
    generated_schema = build_contract_artifact_manifest_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "artifact manifest schema drifted from application builder"
        )


def _validate_artifact_manifest_check_report(
    report: dict[str, Any],
    schema_path: Path,
) -> None:
    schema = _load_json_object(schema_path, label="artifact manifest check schema")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_contract_artifact_manifest_file_check_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "artifact manifest check schema drifted from application builder"
        )


def _write_artifact_manifest(
    args: argparse.Namespace,
    *,
    receipt: dict[str, Any] | None,
    request_validation_report: dict[str, Any] | None,
) -> list[str]:
    if args.artifact_manifest_out is None:
        return []
    manifest = _build_artifact_manifest(
        args,
        receipt=receipt,
        request_validation_report=request_validation_report,
    )
    _validate_artifact_manifest(manifest, args.artifact_manifest_schema)
    write_json(args.artifact_manifest_out, manifest)
    if args.artifact_manifest_check_out is not None:
        manifest_check_report = build_contract_artifact_manifest_file_check_report(
            manifest,
            manifest_path=args.artifact_manifest_out,
        )
        pin_failures = _apply_artifact_pin_policy(manifest_check_report, args)
        _validate_artifact_manifest_check_report(
            manifest_check_report,
            args.artifact_manifest_check_schema,
        )
        write_json(args.artifact_manifest_check_out, manifest_check_report)
        return pin_failures
    return []


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
        ("compact_receipt_json", args.compact_json_out),
        ("receipt_check", args.receipt_check_out),
        ("receipt_replay_check", args.receipt_replay_check_out),
        ("gate_report", args.gate_report_out),
        ("certification_bundle", args.certification_bundle_out),
        ("certification_bundle_check", args.certification_bundle_check_out),
        ("artifact_manifest", args.artifact_manifest_out),
        ("artifact_manifest_check", args.artifact_manifest_check_out),
    ]
    model_config_import_report_out = getattr(
        args,
        "model_config_import_report_out",
        None,
    )
    artifacts.insert(2, ("model_config_import_report", model_config_import_report_out))
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
        ),
    )
    written = [
        f"{label}={_display_path(path)}"
        for label, path in artifacts
        if path is not None
    ]
    if not written:
        return None
    return "artifacts=" + " ".join(written)


def _source_import_summary_line(
    args: argparse.Namespace,
    *,
    model_config_import_report: Mapping[str, Any] | None,
    architecture_config_import_report: Mapping[str, Any] | None,
) -> str | None:
    if model_config_import_report is not None:
        request = model_config_import_report.get("request")
        kind = request.get("kind") if isinstance(request, Mapping) else None
        return (
            "source_config=model_config "
            f"path={_display_path(args.model_config)} "
            "model_config_fingerprint="
            f"{model_config_import_report.get('model_config_fingerprint')} "
            f"kind={kind} "
            "request_fingerprint="
            f"{model_config_import_report.get('request_content_fingerprint')}"
        )
    if architecture_config_import_report is not None:
        request = architecture_config_import_report.get("request")
        kind = request.get("kind") if isinstance(request, Mapping) else None
        unsupported_fields = architecture_config_import_report.get(
            "unsupported_architecture_config_fields",
        )
        unsupported_field_names = (
            ",".join(
                str(field)
                for field in unsupported_fields
                if isinstance(field, str)
            )
            if isinstance(unsupported_fields, list)
            else ""
        )
        unsupported_field_count = (
            len(unsupported_fields) if isinstance(unsupported_fields, list) else 0
        )
        return (
            "source_config=architecture_config "
            f"path={_display_path(args.architecture_config)} "
            "architecture_config_fingerprint="
            f"{architecture_config_import_report.get('architecture_config_fingerprint')} "
            f"kind={kind} "
            f"unsupported_architecture_fields={unsupported_field_count} "
            f"unsupported_architecture_field_names={unsupported_field_names or '-'} "
            "request_fingerprint="
            f"{architecture_config_import_report.get('request_content_fingerprint')}"
        )
    return None


def main() -> int:
    args = parse_args()
    _apply_artifact_dir_defaults(args)
    try:
        cli_required_normalized_params = tuple(
            _parse_normalized_param_pin(raw)
            for raw in args.require_normalized_param
        )
        _merge_artifact_pin_policy(args, cli_required_normalized_params)
    except ValueError as exc:
        raise SystemExit(str(exc))
    if (
        _has_artifact_pin_requirements(args)
        and args.artifact_manifest_check_out is None
    ):
        raise SystemExit(
            "artifact dependency pin requirements need "
            "--artifact-manifest-check-out or --artifact-dir"
        )
    if (
        getattr(args, "model_config_import_report_out", None) is not None
        and getattr(args, "model_config", None) is None
    ):
        raise SystemExit("--model-config-import-report-out requires --model-config")
    if (
        getattr(args, "model_config", None) is not None
        and getattr(args, "architecture_config", None) is not None
    ):
        raise SystemExit("--model-config and --architecture-config cannot be combined")
    if (
        getattr(args, "architecture_config_import_report_out", None) is not None
        and getattr(args, "architecture_config", None) is None
    ):
        raise SystemExit(
            "--architecture-config-import-report-out requires --architecture-config"
        )
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
    if args.artifact_manifest_check_out is not None and args.artifact_manifest_out is None:
        raise SystemExit(
            "--artifact-manifest-check-out requires --artifact-manifest-out "
            "so the report points at a saved artifact manifest"
        )
    request_for_bundle: dict[str, Any] | None = None
    model_config_import_report_for_bundle: dict[str, Any] | None = None
    architecture_config_import_report_for_bundle: dict[str, Any] | None = None
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
                or args.compact_json_out
                or args.format == "compact-json"
            ):
                raise SystemExit(
                    "--require-status, --require-decision, --require-assurance, "
                    "--require-passed, --receipt-check-out, --gate-report-out, "
                    "--certification-bundle-out, and "
                    "--certification-bundle-check-out, --compact-json-out, and "
                    "--format compact-json require a receipt; omit --validate-only"
                )
            report = _validated_request_validation_report(
                request_object,
                args.request_validation_schema,
            )
            if args.request_validation_report_out is not None:
                write_json(args.request_validation_report_out, report)
            if args.json_out is not None:
                write_json(args.json_out, report)
            artifact_failures = _write_artifact_manifest(
                args,
                receipt=None,
                request_validation_report=report,
            )
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
                for failure in artifact_failures:
                    print(
                        f"artifact_manifest_check_failure={failure}",
                        file=sys.stderr,
                    )
            return 0 if report["ok"] and not artifact_failures else 1
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
                config = _load_json_object(
                    args.model_config,
                    label="model config JSON",
                    allow_config_dir=True,
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
            if (
                request is None
                and args.kind in {"rope", "kv-cache", "sparse-attention", "recurrence"}
                and getattr(args, "architecture_config", None) is not None
            ):
                config = _load_json_object(
                    args.architecture_config,
                    label="architecture config JSON",
                )
                import_report = build_architecture_config_import_report(
                    args.kind,
                    config,
                    overrides=_architecture_overrides_from_args(args),
                )
                architecture_config_import_report_for_bundle = import_report
                if args.architecture_config_import_report_out is not None:
                    _validate_architecture_config_import_report(
                        import_report,
                        args.architecture_config_import_schema,
                    )
                    write_json(
                        args.architecture_config_import_report_out,
                        import_report,
                    )
                if not import_report["ok"]:
                    raise ValueError("; ".join(import_report["failures"]))
                if not isinstance(import_report["request"], dict):
                    raise ValueError(
                        "architecture config import report did not emit a request"
                    )
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
    compact_receipt = None
    if args.format == "compact-json" or args.compact_json_out is not None:
        compact_receipt = build_compact_contract_receipt(receipt)
        _validate_compact_receipt_schema(
            compact_receipt,
            args.compact_receipt_schema,
        )
        if args.compact_json_out is not None:
            write_json(args.compact_json_out, compact_receipt)
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
    if args.receipt_replay_check_out is not None:
        replay_report = build_contract_receipt_replay_check_report(
            receipt,
            pack=pack,
            receipt_path=(
                _display_path(args.json_out)
                if args.json_out is not None
                else "<in-memory-receipt>"
            ),
        )
        _validate_receipt_replay_check_report(
            replay_report,
            args.receipt_replay_check_schema,
        )
        write_json(args.receipt_replay_check_out, replay_report)
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
            architecture_config_import_report=(
                architecture_config_import_report_for_bundle
            ),
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
    artifact_failures = _write_artifact_manifest(
        args,
        receipt=receipt,
        request_validation_report=None,
    )
    if args.format == "json":
        print(json.dumps(receipt, indent=2, sort_keys=True))
    elif args.format == "compact-json":
        assert compact_receipt is not None
        print(json.dumps(compact_receipt, indent=2, sort_keys=True))
    else:
        for line in receipt_summary_lines(receipt):
            print(line)
        source_line = _source_import_summary_line(
            args,
            model_config_import_report=model_config_import_report_for_bundle,
            architecture_config_import_report=architecture_config_import_report_for_bundle,
        )
        if source_line is not None:
            print(source_line)
        artifact_line = _artifact_summary_line(args)
        if artifact_line is not None:
            print(artifact_line)
    for failure in gate_failures:
        print(f"receipt_gate_failure={failure}", file=sys.stderr)
    for failure in artifact_failures:
        print(f"artifact_manifest_check_failure={failure}", file=sys.stderr)
    return 0 if not gate_failures and not artifact_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
