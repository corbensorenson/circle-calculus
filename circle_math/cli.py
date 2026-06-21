"""Small package-native command-line entry points.

The repository keeps richer maintenance CLIs under ``scripts/``. The functions
here are intentionally narrow public commands that work from the installed
Python package.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .ai_contracts import (
    CONTRACT_PACK_SCHEMA_ID,
    SUPPORTED_CONTRACT_KINDS,
    build_contract_pack,
    build_rope_model_config_import_report,
    build_validated_contract_receipt,
    build_validated_contract_receipt_from_request,
    build_validated_rope_receipt_from_model_config,
    canonical_contract_kind,
    receipt_summary_lines,
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
) -> dict[str, Any]:
    if inline_json is not None and json_file is not None:
        parser.error(f"use either --{label} or --{label}-file, not both")
    if json_file is not None:
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
            "Path to a model config JSON object. Currently supported for "
            "standard RoPE receipts only."
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
    if args.format == "json":
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        for line in receipt_summary_lines(receipt):
            print(line)
    return 0


__all__ = [
    "contract_ready_main",
    "contract_receipt_main",
    "rope_certify_main",
    "sparse_attention_certify_main",
]


if __name__ == "__main__":
    raise SystemExit(contract_ready_main())
