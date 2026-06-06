import Circle.Common.Scaffold
import Mathlib.Data.Finite.Card

namespace Circle.S0

inductive Sign
  | neg
  | pos
deriving DecidableEq, Repr

def antipode : Sign -> Sign
  | Sign.neg => Sign.pos
  | Sign.pos => Sign.neg

def signEquivBool : Sign ≃ Bool where
  toFun
    | Sign.neg => false
    | Sign.pos => true
  invFun
    | false => Sign.neg
    | true => Sign.pos
  left_inv := by
    intro x
    cases x <;> rfl
  right_inv := by
    intro x
    cases x <;> rfl

instance : Finite Sign :=
  Finite.of_equiv Bool signEquivBool.symm

theorem card_sign : Nat.card Sign = 2 :=
  Nat.card_eq_of_equiv_fin (signEquivBool.trans finTwoEquiv.symm)

theorem antipode_involutive (x : Sign) : antipode (antipode x) = x := by
  cases x <;> rfl

theorem antipode_ne (x : Sign) : antipode x ≠ x := by
  cases x <;> intro h <;> cases h

theorem antipode_swaps :
    antipode Sign.neg = Sign.pos ∧ antipode Sign.pos = Sign.neg := by
  constructor <;> rfl

theorem antipode_bijective : Function.Bijective antipode := by
  constructor
  · intro x y h
    cases x <;> cases y <;> simp [antipode] at h ⊢
  · intro y
    exact ⟨antipode y, antipode_involutive y⟩

end Circle.S0
