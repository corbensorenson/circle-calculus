import Circle.S3.Scaffold

/-!
# The unit-quaternion double cover of rotations (real spine)

This file extends the real-quaternion conjugation action
`quaternionConjugationAction q v = q v q⋆` (defined in `Circle.S3.Scaffold`) with the
pieces that make it the genuine double cover `Sp(1) = S³ → SO(3)`:

* `quaternionConjugation_normSq` — conjugation by a **unit** quaternion preserves the
  norm (it is an isometry / lands in the orthogonal group);
* `quaternionConjugation_re` — it preserves the real part, hence preserves the
  pure-imaginary copy of `ℝ³`;
* `quaternionConjugation_mul` — it is a **monoid homomorphism**
  (conjugation by `a*b` = conjugation by `a` then `b`);
* together with the existing two-to-one fact `quaternionConjugation_neg`
  (`q` and `-q` agree), `realUnitQuaternion_eq_pm_one` shows the **real** unit
  quaternions are exactly `±1`, and `quaternionConjugation_real_trivial` shows they
  act trivially.

Together these say: the conjugation action is a norm- and real-part-preserving
monoid homomorphism that identifies `q` with `-q` — the algebraic heart of the
double cover.

And `quaternionConjugation_trivial_iff_pm_one` **completes the kernel computation**: the
kernel of the action on the unit quaternions is *exactly* `{±1}`.

Roadmap (tracked, not claimed): surjectivity of the action onto `SO(3)`. With the exact
kernel now in hand, that is the one remaining step to the full double-cover isomorphism
`Sp(1) / {±1} ≅ SO(3)`.
-/

namespace Circle.S3

/-- **Isometry / orthogonality.** Conjugation by a unit quaternion preserves the
quaternion norm — the property that makes the action a rotation. -/
theorem quaternionConjugation_normSq {q : RealQuaternion} (hq : Quaternion.normSq q = 1)
    (v : RealQuaternion) :
    Quaternion.normSq (quaternionConjugationAction q v) = Quaternion.normSq v := by
  unfold quaternionConjugationAction
  rw [map_mul, map_mul, Quaternion.normSq_star, hq]
  ring

/-- Conjugation by a unit quaternion preserves the real part. -/
theorem quaternionConjugation_re {q : RealQuaternion} (hq : Quaternion.normSq q = 1)
    (v : RealQuaternion) : (quaternionConjugationAction q v).re = v.re := by
  have key : (quaternionConjugationAction q v).re = v.re * Quaternion.normSq q := by
    unfold quaternionConjugationAction
    rw [Quaternion.normSq_def']
    simp only [Quaternion.re_mul, Quaternion.imI_mul, Quaternion.imJ_mul, Quaternion.imK_mul,
      Quaternion.re_star, Quaternion.imI_star, Quaternion.imJ_star, Quaternion.imK_star]
    ring
  rw [key, hq, mul_one]

/-- **Homomorphism.** Conjugating by a product is conjugating by each factor in turn:
`q ↦ quaternionConjugationAction q` is a monoid homomorphism into the rotations. -/
theorem quaternionConjugation_mul (a b v : RealQuaternion) :
    quaternionConjugationAction (a * b) v
      = quaternionConjugationAction a (quaternionConjugationAction b v) := by
  unfold quaternionConjugationAction
  rw [star_mul]
  simp only [mul_assoc]

/-- **Kernel, easy direction.** A *real* unit quaternion acts trivially. -/
theorem quaternionConjugation_real_trivial {q : RealQuaternion}
    (hq : Quaternion.normSq q = 1) (hreal : q = (q.re : RealQuaternion)) (v : RealQuaternion) :
    quaternionConjugationAction q v = v := by
  unfold quaternionConjugationAction
  have hcomm : q * v = v * q := by
    conv_lhs => rw [hreal]
    rw [Quaternion.coe_commutes, ← hreal]
  rw [hcomm, mul_assoc, Quaternion.self_mul_star, hq]
  simp

/-- **The real unit quaternions are exactly `±1`.** With `quaternionConjugation_neg`
(`q` and `-q` agree) this identifies the trivially-acting real quaternions and is the
`±1` content of the double cover. -/
theorem realUnitQuaternion_eq_pm_one {q : RealQuaternion} (hq : Quaternion.normSq q = 1)
    (hreal : q = (q.re : RealQuaternion)) : q = 1 ∨ q = -1 := by
  have hsq : q.re * q.re = 1 := by
    have h := Quaternion.normSq_coe (R := ℝ) q.re
    rw [← hreal, hq, sq] at h
    exact h.symm
  rcases mul_self_eq_one_iff.mp hsq with h | h
  · left; rw [hreal, h]; simp
  · right; rw [hreal, h]; simp

/-- **Exact kernel.** A unit quaternion fixes every vector under conjugation if and only if
it is `±1`. Together with the isometry (`quaternionConjugation_normSq`) and homomorphism
(`quaternionConjugation_mul`) facts, this *completes* the kernel computation for the double
cover: the kernel of `q ↦ (v ↦ q v q⋆)` on the unit quaternions is exactly `{±1}`. -/
theorem quaternionConjugation_trivial_iff_pm_one {q : RealQuaternion}
    (hq : Quaternion.normSq q = 1) :
    (∀ v : RealQuaternion, quaternionConjugationAction q v = v) ↔ (q = 1 ∨ q = -1) := by
  constructor
  · intro h
    -- A trivial conjugation action means q commutes with every quaternion.
    have hc : ∀ w : RealQuaternion, q * w = w * q := by
      intro w
      have hqq : star q * q = 1 := by rw [Quaternion.star_mul_self, hq]; simp
      have hw := h w
      unfold quaternionConjugationAction at hw
      calc q * w = q * w * 1 := by rw [mul_one]
        _ = q * w * (star q * q) := by rw [hqq]
        _ = q * w * star q * q := by rw [← mul_assoc]
        _ = w * q := by rw [hw]
    -- Commuting with the imaginary units `i` and `j` forces the imaginary parts to vanish.
    have e1 := congrArg (fun x : RealQuaternion => x.imJ) (hc ⟨0, 1, 0, 0⟩)
    have e2 := congrArg (fun x : RealQuaternion => x.imK) (hc ⟨0, 1, 0, 0⟩)
    have e3 := congrArg (fun x : RealQuaternion => x.imK) (hc ⟨0, 0, 1, 0⟩)
    simp only [Quaternion.imJ_mul, Quaternion.imK_mul] at e1 e2 e3
    have hreal : q = (q.re : RealQuaternion) := by
      apply Quaternion.ext <;> simp <;> linarith [e1, e2, e3]
    exact realUnitQuaternion_eq_pm_one hq hreal
  · rintro (rfl | rfl) v
    · exact quaternionConjugation_one v
    · exact (quaternionConjugation_neg 1 v).trans (quaternionConjugation_one v)

end Circle.S3
