from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from scripts.confirm_prime_external_modes import (
    build_confirmation,
    confirmation_input_metadata,
    fresh_sweep_command,
    render_markdown,
    run_fresh_sweeps,
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
    run1 = recommendation(source="run1", median_ms=2.9)
    run1["candidates"] = [
        dict(run1),
        recommendation(source="run1", mode="segmented", median_ms=3.2),
    ]
    run2 = recommendation(source="run2", median_ms=3.0)
    run2["candidates"] = [
        dict(run2),
        recommendation(source="run2", mode="segmented", median_ms=3.1),
    ]
    run3 = recommendation(source="run3", mode="segmented", median_ms=3.2)
    run3["candidates"] = [
        recommendation(source="run3", median_ms=3.3),
        dict(run3),
    ]
    confirmation = build_confirmation(
        [run1, run2, run3],
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
    assert row["median_speedup_values"] == [1.1, 1.1]
    identities = confirmation["identity_summaries"]
    dynamic = [
        row for row in identities if row["count_mode"] == "dynamic"
    ][0]
    segmented = [
        row for row in identities if row["count_mode"] == "segmented"
    ][0]
    assert dynamic["status"] == "confirmed"
    assert dynamic["confirmation_count"] == 3
    assert dynamic["observed_count"] == 3
    assert segmented["status"] == "confirmed"
    assert segmented["confirmation_count"] == 3
    assert segmented["observed_count"] == 3
    markdown = render_markdown(confirmation)
    assert "External Mode Confirmation" in markdown
    assert "Median Speedups" in markdown
    assert "Identity Evidence" in markdown
    assert "Fresh-run count requests per timed sample: `3`" in markdown


def test_build_confirmation_records_input_metadata_provenance(tmp_path: Path) -> None:
    csv_path = tmp_path / "confirm.csv"
    metadata_path = tmp_path / "confirm.json"
    metadata_path.write_text(
        """{
  "started_at_utc": "2026-01-01T00:00:00Z",
  "finished_at_utc": "2026-01-01T00:00:02Z",
  "rounds": 9,
  "batch_size": 20,
  "warmup_rounds": 2,
  "circle_variants": [{"count_mode": "default", "segment_size": 0}],
  "external_baselines": ["external_primesieve_count_server"],
  "thread_policy": {"circle_requested_threads": 8},
  "circle_prime_defaults": {"sha256": "0123456789abcdef"},
  "tools": {
    "circle_prime": {
      "binary": {"sha256": "abcdef0123456789"},
      "defaults": {"sha256": "ignored"}
    }
  }
}
"""
    )
    input_metadata = confirmation_input_metadata([csv_path], [metadata_path])

    confirmation = build_confirmation(
        [recommendation(source=str(csv_path))],
        baseline_priority=["external_primesieve_count"],
        min_confirmations=1,
        require_stable_samples=True,
        generated_at_utc="2026-01-01T00:00:03Z",
        inputs=[str(csv_path)],
        input_metadata=input_metadata,
    )

    row = confirmation["input_metadata"][0]
    assert row["input"] == str(csv_path)
    assert row["finished_at_utc"] == "2026-01-01T00:00:02Z"
    assert row["circle_prime_defaults"]["sha256"] == "0123456789abcdef"
    markdown = render_markdown(confirmation)
    assert "Input Provenance" in markdown
    assert "`abcdef012345`" in markdown
    assert "`0123456789ab`" in markdown


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


def test_run_fresh_sweeps_runs_each_requested_sweep_once(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: object) -> object:
        calls.append(command)
        assert kwargs["check"] is True
        return object()

    monkeypatch.setattr("scripts.confirm_prime_external_modes.subprocess.run", fake_run)
    args = Namespace(
        output_dir=tmp_path,
        run_prefix="confirm_probe",
        runs=2,
        ranges="1000000000000:1000010000000",
        rounds=3,
        batch_size=20,
        warmup_rounds=1,
        circle_threads=8,
        external_threads=8,
        external_baselines="external_primesieve_count_server",
        circle_count_modes="segmented,presieve13,presieve17",
        segment_sizes="0",
        circle_variant=["default:0"],
        include_circle_server=True,
        circle_server_only=True,
        include_primesieve_count_server=True,
        require_tool=["primesieve-library"],
    )

    csv_paths, metadata_paths = run_fresh_sweeps(args)

    assert len(calls) == 2
    assert [path.name for path in csv_paths] == [
        "confirm_probe_01.csv",
        "confirm_probe_02.csv",
    ]
    assert [path.name for path in metadata_paths] == [
        "confirm_probe_01.json",
        "confirm_probe_02.json",
    ]
