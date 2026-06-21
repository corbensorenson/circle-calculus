from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_RUNNER_REQUEST_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_request.schema.json"
)
DEFAULT_RUNNER_REQUEST_VALIDATION_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_request_validation.schema.json"
)
DEFAULT_RUNNER_RECEIPT_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_receipt.schema.json"
)
DEFAULT_RUNNER_CHECK_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_runner_check.schema.json"
)
DEFAULT_RECEIPT_FILE_CHECK_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_receipt_file_check.schema.json"
)
DEFAULT_CERTIFICATION_BUNDLE_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_certification_bundle.schema.json"
)
DEFAULT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_certification_bundle_file_check.schema.json"
)
DEFAULT_ARTIFACT_MANIFEST_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_artifact_manifest.schema.json"
)
DEFAULT_ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_artifact_manifest_file_check.schema.json"
)
EXPECTED_SCHEMA_ID = "circle_calculus.ai_contract_pack.v0"
EXPECTED_ACCEPTANCE_POLICY_SCHEMA_ID = "circle_calculus.ai_contract_acceptance_policy.v0"
EXPECTED_ACCEPTANCE_POLICY_REPORT_SCHEMA_ID = (
    "circle_calculus.ai_contract_acceptance_policy_report.v0"
)
EXPECTED_ACCEPTANCE_RECEIPT_SCHEMA_ID = (
    "circle_calculus.ai_contract_acceptance_receipt.v0"
)
EXPECTED_DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID = (
    "circle_calculus.downstream_ci_rejection_report.v0"
)
EXPECTED_FINGERPRINT_ALGORITHM = "sha256-json-v1"
FINGERPRINT_KEYS = {
    "content_fingerprint",
    "pack_content_fingerprint",
    "contract_fingerprint_index",
}
PROVED_STATUSES = {"lean_proved", "proved"}
MAKE_TARGET_RE = re.compile(r"^([A-Za-z0-9_.-]+):(?:\s|$)")
EXPECTED_LIVING_BOOK_PAGE_BY_KIND = {
    "rope_position_distinguishability": "site/chapters/applications/rope_certifier.qmd",
    "kv_cache_ring_buffer": "site/chapters/applications/kv_cache_ring_buffer.qmd",
    "sparse_attention_coverage": "site/chapters/applications/sparse_attention_contract.qmd",
    "recurrence_schedule": "site/chapters/applications/looped_recurrence_contracts.qmd",
    "strided_candidate_fanout": "site/chapters/applications/strided_candidate_fanout.qmd",
    "cyclic_memory_residue_winding": (
        "site/chapters/applications/cyclic_memory_residue_winding.qmd"
    ),
    "multicoil_phase_feature": "site/chapters/applications/multicoil_phase_feature.qmd",
    "circulant_block_cyclic_mixer": (
        "site/chapters/applications/circulant_block_cyclic_mixer.qmd"
    ),
    "seed_rule_exact_regeneration": "site/chapters/applications/generative.qmd",
}


def _walk_ids(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        identifier = value.get("id")
        if isinstance(identifier, str):
            found.add(identifier)
        for child in value.values():
            found.update(_walk_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_walk_ids(child))
    return found


def _yaml_ids(root: Path) -> set[str]:
    ids: set[str] = set()
    for path in sorted(root.glob("**/*.yaml")):
        ids.update(_walk_ids(yaml.safe_load(path.read_text()) or {}))
    return ids


def _walk_manifest_entries(value: object) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            entries.append(value)
        for child in value.values():
            entries.extend(_walk_manifest_entries(child))
    elif isinstance(value, list):
        for child in value:
            entries.extend(_walk_manifest_entries(child))
    return entries


def _yaml_entry_index(root: Path) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("**/*.yaml")):
        for entry in _walk_manifest_entries(yaml.safe_load(path.read_text()) or {}):
            entry_id = entry.get("id")
            if isinstance(entry_id, str) and entry_id not in entries:
                entries[entry_id] = entry
    return entries


def _path_exists(ref: str) -> bool:
    return (ROOT / ref).exists()


def _contract_fields_by_kind(pack: dict[str, Any]) -> dict[str, set[str]]:
    fields_by_kind: dict[str, set[str]] = {}
    contracts = pack.get("contracts")
    if not isinstance(contracts, list):
        return fields_by_kind
    for contract in contracts:
        if not isinstance(contract, dict):
            continue
        kind = contract.get("kind")
        fields = contract.get("fields")
        if isinstance(kind, str) and isinstance(fields, dict):
            fields_by_kind[kind] = set(fields)
    return fields_by_kind


def _strip_fingerprint_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_fingerprint_fields(child)
            for key, child in sorted(value.items())
            if key not in FINGERPRINT_KEYS
        }
    if isinstance(value, list):
        return [_strip_fingerprint_fields(child) for child in value]
    return value


def _json_fingerprint(value: Any) -> str:
    normalized = json.dumps(
        _strip_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _make_targets() -> set[str]:
    makefile = ROOT / "Makefile"
    if not makefile.exists():
        return set()
    targets: set[str] = set()
    for line in makefile.read_text(encoding="utf-8").splitlines():
        match = MAKE_TARGET_RE.match(line)
        if match:
            targets.add(match.group(1))
    return targets


def _check_entrypoint(command: str, failures: list[str]) -> None:
    if command.startswith("python "):
        parts = command.split()
        if len(parts) < 2:
            failures.append(f"entrypoint is incomplete: {command}")
            return
        script = parts[1]
        if not _path_exists(script):
            failures.append(f"entrypoint script is missing: {command}")


def _check_command_reference(
    command: object,
    failures: list[str],
    *,
    context: str,
    make_targets: set[str],
    fields_by_kind: dict[str, set[str]] | None = None,
) -> None:
    if not isinstance(command, str) or not command.strip():
        failures.append(f"{context}: validation command must be a non-empty string")
        return
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        failures.append(f"{context}: validation command is not shell-parseable: {exc}")
        return
    if not parts:
        failures.append(f"{context}: validation command is empty")
        return
    if parts[0] == "python":
        if len(parts) < 2:
            failures.append(f"{context}: python validation command is incomplete: {command}")
            return
        if parts[1] == "-m":
            if len(parts) >= 3 and parts[2] == "pytest":
                for arg in parts[3:]:
                    if arg.startswith("-"):
                        continue
                    ref = arg.split("::", 1)[0]
                    if ref and not _path_exists(ref):
                        failures.append(
                            f"{context}: pytest validation path is missing: {ref}"
                        )
            return
        script = parts[1]
        if not _path_exists(script):
            failures.append(f"{context}: validation script is missing: {script}")
        if fields_by_kind is not None:
            _check_contract_ready_command_semantics(
                parts,
                failures,
                context=context,
                fields_by_kind=fields_by_kind,
            )
        return
    if parts[0] == "make":
        targets = [
            part
            for part in parts[1:]
            if not part.startswith("-") and "=" not in part
        ]
        if not targets:
            return
        for target in targets:
            if target not in make_targets:
                failures.append(f"{context}: make target is missing: {target}")
        return
    failures.append(f"{context}: validation command must start with python or make: {command}")


def _split_command(command: object) -> list[str]:
    if not isinstance(command, str):
        return []
    try:
        return shlex.split(command)
    except ValueError:
        return []


def _is_contract_ready_kind_command(command: object, kind: str) -> bool:
    parts = _split_command(command)
    if len(parts) < 2:
        return False
    if parts[0] != "python" or parts[1] != "scripts/circle_ai_contract_ready.py":
        return False
    kinds, _ = _option_values(parts, "--kind")
    return kind in kinds


def _is_pytest_command(command: object) -> bool:
    parts = _split_command(command)
    return len(parts) >= 3 and parts[0] == "python" and parts[1] == "-m" and parts[2] == "pytest"


def _option_values(parts: list[str], option: str) -> tuple[list[str], list[int]]:
    values: list[str] = []
    missing_indexes: list[int] = []
    for index, part in enumerate(parts):
        if part != option:
            continue
        if index + 1 >= len(parts) or parts[index + 1].startswith("--"):
            missing_indexes.append(index)
            continue
        values.append(parts[index + 1])
    return values, missing_indexes


def _check_contract_ready_command_semantics(
    parts: list[str],
    failures: list[str],
    *,
    context: str,
    fields_by_kind: dict[str, set[str]],
) -> None:
    if len(parts) < 2 or parts[1] != "scripts/circle_ai_contract_ready.py":
        return
    kind_values: list[str] = []
    for option in ("--kind", "--planner-kind"):
        values, missing_indexes = _option_values(parts, option)
        for _ in missing_indexes:
            failures.append(f"{context}: {option} is missing a contract kind")
        kind_values.extend(values)
    for kind in kind_values:
        if kind not in fields_by_kind:
            failures.append(f"{context}: unknown contract kind in command: {kind}")

    field_values, missing_field_indexes = _option_values(parts, "--field")
    for _ in missing_field_indexes:
        failures.append(f"{context}: --field is missing a field name")
    if not field_values:
        return
    unique_kinds = sorted(set(kind_values))
    if len(unique_kinds) != 1:
        failures.append(
            f"{context}: --field validation requires exactly one --kind value"
        )
        return
    kind = unique_kinds[0]
    known_fields = fields_by_kind.get(kind, set())
    for field in field_values:
        if field not in known_fields:
            failures.append(
                f"{context}: unknown field for {kind} in command: {field}"
            )


def _json_value_kind(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if value is None:
        return "null"
    return type(value).__name__


def validate_pack(pack: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    make_targets = _make_targets()
    fields_by_kind = _contract_fields_by_kind(pack)
    if pack.get("schema_id") != EXPECTED_SCHEMA_ID:
        failures.append(f"expected schema_id {EXPECTED_SCHEMA_ID!r}")
    if pack.get("content_fingerprint_algorithm") != EXPECTED_FINGERPRINT_ALGORITHM:
        failures.append(
            "content_fingerprint_algorithm must be "
            f"{EXPECTED_FINGERPRINT_ALGORITHM!r}"
        )
    pack_fingerprint = pack.get("pack_content_fingerprint")
    if not isinstance(pack_fingerprint, str) or not re.fullmatch(
        r"[0-9a-f]{64}",
        pack_fingerprint,
    ):
        failures.append("pack_content_fingerprint must be a lowercase sha256 hex string")
    elif pack_fingerprint != _json_fingerprint(pack):
        failures.append("pack_content_fingerprint drifted from pack content")

    schema = pack.get("contract_schema")
    if not isinstance(schema, dict):
        failures.append("missing contract_schema")
        return failures

    required_keys = schema.get("required_contract_keys")
    minimum_fields_by_kind = schema.get("minimum_fields_by_kind")
    minimum_field_catalog_by_kind = schema.get("minimum_field_catalog_by_kind")
    consumer_check_keys = schema.get("consumer_check_keys")
    planner_recommendation_keys = schema.get("planner_recommendation_keys")
    if not isinstance(required_keys, list) or not required_keys:
        failures.append("contract_schema.required_contract_keys must be a non-empty list")
    if not isinstance(minimum_fields_by_kind, dict) or not minimum_fields_by_kind:
        failures.append("contract_schema.minimum_fields_by_kind must be a non-empty object")
    if (
        not isinstance(minimum_field_catalog_by_kind, dict)
        or not minimum_field_catalog_by_kind
    ):
        failures.append(
            "contract_schema.minimum_field_catalog_by_kind must be a non-empty object"
        )
    if not isinstance(consumer_check_keys, list) or not consumer_check_keys:
        failures.append("contract_schema.consumer_check_keys must be a non-empty list")
        consumer_check_keys = []
    if (
        not isinstance(planner_recommendation_keys, list)
        or not planner_recommendation_keys
    ):
        failures.append(
            "contract_schema.planner_recommendation_keys must be a non-empty list"
        )
        planner_recommendation_keys = []

    if isinstance(minimum_fields_by_kind, dict) and isinstance(
        minimum_field_catalog_by_kind,
        dict,
    ):
        if set(minimum_field_catalog_by_kind) != set(minimum_fields_by_kind):
            failures.append(
                "contract_schema.minimum_field_catalog_by_kind kinds drifted from "
                "minimum_fields_by_kind"
            )
        for kind, minimum_fields in minimum_fields_by_kind.items():
            if not isinstance(minimum_fields, list) or not minimum_fields:
                failures.append(
                    f"contract_schema.minimum_fields_by_kind.{kind} must be a "
                    "non-empty list"
                )
                continue
            catalog = minimum_field_catalog_by_kind.get(kind)
            if not isinstance(catalog, dict):
                failures.append(
                    f"contract_schema.minimum_field_catalog_by_kind.{kind} must be "
                    "an object"
                )
                continue
            missing_catalog_fields = [
                field for field in minimum_fields if field not in catalog
            ]
            extra_catalog_fields = sorted(set(catalog) - set(minimum_fields))
            if missing_catalog_fields:
                failures.append(
                    f"contract_schema.minimum_field_catalog_by_kind.{kind} missing "
                    f"fields {missing_catalog_fields}"
                )
            if extra_catalog_fields:
                failures.append(
                    f"contract_schema.minimum_field_catalog_by_kind.{kind} has "
                    f"unknown fields {extra_catalog_fields}"
                )
            for field in minimum_fields:
                entry = catalog.get(field)
                if not isinstance(entry, dict):
                    failures.append(
                        f"contract_schema.minimum_field_catalog_by_kind.{kind}."
                        f"{field} must be an object"
                    )
                    continue
                for entry_key in ("description", "value_kind", "proof_role"):
                    value = entry.get(entry_key)
                    if not isinstance(value, str) or not value.strip():
                        failures.append(
                            "contract_schema.minimum_field_catalog_by_kind."
                            f"{kind}.{field}.{entry_key} must be a non-empty string"
                        )

    proof_indexes = pack.get("proof_indexes", {})
    if not isinstance(proof_indexes, dict) or not proof_indexes:
        failures.append("proof_indexes must be a non-empty object")
    else:
        for key in ("theorem_index", "dictionary_index"):
            ref = proof_indexes.get(key)
            if not isinstance(ref, str) or not _path_exists(ref):
                failures.append(f"proof_indexes.{key} is missing: {ref}")

    acceptance_policy = pack.get("acceptance_policy")
    if not isinstance(acceptance_policy, dict) or not acceptance_policy:
        failures.append("acceptance_policy must be a non-empty object")
        acceptance_policy = {}
    else:
        if acceptance_policy.get("schema_id") != EXPECTED_ACCEPTANCE_POLICY_SCHEMA_ID:
            failures.append(
                "acceptance_policy.schema_id must be "
                f"{EXPECTED_ACCEPTANCE_POLICY_SCHEMA_ID!r}"
            )
        if (
            acceptance_policy.get("report_schema_id")
            != EXPECTED_ACCEPTANCE_POLICY_REPORT_SCHEMA_ID
        ):
            failures.append(
                "acceptance_policy.report_schema_id must be "
                f"{EXPECTED_ACCEPTANCE_POLICY_REPORT_SCHEMA_ID!r}"
            )
        if (
            acceptance_policy.get("receipt_schema_id")
            != EXPECTED_ACCEPTANCE_RECEIPT_SCHEMA_ID
        ):
            failures.append(
                "acceptance_policy.receipt_schema_id must be "
                f"{EXPECTED_ACCEPTANCE_RECEIPT_SCHEMA_ID!r}"
            )
        if (
            acceptance_policy.get("rejection_report_schema_id")
            != EXPECTED_DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID
        ):
            failures.append(
                "acceptance_policy.rejection_report_schema_id must be "
                f"{EXPECTED_DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID!r}"
            )
        for key in (
            "policy_schema_path",
            "report_schema_path",
            "receipt_schema_path",
            "rejection_report_schema_path",
            "default_policy_path",
            "checker",
            "standalone_checker",
            "standalone_schema_checker",
        ):
            ref = acceptance_policy.get(key)
            if not isinstance(ref, str) or not ref.strip():
                failures.append(f"acceptance_policy.{key} must be a non-empty path")
            elif not _path_exists(ref):
                failures.append(f"acceptance_policy.{key} is missing: {ref}")
        pinned_keys = acceptance_policy.get("pinned_requirement_keys")
        required_pinned_keys = {
            "required_fields",
            "required_theorem_ids",
            "required_recommendation_ids",
            "required_recommendation_evidence_fields",
            "required_recommendation_theorem_ids",
            "required_recommendation_action_parameters",
            "required_recommendation_action_parameter_paths",
            "expected_pack_fingerprint",
            "expected_contract_fingerprint",
        }
        if not isinstance(pinned_keys, list) or not pinned_keys:
            failures.append(
                "acceptance_policy.pinned_requirement_keys must be a non-empty list"
            )
        elif not required_pinned_keys <= set(pinned_keys):
            failures.append(
                "acceptance_policy.pinned_requirement_keys missing required keys "
                f"{sorted(required_pinned_keys - set(pinned_keys))}"
            )
        rule = acceptance_policy.get("rule")
        if not isinstance(rule, str) or "preserve" not in rule.lower():
            failures.append("acceptance_policy.rule must state preservation behavior")
        policy_commands = acceptance_policy.get("validation_commands")
        if not isinstance(policy_commands, list) or not policy_commands:
            failures.append(
                "acceptance_policy.validation_commands must be a non-empty list"
            )
            policy_commands = []
        for command in policy_commands:
            _check_command_reference(
                command,
                failures,
                context="acceptance_policy.validation_commands",
                make_targets=make_targets,
                fields_by_kind=fields_by_kind,
            )
        refresh_command = acceptance_policy.get("fingerprint_refresh_command")
        _check_command_reference(
            refresh_command,
            failures,
            context="acceptance_policy.fingerprint_refresh_command",
            make_targets=make_targets,
            fields_by_kind=fields_by_kind,
        )
        policy_schema_path = acceptance_policy.get("policy_schema_path")
        report_schema_path = acceptance_policy.get("report_schema_path")
        receipt_schema_path = acceptance_policy.get("receipt_schema_path")
        rejection_report_schema_path = acceptance_policy.get(
            "rejection_report_schema_path"
        )
        default_policy_path = acceptance_policy.get("default_policy_path")
        if isinstance(policy_schema_path, str) and isinstance(default_policy_path, str):
            try:
                policy_schema = json.loads((ROOT / policy_schema_path).read_text())
                default_policy = json.loads((ROOT / default_policy_path).read_text())
                jsonschema.Draft202012Validator.check_schema(policy_schema)
                jsonschema.validate(default_policy, policy_schema)
            except jsonschema.ValidationError as exc:
                failures.append(
                    "acceptance_policy.default_policy_path does not match "
                    f"policy_schema_path: {exc.message}"
                )
            except jsonschema.SchemaError as exc:
                failures.append(
                    f"acceptance_policy.policy_schema_path is invalid: {exc.message}"
                )
            except (OSError, json.JSONDecodeError) as exc:
                failures.append(
                    "acceptance_policy policy schema validation failed: "
                    f"{exc}"
                )
        if (
            isinstance(report_schema_path, str)
            and isinstance(receipt_schema_path, str)
            and isinstance(default_policy_path, str)
        ):
            try:
                from circle_math.applications.circle_ai_contract_consumer import (
                    contract_acceptance_policy_report,
                )

                report_schema = json.loads((ROOT / report_schema_path).read_text())
                receipt_schema = json.loads((ROOT / receipt_schema_path).read_text())
                default_policy = json.loads((ROOT / default_policy_path).read_text())
                report = contract_acceptance_policy_report(pack, default_policy)
                jsonschema.Draft202012Validator.check_schema(report_schema)
                jsonschema.Draft202012Validator.check_schema(receipt_schema)
                jsonschema.validate(report, report_schema)
                for receipt in report.get("receipts", []):
                    jsonschema.validate(receipt, receipt_schema)
            except jsonschema.ValidationError as exc:
                failures.append(
                    "acceptance_policy report or receipt does not match "
                    f"generated schema: {exc.message}"
                )
            except jsonschema.SchemaError as exc:
                failures.append(
                    "acceptance_policy report or receipt schema is invalid: "
                    f"{exc.message}"
                )
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                failures.append(
                    "acceptance_policy report or receipt schema validation "
                    f"failed: {exc}"
                )
        if isinstance(rejection_report_schema_path, str):
            try:
                rejection_report_schema = json.loads(
                    (ROOT / rejection_report_schema_path).read_text()
                )
                jsonschema.Draft202012Validator.check_schema(
                    rejection_report_schema
                )
                if rejection_report_schema.get("properties", {}).get(
                    "schema_id", {}
                ).get("const") != EXPECTED_DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID:
                    failures.append(
                        "acceptance_policy.rejection_report_schema_path has "
                        "unexpected schema_id const"
                    )
            except jsonschema.SchemaError as exc:
                failures.append(
                    "acceptance_policy rejection report schema is invalid: "
                    f"{exc.message}"
                )
            except (OSError, json.JSONDecodeError) as exc:
                failures.append(
                    "acceptance_policy rejection report schema validation "
                    f"failed: {exc}"
                )

    manifest_entries = _yaml_entry_index(ROOT / "manifests")
    manifest_ids = set(manifest_entries)
    known_dictionary_ids = _yaml_ids(ROOT / "dictionary")

    for source_doc in pack.get("source_docs", []):
        if not _path_exists(source_doc):
            failures.append(f"source_doc is missing: {source_doc}")

    validation_commands = pack.get("validation_commands", [])
    if not isinstance(validation_commands, list) or not validation_commands:
        failures.append("validation_commands must be a non-empty list")
        validation_commands = []
    for command in validation_commands:
        _check_command_reference(
            command,
            failures,
            context="pack.validation_commands",
            make_targets=make_targets,
            fields_by_kind=fields_by_kind,
        )
    for command in acceptance_policy.get("validation_commands", []):
        if command not in validation_commands:
            failures.append(
                "pack.validation_commands must include acceptance policy command: "
                f"{command}"
            )

    contracts = pack.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        failures.append("contracts must be a non-empty list")
        return failures

    readiness_index = pack.get("contract_readiness_index")
    if not isinstance(readiness_index, dict) or not readiness_index:
        failures.append("contract_readiness_index must be a non-empty object")
        readiness_index = {}
    recommendation_index = pack.get("planner_recommendation_index")
    if not isinstance(recommendation_index, dict) or not recommendation_index:
        failures.append("planner_recommendation_index must be a non-empty object")
        recommendation_index = {}
    fingerprint_index = pack.get("contract_fingerprint_index")
    if not isinstance(fingerprint_index, dict) or not fingerprint_index:
        failures.append("contract_fingerprint_index must be a non-empty object")
        fingerprint_index = {}

    expected_recommendation_index: dict[str, dict[str, Any]] = {}
    seen_recommendation_ids: dict[str, str] = {}
    expected_fingerprint_index: dict[str, dict[str, str]] = {}
    for contract in contracts:
        if not isinstance(contract, dict):
            failures.append("contract entry must be an object")
            continue
        contract_id = contract.get("id", "<missing id>")
        kind = contract.get("kind")
        for key in required_keys:
            if key not in contract:
                failures.append(f"{contract_id}: missing required key {key}")
        if (
            contract.get("content_fingerprint_algorithm")
            != EXPECTED_FINGERPRINT_ALGORITHM
        ):
            failures.append(
                f"{contract_id}: content_fingerprint_algorithm must be "
                f"{EXPECTED_FINGERPRINT_ALGORITHM!r}"
            )
        content_fingerprint = contract.get("content_fingerprint")
        if not isinstance(content_fingerprint, str) or not re.fullmatch(
            r"[0-9a-f]{64}",
            content_fingerprint,
        ):
            failures.append(
                f"{contract_id}: content_fingerprint must be a lowercase sha256 "
                "hex string"
            )
        elif content_fingerprint != _json_fingerprint(contract):
            failures.append(f"{contract_id}: content_fingerprint drifted")

        if not isinstance(kind, str) or kind not in minimum_fields_by_kind:
            failures.append(f"{contract_id}: unknown or missing kind {kind!r}")
            continue
        if isinstance(content_fingerprint, str):
            expected_fingerprint_index[kind] = {
                "id": str(contract_id),
                "content_fingerprint_algorithm": EXPECTED_FINGERPRINT_ALGORITHM,
                "content_fingerprint": content_fingerprint,
            }

        fields = contract.get("fields")
        if not isinstance(fields, dict):
            failures.append(f"{contract_id}: fields must be an object")
            continue

        minimum_fields = minimum_fields_by_kind[kind]
        missing_fields = [field for field in minimum_fields if field not in fields]
        if missing_fields:
            failures.append(f"{contract_id}: missing minimum fields {missing_fields}")
        if isinstance(minimum_field_catalog_by_kind, dict):
            catalog = minimum_field_catalog_by_kind.get(kind, {})
            if isinstance(catalog, dict):
                for field in minimum_fields:
                    entry = catalog.get(field)
                    if isinstance(entry, dict) and field in fields:
                        expected_kind = _json_value_kind(fields[field])
                        if entry.get("value_kind") != expected_kind:
                            failures.append(
                                f"{contract_id}: catalog value_kind for {field} "
                                f"drifted from field value"
                            )

        consumer_check = contract.get("consumer_check")
        if not isinstance(consumer_check, dict):
            failures.append(f"{contract_id}: missing consumer_check")
        else:
            for key in consumer_check_keys:
                if key not in consumer_check:
                    failures.append(f"{contract_id}: consumer_check missing {key}")
            if consumer_check.get("minimum_fields") != minimum_fields:
                failures.append(f"{contract_id}: consumer_check minimum_fields drifted")
            if consumer_check.get("missing_minimum_fields") != missing_fields:
                failures.append(f"{contract_id}: consumer_check missing field list drifted")
            if consumer_check.get("required_fields_present") != (not missing_fields):
                failures.append(f"{contract_id}: required_fields_present drifted")
            proof_status = contract.get("proof_status")
            all_resolved = (
                isinstance(proof_status, dict)
                and proof_status.get("all_theorem_ids_resolved") is True
            )
            all_proved = (
                isinstance(proof_status, dict)
                and proof_status.get("all_theorem_ids_proved") is True
            )
            if consumer_check.get("all_theorem_ids_resolved") != all_resolved:
                failures.append(f"{contract_id}: consumer_check resolved flag drifted")
            if consumer_check.get("all_theorem_ids_proved") != all_proved:
                failures.append(f"{contract_id}: consumer_check proved flag drifted")
            if consumer_check.get("unresolved_theorem_ids") != (
                proof_status.get("unresolved_theorem_ids", [])
                if isinstance(proof_status, dict)
                else []
            ):
                failures.append(f"{contract_id}: consumer_check unresolved list drifted")
            if consumer_check.get("unproved_theorem_ids") != (
                proof_status.get("unproved_theorem_ids", [])
                if isinstance(proof_status, dict)
                else []
            ):
                failures.append(f"{contract_id}: consumer_check unproved list drifted")
            expected_ready = (
                bool(contract.get("contract_passed"))
                and not missing_fields
                and all_resolved
                and all_proved
            )
            if consumer_check.get("ready_for_downstream_fixture_use") != expected_ready:
                failures.append(f"{contract_id}: ready_for_downstream_fixture_use drifted")

        theorem_ids = contract.get("theorem_ids", [])
        unknown_theorems = sorted(set(theorem_ids) - manifest_ids)
        if unknown_theorems:
            failures.append(f"{contract_id}: unknown theorem ids {unknown_theorems}")

        planner_recommendations = contract.get("planner_recommendations", [])
        if planner_recommendations is not None and not isinstance(
            planner_recommendations,
            list,
        ):
            failures.append(f"{contract_id}: planner_recommendations must be a list")
            planner_recommendations = []
        for index, recommendation in enumerate(planner_recommendations):
            if not isinstance(recommendation, dict):
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] must be an object"
                )
                continue
            for key in planner_recommendation_keys:
                if key not in recommendation:
                    failures.append(
                        f"{contract_id}: planner_recommendations[{index}] missing {key}"
                    )
            evidence_fields = recommendation.get("evidence_fields", [])
            if not isinstance(evidence_fields, list):
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}]."
                    "evidence_fields must be a list"
                )
                evidence_fields = []
            unknown_evidence_fields = [
                field for field in evidence_fields if field not in fields
            ]
            if unknown_evidence_fields:
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] unknown "
                    f"evidence fields {unknown_evidence_fields}"
                )
            recommendation_theorem_ids = recommendation.get("theorem_ids", [])
            if not isinstance(recommendation_theorem_ids, list):
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}]."
                    "theorem_ids must be a list"
                )
                recommendation_theorem_ids = []
            unknown_recommendation_theorems = sorted(
                set(recommendation_theorem_ids) - set(theorem_ids)
            )
            if unknown_recommendation_theorems:
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] unknown "
                    f"theorem ids {unknown_recommendation_theorems}"
                )
            if "not" not in str(recommendation.get("not_claimed", "")).lower():
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] "
                    "not_claimed boundary is missing or weak"
                )
            recommendation_id = recommendation.get("id")
            if not isinstance(recommendation_id, str) or not recommendation_id:
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}].id "
                    "must be a non-empty string"
                )
            else:
                previous_contract_id = seen_recommendation_ids.get(
                    recommendation_id
                )
                if previous_contract_id is not None:
                    failures.append(
                        f"{contract_id}: duplicate planner recommendation id "
                        f"{recommendation_id} already used by "
                        f"{previous_contract_id}"
                    )
                else:
                    seen_recommendation_ids[recommendation_id] = contract_id
                expected_recommendation_index[recommendation_id] = {
                    "id": recommendation_id,
                    "kind": kind,
                    "contract_id": contract_id,
                    "ready_for_downstream_fixture_use": (
                        isinstance(consumer_check, dict)
                        and consumer_check.get("ready_for_downstream_fixture_use")
                        is True
                    ),
                    "action_kind": recommendation.get("action_kind"),
                    "status": recommendation.get("status"),
                    "coverage_scope": recommendation.get("coverage_scope"),
                    "evidence_fields": list(evidence_fields),
                    "theorem_ids": list(recommendation_theorem_ids),
                    "quickstart_docs": list(contract.get("quickstart_docs", [])),
                    "living_book_pages": list(contract.get("living_book_pages", [])),
                    "validation_commands": list(
                        contract.get("validation_commands", []),
                    ),
                    "source_paper": contract.get("source_paper"),
                    "not_claimed": recommendation.get("not_claimed"),
                }

        proof_status = contract.get("proof_status")
        if not isinstance(proof_status, dict):
            failures.append(f"{contract_id}: missing proof_status")
        else:
            proof_records = proof_status.get("theorems")
            if not isinstance(proof_records, list):
                failures.append(f"{contract_id}: proof_status.theorems must be a list")
                proof_records = []
            if proof_status.get("theorem_count") != len(theorem_ids):
                failures.append(f"{contract_id}: proof_status theorem_count drifted")
            if proof_status.get("all_theorem_ids_resolved") != (not unknown_theorems):
                failures.append(f"{contract_id}: proof_status resolved flag drifted")
            unproved_ids = sorted(
                theorem_id
                for theorem_id in theorem_ids
                if theorem_id in manifest_entries
                and str(manifest_entries[theorem_id].get("status", "")).strip()
                not in PROVED_STATUSES
            )
            expected_all_proved = not unknown_theorems and not unproved_ids
            if proof_status.get("all_theorem_ids_proved") != expected_all_proved:
                failures.append(f"{contract_id}: proof_status proved flag drifted")
            if sorted(proof_status.get("unresolved_theorem_ids", [])) != unknown_theorems:
                failures.append(f"{contract_id}: proof_status unresolved list drifted")
            if sorted(proof_status.get("unproved_theorem_ids", [])) != unproved_ids:
                failures.append(f"{contract_id}: proof_status unproved list drifted")
            records_by_id = {
                record.get("id"): record
                for record in proof_records
                if isinstance(record, dict) and isinstance(record.get("id"), str)
            }
            if set(records_by_id) != set(theorem_ids):
                failures.append(f"{contract_id}: proof_status theorem records do not match theorem_ids")
            for theorem_id in theorem_ids:
                record = records_by_id.get(theorem_id)
                entry = manifest_entries.get(theorem_id)
                if record is None or entry is None:
                    continue
                manifest_status = str(entry.get("status", "")).strip()
                if record.get("status") != manifest_status:
                    failures.append(f"{contract_id}: {theorem_id} proof_status status drifted")
                if record.get("lean_name") != entry.get("lean_name"):
                    failures.append(f"{contract_id}: {theorem_id} proof_status lean_name drifted")
                if record.get("resolved") is not True:
                    failures.append(f"{contract_id}: {theorem_id} proof_status should be resolved")
                if record.get("proved") != (manifest_status in PROVED_STATUSES):
                    failures.append(f"{contract_id}: {theorem_id} proof_status proved drifted")

        contract_dictionary_ids = contract.get("dictionary_ids", [])
        unknown_dictionary_ids = sorted(set(contract_dictionary_ids) - known_dictionary_ids)
        if unknown_dictionary_ids:
            failures.append(f"{contract_id}: unknown dictionary ids {unknown_dictionary_ids}")

        if not str(contract_id).startswith("CC-AI-CONTRACT-"):
            failures.append(f"{contract_id}: id must use CC-AI-CONTRACT prefix")
        if not contract.get("contract_passed"):
            failures.append(f"{contract_id}: contract_passed is not true")
        if "not" not in str(contract.get("not_claimed", "")).lower():
            failures.append(f"{contract_id}: not_claimed boundary is missing or weak")

        source_paper = contract.get("source_paper")
        if not isinstance(source_paper, str) or not source_paper.strip():
            failures.append(f"{contract_id}: source_paper must be a non-empty path")
        elif not _path_exists(source_paper):
            failures.append(f"{contract_id}: source_paper is missing: {source_paper}")
        for path_key in ("quickstart_docs", "living_book_pages"):
            refs = contract.get(path_key, [])
            if not isinstance(refs, list) or not refs:
                failures.append(f"{contract_id}: {path_key} must be a non-empty list")
                continue
            for ref in refs:
                if not _path_exists(ref):
                    failures.append(f"{contract_id}: {path_key} entry is missing: {ref}")
        expected_page = EXPECTED_LIVING_BOOK_PAGE_BY_KIND.get(kind)
        living_book_pages = contract.get("living_book_pages", [])
        if expected_page is not None and expected_page not in living_book_pages:
            failures.append(
                f"{contract_id}: living_book_pages must include focused lesson "
                f"{expected_page}"
            )
        for command in contract.get("entrypoints", []):
            _check_entrypoint(command, failures)
        contract_validation_commands = contract.get("validation_commands", [])
        if not isinstance(contract_validation_commands, list) or not contract_validation_commands:
            failures.append(f"{contract_id}: validation_commands must be a non-empty list")
            contract_validation_commands = []
        for command in contract_validation_commands:
            _check_command_reference(
                command,
                failures,
                context=f"{contract_id}.validation_commands",
                make_targets=make_targets,
                fields_by_kind=fields_by_kind,
            )
        if not any(
            _is_contract_ready_kind_command(command, kind)
            for command in contract_validation_commands
        ):
            failures.append(
                f"{contract_id}: validation_commands must include "
                f"circle_ai_contract_ready.py --kind {kind}"
            )
        if not any(_is_pytest_command(command) for command in contract_validation_commands):
            failures.append(f"{contract_id}: validation_commands must include pytest")

        readiness_entry = readiness_index.get(kind)
        if not isinstance(readiness_entry, dict):
            failures.append(f"{contract_id}: missing contract_readiness_index entry")
        else:
            expected_ready = (
                isinstance(consumer_check, dict)
                and consumer_check.get("ready_for_downstream_fixture_use") is True
            )
            proof_status = contract.get("proof_status")
            missing_minimum_fields = (
                consumer_check.get("missing_minimum_fields", [])
                if isinstance(consumer_check, dict)
                else []
            )
            unresolved_theorem_ids = (
                consumer_check.get("unresolved_theorem_ids", [])
                if isinstance(consumer_check, dict)
                else []
            )
            unproved_theorem_ids = (
                consumer_check.get("unproved_theorem_ids", [])
                if isinstance(consumer_check, dict)
                else []
            )
            expected_pairs = {
                "id": contract_id,
                "kind": kind,
                "ready_for_downstream_fixture_use": expected_ready,
                "contract_passed": bool(contract.get("contract_passed")),
                "required_fields_present": (
                    isinstance(consumer_check, dict)
                    and consumer_check.get("required_fields_present") is True
                ),
                "missing_minimum_field_count": (
                    len(missing_minimum_fields)
                    if isinstance(missing_minimum_fields, list)
                    else 0
                ),
                "missing_minimum_fields": missing_minimum_fields,
                "all_theorem_ids_resolved": (
                    isinstance(consumer_check, dict)
                    and consumer_check.get("all_theorem_ids_resolved") is True
                ),
                "all_theorem_ids_proved": (
                    isinstance(consumer_check, dict)
                    and consumer_check.get("all_theorem_ids_proved") is True
                ),
                "unresolved_theorem_count": (
                    len(unresolved_theorem_ids)
                    if isinstance(unresolved_theorem_ids, list)
                    else 0
                ),
                "unresolved_theorem_ids": unresolved_theorem_ids,
                "unproved_theorem_count": (
                    len(unproved_theorem_ids)
                    if isinstance(unproved_theorem_ids, list)
                    else 0
                ),
                "unproved_theorem_ids": unproved_theorem_ids,
                "theorem_count": (
                    proof_status.get("theorem_count")
                    if isinstance(proof_status, dict)
                    else len(theorem_ids)
                ),
                "entrypoint_count": len(contract.get("entrypoints", [])),
                "quickstart_docs": contract.get("quickstart_docs", []),
                "living_book_pages": contract.get("living_book_pages", []),
                "planner_recommendation_count": len(planner_recommendations),
                "planner_recommendation_ids": [
                    recommendation["id"]
                    for recommendation in planner_recommendations
                    if isinstance(recommendation, dict)
                    and isinstance(recommendation.get("id"), str)
                ],
            }
            for key, expected in expected_pairs.items():
                if readiness_entry.get(key) != expected:
                    failures.append(f"{contract_id}: readiness index {key} drifted")

    contract_kinds = {
        contract.get("kind")
        for contract in contracts
        if isinstance(contract, dict) and isinstance(contract.get("kind"), str)
    }
    if set(readiness_index) != contract_kinds:
        failures.append("contract_readiness_index keys drifted from contract kinds")
    if set(recommendation_index) != set(expected_recommendation_index):
        failures.append("planner_recommendation_index keys drifted from contracts")
    if set(fingerprint_index) != set(expected_fingerprint_index):
        failures.append("contract_fingerprint_index keys drifted from contracts")
    for kind, expected in expected_fingerprint_index.items():
        indexed = fingerprint_index.get(kind)
        if not isinstance(indexed, dict):
            failures.append(f"contract_fingerprint_index.{kind} must be an object")
            continue
        for key, expected_value in expected.items():
            if indexed.get(key) != expected_value:
                failures.append(
                    f"contract_fingerprint_index.{kind}.{key} drifted"
                )
    for recommendation_id, expected in expected_recommendation_index.items():
        indexed = recommendation_index.get(recommendation_id)
        if not isinstance(indexed, dict):
            failures.append(
                f"planner_recommendation_index.{recommendation_id} must be an object"
            )
            continue
        for key, expected_value in expected.items():
            if indexed.get(key) != expected_value:
                failures.append(
                    f"planner_recommendation_index.{recommendation_id}.{key} drifted"
                )

    return failures


def find_contract(pack: dict[str, Any], kind: str) -> dict[str, Any] | None:
    contracts = pack.get("contracts")
    if not isinstance(contracts, list):
        return None
    for contract in contracts:
        if isinstance(contract, dict) and contract.get("kind") == kind:
            return contract
    return None


def contract_summary_lines(pack: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    contracts = pack.get("contracts", [])
    if not isinstance(contracts, list):
        return lines
    for contract in contracts:
        if not isinstance(contract, dict):
            continue
        consumer_check = contract.get("consumer_check")
        ready = (
            isinstance(consumer_check, dict)
            and consumer_check.get("ready_for_downstream_fixture_use") is True
        )
        fields = contract.get("fields")
        theorem_ids = contract.get("theorem_ids")
        entrypoints = contract.get("entrypoints")
        proof_status = contract.get("proof_status")
        minimum_fields = (
            consumer_check.get("minimum_fields", [])
            if isinstance(consumer_check, dict)
            else []
        )
        proof_resolved = (
            isinstance(proof_status, dict)
            and proof_status.get("all_theorem_ids_resolved") is True
        )
        proof_proved = (
            isinstance(proof_status, dict)
            and proof_status.get("all_theorem_ids_proved") is True
        )
        unresolved = (
            proof_status.get("unresolved_theorem_ids", [])
            if isinstance(proof_status, dict)
            else []
        )
        unproved = (
            proof_status.get("unproved_theorem_ids", [])
            if isinstance(proof_status, dict)
            else []
        )
        lines.append(
            "contract "
            f"kind={contract.get('kind', '<missing>')} "
            f"id={contract.get('id', '<missing>')} "
            f"ready={ready} "
            f"fields={len(fields) if isinstance(fields, dict) else 0} "
            f"minimum_fields={len(minimum_fields) if isinstance(minimum_fields, list) else 0} "
            f"theorems={len(theorem_ids) if isinstance(theorem_ids, list) else 0} "
            f"proof_resolved={proof_resolved} "
            f"proof_proved={proof_proved} "
            f"unresolved={len(unresolved) if isinstance(unresolved, list) else 0} "
            f"unproved={len(unproved) if isinstance(unproved, list) else 0} "
            f"entrypoints={len(entrypoints) if isinstance(entrypoints, list) else 0}"
        )
    return lines


def validate_schema_sidecar(pack: dict[str, Any], schema_path: Path) -> list[str]:
    if not schema_path.exists():
        return []
    try:
        schema = json.loads(schema_path.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(pack, schema)
    except jsonschema.ValidationError as exc:
        return [f"JSON Schema validation failed: {exc.message}"]
    except jsonschema.SchemaError as exc:
        return [f"JSON Schema sidecar is invalid: {exc.message}"]
    except json.JSONDecodeError as exc:
        return [f"JSON Schema sidecar is not valid JSON: {exc}"]
    return []


def validate_json_schema_file(schema_path: Path, *, label: str) -> list[str]:
    if not schema_path.exists():
        return [f"{label} JSON Schema is missing: {schema_path}"]
    try:
        schema = json.loads(schema_path.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        return [f"{label} JSON Schema is invalid: {exc.message}"]
    except json.JSONDecodeError as exc:
        return [f"{label} JSON Schema is not valid JSON: {exc}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a generated Circle AI contract pack JSON artifact.",
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_PACK),
        help="Path to circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print one downstream-readiness summary line per contract.",
    )
    parser.add_argument(
        "--schema-path",
        help=(
            "Optional JSON Schema sidecar path. Defaults to the pack path with "
            ".schema.json suffix when that file exists."
        ),
    )
    parser.add_argument(
        "--require-kind",
        action="append",
        default=[],
        help=(
            "Require a contract kind to exist and be ready for downstream fixture "
            "use. May be passed more than once."
        ),
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_absolute():
        path = ROOT / path
    pack = json.loads(path.read_text())
    failures = validate_pack(pack)
    schema_path = (
        Path(args.schema_path)
        if args.schema_path
        else path.with_suffix(".schema.json")
    )
    if not schema_path.is_absolute():
        schema_path = ROOT / schema_path
    if args.schema_path and not schema_path.exists():
        failures.append(f"JSON Schema sidecar is missing: {schema_path}")
    else:
        failures.extend(validate_schema_sidecar(pack, schema_path))
    failures.extend(
        validate_json_schema_file(
            DEFAULT_RUNNER_REQUEST_SCHEMA,
            label="contract-runner request",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_RUNNER_REQUEST_VALIDATION_SCHEMA,
            label="contract-runner request validation",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_RUNNER_RECEIPT_SCHEMA,
            label="contract-runner receipt",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_RUNNER_CHECK_SCHEMA,
            label="contract-runner check report",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_RECEIPT_FILE_CHECK_SCHEMA,
            label="contract receipt-file check report",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_CERTIFICATION_BUNDLE_SCHEMA,
            label="contract certification bundle",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA,
            label="contract certification-bundle file-check report",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_ARTIFACT_MANIFEST_SCHEMA,
            label="contract artifact manifest",
        )
    )
    failures.extend(
        validate_json_schema_file(
            DEFAULT_ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA,
            label="contract artifact-manifest file-check report",
        )
    )
    for kind in args.require_kind:
        contract = find_contract(pack, kind)
        if contract is None:
            failures.append(f"required contract kind is missing: {kind}")
            continue
        consumer_check = contract.get("consumer_check")
        if not isinstance(consumer_check, dict) or not consumer_check.get(
            "ready_for_downstream_fixture_use"
        ):
            failures.append(f"required contract kind is not downstream-ready: {kind}")
    if failures:
        print("circle AI contract pack check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    print(f"circle AI contract pack ok: {display_path}")
    if args.summary:
        for line in contract_summary_lines(pack):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
