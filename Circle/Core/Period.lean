import Circle.Core.Coil
import Mathlib.GroupTheory.OrderOfElement

namespace Circle

/-- The stride element whose additive order is the coil period. -/
def stride (n : Nat) (k : Nat) : C n :=
  (k : ZMod n)

/-- The period of a finite coil is the additive order of its stride. -/
noncomputable def period (n k : Nat) : Nat :=
  addOrderOf (stride n k)

theorem period_eq_n_div_gcd {n k : Nat} (hn : n ≠ 0) :
    period n k = n / Nat.gcd n k := by
  unfold period stride
  simpa using ZMod.addOrderOf_coe k (n := n) hn

end Circle
