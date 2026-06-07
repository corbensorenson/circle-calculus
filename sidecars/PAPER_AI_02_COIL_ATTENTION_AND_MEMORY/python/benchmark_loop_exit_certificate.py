"""Run the deterministic loop-exit certificate fixture."""

from circle_math.applications.circle_ai import loop_exit_certificate


def main() -> None:
    certificate = loop_exit_certificate(
        4,
        sample_index=6,
        max_loops=4,
        overthink_tolerance=1,
    )
    print(certificate)


if __name__ == "__main__":
    main()
