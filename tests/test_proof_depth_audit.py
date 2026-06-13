from __future__ import annotations

import json
import subprocess
import sys


def test_proof_depth_audit_runs_as_nonfailing_heuristic(tmp_path) -> None:
    output = tmp_path / "proof_depth_audit.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_proof_depth_audit.py",
            "--json-out",
            str(output),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "proof depth audit:" in result.stdout
    payload = json.loads(output.read_text())
    assert payload["schema_id"] == "circle_calculus.proof_depth_audit.v0"
    assert payload["scanned_theorem_count"] > 0
    assert "not a sound mathematical depth measure" in payload["heuristic_boundary"]
    assert payload["candidates"]
    assert "review_category" in payload["candidates"][0]
    assert payload["review_required_count"] == 0


def test_proof_depth_audit_can_fail_on_unclassified_low_depth_candidate(tmp_path) -> None:
    lean_file = tmp_path / "Unclassified.lean"
    lean_file.write_text(
        "theorem toyLowDepthCandidate : True := by\n"
        "  constructor\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_proof_depth_audit.py",
            "--root",
            str(tmp_path),
            "--fail-on-review-required",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "1 require category review" in result.stdout
