import Circle.Core.Finite

namespace Circle

/-- Rotate a node by adding a natural-number stride in `C n`. -/
def rot (n : Nat) (k : Nat) (x : C n) : C n :=
  x + (k : ZMod n)

theorem rot_zero (n : Nat) (x : C n) : rot n 0 x = x := by
  simp [rot]

theorem rot_comp (n a b : Nat) (x : C n) :
    rot n a (rot n b x) = rot n (a + b) x := by
  simp [rot, Nat.cast_add, add_comm, add_left_comm]

theorem rot_inverse_left (n a : Nat) (x : C n) :
    x + (a : ZMod n) - (a : ZMod n) = x := by
  simp

end Circle
