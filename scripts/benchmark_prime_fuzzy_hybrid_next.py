from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
from scripts.benchmark_prime_external_controls import (
    circle_prime_metadata,
    external_tool_metadata,
    file_fingerprint,
    utc_now,
)
from scripts.prime_fuzzy_hybrid import (
    BuiltinMr64Labeler,
    DEFAULT_RESIDUE_MODULI,
    TinyBitLogisticModel,
    candidate_sequence,
    hybrid_contract,
    hybrid_next_prime_search,
    labels_for,
    parse_residue_moduli,
    sample_numbers,
    train_tiny_bit_logistic,
)


DEFAULT_STARTS = "1000000,1004096,1008192"
SCHEMA_ID = "circle_calculus.prime_fuzzy_hybrid_next_benchmark.v0"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Short exact-next benchmark for the fuzzy hybrid prime lane."
    )
    parser.add_argument("--starts", default=DEFAULT_STARTS)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--warmup-rounds", type=int, default=1)
    parser.add_argument("--bit-width", type=int, default=21)
    parser.add_argument("--train-low", type=int, default=900_000)
    parser.add_argument("--train-high", type=int, default=1_000_000)
    parser.add_argument("--train-samples", type=int, default=2048)
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--learning-rate", type=float, default=0.2)
    parser.add_argument("--positive-weight", type=float, default=4.0)
    parser.add_argument(
        "--residue-moduli",
        default=",".join(str(modulus) for modulus in DEFAULT_RESIDUE_MODULI),
    )
    parser.add_argument("--search-window", type=int, default=512)
    parser.add_argument("--top-k", type=int, default=8)
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
            hybrid_exact_next_measurement(
                model=model,
                start=start,
                window=args.search_window,
                top_k=args.top_k,
                batch_size=args.batch_size,
            ),
            rust_fuzzy_next_server_measurement(
                binary=circle_prime,
                model_path=args.rust_model_output,
                start=start,
                window=args.search_window,
                top_k=args.top_k,
                batch_size=args.batch_size,
            ),
            deterministic_python_next_measurement(
                start=start,
                window=args.search_window,
                batch_size=args.batch_size,
            ),
            circle_next_server_measurement(
                circle_prime,
                start,
                args.batch_size,
            ),
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
        assert_same_next_prime(timing_rows, start)
        rows.extend(timing_rows)
        samples.extend(timing_samples)
        hybrid_rows = [
            row
            for row in timing_rows
            if row.name
            in {
                "circle_fuzzy_hybrid_python_exact_next",
                "circle_fuzzy_hybrid_rust_server_exact_next",
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
        print(f"wrote fuzzy hybrid next-prime metadata JSON to {args.metadata_output}")
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


def hybrid_exact_next_measurement(
    *,
    model: TinyBitLogisticModel,
    start: int,
    window: int,
    top_k: int,
    batch_size: int,
) -> NextMeasurement:
    labeler = BuiltinMr64Labeler()
    probe = hybrid_next_prime_search(
        model,
        labeler,
        start=start,
        window=window,
        top_k=top_k,
    )
    expected = probe["reported_prime"]
    if expected is None:
        raise ValueError(f"hybrid exact-next found no prime in window for start={start}")

    def run_once() -> int:
        result = 0
        for _ in range(batch_size):
            search = hybrid_next_prime_search(
                model,
                labeler,
                start=start,
                window=window,
                top_k=top_k,
            )
            result = int(search["reported_prime"])
            if result != expected:
                raise AssertionError(
                    f"hybrid exact-next result changed for start={start}: "
                    f"expected {expected}, got {result}"
                )
        return result

    return NextMeasurement(
        name="circle_fuzzy_hybrid_python_exact_next",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=int(probe["baseline_sequential_checks_to_first_prime"]),
        run_once=run_once,
    )


def deterministic_python_next_measurement(
    *,
    start: int,
    window: int,
    batch_size: int,
) -> NextMeasurement:
    labeler = BuiltinMr64Labeler()
    expected, candidate_count = deterministic_next_prime(labeler, start, window)

    def run_once() -> int:
        result = 0
        for _ in range(batch_size):
            result, _ = deterministic_next_prime(labeler, start, window)
            if result != expected:
                raise AssertionError(
                    f"deterministic Python next result changed for start={start}: "
                    f"expected {expected}, got {result}"
                )
        return result

    return NextMeasurement(
        name="deterministic_python_mr64_next_prime",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=candidate_count,
        run_once=run_once,
    )


def rust_fuzzy_next_server_measurement(
    *,
    binary: Path,
    model_path: Path,
    start: int,
    window: int,
    top_k: int,
    batch_size: int,
) -> NextMeasurement:
    expected, candidate_count = deterministic_next_prime(BuiltinMr64Labeler(), start, window)
    client = PrimeLineServerClient(
        [
            str(binary),
            "fuzzy-server",
            str(model_path),
            "--mode",
            "exact-next",
            "--window",
            str(window),
            "--top-k",
            str(top_k),
        ],
        "Circle Rust fuzzy hybrid exact-next server",
    )

    def run_once() -> int:
        results = client.next_primes(start, batch_size)
        for result in results:
            if result != expected:
                raise AssertionError(
                    f"Rust fuzzy exact-next result changed for start={start}: "
                    f"expected {expected}, got {result}"
                )
        return results[-1] if results else 0

    return NextMeasurement(
        name="circle_fuzzy_hybrid_rust_server_exact_next",
        start=start,
        batch_size=batch_size,
        threads=1,
        requested_threads=1,
        candidate_count=candidate_count,
        run_once=run_once,
        close=client.close,
    )


def deterministic_next_prime(
    labeler: BuiltinMr64Labeler,
    start: int,
    window: int,
) -> tuple[int, int]:
    for index, candidate in enumerate(candidate_sequence(start, window), start=1):
        if labeler.is_prime(candidate):
            return candidate, index
    raise ValueError(f"no prime found in bounded window for start={start}")


def assert_same_next_prime(rows: list[NextBenchRow], start: int) -> None:
    results = {row.result for row in rows if row.kind == "timing"}
    if len(results) != 1:
        rendered = ", ".join(f"{row.name}={row.result}" for row in rows)
        raise AssertionError(f"next-prime mismatch for start={start}: {rendered}")


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
        "model": model.to_json(),
        "rust_model_output": str(rust_model_output),
        "rust_model_fingerprint": file_fingerprint(rust_model_output),
        "training": training,
        "hybrid_proof_contract": hybrid_contract(),
        "not_claimed": [
            "the Python hybrid row is not a Rust implementation speed claim",
            "the Rust hybrid row is a current implementation measurement, not proof that weights are useful",
            "exact-next acceptance still requires deterministic verification of earlier candidates",
            "model weights are not theorem proved",
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
            "circle_fuzzy_hybrid_python_exact_next",
            "circle_fuzzy_hybrid_rust_server_exact_next",
        }
    ]
    for row in speedups:
        print(
            "fuzzy hybrid exact-next: "
            f"name={row.name}, start={row.start}, baseline={row.baseline}, "
            f"median_speedup={row.median_speedup}, best_speedup={row.best_speedup}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
