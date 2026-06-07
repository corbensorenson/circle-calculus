import Circle.Basic
import Mathlib.Combinatorics.KatonaCircle
import Mathlib.Combinatorics.SetFamily.KruskalKatona

namespace Circle

/-- Circle-method density bridge for Katona prefixes.

For a finite type `X`, the density of numberings in which a fixed set appears
as a prefix is the reciprocal binomial coefficient. This is the local
double-counting atom used by the Katona circle method.
-/
theorem katona_prefixed_density_bridge
    {X : Type*} [Fintype X] [DecidableEq X] (s : Finset X) :
    (Numbering.prefixed s).dens = ((Fintype.card X).choose s.card : ℚ≥0)⁻¹ := by
  simp

/-- Circle-method bridge to the Erdős-Ko-Rado theorem.

An intersecting family of `r`-subsets of `Fin n`, with `r <= n / 2`, has size
at most `(n - 1).choose (r - 1)`.
-/
theorem erdos_ko_rado_circle_bridge
    {n r : Nat} {𝒜 : Finset (Finset (Fin n))}
    (h𝒜 : (𝒜 : Set (Finset (Fin n))).Intersecting)
    (hSized : (𝒜 : Set (Finset (Fin n))).Sized r)
    (hr : r ≤ n / 2) :
    𝒜.card ≤ (n - 1).choose (r - 1) := by
  exact Finset.erdos_ko_rado h𝒜 hSized hr

end Circle
