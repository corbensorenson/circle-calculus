from __future__ import annotations

import re
import sys
from pathlib import Path


FORBIDDEN = [
    re.compile(r"\bsorry\b"),
    re.compile(r"\badmit\b"),
    re.compile(r"\bby\?\b"),
    re.compile(r"\baxiom\b"),
    re.compile(r"\bunsafe\b"),
    re.compile(r"set_option\s+autoImplicit\s+true"),
]


def main() -> int:
    violations: list[str] = []
    for path in Path(".").glob("**/*.lean"):
        if ".lake" in path.parts or "lake-packages" in path.parts:
            continue
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            for pattern in FORBIDDEN:
                if pattern.search(line):
                    violations.append(f"{path}:{lineno}: {line.strip()}")
    if violations:
        print("forbidden proof placeholders found:", file=sys.stderr)
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1
    print("no fake proof markers found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

