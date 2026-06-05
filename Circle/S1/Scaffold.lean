import Circle.Common.Scaffold
import Circle.Core.Finite

namespace Circle.S1

def legacyFiniteCoreName : String :=
  "Circle.Core"

def signedRot (n : Nat) (k : Int) (x : Circle.C n) : Circle.C n :=
  x + (k : ZMod n)

theorem signedRot_zero (n : Nat) (x : Circle.C n) :
    signedRot n 0 x = x := by
  simp [signedRot]

theorem signedRot_comp (n : Nat) (a b : Int) (x : Circle.C n) :
    signedRot n a (signedRot n b x) = signedRot n (a + b) x := by
  simp [signedRot, add_comm, add_left_comm]

theorem signedRot_inverse (n : Nat) (k : Int) (x : Circle.C n) :
    signedRot n (-k) (signedRot n k x) = x := by
  simp [signedRot, add_assoc]

end Circle.S1
