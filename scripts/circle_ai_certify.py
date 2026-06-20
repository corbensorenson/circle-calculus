#!/usr/bin/env python
"""Run parameterized Circle AI contract certifiers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications import (  # noqa: E402
    build_contract_receipt,
    load_contract_pack,
    receipt_summary_lines,
)


def parse_tokens(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    return tuple(int(part.strip()) for part in raw.replace(";", ",").split(",") if part.strip())


def parse_strides(raw: str) -> tuple[int, ...]:
    strides = parse_tokens(raw)
    if not strides:
        raise argparse.ArgumentTypeError("strides must contain at least one integer")
    if any(stride <= 0 for stride in strides):
        raise argparse.ArgumentTypeError("strides must be positive")
    return strides


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either a human summary or the full receipt JSON.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for the machine-readable receipt JSON.",
    )
    parser.add_argument(
        "--pack",
        type=Path,
        help=(
            "Optional generated contract-pack path. Defaults to building the "
            "pack in memory from repository sources."
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Issue theorem-linked Circle AI contract receipts for user-supplied "
            "RoPE, KV-cache, sparse-attention, and recurrence parameters."
        ),
    )
    subparsers = parser.add_subparsers(dest="kind", required=True)

    rope = subparsers.add_parser(
        "rope",
        help="Certify a RoPE position-distinguishability configuration.",
    )
    add_common_options(rope)
    rope.add_argument("--head-dim", type=int, default=128)
    rope.add_argument("--base", type=float, default=10000.0)
    rope.add_argument("--context", type=int, default=32768)
    rope.add_argument("--tolerance", type=float, default=1e-6)
    rope.add_argument(
        "--discretization",
        choices=("round", "floor", "ceil"),
        default="round",
    )
    rope.add_argument(
        "--requested-margin",
        help=(
            "Optional real-phase margin request, for example 1/328459. "
            "Currently classified by the D19 channel-0 range theorem when in scope."
        ),
    )

    kv = subparsers.add_parser(
        "kv-cache",
        help="Certify a KV-cache ring-buffer freshness request.",
    )
    add_common_options(kv)
    kv.add_argument("--cache-size", required=True, type=int)
    kv.add_argument("--current", required=True, type=int)
    kv.add_argument("--token", required=True, type=int)
    kv.add_argument("--batch-tokens", type=parse_tokens, default=())
    kv.add_argument("--sink-size", type=int, default=0)
    kv.add_argument("--request-id", default="read_request")

    sparse = subparsers.add_parser(
        "sparse-attention",
        help="Certify a local-window plus stride-family sparse-attention plan.",
    )
    add_common_options(sparse)
    sparse.add_argument("--context", required=True, type=int)
    sparse.add_argument("--strides", required=True, type=parse_strides)
    sparse.add_argument("--path-length", required=True, type=int)
    sparse.add_argument("--local-window", required=True, type=int)

    recurrence = subparsers.add_parser(
        "recurrence",
        help="Certify a finite looped/recursive schedule.",
    )
    add_common_options(recurrence)
    recurrence.add_argument("--loop-period", type=int, default=5)
    recurrence.add_argument("--sample-index", type=int, default=8)
    recurrence.add_argument("--max-loops", type=int, default=7)
    recurrence.add_argument("--token-count", type=int, default=8)
    recurrence.add_argument("--selected-block-start", type=int, default=2)
    recurrence.add_argument("--selected-block-width", type=int, default=3)
    recurrence.add_argument("--shift-passes", type=int, default=3)

    return parser.parse_args()


def _pack_from_args(args: argparse.Namespace) -> dict[str, Any] | None:
    if args.pack is None:
        return None
    path = args.pack
    if not path.is_absolute():
        path = ROOT / path
    return load_contract_pack(path)


def _parameters_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if args.kind == "rope":
        return {
            "head_dim": args.head_dim,
            "base": args.base,
            "context": args.context,
            "tolerance": args.tolerance,
            "discretization": args.discretization,
            "requested_margin": args.requested_margin,
        }
    if args.kind == "kv-cache":
        return {
            "cache_size": args.cache_size,
            "current": args.current,
            "token": args.token,
            "batch_tokens": args.batch_tokens,
            "sink_size": args.sink_size,
            "request_id": args.request_id,
        }
    if args.kind == "sparse-attention":
        return {
            "context": args.context,
            "strides": args.strides,
            "path_length": args.path_length,
            "local_window": args.local_window,
        }
    if args.kind == "recurrence":
        return {
            "loop_period": args.loop_period,
            "sample_index": args.sample_index,
            "max_loops": args.max_loops,
            "token_count": args.token_count,
            "selected_block_start": args.selected_block_start,
            "selected_block_width": args.selected_block_width,
            "shift_passes": args.shift_passes,
        }
    raise SystemExit(f"unsupported subcommand: {args.kind}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    receipt = build_contract_receipt(
        args.kind,
        _parameters_from_args(args),
        pack=_pack_from_args(args),
    )
    if args.json_out is not None:
        write_json(args.json_out, receipt)
    if args.format == "json":
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        for line in receipt_summary_lines(receipt):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
