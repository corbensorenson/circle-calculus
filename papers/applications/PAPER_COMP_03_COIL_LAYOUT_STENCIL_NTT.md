# Circle Calculus Compute 3: CoilLayout, CoilStencil, and CoilNTT

Status: draft with a proved stride-address seed.

## Aim

Explore gcd-cycle memory layouts, verified periodic-boundary stencils, and exact finite-circle transform tooling.

The current formal seed is `COMMON-0022`, the stride address

```text
addr(size,stride,step) = (step * stride) mod size
```

for circular stride schedules. This is the address-level spine for future `CoilLayout`, `CoilStencil`, and `CoilNTT` work; it is not a proof of cache locality, transform correctness, or backend speed.

## Theorem Spine

- `COMPL-T0001`: for positive circular size, a stride address is bounded by the size. Lean declaration: `Circle.Applications.strideAddress_lt_size`.
- `COMPL-T0002`: adding one full circular size to the step count preserves the stride address. Lean declaration: `Circle.Applications.strideAddress_add_size_steps`.

The Python sidecar checks the same finite stride examples. Layout, stencil, FFT, NTT, and MLX/backend claims still require explicit algorithms and benchmarks.

## Next Program

- `CoilLayout`: reorder `i -> i+k mod n` access into orbit order.
- `CoilStencil`: identify periodic axes and choose direct, FFT, or block-circulant backends.
- `CoilNTT`: model exact cyclic convolution, roots, moduli, and butterfly layouts.

## Guardrail

Local acceleration should be MLX/Mac-compatible first. CUDA/cuFFT remain external baselines or portability notes.
