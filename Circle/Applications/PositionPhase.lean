import Mathlib.Data.Nat.ModEq
import Mathlib.Data.List.Basic

/-!
# General phase-bank positional encoding contracts

This file factors the integer residue core out of the RoPE-specific certifier.
The model is intentionally finite and exact: a phase channel is represented by
a declared positive or zero period, and a token position is observed through its
residue modulo that period.

The engineering use is broader than RoPE. Sinusoidal positional encodings, RoPE
families, xPos/YaRN/LongRoPE-style rescalings, and 2D rotary grids can all export
finite declared period banks and cite the same collision/distinguishability
theorems here. Real-valued approximation margins remain separate executable
contracts; the proved claim in this file is the exact integer phase-bank layer.
-/

namespace Circle.Applications

/-! ### Single finite phase channel -/

/-- The residue seen by one finite positional phase channel. -/
def phaseResidue (period position : Nat) : Nat :=
  position % period

/-- Two positions collide in a finite phase channel when they have the same
residue modulo that channel's declared period. -/
def phaseChannelCollision (period left right : Nat) : Prop :=
  phaseResidue period left = phaseResidue period right

/-- A finite phase channel distinguishes two positions when they do not collide
in that channel. -/
def phaseChannelDistinguishable (period left right : Nat) : Prop :=
  ¬ phaseChannelCollision period left right

/-- Exact single-channel collision criterion: for ordered positions, equality
of residues modulo the declared period is equivalent to the period dividing the
position gap. -/
theorem phaseChannelCollision_iff_gap_dvd
    {period left right : Nat} (hleft : left ≤ right) :
    phaseChannelCollision period left right ↔ period ∣ right - left := by
  unfold phaseChannelCollision phaseResidue
  exact Nat.modEq_iff_dvd' hleft

/-- Exact single-channel distinguishability criterion. -/
theorem phaseChannelDistinguishable_iff_not_gap_dvd
    {period left right : Nat} (hleft : left ≤ right) :
    phaseChannelDistinguishable period left right ↔ ¬ period ∣ right - left := by
  unfold phaseChannelDistinguishable
  rw [phaseChannelCollision_iff_gap_dvd hleft]

/-- If the inspected context fits inside one declared period, the channel is
injective on the context range: residue collision is exactly position equality. -/
theorem phaseChannelCollision_iff_eq_on_context
    {period context left right : Nat}
    (hcontext : context ≤ period) (hleft : left < context) (hright : right < context) :
    phaseChannelCollision period left right ↔ left = right := by
  unfold phaseChannelCollision phaseResidue
  have hleft_period : left < period := lt_of_lt_of_le hleft hcontext
  have hright_period : right < period := lt_of_lt_of_le hright hcontext
  rw [Nat.mod_eq_of_lt hleft_period, Nat.mod_eq_of_lt hright_period]

/-! ### Finite phase-bank contract -/

/-- A finite phase bank collides when every declared channel period collides. -/
def phaseBankCollision (periods : List Nat) (left right : Nat) : Prop :=
  ∀ period, period ∈ periods → phaseChannelCollision period left right

/-- A finite phase bank distinguishes two positions when at least one declared
channel period distinguishes them. -/
def phaseBankDistinguishable (periods : List Nat) (left right : Nat) : Prop :=
  ∃ period, period ∈ periods ∧ phaseChannelDistinguishable period left right

/-- Exact finite-bank collision criterion: an ordered pair collides in every
declared channel iff every declared period divides the position gap. -/
theorem phaseBankCollision_iff_forall_gap_dvd
    {periods : List Nat} {left right : Nat} (hleft : left ≤ right) :
    phaseBankCollision periods left right ↔
      ∀ period, period ∈ periods → period ∣ right - left := by
  constructor
  · intro hcollision period hmem
    exact (phaseChannelCollision_iff_gap_dvd (period := period) hleft).1
      (hcollision period hmem)
  · intro hdivides period hmem
    exact (phaseChannelCollision_iff_gap_dvd (period := period) hleft).2
      (hdivides period hmem)

/-- Exact finite-bank distinguishability criterion: an ordered pair is
distinguished by the phase bank iff some declared period does not divide the
position gap. -/
theorem phaseBankDistinguishable_iff_exists_not_gap_dvd
    {periods : List Nat} {left right : Nat} (hleft : left ≤ right) :
    phaseBankDistinguishable periods left right ↔
      ∃ period, period ∈ periods ∧ ¬ period ∣ right - left := by
  unfold phaseBankDistinguishable phaseChannelDistinguishable
  constructor
  · rintro ⟨period, hmem, hdistinguish⟩
    exact ⟨period, hmem,
      mt (phaseChannelCollision_iff_gap_dvd (period := period) hleft).2 hdistinguish⟩
  · rintro ⟨period, hmem, hnotdvd⟩
    exact ⟨period, hmem,
      mt (phaseChannelCollision_iff_gap_dvd (period := period) hleft).1 hnotdvd⟩

/-- If a phase bank contains a period at least as large as the inspected
context, then that bank distinguishes every unequal pair inside the context. -/
theorem phaseBankDistinguishable_of_period_ge_context
    {periods : List Nat} {period context left right : Nat}
    (hmem : period ∈ periods) (hcontext : context ≤ period)
    (hleft : left < context) (hright : right < context) (hne : left ≠ right) :
    phaseBankDistinguishable periods left right := by
  refine ⟨period, hmem, ?_⟩
  unfold phaseChannelDistinguishable
  intro hcollision
  exact hne ((phaseChannelCollision_iff_eq_on_context hcontext hleft hright).1 hcollision)

/-- Collision is contravariant under adding channels: if a larger declared
phase bank collides, then any sub-bank also collides. -/
theorem phaseBankCollision_of_subset
    {periods extended : List Nat} {left right : Nat}
    (hsubset : ∀ period, period ∈ periods → period ∈ extended)
    (hcollision : phaseBankCollision extended left right) :
    phaseBankCollision periods left right := by
  intro period hmem
  exact hcollision period (hsubset period hmem)

/-- Distinguishability is monotone under adding channels: a witness channel in
a sub-bank remains a witness in any larger declared bank. -/
theorem phaseBankDistinguishable_of_subset
    {periods extended : List Nat} {left right : Nat}
    (hsubset : ∀ period, period ∈ periods → period ∈ extended)
    (hdistinguish : phaseBankDistinguishable periods left right) :
    phaseBankDistinguishable extended left right := by
  rcases hdistinguish with ⟨period, hmem, hchannel⟩
  exact ⟨period, hsubset period hmem, hchannel⟩

/-! ### Product grids and scaled declared periods -/

/-- A two-axis phase grid collides exactly when both axis banks collide. This is
the finite contract behind 2D RoPE-style row/column phase products. -/
def phaseGrid2DCollision
    (xPeriods yPeriods : List Nat) (leftX rightX leftY rightY : Nat) : Prop :=
  phaseBankCollision xPeriods leftX rightX ∧
    phaseBankCollision yPeriods leftY rightY

/-- The two-axis grid collision predicate is just the conjunction of the two
axis-bank collision predicates. -/
theorem phaseGrid2DCollision_iff_axes
    {xPeriods yPeriods : List Nat} {leftX rightX leftY rightY : Nat} :
    phaseGrid2DCollision xPeriods yPeriods leftX rightX leftY rightY ↔
      phaseBankCollision xPeriods leftX rightX ∧
        phaseBankCollision yPeriods leftY rightY := by
  rfl

/-- Scale a declared finite phase period by an integer factor. This models the
integer contract layer of interpolation and extension schemes. -/
def scaledPhasePeriod (scale period : Nat) : Nat :=
  scale * period

/-- Scale every declared period in a phase bank by the same integer factor. -/
def scaledPhasePeriodBank (scale : Nat) (periods : List Nat) : List Nat :=
  periods.map (scaledPhasePeriod scale)

/-- Positive scales preserve positive declared periods. -/
theorem scaledPhasePeriod_pos
    {scale period : Nat} (hscale : 0 < scale) (hperiod : 0 < period) :
    0 < scaledPhasePeriod scale period := by
  unfold scaledPhasePeriod
  exact Nat.mul_pos hscale hperiod

/-- A positive scale maps a positive declared phase bank to another positive
declared phase bank. -/
theorem scaledPhasePeriodBank_all_pos
    {scale : Nat} {periods : List Nat}
    (hscale : 0 < scale)
    (hperiods : ∀ period, period ∈ periods → 0 < period) :
    ∀ period, period ∈ scaledPhasePeriodBank scale periods → 0 < period := by
  intro period hmem
  unfold scaledPhasePeriodBank at hmem
  rw [List.mem_map] at hmem
  rcases hmem with ⟨base, hbase, rfl⟩
  exact scaledPhasePeriod_pos hscale (hperiods base hbase)

end Circle.Applications
