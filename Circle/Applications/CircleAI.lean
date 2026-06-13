import Mathlib.Data.Nat.ModEq
import Mathlib.Tactic.Ring

/-!
Application seeds for Circle AI tracks.

These definitions formalize finite schedule/indexing primitives for AI
experiments. They do not prove model quality, efficiency, or general AI
improvement.
-/

namespace Circle.Applications

def phaseChannel (period position : Nat) : Nat :=
  position % period

theorem phaseChannel_lt_period {period : Nat} (h : 0 < period) (position : Nat) :
    phaseChannel period position < period := by
  unfold phaseChannel
  exact Nat.mod_lt position h

theorem phaseChannel_add_period {period : Nat} (h : 0 < period) (position : Nat) :
    phaseChannel period (position + period) = phaseChannel period position := by
  unfold phaseChannel
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt position h)

theorem phaseChannel_add_mul_period {period : Nat} (_h : 0 < period)
    (position passes : Nat) :
    phaseChannel period (position + passes * period) = phaseChannel period position := by
  unfold phaseChannel
  exact Nat.add_mul_mod_self_right position passes period

theorem phaseChannel_idempotent (period position : Nat) :
    phaseChannel period (phaseChannel period position) = phaseChannel period position := by
  unfold phaseChannel
  by_cases h : period = 0
  · simp [h]
  · exact Nat.mod_eq_of_lt (Nat.mod_lt position (Nat.pos_of_ne_zero h))

theorem phaseChannel_zero (period : Nat) :
    phaseChannel period 0 = 0 := by
  unfold phaseChannel
  simp

def multiPhase2 (periodA periodB position : Nat) : Nat × Nat :=
  (phaseChannel periodA position, phaseChannel periodB position)

theorem multiPhase2_fst_lt_periodA {periodA : Nat} (hA : 0 < periodA)
    (periodB position : Nat) :
    (multiPhase2 periodA periodB position).fst < periodA := by
  unfold multiPhase2
  exact phaseChannel_lt_period hA position

theorem multiPhase2_snd_lt_periodB {periodB : Nat} (hB : 0 < periodB)
    (periodA position : Nat) :
    (multiPhase2 periodA periodB position).snd < periodB := by
  unfold multiPhase2
  exact phaseChannel_lt_period hB position

theorem multiPhase2_zero (periodA periodB : Nat) :
    multiPhase2 periodA periodB 0 = (0, 0) := by
  unfold multiPhase2
  simp [phaseChannel_zero]

theorem multiPhase2_add_periodProduct {periodA periodB : Nat}
    (hA : 0 < periodA) (hB : 0 < periodB) (position : Nat) :
    multiPhase2 periodA periodB (position + periodA * periodB) =
      multiPhase2 periodA periodB position := by
  unfold multiPhase2
  apply Prod.ext
  · rw [Nat.mul_comm periodA periodB]
    exact phaseChannel_add_mul_period hA position periodB
  · exact phaseChannel_add_mul_period hB position periodA

theorem multiPhase2_add_mul_periodProduct {periodA periodB : Nat}
    (hA : 0 < periodA) (hB : 0 < periodB) (position passes : Nat) :
    multiPhase2 periodA periodB (position + passes * (periodA * periodB)) =
      multiPhase2 periodA periodB position := by
  unfold multiPhase2
  apply Prod.ext
  · rw [
      show passes * (periodA * periodB) =
        (passes * periodB) * periodA by ac_rfl,
    ]
    exact phaseChannel_add_mul_period hA position (passes * periodB)
  · rw [
      show passes * (periodA * periodB) =
        (passes * periodA) * periodB by ac_rfl,
    ]
    exact phaseChannel_add_mul_period hB position (passes * periodA)

def memorySlot (bankSize token : Nat) : Nat :=
  token % bankSize

theorem memorySlot_lt_bankSize {bankSize : Nat} (h : 0 < bankSize) (token : Nat) :
    memorySlot bankSize token < bankSize := by
  unfold memorySlot
  exact Nat.mod_lt token h

theorem memorySlot_add_bankSize {bankSize : Nat} (h : 0 < bankSize) (token : Nat) :
    memorySlot bankSize (token + bankSize) = memorySlot bankSize token := by
  unfold memorySlot
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt token h)

theorem memorySlot_add_mul_bankSize {bankSize : Nat} (_h : 0 < bankSize)
    (token passes : Nat) :
    memorySlot bankSize (token + passes * bankSize) = memorySlot bankSize token := by
  unfold memorySlot
  exact Nat.add_mul_mod_self_right token passes bankSize

theorem memorySlot_idempotent (bankSize token : Nat) :
    memorySlot bankSize (memorySlot bankSize token) = memorySlot bankSize token := by
  unfold memorySlot
  by_cases h : bankSize = 0
  · simp [h]
  · exact Nat.mod_eq_of_lt (Nat.mod_lt token (Nat.pos_of_ne_zero h))

theorem memorySlot_zero (bankSize : Nat) :
    memorySlot bankSize 0 = 0 := by
  unfold memorySlot
  simp

/-! ### Ring-buffer / KV-cache slot safety -/

/-- A KV-cache ring-buffer slot is the cyclic memory slot used by a token. -/
def kvCacheSlot (cacheSize token : Nat) : Nat :=
  token % cacheSize

/-- Two token positions collide in the same KV-cache ring-buffer slot. -/
def kvCacheSlotCollision (cacheSize left right : Nat) : Prop :=
  kvCacheSlot cacheSize left = kvCacheSlot cacheSize right

/-- A retained token is still inside the current ring-buffer window when it is
not in the future and its lag from the current token is smaller than the cache
size. -/
def kvCacheWindowContains (cacheSize current token : Nat) : Prop :=
  token ≤ current ∧ current - token < cacheSize

/-- The first token position still live in the KV-cache window ending at
`current`. If the cache is larger than the prefix seen so far, the window starts
at zero. -/
def kvCacheLiveWindowStart (cacheSize current : Nat) : Nat :=
  (current + 1) - cacheSize

/-- The number of live token positions in the KV-cache window ending at
`current`. -/
def kvCacheLiveWindowLength (cacheSize current : Nat) : Nat :=
  min cacheSize (current + 1)

/-- The explicit finite list of token positions still live in the KV-cache
window ending at `current`. -/
def kvCacheLiveWindowTokens (cacheSize current : Nat) : List Nat :=
  List.range'
    (kvCacheLiveWindowStart cacheSize current)
    (kvCacheLiveWindowLength cacheSize current)

theorem kvCacheSlot_lt_cacheSize {cacheSize : Nat} (h : 0 < cacheSize) (token : Nat) :
    kvCacheSlot cacheSize token < cacheSize := by
  unfold kvCacheSlot
  exact Nat.mod_lt token h

theorem kvCacheSlot_add_cacheSize {cacheSize : Nat} (h : 0 < cacheSize) (token : Nat) :
    kvCacheSlot cacheSize (token + cacheSize) = kvCacheSlot cacheSize token := by
  unfold kvCacheSlot
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt token h)

theorem kvCacheSlotCollision_iff_gap_dvd
    {cacheSize left right : Nat} (hleft : left ≤ right) :
    kvCacheSlotCollision cacheSize left right ↔ cacheSize ∣ right - left := by
  unfold kvCacheSlotCollision kvCacheSlot
  exact Nat.modEq_iff_dvd' hleft

/-- Two ordered token positions with a positive gap smaller than the cache size
cannot occupy the same KV-cache ring-buffer slot. -/
theorem kvCacheSlot_ne_of_positive_gap_lt_cache
    {cacheSize left right : Nat}
    (hleft : left < right) (hgap : right - left < cacheSize) :
    kvCacheSlot cacheSize left ≠ kvCacheSlot cacheSize right := by
  intro hcollision
  have hdvd : cacheSize ∣ right - left :=
    (kvCacheSlotCollision_iff_gap_dvd (cacheSize := cacheSize)
      (left := left) (right := right) (Nat.le_of_lt hleft)).1 hcollision
  have hgap_pos : 0 < right - left := Nat.sub_pos_of_lt hleft
  have hcache_le_gap : cacheSize ≤ right - left := Nat.le_of_dvd hgap_pos hdvd
  exact (not_lt.mpr hcache_le_gap) hgap

/-- If a token is still inside the retained KV-cache window at `current`, then
its next write to the same ring-buffer slot, `token + cacheSize`, occurs after
`current`. -/
theorem kvCacheWindow_nextOverwrite_after_current
    {cacheSize current token : Nat}
    (hwindow : kvCacheWindowContains cacheSize current token) :
    current < token + cacheSize := by
  rcases hwindow with ⟨htoken_current, hlag⟩
  have h := Nat.add_lt_add_right hlag token
  rw [Nat.sub_add_cancel htoken_current] at h
  simpa [Nat.add_comm] using h

/-- Retained-window membership is exactly the implementation-facing
next-overwrite boundary.

For a non-future token, being retained in the cache window is equivalent to
the next same-slot overwrite `token + cacheSize` occurring after `current`. -/
theorem kvCacheWindowContains_iff_current_lt_nextOverwrite
    {cacheSize current token : Nat} :
    kvCacheWindowContains cacheSize current token ↔
      token ≤ current ∧ current < token + cacheSize := by
  constructor
  · intro hwindow
    exact ⟨hwindow.1, kvCacheWindow_nextOverwrite_after_current hwindow⟩
  · rintro ⟨htoken_current, hcurrent_next⟩
    refine ⟨htoken_current, ?_⟩
    have hcurrent_next' : current < cacheSize + token := by
      simpa [Nat.add_comm] using hcurrent_next
    exact (Nat.sub_lt_iff_lt_add htoken_current).2 hcurrent_next'

/-- For a non-future token, being stale is exactly the next same-slot overwrite
having occurred at or before the current token.

This is the implementation-facing read guard: if the token is not retained and
is not in the future, the cache slot has already been reused by the time
`current` is read. -/
theorem not_kvCacheWindowContains_iff_nextOverwrite_le_current_of_le
    {cacheSize current token : Nat} (htoken_current : token ≤ current) :
    ¬ kvCacheWindowContains cacheSize current token ↔ token + cacheSize ≤ current := by
  constructor
  · intro hnot
    exact le_of_not_gt (fun hcurrent_next =>
      hnot ((kvCacheWindowContains_iff_current_lt_nextOverwrite).2
        ⟨htoken_current, hcurrent_next⟩))
  · intro hoverwritten hwindow
    exact (not_lt_of_ge hoverwritten) (kvCacheWindow_nextOverwrite_after_current hwindow)

/-- The explicit live-window list ends exactly one past `current`. -/
theorem kvCacheLiveWindowStart_add_length (cacheSize current : Nat) :
    kvCacheLiveWindowStart cacheSize current +
      kvCacheLiveWindowLength cacheSize current = current + 1 := by
  unfold kvCacheLiveWindowStart kvCacheLiveWindowLength
  by_cases hcache : cacheSize ≤ current + 1
  · rw [Nat.min_eq_left hcache]
    exact Nat.sub_add_cancel hcache
  · have hprefix : current + 1 ≤ cacheSize := le_of_not_ge hcache
    rw [Nat.min_eq_right hprefix, Nat.sub_eq_zero_of_le hprefix, Nat.zero_add]

/-- The generated live-window token list is exactly the retained-window
predicate. -/
theorem kvCacheWindowContains_iff_mem_liveWindowTokens
    {cacheSize current token : Nat} :
    kvCacheWindowContains cacheSize current token ↔
      token ∈ kvCacheLiveWindowTokens cacheSize current := by
  unfold kvCacheWindowContains kvCacheLiveWindowTokens
  rw [List.mem_range']
  unfold kvCacheLiveWindowStart kvCacheLiveWindowLength
  by_cases hcache : cacheSize ≤ current + 1
  · rw [Nat.min_eq_left hcache]
    constructor
    · intro hwindow
      have hcurrent_eq : current - token + token = current :=
        Nat.sub_add_cancel hwindow.1
      have hcurrent_eq' : current = token + (current - token) := by
        simpa [Nat.add_comm] using hcurrent_eq.symm
      have hupper :
          (current + 1 - cacheSize) + cacheSize = current + 1 :=
        Nat.sub_add_cancel hcache
      have hstart_le : current + 1 - cacheSize ≤ token := by
        rw [Nat.sub_le_iff_le_add, hcurrent_eq']
        omega
      refine ⟨token - (current + 1 - cacheSize), ?_, ?_⟩
      · have htoken_eq :
            current + 1 - cacheSize + (token - (current + 1 - cacheSize)) =
              token := by
          simpa [Nat.add_comm] using Nat.sub_add_cancel hstart_le
        omega
      · simpa [Nat.one_mul, Nat.add_comm] using (Nat.sub_add_cancel hstart_le).symm
    · rintro ⟨offset, hoffset, htoken⟩
      have hupper :
          (current + 1 - cacheSize) + cacheSize = current + 1 :=
        Nat.sub_add_cancel hcache
      have htoken_current : token ≤ current := by
        omega
      constructor
      · exact htoken_current
      · rw [Nat.sub_lt_iff_lt_add htoken_current]
        omega
  · have hprefix : current + 1 ≤ cacheSize := le_of_not_ge hcache
    rw [Nat.min_eq_right hprefix, Nat.sub_eq_zero_of_le hprefix]
    constructor
    · intro hwindow
      refine ⟨token, ?_, ?_⟩
      · exact Nat.lt_succ_of_le hwindow.1
      · simp
    · rintro ⟨offset, hoffset, htoken⟩
      have htoken_current : token ≤ current := by
        omega
      have hcurrent_lt_cache : current < cacheSize := by
        omega
      constructor
      · exact htoken_current
      · exact lt_of_le_of_lt (Nat.sub_le current token) hcurrent_lt_cache

/-- If an older token is still inside the retained KV-cache window, it cannot
share the current token's ring-buffer slot.

This is the current-read specialization of the positive-gap theorem: retained
non-current tokens have lag smaller than the cache size, so they are slot
distinct from the current token. -/
theorem kvCacheWindow_retainedSlot_ne_current_of_lt
    {cacheSize current token : Nat}
    (hwindow : kvCacheWindowContains cacheSize current token)
    (hstrict : token < current) :
    kvCacheSlot cacheSize token ≠ kvCacheSlot cacheSize current :=
  kvCacheSlot_ne_of_positive_gap_lt_cache hstrict hwindow.2

/-- Any two ordered tokens retained in the same KV-cache window occupy distinct
ring-buffer slots.

The older token's retained-window bound controls the entire gap to any newer
retained token before the current point, so the positive-gap slot-separation
theorem applies pairwise inside the retained window. -/
theorem kvCacheWindow_retainedSlots_ne_of_lt
    {cacheSize current older newer : Nat}
    (holder : kvCacheWindowContains cacheSize current older)
    (hnewer : kvCacheWindowContains cacheSize current newer)
    (hstrict : older < newer) :
    kvCacheSlot cacheSize older ≠ kvCacheSlot cacheSize newer := by
  refine kvCacheSlot_ne_of_positive_gap_lt_cache hstrict ?_
  have hgap_le : newer - older ≤ current - older :=
    Nat.sub_le_sub_right hnewer.1 older
  exact lt_of_le_of_lt hgap_le holder.2

/-- Any two distinct tokens retained in the same KV-cache window occupy
distinct ring-buffer slots.

This removes the caller's burden of ordering the two retained tokens before
applying the pairwise slot-separation theorem. -/
theorem kvCacheWindow_retainedSlots_ne_of_ne
    {cacheSize current left right : Nat}
    (hleftWindow : kvCacheWindowContains cacheSize current left)
    (hrightWindow : kvCacheWindowContains cacheSize current right)
    (hne : left ≠ right) :
    kvCacheSlot cacheSize left ≠ kvCacheSlot cacheSize right := by
  rcases lt_or_gt_of_ne hne with hlt | hgt
  · exact kvCacheWindow_retainedSlots_ne_of_lt hleftWindow hrightWindow hlt
  · intro hslot
    exact (kvCacheWindow_retainedSlots_ne_of_lt hrightWindow hleftWindow hgt) hslot.symm

/-- A batch of pairwise-distinct retained tokens maps to pairwise-distinct
KV-cache ring-buffer slots.

This is the finite batch-read version of the pairwise window theorem: if every
token in the requested batch is live in the current window and no two token
positions are the same, then their ring-buffer slots are all distinct. -/
theorem kvCacheWindow_retainedBatchSlots_pairwise_ne
    {cacheSize current : Nat} :
    ∀ {tokens : List Nat},
      (∀ token ∈ tokens, kvCacheWindowContains cacheSize current token) →
      List.Pairwise (fun left right => left ≠ right) tokens →
      List.Pairwise
        (fun left right => kvCacheSlot cacheSize left ≠ kvCacheSlot cacheSize right)
        tokens := by
  intro tokens
  induction tokens with
  | nil =>
      intro _hwindow _hpairwise
      exact List.Pairwise.nil
  | cons head tail ih =>
      intro hwindow hpairwise
      cases hpairwise with
      | cons hhead htail =>
          refine List.Pairwise.cons ?_ ?_
          · intro token htoken
            exact
              kvCacheWindow_retainedSlots_ne_of_ne
                (hwindow head (by simp))
                (hwindow token (by simp [htoken]))
                (hhead token htoken)
          · exact ih (fun token htoken => hwindow token (by simp [htoken])) htail

/-- A `Nodup` retained-token batch has `Nodup` ring-buffer slots. -/
theorem kvCacheWindow_retainedBatchSlotMap_nodup
    {cacheSize current : Nat} {tokens : List Nat}
    (hwindow : ∀ token ∈ tokens, kvCacheWindowContains cacheSize current token)
    (hnodup : tokens.Nodup) :
    (tokens.map (kvCacheSlot cacheSize)).Nodup := by
  rw [List.nodup_iff_pairwise_ne, List.pairwise_map]
  exact
    kvCacheWindow_retainedBatchSlots_pairwise_ne
      (cacheSize := cacheSize) (current := current) hwindow
      (List.nodup_iff_pairwise_ne.mp hnodup)

/-- The explicit live KV-cache window maps to duplicate-free ring-buffer slots.

This is the end-to-end live-window version of the retained-batch theorem: the
generated list contains exactly the retained positions, and every retained token
in that list occupies a distinct slot. -/
theorem kvCacheLiveWindowTokens_slotMap_nodup
    (cacheSize current : Nat) :
    ((kvCacheLiveWindowTokens cacheSize current).map
      (kvCacheSlot cacheSize)).Nodup := by
  apply kvCacheWindow_retainedBatchSlotMap_nodup
  · intro token htoken
    exact (kvCacheWindowContains_iff_mem_liveWindowTokens).2 htoken
  · unfold kvCacheLiveWindowTokens
    exact List.nodup_range'

def loopRequiredSteps (loopPeriod sample : Nat) : Nat :=
  phaseChannel loopPeriod sample + 1

theorem loopRequiredSteps_pos (loopPeriod sample : Nat) :
    0 < loopRequiredSteps loopPeriod sample := by
  unfold loopRequiredSteps
  exact Nat.succ_pos _

theorem loopRequiredSteps_le_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (sample : Nat) :
    loopRequiredSteps loopPeriod sample ≤ loopPeriod := by
  unfold loopRequiredSteps phaseChannel
  exact Nat.succ_le_of_lt (Nat.mod_lt sample h)

theorem loopRequiredSteps_add_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (sample : Nat) :
    loopRequiredSteps loopPeriod (sample + loopPeriod) =
      loopRequiredSteps loopPeriod sample := by
  unfold loopRequiredSteps
  rw [phaseChannel_add_period h]

theorem loopRequiredSteps_add_mul_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (sample passes : Nat) :
    loopRequiredSteps loopPeriod (sample + passes * loopPeriod) =
      loopRequiredSteps loopPeriod sample := by
  unfold loopRequiredSteps
  rw [phaseChannel_add_mul_period h]

def tokenRecurrenceBudget (loopPeriod token : Nat) : Nat :=
  loopRequiredSteps loopPeriod token

theorem tokenRecurrenceBudget_pos (loopPeriod token : Nat) :
    0 < tokenRecurrenceBudget loopPeriod token := by
  unfold tokenRecurrenceBudget
  exact loopRequiredSteps_pos loopPeriod token

theorem tokenRecurrenceBudget_add_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (token : Nat) :
    tokenRecurrenceBudget loopPeriod (token + loopPeriod) =
      tokenRecurrenceBudget loopPeriod token := by
  unfold tokenRecurrenceBudget
  exact loopRequiredSteps_add_loopPeriod h token

theorem tokenRecurrenceBudget_add_mul_loopPeriod {loopPeriod : Nat}
    (h : 0 < loopPeriod) (token passes : Nat) :
    tokenRecurrenceBudget loopPeriod (token + passes * loopPeriod) =
      tokenRecurrenceBudget loopPeriod token := by
  unfold tokenRecurrenceBudget
  exact loopRequiredSteps_add_mul_loopPeriod h token passes

theorem tokenRecurrenceBudget_le_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (token : Nat) :
    tokenRecurrenceBudget loopPeriod token ≤ loopPeriod := by
  unfold tokenRecurrenceBudget
  exact loopRequiredSteps_le_loopPeriod h token

theorem tokenRecurrenceBudget_zero (loopPeriod : Nat) :
    tokenRecurrenceBudget loopPeriod 0 = 1 := by
  unfold tokenRecurrenceBudget loopRequiredSteps
  rw [phaseChannel_zero]

def loopedRecurrentState (period budget : Nat) : Nat :=
  phaseChannel period (budget - 1)

theorem loopedRecurrentState_lt_period {period : Nat} (h : 0 < period)
    (budget : Nat) :
    loopedRecurrentState period budget < period := by
  unfold loopedRecurrentState
  exact phaseChannel_lt_period h (budget - 1)

theorem loopedRecurrentState_one_zero (period : Nat) :
    loopedRecurrentState period 1 = 0 := by
  unfold loopedRecurrentState phaseChannel
  simp

theorem loopedRecurrentState_of_requiredSteps
    (period sample : Nat) :
    loopedRecurrentState period (loopRequiredSteps period sample) =
      phaseChannel period sample := by
  unfold loopedRecurrentState loopRequiredSteps phaseChannel
  simp

theorem loopedRecurrentState_of_tokenRecurrenceBudget
    (period sample : Nat) :
    loopedRecurrentState period (tokenRecurrenceBudget period sample) =
      phaseChannel period sample := by
  unfold tokenRecurrenceBudget
  exact loopedRecurrentState_of_requiredSteps period sample

theorem loopedRecurrentState_tokenBudget_add_mul_loopPeriod
    {loopPeriod : Nat} (h : 0 < loopPeriod) (sample passes : Nat) :
    loopedRecurrentState loopPeriod
        (tokenRecurrenceBudget loopPeriod (sample + passes * loopPeriod)) =
      loopedRecurrentState loopPeriod
        (tokenRecurrenceBudget loopPeriod sample) := by
  rw [tokenRecurrenceBudget_add_mul_loopPeriod h]

theorem loopedRecurrentState_budget_add_period
    {period budget : Nat} (hperiod : 0 < period) (hbudget : 0 < budget) :
    loopedRecurrentState period (budget + period) =
      loopedRecurrentState period budget := by
  rcases Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hbudget) with ⟨base, rfl⟩
  unfold loopedRecurrentState
  simp
  exact phaseChannel_add_period hperiod base

theorem loopedRecurrentState_budget_add_mul_period
    {period budget : Nat} (hperiod : 0 < period) (hbudget : 0 < budget)
    (passes : Nat) :
    loopedRecurrentState period (budget + passes * period) =
      loopedRecurrentState period budget := by
  rcases Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hbudget) with ⟨base, rfl⟩
  unfold loopedRecurrentState
  simp
  exact phaseChannel_add_mul_period hperiod base passes

def tokenActiveAtStep (loopPeriod token step : Nat) : Prop :=
  step ≤ tokenRecurrenceBudget loopPeriod token

theorem tokenActiveAtStep_one (loopPeriod token : Nat) :
    tokenActiveAtStep loopPeriod token 1 := by
  unfold tokenActiveAtStep
  exact tokenRecurrenceBudget_pos loopPeriod token

theorem tokenActiveAtStep_add_mul_loopPeriod {loopPeriod : Nat}
    (h : 0 < loopPeriod) (token step passes : Nat) :
    tokenActiveAtStep loopPeriod (token + passes * loopPeriod) step ↔
      tokenActiveAtStep loopPeriod token step := by
  unfold tokenActiveAtStep
  rw [tokenRecurrenceBudget_add_mul_loopPeriod h]

theorem tokenActiveAtStep_step_le_loopPeriod {loopPeriod : Nat}
    (h : 0 < loopPeriod) {token step : Nat}
    (hactive : tokenActiveAtStep loopPeriod token step) :
    step ≤ loopPeriod :=
  Nat.le_trans hactive (tokenRecurrenceBudget_le_loopPeriod h token)

theorem tokenInactiveAtStep_of_loopPeriod_lt_step {loopPeriod : Nat}
    (h : 0 < loopPeriod) {token step : Nat} (hstep : loopPeriod < step) :
    ¬ tokenActiveAtStep loopPeriod token step := by
  intro hactive
  exact Nat.not_lt_of_ge (tokenActiveAtStep_step_le_loopPeriod h hactive) hstep

def middleBlockRoute (start width sample : Nat) : Nat :=
  start + phaseChannel width sample

theorem middleBlockRoute_ge_start (start width sample : Nat) :
    start ≤ middleBlockRoute start width sample := by
  unfold middleBlockRoute
  exact Nat.le_add_right _ _

theorem middleBlockRoute_lt_stop {width : Nat} (h : 0 < width)
    (start sample : Nat) :
    middleBlockRoute start width sample < start + width := by
  unfold middleBlockRoute
  exact Nat.add_lt_add_left (phaseChannel_lt_period h sample) start

theorem middleBlockRoute_add_width {width : Nat} (h : 0 < width)
    (start sample : Nat) :
    middleBlockRoute start width (sample + width) =
      middleBlockRoute start width sample := by
  unfold middleBlockRoute
  rw [phaseChannel_add_period h]

theorem middleBlockRoute_add_mul_width {width : Nat} (h : 0 < width)
    (start sample passes : Nat) :
    middleBlockRoute start width (sample + passes * width) =
      middleBlockRoute start width sample := by
  unfold middleBlockRoute
  rw [phaseChannel_add_mul_period h]

theorem middleBlockRoute_zero (start width : Nat) :
    middleBlockRoute start width 0 = start := by
  unfold middleBlockRoute
  rw [phaseChannel_zero]
  simp

def middleBlockBudgetRoute
    (start width loopPeriod sample : Nat) : Nat × Nat :=
  (middleBlockRoute start width sample,
    tokenRecurrenceBudget loopPeriod sample)

theorem middleBlockBudgetRoute_block_ge_start
    (start width loopPeriod sample : Nat) :
    start ≤ (middleBlockBudgetRoute start width loopPeriod sample).1 := by
  unfold middleBlockBudgetRoute
  exact middleBlockRoute_ge_start start width sample

theorem middleBlockBudgetRoute_block_lt_stop {width : Nat} (hwidth : 0 < width)
    (start loopPeriod sample : Nat) :
    (middleBlockBudgetRoute start width loopPeriod sample).1 < start + width := by
  unfold middleBlockBudgetRoute
  exact middleBlockRoute_lt_stop hwidth start sample

theorem middleBlockBudgetRoute_budget_pos
    (start width loopPeriod sample : Nat) :
    0 < (middleBlockBudgetRoute start width loopPeriod sample).2 := by
  unfold middleBlockBudgetRoute
  exact tokenRecurrenceBudget_pos loopPeriod sample

theorem middleBlockBudgetRoute_budget_le_loopPeriod {loopPeriod : Nat}
    (hloop : 0 < loopPeriod) (start width sample : Nat) :
    (middleBlockBudgetRoute start width loopPeriod sample).2 ≤ loopPeriod := by
  unfold middleBlockBudgetRoute
  exact tokenRecurrenceBudget_le_loopPeriod hloop sample

theorem middleBlockBudgetRoute_add_commonCycle
    {width loopPeriod : Nat} (hwidth : 0 < width) (hloop : 0 < loopPeriod)
    (start sample : Nat) :
    middleBlockBudgetRoute start width loopPeriod (sample + width * loopPeriod) =
      middleBlockBudgetRoute start width loopPeriod sample := by
  unfold middleBlockBudgetRoute
  apply Prod.ext
  · rw [Nat.mul_comm width loopPeriod]
    exact middleBlockRoute_add_mul_width hwidth start sample loopPeriod
  · exact tokenRecurrenceBudget_add_mul_loopPeriod hloop sample width

theorem middleBlockBudgetRoute_add_mul_commonCycle
    {width loopPeriod : Nat} (hwidth : 0 < width) (hloop : 0 < loopPeriod)
    (start sample passes : Nat) :
    middleBlockBudgetRoute start width loopPeriod
        (sample + passes * (width * loopPeriod)) =
      middleBlockBudgetRoute start width loopPeriod sample := by
  unfold middleBlockBudgetRoute
  apply Prod.ext
  · rw [
      show passes * (width * loopPeriod) =
        (passes * loopPeriod) * width by ac_rfl,
    ]
    exact middleBlockRoute_add_mul_width hwidth start sample (passes * loopPeriod)
  · rw [
      show passes * (width * loopPeriod) =
        (passes * width) * loopPeriod by ac_rfl,
    ]
    exact tokenRecurrenceBudget_add_mul_loopPeriod hloop sample (passes * width)

theorem middleBlockBudgetRoute_zero (start width loopPeriod : Nat) :
    middleBlockBudgetRoute start width loopPeriod 0 = (start, 1) := by
  unfold middleBlockBudgetRoute
  rw [middleBlockRoute_zero, tokenRecurrenceBudget_zero]

def trainingFreeLoopBudget (loopPeriod sample maxLoops : Nat) : Nat :=
  min (loopRequiredSteps loopPeriod sample) maxLoops

theorem trainingFreeLoopBudget_le_maxLoops (loopPeriod sample maxLoops : Nat) :
    trainingFreeLoopBudget loopPeriod sample maxLoops ≤ maxLoops := by
  unfold trainingFreeLoopBudget
  exact Nat.min_le_right _ _

theorem trainingFreeLoopBudget_le_requiredSteps (loopPeriod sample maxLoops : Nat) :
    trainingFreeLoopBudget loopPeriod sample maxLoops ≤
      loopRequiredSteps loopPeriod sample := by
  unfold trainingFreeLoopBudget
  exact Nat.min_le_left _ _

theorem trainingFreeLoopBudget_add_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (sample maxLoops : Nat) :
    trainingFreeLoopBudget loopPeriod (sample + loopPeriod) maxLoops =
      trainingFreeLoopBudget loopPeriod sample maxLoops := by
  unfold trainingFreeLoopBudget
  rw [loopRequiredSteps_add_loopPeriod h]

theorem trainingFreeLoopBudget_add_mul_loopPeriod {loopPeriod : Nat}
    (h : 0 < loopPeriod) (sample maxLoops passes : Nat) :
    trainingFreeLoopBudget loopPeriod (sample + passes * loopPeriod) maxLoops =
      trainingFreeLoopBudget loopPeriod sample maxLoops := by
  unfold trainingFreeLoopBudget
  rw [loopRequiredSteps_add_mul_loopPeriod h]

def loopExitAvailable (loopPeriod sample maxLoops : Nat) : Prop :=
  loopRequiredSteps loopPeriod sample ≤ maxLoops

theorem trainingFreeLoopBudget_eq_required_of_available
    (loopPeriod sample maxLoops : Nat)
    (hbudget : loopExitAvailable loopPeriod sample maxLoops) :
    trainingFreeLoopBudget loopPeriod sample maxLoops =
      loopRequiredSteps loopPeriod sample := by
  unfold trainingFreeLoopBudget loopExitAvailable at *
  exact Nat.min_eq_left hbudget

theorem trainingFreeLoopBudget_pos_of_available
    (loopPeriod sample maxLoops : Nat)
    (hbudget : loopExitAvailable loopPeriod sample maxLoops) :
    0 < trainingFreeLoopBudget loopPeriod sample maxLoops := by
  rw [trainingFreeLoopBudget_eq_required_of_available loopPeriod sample maxLoops hbudget]
  exact loopRequiredSteps_pos loopPeriod sample

theorem trainingFreeLoopBudget_eq_max_of_unavailable
    (loopPeriod sample maxLoops : Nat)
    (hunavailable : ¬ loopExitAvailable loopPeriod sample maxLoops) :
    trainingFreeLoopBudget loopPeriod sample maxLoops = maxLoops := by
  unfold trainingFreeLoopBudget loopExitAvailable at *
  exact Nat.min_eq_right (Nat.le_of_lt (Nat.lt_of_not_ge hunavailable))

def loopOverthinkingBoundary (loopPeriod sample tolerance : Nat) : Nat :=
  loopRequiredSteps loopPeriod sample + tolerance

structure LoopExitCertificate where
  loopPeriod : Nat
  sample : Nat
  maxLoops : Nat
  tolerance : Nat
  exitStep : Nat
  exactRequired : exitStep = loopRequiredSteps loopPeriod sample
  withinBudget : exitStep ≤ maxLoops
  withinGuardrail : exitStep ≤ loopOverthinkingBoundary loopPeriod sample tolerance

def loopExitCertificate
    (loopPeriod sample maxLoops tolerance : Nat)
    (hbudget : loopExitAvailable loopPeriod sample maxLoops) :
    LoopExitCertificate :=
  { loopPeriod := loopPeriod,
    sample := sample,
    maxLoops := maxLoops,
    tolerance := tolerance,
    exitStep := loopRequiredSteps loopPeriod sample,
    exactRequired := rfl,
    withinBudget := hbudget,
    withinGuardrail := by
      unfold loopOverthinkingBoundary
      exact Nat.le_add_right _ _ }

theorem loopOverthinkingBoundary_ge_required
    (loopPeriod sample tolerance : Nat) :
    loopRequiredSteps loopPeriod sample ≤
      loopOverthinkingBoundary loopPeriod sample tolerance := by
  unfold loopOverthinkingBoundary
  exact Nat.le_add_right _ _

theorem loopOverthinkingBoundary_add_loopPeriod
    {loopPeriod : Nat} (hpositive : 0 < loopPeriod)
    (sample tolerance : Nat) :
    loopOverthinkingBoundary loopPeriod (sample + loopPeriod) tolerance =
      loopOverthinkingBoundary loopPeriod sample tolerance := by
  unfold loopOverthinkingBoundary
  rw [loopRequiredSteps_add_loopPeriod hpositive]

theorem loopOverthinkingBoundary_add_mul_loopPeriod
    {loopPeriod : Nat} (hpositive : 0 < loopPeriod)
    (sample tolerance passes : Nat) :
    loopOverthinkingBoundary loopPeriod (sample + passes * loopPeriod) tolerance =
      loopOverthinkingBoundary loopPeriod sample tolerance := by
  unfold loopOverthinkingBoundary
  rw [loopRequiredSteps_add_mul_loopPeriod hpositive]

theorem loopExitAvailable_of_loopPeriod_le_budget
    {loopPeriod maxLoops : Nat} (hpositive : 0 < loopPeriod)
    (hbudget : loopPeriod ≤ maxLoops) (sample : Nat) :
    loopExitAvailable loopPeriod sample maxLoops := by
  unfold loopExitAvailable
  exact Nat.le_trans (loopRequiredSteps_le_loopPeriod hpositive sample) hbudget

theorem loopExitAvailable_add_loopPeriod
    {loopPeriod maxLoops : Nat} (hpositive : 0 < loopPeriod)
    (sample : Nat) :
    loopExitAvailable loopPeriod (sample + loopPeriod) maxLoops ↔
      loopExitAvailable loopPeriod sample maxLoops := by
  unfold loopExitAvailable
  rw [loopRequiredSteps_add_loopPeriod hpositive]

theorem loopExitAvailable_add_mul_loopPeriod
    {loopPeriod maxLoops : Nat} (hpositive : 0 < loopPeriod)
    (sample passes : Nat) :
    loopExitAvailable loopPeriod (sample + passes * loopPeriod) maxLoops ↔
      loopExitAvailable loopPeriod sample maxLoops := by
  unfold loopExitAvailable
  rw [loopRequiredSteps_add_mul_loopPeriod hpositive]

theorem loopExitCertificate_exit_eq_required
    (certificate : LoopExitCertificate) :
    certificate.exitStep =
      loopRequiredSteps certificate.loopPeriod certificate.sample :=
  certificate.exactRequired

theorem loopExitCertificate_exit_pos
    (certificate : LoopExitCertificate) :
    0 < certificate.exitStep := by
  rw [loopExitCertificate_exit_eq_required certificate]
  exact loopRequiredSteps_pos certificate.loopPeriod certificate.sample

theorem loopExitCertificate_within_budget
    (certificate : LoopExitCertificate) :
    certificate.exitStep ≤ certificate.maxLoops :=
  certificate.withinBudget

theorem loopExitCertificate_within_guardrail
    (certificate : LoopExitCertificate) :
    certificate.exitStep ≤
      loopOverthinkingBoundary
        certificate.loopPeriod certificate.sample certificate.tolerance :=
  certificate.withinGuardrail

theorem loopExitCertificate_exit_available
    (certificate : LoopExitCertificate) :
    loopExitAvailable
      certificate.loopPeriod certificate.sample certificate.maxLoops := by
  unfold loopExitAvailable
  rw [← loopExitCertificate_exit_eq_required certificate]
  exact certificate.withinBudget

theorem loopExitCertificate_budget_eq_exitStep
    (certificate : LoopExitCertificate) :
    trainingFreeLoopBudget
      certificate.loopPeriod certificate.sample certificate.maxLoops =
      certificate.exitStep := by
  rw [
    trainingFreeLoopBudget_eq_required_of_available
      certificate.loopPeriod certificate.sample certificate.maxLoops
      (loopExitCertificate_exit_available certificate),
    ← loopExitCertificate_exit_eq_required certificate,
  ]

theorem loopExitCertificate_exitStep_add_mul_loopPeriod
    {loopPeriod maxLoops : Nat} (hpositive : 0 < loopPeriod)
    (sample passes tolerance : Nat)
    (hbudget : loopExitAvailable loopPeriod sample maxLoops)
    (hshift :
      loopExitAvailable loopPeriod (sample + passes * loopPeriod) maxLoops) :
    (loopExitCertificate
        loopPeriod (sample + passes * loopPeriod) maxLoops tolerance hshift).exitStep =
      (loopExitCertificate loopPeriod sample maxLoops tolerance hbudget).exitStep := by
  simp [loopExitCertificate, loopRequiredSteps_add_mul_loopPeriod hpositive]

theorem loopExitCertificate_boundary_add_mul_loopPeriod
    {loopPeriod maxLoops : Nat} (hpositive : 0 < loopPeriod)
    (sample passes tolerance : Nat)
    (hbudget : loopExitAvailable loopPeriod sample maxLoops)
    (hshift :
      loopExitAvailable loopPeriod (sample + passes * loopPeriod) maxLoops) :
    loopOverthinkingBoundary
        (loopExitCertificate
          loopPeriod (sample + passes * loopPeriod) maxLoops tolerance hshift).loopPeriod
        (loopExitCertificate
          loopPeriod (sample + passes * loopPeriod) maxLoops tolerance hshift).sample
        (loopExitCertificate
          loopPeriod (sample + passes * loopPeriod) maxLoops tolerance hshift).tolerance =
      loopOverthinkingBoundary
        (loopExitCertificate loopPeriod sample maxLoops tolerance hbudget).loopPeriod
        (loopExitCertificate loopPeriod sample maxLoops tolerance hbudget).sample
        (loopExitCertificate loopPeriod sample maxLoops tolerance hbudget).tolerance := by
  simp [loopExitCertificate, loopOverthinkingBoundary_add_mul_loopPeriod hpositive]

def adapterBlock (blockSize channel : Nat) : Nat :=
  channel % blockSize

theorem adapterBlock_lt_blockSize {blockSize : Nat} (h : 0 < blockSize) (channel : Nat) :
    adapterBlock blockSize channel < blockSize := by
  unfold adapterBlock
  exact Nat.mod_lt channel h

theorem adapterBlock_add_blockSize {blockSize : Nat} (h : 0 < blockSize) (channel : Nat) :
    adapterBlock blockSize (channel + blockSize) = adapterBlock blockSize channel := by
  unfold adapterBlock
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt channel h)

theorem adapterBlock_add_mul_blockSize {blockSize : Nat} (_h : 0 < blockSize)
    (channel passes : Nat) :
    adapterBlock blockSize (channel + passes * blockSize) = adapterBlock blockSize channel := by
  unfold adapterBlock
  exact Nat.add_mul_mod_self_right channel passes blockSize

theorem adapterBlock_idempotent (blockSize channel : Nat) :
    adapterBlock blockSize (adapterBlock blockSize channel) = adapterBlock blockSize channel := by
  unfold adapterBlock
  by_cases h : blockSize = 0
  · simp [h]
  · exact Nat.mod_eq_of_lt (Nat.mod_lt channel (Nat.pos_of_ne_zero h))

theorem adapterBlock_zero (blockSize : Nat) :
    adapterBlock blockSize 0 = 0 := by
  unfold adapterBlock
  simp

def blockCyclicCell (blockSize row column : Nat) : Nat × Nat :=
  (adapterBlock blockSize row, adapterBlock blockSize column)

theorem blockCyclicCell_fst_lt_blockSize {blockSize : Nat} (h : 0 < blockSize)
    (row column : Nat) :
    (blockCyclicCell blockSize row column).fst < blockSize := by
  unfold blockCyclicCell
  exact adapterBlock_lt_blockSize h row

theorem blockCyclicCell_snd_lt_blockSize {blockSize : Nat} (h : 0 < blockSize)
    (row column : Nat) :
    (blockCyclicCell blockSize row column).snd < blockSize := by
  unfold blockCyclicCell
  exact adapterBlock_lt_blockSize h column

theorem blockCyclicCell_add_row_blockSize {blockSize : Nat} (h : 0 < blockSize)
    (row column : Nat) :
    blockCyclicCell blockSize (row + blockSize) column =
      blockCyclicCell blockSize row column := by
  unfold blockCyclicCell
  rw [adapterBlock_add_blockSize h]

theorem blockCyclicCell_add_column_blockSize {blockSize : Nat} (h : 0 < blockSize)
    (row column : Nat) :
    blockCyclicCell blockSize row (column + blockSize) =
      blockCyclicCell blockSize row column := by
  unfold blockCyclicCell
  rw [adapterBlock_add_blockSize h]

theorem blockCyclicCell_add_mul_blockSize {blockSize : Nat} (h : 0 < blockSize)
    (row column rowPasses columnPasses : Nat) :
    blockCyclicCell blockSize (row + rowPasses * blockSize)
        (column + columnPasses * blockSize) =
      blockCyclicCell blockSize row column := by
  unfold blockCyclicCell
  rw [adapterBlock_add_mul_blockSize h, adapterBlock_add_mul_blockSize h]

def positionResidue (period position : Nat) : Nat :=
  position % period

def positionWinding (period position : Nat) : Nat :=
  position / period

def windingPosition (period position : Nat) : Nat × Nat :=
  (positionWinding period position, positionResidue period position)

theorem positionResidue_lt_period {period : Nat} (h : 0 < period) (position : Nat) :
    positionResidue period position < period := by
  unfold positionResidue
  exact Nat.mod_lt position h

theorem positionResidue_add_period {period : Nat} (h : 0 < period) (position : Nat) :
    positionResidue period (position + period) = positionResidue period position := by
  unfold positionResidue
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt position h)

theorem positionResidue_add_mul_period {period : Nat} (_h : 0 < period)
    (position passes : Nat) :
    positionResidue period (position + passes * period) = positionResidue period position := by
  unfold positionResidue
  exact Nat.add_mul_mod_self_right position passes period

theorem positionWinding_mul_add_residue (period position : Nat) :
    positionWinding period position * period + positionResidue period position = position := by
  unfold positionWinding positionResidue
  simpa [Nat.mul_comm] using Nat.div_add_mod position period

theorem windingPosition_fst_mul_add_snd (period position : Nat) :
    (windingPosition period position).fst * period + (windingPosition period position).snd =
      position := by
  unfold windingPosition
  exact positionWinding_mul_add_residue period position

end Circle.Applications
