# Circle Calculus Compute 1: Proof-Carrying Circular Computation

Status: polished draft with a proved cyclic-address seed.

## Aim

This paper starts the compute track: certified cyclic, circulant, and orbit-structured computations that can lower to specialized backends. The long-term target is a `CoilIR`-style optimizer:

```text
circle/coil expression
  -> dictionary-recognized cyclic structure
  -> Lean-proved rewrite or address transformation
  -> backend selection
  -> benchmark validation
```

The current formal seed is `COMMON-0018`, the cyclic address

```text
addr(size,index) = index mod size
```

for positive circular buffer sizes. This is a proof-carrying rewrite primitive, not a benchmark result.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION/lean/PaperComp01.lean
```

The Python examples are:

```text
sidecars/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION/python/test_cyclic_address_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks cyclic-address examples; Lean declarations determine proof status.

## Theorem Spine

- `COMPC-T0001`: `Circle.Applications.cyclicAddress_lt_size`
- `COMPC-T0002`: `Circle.Applications.cyclicAddress_add_size`
- `COMPC-T0003`: `Circle.Applications.cyclicAddress_zero`
- `COMPC-T0004`: `Circle.Applications.cyclicAddress_add_mul_size`
- `COMPC-T0005`: `Circle.Applications.cyclicAddress_idempotent`

## Proved Core

`COMPC-T0001` proves that a cyclic address is bounded by the positive circular size. `COMPC-T0002` proves the wraparound law:

```text
cyclicAddress size (index + size) =
  cyclicAddress size index
```

`COMPC-T0004` proves the corresponding multi-pass law for any whole number of full buffer-size passes. `COMPC-T0005` proves that normalizing an already normalized cyclic address is a no-op:

```text
cyclicAddress size (cyclicAddress size index) =
  cyclicAddress size index
```

`COMPC-T0003` proves the zero anchor.

Together these are the basic address-safety facts required before any compiler pass can replace an ordinary index with a circular one. The Python sidecar checks the same wraparound examples.

## Backend Program

The later optimizer should only use a specialized backend when the structure is real enough to justify it. Candidate backends include direct cyclic loops, FFT convolution, NTT convolution, circulant or block-circulant matrix routines, coiled memory layouts, ring-buffer kernels, and spherical or quaternion kernels for geometric workloads.

Each backend needs both a proof side and a benchmark side:

- proof: the rewrite preserves the intended finite address or algebraic structure;
- benchmark: the backend beats a relevant baseline on a specified workload.

## Next Program

- Represent circle/coil expressions explicitly.
- Record Lean proofs of legal rewrites.
- Benchmark direct, dense, FFT, NTT, and layout-based backends.
- Keep MLX/Mac-compatible experiments first for local acceleration.

## Guardrail

Benchmarks decide performance claims. Dense, direct, and standard library baselines must be included before any speedup is treated as real.
