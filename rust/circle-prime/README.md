# circle-prime

Rust prime-search and horizon/coil utilities for Circle Calculus.

This crate is intentionally narrow. It exposes prime decisions, prime counts,
horizon inspection, coil signatures, and JSON proof-contract helpers used by
the wider Circle Calculus project. The Lean theorem corpus and Python reference
models live in the repository root package rather than in this crate.

## Library Use

```rust
use circle_prime::{is_prime_u64, prime_pi_u64};

assert_eq!(is_prime_u64(17), true);
assert_eq!(prime_pi_u64(10), 4);
```

## Command-Line Tools

- `circle-prime`
- `circle-prime-count`

See the repository README for the full Circle Calculus proof and contract
documentation.
