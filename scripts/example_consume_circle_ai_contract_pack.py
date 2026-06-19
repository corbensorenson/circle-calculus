#!/usr/bin/env python3
"""Example downstream consumer for the Circle AI contract pack.

This script is intentionally small and copyable. It uses only the public
consumer adapter, not Lean, manifests, dictionary YAML, Quarto, or private
Theseus-Hive state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from circle_math.applications.circle_ai_contract_consumer import (  # noqa: E402
    ContractAcceptanceError,
    ContractConsumerError,
    ContractFingerprintMismatchError,
    contract_acceptance_receipt,
    contract_digest,
    contract_fingerprint_summary,
    contract_kinds,
    load_contract_pack,
    planner_action_plan,
    readiness_report,
    readiness_summary,
    require_fingerprint_expectations,
)


def _parse_contract_fingerprint_expectations(
    values: list[str],
) -> tuple[dict[str, str], list[str]]:
    expectations: dict[str, str] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--expect-contract-fingerprint must have the form kind=sha256"
            )
            continue
        kind, fingerprint = raw.split("=", 1)
        kind = kind.strip()
        fingerprint = fingerprint.strip()
        if not kind:
            failures.append("--expect-contract-fingerprint kind is empty")
            continue
        if kind in expectations:
            failures.append(
                f"--expect-contract-fingerprint repeats contract kind: {kind}"
            )
            continue
        expectations[kind] = fingerprint
    return expectations, failures


def _parse_recommendation_evidence_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-evidence-field must have the form "
                "RECOMMENDATION_ID=field_name"
            )
            continue
        recommendation_id, field = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        field = field.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-evidence-field recommendation id is empty"
            )
            continue
        if not field:
            failures.append(
                "--require-recommendation-evidence-field field name is empty"
            )
            continue
        fields = requirements.setdefault(recommendation_id, [])
        if field in fields:
            failures.append(
                "--require-recommendation-evidence-field repeats "
                f"{recommendation_id}={field}"
            )
            continue
        fields.append(field)
    return {
        recommendation_id: tuple(fields)
        for recommendation_id, fields in requirements.items()
    }, failures


def _parse_recommendation_theorem_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-theorem must have the form "
                "RECOMMENDATION_ID=THEOREM_ID"
            )
            continue
        recommendation_id, theorem_id = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        theorem_id = theorem_id.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-theorem recommendation id is empty"
            )
            continue
        if not theorem_id:
            failures.append("--require-recommendation-theorem theorem id is empty")
            continue
        theorem_ids = requirements.setdefault(recommendation_id, [])
        if theorem_id in theorem_ids:
            failures.append(
                "--require-recommendation-theorem repeats "
                f"{recommendation_id}={theorem_id}"
            )
            continue
        theorem_ids.append(theorem_id)
    return {
        recommendation_id: tuple(theorem_ids)
        for recommendation_id, theorem_ids in requirements.items()
    }, failures


def _parse_recommendation_action_parameter_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-action-parameter must have the form "
                "RECOMMENDATION_ID=PARAMETER_KEY"
            )
            continue
        recommendation_id, parameter_key = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        parameter_key = parameter_key.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-action-parameter recommendation id is empty"
            )
            continue
        if not parameter_key:
            failures.append(
                "--require-recommendation-action-parameter parameter key is empty"
            )
            continue
        parameter_keys = requirements.setdefault(recommendation_id, [])
        if parameter_key in parameter_keys:
            failures.append(
                "--require-recommendation-action-parameter repeats "
                f"{recommendation_id}={parameter_key}"
            )
            continue
        parameter_keys.append(parameter_key)
    return {
        recommendation_id: tuple(parameter_keys)
        for recommendation_id, parameter_keys in requirements.items()
    }, failures


def _parse_recommendation_action_parameter_path_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-action-parameter-path must have the "
                "form RECOMMENDATION_ID=PARAMETER_PATH"
            )
            continue
        recommendation_id, parameter_path = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        parameter_path = parameter_path.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-action-parameter-path "
                "recommendation id is empty"
            )
            continue
        if not parameter_path:
            failures.append(
                "--require-recommendation-action-parameter-path path is empty"
            )
            continue
        parameter_paths = requirements.setdefault(recommendation_id, [])
        if parameter_path in parameter_paths:
            failures.append(
                "--require-recommendation-action-parameter-path repeats "
                f"{recommendation_id}={parameter_path}"
            )
            continue
        parameter_paths.append(parameter_path)
    return {
        recommendation_id: tuple(parameter_paths)
        for recommendation_id, parameter_paths in requirements.items()
    }, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack",
        default="site/data/generated/circle_ai_contract_pack.json",
        help="Path to a generated circle_calculus.ai_contract_pack.v0 JSON file.",
    )
    parser.add_argument(
        "--kind",
        default="rope_position_distinguishability",
        help="Contract kind to require and summarize.",
    )
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="Evidence field to include. Repeat to request multiple fields.",
    )
    parser.add_argument(
        "--list-kinds",
        action="store_true",
        help="Print available contract kinds from the pack and exit.",
    )
    parser.add_argument(
        "--planner",
        action="store_true",
        help=(
            "Emit a copy-safe theorem-linked action plan from planner "
            "recommendations instead of a single contract digest."
        ),
    )
    parser.add_argument(
        "--fingerprints",
        action="store_true",
        help="Print pack and per-contract content fingerprints and exit.",
    )
    parser.add_argument(
        "--readiness",
        action="store_true",
        help="Print the readiness summary for --kind and exit nonzero if unready.",
    )
    parser.add_argument(
        "--all-readiness",
        action="store_true",
        help="Print readiness summaries for every contract kind and exit nonzero if any are unready.",
    )
    parser.add_argument(
        "--receipt",
        action="store_true",
        help=(
            "Emit a strict CI-friendly acceptance receipt for --kind. This "
            "fails if any requested --field, --require-theorem, or "
            "--require-recommendation is missing."
        ),
    )
    parser.add_argument(
        "--planner-kind",
        action="append",
        default=[],
        help=(
            "Contract kind to include in --planner output. Repeat to include "
            "multiple kinds. Defaults to every ready contract kind."
        ),
    )
    parser.add_argument(
        "--planner-include-values",
        action="store_true",
        help=(
            "In --planner output, resolve evidence field names to contract "
            "field values and include recommendation-specific parameters."
        ),
    )
    parser.add_argument(
        "--planner-recommendation",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID",
        help=(
            "In --planner output, emit only this planner recommendation id. "
            "Repeat for multiple ids. Missing ids fail instead of being ignored."
        ),
    )
    parser.add_argument(
        "--include-field-metadata",
        action="store_true",
        help="Include field descriptions, JSON value kinds, and proof roles.",
    )
    parser.add_argument(
        "--include-recommendations",
        action="store_true",
        help="Include optional planner recommendation records.",
    )
    parser.add_argument(
        "--require-recommendation",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID",
        help=(
            "In --receipt mode, require a planner recommendation id to exist "
            "for --kind. Repeat for multiple recommendations."
        ),
    )
    parser.add_argument(
        "--require-theorem",
        action="append",
        default=[],
        metavar="THEOREM_ID",
        help=(
            "In --receipt mode, require a theorem id to appear in the selected "
            "contract theorem spine. Repeat for multiple theorems."
        ),
    )
    parser.add_argument(
        "--require-recommendation-evidence-field",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=FIELD",
        help=(
            "In --receipt mode, require a planner recommendation to cite a "
            "specific evidence field. Repeat for multiple fields. This also "
            "requires the recommendation id itself."
        ),
    )
    parser.add_argument(
        "--require-recommendation-theorem",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=THEOREM_ID",
        help=(
            "In --receipt mode, require a planner recommendation to cite a "
            "specific theorem id. Repeat for multiple theorem ids. This also "
            "requires the recommendation id itself."
        ),
    )
    parser.add_argument(
        "--require-recommendation-action-parameter",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=PARAMETER_KEY",
        help=(
            "In --receipt mode, require a planner recommendation to expose a "
            "specific value-mode action parameter key. Repeat for multiple "
            "keys. This also requires the recommendation id itself."
        ),
    )
    parser.add_argument(
        "--require-recommendation-action-parameter-path",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=PARAMETER_PATH",
        help=(
            "In --receipt mode, require a planner recommendation to expose a "
            "nested value-mode action parameter path, for example "
            "classifier_regions[region=proved].theorem_ids. Repeat for "
            "multiple paths. This also requires the recommendation id itself."
        ),
    )
    parser.add_argument(
        "--expect-pack-fingerprint",
        default=None,
        help=(
            "Require the exported pack fingerprint to match this lowercase "
            "sha256 string before emitting consumer output."
        ),
    )
    parser.add_argument(
        "--expect-contract-fingerprint",
        action="append",
        default=[],
        metavar="KIND=SHA256",
        help=(
            "Require one contract content fingerprint to match before emitting "
            "consumer output. Repeat for multiple contract kinds."
        ),
    )
    args = parser.parse_args()

    try:
        recommendation_evidence_requirements, evidence_parse_failures = (
            _parse_recommendation_evidence_requirements(
                args.require_recommendation_evidence_field,
            )
        )
        recommendation_theorem_requirements, theorem_parse_failures = (
            _parse_recommendation_theorem_requirements(
                args.require_recommendation_theorem,
            )
        )
        recommendation_action_parameter_requirements, action_parse_failures = (
            _parse_recommendation_action_parameter_requirements(
                args.require_recommendation_action_parameter,
            )
        )
        recommendation_action_parameter_path_requirements, path_parse_failures = (
            _parse_recommendation_action_parameter_path_requirements(
                args.require_recommendation_action_parameter_path,
            )
        )
        parse_failures = (
            evidence_parse_failures
            + theorem_parse_failures
            + action_parse_failures
            + path_parse_failures
        )
        if parse_failures:
            print(
                "Circle AI contract acceptance failed:",
                file=sys.stderr,
            )
            for failure in parse_failures:
                print(f"  - {failure}", file=sys.stderr)
            return 4
        if args.require_recommendation_evidence_field and not args.receipt:
            print(
                "Circle AI contract acceptance failed: "
                "--require-recommendation-evidence-field requires --receipt",
                file=sys.stderr,
            )
            return 4
        if args.require_recommendation_theorem and not args.receipt:
            print(
                "Circle AI contract acceptance failed: "
                "--require-recommendation-theorem requires --receipt",
                file=sys.stderr,
            )
            return 4
        if args.require_recommendation_action_parameter and not args.receipt:
            print(
                "Circle AI contract acceptance failed: "
                "--require-recommendation-action-parameter requires --receipt",
                file=sys.stderr,
            )
            return 4
        if args.require_recommendation_action_parameter_path and not args.receipt:
            print(
                "Circle AI contract acceptance failed: "
                "--require-recommendation-action-parameter-path requires --receipt",
                file=sys.stderr,
            )
            return 4
        if args.require_theorem and not args.receipt:
            print(
                "Circle AI contract acceptance failed: "
                "--require-theorem requires --receipt",
                file=sys.stderr,
            )
            return 4
        if args.planner_recommendation and not args.planner:
            print(
                "Circle AI contract pack consumer failed: "
                "--planner-recommendation requires --planner",
                file=sys.stderr,
            )
            return 1
        pack = load_contract_pack(args.pack)
        expected_contracts, parse_failures = (
            _parse_contract_fingerprint_expectations(
                args.expect_contract_fingerprint,
            )
        )
        if parse_failures:
            print(
                "Circle AI contract fingerprint expectation failed:",
                file=sys.stderr,
            )
            for failure in parse_failures:
                print(f"  - {failure}", file=sys.stderr)
            return 3
        try:
            require_fingerprint_expectations(
                pack,
                expected_pack_fingerprint=args.expect_pack_fingerprint,
                expected_contract_fingerprints=expected_contracts,
            )
        except ContractFingerprintMismatchError as exc:
            print(
                f"Circle AI contract fingerprint expectation failed: {exc}",
                file=sys.stderr,
            )
            return 3
        if args.list_kinds:
            print(json.dumps({"kinds": list(contract_kinds(pack))}, indent=2))
            return 0
        if args.fingerprints:
            print(json.dumps(contract_fingerprint_summary(pack), indent=2))
            return 0
        if args.all_readiness:
            report = readiness_report(pack)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["all_ready"] is True else 2
        if args.readiness:
            summary = readiness_summary(pack, args.kind)
            print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
            return 0 if summary.ready else 2
        if args.receipt:
            try:
                receipt = contract_acceptance_receipt(
                    pack,
                    args.kind,
                    required_fields=args.field or None,
                    required_theorem_ids=args.require_theorem or None,
                    required_recommendation_ids=(
                        args.require_recommendation or None
                    ),
                    required_recommendation_evidence_fields=(
                        recommendation_evidence_requirements or None
                    ),
                    required_recommendation_theorem_ids=(
                        recommendation_theorem_requirements or None
                    ),
                    required_recommendation_action_parameters=(
                        recommendation_action_parameter_requirements or None
                    ),
                    required_recommendation_action_parameter_paths=(
                        recommendation_action_parameter_path_requirements or None
                    ),
                    include_field_metadata=args.include_field_metadata,
                )
            except ContractAcceptanceError as exc:
                print(
                    f"Circle AI contract acceptance failed: {exc}",
                    file=sys.stderr,
                )
                return 4
            print(json.dumps(receipt, indent=2, sort_keys=True))
            return 0
        if args.planner:
            print(json.dumps(
                planner_action_plan(
                    pack,
                    args.planner_kind or None,
                    include_values=args.planner_include_values,
                    recommendation_ids=args.planner_recommendation or None,
                ),
                indent=2,
            ))
            return 0
        digest = contract_digest(
            pack,
            args.kind,
            fields=args.field or None,
            include_field_metadata=args.include_field_metadata,
            include_recommendations=args.include_recommendations,
        )
    except (ContractConsumerError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Circle AI contract pack consumer failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(digest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
