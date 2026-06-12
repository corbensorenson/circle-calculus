"""Tiny KV-cache ring-buffer safety sidecar.

This script reports one finite indexing certificate for a declared cache size,
current token position, and retained token position. It is not a model-quality,
throughput, memory-saving, or deployment-safety benchmark.

Run:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import certify_kv_cache_batch, certify_kv_cache_window


def parse_tokens(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    return tuple(int(part.strip()) for part in raw.split(","))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-size", type=int, default=16)
    parser.add_argument("--current", type=int, default=31)
    parser.add_argument("--token", type=int, default=20)
    parser.add_argument("--batch-tokens", default="20,24,29,31")
    args = parser.parse_args()

    certificate = certify_kv_cache_window(
        cache_size=args.cache_size,
        current=args.current,
        token=args.token,
    )
    print(
        "kv_cache_ring_buffer "
        f"cache_size={certificate.cache_size} "
        f"current={certificate.current} "
        f"token={certificate.token} "
        f"slot={certificate.slot} "
        f"current_slot={certificate.current_slot} "
        f"lag={certificate.lag} "
        f"retained={certificate.retained} "
        f"collision_with_current={certificate.collision_with_current} "
        f"retained_noncurrent_slot_distinct_from_current="
        f"{certificate.retained_noncurrent_slot_distinct_from_current} "
        f"next_overwrite_token={certificate.next_overwrite_token} "
        f"next_overwrite_after_current={certificate.next_overwrite_after_current} "
        f"collision_with_next_overwrite={certificate.collision_with_next_overwrite} "
        f"theorem_ids={','.join(certificate.theorem_ids)}"
    )
    print(certificate.note)

    batch = certify_kv_cache_batch(
        cache_size=args.cache_size,
        current=args.current,
        tokens=parse_tokens(args.batch_tokens),
    )
    print(
        "kv_cache_ring_buffer_batch "
        f"cache_size={batch.cache_size} "
        f"current={batch.current} "
        f"tokens={','.join(str(token) for token in batch.tokens)} "
        f"slots={','.join(str(slot) for slot in batch.slots)} "
        f"all_retained={batch.all_retained} "
        f"tokens_distinct={batch.tokens_distinct} "
        f"slots_distinct={batch.slots_distinct} "
        f"theorem_ids={','.join(batch.theorem_ids)}"
    )
    print(batch.note)


if __name__ == "__main__":
    main()
