from __future__ import annotations

import sys
from pathlib import Path

from site_lib import ROOT, collect_paper_refs, repo_relative


def resolve_ref(source: Path, ref: str) -> Path:
    if ref.startswith("papers/"):
        return ROOT / ref
    return (source.parent / ref).resolve()


def main() -> int:
    failures: list[str] = []
    for source, refs in collect_paper_refs().items():
        for ref in sorted(refs):
            path = resolve_ref(source, ref)
            if not path.exists():
                failures.append(f"{repo_relative(source)}: missing paper link {ref}")
    if failures:
        print("site paper link failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("site paper links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
