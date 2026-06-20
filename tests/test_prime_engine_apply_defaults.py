from __future__ import annotations

from scripts.apply_prime_engine_defaults import build_default_updates


def calibration_row(
    *,
    low: int = 0,
    high: int = 10_000_000,
    source: str = "external_segment_sweep",
    stability: str | None = "stable",
    selected_segment_size: int = 98_304,
    selected_count_mode: str | None = None,
) -> dict[str, object]:
    row: dict[str, object] = {
        "source": source,
        "low": low,
        "high": high,
        "selected_segment_size": selected_segment_size,
        "selected_sample_stability": stability,
    }
    if selected_count_mode is not None:
        row["selected_count_mode"] = selected_count_mode
    return row


def defaults_fixture() -> dict[str, object]:
    return {
        "parallel_tiny_prefix_count_mode": "segmented",
        "parallel_tiny_prefix_segment_size": 262_144,
        "parallel_small_prefix_count_mode": "segmented",
        "parallel_small_prefix_segment_size": 65_536,
        "parallel_medium_prefix_count_mode": "segmented",
        "parallel_medium_prefix_segment_size": 131_072,
        "parallel_lower_high_offset_base_limit": 5_000_000,
        "parallel_lower_high_offset_count_mode": "presieve13",
        "parallel_lower_high_offset_min_base_limit": 1_200_000,
        "parallel_very_high_offset_count_mode": "segmented",
        "parallel_very_high_offset_segment_size": 3_145_728,
    }


def test_build_default_updates_applies_stable_external_recommendation() -> None:
    defaults = defaults_fixture()

    updated, changes, skipped = build_default_updates(
        {"recommendations": [calibration_row()]},
        defaults,
    )

    assert skipped == []
    assert updated["parallel_small_prefix_segment_size"] == 98_304
    assert changes == [
        {
            "key": "parallel_small_prefix_segment_size",
            "old": 65_536,
            "new": 98_304,
            "low": 0,
            "high": 10_000_000,
            "source": "external_segment_sweep",
            "stability": "stable",
        }
    ]


def test_build_default_updates_skips_noisy_external_recommendation() -> None:
    defaults = defaults_fixture()

    updated, changes, skipped = build_default_updates(
        {"recommendations": [calibration_row(stability="noisy")]},
        defaults,
    )

    assert updated == defaults
    assert changes == []
    assert skipped == [
        "refusing noisy/unknown external recommendation for "
        "parallel_small_prefix_segment_size/parallel_small_prefix_count_mode: noisy"
    ]


def test_build_default_updates_allows_confirmed_effectively_stable_mode() -> None:
    defaults = defaults_fixture()

    row = calibration_row(
        source="external_mode_sweep",
        stability="noisy",
        selected_segment_size=65_536,
        selected_count_mode="dynamic",
    )
    row["selected_effective_sample_stability"] = "stable"
    row["selected_mode_confirmation_status"] = "confirmed"
    updated, changes, skipped = build_default_updates(
        {"recommendations": [row]},
        defaults,
    )

    assert skipped == []
    assert updated["parallel_small_prefix_count_mode"] == "dynamic"
    assert changes == [
        {
            "key": "parallel_small_prefix_count_mode",
            "old": "segmented",
            "new": "dynamic",
            "low": 0,
            "high": 10_000_000,
            "source": "external_mode_sweep",
            "stability": "noisy",
        }
    ]


def test_build_default_updates_skips_unconfirmed_external_mode_recommendation() -> None:
    defaults = defaults_fixture()

    row = calibration_row(
        source="external_mode_sweep",
        stability="stable",
        selected_segment_size=65_536,
        selected_count_mode="dynamic",
    )
    row["selected_mode_confirmation_status"] = "unconfirmed"
    updated, changes, skipped = build_default_updates(
        {"recommendations": [row]},
        defaults,
    )

    assert updated == defaults
    assert changes == []
    assert skipped == [
        "refusing unconfirmed external recommendation for "
        "parallel_small_prefix_segment_size/parallel_small_prefix_count_mode: unconfirmed"
    ]


def test_build_default_updates_skips_unconfirmed_high_offset_recommendation() -> None:
    defaults = defaults_fixture()

    row = calibration_row(
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        source="external_high_offset_quick",
        stability="stable",
        selected_segment_size=1_441_792,
        selected_count_mode="presieve13",
    )
    row["selected_mode_confirmation_status"] = "unconfirmed"
    updated, changes, skipped = build_default_updates(
        {"recommendations": [row]},
        defaults,
    )

    assert updated == defaults
    assert changes == []
    assert skipped == [
        "refusing unconfirmed external recommendation for "
        "parallel_very_high_offset_segment_size/"
        "parallel_very_high_offset_count_mode: unconfirmed"
    ]


def test_build_default_updates_skips_unconfirmed_high_offset_tight_recommendation() -> None:
    defaults = defaults_fixture()

    row = calibration_row(
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        source="external_high_offset_tight",
        stability="stable",
        selected_segment_size=1_507_328,
        selected_count_mode="presieve17",
    )
    row["selected_mode_confirmation_status"] = "unconfirmed"
    updated, changes, skipped = build_default_updates(
        {"recommendations": [row]},
        defaults,
    )

    assert updated == defaults
    assert changes == []
    assert skipped == [
        "refusing unconfirmed external recommendation for "
        "parallel_very_high_offset_segment_size/"
        "parallel_very_high_offset_count_mode: unconfirmed"
    ]


def test_build_default_updates_applies_confirmed_high_offset_confirmation() -> None:
    defaults = defaults_fixture()

    row = calibration_row(
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        source="external_high_offset_confirmation",
        stability="stable",
        selected_segment_size=4_194_304,
        selected_count_mode="presieve17",
    )
    row["selected_effective_sample_stability"] = "stable"
    row["selected_mode_confirmation_status"] = "confirmed"
    updated, changes, skipped = build_default_updates(
        {"recommendations": [row]},
        defaults,
    )

    assert skipped == []
    assert updated["parallel_very_high_offset_segment_size"] == 4_194_304
    assert updated["parallel_very_high_offset_count_mode"] == "presieve17"
    assert changes == [
        {
            "key": "parallel_very_high_offset_segment_size",
            "old": 3_145_728,
            "new": 4_194_304,
            "low": 1_000_000_000_000,
            "high": 1_000_010_000_000,
            "source": "external_high_offset_confirmation",
            "stability": "stable",
        },
        {
            "key": "parallel_very_high_offset_count_mode",
            "old": "segmented",
            "new": "presieve17",
            "low": 1_000_000_000_000,
            "high": 1_000_010_000_000,
            "source": "external_high_offset_confirmation",
            "stability": "stable",
        },
    ]


def test_build_default_updates_allows_tuning_fallback_without_sample_stability() -> None:
    defaults = defaults_fixture()
    defaults["parallel_tiny_prefix_segment_size"] = 32_768
    defaults["parallel_small_prefix_segment_size"] = 98_304

    updated, changes, skipped = build_default_updates(
        {
            "recommendations": [
                calibration_row(
                    low=0,
                    high=1_000_000,
                    source="tuning",
                    stability=None,
                    selected_segment_size=262_144,
                )
            ]
        },
        defaults,
    )

    assert skipped == []
    assert updated["parallel_tiny_prefix_segment_size"] == 262_144
    assert changes[0]["key"] == "parallel_tiny_prefix_segment_size"


def test_build_default_updates_keeps_within_tolerance_default() -> None:
    defaults = defaults_fixture()
    row = calibration_row(
        low=0,
        high=1_000_000,
        source="tuning",
        stability=None,
        selected_segment_size=131_072,
        selected_count_mode="dynamic",
    )
    row["status"] = "within_tolerance"
    row["default_over_selected"] = 1.017
    defaults["parallel_tiny_prefix_count_mode"] = "dynamic"
    defaults["parallel_tiny_prefix_segment_size"] = 262_144

    updated, changes, skipped = build_default_updates(
        {"recommendations": [row]},
        defaults,
    )

    assert updated == defaults
    assert changes == []
    assert skipped == [
        "keeping current default within calibration tolerance for "
        "parallel_tiny_prefix_segment_size/parallel_tiny_prefix_count_mode: 1.017x"
    ]


def test_build_default_updates_refuses_missing_default_evidence() -> None:
    defaults = defaults_fixture()
    row = calibration_row(
        low=0,
        high=1_000_000,
        source="tuning",
        stability=None,
        selected_segment_size=131_072,
        selected_count_mode="dynamic",
    )
    row["status"] = "missing_default_evidence"

    updated, changes, skipped = build_default_updates(
        {"recommendations": [row]},
        defaults,
    )

    assert updated == defaults
    assert changes == []
    assert skipped == [
        "refusing recommendation without measured current-default evidence for "
        "parallel_tiny_prefix_segment_size/parallel_tiny_prefix_count_mode: "
        "missing_default_evidence"
    ]


def test_build_default_updates_applies_count_mode_recommendation() -> None:
    defaults = defaults_fixture()

    updated, changes, skipped = build_default_updates(
        {
            "recommendations": [
                calibration_row(
                    selected_segment_size=65_536,
                    selected_count_mode="hybrid-wheel30-mark",
                )
            ]
        },
        defaults,
    )

    assert skipped == []
    assert updated["parallel_small_prefix_count_mode"] == "hybrid-wheel30-mark"
    assert changes == [
        {
            "key": "parallel_small_prefix_count_mode",
            "old": "segmented",
            "new": "hybrid-wheel30-mark",
            "low": 0,
            "high": 10_000_000,
            "source": "external_segment_sweep",
            "stability": "stable",
        }
    ]
