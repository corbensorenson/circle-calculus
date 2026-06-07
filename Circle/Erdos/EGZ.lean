import Circle.Basic
import Mathlib.Combinatorics.Additive.ErdosGinzburgZiv

namespace Circle

/-- Circle-form statement of the Erdős-Ginzburg-Ziv theorem.

Any finite list of at least `2 * n - 1` marked positions in `C n` contains `n`
positions whose circle-address sum is zero.
-/
theorem erdos_ginzburg_ziv
    {ι : Type*} {n : Nat} {s : Finset ι} (a : ι → C n)
    (hs : 2 * n - 1 ≤ s.card) :
    ∃ t ⊆ s, t.card = n ∧ ∑ i ∈ t, a i = 0 := by
  simpa [C] using ZMod.erdos_ginzburg_ziv (n := n) (s := s) (a := a) hs

end Circle
