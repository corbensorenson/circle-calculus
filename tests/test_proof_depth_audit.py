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
