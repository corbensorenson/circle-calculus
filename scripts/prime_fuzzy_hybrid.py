from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MR64_BASES = (2, 325, 9_375, 28_178, 450_775, 9_780_504, 1_795_265_022)
SCHEMA_ID = "circle_calculus.prime_fuzzy_hybrid_report.v0"
HYBRID_CONTRACT_NAME = "prime_fuzzy_hybrid_verified_prime_search_v0"
HYBRID_THEOREM_IDS = ("CC-T0073", "CC-T0074", "CC-T0075", "CC-T0076", "CC-T0077")
HYBRID_LEAN_NAMES = (
    "Circle.primeHorizon_iff_no_sqrt_contained",
    "Circle.primeHorizon_no_factor_below_sqrt",
    "Circle.primeHorizon_factor_bound",
    "Circle.primeHorizon_contains_prime",
    "Circle.primeHorizon_prime_of_contains",
)
DEFAULT_RESIDUE_MODULI = (3, 5, 7, 11, 13, 17, 19, 23)


class PrimeLabeler(Protocol):
    name: str

    def is_prime(self, n: int) -> bool:
        ...


class BuiltinMr64Labeler:
    name = "builtin_mr64_reference"

    def is_prime(self, n: int) -> bool:
        return is_prime_u64_mr(n)


class CirclePrimeCliLabeler:
    def __init__(self, binary: Path) -> None:
        self.binary = binary
        self.name = f"circle_prime_cli:{binary}"
        self._cache: dict[int, bool] = {}

    def is_prime(self, n: int) -> bool:
        if n not in self._cache:
            completed = subprocess.run(
                [str(self.binary), "test", str(n), "--json"],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            payload = json.loads(completed.stdout)
            self._cache[n] = payload.get("status") == "prime"
        return self._cache[n]


class CachedCountingLabeler:
    def __init__(self, labeler: PrimeLabeler) -> None:
        self.labeler = labeler
        self.name = labeler.name
        self._cache: dict[int, bool] = {}
        self.unique_checks = 0

    def is_prime(self, n: int) -> bool:
        if n not in self._cache:
            self._cache[n] = self.labeler.is_prime(n)
            self.unique_checks += 1
        return self._cache[n]


@dataclass(frozen=True)
class TinyBitLogisticModel:
    bit_width: int
    weights: tuple[float, ...]
    bias: float
    residue_moduli: tuple[int, ...] = ()

    def score(self, n: int) -> float:
        features = feature_vector(n, self.bit_width, self.residue_moduli)
        z = float(
            np.dot(np.asarray(self.weights, dtype=np.float64), features) + self.bias
        )
        return sigmoid(z)

    def to_json(self) -> dict[str, object]:
        kind = (
            "tiny_bit_residue_logistic"
            if self.residue_moduli
            else "tiny_bit_logistic"
        )
        return {
            "kind": kind,
            "bit_width": self.bit_width,
            "parameter_count": len(self.weights) + 1,
            "feature_count": len(self.weights),
            "input_order": "least_significant_bit_first",
            "residue_moduli": list(self.residue_moduli),
            "residue_features": (
                "bit-derived n mod m is nonzero for each modulus"
                if self.residue_moduli
                else None
            ),
            "weights": [round(weight, 12) for weight in self.weights],
            "bias": round(self.bias, 12),
        }

    def to_text(self) -> str:
        residue_moduli = (
            ",".join(str(modulus) for modulus in self.residue_moduli)
            if self.residue_moduli
            else "none"
        )
        return "\n".join(
            [
                "circle_fuzzy_model_v0",
                f"bit_width {self.bit_width}",
                f"residue_moduli {residue_moduli}",
                "weights " + ",".join(f"{weight:.17g}" for weight in self.weights),
                f"bias {self.bias:.17g}",
                "",
            ]
        )


def is_prime_u64_mr(n: int) -> bool:
    if n < 2:
        return False
    if n >= 1 << 64:
        raise ValueError("builtin MR64 labeler only supports n < 2^64")
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if n == prime:
            return True
        if n % prime == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for base in MR64_BASES:
        a = base % n
        if a == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(1, s):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def bits_lsb(n: int, bit_width: int) -> np.ndarray:
    if n < 0:
        raise ValueError("bit input must be nonnegative")
    if bit_width <= 0:
        raise ValueError("bit_width must be positive")
    if n >= 1 << bit_width:
        raise ValueError(f"n={n} does not fit in bit_width={bit_width}")
    return np.fromiter(((n >> index) & 1 for index in range(bit_width)), dtype=np.float64)


def feature_vector(
    n: int,
    bit_width: int,
    residue_moduli: tuple[int, ...],
) -> np.ndarray:
    bits = bits_lsb(n, bit_width)
    if not residue_moduli:
        return bits
    residues = np.asarray(
        [1.0 if n % modulus != 0 else 0.0 for modulus in residue_moduli],
        dtype=np.float64,
    )
    return np.concatenate([bits, residues])


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def sample_numbers(
    *,
    low: int,
    high: int,
    count: int,
    seed: int,
    odd_only: bool,
) -> list[int]:
    if count <= 0:
        raise ValueError("sample count must be positive")
    if high <= low:
        raise ValueError("sample high must be greater than low")
    rng = random.Random(seed)
    if odd_only:
        has_two = low <= 2 < high
        first_odd = max(low, 3)
        if first_odd % 2 == 0:
            first_odd += 1
        odd_count = 0
        if first_odd < high:
            odd_count = ((high - 1 - first_odd) // 2) + 1
        total_candidates = odd_count + (1 if has_two else 0)
        if total_candidates == 0:
            raise ValueError("odd-only sampling range has no odd candidate")
        numbers = []
        while len(numbers) < count:
            draw = rng.randrange(total_candidates)
            if has_two and draw == 0:
                numbers.append(2)
            else:
                odd_index = draw - 1 if has_two else draw
                numbers.append(first_odd + (2 * odd_index))
        return numbers

    numbers: list[int] = []
    while len(numbers) < count:
        numbers.append(rng.randrange(low, high))
    return numbers


def labels_for(numbers: Iterable[int], labeler: PrimeLabeler) -> np.ndarray:
    return np.asarray([1.0 if labeler.is_prime(n) else 0.0 for n in numbers], dtype=np.float64)


def bit_matrix(
    numbers: Iterable[int],
    bit_width: int,
    residue_moduli: tuple[int, ...] = (),
) -> np.ndarray:
    return np.vstack([feature_vector(n, bit_width, residue_moduli) for n in numbers])


def train_tiny_bit_logistic(
    *,
    numbers: list[int],
    labels: np.ndarray,
    bit_width: int,
    residue_moduli: tuple[int, ...],
    epochs: int,
    learning_rate: float,
    positive_weight: float,
) -> TinyBitLogisticModel:
    if epochs <= 0:
        raise ValueError("epochs must be positive")
    if learning_rate <= 0.0:
        raise ValueError("learning_rate must be positive")
    if positive_weight <= 0.0:
        raise ValueError("positive_weight must be positive")
    x = bit_matrix(numbers, bit_width, residue_moduli)
    y = labels
    weights = np.zeros(x.shape[1], dtype=np.float64)
    bias = 0.0

    sample_weights = np.where(y > 0.5, positive_weight, 1.0)
    sample_weights /= float(np.mean(sample_weights))
    n = float(len(y))
    for _ in range(epochs):
        logits = x @ weights + bias
        probabilities = 1.0 / (1.0 + np.exp(-np.clip(logits, -60.0, 60.0)))
        error = (probabilities - y) * sample_weights
        grad_w = (x.T @ error) / n
        grad_b = float(np.sum(error) / n)
        weights -= learning_rate * grad_w
        bias -= learning_rate * grad_b

    return TinyBitLogisticModel(
        bit_width=bit_width,
        weights=tuple(float(value) for value in weights),
        bias=float(bias),
        residue_moduli=residue_moduli,
    )


def evaluate_model(
    model: TinyBitLogisticModel,
    *,
    numbers: list[int],
    labels: np.ndarray,
    threshold: float,
) -> dict[str, object]:
    scores = np.asarray([model.score(n) for n in numbers], dtype=np.float64)
    predictions = scores >= threshold
    truth = labels > 0.5
    tp = int(np.sum(predictions & truth))
    fp = int(np.sum(predictions & ~truth))
    tn = int(np.sum(~predictions & ~truth))
    fn = int(np.sum(~predictions & truth))
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    f1 = safe_div(2.0 * precision * recall, precision + recall)
    return {
        "threshold": threshold,
        "sample_count": len(numbers),
        "prime_count": int(np.sum(truth)),
        "composite_count": int(np.sum(~truth)),
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "accuracy": safe_div(tp + tn, len(numbers)),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mean_prime_score": float(np.mean(scores[truth])) if np.any(truth) else None,
        "mean_composite_score": float(np.mean(scores[~truth])) if np.any(~truth) else None,
    }


def safe_div(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else float(numerator / denominator)


def candidate_sequence(start: int, window: int) -> list[int]:
    return [n for n in range(max(2, start), start + window) if n == 2 or n % 2 == 1]


def hybrid_prime_search(
    model: TinyBitLogisticModel,
    labeler: PrimeLabeler,
    *,
    start: int,
    window: int,
    top_k: int,
) -> dict[str, object]:
    if window <= 0:
        raise ValueError("search window must be positive")
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    candidates = candidate_sequence(start, window)
    scored = sorted(
        ((model.score(n), n) for n in candidates),
        key=lambda item: (-item[0], item[1]),
    )
    checked: list[int] = []
    found: int | None = None
    used_fallback = False
    for _, candidate in scored[:top_k]:
        checked.append(candidate)
        if labeler.is_prime(candidate):
            found = candidate
            break
    if found is None:
        used_fallback = True
        checked_set = set(checked)
        for candidate in candidates:
            if candidate in checked_set:
                continue
            checked.append(candidate)
            if labeler.is_prime(candidate):
                found = candidate
                break

    baseline_checked = 0
    baseline_found = None
    for candidate in candidates:
        baseline_checked += 1
        if labeler.is_prime(candidate):
            baseline_found = candidate
            break

    return {
        "search_kind": "find_any_prime_in_window",
        "start": start,
        "window": window,
        "top_k": top_k,
        "candidate_count": len(candidates),
        "reported_prime": found,
        "deterministically_verified": found is not None,
        "verified_by": labeler.name if found is not None else None,
        "used_deterministic_fallback": used_fallback,
        "hybrid_deterministic_checks": len(checked),
        "baseline_first_prime": baseline_found,
        "baseline_sequential_checks_to_first_prime": baseline_checked,
        "reported_prime_is_baseline_first_prime": found == baseline_found,
        "check_ratio_vs_sequential_first_prime": (
            safe_div(len(checked), baseline_checked) if baseline_found is not None else None
        ),
        "not_claimed": [
            "reported_prime is not claimed to be the next prime unless it equals baseline_first_prime",
            "neural score is not a primality proof",
            "hybrid check count is not a wall-clock speed claim",
        ],
    }


def hybrid_next_prime_search(
    model: TinyBitLogisticModel,
    labeler: PrimeLabeler,
    *,
    start: int,
    window: int,
    top_k: int,
) -> dict[str, object]:
    if window <= 0:
        raise ValueError("search window must be positive")
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    candidates = candidate_sequence(start, window)
    counting_labeler = CachedCountingLabeler(labeler)
    hint_candidates = candidates[:top_k]
    scored = sorted(
        ((model.score(n), n) for n in hint_candidates),
        key=lambda item: (-item[0], item[1]),
    )
    hinted_prime = None
    hinted_checks = 0
    for _, candidate in scored[:1]:
        hinted_checks += 1
        if counting_labeler.is_prime(candidate):
            hinted_prime = candidate
            break

    exact_next = None
    proof_checked = 0
    for candidate in candidates:
        proof_checked += 1
        if counting_labeler.is_prime(candidate):
            exact_next = candidate
            break

    baseline_checked = 0
    baseline_found = None
    for candidate in candidates:
        baseline_checked += 1
        if labeler.is_prime(candidate):
            baseline_found = candidate
            break

    if exact_next != baseline_found:
        raise AssertionError(
            "hybrid exact-next proof scan disagreed with deterministic baseline"
        )

    return {
        "search_kind": "exact_next_prime_in_window",
        "start": start,
        "window": window,
        "top_k": top_k,
        "candidate_count": len(candidates),
        "reported_prime": exact_next,
        "deterministically_verified": exact_next is not None,
        "exact_next_certified": exact_next is not None,
        "verified_by": labeler.name if exact_next is not None else None,
        "hinted_prime": hinted_prime,
        "hinted_prime_was_next": hinted_prime == exact_next,
        "hinted_prime_checks": hinted_checks,
        "proof_scan_checks": proof_checked,
        "hybrid_unique_deterministic_checks": counting_labeler.unique_checks,
        "baseline_first_prime": baseline_found,
        "baseline_sequential_checks_to_first_prime": baseline_checked,
        "reported_prime_is_baseline_first_prime": exact_next == baseline_found,
        "check_ratio_vs_sequential_first_prime": (
            safe_div(counting_labeler.unique_checks, baseline_checked)
            if baseline_found is not None
            else None
        ),
        "certification_rule": (
            "exact next-prime claims require deterministic verification of the "
            "reported prime and every earlier candidate in the search window"
        ),
        "not_claimed": [
            "neural ranking does not skip earlier candidates for exact next-prime claims",
            "neural score is not a primality proof",
            "a missing reported_prime means no prime was found inside this bounded window",
        ],
    }


def run_hybrid_search(
    model: TinyBitLogisticModel,
    labeler: PrimeLabeler,
    *,
    search_mode: str,
    start: int,
    window: int,
    top_k: int,
) -> dict[str, object]:
    if search_mode == "any-prime":
        return hybrid_prime_search(
            model,
            labeler,
            start=start,
            window=window,
            top_k=top_k,
        )
    if search_mode == "exact-next":
        return hybrid_next_prime_search(
            model,
            labeler,
            start=start,
            window=window,
            top_k=top_k,
        )
    raise ValueError(f"unknown search mode: {search_mode}")


def hybrid_prime_search_batch(
    model: TinyBitLogisticModel,
    labeler: PrimeLabeler,
    *,
    search_mode: str,
    start: int,
    window: int,
    top_k: int,
    runs: int,
    stride: int,
) -> list[dict[str, object]]:
    if runs <= 0:
        raise ValueError("search_runs must be positive")
    if stride <= 0:
        raise ValueError("search_stride must be positive")
    return [
        run_hybrid_search(
            model,
            labeler,
            search_mode=search_mode,
            start=start + (index * stride),
            window=window,
            top_k=top_k,
        )
        for index in range(runs)
    ]


def summarize_hybrid_prime_searches(
    searches: list[dict[str, object]],
) -> dict[str, object]:
    ratios = [
        float(search["check_ratio_vs_sequential_first_prime"])
        for search in searches
        if search["check_ratio_vs_sequential_first_prime"] is not None
    ]
    hybrid_checks = [
        int(
            search.get(
                "hybrid_deterministic_checks",
                search.get("hybrid_unique_deterministic_checks", 0),
            )
        )
        for search in searches
        if search["baseline_first_prime"] is not None
    ]
    baseline_checks = [
        int(search["baseline_sequential_checks_to_first_prime"])
        for search in searches
        if search["baseline_first_prime"] is not None
    ]
    return {
        "window_count": len(searches),
        "windows_with_prime": len(ratios),
        "verified_count": sum(
            1 for search in searches if search["deterministically_verified"]
        ),
        "fallback_count": sum(
            1 for search in searches if search["used_deterministic_fallback"]
        )
        if searches and "used_deterministic_fallback" in searches[0]
        else None,
        "hinted_prime_was_next_count": sum(
            1 for search in searches if search.get("hinted_prime_was_next") is True
        ),
        "next_prime_match_count": sum(
            1 for search in searches if search["reported_prime_is_baseline_first_prime"]
        ),
        "ordering_win_count": sum(1 for ratio in ratios if ratio < 1.0),
        "ordering_tie_count": sum(1 for ratio in ratios if ratio == 1.0),
        "ordering_loss_count": sum(1 for ratio in ratios if ratio > 1.0),
        "mean_check_ratio_vs_sequential_first_prime": (
            float(np.mean(ratios)) if ratios else None
        ),
        "median_check_ratio_vs_sequential_first_prime": (
            float(np.median(ratios)) if ratios else None
        ),
        "mean_hybrid_deterministic_checks": (
            float(np.mean(hybrid_checks)) if hybrid_checks else None
        ),
        "mean_baseline_sequential_checks_to_first_prime": (
            float(np.mean(baseline_checks)) if baseline_checks else None
        ),
    }


def hybrid_contract() -> dict[str, object]:
    return {
        "name": HYBRID_CONTRACT_NAME,
        "lean_module": "Circle.Core.Horizon",
        "theorem_ids": list(HYBRID_THEOREM_IDS),
        "lean_names": list(HYBRID_LEAN_NAMES),
        "rust_domain": "u64_exact_arithmetic",
        "neural_role": "candidate_ordering_only",
        "deterministic_prefilter": (
            "candidate prefilters are allowed only when each skipped value has "
            "a deterministic divisibility reason; the Rust exact-next lane uses "
            "a 2/3/5 wheel before neural scoring"
        ),
        "acceptance_rule": (
            "a reported prime is accepted only after deterministic verification; "
            "Rust exact-next claims use the Circle deterministic next-prime proof "
            "path, including static exact tables or verification of every earlier "
            "candidate that survives the deterministic prefilter; the neural model "
            "cannot certify primality or compositeness"
        ),
        "not_claimed": [
            "model weights are not theorem proved",
            "false positives and false negatives are expected and measured",
            "no candidate may be silently discarded in exact count/enumeration workflows",
        ],
    }


def run_experiment(args: argparse.Namespace) -> dict[str, object]:
    labeler = build_labeler(args)
    validate_bit_width(args)
    residue_moduli = parse_residue_moduli(args.residue_moduli)
    train_numbers = sample_numbers(
        low=args.train_low,
        high=args.train_high,
        count=args.train_samples,
        seed=args.seed,
        odd_only=args.odd_only,
    )
    eval_numbers = sample_numbers(
        low=args.eval_low,
        high=args.eval_high,
        count=args.eval_samples,
        seed=args.seed + 1,
        odd_only=args.odd_only,
    )
    start = time.perf_counter()
    train_labels = labels_for(train_numbers, labeler)
    eval_labels = labels_for(eval_numbers, labeler)
    model = train_tiny_bit_logistic(
        numbers=train_numbers,
        labels=train_labels,
        bit_width=args.bit_width,
        residue_moduli=residue_moduli,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        positive_weight=args.positive_weight,
    )
    training_seconds = time.perf_counter() - start
    evaluation = evaluate_model(
        model,
        numbers=eval_numbers,
        labels=eval_labels,
        threshold=args.threshold,
    )
    search = None
    if args.search_start is not None:
        searches = hybrid_prime_search_batch(
            model,
            labeler,
            search_mode=args.search_mode,
            start=args.search_start,
            window=args.search_window,
            top_k=args.top_k,
            runs=args.search_runs,
            stride=args.search_stride,
        )
        if len(searches) == 1:
            search = searches[0]
        else:
            search = {
                "search_kind": (
                    "multi_window_find_any_prime"
                    if args.search_mode == "any-prime"
                    else "multi_window_exact_next_prime"
                ),
                "search_mode": args.search_mode,
                "start": args.search_start,
                "window": args.search_window,
                "top_k": args.top_k,
                "runs": args.search_runs,
                "stride": args.search_stride,
                "summary": summarize_hybrid_prime_searches(searches),
                "windows": searches,
                "not_claimed": [
                    "aggregate check ratios are not wall-clock speed claims",
                    "reported primes are not next-prime claims unless each window matches baseline_first_prime",
                    "neural score is not a primality proof",
                ],
            }
    return {
        "schema_id": SCHEMA_ID,
        "label_source": labeler.name,
        "_trained_model_text": model.to_text(),
        "model": model.to_json(),
        "training": {
            "train_low": args.train_low,
            "train_high": args.train_high,
            "train_samples": args.train_samples,
            "prime_count": int(np.sum(train_labels > 0.5)),
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "positive_weight": args.positive_weight,
            "residue_moduli": list(residue_moduli),
            "seconds": training_seconds,
        },
        "evaluation": evaluation,
        "hybrid_search": search,
        "hybrid_proof_contract": hybrid_contract(),
    }


def build_labeler(args: argparse.Namespace) -> PrimeLabeler:
    if args.labeler == "builtin-mr64":
        return BuiltinMr64Labeler()
    if args.labeler == "circle-prime":
        binary = args.circle_prime_bin
        if not binary.exists():
            raise FileNotFoundError(f"circle-prime binary not found: {binary}")
        return CirclePrimeCliLabeler(binary)
    raise ValueError(f"unknown labeler: {args.labeler}")


def parse_residue_moduli(raw: str) -> tuple[int, ...]:
    if raw.strip() == "":
        return ()
    moduli = []
    seen = set()
    for item in raw.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        try:
            modulus = int(stripped)
        except ValueError as exc:
            raise ValueError(f"residue modulus must be an integer: {stripped!r}") from exc
        if modulus <= 1:
            raise ValueError("residue moduli must be greater than 1")
        if modulus not in seen:
            moduli.append(modulus)
            seen.add(modulus)
    return tuple(moduli)


def validate_bit_width(args: argparse.Namespace) -> None:
    max_value = max(args.train_high - 1, args.eval_high - 1)
    if args.search_start is not None:
        if args.search_runs <= 0:
            raise ValueError("search_runs must be positive")
        if args.search_stride <= 0:
            raise ValueError("search_stride must be positive")
        search_max = (
            args.search_start
            + ((args.search_runs - 1) * args.search_stride)
            + args.search_window
            - 1
        )
        max_value = max(max_value, search_max)
    if max_value >= 1 << args.bit_width:
        raise ValueError(
            f"bit_width={args.bit_width} cannot represent max input {max_value}; "
            "increase --bit-width"
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train/evaluate a tiny bit-level fuzzy prime classifier safely."
    )
    parser.add_argument(
        "--labeler",
        choices=["builtin-mr64", "circle-prime"],
        default="builtin-mr64",
    )
    parser.add_argument(
        "--circle-prime-bin",
        type=Path,
        default=ROOT / "target" / "debug" / binary_name("circle-prime"),
    )
    parser.add_argument("--bit-width", type=int, default=16)
    parser.add_argument("--train-low", type=int, default=2)
    parser.add_argument("--train-high", type=int, default=4096)
    parser.add_argument("--eval-low", type=int, default=4096)
    parser.add_argument("--eval-high", type=int, default=8192)
    parser.add_argument("--train-samples", type=int, default=512)
    parser.add_argument("--eval-samples", type=int, default=256)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--learning-rate", type=float, default=0.2)
    parser.add_argument("--positive-weight", type=float, default=4.0)
    parser.add_argument(
        "--residue-moduli",
        default="",
        help=(
            "Optional comma-separated moduli for tiny bit-derived residue features, "
            "for example 3,5,7,11."
        ),
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--odd-only", action="store_true", default=True)
    parser.add_argument("--include-even", dest="odd_only", action="store_false")
    parser.add_argument("--search-start", type=int)
    parser.add_argument(
        "--search-mode",
        choices=["any-prime", "exact-next"],
        default="any-prime",
    )
    parser.add_argument("--search-window", type=int, default=256)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--search-runs", type=int, default=1)
    parser.add_argument("--search-stride", type=int, default=4096)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--model-out", type=Path)
    parser.add_argument("--summary", action="store_true")
    return parser.parse_args(argv)


def binary_name(name: str) -> str:
    return f"{name}.exe" if sys.platform == "win32" else name


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = run_experiment(args)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: prime fuzzy hybrid experiment failed: {exc}", file=sys.stderr)
        return 1
    model_text = str(report.pop("_trained_model_text"))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered)
    if args.model_out is not None:
        args.model_out.parent.mkdir(parents=True, exist_ok=True)
        args.model_out.write_text(model_text)
    if args.summary:
        evaluation = report["evaluation"]
        search = report.get("hybrid_search")
        print(
            "prime fuzzy hybrid: "
            f"f1={evaluation['f1']:.3f}, "
            f"precision={evaluation['precision']:.3f}, "
            f"recall={evaluation['recall']:.3f}, "
            f"labeler={report['label_source']}"
        )
        if isinstance(search, dict):
            if "summary" in search:
                search_summary = search["summary"]
                mean_ratio = search_summary[
                    "mean_check_ratio_vs_sequential_first_prime"
                ]
                mean_ratio_text = "n/a" if mean_ratio is None else f"{mean_ratio:.3f}"
                print(
                    "hybrid search batch: "
                    f"windows={search_summary['window_count']}, "
                    f"wins={search_summary['ordering_win_count']}, "
                    f"ties={search_summary['ordering_tie_count']}, "
                    f"losses={search_summary['ordering_loss_count']}, "
                    f"mean_check_ratio={mean_ratio_text}"
                )
            else:
                print(
                    "hybrid search: "
                    f"reported_prime={search['reported_prime']}, "
                    f"verified={search['deterministically_verified']}, "
                    f"checks={search['hybrid_deterministic_checks']}, "
                    f"fallback={search['used_deterministic_fallback']}"
                )
    elif args.json_out is None:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
