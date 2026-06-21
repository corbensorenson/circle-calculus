from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.benchmark_prime_external_controls import (
    circle_prime_metadata,
    external_tool_metadata,
    file_fingerprint,
    utc_now,
)
from scripts.benchmark_prime_external_next import (
    NextBenchRow,
    NextMeasurement,
    PrimeLineServerClient,
    build_circle_prime,
    build_primecount_next_server,
    build_primesieve_iterator_next_server,
    build_primesieve_next_server,
    circle_next_server_measurement,
    emit_csv,
    emit_samples,
    measure_interleaved_next,
    parse_starts,
    primecount_next_server_measurement,
    primesieve_generate_server_measurement,
    primesieve_iterator_server_measurement,
    require_cargo,
    speedup_row,
)
from scripts.prime_fuzzy_hybrid import (
    BuiltinMr64Labeler,
    DEFAULT_RESIDUE_MODULI,
    TinyBitLogisticModel,
    hybrid_contract,
    hybrid_prime_search,
    labels_for,
    parse_residue_moduli,
    sample_numbers,
    train_tiny_bit_logistic,
)


DEFAULT_STARTS = "4295061710,4295087310,4295135570"
SCHEMA_ID = "circle_calculus.prime_fuzzy_hybrid_any_benchmark.v0"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Short any-prime benchmark for the fuzzy hybrid prime lane."
    )
    parser.add_argument("--starts", default=DEFAULT_STARTS)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--warmup-rounds", type=int, default=1)
    parser.add_argument("--bit-width", type=int, default=33)
    parser.add_argument("--train-low", type=int, default=4_294_900_000)
    parser.add_argument("--train-high", type=int, default=4_295_300_000)
    parser.add_argument("--train-samples", type=int, default=4096)
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--learning-rate", type=float, default=0.2)
    parser.add_argument("--positive-weight", type=float, default=4.0)
    parser.add_argument(
        "--residue-moduli",
        default=",".join(str(modulus) for modulus in DEFAULT_RESIDUE_MODULI),
    )
    parser.add_argument("--search-window", type=int, default=2048)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--score-limit", type=int, default=64)
    parser.add_argument("--external-threads", type=int, default=0)
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--cxx", default="c++")
    parser.add_argument("--primesieve-include-dir", type=Path)
    parser.add_argument("--primesieve-lib-dir", type=Path)
    parser.add_argument("--primecount-include-dir", type=Path)
    parser.add_argument("--primecount-lib-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sample-output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument(
        "--rust-model-output",
        type=Path,
        default=REPO_ROOT / "target" / "prime-controls" / "prime-fuzzy-hybrid-model.txt",
    )
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    validate_args(args, parser)
    starts = parse_starts(args.starts)
    residue_moduli = parse_residue_moduli(args.residue_moduli)
    validate_bit_width(args, starts)

    started_at_utc = utc_now()
    labeler = BuiltinMr64Labeler()
    model, training = train_model(args, labeler, residue_moduli)
    args.rust_model_output.parent.mkdir(parents=True, exist_ok=True)
    args.rust_model_output.write_text(model.to_text())

    cargo = require_cargo()
    circle_prime = build_circle_prime(cargo)
    primesieve_binary = shutil.which("primesieve")
    primecount_binary = shutil.which("primecount")
    primesieve_server = build_primesieve_next_server(args)
    primesieve_iterator_server = build_primesieve_iterator_next_server(args)
    primecount_server = build_primecount_next_server(args)

    rows: list[NextBenchRow] = []
    samples = []
    for start in starts:
        measurements = [
            python_hybrid_any_measurement(
                model=model,
                start=start,
                window=args.search_window,
                top_k=args.top_k,
                batch_size=args.batch_size,
            ),
            rust_fuzzy_any_server_measurement(
                binary=circle_prime,
                model_path=args.rust_model_output,
                start=start,
                window=args.search_window,
                top_k=args.top_k,
                score_limit=args.score_limit,
                batch_size=args.batch_size,
            ),
            deterministic_python_any_measurement(
                start=start,
                window=args.search_window,
                batch_size=args.batch_size,
            ),
            circle_next_server_measurement(circle_prime, start, args.batch_size),
            primesieve_generate_server_measurement(
                primesieve_server,
                start,
                args.batch_size,
            ),
            primesieve_iterator_server_measurement(
                primesieve_iterator_server,
                start,
                args.batch_size,
            ),
            primecount_next_server_measurement(
                primecount_server,
                start,
                args.batch_size,
                args.external_threads,
            ),
        ]
        try:
            timing_rows, timing_samples = measure_interleaved_next(
                measurements,
                args.rounds,
                warmup_rounds=args.warmup_rounds,
            )
        finally:
            for measurement in measurements:
                if measurement.close is not None:
                    measurement.close()
        assert_any_prime_rows(timing_rows, start, args.search_window, labeler)
        rows.extend(timing_rows)
        samples.extend(timing_samples)
        hybrid_rows = [
            row
            for row in timing_rows
            if row.name
            in {
                "circle_fuzzy_hybrid_python_any_prime",
                "circle_fuzzy_hybrid_rust_server_any_prime",
            }
        ]
        for hybrid_row in hybrid_rows:
            for baseline_row in timing_rows:
                if baseline_row.name != hybrid_row.name:
                    rows.append(speedup_row(hybrid_row, baseline_row))

    emit_csv(rows, args.output)
    emit_samples(samples, args.sample_output)
    metadata = build_metadata(
        args=args,
        starts=starts,
        started_at_utc=started_at_utc,
        cargo=cargo,
        circle_prime=circle_prime,
        primesieve_binary=primesieve_binary,
        primecount_binary=primecount_binary,
        primesieve_server=primesieve_server,
        primesieve_iterator_server=primesieve_iterator_server,
        primecount_server=primecount_server,
        model=model,
        training=training,
        rust_model_output=args.rust_model_output,
        row_count=len(rows),
    )
    if args.metadata_output is not None:
        args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
        args.metadata_output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        print(f"wrote fuzzy hybrid any-prime metadata JSON to {args.metadata_output}")
    if args.summary:
        print_summary(rows)
    return 0


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.rounds <= 0:
        parser.error("--rounds must be positive")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if args.warmup_rounds < 0:
        parser.error("--warmup-rounds must be nonnegative")
    if args.search_window <= 0:
        parser.error("--search-window must be positive")
    if args.top_k <= 0:
        parser.error("--top-k must be positive")
    if args.score_limit <= 0:
        parser.error("--score-limit must be positive")
    if args.external_threads < 0:
        parser.error("--external-threads must be nonnegative")


def validate_bit_width(args: argparse.Namespace, starts: list[int]) -> None:
    max_value = max(args.train_high - 1, max(starts) + args.search_window - 1)
    if max_value >= 1 << args.bit_width:
        raise ValueError(
            f"bit_width={args.bit_width} cannot represent max input {max_value}; "
            "increase --bit-width"
        )


def train_model(
    args: argparse.Namespace,
    labeler: BuiltinMr64Labeler,
    residue_moduli: tuple[int, ...],
) -> tuple[TinyBitLogisticModel, dict[str, Any]]:
    train_numbers = sample_numbers(
        low=args.train_low,
        high=args.train_high,
        count=args.train_samples,
        seed=1729,
        odd_only=True,
    )
    train_labels = labels_for(train_numbers, labeler)
    model = train_tiny_bit_logistic(
        numbers=train_numbers,
        labels=train_labels,
        bit_width=args.bit_width,
        residue_moduli=residue_moduli,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        positive_weight=args.positive_weight,
    )
    return model, {
        "label_source": labeler.name,
        "train_low": args.train_low,
        "train_high": args.train_high,
        "train_samples": args.train_samples,
        "prime_count": int(np.sum(train_labels > 0.5)),
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "positive_weight": args.positive_weight,
        "residue_moduli": list(residue_moduli),
    }


def python_hybrid_any_measurement(
    *,
    model: TinyBitLogisticModel,
    start: int,
    window: int,
    top_k: int,
    batch_size: int,
) -> NextMeasurement:
    labeler = BuiltinMr64Labeler()
    probe = hybrid_prime_search(
        model,
        labeler,
        start=start,
        window=window,
        top_k=top_k,
    )
    expected = probe["reported_prime"]
    if expected is None:
        raise ValueError(f"Python hybrid any-prime found no prime for start={start}")
    assert_valid_any_prime(int(expected), start, window, labeler)

    def run_once() -> int:
        result = 0
        for _ in range(batch_size):
            search = hybrid_prime_search(
                model,
                labeler,
                start=start,
                window=window,
                top_k=top_k,
            )
            result = int(search["reported_prime"])
            if result != expected:
                raise AssertionError(
                    f"Python hybrid any-prime result changed for start={start}: "
                    f"expected {expected}, got {result}"
                )
        return result

    return NextMeasurement(
        name="circle_fuzzy_hybrid_python_any_prime",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=int(probe["hybrid_deterministic_checks"]),
        run_once=run_once,
    )


def rust_fuzzy_any_server_measurement(
    *,
    binary: Path,
    model_path: Path,
    start: int,
    window: int,
    top_k: int,
    score_limit: int,
    batch_size: int,
) -> NextMeasurement:
    probe = rust_fuzzy_probe(
        binary=binary,
        model_path=model_path,
        start=start,
        window=window,
        top_k=top_k,
        score_limit=score_limit,
    )
    expected = probe.get("reported_prime")
    if expected is None:
        raise ValueError(f"Rust fuzzy any-prime found no prime for start={start}")
    labeler = BuiltinMr64Labeler()
    assert_valid_any_prime(int(expected), start, window, labeler)
    client = PrimeLineServerClient(
        [
            str(binary),
            "fuzzy-server",
            str(model_path),
            "--mode",
            "any-prime",
            "--window",
            str(window),
            "--top-k",
            str(top_k),
            "--score-limit",
            str(score_limit),
        ],
        "Circle Rust fuzzy hybrid any-prime server",
    )

    def run_once() -> int:
        results = client.next_primes(start, batch_size)
        for result in results:
            if result != expected:
                raise AssertionError(
                    f"Rust fuzzy any-prime result changed for start={start}: "
                    f"expected {expected}, got {result}"
                )
        return results[-1] if results else 0

    return NextMeasurement(
        name="circle_fuzzy_hybrid_rust_server_any_prime",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=int(probe["hybrid_deterministic_checks"]),
        run_once=run_once,
        close=client.close,
    )


def deterministic_python_any_measurement(
    *,
    start: int,
    window: int,
    batch_size: int,
) -> NextMeasurement:
    labeler = BuiltinMr64Labeler()
    expected, candidate_count = deterministic_any_prime(labeler, start, window)

    def run_once() -> int:
        result = 0
        for _ in range(batch_size):
            result, _ = deterministic_any_prime(labeler, start, window)
            if result != expected:
                raise AssertionError(
                    f"deterministic Python any-prime result changed for start={start}: "
                    f"expected {expected}, got {result}"
                )
        return result

    return NextMeasurement(
        name="deterministic_python_mr64_any_prime",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=candidate_count,
        run_once=run_once,
    )


def rust_fuzzy_probe(
    *,
    binary: Path,
    model_path: Path,
    start: int,
    window: int,
    top_k: int,
    score_limit: int,
) -> dict[str, Any]:
    completed = subprocess.run(
        [
            str(binary),
            "fuzzy-search",
            str(model_path),
            str(start),
            "--mode",
            "any-prime",
            "--window",
            str(window),
            "--top-k",
            str(top_k),
            "--score-limit",
            str(score_limit),
            "--json",
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def deterministic_any_prime(
    labeler: BuiltinMr64Labeler,
    start: int,
    window: int,
) -> tuple[int, int]:
    checked = 0
    for candidate in wheel30_candidates(start, window):
        checked += 1
        if labeler.is_prime(candidate):
            return candidate, checked
    raise ValueError(f"no prime found in bounded window for start={start}")


def wheel30_candidates(start: int, window: int) -> list[int]:
    high = start + window
    candidates = []
    for small_prime in (2, 3, 5):
        if start <= small_prime < high:
            candidates.append(small_prime)
    first = max(start, 7)
    for candidate in range(first, high):
        if candidate % 30 in {1, 7, 11, 13, 17, 19, 23, 29}:
            candidates.append(candidate)
    return candidates


def assert_any_prime_rows(
    rows: list[NextBenchRow],
    start: int,
    window: int,
    labeler: BuiltinMr64Labeler,
) -> None:
    for row in rows:
        if row.kind == "timing":
            assert_valid_any_prime(row.result, start, window, labeler)


def assert_valid_any_prime(
    result: int,
    start: int,
    window: int,
    labeler: BuiltinMr64Labeler,
) -> None:
    if result < start or result >= start + window:
        raise AssertionError(
            f"any-prime result {result} is outside [{start}, {start + window})"
        )
    if not labeler.is_prime(result):
        raise AssertionError(f"any-prime result {result} is not prime")


def build_metadata(
    *,
    args: argparse.Namespace,
    starts: list[int],
    started_at_utc: str,
    cargo: str,
    circle_prime: Path,
    primesieve_binary: str | None,
    primecount_binary: str | None,
    primesieve_server: Path,
    primesieve_iterator_server: Path,
    primecount_server: Path,
    model: TinyBitLogisticModel,
    training: dict[str, Any],
    rust_model_output: Path,
    row_count: int,
) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "started_at_utc": started_at_utc,
        "finished_at_utc": utc_now(),
        "row_count": row_count,
        "starts": starts,
        "rounds": args.rounds,
        "batch_size": args.batch_size,
        "warmup_rounds": args.warmup_rounds,
        "search_window": args.search_window,
        "top_k": args.top_k,
        "score_limit": args.score_limit,
        "search_mode": "any-prime",
        "model": model.to_json(),
        "rust_model_output": str(rust_model_output),
        "rust_model_fingerprint": file_fingerprint(rust_model_output),
        "training": training,
        "hybrid_proof_contract": hybrid_contract(),
        "not_claimed": [
            "any-prime rows do not claim the reported prime is the next prime",
            "model weights are not theorem proved",
            "the neural model may only choose verification order",
            "exact next-prime and enumeration workflows may not discard candidates by score",
        ],
        "tools": {
            "circle_prime": circle_prime_metadata(cargo, circle_prime),
            "primesieve": external_tool_metadata(
                "primesieve",
                primesieve_binary,
                ["--version"],
            ),
            "primecount": external_tool_metadata(
                "primecount",
                primecount_binary,
                ["--version"],
            ),
            "primesieve_library_server": {
                "available": True,
                "path": str(primesieve_server),
                "binary": file_fingerprint(primesieve_server),
                "method": "primesieve_generate_n_primes(1, START, UINT64_PRIMES)",
            },
            "primesieve_iterator_server": {
                "available": True,
                "path": str(primesieve_iterator_server),
                "binary": file_fingerprint(primesieve_iterator_server),
                "method": "primesieve::iterator.jump_to(START).next_prime()",
            },
            "primecount_library_server": {
                "available": True,
                "path": str(primecount_server),
                "binary": file_fingerprint(primecount_server),
                "method": "primecount_pi(START-1) then primecount_nth_prime(pi+1)",
            },
        },
    }


def print_summary(rows: list[NextBenchRow]) -> None:
    speedups = [
        row
        for row in rows
        if row.kind == "speedup"
        and row.name
        in {
            "circle_fuzzy_hybrid_python_any_prime",
            "circle_fuzzy_hybrid_rust_server_any_prime",
        }
    ]
    for row in speedups:
        print(
            "fuzzy hybrid any-prime: "
            f"name={row.name}, start={row.start}, baseline={row.baseline}, "
            f"median_speedup={row.median_speedup}, best_speedup={row.best_speedup}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
