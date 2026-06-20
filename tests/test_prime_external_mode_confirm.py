from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from scripts.confirm_prime_external_modes import (
    build_confirmation,
    fresh_sweep_command,
    render_markdown,
)


def recommendation(
    *,
    low: int = 0,
    high: int = 10_000_000,
    baseline: str = "external_primesieve_count",
    mode: str = "dynamic",
    segment_size: int = 65_536,
    threads: int = 8,
    requested_threads: int = 8,
    median_ms: float = 3.0,
    median_speedup: float = 1.1,
    stability: str = "stable",
    source: str = "run",
) -> dict[str, object]:
    return {
        "source": source,
        "source_path": source,
        "baseline": baseline,
        "low": low,
        "high": high,
        "span": high - low,
        "count_mode": mode,
        "segment_size": segment_size,
        "threads": threads,
        "requested_threads": requested_threads,
        "best_ms": median_ms * 0.95,
        "median_ms": median_ms,
        "circle_speedup": median_speedup,
        "median_circle_speedup": median_speedup,
        "sample_stability": stability,
    }


def test_build_confirmation_requires_repeated_stable_winner() -> None:
    confirmation = build_confirmation(
        [
            recommendation(source="run1", median_ms=2.9),
            recommendation(source="run2", median_ms=3.0),
            recommendation(source="run3", mode="segmented", median_ms=3.2),
        ],
        baseline_priority=["external_primesieve_count"],
        min_confirmations=2,
        require_stable_samples=True,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs=["run1.csv", "run2.csv", "run3.csv"],
        batch_size=3,
    )

    assert confirmation["confirmed_count"] == 1
    assert confirmation["unconfirmed_count"] == 0
    row = confirmation["winners"][0]
    assert row["status"] == "confirmed"
    assert row["count_mode"] == "dynamic"
    assert row["confirmation_count"] == 2
    assert row["stable_observed_count"] == 3
    markdown = render_markdown(confirmation)
    assert "External Mode Confirmation" in markdown
    assert "Fresh-run count requests per timed sample: `3`" in markdown


def test_build_confirmation_rejects_noisy_repeat_by_default() -> None:
    confirmation = build_confirmation(
        [
            recommendation(source="run1", stability="noisy"),
            recommendation(source="run2", stability="noisy"),
        ],
        baseline_priority=["external_primesieve_count"],
        min_confirmations=2,
        require_stable_samples=True,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs=["run1.csv", "run2.csv"],
    )

    row = confirmation["winners"][0]
    assert row["status"] == "unconfirmed"
    assert row["confirmation_count"] == 0
    assert row["stable_observed_count"] == 0


def test_build_confirmation_rejects_stable_rows_that_do_not_beat_baseline() -> None:
    confirmation = build_confirmation(
        [
            recommendation(source="run1", median_speedup=0.995),
            recommendation(source="run2", median_speedup=1.0),
        ],
        baseline_priority=["external_primesieve_count"],
        min_confirmations=2,
        require_stable_samples=True,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs=["run1.csv", "run2.csv"],
    )

    row = confirmation["winners"][0]
    assert row["status"] == "unconfirmed"
    assert row["confirmation_count"] == 0
    assert row["stable_observed_count"] == 2


def test_build_confirmation_can_allow_unstable_for_exploration() -> None:
    confirmation = build_confirmation(
        [
            recommendation(source="run1", stability="noisy"),
            recommendation(source="run2", stability="unknown"),
        ],
        baseline_priority=["external_primesieve_count"],
        min_confirmations=2,
        require_stable_samples=False,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs=["run1.csv", "run2.csv"],
    )

    row = confirmation["winners"][0]
    assert row["status"] == "confirmed"
    assert row["confirmation_count"] == 2


def test_fresh_sweep_command_forwards_segment_size_grid() -> None:
    command = fresh_sweep_command(
        Namespace(
            ranges="0:10000000",
            rounds=5,
            batch_size=3,
            warmup_rounds=1,
            circle_threads=8,
            external_threads=8,
            external_baselines="external_primesieve_count_server",
            circle_count_modes="dynamic,segmented",
            segment_sizes="0,98304,196608",
            circle_variant=["default:0,dynamic:98304"],
            include_circle_server=True,
            circle_server_only=True,
            include_primesieve_count_server=True,
            require_tool=[
                "primecount",
                "primesieve",
                "primesieve",
                "primesieve-library",
            ],
        ),
        Path("out.csv"),
        Path("samples.csv"),
        Path("meta.json"),
    )

    assert "--segment-sizes" in command
    assert command[command.index("--segment-sizes") + 1] == "0,98304,196608"
    assert "--batch-size" in command
    assert command[command.index("--batch-size") + 1] == "3"
    assert "--warmup-rounds" in command
    assert command[command.index("--warmup-rounds") + 1] == "1"
    assert "--external-baselines" in command
    assert (
        command[command.index("--external-baselines") + 1]
        == "external_primesieve_count_server"
    )
    assert "--circle-variant" in command
    assert command[command.index("--circle-variant") + 1] == "default:0,dynamic:98304"
    assert "--include-circle-server" in command
    assert "--circle-server-only" in command
    assert "--include-primesieve-count-server" in command
    assert command.count("--require-tool") == 3
