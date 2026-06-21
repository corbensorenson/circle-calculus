from __future__ import annotations

from pathlib import Path

from scripts import check_prime_external_correctness as correctness


def test_parse_count_modes_all_expands_current_modes() -> None:
    assert correctness.parse_count_modes_argument("all") == [
        "segmented",
        "balanced",
        "dynamic",
        "prefix-pi",
        "presieve13",
        "presieve17",
        "wheel30-mark",
        "hybrid-wheel30-mark",
    ]


def test_default_correctness_ranges_cover_boundary_windows() -> None:
    assert (529, 5000) in correctness.parse_ranges(correctness.DEFAULT_RANGES)
    assert (4294900000, 4295100000) in correctness.parse_ranges(
        correctness.DEFAULT_RANGES
    )
    assert (999999000000, 1000001000000) in correctness.parse_ranges(
        correctness.DEFAULT_RANGES
    )
    assert (529, 1000) in correctness.parse_ranges(
        correctness.DEFAULT_ENUMERATION_RANGES
    )
    assert (4294967000, 4294968000) in correctness.parse_ranges(
        correctness.DEFAULT_ENUMERATION_RANGES
    )
    assert (
        18446744073709551515,
        18446744073709551615,
    ) in correctness.parse_ranges(correctness.DEFAULT_ENUMERATION_RANGES)
    assert 4_294_967_000 in correctness.parse_integer_list_argument(
        correctness.DEFAULT_NEXT_STARTS
    )
    assert 18_446_744_073_709_551_500 in correctness.parse_integer_list_argument(
        correctness.DEFAULT_NEXT_STARTS
    )
    assert 18_446_744_073_709_551_558 in correctness.parse_integer_list_argument(
        correctness.DEFAULT_NEXT_STARTS
    )


def test_run_checks_deduplicates_resolved_circle_variants(monkeypatch) -> None:
    monkeypatch.setattr(
        correctness,
        "external_range_counts",
        lambda **_: {"primesieve": 168, "primecount": 168},
    )

    def fake_circle_count(
        binary: Path,
        low: int,
        high: int,
        segment_size: int,
        threads: int,
        count_mode: str,
    ) -> dict[str, int | str]:
        del binary, low, high
        return {
            "count": 168,
            "count_mode": count_mode,
            "segment_size": 64 if segment_size == 0 else segment_size,
            "threads": threads,
            "requested_threads": threads,
        }

    monkeypatch.setattr(correctness, "circle_count", fake_circle_count)

    checks = correctness.run_checks(
        circle_prime=Path("circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        ranges=[(0, 1000)],
        segment_sizes=[0, 64],
        circle_count_modes=["segmented", "balanced"],
        circle_threads=8,
        external_threads=8,
    )

    assert len(checks) == 2
    assert {check["count_mode"] for check in checks} == {"segmented", "balanced"}
    assert all(check["passes"] for check in checks)
    assert all(check["segment_size"] == 64 for check in checks)


def test_run_checks_deduplicates_prefix_pi_before_subprocess(monkeypatch) -> None:
    monkeypatch.setattr(
        correctness,
        "external_range_counts",
        lambda **_: {"primesieve": 168, "primecount": 168},
    )
    calls = []

    def fake_circle_count(
        binary: Path,
        low: int,
        high: int,
        segment_size: int,
        threads: int,
        count_mode: str,
    ) -> dict[str, int | str]:
        del binary, low, high, threads
        calls.append((segment_size, count_mode))
        return {
            "count": 168,
            "count_mode": "prefix-pi",
            "segment_size": segment_size or 262_144,
            "threads": 1,
            "requested_threads": 8,
        }

    monkeypatch.setattr(correctness, "circle_count", fake_circle_count)

    checks = correctness.run_checks(
        circle_prime=Path("circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        ranges=[(0, 1000)],
        segment_sizes=[0, 64, 262_144],
        circle_count_modes=["prefix-pi"],
        circle_threads=8,
        external_threads=8,
    )

    assert calls == [(0, "prefix-pi")]
    assert len(checks) == 1
    assert checks[0]["passes"] is True


def test_run_enumeration_checks_compares_exact_prime_lists(monkeypatch) -> None:
    monkeypatch.setattr(
        correctness,
        "primesieve_primes",
        lambda binary, low, high: [2, 3, 5, 7],
    )

    def fake_circle_primes(
        binary: Path,
        low: int,
        high: int,
        segment_size: int,
    ) -> dict[str, object]:
        del binary, low, high
        return {
            "primes": [2, 3, 5, 7],
            "segment_size": 64 if segment_size == 0 else segment_size,
            "threads": 1,
            "requested_threads": 1,
        }

    monkeypatch.setattr(correctness, "circle_primes", fake_circle_primes)

    checks = correctness.run_enumeration_checks(
        circle_prime=Path("circle-prime"),
        primesieve="/opt/bin/primesieve",
        ranges=[(0, 10)],
        segment_sizes=[0, 64, 128],
    )

    assert len(checks) == 2
    assert [check["segment_size"] for check in checks] == [64, 128]
    assert all(check["passes"] for check in checks)
    assert all(check["circle_count"] == 4 for check in checks)


def test_run_next_checks_compares_against_primesieve_and_primecount(monkeypatch) -> None:
    monkeypatch.setattr(
        correctness,
        "primesieve_next_prime",
        lambda binary, start, search_window: start + 1,
    )
    monkeypatch.setattr(
        correctness,
        "primecount_next_prime",
        lambda binary, start, threads: start + 1,
    )
    monkeypatch.setattr(
        correctness,
        "circle_next_prime",
        lambda binary, start: {"prime": start + 1, "candidate_count": 1},
    )

    checks = correctness.run_next_checks(
        circle_prime=Path("circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        starts=[100, 1_000_000],
        search_window=1000,
        external_threads=8,
        primecount_max_start=1_000_000_000_000,
    )

    assert len(checks) == 2
    assert all(check["passes"] for check in checks)
    assert checks[0]["circle_prime"] == 101
    assert checks[0]["external_prime"] == 101
    assert checks[0]["external_primes"] == {"primesieve": 101, "primecount": 101}
    assert checks[0]["matches"] == {"primesieve": True, "primecount": True}


def test_run_next_checks_skips_primecount_above_cap(monkeypatch) -> None:
    monkeypatch.setattr(
        correctness,
        "primesieve_next_prime",
        lambda binary, start, search_window: start + 1,
    )
    monkeypatch.setattr(
        correctness,
        "primecount_next_prime",
        lambda binary, start, threads: (_ for _ in ()).throw(
            AssertionError("primecount should be capped for this start")
        ),
    )
    monkeypatch.setattr(
        correctness,
        "circle_next_prime",
        lambda binary, start: {"prime": start + 1, "candidate_count": 1},
    )

    checks = correctness.run_next_checks(
        circle_prime=Path("circle-prime"),
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        starts=[18_446_744_073_709_551_500],
        search_window=1000,
        external_threads=8,
        primecount_max_start=1_000_000_000_000,
    )

    assert checks[0]["external_primes"] == {
        "primesieve": 18_446_744_073_709_551_501
    }
    assert checks[0]["matches"] == {"primesieve": True}


def test_run_count_server_checks_compares_one_shot_and_external_counts(monkeypatch) -> None:
    class FakeCountServerClient:
        def __init__(self, binary: Path) -> None:
            self.binary = binary
            self.closed = False

        def count(
            self,
            low: int,
            high: int,
            segment_size: int,
            threads: int,
            count_mode: str,
        ) -> int:
            assert (low, high, segment_size, threads, count_mode) == (
                0,
                1000,
                64,
                8,
                "segmented",
            )
            return 168

        def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(correctness, "CountServerClient", FakeCountServerClient)

    checks = correctness.run_count_server_checks(
        circle_prime=Path("circle-prime"),
        count_checks=[
            {
                "low": 0,
                "high": 1000,
                "span": 1000,
                "count_mode": "segmented",
                "segment_size": 64,
                "threads": 8,
                "requested_threads": 8,
                "circle_count": 168,
                "external_counts": {"primesieve": 168, "primecount": 168},
                "matches": {"primesieve": True, "primecount": True},
                "passes": True,
            }
        ],
    )

    assert len(checks) == 1
    assert checks[0]["circle_count"] == 168
    assert checks[0]["one_shot_circle_count"] == 168
    assert checks[0]["matches_one_shot"] is True
    assert checks[0]["passes"] is True


def test_first_mismatch_reports_value_or_length_difference() -> None:
    assert correctness.first_mismatch([2, 3, 7], [2, 3, 5]) == {
        "index": 2,
        "circle": 7,
        "external": 5,
    }
    assert correctness.first_mismatch([2, 3], [2, 3, 5]) == {
        "index": 2,
        "circle": None,
        "external": 5,
    }
    assert correctness.first_mismatch([2, 3], [2, 3]) is None


def test_build_report_counts_failures() -> None:
    report = correctness.build_report(
        started_at_utc="2026-01-01T00:00:00Z",
        cargo=None,
        circle_prime=None,
        primesieve="/opt/bin/primesieve",
        primecount="/opt/bin/primecount",
        ranges=[(0, 1000)],
        enumeration_ranges=[(0, 10)],
        next_starts=[100],
        segment_sizes=[0],
        circle_count_modes=["segmented"],
        circle_threads=8,
        external_threads=8,
        required_tools=["primecount", "primesieve"],
        missing_tools=[],
        checks=[
            {
                "low": 0,
                "high": 1000,
                "span": 1000,
                "count_mode": "segmented",
                "segment_size": 64,
                "threads": 8,
                "requested_threads": 8,
                "circle_count": 167,
                "external_counts": {"primesieve": 168, "primecount": 168},
                "matches": {"primesieve": False, "primecount": False},
                "passes": False,
            }
        ],
        count_server_checks=[
            {
                "low": 0,
                "high": 1000,
                "span": 1000,
                "count_mode": "segmented",
                "segment_size": 64,
                "threads": 8,
                "requested_threads": 8,
                "circle_count": 168,
                "one_shot_circle_count": 167,
                "external_counts": {"primesieve": 168, "primecount": 168},
                "matches": {"primesieve": True, "primecount": True},
                "matches_one_shot": False,
                "passes": False,
            }
        ],
        enumeration_checks=[
            {
                "low": 0,
                "high": 10,
                "span": 10,
                "segment_size": 64,
                "threads": 1,
                "requested_threads": 1,
                "circle_count": 3,
                "external_count": 4,
                "first_mismatch": {"index": 2, "circle": 7, "external": 5},
                "passes": False,
            }
        ],
        next_checks=[
            {
                "start": 100,
                "search_window": 1000,
                "circle_prime": 101,
                "external_prime": 103,
                "external_primes": {"primesieve": 103, "primecount": 103},
                "matches": {"primesieve": False, "primecount": False},
                "candidate_count": 1,
                "passes": False,
            }
        ],
    )

    assert report["count_check_count"] == 1
    assert report["count_server_check_count"] == 1
    assert report["enumeration_check_count"] == 1
    assert report["next_check_count"] == 1
    assert report["next_external_check_count"] == 2
    assert report["check_count"] == 4
    assert report["count_failure_count"] == 1
    assert report["count_server_failure_count"] == 1
    assert report["enumeration_failure_count"] == 1
    assert report["next_failure_count"] == 1
    assert report["failure_count"] == 4
    assert report["passes"] is False
