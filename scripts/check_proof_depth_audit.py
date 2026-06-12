from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


DECL_RE = re.compile(r"^\s*(?:@[^\n]+?\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)")
NEXT_TOP_LEVEL_RE = re.compile(
    r"^(?:@[^\n]+)?\s*(?:theorem|lemma|def|abbrev|structure|inductive|namespace|section|end)\b"
)

TRIVIAL_LINE_PATTERNS = [
    re.compile(r"^rfl$"),
    re.compile(r"^simp(?:\s|\[|$)"),
    re.compile(r"^simpa(?:\s|\[|$)"),
    re.compile(r"^exact\s+rfl$"),
    re.compile(r"^exact\s+Iff\.rfl$"),
    re.compile(r"^constructor$"),
    re.compile(r"^Or\.inl\b"),
    re.compile(r"^Or\.inr\b"),
    re.compile("^exact\\s+\\u27e8"),
    re.compile(r"^exact\s+.*\.(?:fst|snd)$"),
]


@dataclass(frozen=True)
class ProofDepthCandidate:
    path: str
    line: int
    declaration: str
    reason: str
    review_category: str
    proof_line_count: int
    first_proof_lines: list[str]


def iter_lean_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.glob("**/*.lean"):
        if ".lake" in path.parts or "lake-packages" in path.parts:
            continue
        paths.append(path)
    return sorted(paths)


def collect_block(lines: list[str], start_index: int) -> list[str]:
    block = [lines[start_index]]
    for line in lines[start_index + 1 :]:
        if line and not line.startswith((" ", "\t")):
            if NEXT_TOP_LEVEL_RE.match(line) or line.startswith(("/-", "--")):
                break
        block.append(line)
    return block


def meaningful_proof_lines(block: list[str]) -> list[str]:
    proof_lines: list[str] = []
    after_by = False
    for line in block:
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if " by" in line or stripped == "by" or stripped.endswith(":= by"):
            after_by = True
            tail = line.split(" by", 1)[-1].strip()
            if tail and tail != stripped:
                proof_lines.append(tail)
            continue
        if after_by:
            proof_lines.append(stripped)
    return proof_lines


def classify_candidate(decl_name: str, proof_lines: list[str]) -> str | None:
    if not proof_lines:
        return None

    first = proof_lines[0]
    short = len(proof_lines) <= 5
    trivial_first = any(pattern.search(first) for pattern in TRIVIAL_LINE_PATTERNS)
    trivial_all = all(
        any(pattern.search(line) for pattern in TRIVIAL_LINE_PATTERNS)
        or line in {"left", "right", "omega", "norm_num"}
        for line in proof_lines
    )

    if trivial_first and short:
        return "short proof starts with a constructor/projection/trivial-normalization pattern"
    if trivial_all and short:
        return "short proof is made only of simple constructor/projection/normalization steps"
    if short and decl_name.endswith("_of_iff"):
        return "short theorem appears to package an iff direction"
    return None


def suggest_review_category(path: Path, decl_name: str) -> str:
    path_text = str(path)
    if "/Erdos/" in path_text:
        return "mathlib_bridge_wrapper"
    if "/Future/" in path_text or "Scaffold.lean" in path_text:
        return "scaffold_or_roadmap_fact"
    if "GlyphProof.lean" in path_text or "metadata" in decl_name.lower():
        return "metadata_projection"
    if "Certifier.lean" in path_text or "Certificate" in decl_name or "certificate" in decl_name:
        return "application_contract_bridge"
    if decl_name.endswith("_iff") or "_iff_" in decl_name:
        return "iff_packaging"
    if decl_name.endswith("_eq") or "_zero" in decl_name or "_idempotent" in decl_name:
        return "normalization_fact"
    return "review_required"


def scan(root: Path) -> tuple[int, list[ProofDepthCandidate]]:
    scanned = 0
    candidates: list[ProofDepthCandidate] = []
    for path in iter_lean_files(root):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            match = DECL_RE.match(line)
            if match is None:
                continue
            scanned += 1
            decl_name = match.group(1)
            block = collect_block(lines, index)
            proof_lines = meaningful_proof_lines(block)
            reason = classify_candidate(decl_name, proof_lines)
            if reason is None:
                continue
            candidates.append(
                ProofDepthCandidate(
                    path=str(path),
                    line=index + 1,
                    declaration=decl_name,
                    reason=reason,
                    review_category=suggest_review_category(path, decl_name),
                    proof_line_count=len(proof_lines),
                    first_proof_lines=proof_lines[:4],
                )
            )
    return scanned, candidates


def build_payload(scanned: int, candidates: list[ProofDepthCandidate]) -> dict[str, object]:
    return {
        "schema_id": "circle_calculus.proof_depth_audit.v0",
        "scanned_theorem_count": scanned,
        "candidate_count": len(candidates),
        "heuristic_boundary": (
            "This is a syntactic audit for review triage, not a sound mathematical "
            "depth measure and not part of the formal proof standard."
        ),
        "candidates": [asdict(candidate) for candidate in candidates],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Heuristically flag Lean theorem proofs that may be ceremonial wrappers."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return nonzero if low-depth candidates are found.",
    )
    args = parser.parse_args()

    scanned, candidates = scan(args.root)
    payload = build_payload(scanned, candidates)

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(
        f"proof depth audit: {scanned} theorem/lemma declarations scanned; "
        f"{len(candidates)} low-depth candidates"
    )
    for candidate in candidates[:25]:
        preview = " | ".join(candidate.first_proof_lines)
        print(
            f"{candidate.path}:{candidate.line}: {candidate.declaration}: "
            f"{candidate.reason}; category={candidate.review_category}; proof={preview}"
        )
    if len(candidates) > 25:
        print(f"... {len(candidates) - 25} more candidates omitted")

    if args.strict and candidates:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
