from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from circle_math import Circle


OUT = Path("sidecars/PAPER_01_FINITE_CIRCLES/diagrams")


def render_orbit_svg(circle: Circle, stride: int, filename: str) -> None:
    orbit = circle.orbit(0, stride)
    width = 720
    height = 120
    step = width / max(len(orbit), 1)
    labels = []
    lines = []
    for index, node in enumerate(orbit):
        x = 20 + index * step
        labels.append(f'<text x="{x:.1f}" y="70" font-size="16" text-anchor="middle">{node}</text>')
        if index + 1 < len(orbit):
            x2 = 20 + (index + 1) * step
            lines.append(f'<line x1="{x + 10:.1f}" y1="62" x2="{x2 - 10:.1f}" y2="62" stroke="black"/>')
    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            f'<text x="20" y="25" font-size="18">C_{circle.n}, stride {stride}</text>',
            *lines,
            *labels,
            "</svg>",
        ]
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / filename).write_text(svg)


def main() -> int:
    render_orbit_svg(Circle(12), 5, "c12_stride5.svg")
    render_orbit_svg(Circle(12), 4, "c12_stride4.svg")
    render_orbit_svg(Circle(13), 5, "c13_stride5.svg")
    render_orbit_svg(Circle(36), 6, "c36_stride6.svg")
    print(f"rendered examples to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
