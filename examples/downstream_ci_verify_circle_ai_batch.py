#!/usr/bin/env python3
"""Standalone downstream CI gate for Circle AI batch runner artifacts.

This example intentionally uses only the Python standard library. A downstream
project can copy it next to a ``circle-ai-certify batch --artifact-dir`` output
and fail CI when the runner-check report or one of its sidecars is missing,
schema-mismatched, stale, or outside the consumer's accepted proof-status
policy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPORT_SCHEMA_ID = "circle_calculus.ai_contract_runner_check.v0"
EXAMPLE_SCHEMA_ID = "circle_calculus.downstream_ci_batch_artifact_acceptance.v0"
FAILURE_SCHEMA_ID = "circle_calculus.downstream_ci_batch_artifact_rejection.v0"
SUPPORTED_STATUSES = {
    "proved",
    "impossible",
    "undecided",
    "numerical_only",
    "outside_scope",
}
SUPPORTED_DECISIONS = {
    "passed",
    "failed",
    "undecided",
    "numerical_only",
    "outside_scope",
}
SUPPORTED_ASSURANCES = {
    "theorem_backed",
    "mixed_theorem_and_computation",
    "numerical_only",
    "unsupported",
    "undecided",
}
EXPECTED_SCHEMA_BY_SUMMARY_PATH = {
    "receipt_path": "circle_calculus.ai_contract_receipt.v0",
    "compact_receipt_path": "circle_calculus.ai_contract_compact_receipt.v0",
    "model_config_import_report_path": "circle_calculus.rope_model_config_import.v0",
    "architecture_config_import_report_path": (
        "circle_calculus.ai_architecture_config_import.v0"
    ),
    "request_validation_report_path": (
        "circle_calculus.ai_contract_request_validation.v0"
    ),
    "certification_bundle_path": (
        "circle_calculus.ai_contract_certification_bundle.v0"
    ),
    "certification_bundle_check_path": (
        "circle_calculus.ai_contract_certification_bundle_file_check.v0"
    ),
}


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _short(value: object) -> str | None:
    return value[:12] if isinstance(value, str) else None


def _resolve_candidates(
    raw_path: str,
    *,
    report_path: Path,
    base_dir: Path | None,
) -> list[Path]:
    path = Path(raw_path)
    candidates = [path]
    if not path.is_absolute():
        candidates.extend([Path.cwd() / path, report_path.parent / path])
        if base_dir is not None:
            candidates.append(base_dir / path)
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def _resolve_existing_artifact(
    raw_path: str,
    *,
    report_path: Path,
    base_dir: Path | None,
) -> Path | None:
    for candidate in _resolve_candidates(
        raw_path,
        report_path=report_path,
        base_dir=base_dir,
    ):
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _load_artifact(
    raw_path: object,
    *,
    report_path: Path,
    base_dir: Path | None,
    label: str,
    required: bool,
) -> tuple[Path | None, dict[str, Any] | None, list[str]]:
    if raw_path is None:
        if required:
            return None, None, [f"{label} is required but missing from summary"]
        return None, None, []
    if not isinstance(raw_path, str) or not raw_path:
        return None, None, [f"{label} must be a non-empty string or null"]
    resolved = _resolve_existing_artifact(
        raw_path,
        report_path=report_path,
        base_dir=base_dir,
    )
    if resolved is None:
        return None, None, [f"{label} artifact is missing: {raw_path}"]
    try:
        payload = _load_json_object(resolved)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return resolved, None, [f"{label} artifact is unreadable: {exc}"]
    expected_schema = EXPECTED_SCHEMA_BY_SUMMARY_PATH[label]
    if payload.get("schema_id") != expected_schema:
        return resolved, payload, [f"{label} schema_id is unexpected"]
    return resolved, payload, []


def _check_policy_values(
    *,
    statuses: list[str],
    decisions: list[str],
    assurances: list[str],
) -> None:
    unknown_statuses = sorted(set(statuses) - SUPPORTED_STATUSES)
    unknown_decisions = sorted(set(decisions) - SUPPORTED_DECISIONS)
    unknown_assurances = sorted(set(assurances) - SUPPORTED_ASSURANCES)
    if unknown_statuses:
        raise ValueError(f"unsupported required statuses: {unknown_statuses}")
    if unknown_decisions:
        raise ValueError(f"unsupported required decisions: {unknown_decisions}")
    if unknown_assurances:
        raise ValueError(f"unsupported required assurances: {unknown_assurances}")


def _receipt_consistency_failures(
    summary: dict[str, Any],
    receipt: dict[str, Any] | None,
) -> list[str]:
    if receipt is None:
        return []
    decision = receipt.get("decision")
    decision_obj = decision if isinstance(decision, dict) else {}
    comparisons = (
        ("kind", summary.get("kind"), receipt.get("kind")),
        ("status", summary.get("status"), receipt.get("status")),
        ("request_passed", summary.get("request_passed"), receipt.get("request_passed")),
        ("decision_verdict", summary.get("decision_verdict"), decision_obj.get("verdict")),
        (
            "decision_assurance",
            summary.get("decision_assurance"),
            decision_obj.get("assurance"),
        ),
        (
            "request_content_fingerprint",
            summary.get("request_content_fingerprint"),
            receipt.get("request_content_fingerprint"),
        ),
        (
            "normalized_request_fingerprint",
            summary.get("normalized_request_fingerprint"),
            receipt.get("normalized_request_fingerprint"),
        ),
        (
            "receipt_content_fingerprint",
            summary.get("receipt_content_fingerprint"),
            receipt.get("receipt_content_fingerprint"),
        ),
    )
    failures: list[str] = []
    for field, summary_value, receipt_value in comparisons:
        if summary_value != receipt_value:
            failures.append(
                f"summary {field} does not match receipt: "
                f"{summary_value!r} != {receipt_value!r}"
            )
    return failures


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _policy_string_list(
    policy: dict[str, Any],
    field: str,
    *,
    supported: set[str],
) -> tuple[list[str], list[str]]:
    value = policy.get(field)
    if not isinstance(value, list):
        return [], [f"runner gate_policy {field} must be a list"]
    items: list[str] = []
    failures: list[str] = []
    for item in value:
        if not isinstance(item, str):
            failures.append(f"runner gate_policy {field} entries must be strings")
            continue
        items.append(item)
    unsupported = sorted(set(items) - supported)
    if unsupported:
        failures.append(
            f"runner gate_policy {field} has unsupported values: {unsupported}"
        )
    return items, failures


def _runner_gate_policy(report: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    raw_policy = report.get("gate_policy")
    if not isinstance(raw_policy, dict):
        return {}, ["runner-check gate_policy must be an object"]
    failures: list[str] = []
    statuses, status_failures = _policy_string_list(
        raw_policy,
        "allowed_statuses",
        supported=SUPPORTED_STATUSES,
    )
    decisions, decision_failures = _policy_string_list(
        raw_policy,
        "allowed_decision_verdicts",
        supported=SUPPORTED_DECISIONS,
    )
    assurances, assurance_failures = _policy_string_list(
        raw_policy,
        "allowed_assurance_levels",
        supported=SUPPORTED_ASSURANCES,
    )
    failures.extend(status_failures)
    failures.extend(decision_failures)
    failures.extend(assurance_failures)
    require_passed = raw_policy.get("require_passed")
    if not isinstance(require_passed, bool):
        failures.append("runner gate_policy require_passed must be a boolean")
        require_passed = False
    require_no_unsupported = raw_policy.get(
        "require_no_unsupported_architecture_fields"
    )
    if not isinstance(require_no_unsupported, bool):
        failures.append(
            "runner gate_policy require_no_unsupported_architecture_fields "
            "must be a boolean"
        )
        require_no_unsupported = False
    return {
        "allowed_statuses": statuses,
        "allowed_decision_verdicts": decisions,
        "allowed_assurance_levels": assurances,
        "require_passed": require_passed,
        "require_no_unsupported_architecture_fields": require_no_unsupported,
    }, failures


def _load_pin_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = _load_json_object(path)
    if "pin_policy" in payload:
        policy = payload["pin_policy"]
        if not isinstance(policy, dict):
            raise ValueError(f"{path} pin_policy must be a JSON object")
        return policy
    return payload


def _policy_required_string_list(
    policy: dict[str, Any],
    key: str,
    *,
    supported: set[str] | None = None,
) -> list[str]:
    values = policy.get(key, [])
    if not isinstance(values, list) or not all(
        isinstance(value, str) for value in values
    ):
        raise ValueError(f"pin policy {key} must be a list of strings")
    if supported is not None:
        unsupported = sorted(set(values) - supported)
        if unsupported:
            raise ValueError(f"pin policy {key} has unsupported values: {unsupported}")
    return list(values)


def _policy_bool(policy: dict[str, Any], key: str) -> bool | None:
    if key not in policy:
        return None
    value = policy[key]
    if not isinstance(value, bool):
        raise ValueError(f"pin policy {key} must be a boolean")
    return value


def _merge_strings(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                merged.append(value)
    return merged


def _expected_runner_gate_policy(
    policy: dict[str, Any],
) -> dict[str, Any] | None:
    if "expected_runner_gate_policy" not in policy:
        return None
    raw_policy = policy["expected_runner_gate_policy"]
    if not isinstance(raw_policy, dict):
        raise ValueError("pin policy expected_runner_gate_policy must be an object")
    normalized, failures = _runner_gate_policy({"gate_policy": raw_policy})
    if failures:
        raise ValueError(
            "pin policy expected_runner_gate_policy is invalid: "
            + "; ".join(failures)
        )
    return normalized


def _merge_pin_policy_args(args: argparse.Namespace) -> dict[str, Any] | None:
    policy = _load_pin_policy(args.pin_policy)
    args.require_kind = _merge_strings(
        _policy_required_string_list(policy, "required_kinds"),
        args.require_kind,
    )
    args.require_status = _merge_strings(
        _policy_required_string_list(
            policy,
            "required_statuses",
            supported=SUPPORTED_STATUSES,
        ),
        args.require_status,
    )
    args.require_decision = _merge_strings(
        _policy_required_string_list(
            policy,
            "required_decisions",
            supported=SUPPORTED_DECISIONS,
        ),
        args.require_decision,
    )
    args.require_assurance = _merge_strings(
        _policy_required_string_list(
            policy,
            "required_assurances",
            supported=SUPPORTED_ASSURANCES,
        ),
        args.require_assurance,
    )
    if _policy_bool(policy, "require_passed") is True:
        args.require_passed = True
    if _policy_bool(policy, "require_receipts") is True:
        args.allow_missing_receipts = False
    if _policy_bool(policy, "require_compact_receipts") is True:
        args.allow_missing_compact_receipts = False
    if _policy_bool(policy, "require_request_validation") is True:
        args.allow_missing_request_validation = False
    if _policy_bool(policy, "require_bundles") is True:
        args.allow_missing_bundles = False
    if _policy_bool(policy, "require_no_unsupported_architecture_fields") is True:
        args.require_no_unsupported_architecture_fields = True
    return _expected_runner_gate_policy(policy)


def _pin_policy(
    *,
    required_kinds: list[str],
    required_statuses: list[str],
    required_decisions: list[str],
    required_assurances: list[str],
    require_passed: bool,
    require_receipts: bool,
    require_compact_receipts: bool,
    require_request_validation: bool,
    require_bundles: bool,
    require_no_unsupported_architecture_fields: bool,
    expected_runner_gate_policy: dict[str, Any],
) -> dict[str, Any]:
    return {
        "required_kinds": required_kinds,
        "required_statuses": required_statuses,
        "required_decisions": required_decisions,
        "required_assurances": required_assurances,
        "require_passed": require_passed,
        "require_receipts": require_receipts,
        "require_compact_receipts": require_compact_receipts,
        "require_request_validation": require_request_validation,
        "require_bundles": require_bundles,
        "require_no_unsupported_architecture_fields": (
            require_no_unsupported_architecture_fields
        ),
        "expected_runner_gate_policy": expected_runner_gate_policy,
    }


def _sidecar_consistency_failures(
    summary: dict[str, Any],
    *,
    receipt: dict[str, Any] | None,
    compact_receipt: dict[str, Any] | None,
    request_validation: dict[str, Any] | None,
    certification_bundle: dict[str, Any] | None,
    certification_bundle_check: dict[str, Any] | None,
    model_config_import: dict[str, Any] | None,
    architecture_config_import: dict[str, Any] | None,
) -> list[str]:
    failures: list[str] = []
    receipt_fingerprint = summary.get("receipt_content_fingerprint")
    request_fingerprint = summary.get("request_content_fingerprint")

    if compact_receipt is not None:
        fingerprints = compact_receipt.get("fingerprints")
        compact_fingerprint = (
            fingerprints.get("receipt_content_fingerprint")
            if isinstance(fingerprints, dict)
            else None
        )
        if compact_fingerprint != receipt_fingerprint:
            failures.append("compact receipt fingerprint does not match summary")
    if request_validation is not None:
        if request_validation.get("ok") is not True:
            failures.append("request validation report ok was not true")
        if request_validation.get("failure_count") != 0:
            failures.append("request validation failure_count was not zero")
        if request_validation.get("request_content_fingerprint") != request_fingerprint:
            failures.append(
                "request validation request_content_fingerprint does not match summary"
            )
    if certification_bundle is not None:
        if certification_bundle.get("ok") is not True:
            failures.append("certification bundle ok was not true")
        bundled_receipt = certification_bundle.get("receipt")
        if isinstance(bundled_receipt, dict):
            bundled_fingerprint = bundled_receipt.get("receipt_content_fingerprint")
            if bundled_fingerprint != receipt_fingerprint:
                failures.append("certification bundle receipt fingerprint mismatch")
        elif receipt is not None:
            failures.append("certification bundle receipt was not an object")
        if model_config_import is not None and certification_bundle.get(
            "model_config_import_report"
        ) != model_config_import:
            failures.append(
                "certification bundle model-config import report does not match sidecar"
            )
        if architecture_config_import is not None and certification_bundle.get(
            "architecture_config_import_report"
        ) != architecture_config_import:
            failures.append(
                "certification bundle architecture-config import report does not "
                "match sidecar"
            )
    if certification_bundle_check is not None:
        if certification_bundle_check.get("ok") is not True:
            failures.append("certification bundle check ok was not true")
        if certification_bundle_check.get("failure_count") != 0:
            failures.append("certification bundle check failure_count was not zero")
    return failures


def _verify_summary(
    summary: dict[str, Any],
    *,
    report_path: Path,
    base_dir: Path | None,
    require_receipts: bool,
    require_compact_receipts: bool,
    require_request_validation: bool,
    require_bundles: bool,
) -> dict[str, Any]:
    failures: list[str] = []
    loaded: dict[str, dict[str, Any] | None] = {}
    resolved_paths: dict[str, str | None] = {}
    for label in EXPECTED_SCHEMA_BY_SUMMARY_PATH:
        required = (
            label == "receipt_path"
            and require_receipts
            or label == "compact_receipt_path"
            and require_compact_receipts
            or label == "request_validation_report_path"
            and require_request_validation
            or label
            in {
                "certification_bundle_path",
                "certification_bundle_check_path",
            }
            and require_bundles
        )
        resolved, payload, path_failures = _load_artifact(
            summary.get(label),
            report_path=report_path,
            base_dir=base_dir,
            label=label,
            required=required,
        )
        resolved_paths[label] = None if resolved is None else str(resolved)
        loaded[label] = payload
        failures.extend(path_failures)

    receipt = loaded["receipt_path"]
    failures.extend(_receipt_consistency_failures(summary, receipt))
    failures.extend(
        _sidecar_consistency_failures(
            summary,
            receipt=receipt,
            compact_receipt=loaded["compact_receipt_path"],
            request_validation=loaded["request_validation_report_path"],
            certification_bundle=loaded["certification_bundle_path"],
            certification_bundle_check=loaded["certification_bundle_check_path"],
            model_config_import=loaded["model_config_import_report_path"],
            architecture_config_import=loaded["architecture_config_import_report_path"],
        )
    )
    unsupported_architecture_fields = _string_list(
        summary.get("unsupported_architecture_config_fields")
    )

    return {
        "source_type": summary.get("source_type"),
        "source_path": summary.get("source_path"),
        "kind": summary.get("kind"),
        "status": summary.get("status"),
        "request_passed": summary.get("request_passed"),
        "decision_verdict": summary.get("decision_verdict"),
        "decision_assurance": summary.get("decision_assurance"),
        "receipt_content_fingerprint": summary.get("receipt_content_fingerprint"),
        "receipt_content_fingerprint_short": _short(
            summary.get("receipt_content_fingerprint")
        ),
        "unsupported_architecture_config_field_count": len(
            unsupported_architecture_fields
        ),
        "unsupported_architecture_config_fields": unsupported_architecture_fields,
        "resolved_paths": resolved_paths,
        "failure_count": len(failures),
        "failures": failures,
    }


def verify_runner_check(
    path: Path,
    *,
    base_dir: Path | None,
    required_kinds: list[str],
    required_statuses: list[str],
    required_decisions: list[str],
    required_assurances: list[str],
    require_passed: bool,
    require_receipts: bool,
    require_compact_receipts: bool,
    require_request_validation: bool,
    require_bundles: bool,
    require_no_unsupported_architecture_fields: bool,
    expected_runner_gate_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    _check_policy_values(
        statuses=required_statuses,
        decisions=required_decisions,
        assurances=required_assurances,
    )
    report = _load_json_object(path)
    failures: list[str] = []
    if report.get("schema_id") != REPORT_SCHEMA_ID:
        failures.append("runner-check schema_id is unexpected")
    if report.get("ok") is not True:
        failures.append("runner-check report ok was not true")
    if report.get("failure_count") != 0:
        failures.append("runner-check failure_count was not zero")
    runner_gate_policy, runner_gate_policy_failures = _runner_gate_policy(report)
    failures.extend(runner_gate_policy_failures)
    if (
        expected_runner_gate_policy is not None
        and runner_gate_policy != expected_runner_gate_policy
    ):
        failures.append(
            "runner-check gate_policy does not match pinned "
            "expected_runner_gate_policy"
        )

    raw_summaries = report.get("summaries")
    summaries: list[dict[str, Any]] = []
    if not isinstance(raw_summaries, list):
        failures.append("runner-check summaries must be a list")
        raw_summaries = []
    for index, summary in enumerate(raw_summaries, start=1):
        if not isinstance(summary, dict):
            failures.append(f"summary {index} is not an object")
            continue
        summaries.append(
            _verify_summary(
                summary,
                report_path=path,
                base_dir=base_dir,
                require_receipts=require_receipts,
                require_compact_receipts=require_compact_receipts,
                require_request_validation=require_request_validation,
                require_bundles=require_bundles,
            )
        )

    failures.extend(
        f"{summary['source_path']}:{summary['kind']}: {failure}"
        for summary in summaries
        for failure in summary["failures"]
    )
    observed_kinds = [
        summary["kind"] for summary in summaries if isinstance(summary.get("kind"), str)
    ]
    kind_counts = {
        kind: observed_kinds.count(kind) for kind in sorted(set(observed_kinds))
    }
    if report.get("example_count") != len(summaries):
        failures.append(
            "runner-check example_count does not match summaries length: "
            f"{report.get('example_count')!r} != {len(summaries)!r}"
        )
    raw_selected_kinds = report.get("selected_kinds")
    selected_kinds: list[str] = []
    if not isinstance(raw_selected_kinds, list):
        failures.append("runner-check selected_kinds must be a list")
    else:
        for item in raw_selected_kinds:
            if isinstance(item, str):
                selected_kinds.append(item)
            else:
                failures.append("runner-check selected_kinds entries must be strings")
    if sorted(set(selected_kinds)) != sorted(set(observed_kinds)):
        failures.append(
            "runner-check selected_kinds does not match observed summary kinds: "
            f"{sorted(set(selected_kinds))!r} != {sorted(set(observed_kinds))!r}"
        )
    for kind in required_kinds:
        if kind not in kind_counts:
            failures.append(f"required contract kind is missing: {kind}")
    for summary in summaries:
        if (
            runner_gate_policy.get("allowed_statuses")
            and summary["status"] not in runner_gate_policy["allowed_statuses"]
        ):
            failures.append(
                f"{summary['kind']} status {summary['status']!r} violates "
                "runner gate_policy allowed_statuses"
            )
        if (
            runner_gate_policy.get("allowed_decision_verdicts")
            and summary["decision_verdict"]
            not in runner_gate_policy["allowed_decision_verdicts"]
        ):
            failures.append(
                f"{summary['kind']} decision {summary['decision_verdict']!r} "
                "violates runner gate_policy allowed_decision_verdicts"
            )
        if (
            runner_gate_policy.get("allowed_assurance_levels")
            and summary["decision_assurance"]
            not in runner_gate_policy["allowed_assurance_levels"]
        ):
            failures.append(
                f"{summary['kind']} assurance {summary['decision_assurance']!r} "
                "violates runner gate_policy allowed_assurance_levels"
            )
        if (
            runner_gate_policy.get("require_passed") is True
            and summary["request_passed"] is not True
        ):
            failures.append(
                f"{summary['kind']} request_passed violated runner gate_policy"
            )
        if (
            runner_gate_policy.get("require_no_unsupported_architecture_fields")
            is True
            and summary["unsupported_architecture_config_fields"]
        ):
            failures.append(
                f"{summary['source_path']}:{summary['kind']} has unsupported "
                "architecture-config fields despite runner gate_policy: "
                + ", ".join(summary["unsupported_architecture_config_fields"])
            )
        if required_statuses and summary["status"] not in set(required_statuses):
            failures.append(
                f"{summary['kind']} status {summary['status']!r} not in "
                f"{required_statuses!r}"
            )
        if required_decisions and summary["decision_verdict"] not in set(
            required_decisions
        ):
            failures.append(
                f"{summary['kind']} decision {summary['decision_verdict']!r} "
                f"not in {required_decisions!r}"
            )
        if required_assurances and summary["decision_assurance"] not in set(
            required_assurances
        ):
            failures.append(
                f"{summary['kind']} assurance {summary['decision_assurance']!r} "
                f"not in {required_assurances!r}"
            )
        if require_passed and summary["request_passed"] is not True:
            failures.append(f"{summary['kind']} request_passed was not true")
        unsupported_architecture_fields = summary[
            "unsupported_architecture_config_fields"
        ]
        if (
            require_no_unsupported_architecture_fields
            and unsupported_architecture_fields
        ):
            failures.append(
                f"{summary['source_path']}:{summary['kind']} has unsupported "
                "architecture-config fields: "
                f"{', '.join(unsupported_architecture_fields)}"
            )

    return {
        "schema_id": EXAMPLE_SCHEMA_ID,
        "accepted": not failures,
        "runner_check_path": str(path),
        "source_count": len(summaries),
        "failure_count": len(failures),
        "failures": failures,
        "required_kinds": required_kinds,
        "runner_selected_kinds": selected_kinds,
        "observed_kinds": sorted(set(observed_kinds)),
        "kind_counts": kind_counts,
        "required_statuses": required_statuses,
        "required_decisions": required_decisions,
        "required_assurances": required_assurances,
        "runner_gate_policy": runner_gate_policy,
        "expected_runner_gate_policy": expected_runner_gate_policy,
        "require_passed": require_passed,
        "require_receipts": require_receipts,
        "require_compact_receipts": require_compact_receipts,
        "require_request_validation": require_request_validation,
        "require_bundles": require_bundles,
        "require_no_unsupported_architecture_fields": (
            require_no_unsupported_architecture_fields
        ),
        "pin_policy": _pin_policy(
            required_kinds=required_kinds,
            required_statuses=required_statuses,
            required_decisions=required_decisions,
            required_assurances=required_assurances,
            require_passed=require_passed,
            require_receipts=require_receipts,
            require_compact_receipts=require_compact_receipts,
            require_request_validation=require_request_validation,
            require_bundles=require_bundles,
            require_no_unsupported_architecture_fields=(
                require_no_unsupported_architecture_fields
            ),
            expected_runner_gate_policy=runner_gate_policy,
        ),
        "summaries": summaries,
        "not_claimed": (
            "This is a downstream batch artifact-integrity gate. It is not a "
            "mathematical proof, Lean verification run, model-quality result, "
            "deployment-safety claim, or ASI claim."
        ),
    }


def _failure_report(exc: BaseException, path: Path) -> dict[str, Any]:
    message = str(exc)
    return {
        "schema_id": FAILURE_SCHEMA_ID,
        "example_schema_id": EXAMPLE_SCHEMA_ID,
        "accepted": False,
        "error": message,
        "failure_count": 1,
        "failures": [message],
        "runner_check_path": str(path),
        "not_claimed": (
            "This is a machine-readable rejection report for a batch artifact "
            "integrity gate. It is not a mathematical proof, model-quality "
            "result, deployment-safety claim, or ASI claim."
        ),
    }


def _print_text(report: dict[str, Any]) -> None:
    print(
        "circle AI downstream batch verification "
        f"accepted={report['accepted']} sources={report['source_count']} "
        f"failures={report['failure_count']}"
    )
    for summary in report["summaries"]:
        print(
            "batch_summary "
            f"source={summary['source_path']} kind={summary['kind']} "
            f"status={summary['status']} passed={summary['request_passed']} "
            f"decision={summary['decision_verdict']} "
            f"assurance={summary['decision_assurance']} "
            "unsupported_architecture_fields="
            f"{summary['unsupported_architecture_config_field_count']} "
            f"failures={summary['failure_count']}"
        )
        for failure in summary["failures"]:
            print(
                f"failure={summary['source_path']}:{summary['kind']}: {failure}",
                file=sys.stderr,
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Standalone downstream CI verifier for Circle AI batch "
            "runner-check artifacts."
        ),
    )
    parser.add_argument("runner_check", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument(
        "--base-dir",
        type=Path,
        help="Optional base directory for resolving relative artifact paths.",
    )
    parser.add_argument(
        "--require-kind",
        action="append",
        default=[],
        help="Require at least one batch summary for this contract kind.",
    )
    parser.add_argument(
        "--require-status",
        action="append",
        default=[],
        help="Require every batch summary status to match this value.",
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        default=[],
        help="Require every batch summary decision_verdict to match this value.",
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        default=[],
        help="Require every batch summary decision_assurance to match this value.",
    )
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Fail unless every batch summary has request_passed=true.",
    )
    parser.add_argument(
        "--allow-missing-receipts",
        action="store_true",
        help="Do not require receipt_path sidecars to be present.",
    )
    parser.add_argument(
        "--allow-missing-compact-receipts",
        action="store_true",
        help="Do not require compact_receipt_path sidecars to be present.",
    )
    parser.add_argument(
        "--allow-missing-request-validation",
        action="store_true",
        help="Do not require request_validation_report_path sidecars to be present.",
    )
    parser.add_argument(
        "--allow-missing-bundles",
        action="store_true",
        help=(
            "Do not require certification_bundle_path and "
            "certification_bundle_check_path sidecars to be present."
        ),
    )
    parser.add_argument(
        "--require-no-unsupported-architecture-fields",
        action="store_true",
        help=(
            "Fail if any architecture-config batch summary reports fields that "
            "were present in the source config but unsupported by the emitted "
            "theorem-linked request."
        ),
    )
    parser.add_argument(
        "--pin-policy",
        type=Path,
        help=(
            "Merge requirements from a previous JSON report's pin_policy block "
            "or from a standalone pin-policy object, including the expected "
            "runner gate_policy."
        ),
    )
    args = parser.parse_args()

    try:
        expected_runner_gate_policy = _merge_pin_policy_args(args)
        report = verify_runner_check(
            args.runner_check,
            base_dir=args.base_dir,
            required_kinds=args.require_kind,
            required_statuses=args.require_status,
            required_decisions=args.require_decision,
            required_assurances=args.require_assurance,
            require_passed=args.require_passed,
            require_receipts=not args.allow_missing_receipts,
            require_compact_receipts=not args.allow_missing_compact_receipts,
            require_request_validation=not args.allow_missing_request_validation,
            require_bundles=not args.allow_missing_bundles,
            require_no_unsupported_architecture_fields=(
                args.require_no_unsupported_architecture_fields
            ),
            expected_runner_gate_policy=expected_runner_gate_policy,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        failure = _failure_report(exc, args.runner_check)
        if args.format == "json":
            print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        else:
            print(
                f"circle AI downstream batch verification failed: {exc}",
                file=sys.stderr,
            )
        return 4

    if args.format == "json":
        output = sys.stdout if report["accepted"] else sys.stderr
        print(json.dumps(report, indent=2, sort_keys=True), file=output)
    else:
        _print_text(report)
    return 0 if report["accepted"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
