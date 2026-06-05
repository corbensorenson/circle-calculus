from __future__ import annotations

import sys

from site_lib import GENERATED, collect_dictionary_ids, load_json, repo_relative


def main() -> int:
    data = load_json(GENERATED / "dictionary.json")
    known = {item["id"] for item in data.get("entries", [])}
    unknown: list[str] = []
    for path, ids in collect_dictionary_ids().items():
        for dictionary_id in sorted(ids - known):
            unknown.append(f"{repo_relative(path)}: {dictionary_id}")
    if unknown:
        print("unknown dictionary ids:", file=sys.stderr)
        for item in unknown:
            print(item, file=sys.stderr)
        return 1
    print("site dictionary links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
