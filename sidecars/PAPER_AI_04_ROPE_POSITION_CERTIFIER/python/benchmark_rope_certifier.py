"""Run the public RoPE position distinguishability certifier presets.

This sidecar is a paper-local convenience wrapper around ``scripts/rope_certify.py``.
It emits compact text summaries for the three named configurations used by
the paper. The certificates are structural position-contract reports, not model
quality or long-context benchmark claims.
"""

from __future__ import annotations

import argparse

from circle_math.applications import (
    ROPE_CERTIFIER_PRESETS,
    certificate_summary_lines,
    certify_rope_positions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run named RoPE certifier presets.")
    parser.add_argument(
        "--preset",
        action="append",
        choices=sorted(ROPE_CERTIFIER_PRESETS),
        help="Preset to run. May be passed more than once. Defaults to all presets.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    presets = tuple(args.preset) if args.preset else tuple(sorted(ROPE_CERTIFIER_PRESETS))
    for index, preset in enumerate(presets):
        if index:
            print()
        certificate = certify_rope_positions(ROPE_CERTIFIER_PRESETS[preset])
        print(f"preset={preset}")
        for line in certificate_summary_lines(certificate):
            print(line)


if __name__ == "__main__":
    main()
