import Circle.Core.Period
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.ZMod.Units

namespace Circle

/-- Scaling multiplies a node by `k` in `C n`. -/
def scale (n k : Nat) (x : C n) : C n :=
  (k : ZMod n) * x

def scaleAddMonoidHom (n k : Nat) : C n →+ C n where
  toFun := scale n k
  map_zero' := by
    unfold scale
    simp
  map_add' := by
    intro x y
    unfold scale
    rw [mul_add]

def scaleKernelSubgroup (n k : Nat) : AddSubgroup (C n) :=
  (scaleAddMonoidHom n k).ker

theorem scale_zero_factor (n : Nat) (x : C n) :
    scale n 0 x = 0 := by
  unfold scale
  simp

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

theorem scale_nat_to_coilStep (n k steps : Nat) :
    scale n k ((steps : Nat) : C n) = coilStep n k 0 steps := by
  unfold scale coilStep
  simp [Nat.mul_comm]

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

theorem scale_cofactor_multiple_zero {n k m : Nat} (hkn : k ∣ n) :
    scale n k ((m * (n / k) : Nat) : C n) = 0 := by
  unfold scale
  rw [← Nat.cast_mul]
  have hmul : k * (n / k) = n := Nat.mul_div_cancel' hkn
  have hmul' : k * (m * (n / k)) = m * n := by
    rw [← Nat.mul_assoc]
    rw [Nat.mul_comm k m]
    rw [Nat.mul_assoc]
    rw [hmul]
  rw [hmul']
  rw [Nat.cast_mul]
  rw [CharP.cast_eq_zero (ZMod n) n]
  simp

theorem scale_add_cofactor_multiple {n k x m : Nat} (hkn : k ∣ n) :
    scale n k (((x + m * (n / k)) : Nat) : C n) = scale n k ((x : Nat) : C n) := by
  unfold scale
  rw [Nat.cast_add]
  rw [mul_add]
  have hzero := scale_cofactor_multiple_zero (n := n) (k := k) (m := m) hkn
  unfold scale at hzero
  rw [hzero]
  simp

theorem scale_nat_eq_zero_iff_dvd_mul (n k x : Nat) :
    scale n k ((x : Nat) : C n) = 0 ↔ n ∣ k * x := by
  unfold scale
  rw [← Nat.cast_mul]
  exact CharP.cast_eq_zero_iff (ZMod n) n (k * x)

theorem scale_nat_eq_zero_iff_period_dvd {n k x : Nat} (hn : n ≠ 0) :
    scale n k ((x : Nat) : C n) = 0 ↔ period n k ∣ x := by
  rw [period_eq_n_div_gcd hn]
  have hnpos : 0 < n := Nat.pos_of_ne_zero hn
  rw [scale_nat_eq_zero_iff_dvd_mul]
  let g := Nat.gcd n k
  have hgpos : 0 < g := Nat.gcd_pos_of_pos_left k hnpos
  have hgn : g ∣ n := Nat.gcd_dvd_left n k
  have hgk : g ∣ k := Nat.gcd_dvd_right n k
  have hn_decomp : n = g * (n / g) := by
    rw [Nat.mul_div_cancel' hgn]
  have hk_decomp : k = g * (k / g) := by
    rw [Nat.mul_div_cancel' hgk]
  have hcop : Nat.Coprime (n / g) (k / g) := Nat.coprime_div_gcd_div_gcd hgpos
  constructor
  · intro h
    have h1a : g * (n / g) ∣ k * x := by
      rw [← hn_decomp]
      exact h
    have h1b : g * (n / g) ∣ (g * (k / g)) * x := by
      rw [← hk_decomp]
      exact h1a
    have h1 : g * (n / g) ∣ g * ((k / g) * x) := by
      simpa [Nat.mul_assoc] using h1b
    have h2 : n / g ∣ (k / g) * x := (Nat.mul_dvd_mul_iff_left hgpos).mp h1
    exact hcop.dvd_of_dvd_mul_left h2
  · intro h
    have h2 : n / g ∣ (k / g) * x := dvd_mul_of_dvd_right h (k / g)
    have h1 : g * (n / g) ∣ g * ((k / g) * x) := (Nat.mul_dvd_mul_iff_left hgpos).mpr h2
    have h1b : g * (n / g) ∣ (g * (k / g)) * x := by
      simpa [Nat.mul_assoc] using h1
    have h1a : g * (n / g) ∣ k * x := by
      rw [hk_decomp]
      exact h1b
    rw [hn_decomp]
    exact h1a

theorem mem_scaleKernelSubgroup_iff {n k : Nat} (x : C n) :
    x ∈ scaleKernelSubgroup n k ↔ scale n k x = 0 := by
  rfl

theorem nat_mem_scaleKernelSubgroup_iff_period_dvd {n k x : Nat} (hn : n ≠ 0) :
    ((x : Nat) : C n) ∈ scaleKernelSubgroup n k ↔ period n k ∣ x := by
  rw [mem_scaleKernelSubgroup_iff]
  exact scale_nat_eq_zero_iff_period_dvd hn

theorem scale_period_multiple_zero {n k m : Nat} (hn : n ≠ 0) :
    scale n k ((m * period n k : Nat) : C n) = 0 := by
  rw [scale_nat_eq_zero_iff_period_dvd hn]
  exact Nat.dvd_mul_left (period n k) m

theorem scale_add_period_multiple {n k x m : Nat} (hn : n ≠ 0) :
    scale n k (((x + m * period n k) : Nat) : C n) = scale n k ((x : Nat) : C n) := by
  unfold scale
  rw [Nat.cast_add]
  rw [mul_add]
  have hzero := scale_period_multiple_zero (n := n) (k := k) (m := m) hn
  unfold scale at hzero
  rw [hzero]
  simp

theorem scale_nat_period_normalForm {n k x : Nat} (hn : n ≠ 0) :
    scale n k ((x : Nat) : C n) = scale n k (((x % period n k) : Nat) : C n) := by
  let p := period n k
  have hdecomp : x = x % p + (x / p) * p := by
    have h0 := Nat.mod_add_div x p
    rw [Nat.mul_comm p (x / p)] at h0
    exact h0.symm
  calc
    scale n k ((x : Nat) : C n) = scale n k (((x % p + (x / p) * p) : Nat) : C n) := by
      exact congrArg (fun t : Nat => scale n k ((t : Nat) : C n)) hdecomp
    _ = scale n k (((x % p) : Nat) : C n) := by
      exact scale_add_period_multiple (n := n) (k := k) (x := x % p) (m := x / p) hn
    _ = scale n k (((x % period n k) : Nat) : C n) := by
      rfl

theorem scale_nat_eq_iff_mul_modEq (n k x y : Nat) :
    scale n k ((x : Nat) : C n) = scale n k ((y : Nat) : C n) ↔
      k * x ≡ k * y [MOD n] := by
  unfold scale
  rw [← Nat.cast_mul, ← Nat.cast_mul]
  exact ZMod.natCast_eq_natCast_iff (k * x) (k * y) n

theorem scale_nat_eq_iff_period_modEq {n k x y : Nat} (hn : n ≠ 0) :
    scale n k ((x : Nat) : C n) = scale n k ((y : Nat) : C n) ↔
      x ≡ y [MOD period n k] := by
  rw [scale_nat_eq_iff_mul_modEq]
  rw [period_eq_n_div_gcd hn]
  let g := Nat.gcd n k
  have hnpos : 0 < n := Nat.pos_of_ne_zero hn
  have hgpos : 0 < g := Nat.gcd_pos_of_pos_left k hnpos
  have hgn : g ∣ n := Nat.gcd_dvd_left n k
  have hgk : g ∣ k := Nat.gcd_dvd_right n k
  have hn_decomp : n = g * (n / g) := by
    rw [Nat.mul_div_cancel' hgn]
  have hk_decomp : k = g * (k / g) := by
    rw [Nat.mul_div_cancel' hgk]
  have hcop : Nat.Coprime (n / g) (k / g) := Nat.coprime_div_gcd_div_gcd hgpos
  have hcop_gcd : Nat.gcd (n / g) (k / g) = 1 :=
    Nat.coprime_iff_gcd_eq_one.mp hcop
  constructor
  · intro h
    have h1n : (g * (k / g)) * x ≡ (g * (k / g)) * y [MOD n] := by
      rw [← hk_decomp]
      exact h
    have h1 : (g * (k / g)) * x ≡ (g * (k / g)) * y [MOD g * (n / g)] := by
      rw [← hn_decomp]
      exact h1n
    have h2 : g * ((k / g) * x) ≡ g * ((k / g) * y) [MOD g * (n / g)] := by
      simpa [Nat.mul_assoc] using h1
    have h3 : (k / g) * x ≡ (k / g) * y [MOD n / g] :=
      Nat.ModEq.mul_left_cancel' hgpos.ne' h2
    exact Nat.ModEq.cancel_left_of_coprime hcop_gcd h3
  · intro h
    have h1 : (k / g) * x ≡ (k / g) * y [MOD n / g] :=
      h.mul_left (k / g)
    have h2 : g * ((k / g) * x) ≡ g * ((k / g) * y) [MOD g * (n / g)] :=
      h1.mul_left' g
    have h3 : (g * (k / g)) * x ≡ (g * (k / g)) * y [MOD g * (n / g)] := by
      simpa [Nat.mul_assoc] using h2
    have h4 : (g * (k / g)) * x ≡ (g * (k / g)) * y [MOD n] := by
      rw [hn_decomp]
      exact h3
    rw [hk_decomp]
    exact h4

theorem scale_nat_period_representatives_injective {n k x y : Nat} (hn : n ≠ 0)
    (hx : x < period n k) (hy : y < period n k) :
    scale n k ((x : Nat) : C n) = scale n k ((y : Nat) : C n) ↔ x = y := by
  rw [scale_nat_eq_iff_period_modEq hn]
  constructor
  · intro h
    exact h.eq_of_lt_of_lt hx hy
  · intro h
    rw [h]

noncomputable def scalePeriodRepresentativeImage (n k : Nat) : Finset (C n) :=
  Finset.univ.image (fun r : Fin (period n k) => scale n k ((r : Nat) : C n))

theorem scalePeriodRepresentativeImage_card {n k : Nat} (hn : n ≠ 0) :
    (scalePeriodRepresentativeImage n k).card = period n k := by
  unfold scalePeriodRepresentativeImage
  rw [Finset.card_image_of_injective]
  · exact Fintype.card_fin (period n k)
  · intro a b h
    apply Fin.ext
    exact (scale_nat_period_representatives_injective (n := n) (k := k)
      (x := a.val) (y := b.val) hn a.isLt b.isLt).mp h

theorem scale_nat_mem_scalePeriodRepresentativeImage {n k x : Nat} (hn : n ≠ 0) :
    scale n k ((x : Nat) : C n) ∈ scalePeriodRepresentativeImage n k := by
  unfold scalePeriodRepresentativeImage
  have hnpos : 0 < n := Nat.pos_of_ne_zero hn
  have hgpos : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_left k hnpos
  have hp : 0 < period n k := by
    rw [period_eq_n_div_gcd hn]
    exact Nat.div_pos (Nat.gcd_le_left k hnpos) hgpos
  rw [scale_nat_period_normalForm (n := n) (k := k) (x := x) hn]
  exact Finset.mem_image.mpr
    ⟨⟨x % period n k, Nat.mod_lt x hp⟩, Finset.mem_univ _, rfl⟩

noncomputable def scaleCircleImage (n k : Nat) : Finset (C n) :=
  (Finset.range n).image (fun x : Nat => scale n k ((x : Nat) : C n))

theorem scaleCircleImage_eq_scalePeriodRepresentativeImage {n k : Nat} (hn : n ≠ 0) :
    scaleCircleImage n k = scalePeriodRepresentativeImage n k := by
  apply Finset.ext
  intro y
  constructor
  · intro hy
    unfold scaleCircleImage at hy
    rcases Finset.mem_image.mp hy with ⟨x, _, hx⟩
    rw [← hx]
    exact scale_nat_mem_scalePeriodRepresentativeImage (n := n) (k := k) (x := x) hn
  · intro hy
    unfold scaleCircleImage
    unfold scalePeriodRepresentativeImage at hy
    rcases Finset.mem_image.mp hy with ⟨r, _, hr⟩
    have hp_le_n : period n k ≤ n := by
      rw [period_eq_n_div_gcd hn]
      exact Nat.div_le_self n (Nat.gcd n k)
    have hrn : (r : Nat) < n := lt_of_lt_of_le r.isLt hp_le_n
    exact Finset.mem_image.mpr ⟨(r : Nat), Finset.mem_range.mpr hrn, hr⟩

theorem scaleCircleImage_card {n k : Nat} (hn : n ≠ 0) :
    (scaleCircleImage n k).card = period n k := by
  rw [scaleCircleImage_eq_scalePeriodRepresentativeImage hn]
  exact scalePeriodRepresentativeImage_card hn

noncomputable def scaleKernelRepresentativeSet (n k : Nat) : Finset Nat :=
  (Finset.range n).filter (fun x : Nat => scale n k ((x : Nat) : C n) = 0)

noncomputable def scalePeriodKernelRepresentatives (n k : Nat) : Finset Nat :=
  Finset.univ.image (fun m : Fin (Nat.gcd n k) => (m : Nat) * period n k)

theorem scalePeriodKernelRepresentatives_card {n k : Nat} (hn : n ≠ 0) :
    (scalePeriodKernelRepresentatives n k).card = Nat.gcd n k := by
  unfold scalePeriodKernelRepresentatives
  rw [Finset.card_image_of_injective]
  · exact Fintype.card_fin (Nat.gcd n k)
  · intro a b h
    apply Fin.ext
    have hnpos : 0 < n := Nat.pos_of_ne_zero hn
    have hgpos : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_left k hnpos
    have hp : 0 < period n k := by
      rw [period_eq_n_div_gcd hn]
      exact Nat.div_pos (Nat.gcd_le_left k hnpos) hgpos
    exact Nat.mul_right_cancel hp h

theorem scaleKernelRepresentativeSet_eq_periodMultiples {n k : Nat} (hn : n ≠ 0) :
    scaleKernelRepresentativeSet n k = scalePeriodKernelRepresentatives n k := by
  apply Finset.ext
  intro x
  constructor
  · intro hx
    unfold scaleKernelRepresentativeSet at hx
    rcases Finset.mem_filter.mp hx with ⟨hxn, hzero⟩
    have hdvd : period n k ∣ x := (scale_nat_eq_zero_iff_period_dvd hn).mp hzero
    rcases hdvd with ⟨m, hm⟩
    unfold scalePeriodKernelRepresentatives
    have hnpos : 0 < n := Nat.pos_of_ne_zero hn
    have hgpos : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_left k hnpos
    have hp : 0 < period n k := by
      rw [period_eq_n_div_gcd hn]
      exact Nat.div_pos (Nat.gcd_le_left k hnpos) hgpos
    have hg_mul_p : Nat.gcd n k * period n k = n := by
      rw [period_eq_n_div_gcd hn]
      exact Nat.mul_div_cancel' (Nat.gcd_dvd_left n k)
    have hlt : m * period n k < Nat.gcd n k * period n k := by
      rw [hg_mul_p]
      rw [hm] at hxn
      simpa [Nat.mul_comm] using hxn
    have hm_lt : m < Nat.gcd n k := (Nat.mul_lt_mul_right hp).mp hlt
    exact Finset.mem_image.mpr
      ⟨⟨m, hm_lt⟩, Finset.mem_univ _, by simp [hm, Nat.mul_comm]⟩
  · intro hx
    unfold scalePeriodKernelRepresentatives at hx
    rcases Finset.mem_image.mp hx with ⟨m, _, hm⟩
    unfold scaleKernelRepresentativeSet
    exact Finset.mem_filter.mpr
      ⟨by
        have hnpos : 0 < n := Nat.pos_of_ne_zero hn
        have hgpos : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_left k hnpos
        have hp : 0 < period n k := by
          rw [period_eq_n_div_gcd hn]
          exact Nat.div_pos (Nat.gcd_le_left k hnpos) hgpos
        have hg_mul_p : Nat.gcd n k * period n k = n := by
          rw [period_eq_n_div_gcd hn]
          exact Nat.mul_div_cancel' (Nat.gcd_dvd_left n k)
        have hlt : (m : Nat) * period n k < Nat.gcd n k * period n k :=
          (Nat.mul_lt_mul_right hp).mpr m.isLt
        exact Finset.mem_range.mpr (by
          rw [← hm]
          exact lt_of_lt_of_eq hlt hg_mul_p),
       by
        rw [← hm]
        simpa [Nat.mul_comm] using
          scale_period_multiple_zero (n := n) (k := k) (m := (m : Nat)) hn⟩

theorem scaleKernelRepresentativeSet_card {n k : Nat} (hn : n ≠ 0) :
    (scaleKernelRepresentativeSet n k).card = Nat.gcd n k := by
  rw [scaleKernelRepresentativeSet_eq_periodMultiples hn]
  exact scalePeriodKernelRepresentatives_card hn

noncomputable def scaleFiberRepresentativeSet (n k r : Nat) : Finset Nat :=
  (Finset.range n).filter
    (fun x : Nat => scale n k ((x : Nat) : C n) = scale n k ((r : Nat) : C n))

noncomputable def scalePeriodFiberRepresentatives (n k r : Nat) : Finset Nat :=
  Finset.univ.image
    (fun m : Fin (Nat.gcd n k) => (r % period n k) + (m : Nat) * period n k)

theorem scalePeriodFiberRepresentatives_card {n k r : Nat} (hn : n ≠ 0) :
    (scalePeriodFiberRepresentatives n k r).card = Nat.gcd n k := by
  unfold scalePeriodFiberRepresentatives
  rw [Finset.card_image_of_injective]
  · exact Fintype.card_fin (Nat.gcd n k)
  · intro a b h
    apply Fin.ext
    have hnpos : 0 < n := Nat.pos_of_ne_zero hn
    have hgpos : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_left k hnpos
    have hp : 0 < period n k := by
      rw [period_eq_n_div_gcd hn]
      exact Nat.div_pos (Nat.gcd_le_left k hnpos) hgpos
    have hmul : (a : Nat) * period n k = (b : Nat) * period n k :=
      Nat.add_left_cancel h
    exact Nat.mul_right_cancel hp hmul

theorem scaleFiberRepresentativeSet_eq_periodFibers {n k r : Nat} (hn : n ≠ 0) :
    scaleFiberRepresentativeSet n k r = scalePeriodFiberRepresentatives n k r := by
  apply Finset.ext
  intro x
  constructor
  · intro hx
    unfold scaleFiberRepresentativeSet at hx
    rcases Finset.mem_filter.mp hx with ⟨hxn, hscale⟩
    unfold scalePeriodFiberRepresentatives
    have hnpos : 0 < n := Nat.pos_of_ne_zero hn
    have hgpos : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_left k hnpos
    have hp : 0 < period n k := by
      rw [period_eq_n_div_gcd hn]
      exact Nat.div_pos (Nat.gcd_le_left k hnpos) hgpos
    have hg_mul_p : Nat.gcd n k * period n k = n := by
      rw [period_eq_n_div_gcd hn]
      exact Nat.mul_div_cancel' (Nat.gcd_dvd_left n k)
    have htarget :
        scale n k ((x : Nat) : C n) =
          scale n k (((r % period n k) : Nat) : C n) :=
      hscale.trans (scale_nat_period_normalForm (n := n) (k := k) (x := r) hn)
    have hmod : x ≡ r % period n k [MOD period n k] :=
      (scale_nat_eq_iff_period_modEq (n := n) (k := k)
        (x := x) (y := r % period n k) hn).mp htarget
    have hrmod_lt : r % period n k < period n k := Nat.mod_lt r hp
    have hxmod : x % period n k = r % period n k := by
      unfold Nat.ModEq at hmod
      simpa [Nat.mod_eq_of_lt hrmod_lt] using hmod
    have hx_decomp : x = r % period n k + (x / period n k) * period n k := by
      have h0 := Nat.mod_add_div x (period n k)
      rw [hxmod] at h0
      rw [Nat.mul_comm (period n k) (x / period n k)] at h0
      exact h0.symm
    have hq_lt : x / period n k < Nat.gcd n k := by
      rw [Nat.div_lt_iff_lt_mul hp]
      rw [hg_mul_p]
      exact Finset.mem_range.mp hxn
    exact Finset.mem_image.mpr
      ⟨⟨x / period n k, hq_lt⟩, Finset.mem_univ _, hx_decomp.symm⟩
  · intro hx
    unfold scalePeriodFiberRepresentatives at hx
    rcases Finset.mem_image.mp hx with ⟨m, _, hm⟩
    unfold scaleFiberRepresentativeSet
    exact Finset.mem_filter.mpr
      ⟨by
        have hnpos : 0 < n := Nat.pos_of_ne_zero hn
        have hgpos : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_left k hnpos
        have hp : 0 < period n k := by
          rw [period_eq_n_div_gcd hn]
          exact Nat.div_pos (Nat.gcd_le_left k hnpos) hgpos
        have hrmod_lt : r % period n k < period n k := Nat.mod_lt r hp
        have hg_mul_p : Nat.gcd n k * period n k = n := by
          rw [period_eq_n_div_gcd hn]
          exact Nat.mul_div_cancel' (Nat.gcd_dvd_left n k)
        have hlt1 :
            r % period n k + (m : Nat) * period n k <
              ((m : Nat) + 1) * period n k := by
          calc
            r % period n k + (m : Nat) * period n k =
                (m : Nat) * period n k + r % period n k := by
                  exact Nat.add_comm _ _
            _ < (m : Nat) * period n k + period n k := by
                  exact Nat.add_lt_add_left hrmod_lt ((m : Nat) * period n k)
            _ = ((m : Nat) + 1) * period n k := by
                  rw [Nat.add_mul, one_mul]
        have hle :
            ((m : Nat) + 1) * period n k ≤ Nat.gcd n k * period n k :=
          Nat.mul_le_mul_right (period n k) (Nat.succ_le_of_lt m.isLt)
        exact Finset.mem_range.mpr (by
          rw [← hm]
          exact lt_of_lt_of_le hlt1 (hle.trans_eq hg_mul_p)),
       by
        rw [← hm]
        calc
          scale n k (((r % period n k + (m : Nat) * period n k) : Nat) : C n) =
              scale n k (((r % period n k) : Nat) : C n) := by
                exact scale_add_period_multiple
                  (n := n) (k := k) (x := r % period n k) (m := (m : Nat)) hn
          _ = scale n k ((r : Nat) : C n) := by
                exact (scale_nat_period_normalForm (n := n) (k := k) (x := r) hn).symm⟩

theorem scaleFiberRepresentativeSet_card {n k r : Nat} (hn : n ≠ 0) :
    (scaleFiberRepresentativeSet n k r).card = Nat.gcd n k := by
  rw [scaleFiberRepresentativeSet_eq_periodFibers hn]
  exact scalePeriodFiberRepresentatives_card hn

theorem scaleFiberRepresentativeSet_zero_eq_scaleKernelRepresentativeSet (n k : Nat) :
    scaleFiberRepresentativeSet n k 0 = scaleKernelRepresentativeSet n k := by
  unfold scaleFiberRepresentativeSet scaleKernelRepresentativeSet
  simp [scale]

theorem scaleFiberRepresentativeSet_eq_iff_scaled_eq_of_lt
    {n k r s : Nat} (hr : r < n) :
    scaleFiberRepresentativeSet n k r = scaleFiberRepresentativeSet n k s ↔
      scale n k ((r : Nat) : C n) = scale n k ((s : Nat) : C n) := by
  constructor
  · intro hset
    have hrmem : r ∈ scaleFiberRepresentativeSet n k r := by
      unfold scaleFiberRepresentativeSet
      exact Finset.mem_filter.mpr ⟨Finset.mem_range.mpr hr, rfl⟩
    have hmem : r ∈ scaleFiberRepresentativeSet n k s := by
      rwa [hset] at hrmem
    exact (Finset.mem_filter.mp hmem).2
  · intro hscale
    unfold scaleFiberRepresentativeSet
    apply Finset.ext
    intro x
    constructor
    · intro hx
      rcases Finset.mem_filter.mp hx with ⟨hxn, hxscale⟩
      exact Finset.mem_filter.mpr ⟨hxn, hxscale.trans hscale⟩
    · intro hx
      rcases Finset.mem_filter.mp hx with ⟨hxn, hxscale⟩
      exact Finset.mem_filter.mpr ⟨hxn, hxscale.trans hscale.symm⟩

theorem scaleFiberRepresentativeSet_eq_iff_period_modEq_of_lt
    {n k r s : Nat} (hn : n ≠ 0) (hr : r < n) :
    scaleFiberRepresentativeSet n k r = scaleFiberRepresentativeSet n k s ↔
      r ≡ s [MOD period n k] := by
  rw [scaleFiberRepresentativeSet_eq_iff_scaled_eq_of_lt
    (n := n) (k := k) (r := r) (s := s) hr]
  exact scale_nat_eq_iff_period_modEq (n := n) (k := k) (x := r) (y := s) hn

noncomputable def scaleTargetFiberRepresentativeSet (n k : Nat) (target : C n) :
    Finset Nat :=
  (Finset.range n).filter (fun x : Nat => scale n k ((x : Nat) : C n) = target)

theorem scaleTargetFiberRepresentativeSet_scaled_eq_scaleFiberRepresentativeSet
    (n k r : Nat) :
    scaleTargetFiberRepresentativeSet n k (scale n k ((r : Nat) : C n)) =
      scaleFiberRepresentativeSet n k r := by
  rfl

theorem scaleTargetFiberRepresentativeSet_eq_empty_of_not_mem_scaleCircleImage
    {n k : Nat} {target : C n} (hnot : target ∉ scaleCircleImage n k) :
    scaleTargetFiberRepresentativeSet n k target = ∅ := by
  apply Finset.ext
  intro x
  constructor
  · intro hx
    unfold scaleTargetFiberRepresentativeSet at hx
    rcases Finset.mem_filter.mp hx with ⟨hxn, htarget⟩
    have hmem : target ∈ scaleCircleImage n k := by
      unfold scaleCircleImage
      exact Finset.mem_image.mpr ⟨x, hxn, htarget⟩
    exact (hnot hmem).elim
  · intro hx
    simp at hx

theorem scaleTargetFiberRepresentativeSet_card_of_mem_scaleCircleImage
    {n k : Nat} (hn : n ≠ 0) {target : C n} (hmem : target ∈ scaleCircleImage n k) :
    (scaleTargetFiberRepresentativeSet n k target).card = Nat.gcd n k := by
  unfold scaleCircleImage at hmem
  rcases Finset.mem_image.mp hmem with ⟨r, _, hr⟩
  have hset : scaleTargetFiberRepresentativeSet n k target = scaleFiberRepresentativeSet n k r := by
    rw [← hr]
    rfl
  rw [hset]
  exact scaleFiberRepresentativeSet_card hn

theorem scaleCircleImage_card_mul_targetFiberRepresentativeSet_card
    {n k : Nat} (hn : n ≠ 0) {target : C n} (hmem : target ∈ scaleCircleImage n k) :
    (scaleCircleImage n k).card *
      (scaleTargetFiberRepresentativeSet n k target).card = n := by
  rw [scaleCircleImage_card hn]
  rw [scaleTargetFiberRepresentativeSet_card_of_mem_scaleCircleImage hn hmem]
  rw [period_eq_n_div_gcd hn]
  rw [Nat.mul_comm]
  exact Nat.mul_div_cancel' (Nat.gcd_dvd_left n k)

theorem scaleCircleImage_card_mul_scaleKernelRepresentativeSet_card
    {n k : Nat} (hn : n ≠ 0) :
    (scaleCircleImage n k).card * (scaleKernelRepresentativeSet n k).card = n := by
  rw [scaleCircleImage_card hn]
  rw [scaleKernelRepresentativeSet_card hn]
  rw [period_eq_n_div_gcd hn]
  rw [Nat.mul_comm]
  exact Nat.mul_div_cancel' (Nat.gcd_dvd_left n k)

theorem scale_nat_eq_iff_nat_modEq_of_coprime {n k x y : Nat} (hcop : Nat.Coprime n k) :
    scale n k ((x : Nat) : C n) = scale n k ((y : Nat) : C n) ↔ x ≡ y [MOD n] := by
  have hbij : Function.Bijective (scale n k) := (scale_invertible_iff_coprime n k).mpr hcop
  constructor
  · intro h
    have hxy : ((x : Nat) : C n) = ((y : Nat) : C n) := hbij.1 h
    exact (ZMod.natCast_eq_natCast_iff x y n).mp hxy
  · intro h
    have hxy : ((x : Nat) : C n) = ((y : Nat) : C n) :=
      (ZMod.natCast_eq_natCast_iff x y n).mpr h
    exact congrArg (scale n k) hxy

theorem scale_factor_modEq {n k l : Nat} (h : k ≡ l [MOD n]) (x : C n) :
    scale n k x = scale n l x := by
  unfold scale
  have hcast : ((k : Nat) : ZMod n) = ((l : Nat) : ZMod n) :=
    (ZMod.natCast_eq_natCast_iff k l n).mpr h
  rw [hcast]

end Circle
