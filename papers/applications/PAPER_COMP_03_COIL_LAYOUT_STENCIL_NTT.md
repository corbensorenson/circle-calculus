# Circle Calculus Compute 3: CoilLayout, CoilStencil, and CoilNTT

Status: polished draft with a proved stride-address seed and an exploratory layout benchmark/validation harness.

## Aim

This paper tracks the most practical non-AI compute ideas: gcd-cycle memory layouts, verified periodic-boundary stencils, and exact finite-circle transform tooling. The shared structure is a circular stride:

```text
i -> i + k mod n
```

Circle Calculus can make that structure explicit through orbit decomposition, address proofs, and benchmarkable layouts.

The current formal seed is `COMMON-0022`, the stride address

```text
addr(size,stride,step) = (step * stride) mod size
```

for circular stride schedules.

## Theorem Spine

- `COMPL-T0001`: `Circle.Applications.strideAddress_lt_size`
- `COMPL-T0002`: `Circle.Applications.strideAddress_add_size_steps`
- `COMPL-T0003`: `Circle.Applications.strideAddress_zero_step`
- `COMPL-T0004`: `Circle.Applications.strideAddress_zero_stride`

## Proved Core

`COMPL-T0001` proves that a stride address is bounded by the positive circular size. `COMPL-T0002` proves closure after one full pass through the circular step horizon. `COMPL-T0003` and `COMPL-T0004` prove the zero-step and zero-stride anchors.

The Python test sidecar checks the same finite stride examples. The benchmark sidecar `benchmark_coil_layout.py` is a small Mac-compatible harness for natural-order versus gcd-cycle circular-stride traversal, with an optional MLX backend when `mlx.core` is available.

`COMPL-B0001` adds a deterministic validation grid before timing claims. It checks that natural order, gcd-cycle order, direct traversal, and a tiny dense circular-stride reference all produce the same checksum on selected parameter cases. This is expected-output coverage for benchmark safety, not a cache-locality or speed result.

## Compute Program

`CoilLayout` should test whether storing stride cycles contiguously improves real workloads. For composite `n`, a stride decomposes into `gcd(n,k)` cycles, so memory can be arranged by orbit.

`CoilStencil` should recognize periodic axes in finite-grid operations and choose direct stencil, FFT, block-circulant, or coil-layout backends only when benchmarks justify the choice.

`CoilNTT` should target exact cyclic convolution, roots of unity, modulus constraints, and butterfly layouts for polynomial, FHE, ZK, and finite-transform workloads.

## Next Program

- Extend the current traversal benchmark into workload-specific kernels.
- Expand the validation grid into explicit direct, dense, FFT, NTT, and MLX layout baselines.
- Keep CPU reference behavior explicit before adding MLX acceleration.
- Model transform correctness before claiming FFT/NTT backend correctness.
- Include ordinary dense/direct baselines in every benchmark.

## Guardrail

Local acceleration should be MLX/Mac-compatible first. CUDA/cuFFT remain external baselines or portability notes. The proved content is stride-address arithmetic, not cache locality, stencil correctness, or transform performance.
