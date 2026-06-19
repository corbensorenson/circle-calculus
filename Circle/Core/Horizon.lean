import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Order.Interval.Finset.Nat

namespace Circle

/-- Integer form of an exact primitive-horizon angle collision.

`primitiveHorizonCollision n d k` records the cancelled equation
`k / n = 1 / d` as the multiplication law `k * d = n`. -/
def primitiveHorizonCollision (n d k : Nat) : Prop :=
  k * d = n

/-- A primitive `d`-horizon is contained in the `n`-horizon exactly when `d`
divides `n`. This is the exact arithmetic form used by the Rust prime engine. -/
def primitiveHorizonContained (n d : Nat) : Prop :=
  d ∣ n

/-- A prime horizon is a finite circle size with no nontrivial smaller
primitive horizon contained in it. This is ordinary `Nat.Prime` exposed under
the Circle-prime vocabulary used by the Rust engine diagnostics. -/
def primeHorizon (n : Nat) : Prop :=
  Nat.Prime n

noncomputable instance instDecidablePredPrimeHorizon : DecidablePred primeHorizon := by
  classical
  infer_instance

/-- The finite set of prime horizons in the half-open interval `[low, high)`. -/
noncomputable def primeHorizonsInRange (low high : Nat) : Finset Nat := by
  classical
  exact (Finset.Ico low high).filter primeHorizon

/-- The exact mathematical range-count target for the Rust count modes. -/
noncomputable def primeHorizonRangeCount (low high : Nat) : Nat :=
  (primeHorizonsInRange low high).card

theorem primitiveHorizonCollision_exists_iff_dvd (n d : Nat) :
    (∃ k, primitiveHorizonCollision n d k) ↔ d ∣ n := by
  constructor
  · intro h
    rcases h with ⟨k, hk⟩
    refine ⟨k, ?_⟩
    rw [Nat.mul_comm]
    exact hk.symm
  · intro h
    rcases h with ⟨k, hk⟩
    refine ⟨k, ?_⟩
    unfold primitiveHorizonCollision
    rw [Nat.mul_comm]
    exact hk.symm

theorem primitiveHorizonContained_iff_dvd (n d : Nat) :
    primitiveHorizonContained n d ↔ d ∣ n := by
  rfl

theorem mem_primeHorizonsInRange_iff {low high n : Nat} :
    n ∈ primeHorizonsInRange low high ↔ low ≤ n ∧ n < high ∧ primeHorizon n := by
  classical
  unfold primeHorizonsInRange
  simp [and_left_comm, and_comm]

theorem primeHorizonRangeCount_eq_filter_card (low high : Nat) :
    primeHorizonRangeCount low high = ((Finset.Ico low high).filter primeHorizon).card := by
  classical
  rfl

theorem primitiveHorizonCollision_div_skip {n d : Nat} (hd : d ∣ n) :
    primitiveHorizonCollision n d (n / d) := by
  unfold primitiveHorizonCollision
  exact Nat.div_mul_cancel hd

theorem primeHorizon_iff_no_smaller_contained {n : Nat} :
    primeHorizon n ↔
      2 ≤ n ∧ ∀ d, 2 ≤ d → d < n → ¬ primitiveHorizonContained n d := by
  unfold primeHorizon primitiveHorizonContained
  exact Nat.prime_def_lt'

theorem primeHorizon_iff_no_sqrt_contained {n : Nat} :
    primeHorizon n ↔
      2 ≤ n ∧ ∀ d, 2 ≤ d → d ≤ Nat.sqrt n → ¬ primitiveHorizonContained n d := by
  unfold primeHorizon primitiveHorizonContained
  exact Nat.prime_def_le_sqrt

theorem primeHorizon_of_no_sqrt_contained {n : Nat}
    (hn2 : 2 ≤ n)
    (hnone : ∀ d, 2 ≤ d → d ≤ Nat.sqrt n → ¬ primitiveHorizonContained n d) :
    primeHorizon n := by
  exact primeHorizon_iff_no_sqrt_contained.mpr ⟨hn2, hnone⟩

theorem primeHorizon_no_sqrt_contained {n d : Nat}
    (hn : primeHorizon n) (hd2 : 2 ≤ d) (hdsqrt : d ≤ Nat.sqrt n) :
    ¬ primitiveHorizonContained n d := by
  exact (primeHorizon_iff_no_sqrt_contained.mp hn).2 d hd2 hdsqrt

theorem primeHorizon_no_smaller_contained {n d : Nat}
    (hn : primeHorizon n) (hd2 : 2 ≤ d) (hdlt : d < n) :
    ¬ primitiveHorizonContained n d := by
  exact (primeHorizon_iff_no_smaller_contained.mp hn).2 d hd2 hdlt

theorem not_primeHorizon_has_sqrt_contained {n : Nat}
    (hn2 : 2 ≤ n) (hnot : ¬ primeHorizon n) :
    ∃ d, 2 ≤ d ∧ d ≤ Nat.sqrt n ∧ primitiveHorizonContained n d := by
  by_contra hnone
  apply hnot
  rw [primeHorizon_iff_no_sqrt_contained]
  refine ⟨hn2, ?_⟩
  intro d hd2 hdsqrt hdvd
  apply hnone
  exact ⟨d, hd2, hdsqrt, hdvd⟩

theorem not_primeHorizon_has_smaller_contained {n : Nat}
    (hn2 : 2 ≤ n) (hnot : ¬ primeHorizon n) :
    ∃ d, 2 ≤ d ∧ d < n ∧ primitiveHorizonContained n d := by
  by_contra hnone
  apply hnot
  rw [primeHorizon_iff_no_smaller_contained]
  refine ⟨hn2, ?_⟩
  intro d hd2 hdlt hdvd
  apply hnone
  exact ⟨d, hd2, hdlt, hdvd⟩

end Circle
