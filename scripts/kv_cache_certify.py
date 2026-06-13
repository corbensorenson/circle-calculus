#!/usr/bin/env python
"""Run the finite KV-cache ring-buffer safety certifier."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from circle_math.applications import (
    certify_kv_cache_batch,
    certify_kv_cache_live_window,
    certify_kv_cache_window,
)

CLAIM_BOUNDARY = (
    "This is a proof-carrying finite ring-buffer indexing and retained-window "
    "certificate. It is not a paging-policy, throughput, memory-saving, "
    "retrieval-quality, implementation-correctness, deployment-safety, or "
    "model-quality claim."
)


def parse_tokens(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    return tuple(int(part.strip()) for part in raw.replace(";", ",").split(",") if part.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify finite KV-cache ring-buffer slot, freshness, retained-batch, "
            "and full live-window coverage facts."
        ),
    )
    parser.add_argument("--cache-size", required=True, type=int, help="Positive ring-buffer size.")
    parser.add_argument("--current", required=True, type=int, help="Current token index.")
    parser.add_argument("--token", required=True, type=int, help="Token to inspect.")
    parser.add_argument(
        "--batch-tokens",
        type=parse_tokens,
        default=(),
        help="Optional comma-separated retained batch to certify, for example 20,24,29,31.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable certificate JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full certificate JSON to stdout.",
    )
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    window = certify_kv_cache_window(
        cache_size=args.cache_size,
        current=args.current,
        token=args.token,
    )
    batch_tokens = args.batch_tokens or (args.token,)
    batch = certify_kv_cache_batch(
        cache_size=args.cache_size,
        current=args.current,
        tokens=batch_tokens,
    )
    live_window = certify_kv_cache_live_window(
        cache_size=args.cache_size,
        current=args.current,
    )
    return {
        "schema_id": "circle_calculus.kv_cache_ring_buffer_certificate.v0",
        "claim_boundary": CLAIM_BOUNDARY,
        "window_certificate": asdict(window),
        "batch_certificate": asdict(batch),
        "live_window_certificate": asdict(live_window),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def unique_theorem_ids(*groups: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for group in groups:
        for theorem_id in group:
            if theorem_id not in seen:
                seen.add(theorem_id)
                ordered.append(theorem_id)
    return tuple(ordered)


def summary_lines(payload: dict[str, Any]) -> list[str]:
    window = payload["window_certificate"]
    batch = payload["batch_certificate"]
    live_window = payload["live_window_certificate"]
    freshness = "LIVE" if window["retained"] else "STALE_OR_FUTURE"
    coverage = "FULL" if live_window["full_coverage_contract"] else "PREFIX"
    return [
        (
            "kv_cache_contract="
            f"{freshness} cache_size={window['cache_size']} current={window['current']} "
            f"token={window['token']} slot={window['slot']} "
            f"current_slot={window['current_slot']} lag={window['lag']}"
        ),
        (
            "overwrite_boundary="
            f"next_overwrite={window['next_overwrite_token']} "
            f"after_current={window['next_overwrite_after_current']} "
            f"stale_by_boundary={window['stale_by_next_overwrite_boundary']} "
            "no_same_slot_overwrite_before_current="
            f"{window['no_same_slot_overwrite_before_current']} "
            "same_slot_overwrite_witness_when_stale="
            f"{window['same_slot_overwrite_witness_when_stale']} "
            "retained_iff_no_same_slot_overwrite_trace="
            f"{window['retained_iff_no_same_slot_overwrite_trace']}"
        ),
        (
            "batch_contract="
            f"tokens={tuple(batch['tokens'])} slots={tuple(batch['slots'])} "
            f"all_retained={batch['all_retained']} "
            f"tokens_distinct={batch['tokens_distinct']} "
            f"slots_distinct={batch['slots_distinct']} "
            "retained_iff_no_same_slot_overwrite_trace="
            f"{batch['retained_iff_no_same_slot_overwrite_trace']}"
        ),
        (
            "live_window_contract="
            f"{coverage} start={live_window['start']} length={live_window['length']} "
            f"slots_distinct={live_window['slots_distinct']} "
            f"slot_count_matches_cache_size={live_window['slot_count_matches_cache_size']} "
            f"full_coverage_contract={live_window['full_coverage_contract']}"
        ),
        (
            "theorem_ids="
            f"{unique_theorem_ids(window['theorem_ids'], batch['theorem_ids'], live_window['theorem_ids'])}"
        ),
        f"boundary={payload['claim_boundary']}",
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
