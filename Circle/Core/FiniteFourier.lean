import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.ZMod.Basic

/-!
# Finite Fourier structure on a finite circle

This file gives the small formal spine needed by the public Circle Calculus API
before committing to a particular analytic realization of roots of unity.

A `CyclicCharacter n R` is a multiplicative character of the additive finite
circle `ZMod n` into a commutative monoid `R`.  Complex roots of unity are the
standard model, but the theorems below are deliberately algebraic: character
values are roots of unity, multiplying characters stays a character, Fourier
coefficients are additive in the signal, and cyclic shifts become phase factors.
-/

namespace Circle

variable (n : Nat) (R : Type*)

/-- A multiplicative character of the additive finite circle `ZMod n`. -/
structure CyclicCharacter [CommMonoid R] where
  eval : ZMod n → R
  map_zero' : eval 0 = 1
  map_add' : ∀ a b : ZMod n, eval (a + b) = eval a * eval b

namespace CyclicCharacter

variable {n R}

instance [CommMonoid R] : CoeFun (CyclicCharacter n R) (fun _ => ZMod n → R) where
  coe χ := χ.eval

@[simp] theorem map_zero [CommMonoid R] (χ : CyclicCharacter n R) :
    χ (0 : ZMod n) = 1 :=
  χ.map_zero'

@[simp] theorem map_add [CommMonoid R] (χ : CyclicCharacter n R) (a b : ZMod n) :
    χ (a + b) = χ a * χ b :=
  χ.map_add' a b

/-- The trivial character sends every finite-circle node to `1`. -/
def trivial [CommMonoid R] : CyclicCharacter n R where
  eval := fun _ => 1
  map_zero' := rfl
  map_add' := by simp

@[simp] theorem trivial_apply [CommMonoid R] (a : ZMod n) :
    (trivial : CyclicCharacter n R) a = 1 :=
  rfl

/-- Pointwise multiplication of cyclic characters. -/
def mul [CommMonoid R] (χ ψ : CyclicCharacter n R) : CyclicCharacter n R where
  eval := fun a => χ a * ψ a
  map_zero' := by simp
  map_add' := by
    intro a b
    simp [mul_assoc, mul_left_comm]

@[simp] theorem mul_apply [CommMonoid R] (χ ψ : CyclicCharacter n R) (a : ZMod n) :
    mul χ ψ a = χ a * ψ a :=
  rfl

/-- Character evaluation carries repeated addition to powers. -/
theorem map_nsmul [CommMonoid R] (χ : CyclicCharacter n R) (m : Nat) (a : ZMod n) :
    χ (m • a) = χ a ^ m := by
  induction m with
  | zero =>
      simp
  | succ m ih =>
      rw [succ_nsmul, map_add, ih, pow_succ]

/--
Every value of a finite-circle character is an `n`th root of unity.  This is the
algebraic bridge from cyclic addresses to roots-of-unity Fourier phases.
-/
theorem value_pow_card [CommMonoid R] (χ : CyclicCharacter n R) (a : ZMod n) :
    χ a ^ n = 1 := by
  have hmap := χ.map_nsmul n a
  have hzero : n • a = 0 := by
    rw [← Nat.cast_smul_eq_nsmul (ZMod n)]
    simp
  rw [hzero] at hmap
  simpa using hmap.symm

end CyclicCharacter

variable {n R}

/-- Cyclic shift of a finite-circle signal by `s`. -/
def finiteShift (s : ZMod n) (x : ZMod n → R) : ZMod n → R :=
  fun i => x (i - s)

@[simp] theorem finiteShift_zero (x : ZMod n → R) :
    finiteShift (0 : ZMod n) x = x := by
  funext i
  simp [finiteShift]

theorem finiteShift_add (s t : ZMod n) (x : ZMod n → R) :
    finiteShift (s + t) x = finiteShift s (finiteShift t x) := by
  funext i
  simp [finiteShift, sub_add_eq_sub_sub]

section Fourier

variable [NeZero n] [CommSemiring R]

/-- Fourier coefficient of a finite-circle signal at a cyclic character. -/
def finiteFourierCoeff (χ : CyclicCharacter n R) (x : ZMod n → R) : R :=
  ∑ i : ZMod n, x i * χ i

theorem finiteFourierCoeff_add (χ : CyclicCharacter n R) (x y : ZMod n → R) :
    finiteFourierCoeff χ (x + y) =
      finiteFourierCoeff χ x + finiteFourierCoeff χ y := by
  simp [finiteFourierCoeff, Pi.add_apply, add_mul, Finset.sum_add_distrib]

theorem finiteFourierCoeff_zero (χ : CyclicCharacter n R) :
    finiteFourierCoeff χ (0 : ZMod n → R) = 0 := by
  simp [finiteFourierCoeff]

/--
Finite Fourier shift law: shifting the signal by `s` multiplies its coefficient
by the character phase at `s`.
-/
theorem finiteFourierCoeff_shift (χ : CyclicCharacter n R) (s : ZMod n)
    (x : ZMod n → R) :
    finiteFourierCoeff χ (finiteShift s x) =
      χ s * finiteFourierCoeff χ x := by
  unfold finiteFourierCoeff finiteShift
  rw [← Equiv.sum_comp (Equiv.subRight s).symm]
  change
    (∑ i : ZMod n, x (i + s - s) * χ (i + s)) =
      χ s * ∑ i : ZMod n, x i * χ i
  calc
    (∑ i : ZMod n, x (i + s - s) * χ (i + s))
        = ∑ i : ZMod n, x i * (χ i * χ s) := by
          refine Finset.sum_congr rfl (fun i _ => ?_)
          simp [CyclicCharacter.map_add]
    _ = ∑ i : ZMod n, (x i * χ i) * χ s := by
          refine Finset.sum_congr rfl (fun i _ => ?_)
          simp [mul_assoc]
    _ = (∑ i : ZMod n, x i * χ i) * χ s := by
          rw [Finset.sum_mul]
    _ = χ s * ∑ i : ZMod n, x i * χ i := by
          rw [mul_comm]

end Fourier

end Circle
