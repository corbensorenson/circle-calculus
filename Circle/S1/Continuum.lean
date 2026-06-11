import Mathlib.Topology.Instances.AddCircle.Real

/-!
# The continuum limit: finite circles inside the real circle

This file connects the finite circle `C n = ZMod n` to the **actual continuous circle**
`UnitAddCircle = ℝ / ℤ`, via mathlib's homomorphism `ZMod.toAddCircle`
(`j mod n ↦ j / n mod 1`). The point is to make precise the sense in which the finite
circles *approximate* the real circle.

* `finiteCircle_toRealCircle_add` / `_zero` — the embedding turns rotation in `C n` into
  genuine rotation of the real circle (it is a group homomorphism);
* `finiteCircle_toRealCircle_injective` — `C n` embeds **faithfully**: distinct finite
  nodes land on distinct real-circle points;
* `finiteCircle_lands_in_torsion` — the image lies in the `n`-torsion of the real circle
  (the "`n`-th roots of unity"): every embedded node is killed by `n`;
* `finiteCircle_refines` — **the directed-system step**: for any refinement
  `n ↦ n·d`, the circle `C n` sits *inside* `C (n·d)` at the real-circle level. The
  finite circles therefore form a nested family `C₁ ⊆ C₂ ⊆ C₆ ⊆ …` whose union is the
  rational points `ℚ/ℤ ⊆ ℝ/ℤ`.

The first facts are Circle-facing wrappers around mathlib's `ZMod.toAddCircle`; the
refinement theorem is the genuinely new content — the spine of the continuum limit.

Roadmap (tracked, not claimed): that the union of all finite circles is **dense** in the
real circle, and that the real circle is its metric completion. Those use the topology of
`AddCircle` and are the next step.
-/

namespace Circle.S1

/-- **Rotation-compatible.** The embedding `ZMod.toAddCircle : C n → ℝ/ℤ` turns rotation
(addition) in the finite circle into addition on the real circle. -/
theorem finiteCircle_toRealCircle_add {n : ℕ} [NeZero n] (a b : ZMod n) :
    ZMod.toAddCircle (a + b) = ZMod.toAddCircle a + ZMod.toAddCircle b :=
  map_add _ _ _

/-- The base node of `C n` lands on the base point of the real circle. -/
theorem finiteCircle_toRealCircle_zero {n : ℕ} [NeZero n] :
    ZMod.toAddCircle (0 : ZMod n) = (0 : UnitAddCircle) :=
  map_zero _

/-- **Faithful embedding.** Distinct nodes of `C n` map to distinct points of the real
circle: `C n` is realized as an honest finite subset of `ℝ / ℤ`. -/
theorem finiteCircle_toRealCircle_injective {n : ℕ} [NeZero n] :
    Function.Injective (ZMod.toAddCircle : ZMod n → UnitAddCircle) :=
  ZMod.toAddCircle_injective n

/-- Two finite nodes coincide on the real circle iff they are equal in `C n`. -/
theorem finiteCircle_toRealCircle_inj {n : ℕ} [NeZero n] {a b : ZMod n} :
    ZMod.toAddCircle a = ZMod.toAddCircle b ↔ a = b :=
  ZMod.toAddCircle_inj

/-- **The image lies in the `n`-torsion.** Every embedded node, added to itself `n`
times, returns to the base point — the image of `C n` is among the `n`-th "roots of
unity" of the real circle. -/
theorem finiteCircle_lands_in_torsion {n : ℕ} [NeZero n] (a : ZMod n) :
    n • ZMod.toAddCircle a = (0 : UnitAddCircle) := by
  rw [← map_nsmul]
  have hna : n • a = 0 := by rw [nsmul_eq_mul, ZMod.natCast_self, zero_mul]
  rw [hna, map_zero]

/-- **The refinement step (continuum-limit spine).** For any refinement factor `d ≠ 0`,
the finite circle `C n` sits inside `C (n*d)` as a subset of the real circle: node `k` of
`C n` is the same real-circle point as node `k*d` of `C (n*d)`. Iterating, the finite
circles form a nested directed family filling out the rational points of `ℝ / ℤ`. -/
theorem finiteCircle_refines (n d k : ℕ) [NeZero n] [NeZero (n * d)] (hd : d ≠ 0) :
    ZMod.toAddCircle ((k : ZMod n))
      = ZMod.toAddCircle (((k * d : ℕ) : ZMod (n * d))) := by
  rw [ZMod.toAddCircle_natCast, ZMod.toAddCircle_natCast]
  have hn : (n : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (NeZero.ne n)
  have hd' : (d : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hd
  congr 1
  push_cast
  field_simp

end Circle.S1
