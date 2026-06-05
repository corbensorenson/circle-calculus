from __future__ import annotations

import sys

from site_lib import GENERATED, THEOREM_ID_RE, load_json, repo_relative, site_source_files

from check_manifest import lean_declarations


PROVED_WORDS = ("Lean-proved", "proved")


def main() -> int:
    data = load_json(GENERATED / "theorem_manifest.json")
    theorem_by_id = {item["id"]: item for item in data.get("theorems", [])}
    declarations = lean_declarations()
    failures: list[str] = []

    for theorem in theorem_by_id.values():
        if theorem.get("canonical_status") == "proved":
            if theorem.get("original_status") not in {"proved", "lean_proved"}:
                failures.append(f"{theorem['id']}: canonical proved status is not backed by original proved status")
            lean_name = theorem.get("lean_name")
            if lean_name and lean_name not in declarations:
                failures.append(f"{theorem['id']}: proved Lean declaration not found: {lean_name}")

    for path in site_source_files():
        lines = path.read_text().splitlines()
        for index, line in enumerate(lines):
            ids = THEOREM_ID_RE.findall(line)
            if not ids:
                continue
            context = "\n".join(lines[max(0, index - 2): index + 3])
            for theorem_id in ids:
                theorem = theorem_by_id.get(theorem_id)
                if not theorem:
                    continue
                if theorem.get("canonical_status") != "proved" and any(word in context for word in PROVED_WORDS):
                    failures.append(f"{repo_relative(path)}: unproved theorem {theorem_id} appears near proved language")

    if failures:
        print("site theorem status failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("site theorem status ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
