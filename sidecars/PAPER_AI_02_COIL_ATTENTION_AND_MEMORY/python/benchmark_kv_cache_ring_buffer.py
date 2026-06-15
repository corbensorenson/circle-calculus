"""Tiny KV-cache ring-buffer safety sidecar.

This script reports one finite indexing certificate for a declared cache size,
current token position, and retained token position. It is not a model-quality,
throughput, memory-saving, or deployment-safety benchmark.

Run:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from circle_math.applications.circle_ai import (
    certify_kv_cache_adapter_request_trace,
    certify_kv_cache_batch,
    certify_kv_cache_live_window,
    certify_kv_cache_live_window_request,
    certify_kv_cache_window,
)

CLAIM_BOUNDARY = (
    "These are proof-carrying finite ring-buffer indexing certificates for a "
    "declared KV-cache window, retained token batch, and modeled adapter "
    "request trace. They are not model-quality, throughput, memory-saving, "
    "retrieval-quality, paging-policy, implementation, or deployment-safety claims."
)


def parse_tokens(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    return tuple(int(part.strip()) for part in raw.split(","))


def build_payload(*, cache_size: int, current: int, token: int, batch_tokens: str) -> dict[str, Any]:
    certificate = certify_kv_cache_window(
        cache_size=cache_size,
        current=current,
        token=token,
    )
    batch = certify_kv_cache_batch(
        cache_size=cache_size,
        current=current,
        tokens=parse_tokens(batch_tokens),
    )
    adapter_request = certify_kv_cache_adapter_request_trace(
        cache_size=cache_size,
        current=current,
        requested_tokens=parse_tokens(batch_tokens),
        request_id="default_read_request",
    )
    live_window = certify_kv_cache_live_window(
        cache_size=cache_size,
        current=current,
    )
    live_window_request = certify_kv_cache_live_window_request(
        cache_size=cache_size,
        current=current,
        request_id="generated_live_window_read",
    )
    return {
        "schema_id": "circle_calculus.kv_cache_ring_buffer_certificate.v0",
        "claim_boundary": CLAIM_BOUNDARY,
        "window_certificate": asdict(certificate),
        "batch_certificate": asdict(batch),
        "adapter_request_trace_certificate": asdict(adapter_request),
        "live_window_certificate": asdict(live_window),
        "live_window_request_certificate": asdict(live_window_request),
    }


def text_results(payload: dict[str, Any]) -> str:
    certificate = payload["window_certificate"]
    batch = payload["batch_certificate"]
    adapter_request = payload["adapter_request_trace_certificate"]
    live_window = payload["live_window_certificate"]
    live_window_request = payload["live_window_request_certificate"]
    lines = [
        (
            "kv_cache_ring_buffer "
            f"cache_size={certificate['cache_size']} "
            f"current={certificate['current']} "
            f"token={certificate['token']} "
            f"slot={certificate['slot']} "
            f"current_slot={certificate['current_slot']} "
            f"lag={certificate['lag']} "
            f"retained={certificate['retained']} "
            f"collision_with_current={certificate['collision_with_current']} "
            "retained_noncurrent_slot_distinct_from_current="
            f"{certificate['retained_noncurrent_slot_distinct_from_current']} "
            f"next_overwrite_token={certificate['next_overwrite_token']} "
            f"next_overwrite_after_current={certificate['next_overwrite_after_current']} "
            f"stale_by_next_overwrite_boundary={certificate['stale_by_next_overwrite_boundary']} "
            "no_same_slot_overwrite_before_current="
            f"{certificate['no_same_slot_overwrite_before_current']} "
            "same_slot_overwrite_witness_when_stale="
            f"{certificate['same_slot_overwrite_witness_when_stale']} "
            "retained_iff_no_same_slot_overwrite_trace="
            f"{certificate['retained_iff_no_same_slot_overwrite_trace']} "
            "trace_fresh_iff_next_overwrite_boundary="
            f"{certificate['trace_fresh_iff_next_overwrite_boundary']} "
            f"collision_with_next_overwrite={certificate['collision_with_next_overwrite']} "
            f"theorem_ids={','.join(certificate['theorem_ids'])}"
        ),
        certificate["note"],
        (
            "kv_cache_ring_buffer_batch "
            f"cache_size={batch['cache_size']} "
            f"current={batch['current']} "
            f"tokens={','.join(str(token) for token in batch['tokens'])} "
            f"slots={','.join(str(slot) for slot in batch['slots'])} "
            f"all_retained={batch['all_retained']} "
            f"tokens_distinct={batch['tokens_distinct']} "
            f"slots_distinct={batch['slots_distinct']} "
            "retained_iff_no_same_slot_overwrite_trace="
            f"{batch['retained_iff_no_same_slot_overwrite_trace']} "
            "next_overwrites_after_current="
            f"{batch['next_overwrites_after_current']} "
            "trace_fresh_iff_next_overwrite_boundary="
            f"{batch['trace_fresh_iff_next_overwrite_boundary']} "
            f"trace_fresh_slots_distinct={batch['trace_fresh_slots_distinct']} "
            f"theorem_ids={','.join(batch['theorem_ids'])}"
        ),
        batch["note"],
        (
            "kv_cache_adapter_request_trace "
            f"request_id={adapter_request['request_id']} "
            f"cache_size={adapter_request['cache_size']} "
            f"current={adapter_request['current']} "
            f"tokens={','.join(str(token) for token in adapter_request['requested_tokens'])} "
            f"slots={','.join(str(slot) for slot in adapter_request['requested_slots'])} "
            f"request_token_count={adapter_request['request_token_count']} "
            f"all_non_future={adapter_request['all_non_future']} "
            f"all_retained={adapter_request['all_retained']} "
            f"tokens_distinct={adapter_request['tokens_distinct']} "
            f"slots_distinct={adapter_request['slots_distinct']} "
            "retained_iff_no_same_slot_overwrite_trace="
            f"{adapter_request['retained_iff_no_same_slot_overwrite_trace']} "
            "next_overwrites_after_current="
            f"{adapter_request['next_overwrites_after_current']} "
            "trace_fresh_iff_next_overwrite_boundary="
            f"{adapter_request['trace_fresh_iff_next_overwrite_boundary']} "
            f"trace_fresh_slots_distinct={adapter_request['trace_fresh_slots_distinct']} "
            "ordered_live_window_subrequest="
            f"{adapter_request['ordered_live_window_subrequest']} "
            "duplicate_free_live_window_subrequest="
            f"{adapter_request['duplicate_free_live_window_subrequest']} "
            "live_window_subrequest_pass_contract="
            f"{adapter_request['live_window_subrequest_pass_contract']} "
            f"pass_certificate={adapter_request['pass_certificate']} "
            "pass_iff_next_overwrite_boundary="
            f"{adapter_request['pass_iff_next_overwrite_boundary']} "
            f"theorem_ids={','.join(adapter_request['theorem_ids'])}"
        ),
        adapter_request["note"],
        (
            "kv_cache_live_window "
            f"cache_size={live_window['cache_size']} "
            f"current={live_window['current']} "
            f"start={live_window['start']} "
            f"length={live_window['length']} "
            f"tokens={','.join(str(token) for token in live_window['tokens'])} "
            f"slots={','.join(str(slot) for slot in live_window['slots'])} "
            f"all_tokens_retained={live_window['all_tokens_retained']} "
            f"slots_distinct={live_window['slots_distinct']} "
            f"full_window={live_window['full_window']} "
            f"slots_within_cache={live_window['slots_within_cache']} "
            f"slot_range_covered={live_window['slot_range_covered']} "
            "slot_count_matches_cache_size="
            f"{live_window['slot_count_matches_cache_size']} "
            "slot_count_matches_full_window="
            f"{live_window['slot_count_matches_full_window']} "
            f"full_coverage_contract={live_window['full_coverage_contract']} "
            "full_coverage_contract_matches_full_window="
            f"{live_window['full_coverage_contract_matches_full_window']} "
            f"theorem_ids={','.join(live_window['theorem_ids'])}"
        ),
        live_window["note"],
        (
            "kv_cache_live_window_request "
            f"request_id={live_window_request['request_id']} "
            f"cache_size={live_window_request['cache_size']} "
            f"current={live_window_request['current']} "
            f"tokens={','.join(str(token) for token in live_window_request['requested_tokens'])} "
            f"slots={','.join(str(slot) for slot in live_window_request['requested_slots'])} "
            "exact_live_window_request="
            f"{live_window_request['exact_live_window_request']} "
            f"request_token_count={live_window_request['request_token_count']} "
            f"all_non_future={live_window_request['all_non_future']} "
            f"all_retained={live_window_request['all_retained']} "
            f"tokens_distinct={live_window_request['tokens_distinct']} "
            f"slots_distinct={live_window_request['slots_distinct']} "
            f"pass_certificate={live_window_request['pass_certificate']} "
            "live_window_request_contract="
            f"{live_window_request['live_window_request_contract']} "
            f"fixture_theorem_ids={','.join(live_window_request['fixture_theorem_ids'])} "
            f"theorem_ids={','.join(live_window_request['theorem_ids'])}"
        ),
        live_window_request["note"],
    ]
    return "\n".join(lines) + "\n"


def markdown_results(payload: dict[str, Any]) -> str:
    certificate = payload["window_certificate"]
    batch = payload["batch_certificate"]
    adapter_request = payload["adapter_request_trace_certificate"]
    live_window = payload["live_window_certificate"]
    live_window_request = payload["live_window_request_certificate"]
    return "\n".join(
        [
            "# KV-Cache Ring-Buffer Certificate Results",
            "",
            payload["claim_boundary"],
            "",
            "| Cache size | Current | Token | Slot | Current slot | Lag | Retained | Distinct from current | Next overwrite | Overwrite after current | Stale by overwrite boundary | No same-slot overwrite before current | Stale same-slot overwrite witness | Retained iff no later same-slot write | Trace iff boundary | Theorem ids |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {certificate['cache_size']} | {certificate['current']} | "
                f"{certificate['token']} | {certificate['slot']} | "
                f"{certificate['current_slot']} | {certificate['lag']} | "
                f"{certificate['retained']} | "
                f"{certificate['retained_noncurrent_slot_distinct_from_current']} | "
                f"{certificate['next_overwrite_token']} | "
                f"{certificate['next_overwrite_after_current']} | "
                f"{certificate['stale_by_next_overwrite_boundary']} | "
                f"{certificate['no_same_slot_overwrite_before_current']} | "
                f"{certificate['same_slot_overwrite_witness_when_stale']} | "
                f"{certificate['retained_iff_no_same_slot_overwrite_trace']} | "
                f"{certificate['trace_fresh_iff_next_overwrite_boundary']} | "
                f"{', '.join(certificate['theorem_ids'])} |"
            ),
            "",
            "| Batch tokens | Batch slots | All retained | Tokens distinct | Slots distinct | Retained iff no later same-slot writes | Next overwrites after current | Trace iff boundary | Trace-fresh slots distinct | Theorem ids |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {', '.join(str(token) for token in batch['tokens'])} | "
                f"{', '.join(str(slot) for slot in batch['slots'])} | "
                f"{batch['all_retained']} | {batch['tokens_distinct']} | "
                f"{batch['slots_distinct']} | "
                f"{batch['retained_iff_no_same_slot_overwrite_trace']} | "
                f"{batch['next_overwrites_after_current']} | "
                f"{batch['trace_fresh_iff_next_overwrite_boundary']} | "
                f"{batch['trace_fresh_slots_distinct']} | "
                f"{', '.join(batch['theorem_ids'])} |"
            ),
            "",
            "| Request id | Requested tokens | Requested slots | All non-future | All retained | Tokens distinct | Slots distinct | Trace iff | Next overwrites after current | Trace iff boundary | Trace-fresh slots distinct | Ordered live-window subrequest | Duplicate-free live-window subrequest | Subrequest pass contract | Pass certificate | Pass iff boundary | Theorem ids |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {adapter_request['request_id']} | "
                f"{', '.join(str(token) for token in adapter_request['requested_tokens'])} | "
                f"{', '.join(str(slot) for slot in adapter_request['requested_slots'])} | "
                f"{adapter_request['all_non_future']} | "
                f"{adapter_request['all_retained']} | "
                f"{adapter_request['tokens_distinct']} | "
                f"{adapter_request['slots_distinct']} | "
                f"{adapter_request['retained_iff_no_same_slot_overwrite_trace']} | "
                f"{adapter_request['next_overwrites_after_current']} | "
                f"{adapter_request['trace_fresh_iff_next_overwrite_boundary']} | "
                f"{adapter_request['trace_fresh_slots_distinct']} | "
                f"{adapter_request['ordered_live_window_subrequest']} | "
                f"{adapter_request['duplicate_free_live_window_subrequest']} | "
                f"{adapter_request['live_window_subrequest_pass_contract']} | "
                f"{adapter_request['pass_certificate']} | "
                f"{adapter_request['pass_iff_next_overwrite_boundary']} | "
                f"{', '.join(adapter_request['theorem_ids'])} |"
            ),
            "",
            "| Live start | Live length | Live tokens | Live slots | All retained | Slots distinct | Full window | Slot count matches cache | Slot range covered | Slot count iff full window | Slots within cache | Full coverage contract | Full coverage iff full window | Theorem ids |",
            "| ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {live_window['start']} | {live_window['length']} | "
                f"{', '.join(str(token) for token in live_window['tokens'])} | "
                f"{', '.join(str(slot) for slot in live_window['slots'])} | "
                f"{live_window['all_tokens_retained']} | {live_window['slots_distinct']} | "
                f"{live_window['full_window']} | "
                f"{live_window['slot_count_matches_cache_size']} | "
                f"{live_window['slot_range_covered']} | "
                f"{live_window['slot_count_matches_full_window']} | "
                f"{live_window['slots_within_cache']} | "
                f"{live_window['full_coverage_contract']} | "
                f"{live_window['full_coverage_contract_matches_full_window']} | "
                f"{', '.join(live_window['theorem_ids'])} |"
            ),
            "",
            "| Request id | Requested tokens | Requested slots | Exact live-window request | Request count | All retained | Tokens distinct | Slots distinct | Pass certificate | Live-window request contract | Fixture theorem ids | Theorem ids |",
            "| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {live_window_request['request_id']} | "
                f"{', '.join(str(token) for token in live_window_request['requested_tokens'])} | "
                f"{', '.join(str(slot) for slot in live_window_request['requested_slots'])} | "
                f"{live_window_request['exact_live_window_request']} | "
                f"{live_window_request['request_token_count']} | "
                f"{live_window_request['all_retained']} | "
                f"{live_window_request['tokens_distinct']} | "
                f"{live_window_request['slots_distinct']} | "
                f"{live_window_request['pass_certificate']} | "
                f"{live_window_request['live_window_request_contract']} | "
                f"{', '.join(live_window_request['fixture_theorem_ids'])} | "
                f"{', '.join(live_window_request['theorem_ids'])} |"
            ),
            "",
            "Reproduce with:",
            "",
            "```bash",
            "python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py --format markdown",
            "```",
            "",
        ]
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-size", type=int, default=16)
    parser.add_argument("--current", type=int, default=31)
    parser.add_argument("--token", type=int, default=20)
    parser.add_argument("--batch-tokens", default="20,24,29,31")
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format for stdout.",
    )
    parser.add_argument("--json-out", type=Path, help="Optional JSON result file.")
    parser.add_argument("--markdown-out", type=Path, help="Optional Markdown result file.")
    args = parser.parse_args()

    payload = build_payload(
        cache_size=args.cache_size,
        current=args.current,
        token=args.token,
        batch_tokens=args.batch_tokens,
    )
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown_text = markdown_results(payload)
    if args.json_out is not None:
        write_text(args.json_out, json_text)
    if args.markdown_out is not None:
        write_text(args.markdown_out, markdown_text)
    if args.format == "json":
        print(json_text, end="")
    elif args.format == "markdown":
        print(markdown_text, end="")
    else:
        print(text_results(payload), end="")


if __name__ == "__main__":
    main()
