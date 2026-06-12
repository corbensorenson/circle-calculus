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

from circle_math.applications.circle_ai import certify_kv_cache_batch, certify_kv_cache_window

CLAIM_BOUNDARY = (
    "These are proof-carrying finite ring-buffer indexing certificates for a "
    "declared KV-cache window and retained token batch. They are not model-quality, "
    "throughput, memory-saving, retrieval-quality, paging-policy, implementation, "
    "or deployment-safety claims."
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
    return {
        "schema_id": "circle_calculus.kv_cache_ring_buffer_certificate.v0",
        "claim_boundary": CLAIM_BOUNDARY,
        "window_certificate": asdict(certificate),
        "batch_certificate": asdict(batch),
    }


def text_results(payload: dict[str, Any]) -> str:
    certificate = payload["window_certificate"]
    batch = payload["batch_certificate"]
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
            f"theorem_ids={','.join(batch['theorem_ids'])}"
        ),
        batch["note"],
    ]
    return "\n".join(lines) + "\n"


def markdown_results(payload: dict[str, Any]) -> str:
    certificate = payload["window_certificate"]
    batch = payload["batch_certificate"]
    return "\n".join(
        [
            "# KV-Cache Ring-Buffer Certificate Results",
            "",
            payload["claim_boundary"],
            "",
            "| Cache size | Current | Token | Slot | Current slot | Lag | Retained | Distinct from current | Next overwrite | Overwrite after current | Theorem ids |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- |",
            (
                f"| {certificate['cache_size']} | {certificate['current']} | "
                f"{certificate['token']} | {certificate['slot']} | "
                f"{certificate['current_slot']} | {certificate['lag']} | "
                f"{certificate['retained']} | "
                f"{certificate['retained_noncurrent_slot_distinct_from_current']} | "
                f"{certificate['next_overwrite_token']} | "
                f"{certificate['next_overwrite_after_current']} | "
                f"{', '.join(certificate['theorem_ids'])} |"
            ),
            "",
            "| Batch tokens | Batch slots | All retained | Tokens distinct | Slots distinct | Theorem ids |",
            "| --- | --- | --- | --- | --- | --- |",
            (
                f"| {', '.join(str(token) for token in batch['tokens'])} | "
                f"{', '.join(str(slot) for slot in batch['slots'])} | "
                f"{batch['all_retained']} | {batch['tokens_distinct']} | "
                f"{batch['slots_distinct']} | {', '.join(batch['theorem_ids'])} |"
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
