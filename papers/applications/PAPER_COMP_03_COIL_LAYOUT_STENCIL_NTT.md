# Circle Calculus Compute 3: CoilLayout, CoilStencil, and CoilNTT

Status: planned compute scaffold.

## Aim

Explore gcd-cycle memory layouts, verified periodic-boundary stencils, and exact finite-circle transform tooling.

## Program

- `CoilLayout`: reorder `i -> i+k mod n` access into orbit order.
- `CoilStencil`: identify periodic axes and choose direct, FFT, or block-circulant backends.
- `CoilNTT`: model exact cyclic convolution, roots, moduli, and butterfly layouts.

## Guardrail

Local acceleration should be MLX/Mac-compatible first. CUDA/cuFFT remain external baselines or portability notes.
