from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from circle_math.applications.phase_probe import run_circle_phase_probe


ROOT = Path(__file__).resolve().parents[1]


def test_phase_features_make_synthetic_periodic_label_linearly_readable() -> None:
    result = run_circle_phase_probe(period=8, train_cycles=4, test_cycles=2, backend="numpy")

    assert result.backend_used == "numpy"
    assert result.baseline_train_accuracy == pytest.approx(0.5)
    assert result.baseline_test_accuracy == pytest.approx(0.5)
    assert result.phase_train_accuracy == pytest.approx(1.0)
    assert result.phase_test_accuracy == pytest.approx(1.0)
    assert "does not prove" in result.non_claims


@pytest.mark.parametrize("period", [6, 8, 10, 12])
def test_probe_is_deterministic_for_even_periods(period: int) -> None:
    result = run_circle_phase_probe(period=period, train_cycles=4, test_cycles=2, backend="numpy")

    assert result.baseline_test_accuracy == pytest.approx(0.5)
    assert result.phase_test_accuracy == pytest.approx(1.0)


def test_probe_rejects_invalid_period() -> None:
    with pytest.raises(ValueError, match="period must be positive"):
        run_circle_phase_probe(period=0, backend="numpy")


def test_probe_cli_json_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/circle_phase_probe_demo.py",
            "--backend",
            "numpy",
            "--format",
            "json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["backend_used"] == "numpy"
    assert payload["baseline_test_accuracy"] == pytest.approx(0.5)
    assert payload["phase_test_accuracy"] == pytest.approx(1.0)
    assert "does not prove" in payload["non_claims"]


def test_probe_cli_text_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/circle_phase_probe_demo.py",
            "--backend",
            "numpy",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    assert "circle_phase_probe=READY period=8 backend=numpy train=32 test=16" in completed.stdout
    assert "baseline=raw_position_linear train_accuracy=0.500000 test_accuracy=0.500000" in completed.stdout
    assert "phase=circle_sin_cos_linear train_accuracy=1.000000 test_accuracy=1.000000" in completed.stdout
    assert "non_claimed=This synthetic probe does not prove" in completed.stdout
