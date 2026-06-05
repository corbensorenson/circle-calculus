from __future__ import annotations

import sys

from site_lib import GENERATED, collect_theorem_ids, load_json, repo_relative


def main() -> int:
    data = load_json(GENERATED / "theorem_manifest.json")
    known = {item["id"] for item in data.get("theorems", [])}
    unknown: list[str] = []
    for path, ids in collect_theorem_ids().items():
        for theorem_id in sorted(ids - known):
            unknown.append(f"{repo_relative(path)}: {theorem_id}")
    if unknown:
        print("unknown theorem ids:", file=sys.stderr)
        for item in unknown:
            print(item, file=sys.stderr)
        return 1
    print("site theorem links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
