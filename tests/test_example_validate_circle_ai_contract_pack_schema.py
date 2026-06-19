from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications.circle_ai_contracts import (
    build_contract_pack,
    build_contract_pack_json_schema,
)


def _write_pack_and_schema(tmp_path: Path) -> tuple[Path, Path]:
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    schema_path = tmp_path / "circle_ai_contract_pack.schema.json"
    pack_path.write_text(json.dumps(build_contract_pack()))
    schema_path.write_text(json.dumps(build_contract_pack_json_schema()))
    return pack_path, schema_path


def test_example_schema_validator_accepts_generated_pack(tmp_path: Path) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
            "--summary",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract schema ok:" in result.stdout
    assert "schema_id=circle_calculus.ai_contract_pack.v0" in result.stdout
    assert "contracts=9" in result.stdout
    assert "rope_position_distinguishability" in result.stdout


def test_example_schema_validator_rejects_missing_minimum_field(
    tmp_path: Path,
) -> None:
    pack_path, schema_path = _write_pack_and_schema(tmp_path)
    pack = json.loads(pack_path.read_text())
    for contract in pack["contracts"]:
        if contract["kind"] == "strided_candidate_fanout":
            del contract["fields"]["effective_candidate_budget"]
            break
    pack_path.write_text(json.dumps(pack))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_validate_circle_ai_contract_pack_schema.py",
            "--pack",
            str(pack_path),
            "--schema",
            str(schema_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "effective_candidate_budget" in result.stderr
