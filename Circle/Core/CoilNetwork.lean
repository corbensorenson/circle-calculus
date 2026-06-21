import Circle.Core.Antinode

namespace Circle

/-!
Finite coil-network bookkeeping from the Drive notes.

The definitions here keep FCN/PCN/CCN terminology at the same abstraction level
as the old code: a network is represented by a finite node count and a stride
family, not by embedded Euclidean line segments.
-/

/-- A full coil-network stride is any forward non-spoke stride under consideration. -/
def fullCoilNetworkStride (n k : Nat) : Prop :=
  nonSpokeForwardStride n k

/-- A prime coil-network stride is a forward non-spoke stride that traverses one full coil. -/
def primeCoilNetworkStride (n k : Nat) : Prop :=
  nonSpokeForwardStride n k ∧ fullCoil n k

/-- A composite coil-network stride is a forward non-spoke stride that is not full. -/
def compositeCoilNetworkStride (n k : Nat) : Prop :=
  nonSpokeForwardStride n k ∧ ¬ fullCoil n k

theorem primeCoilNetworkStride_full {n k : Nat} (h : primeCoilNetworkStride n k) :
    fullCoilNetworkStride n k := by
  exact h.1

theorem primeCoilNetworkStride_fullCoil {n k : Nat} (h : primeCoilNetworkStride n k) :
    fullCoil n k := by
  exact h.2

theorem compositeCoilNetworkStride_full {n k : Nat}
    (h : compositeCoilNetworkStride n k) :
    fullCoilNetworkStride n k := by
  exact h.1

theorem compositeCoilNetworkStride_not_prime {n k : Nat}
    (h : compositeCoilNetworkStride n k) :
    ¬ primeCoilNetworkStride n k := by
  intro hp
  exact h.2 hp.2

theorem fullCoilNetworkStride_iff_prime_or_composite (n k : Nat) :
    fullCoilNetworkStride n k ↔
      primeCoilNetworkStride n k ∨ compositeCoilNetworkStride n k := by
  unfold fullCoilNetworkStride primeCoilNetworkStride compositeCoilNetworkStride
  constructor
  · intro h
    by_cases hf : fullCoil n k
    · exact Or.inl ⟨h, hf⟩
    · exact Or.inr ⟨h, hf⟩
  · intro h
    cases h with
    | inl hp => exact hp.1
    | inr hc => exact hc.1

theorem primeCircle_fullNetworkStride_is_prime {p k : Nat} (hp : Nat.Prime p)
    (h : fullCoilNetworkStride p k) :
    primeCoilNetworkStride p k := by
  have hpa := primeAngleStride_of_prime hp h
  exact ⟨hpa.1, hpa.2⟩

/-- A midpoint spoke is the excluded diameter-like stride `k = n/2`. -/
def spokeStride (n k : Nat) : Prop :=
  2 * k = n

theorem spokeStride_not_nonSpokeForwardStride {n k : Nat} (h : spokeStride n k) :
    ¬ nonSpokeForwardStride n k := by
  intro hstride
  have hn : n = 2 * k := h.symm
  have hlt : 2 * k < 2 * k := by
    simpa [hn] using hstride.2
  exact (Nat.lt_irrefl (2 * k)) hlt

/-! ### White-paper skip terminology -/

/--
The older Primecoin/(ed) drafts name chord families by a `skip` count.  A skip
of `0` means stride `1`, a skip of `4` means stride `5`, and so on.
-/
def whitePaperSkipStride (skip : Nat) : Nat :=
  skip + 1

/--
The skip families considered by the older prose stop before the midpoint
diameter/spoke.  Unlike `nonSpokeForwardStride`, this keeps skip `0` because
the Primecoin draft calls the base angle prime.
-/
def whitePaperForwardSkip (n skip : Nat) : Prop :=
  2 * whitePaperSkipStride skip < n

instance whitePaperForwardSkip_decidable (n skip : Nat) :
    Decidable (whitePaperForwardSkip n skip) := by
  unfold whitePaperForwardSkip
  infer_instance

/--
A white-paper prime-angle skip is a forward skip whose induced stride is
coprime to the node count, equivalently a full coil when `n ≠ 0`.
-/
def whitePaperPrimeAngleSkip (n skip : Nat) : Prop :=
  whitePaperForwardSkip n skip ∧ Nat.gcd n (whitePaperSkipStride skip) = 1

instance whitePaperPrimeAngleSkip_decidable (n skip : Nat) :
    Decidable (whitePaperPrimeAngleSkip n skip) := by
  unfold whitePaperPrimeAngleSkip
  infer_instance

theorem whitePaperPrimeAngleSkip_fullCoil {n skip : Nat} (hn : n ≠ 0)
    (h : whitePaperPrimeAngleSkip n skip) :
    fullCoil n (whitePaperSkipStride skip) := by
  exact (fullCoil_iff_coprime hn).2 (Nat.coprime_iff_gcd_eq_one.2 h.2)

theorem whitePaperPrimeAngleSkip_of_prime {p skip : Nat} (hp : Nat.Prime p)
    (hskip : whitePaperForwardSkip p skip) :
    whitePaperPrimeAngleSkip p skip := by
  refine ⟨hskip, ?_⟩
  have hs0 : 0 < whitePaperSkipStride skip := by
    unfold whitePaperSkipStride
    exact Nat.succ_pos skip
  have hle : whitePaperSkipStride skip ≤ 2 * whitePaperSkipStride skip := by
    exact Nat.le_mul_of_pos_left (whitePaperSkipStride skip) (by decide : 0 < 2)
  have hsp : whitePaperSkipStride skip < p := lt_of_le_of_lt hle hskip
  exact Nat.coprime_iff_gcd_eq_one.1 (Nat.coprime_of_lt_prime hs0.ne' hsp hp)

theorem whitePaperPrimeAngleSkips12_eq :
    ((List.range 5).filter (fun skip => decide (whitePaperPrimeAngleSkip 12 skip))) =
      [0, 4] := by
  native_decide

theorem whitePaperPrimeAngleSkips13_eq :
    ((List.range 6).filter (fun skip => decide (whitePaperPrimeAngleSkip 13 skip))) =
      [0, 1, 2, 3, 4, 5] := by
  native_decide

theorem whitePaperPrimeAngleSkips13_all_forward {skip : Nat}
    (hskip : whitePaperForwardSkip 13 skip) :
    whitePaperPrimeAngleSkip 13 skip := by
  exact whitePaperPrimeAngleSkip_of_prime (by native_decide) hskip

/-- A factor-sized subcoil exists exactly when its visible node count divides the host. -/
def factorSubcoilExists (n d : Nat) : Prop :=
  d ∣ n

/-- Number of disjoint factor-sized subcoil copies inside a host node count. -/
def factorSubcoilCopies (n d : Nat) : Nat :=
  n / d

theorem factorSubcoilCopies_mul {n d : Nat} (h : factorSubcoilExists n d) :
    factorSubcoilCopies n d * d = n := by
  unfold factorSubcoilCopies factorSubcoilExists at *
  exact Nat.div_mul_cancel h

theorem factorSubcoilCopies_18_examples :
    factorSubcoilCopies 18 3 = 6 ∧
      factorSubcoilCopies 18 9 = 2 ∧
      factorSubcoilCopies 72 18 = 4 := by
  native_decide

/-- Total concrete nodes represented by a coil map with fixed-size node fibers. -/
def coilMapTotalNodes (mapNodes fiber : Nat) : Nat :=
  mapNodes * fiber

/-- Start of the concrete block represented by visible map node `i`. -/
def coilMapBlockStart (fiber i : Nat) : Nat :=
  i * fiber

/-- Exclusive end of the concrete block represented by visible map node `i`. -/
def coilMapBlockEnd (fiber i : Nat) : Nat :=
  (i + 1) * fiber

theorem coilMapTotalNodes_18_4 :
    coilMapTotalNodes 18 4 = 72 := by
  native_decide

theorem coilMapBlockWidth (fiber i : Nat) :
    coilMapBlockEnd fiber i - coilMapBlockStart fiber i = fiber := by
  unfold coilMapBlockEnd coilMapBlockStart
  rw [Nat.add_mul, Nat.one_mul, Nat.add_sub_cancel_left]

theorem coilMapBlockStart_lt_blockEnd {fiber i : Nat} (hf : 0 < fiber) :
    coilMapBlockStart fiber i < coilMapBlockEnd fiber i := by
  unfold coilMapBlockStart coilMapBlockEnd
  rw [Nat.add_mul, Nat.one_mul]
  exact Nat.lt_add_of_pos_right hf

end Circle
