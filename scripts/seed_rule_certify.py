#!/usr/bin/env python
"""Run the finite seed-rule exact-regeneration certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import build_seed_rule_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify finite seed/rule exact regeneration, storage-accounting "
            "fields, and bounded declared generator-search facts."
        ),
    )
    parser.add_argument(
        "--n",
        type=int,
        default=128,
        help="Positive finite-circle size for the public seed-rule fixture.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable seed-rule contract JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full generic contract JSON to stdout.",
    )
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.n <= 0:
        raise SystemExit("--n must be positive")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)
    return build_seed_rule_contract(n=args.n)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary_lines(payload: dict[str, Any]) -> list[str]:
    fields = payload["fields"]
    consumer = payload["consumer_check"]
    status = "READY" if consumer["ready_for_downstream_fixture_use"] else "NOT_READY"
    return [
        (
            "seed_rule_contract="
            f"{status} artifact_id={fields['artifact_id']} fixture_n={fields['fixture_n']} "
            f"exact_regeneration={fields['exact_regeneration']} "
            f"generator_shorter={fields['generator_shorter']}"
        ),
        (
            "storage_accounting="
            f"explicit_length={fields['explicit_length']} "
            f"generator_length={fields['generator_length']} "
            f"storage_saving={fields['storage_saving']} "
            f"storage_saving_positive={fields['storage_saving_positive']} "
            "generator_shorter_iff_positive_saving="
            f"{fields['generator_shorter_iff_positive_saving']} "
            "saving_plus_generator_eq_explicit="
            f"{fields['storage_saving_add_generator_length_eq_explicit_length']} "
            "theorems=GEN-T0046,GEN-T0047,GEN-T0048,GEN-T0049,GEN-T0050"
        ),
        (
            "bounded_search="
            f"search_id={fields['bounded_search_id']} "
            f"candidate_count={fields['bounded_search_candidate_count']} "
            f"exact_candidate_count={fields['bounded_search_exact_candidate_count']} "
            "exact_count_le_candidate_count="
            f"{fields['bounded_search_exact_candidate_count_le_candidate_count']} "
            f"has_best_exact={fields['bounded_search_has_best_exact']} "
            "best_exact_regenerates="
            f"{fields['bounded_search_best_exact_regenerates']} "
            f"has_best_shorter={fields['bounded_search_has_best_shorter']} "
            "best_shorter_generator_shorter="
            f"{fields['bounded_search_best_shorter_generator_shorter']} "
            "theorems=GEN-T0037,GEN-T0044,GEN-T0045"
        ),
        (
            "candidate_ranking="
            "by_generator_length="
            f"{tuple(fields['bounded_search_candidate_ids_by_generator_length'])} "
            "exact_by_generator_length="
            f"{tuple(fields['bounded_search_exact_candidate_ids_by_generator_length'])} "
            "shorter_by_generator_length="
            f"{tuple(fields['bounded_search_shorter_candidate_ids_by_generator_length'])} "
            f"best_exact={fields['bounded_search_best_exact_candidate_id']} "
            f"best_shorter={fields['bounded_search_best_shorter_candidate_id']}"
        ),
        (
            "generator_record="
            f"seed={tuple(tuple(item) for item in fields['seed'])} "
            f"rules={tuple(rule['rule_id'] for rule in fields['rules'])} "
            f"closure_condition={fields['closure_condition']!r}"
        ),
        (
            "consumer_check="
            f"ready={consumer['ready_for_downstream_fixture_use']} "
            f"required_fields_present={consumer['required_fields_present']} "
            f"all_theorem_ids_proved={consumer['all_theorem_ids_proved']} "
            f"missing_fields={len(consumer['missing_minimum_fields'])}"
        ),
        f"bounded_search_note={fields['bounded_search_note']}",
        f"not_claimed={payload['not_claimed']}",
    ]


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    if args.json_out is not None:
        write_json(args.json_out, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in summary_lines(payload):
            print(line)


if __name__ == "__main__":
    main()
