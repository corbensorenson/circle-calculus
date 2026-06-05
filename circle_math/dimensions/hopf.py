from __future__ import annotations


def hopf_map(z0: complex, z1: complex) -> tuple[float, float, float]:
    """Return the standard complex-pair Hopf map coordinates."""
    product = z0 * z1.conjugate()
    return (2.0 * product.real, 2.0 * product.imag, abs(z0) ** 2 - abs(z1) ** 2)

