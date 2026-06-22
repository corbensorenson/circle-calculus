from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.check_prime_benchmark_provenance import (
    benchmark_provenance_failures,
    metadata_expectation_failures,
    metadata_range_expectation_failures,
    metadata_start_expectation_failures,
    metadata_tool_version_expectation_failures,
)


def test_benchmark_provenance_accepts_matching_hashes(tmp_path: Path) -> None:
    binary = tmp_path / "circle-prime"
    defaults = tmp_path / "prime_engine_defaults.json"
    helper_binary = tmp_path / "primesieve-next-server"
    helper_source = tmp_path / "primesieve_next_server.c"
    binary.write_bytes(b"circle-prime")
    defaults.write_text('{"segment":1507328}\n')
    helper_binary.write_bytes(b"libprimesieve-helper")
    helper_source.write_text("int main(void) { return 0; }\n")

    failures = benchmark_provenance_failures(
        {
            "circle_prime_defaults": {"sha256": sha256_hex(defaults)},
            "tools": {
                "circle_prime": {"binary": {"sha256": sha256_hex(binary)}},
                "primesieve_library_server": {
                    "available": True,
                    "binary": {
                        "path": str(helper_binary),
                        "sha256": sha256_hex(helper_binary),
                    },
                    "source_fingerprint": {
                        "path": str(helper_source),
                        "sha256": sha256_hex(helper_source),
                    },
                },
            },
        },
        circle_prime=binary,
        defaults_path=defaults,
    )

    assert failures == []


def test_benchmark_provenance_rejects_missing_hashes(tmp_path: Path) -> None:
    binary = tmp_path / "circle-prime"
    defaults = tmp_path / "prime_engine_defaults.json"
    binary.write_bytes(b"circle-prime")
    defaults.write_text('{"segment":1507328}\n')

    failures = benchmark_provenance_failures(
        {"tools": {"circle_prime": {"available": True}}},
        circle_prime=binary,
        defaults_path=defaults,
    )

    assert failures == [
        "benchmark metadata lacks a circle-prime binary hash; rerun the benchmark target.",
        "benchmark metadata lacks a prime-engine defaults hash; rerun the benchmark target.",
    ]


def test_benchmark_provenance_rejects_stale_defaults(tmp_path: Path) -> None:
    binary = tmp_path / "circle-prime"
    defaults = tmp_path / "prime_engine_defaults.json"
    binary.write_bytes(b"circle-prime")
    defaults.write_text('{"segment":1507328}\n')

    failures = benchmark_provenance_failures(
        {
            "circle_prime_defaults": {"sha256": "0" * 64},
            "tools": {"circle_prime": {"binary": {"sha256": sha256_hex(binary)}}},
        },
        circle_prime=binary,
        defaults_path=defaults,
    )

    assert len(failures) == 1
    assert "used defaults 000000000000" in failures[0]


def test_benchmark_provenance_accepts_matching_count_binary_hash(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "circle-prime"
    count_binary = tmp_path / "circle-prime-count"
    defaults = tmp_path / "prime_engine_defaults.json"
    binary.write_bytes(b"circle-prime")
    count_binary.write_bytes(b"circle-prime-count")
    defaults.write_text('{"segment":1507328}\n')

    failures = benchmark_provenance_failures(
        {
            "include_circle_count_binary": True,
            "circle_prime_defaults": {"sha256": sha256_hex(defaults)},
            "tools": {
                "circle_prime": {"binary": {"sha256": sha256_hex(binary)}},
                "circle_prime_count": {
                    "binary": {"sha256": sha256_hex(count_binary)}
                },
            },
        },
        circle_prime=binary,
        circle_prime_count=count_binary,
        defaults_path=defaults,
    )

    assert failures == []


def test_benchmark_provenance_checks_count_binary_socket_client_hash(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "circle-prime"
    count_binary = tmp_path / "circle-prime-count"
    defaults = tmp_path / "prime_engine_defaults.json"
    binary.write_bytes(b"circle-prime")
    count_binary.write_bytes(b"old-circle-prime-count")
    stale_count_hash = sha256_hex(count_binary)
    count_binary.write_bytes(b"new-circle-prime-count")
    defaults.write_text('{"segment":1507328}\n')

    failures = benchmark_provenance_failures(
        {
            "include_circle_count_binary_socket_client": True,
            "circle_prime_defaults": {"sha256": sha256_hex(defaults)},
            "tools": {
                "circle_prime": {"binary": {"sha256": sha256_hex(binary)}},
                "circle_prime_count": {"binary": {"sha256": stale_count_hash}},
            },
        },
        circle_prime=binary,
        circle_prime_count=count_binary,
        defaults_path=defaults,
    )

    assert len(failures) == 1
    assert "circle-prime-count" in failures[0]
    assert "current binary" in failures[0]


def test_benchmark_provenance_accepts_count_binary_under_size_limit(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "circle-prime"
    count_binary = tmp_path / "circle-prime-count"
    defaults = tmp_path / "prime_engine_defaults.json"
    binary.write_bytes(b"circle-prime")
    count_binary.write_bytes(b"x" * 128)
    defaults.write_text('{"segment":1507328}\n')

    failures = benchmark_provenance_failures(
        {
            "include_circle_count_binary": True,
            "circle_prime_defaults": {"sha256": sha256_hex(defaults)},
            "tools": {
                "circle_prime": {"binary": {"sha256": sha256_hex(binary)}},
                "circle_prime_count": {
                    "binary": {"sha256": sha256_hex(count_binary)}
                },
            },
        },
        circle_prime=binary,
        circle_prime_count=count_binary,
        defaults_path=defaults,
        max_circle_prime_count_size_bytes=128,
    )

    assert failures == []


def test_benchmark_provenance_rejects_oversized_count_binary(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "circle-prime"
    count_binary = tmp_path / "circle-prime-count"
    defaults = tmp_path / "prime_engine_defaults.json"
    binary.write_bytes(b"circle-prime")
    count_binary.write_bytes(b"x" * 129)
    defaults.write_text('{"segment":1507328}\n')

    failures = benchmark_provenance_failures(
        {
            "include_circle_count_binary": True,
            "circle_prime_defaults": {"sha256": sha256_hex(defaults)},
            "tools": {
                "circle_prime": {"binary": {"sha256": sha256_hex(binary)}},
                "circle_prime_count": {
                    "binary": {"sha256": sha256_hex(count_binary)}
                },
            },
        },
        circle_prime=binary,
        circle_prime_count=count_binary,
        defaults_path=defaults,
        max_circle_prime_count_size_bytes=128,
    )

    assert len(failures) == 1
    assert "circle-prime-count binary is 129 bytes" in failures[0]
    assert "exceeding max 128" in failures[0]


def test_benchmark_provenance_rejects_stale_count_binary_hash(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "circle-prime"
    count_binary = tmp_path / "circle-prime-count"
    defaults = tmp_path / "prime_engine_defaults.json"
    binary.write_bytes(b"circle-prime")
    count_binary.write_bytes(b"old-circle-prime-count")
    stale_count_hash = sha256_hex(count_binary)
    count_binary.write_bytes(b"new-circle-prime-count")
    defaults.write_text('{"segment":1507328}\n')

    failures = benchmark_provenance_failures(
        {
            "include_circle_count_binary": True,
            "circle_prime_defaults": {"sha256": sha256_hex(defaults)},
            "tools": {
                "circle_prime": {"binary": {"sha256": sha256_hex(binary)}},
                "circle_prime_count": {"binary": {"sha256": stale_count_hash}},
            },
        },
        circle_prime=binary,
        circle_prime_count=count_binary,
        defaults_path=defaults,
    )

    assert len(failures) == 1
    assert "circle-prime-count" in failures[0]
    assert "current binary" in failures[0]


def test_benchmark_provenance_rejects_stale_helper_binary(tmp_path: Path) -> None:
    binary = tmp_path / "circle-prime"
    defaults = tmp_path / "prime_engine_defaults.json"
    helper_binary = tmp_path / "primecount-next-server"
    helper_source = tmp_path / "primecount_next_server.c"
    binary.write_bytes(b"circle-prime")
    defaults.write_text('{"segment":1507328}\n')
    helper_binary.write_bytes(b"old-helper")
    helper_source.write_text("int main(void) { return 0; }\n")
    stale_helper_hash = sha256_hex(helper_binary)
    helper_binary.write_bytes(b"new-helper")

    failures = benchmark_provenance_failures(
        {
            "circle_prime_defaults": {"sha256": sha256_hex(defaults)},
            "tools": {
                "circle_prime": {"binary": {"sha256": sha256_hex(binary)}},
                "primecount_library_server": {
                    "available": True,
                    "binary": {
                        "path": str(helper_binary),
                        "sha256": stale_helper_hash,
                    },
                    "source_fingerprint": {
                        "path": str(helper_source),
                        "sha256": sha256_hex(helper_source),
                    },
                },
            },
        },
        circle_prime=binary,
        defaults_path=defaults,
    )

    assert len(failures) == 1
    assert "primecount_library_server helper binary" in failures[0]
    assert "used" in failures[0]


def test_metadata_expectations_accept_matching_scalar_fields() -> None:
    failures = metadata_expectation_failures(
        {
            "batch_request_profile": "shifted",
            "batch_shift": 10000000,
            "thread_policy": {"circle_requested_threads": 8},
        },
        [
            "batch_request_profile=shifted",
            "batch_shift=10000000",
            "thread_policy.circle_requested_threads=8",
        ],
    )

    assert failures == []


def test_metadata_tool_version_expectations_accept_current_or_newer_controls() -> None:
    failures = metadata_tool_version_expectation_failures(
        {
            "tools": {
                "primesieve": {
                    "available": True,
                    "version": "primesieve 12.14, <https://github.com/kimwalisch/primesieve>",
                },
                "primecount": {
                    "available": True,
                    "version": "primecount 8.6, <https://github.com/kimwalisch/primecount>",
                },
            }
        },
        ["primesieve=12.14", "primecount=8.5"],
    )

    assert failures == []


def test_metadata_tool_version_expectations_reject_old_or_missing_controls() -> None:
    failures = metadata_tool_version_expectation_failures(
        {
            "tools": {
                "primesieve": {"available": True, "version": "primesieve 12.13"},
                "primecount": {"available": False, "version": None},
            }
        },
        ["primesieve=12.14", "primecount=8.5"],
    )

    assert failures == [
        "benchmark metadata tool 'primesieve' version 12.13 is below required 12.14.",
        "benchmark metadata does not show required tool 'primecount' as available.",
    ]


def test_metadata_expectations_reject_mismatched_shifted_profile() -> None:
    failures = metadata_expectation_failures(
        {"batch_request_profile": "identical", "batch_shift": 0},
        ["batch_request_profile=shifted", "batch_shift=10000000"],
    )

    assert failures == [
        "metadata field 'batch_request_profile' is \"identical\", expected \"shifted\".",
        "metadata field 'batch_shift' is 0, expected 10000000.",
    ]


def test_metadata_range_expectations_parse_half_open_ranges() -> None:
    metadata = {
        "ranges": [
            {
                "low": 1000000000000,
                "high": 1000010000000,
                "span": 10000000,
            }
        ]
    }

    assert (
        metadata_range_expectation_failures(
            metadata, "1000000000000:1000010000000"
        )
        == []
    )


def test_metadata_range_expectations_reject_wrong_range() -> None:
    failures = metadata_range_expectation_failures(
        {"ranges": [{"low": 0, "high": 10, "span": 10}]},
        "1000000000000:1000010000000",
    )

    assert len(failures) == 1
    assert "metadata field 'ranges'" in failures[0]
    assert "1000010000000" in failures[0]


def test_metadata_start_expectations_parse_next_prime_starts() -> None:
    metadata = {"starts": [90, 1000000, 4294967000, 1000000000000]}

    assert (
        metadata_start_expectation_failures(
            metadata, "90,1000000,4294967000,1000000000000"
        )
        == []
    )


def test_metadata_start_expectations_reject_wrong_starts() -> None:
    failures = metadata_start_expectation_failures(
        {"starts": [90, 1000000]},
        "90,1000000,4294967000,1000000000000",
    )

    assert len(failures) == 1
    assert "metadata field 'starts'" in failures[0]
    assert "4294967000" in failures[0]


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
