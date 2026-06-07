import Circle.Basic
import Mathlib.Combinatorics.Additive.Corner.Roth

namespace Circle

/-- Roth bridge for dense subsets of the first `n` natural numbers.

If `A` has positive density above the mathlib Roth threshold, then `A` is not
three-term-arithmetic-progression-free.
-/
theorem roth_three_ap_nat_bridge
    {n : Nat} {ε : ℝ} (hε : 0 < ε)
    (hG : cornersTheoremBound (ε / 3) ≤ n)
    (A : Finset Nat) (hAn : A ⊆ Finset.range n) (hAε : ε * n ≤ A.card) :
    ¬ ThreeAPFree (A : Set Nat) := by
  exact roth_3ap_theorem_nat ε hε hG A hAn hAε

/-- Roth bridge as an asymptotic statement for the Roth number. -/
theorem roth_number_sublinear_bridge :
    Asymptotics.IsLittleO Filter.atTop
      (fun N => (rothNumberNat N : ℝ)) (fun N => (N : ℝ)) := by
  exact rothNumberNat_isLittleO_id

end Circle
