"""Honest-experiment test: the circulant inductive bias helps iff the structure matches.

This pins the *honest* finding of the bias-variance study, including the regime where the
circle-structured model LOSES. It is a controlled linear study, not a claim about deep
transformers.
"""

from __future__ import annotations

from circle_math.applications.circle_transformer_experiment import run_experiment


def test_circulant_wins_on_shift_structured_small_sample() -> None:
    # Right inductive bias + few parameters -> better generalization on periodic structure.
    r = run_experiment(n=16, n_train=12, structured=True, seed=0)
    assert r.circulant_test_mse < r.dense_test_mse
    # dense badly overfits 256 params on a tiny sample
    assert r.dense_test_mse > 10 * r.circulant_test_mse


def test_dense_wins_on_unstructured_target() -> None:
    # Wrong inductive bias -> circulant cannot represent a non-circulant map and loses.
    r = run_experiment(n=16, n_train=48, structured=False, seed=0)
    assert r.dense_test_mse < r.circulant_test_mse


def test_circulant_has_irreducible_bias_floor_on_unstructured() -> None:
    # More data does NOT rescue the circulant model when the target isn't shift-structured:
    # its test error stays high (the honest ceiling of the inductive bias).
    small = run_experiment(n=16, n_train=24, structured=False, seed=0)
    large = run_experiment(n=16, n_train=200, structured=False, seed=0)
    assert small.circulant_test_mse > 0.3
    assert large.circulant_test_mse > 0.3
