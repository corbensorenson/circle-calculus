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

from .ai_contracts import CONTRACT_PACK_SCHEMA_ID, build_contract_pack
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


__all__ = [
    "contract_ready_main",
    "rope_certify_main",
    "sparse_attention_certify_main",
]


if __name__ == "__main__":
    raise SystemExit(contract_ready_main())
