import Circle.Core.Coil
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.ZMod.Units

namespace Circle

/-- Scaling multiplies a node by `k` in `C n`. -/
def scale (n k : Nat) (x : C n) : C n :=
  (k : ZMod n) * x

theorem scale_one (n : Nat) (x : C n) :
    scale n 1 x = x := by
  unfold scale
  simp

theorem scale_comp (n a b : Nat) (x : C n) :
    scale n a (scale n b x) = scale n (a * b) x := by
  unfold scale
  rw [← mul_assoc]
  norm_num

theorem scale_rot (n k stride : Nat) (x : C n) :
    scale n k (rot n stride x) = rot n (k * stride) (scale n k x) := by
  unfold scale rot
  rw [mul_add]
  norm_num

theorem scale_coilStep (n k stride start steps : Nat) :
    scale n k (coilStep n stride start steps) =
      coilStep n (k * stride) (k * start) steps := by
  unfold scale coilStep
  rw [mul_add]
  congr 1
  · norm_num
  · norm_num [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]

theorem scale_invertible_iff_coprime (n k : Nat) :
    Function.Bijective (scale n k) ↔ Nat.Coprime n k := by
  change Function.Bijective (fun x : ZMod n => (k : ZMod n) * x) ↔ Nat.Coprime n k
  rw [← IsUnit.isUnit_iff_mulLeft_bijective]
  rw [ZMod.isUnit_iff_coprime]
  exact ⟨Nat.Coprime.symm, Nat.Coprime.symm⟩

theorem prime_scale_bijective {p k : Nat} (hp : Nat.Prime p) (hk0 : 0 < k) (hkp : k < p) :
    Function.Bijective (scale p k) := by
  rw [scale_invertible_iff_coprime]
  exact Nat.coprime_of_lt_prime hk0.ne' hkp hp

theorem scale_cofactor_zero {n k : Nat} (hkn : k ∣ n) :
    scale n k ((n / k : Nat) : C n) = 0 := by
  unfold scale
  rw [← Nat.cast_mul]
  have hmul : k * (n / k) = n := Nat.mul_div_cancel' hkn
  rw [hmul]
  exact CharP.cast_eq_zero (ZMod n) n

end Circle
