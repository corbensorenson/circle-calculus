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

theorem signedRot_bijective (n : Nat) (k : Int) :
    Function.Bijective (signedRot n k) := by
  constructor
  · intro x y h
    calc
      x = signedRot n (-k) (signedRot n k x) := (signedRot_inverse n k x).symm
      _ = signedRot n (-k) (signedRot n k y) := by rw [h]
      _ = y := signedRot_inverse n k y
  · intro y
    refine ⟨signedRot n (-k) y, ?_⟩
    simpa using signedRot_inverse n (-k) y

end Circle.S1
