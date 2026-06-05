# Circle Calculus Compute 1: Proof-Carrying Circular Computation

Status: draft with a proved cyclic-address seed.

## Aim

Build certified cyclic, circulant, and orbit-structured computations that can lower to specialized backends.

The current formal seed is `COMMON-0018`, the cyclic address

```text
addr(size,index) = index mod size
```

for positive circular buffer sizes. This is a proof-carrying rewrite primitive, not a benchmark result.

## Theorem Spine

- `COMPC-T0001`: for positive size, the cyclic address is bounded by the size. Lean declaration: `Circle.Applications.cyclicAddress_lt_size`.
- `COMPC-T0002`: for positive size, adding one full size preserves the cyclic address. Lean declaration: `Circle.Applications.cyclicAddress_add_size`.
- `COMPC-T0003`: cyclic address at zero is zero. Lean declaration: `Circle.Applications.cyclicAddress_zero`.

The Python sidecar checks the same wraparound examples. These examples support implementation intuition; performance claims still require benchmarks against direct, dense, FFT, NTT, and layout baselines.

## Next Program

- Represent circle/coil expressions.
- Record Lean proofs of legal rewrites.
- Benchmark direct, dense, FFT, NTT, and layout-based backends.

## Guardrail

Benchmarks decide performance claims. Dense and direct baselines must be included.
