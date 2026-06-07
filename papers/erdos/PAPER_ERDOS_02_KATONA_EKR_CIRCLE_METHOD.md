# Circle Calculus Erdos 2: Katona and Erdos-Ko-Rado

Status: polished draft with mathlib-backed theorem bridges and executable finite examples.

## Aim

This paper gives Circle Calculus a respected extremal-set-theory lane through the Katona circle method and the Erdos-Ko-Rado theorem. The point is not to claim a new proof of EKR. The point is to connect Circle's cyclic-order intuition to a formal theorem spine where the "put the ground set around a circle and count intervals/prefixes" method is visible and checkable.

The current formal seed has two proved Lean bridges:

- `CC-T0064`: `Circle.katona_prefixed_density_bridge`
- `CC-T0065`: `Circle.erdos_ko_rado_circle_bridge`

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_ERDOS_02_KATONA_EKR_CIRCLE_METHOD/lean/PaperErdos02.lean
```

The Python examples are:

```text
sidecars/PAPER_ERDOS_02_KATONA_EKR_CIRCLE_METHOD/python/test_katona_ekr_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks finite counting and sharpness examples; Lean declarations determine proof status.

## Theorem Spine

- `CC-T0064`: `Circle.katona_prefixed_density_bridge`
- `CC-T0065`: `Circle.erdos_ko_rado_circle_bridge`

## Proved Core

`CC-T0064` packages the key Katona-prefix count:

```text
density(numberings where s is a prefix) = 1 / choose(|X|, |s|)
```

The underlying proof source is mathlib's `Numbering.dens_prefixed`.

`CC-T0065` packages mathlib's Erdos-Ko-Rado theorem:

```text
If A is an intersecting family of r-subsets of Fin n and r <= n/2,
then |A| <= choose(n-1, r-1).
```

## Examples

The Python sidecar checks the exact prefix-density count for a small ground set and checks the standard sharp EKR star family: all `r`-sets containing a fixed center. The star family is uniform, pairwise intersecting, and has size `choose(n-1, r-1)`.

## Why This Matters

This lane is a clean public-facing bridge because it looks like "circle math" in the ordinary combinatorics sense: cyclic arrangements, prefix/interval counts, and double-counting. It gives the project a classical method to teach and formalize before attempting more speculative Erdos problems.

## Next Program

- Formalize star-family examples as Lean data when useful.
- Add circular-arc and interval-family examples that show the Katona method visually.
- Build a Living Book lesson that separates the circle-method idea, the formal imported theorem, and the finite executable examples.

## Guardrail

This paper does not claim a new proof of Erdos-Ko-Rado. It turns a standard theorem and a Katona counting atom into Circle-facing formal artifacts.
