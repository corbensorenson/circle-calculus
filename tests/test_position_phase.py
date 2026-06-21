from __future__ import annotations

import pytest

from circle_math.ai_contracts import (
    POSITION_PHASE_COLLISION_REPORT_SCHEMA_ID,
    POSITION_PHASE_GRID_REPORT_SCHEMA_ID,
    POSITION_PHASE_SCHEMA_ID,
    longrope_nonuniform_scaled_phase_bank,
    period_divides_gap,
    phase_bank_collision_report,
    phase_bank_from_periods,
    phase_channel_collides,
    phase_channel_distinguishes,
    phase_grid_2d_collision_report,
    phase_residue,
    rope_integer_phase_bank,
    scaled_periods,
    scaled_phase_bank,
    sinusoidal_integer_phase_bank,
    xpos_integer_phase_bank,
    yarn_uniform_scaled_phase_bank,
)


def test_phase_channel_residue_matches_divisibility_contract() -> None:
    assert phase_residue(13, 40) == 1
    assert phase_channel_collides(12, 5, 29) is True
    assert period_divides_gap(12, 5, 29) is True
    assert phase_channel_distinguishes(13, 5, 29) is True
    assert period_divides_gap(13, 5, 29) is False


def test_phase_bank_collision_report_exposes_witness_channels() -> None:
    bank = phase_bank_from_periods("diagnostic", [6, 9, 13])
    report = phase_bank_collision_report(bank, 0, 36)

    assert bank.schema_id == POSITION_PHASE_SCHEMA_ID
    assert report.schema_id == POSITION_PHASE_COLLISION_REPORT_SCHEMA_ID
    assert report.gap == 36
    assert report.all_channels_collide is False
    assert report.distinguishes is True
    assert report.witness_channels == ("phase_2",)
    assert [result.period_divides_gap for result in report.channel_results] == [
        True,
        True,
        False,
    ]


def test_scaled_phase_banks_preserve_positive_integer_periods() -> None:
    bank = phase_bank_from_periods("base", [6, 10, 15])

    assert scaled_periods(bank.periods, 4) == (24, 40, 60)

    scaled = scaled_phase_bank(bank, 4)
    assert scaled.periods == (24, 40, 60)
    assert scaled.scheme == "uniform_scaled_integer_phase_bank"

    yarn = yarn_uniform_scaled_phase_bank(bank, scale=8)
    assert yarn.periods == (48, 80, 120)
    assert yarn.scheme == "yarn_uniform_scaled_phase_bank"

    longrope = longrope_nonuniform_scaled_phase_bank(bank, scale_factors=[1, 2, 3])
    assert longrope.periods == (6, 20, 45)
    assert longrope.scheme == "longrope_nonuniform_scaled_phase_bank"


def test_rope_family_descriptors_are_phase_only_contracts() -> None:
    sinusoidal = sinusoidal_integer_phase_bank(model_dim=8, channel_count=3)
    rope = rope_integer_phase_bank(head_dim=8, channel_count=3)
    xpos = xpos_integer_phase_bank(head_dim=8, channel_count=3)

    assert sinusoidal.periods == rope.periods == xpos.periods
    assert rope.scheme == "rope_integer_phase_bank"
    assert xpos.scheme == "xpos_integer_phase_bank"
    assert "amplitude_decay_not_proved" in xpos.channels[0].source

    report = phase_bank_collision_report(rope, 0, rope.periods[0])
    assert report.channel_results[0].collides is True
    assert report.distinguishes is True


def test_2d_phase_grid_report_is_axiswise_collision_conjunction() -> None:
    x_bank = phase_bank_from_periods("x", [4, 6], axis="x")
    y_bank = phase_bank_from_periods("y", [5], axis="y")

    report = phase_grid_2d_collision_report(x_bank, y_bank, (0, 1), (12, 6))
    assert report.schema_id == POSITION_PHASE_GRID_REPORT_SCHEMA_ID
    assert report.x_report.all_channels_collide is True
    assert report.y_report.all_channels_collide is True
    assert report.grid_collides is True
    assert report.grid_distinguishes is False

    separated = phase_grid_2d_collision_report(x_bank, y_bank, (0, 1), (10, 6))
    assert separated.x_report.all_channels_collide is False
    assert separated.y_report.all_channels_collide is True
    assert separated.grid_collides is False
    assert separated.grid_distinguishes is True


def test_phase_bank_rejects_invalid_periods_and_positions() -> None:
    with pytest.raises(ValueError):
        phase_residue(0, 4)
    with pytest.raises(ValueError):
        phase_residue(5, -1)
    with pytest.raises(ValueError):
        phase_bank_from_periods("empty", [])
    with pytest.raises(ValueError):
        longrope_nonuniform_scaled_phase_bank(
            phase_bank_from_periods("base", [6, 7]),
            scale_factors=[2],
        )
