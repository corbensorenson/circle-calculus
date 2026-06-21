from __future__ import annotations

import argparse
import csv
import json
import shutil
import statistics
import subprocess
import sys
import time
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

import sympy


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "sidecars" / "PRIME_ENGINE" / "results"
SCHEMA_ID = "circle_calculus.prime_bigint_controls.v0"

T = TypeVar("T")


@dataclass(frozen=True)
class PrimeCase:
    name: str
    n: int
    expected_prime: bool


@dataclass(frozen=True)
class NextCase:
    name: str
    start: int


@dataclass(frozen=True)
class SampleSet:
    result: object
    samples_ms: list[float]

    @property
    def median_ms(self) -> float:
        return statistics.median(self.samples_ms)

    @property
    def min_ms(self) -> float:
        return min(self.samples_ms)

    @property
    def max_ms(self) -> float:
        return max(self.samples_ms)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark arbitrary-precision Circle probable-prime paths against "
            "OpenSSL BIGNUM and SymPy controls."
        )
    )
    parser.add_argument(
        "--circle-prime-bin",
        type=Path,
        default=ROOT / "target" / "release" / "circle-prime",
        help="circle-prime binary with big-test/big-next support.",
    )
    parser.add_argument(
        "--openssl-bin",
        default=shutil.which("openssl") or "openssl",
        help="OpenSSL executable used for prime checks.",
    )
    parser.add_argument(
        "--bench-rounds",
        type=int,
        default=3,
        help="Measured repetitions per engine/case.",
    )
    parser.add_argument(
        "--warmup-rounds",
        type=int,
        default=1,
        help="Unmeasured warmup repetitions per engine/case.",
    )
    parser.add_argument(
        "--mr-rounds",
        type=int,
        default=16,
        help="Miller-Rabin rounds for Circle and OpenSSL prime checks.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=4096,
        help="Maximum wheel candidates for Circle big-next searches.",
    )
    parser.add_argument(
        "--candidate-window",
        type=int,
        default=512,
        help="Candidate window for Circle big-fuzzy-search smoke rows.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=16,
        help="Top scored candidates for Circle big-fuzzy-search smoke rows.",
    )
    parser.add_argument(
        "--score-limit",
        type=int,
        default=128,
        help="Scored prefix budget for Circle big-fuzzy-search smoke rows.",
    )
    parser.add_argument(
        "--server-batch-size",
        type=int,
        default=16,
        help=(
            "Repeated requests sent per measured sample to persistent Circle "
            "BigUint servers; timings are reported per request."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "prime_bigint_controls_latest.csv",
        help="CSV output path.",
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=RESULTS_DIR / "prime_bigint_controls_latest.json",
        help="JSON metadata output path.",
    )
    parser.add_argument("--summary", action="store_true", help="Print a concise table.")
    return parser.parse_args()


def prime_cases() -> list[PrimeCase]:
    return [
        PrimeCase("mersenne_127_prime", (1 << 127) - 1, True),
        PrimeCase("mersenne_127_composite", (1 << 127) + 1, False),
        PrimeCase("curve25519_prime", (1 << 255) - 19, True),
        PrimeCase("secp256k1_prime", (1 << 256) - (1 << 32) - 977, True),
        PrimeCase("two256_composite", 1 << 256, False),
        PrimeCase("mersenne_521_prime", (1 << 521) - 1, True),
    ]


def next_cases() -> list[NextCase]:
    return [
        NextCase("next_at_2_127", 1 << 127),
        NextCase("next_near_curve25519", (1 << 255) - 1024),
    ]


def timed(
    fn: Callable[[], T],
    *,
    warmup_rounds: int,
    bench_rounds: int,
    sample_divisor: int = 1,
) -> SampleSet:
    if warmup_rounds < 0 or bench_rounds <= 0 or sample_divisor <= 0:
        raise ValueError("warmup_rounds must be >= 0 and bench_rounds must be positive")
    last: object = None
    for _ in range(warmup_rounds):
        last = fn()
    samples = []
    for _ in range(bench_rounds):
        started = time.perf_counter_ns()
        last = fn()
        samples.append(((time.perf_counter_ns() - started) / 1_000_000.0) / sample_divisor)
    return SampleSet(last, samples)


class LineServer:
    def __init__(self, argv: list[str]) -> None:
        self.argv = argv
        self.process = subprocess.Popen(
            argv,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError(f"failed to open line server pipes: {argv}")

    def request(self, value: int, count: int) -> list[str]:
        if count <= 0:
            raise ValueError("server request count must be positive")
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.process.stdin.write(f"{value} {count}\n")
        self.process.stdin.flush()
        lines = []
        for _ in range(count):
            line = self.process.stdout.readline()
            if line == "":
                stderr = ""
                if self.process.stderr is not None:
                    stderr = self.process.stderr.read()
                raise RuntimeError(
                    f"server exited while reading response from {self.argv}: {stderr}"
                )
            lines.append(line.strip())
        return lines

    def close(self) -> None:
        if self.process.poll() is None and self.process.stdin is not None:
            try:
                self.process.stdin.write("quit\n")
                self.process.stdin.flush()
            except BrokenPipeError:
                pass
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def __enter__(self) -> "LineServer":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()


def run_circle_json(binary: Path, *args: str) -> dict[str, object]:
    completed = subprocess.run(
        [str(binary), *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def circle_big_test(binary: Path, n: int, mr_rounds: int) -> bool:
    payload = run_circle_json(
        binary, "big-test", str(n), "--rounds", str(mr_rounds), "--json"
    )
    return payload["status"] in {"prime", "probable_prime"}


def circle_big_test_server(server: LineServer, n: int, batch_size: int) -> bool:
    lines = server.request(n, batch_size)
    if any(line != lines[0] for line in lines):
        raise RuntimeError(f"big-test-server returned inconsistent batch: {lines}")
    if lines[0] in {"prime", "probable_prime"}:
        return True
    if lines[0] == "composite":
        return False
    raise RuntimeError(f"could not parse big-test-server response: {lines[0]!r}")


def circle_big_next(binary: Path, start: int, mr_rounds: int, max_candidates: int) -> int | None:
    payload = run_circle_json(
        binary,
        "big-next",
        str(start),
        "--rounds",
        str(mr_rounds),
        "--max-candidates",
        str(max_candidates),
        "--json",
    )
    prime = payload.get("prime")
    return int(prime) if prime is not None else None


def circle_big_next_server(server: LineServer, start: int, batch_size: int) -> int | None:
    lines = server.request(start, batch_size)
    if any(line != lines[0] for line in lines):
        raise RuntimeError(f"big-next-server returned inconsistent batch: {lines}")
    return None if lines[0] == "none" else int(lines[0])


def circle_big_fuzzy_any(
    binary: Path,
    model: Path,
    start: int,
    mr_rounds: int,
    candidate_window: int,
    top_k: int,
    score_limit: int,
) -> int | None:
    payload = run_circle_json(
        binary,
        "big-fuzzy-search",
        str(model),
        str(start),
        "--candidate-window",
        str(candidate_window),
        "--top-k",
        str(top_k),
        "--score-limit",
        str(score_limit),
        "--rounds",
        str(mr_rounds),
        "--json",
    )
    prime = payload.get("reported_prime")
    return int(prime) if prime is not None else None


def circle_big_fuzzy_any_server(
    server: LineServer,
    start: int,
    batch_size: int,
) -> int | None:
    lines = server.request(start, batch_size)
    if any(line != lines[0] for line in lines):
        raise RuntimeError(f"big-fuzzy-server returned inconsistent batch: {lines}")
    return None if lines[0] == "none" else int(lines[0])


def openssl_prime(binary: str, n: int, mr_rounds: int) -> bool:
    completed = subprocess.run(
        [binary, "prime", "-checks", str(mr_rounds), str(n)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    out = completed.stdout.strip()
    if out.endswith(" is prime"):
        return True
    if out.endswith(" is not prime"):
        return False
    raise RuntimeError(f"could not parse OpenSSL prime output: {out!r}")


def sympy_next_prime_at_or_above(start: int) -> int:
    if sympy.isprime(start):
        return start
    return int(sympy.nextprime(start))


def write_big_fuzzy_model(path: Path, bit_width: int) -> None:
    residue_moduli = [7, 11, 13, 17, 19, 23, 29, 31]
    weights = [0.0] * bit_width + [1.0] * len(residue_moduli)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "circle_fuzzy_model_v0",
                f"bit_width {bit_width}",
                "residue_moduli " + ",".join(str(modulus) for modulus in residue_moduli),
                "weights " + ",".join(f"{weight:.17g}" for weight in weights),
                "bias 0",
                "",
            ]
        )
    )


def file_fingerprint(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": path.stat().st_size,
        "mtime_ns": path.stat().st_mtime_ns,
    }


def tool_version(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"unavailable: {exc}"
    return (completed.stdout or completed.stderr).strip().splitlines()[0]


def add_row(
    rows: list[dict[str, object]],
    *,
    operation: str,
    case: str,
    bits: int,
    engine: str,
    sample_set: SampleSet,
    expected: object,
    agreed: bool,
    mr_rounds: int,
) -> None:
    rows.append(
        {
            "operation": operation,
            "case": case,
            "bits": bits,
            "engine": engine,
            "result": str(sample_set.result),
            "expected": str(expected),
            "agreed": agreed,
            "mr_rounds": mr_rounds,
            "rounds": len(sample_set.samples_ms),
            "median_ms": f"{sample_set.median_ms:.6f}",
            "min_ms": f"{sample_set.min_ms:.6f}",
            "max_ms": f"{sample_set.max_ms:.6f}",
        }
    )


def main() -> int:
    args = parse_args()
    if not args.circle_prime_bin.exists():
        raise SystemExit(
            f"circle-prime binary not found at {args.circle_prime_bin}; "
            "build with `cargo build --release -p circle-prime --bin circle-prime`"
        )
    if args.mr_rounds <= 0:
        raise SystemExit("--mr-rounds must be positive")
    if args.server_batch_size <= 0:
        raise SystemExit("--server-batch-size must be positive")

    max_bits = max([case.n.bit_length() for case in prime_cases()] + [521])
    model_path = ROOT / "target" / "prime-controls" / "prime-big-fuzzy-model.txt"
    write_big_fuzzy_model(model_path, max_bits)

    rows: list[dict[str, object]] = []
    failures: list[str] = []

    with ExitStack() as stack:
        circle_test_server = stack.enter_context(
            LineServer(
                [
                    str(args.circle_prime_bin),
                    "big-test-server",
                    "--rounds",
                    str(args.mr_rounds),
                ]
            )
        )
        circle_next_server = stack.enter_context(
            LineServer(
                [
                    str(args.circle_prime_bin),
                    "big-next-server",
                    "--rounds",
                    str(args.mr_rounds),
                    "--max-candidates",
                    str(args.max_candidates),
                ]
            )
        )
        circle_fuzzy_server = stack.enter_context(
            LineServer(
                [
                    str(args.circle_prime_bin),
                    "big-fuzzy-server",
                    str(model_path),
                    "--candidate-window",
                    str(args.candidate_window),
                    "--top-k",
                    str(args.top_k),
                    "--score-limit",
                    str(args.score_limit),
                    "--rounds",
                    str(args.mr_rounds),
                ]
            )
        )

        for case in prime_cases():
            circle = timed(
                lambda case=case: circle_big_test(
                    args.circle_prime_bin, case.n, args.mr_rounds
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            circle_server = timed(
                lambda case=case: circle_big_test_server(
                    circle_test_server, case.n, args.server_batch_size
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
                sample_divisor=args.server_batch_size,
            )
            openssl = timed(
                lambda case=case: openssl_prime(args.openssl_bin, case.n, args.mr_rounds),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            sympy_result = timed(
                lambda case=case: bool(sympy.isprime(case.n)),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            for engine, sample_set in [
                ("circle_big_test", circle),
                ("circle_big_test_server", circle_server),
                ("openssl_prime", openssl),
                ("sympy_isprime", sympy_result),
            ]:
                agreed = sample_set.result == case.expected_prime
                if not agreed:
                    failures.append(
                        f"{engine} disagreed on {case.name}: "
                        f"got {sample_set.result}, expected {case.expected_prime}"
                    )
                add_row(
                    rows,
                    operation="prime_test",
                    case=case.name,
                    bits=case.n.bit_length(),
                    engine=engine,
                    sample_set=sample_set,
                    expected=case.expected_prime,
                    agreed=agreed,
                    mr_rounds=args.mr_rounds,
                )

        for case in next_cases():
            expected = sympy_next_prime_at_or_above(case.start)
            circle = timed(
                lambda case=case: circle_big_next(
                    args.circle_prime_bin,
                    case.start,
                    args.mr_rounds,
                    args.max_candidates,
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            circle_server = timed(
                lambda case=case: circle_big_next_server(
                    circle_next_server, case.start, args.server_batch_size
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
                sample_divisor=args.server_batch_size,
            )
            sympy_next = timed(
                lambda case=case: sympy_next_prime_at_or_above(case.start),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            fuzzy = timed(
                lambda case=case: circle_big_fuzzy_any(
                    args.circle_prime_bin,
                    model_path,
                    case.start,
                    args.mr_rounds,
                    args.candidate_window,
                    args.top_k,
                    args.score_limit,
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            fuzzy_server = timed(
                lambda case=case: circle_big_fuzzy_any_server(
                    circle_fuzzy_server, case.start, args.server_batch_size
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
                sample_divisor=args.server_batch_size,
            )
            for engine, sample_set, require_exact in [
                ("circle_big_next", circle, True),
                ("circle_big_next_server", circle_server, True),
                ("sympy_nextprime", sympy_next, True),
                ("circle_big_fuzzy_any", fuzzy, False),
                ("circle_big_fuzzy_any_server", fuzzy_server, False),
            ]:
                if require_exact:
                    agreed = sample_set.result == expected
                else:
                    agreed = (
                        isinstance(sample_set.result, int)
                        and sample_set.result >= case.start
                        and bool(sympy.isprime(sample_set.result))
                    )
                if not agreed:
                    failures.append(
                        f"{engine} disagreed on {case.name}: "
                        f"got {sample_set.result}, expected {expected}"
                    )
                add_row(
                    rows,
                    operation="next_search" if require_exact else "fuzzy_any_search",
                    case=case.name,
                    bits=case.start.bit_length(),
                    engine=engine,
                    sample_set=sample_set,
                    expected=expected,
                    agreed=agreed,
                    mr_rounds=args.mr_rounds,
                )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "operation",
                "case",
                "bits",
                "engine",
                "result",
                "expected",
                "agreed",
                "mr_rounds",
                "rounds",
                "median_ms",
                "min_ms",
                "max_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "schema": SCHEMA_ID,
        "bench_rounds": args.bench_rounds,
        "warmup_rounds": args.warmup_rounds,
        "mr_rounds": args.mr_rounds,
        "max_candidates": args.max_candidates,
        "candidate_window": args.candidate_window,
        "top_k": args.top_k,
        "score_limit": args.score_limit,
        "server_batch_size": args.server_batch_size,
        "circle_server_protocol": "stdin lines: N or N COUNT; non-json response per request",
        "circle_prime": file_fingerprint(args.circle_prime_bin),
        "big_fuzzy_model": file_fingerprint(model_path),
        "tools": {
            "openssl": tool_version([args.openssl_bin, "version"]),
            "sympy": sympy.__version__,
        },
        "failures": failures,
    }
    args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

    if args.summary:
        for row in rows:
            print(
                f"{row['operation']} {row['case']} {row['engine']}: "
                f"median={row['median_ms']}ms result={row['result']} "
                f"agreed={row['agreed']}"
            )
        print(f"wrote {args.output}")
        print(f"wrote {args.metadata_output}")

    if failures:
        for failure in failures:
            print(f"failure: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
