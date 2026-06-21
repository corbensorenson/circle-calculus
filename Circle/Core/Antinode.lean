import Circle.Core.Orbit
import Circle.Core.Prime
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Nat.Choose.Basic

namespace Circle

/-!
Abstract chord and antinode bookkeeping.

This module is intentionally finite and combinatorial.  It models the old
coil-network "antinode" code as endpoint interleaving among normalized chord
endpoints, not as Euclidean embedded geometry.
-/

/-- The forward endpoint-interleaving pattern for two normalized chords. -/
def chordCrosses (a b c d : Nat) : Prop :=
  a < c ∧ c < b ∧ b < d

/--
The crossing predicate used in older Python scans.  For normalized endpoint
order on the second chord, its second disjunct is impossible and it reduces to
`chordCrosses`.
-/
def oldScanCrosses (a b c d : Nat) : Prop :=
  a < c ∧ c < b ∧ (b < d ∨ d < a)

theorem chordCrosses_endpoint_order {a b c d : Nat} (h : chordCrosses a b c d) :
    a < b ∧ c < d := by
  exact ⟨Nat.lt_trans h.1 h.2.1, Nat.lt_trans h.2.1 h.2.2⟩

theorem chordCrosses_not_reverse {a b c d : Nat} (h : chordCrosses a b c d) :
    ¬ chordCrosses c d a b := by
  intro hr
  exact (Nat.lt_asymm h.1 hr.1)

theorem oldScanCrosses_iff_chordCrosses_of_sorted {a b c d : Nat} (hcd : c < d) :
    oldScanCrosses a b c d ↔ chordCrosses a b c d := by
  unfold oldScanCrosses chordCrosses
  constructor
  · intro h
    rcases h with ⟨hac, hcb, hbd | hda⟩
    · exact ⟨hac, hcb, hbd⟩
    · have hca : c < a := Nat.lt_trans hcd hda
      exact False.elim ((Nat.lt_asymm hac) hca)
  · intro h
    exact ⟨h.1, h.2.1, Or.inl h.2.2⟩

/--
A forward non-spoke stride is one of the path families used by the old coil
network code: skip 0 and skip 1 are excluded, and the stride stays strictly
before the midpoint so the reverse chord family is not duplicated.
-/
def nonSpokeForwardStride (n k : Nat) : Prop :=
  1 < k ∧ 2 * k < n

/-- A prime-angle stride is a forward non-spoke stride that is also a full coil. -/
def primeAngleStride (n k : Nat) : Prop :=
  nonSpokeForwardStride n k ∧ fullCoil n k

theorem primeAngleStride_fullCoil {n k : Nat} (h : primeAngleStride n k) :
    fullCoil n k := by
  exact h.2

theorem primeAngleStride_of_prime {p k : Nat} (hp : Nat.Prime p)
    (hstride : nonSpokeForwardStride p k) :
    primeAngleStride p k := by
  refine ⟨hstride, ?_⟩
  have hk0 : 0 < k := Nat.lt_trans Nat.zero_lt_one hstride.1
  have hkle : k ≤ 2 * k := Nat.le_mul_of_pos_left k (by decide : 0 < 2)
  have hkp : k < p := lt_of_le_of_lt hkle hstride.2
  exact prime_full_coil hp hk0 hkp

/--
For an odd prime-sized node set, the old prime-network code iterates exactly
the non-boundary, non-reversed path families `2, ..., (p-1)/2`.
-/
def primeChordPathCount (n : Nat) : Nat :=
  (n - 3) / 2

theorem primeChordPathCount_eq (n : Nat) :
    primeChordPathCount n = (n - 3) / 2 := by
  rfl

theorem primeChordPathCount_examples :
    primeChordPathCount 5 = 1 ∧
      primeChordPathCount 7 = 2 ∧
      primeChordPathCount 11 = 4 ∧
      primeChordPathCount 13 = 5 ∧
      primeChordPathCount 17 = 7 ∧
      primeChordPathCount 19 = 8 ∧
      primeChordPathCount 23 = 10 := by
  native_decide

/--
The full abstract chord network has one interior crossing certificate for each
4-subset of boundary nodes.
-/
def fullChordNetworkAntinodeCount (n : Nat) : Nat :=
  n.choose 4

/--
The finite certificate set for full chord-network antinodes: each 4-node subset
of the boundary determines the crossing of the two opposite chords in that
cyclic order.
-/
def fullChordAntinodeCertificates (n : Nat) : Finset (Finset (Fin n)) :=
  Finset.univ.powersetCard 4

theorem fullChordNetworkAntinodeCount_eq_choose (n : Nat) :
    fullChordNetworkAntinodeCount n = n.choose 4 := by
  rfl

theorem fullChordAntinodeCertificates_card (n : Nat) :
    (fullChordAntinodeCertificates n).card = n.choose 4 := by
  unfold fullChordAntinodeCertificates
  rw [Finset.card_powersetCard]
  simp

theorem fullChordNetworkAntinodeCount_eq_certificate_card (n : Nat) :
    fullChordNetworkAntinodeCount n = (fullChordAntinodeCertificates n).card := by
  rw [fullChordNetworkAntinodeCount_eq_choose, fullChordAntinodeCertificates_card]

theorem fullChordNetworkAntinodeCount_prime_examples :
    fullChordNetworkAntinodeCount 5 = 5 ∧
      fullChordNetworkAntinodeCount 7 = 35 ∧
      fullChordNetworkAntinodeCount 11 = 330 ∧
      fullChordNetworkAntinodeCount 13 = 715 ∧
      fullChordNetworkAntinodeCount 17 = 2380 ∧
      fullChordNetworkAntinodeCount 19 = 3876 ∧
      fullChordNetworkAntinodeCount 23 = 8855 ∧
      fullChordNetworkAntinodeCount 29 = 23751 ∧
      fullChordNetworkAntinodeCount 31 = 31465 := by
  native_decide

/-- The subcoil count is the existing stride-orbit class count under old terminology. -/
noncomputable def subcoilCount (n k : Nat) : Nat :=
  orbitClassCount n k

theorem subcoil_count_eq_gcd {n k : Nat} (hn : n ≠ 0) :
    subcoilCount n k = Nat.gcd n k := by
  exact orbit_decomposition_count hn

theorem prime_subcoil_count_one {p k : Nat} (hp : Nat.Prime p)
    (hk0 : 0 < k) (hkp : k < p) :
    subcoilCount p k = 1 := by
  rw [subcoil_count_eq_gcd hp.ne_zero]
  have hcop : Nat.Coprime p k := Nat.coprime_of_lt_prime hk0.ne' hkp hp
  exact Nat.coprime_iff_gcd_eq_one.mp hcop

end Circle
