from circle_math.applications.coil_compute import (
    DEFAULT_LAYOUT_CASES,
    circular_stride_checksum,
    gcd_cycle_order,
    natural_order,
    reference_values,
    run_cpu_grid,
    stride_address,
    validate_layout_grid,
)


def test_stride_address_is_bounded() -> None:
    for size in range(1, 33):
        for stride in range(0, 33):
            for step in range(0, 128):
                assert 0 <= stride_address(size, stride, step) < size


def test_stride_address_closes_after_size_steps() -> None:
    for size in range(1, 33):
        for stride in range(0, 33):
            for step in range(0, 128):
                assert stride_address(size, stride, step + size) == stride_address(size, stride, step)


def test_stride_address_zero_step() -> None:
    for size in range(1, 33):
        for stride in range(0, 33):
            assert stride_address(size, stride, 0) == 0


def test_stride_address_zero_stride() -> None:
    for size in range(1, 33):
        for step in range(0, 128):
            assert stride_address(size, 0, step) == 0


def test_gcd_cycle_order_visits_each_address_once() -> None:
    for case in DEFAULT_LAYOUT_CASES:
        order = gcd_cycle_order(case.size, case.stride)
        assert len(order) == case.size
        assert sorted(order) == list(range(case.size))


def test_layout_grid_expected_outputs_match() -> None:
    results = validate_layout_grid()
    assert len(results) == len(DEFAULT_LAYOUT_CASES)
    for result in results:
        assert result.all_match


def test_cpu_grid_benchmark_uses_expected_checksums() -> None:
    expected = {}
    for case in DEFAULT_LAYOUT_CASES:
        values = reference_values(case.size)
        checksum = circular_stride_checksum(values, case.stride, natural_order(case.size), case.repeats)
        expected[(case.size, case.stride, case.repeats)] = checksum

    results = run_cpu_grid()
    assert len(results) == 2 * len(DEFAULT_LAYOUT_CASES)
    for result in results:
        key = (result.size, result.stride, result.repeats)
        assert result.checksum == expected[key]
