# Circle Calculus Erdős 1: Zero-Sum Circles

Status: polished draft with mathlib-backed external theorem bridges and executable support examples.

## Aim

This paper starts an Erdős-facing additive-combinatorics pillar for Circle Calculus. The claim is deliberately narrow: finite circles `C_n` are cyclic address spaces, so theorems about `ZMod n` can be stated directly in Circle language when the proof source is explicit.

This paper owns two proved Lean bridges:

- `CC-T0062`: `Circle.erdos_ginzburg_ziv`
- `CC-T0063`: `Circle.cauchy_davenport_prime_circle`

These are not new proofs of the underlying theorems. They are Circle-facing wrappers around mathlib theorem statements, packaged so the project can build paper, dictionary, executable witness, and Living Book interfaces without weakening proof-status boundaries.

The broader five-lane extremal-combinatorics program is tracked in `docs/CIRCLE_METHODS_EXTREMAL_COMBINATORICS.md`, with separate papers for Katona/Erdős-Ko-Rado, Roth, Hales-Jewett/Ramsey, and unit-distance/circulant graph work.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_ERDOS_01_ZERO_SUM_CIRCLES/lean/PaperErdos01.lean
```

The Python examples are:

```text
sidecars/PAPER_ERDOS_01_ZERO_SUM_CIRCLES/python/test_zero_sum_circle_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Lean declarations determine proof status; Python checks are executable support for sharpness and concrete finite examples, not formal proofs.

## Theorem Spine

- `CC-T0062`: `Circle.erdos_ginzburg_ziv`
- `CC-T0063`: `Circle.cauchy_davenport_prime_circle`

## Proved Core

`CC-T0062` proves the Circle-form Erdős-Ginzburg-Ziv bridge:

```text
If a finite indexed family has at least 2*n - 1 addresses in C_n,
then some n of those indexed addresses have sum zero in C_n.
```

The underlying formal proof is mathlib's `ZMod.erdos_ginzburg_ziv`. Circle contributes the project-native statement using `Circle.C n`.

`CC-T0063` proves the Circle-form Cauchy-Davenport bridge:

```text
If p is prime and A,B are nonempty finite subsets of C_p,
then |A+B| >= min(p, |A| + |B| - 1).
```

The underlying formal proof is mathlib's `ZMod.cauchy_davenport`. Circle contributes the project-native statement using `Circle.C p`.

## Sharpness And Examples

The Python sidecar records the standard EGZ sharpness family:

```text
(n - 1) zeros and (n - 1) ones in C_n
```

This family has length `2*n - 2` and no length-`n` zero-sum subsequence. It shows why the EGZ threshold `2*n - 1` is the right boundary in the usual theorem statement. The sidecar checks this over a bounded deterministic range and also checks that adding one more `1` in a small example produces a zero-sum witness.

The Cauchy-Davenport examples compute concrete sumsets in prime-size circles and compare them against the lower bound from `CC-T0063`.

The separate bridge papers add small finite examples for intersecting families, arithmetic progressions, coloring lines, and circulant graphs. Those examples support readers without being mistaken for proof.

## Why This Matters

This paper gives Circle Calculus a rigorous contact point with recognized Erdős additive combinatorics while avoiding overclaiming. The value is not novelty of the EGZ or Cauchy-Davenport proofs. The value is a proof-carrying interface:

- theorem ids resolve to compiled Lean declarations;
- finite examples resolve to source code;
- sharpness and witness examples stay executable rather than promoted to proof;
- future Erdős-facing work has a clean local vocabulary for zero sums and sumsets.

## Next Program

The next additive-combinatorics layer should add:

- a formal zero-sum certificate record;
- a formal finite sumset API for `C_n`;
- an EGZ sharpness theorem if it can be proved cleanly in Lean;
- a Living Book lesson that separates theorem proof, imported proof source, and executable witness search;
- exploratory lanes for Erdős-Turán additive bases and Erdős-Straus residue/provenance checks.

## Guardrail

This paper does not claim progress on an open Erdős problem. It turns two established theorems into Circle-facing formal artifacts and uses them as a quality bar for future additive-combinatorics work.
