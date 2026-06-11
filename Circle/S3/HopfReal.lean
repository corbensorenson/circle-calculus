import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring

/-!
# The Hopf map onto the real 2-sphere

This file builds the Hopf map `S³ → S²` with *real* coordinates, not a bounded
finite model. A point of `S³` is `(a,b,c,d) ∈ ℝ⁴` with `a²+b²+c²+d² = 1` (think
`z₁ = a + bi`, `z₂ = c + di`). The Hopf map sends it to a point of `ℝ³`, and we
prove:

* `hopf_norm`     : the image always satisfies `|h|² = (a²+b²+c²+d²)²`;
* `hopf_lands`    : hence on `S³` the image lies on the **actual** unit `S²`;
* `hopf_phase_*`  : multiplying `(z₁,z₂)` by a common unit phase (the circle
  action) leaves the image **unchanged** — the common-phase circle orbit stays inside
  one Hopf fiber.

What remains roadmap (tracked, not claimed): local triviality / the full fiber
*bundle* structure of `S³ → S²`. This file is the coordinate and fiber-invariance
spine that such a development sits on.
-/

namespace Circle.S3

/-- First coordinate of the Hopf image of `(a,b,c,d)`, i.e. `2·Re(z₁ z̄₂)`. -/
def hopfX (a b c d : ℝ) : ℝ := 2 * (a * c + b * d)

/-- Second coordinate of the Hopf image, i.e. `2·Im(z₁ z̄₂)`. -/
def hopfY (a b c d : ℝ) : ℝ := 2 * (b * c - a * d)

/-- Third coordinate of the Hopf image, i.e. `|z₁|² - |z₂|²`. -/
def hopfZ (a b c d : ℝ) : ℝ := a ^ 2 + b ^ 2 - c ^ 2 - d ^ 2

/-- **Norm identity.** The squared length of the Hopf image equals the squared
length of the source point — an unconditional polynomial identity. -/
theorem hopf_norm (a b c d : ℝ) :
    hopfX a b c d ^ 2 + hopfY a b c d ^ 2 + hopfZ a b c d ^ 2
      = (a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2) ^ 2 := by
  unfold hopfX hopfY hopfZ; ring

/-- **Lands on the 2-sphere.** A point of `S³` maps to a point of the actual unit
`S²`. -/
theorem hopf_lands {a b c d : ℝ} (h : a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = 1) :
    hopfX a b c d ^ 2 + hopfY a b c d ^ 2 + hopfZ a b c d ^ 2 = 1 := by
  rw [hopf_norm, h]; norm_num

/-- **Fiber invariance, X.** The common unit-phase circle action
`(a,b,c,d) ↦ (co·a−si·b, si·a+co·b, co·c−si·d, si·c+co·d)` with `co²+si²=1`
leaves the first Hopf coordinate unchanged. -/
theorem hopf_phase_X (a b c d co si : ℝ) (h : co ^ 2 + si ^ 2 = 1) :
    hopfX (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
      = hopfX a b c d := by
  have e : hopfX (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
      = (co ^ 2 + si ^ 2) * hopfX a b c d := by unfold hopfX; ring
  rw [e, h, one_mul]

/-- **Fiber invariance, Y.** -/
theorem hopf_phase_Y (a b c d co si : ℝ) (h : co ^ 2 + si ^ 2 = 1) :
    hopfY (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
      = hopfY a b c d := by
  have e : hopfY (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
      = (co ^ 2 + si ^ 2) * hopfY a b c d := by unfold hopfY; ring
  rw [e, h, one_mul]

/-- **Fiber invariance, Z.** -/
theorem hopf_phase_Z (a b c d co si : ℝ) (h : co ^ 2 + si ^ 2 = 1) :
    hopfZ (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
      = hopfZ a b c d := by
  have e : hopfZ (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
      = (co ^ 2 + si ^ 2) * hopfZ a b c d := by unfold hopfZ; ring
  rw [e, h, one_mul]

/-- **Common-phase invariance.** Acting by any common unit phase fixes the whole
Hopf image — the source point moves around a circle orbit while its image stays put. -/
theorem hopf_phase_invariant (a b c d co si : ℝ) (h : co ^ 2 + si ^ 2 = 1) :
    hopfX (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
        = hopfX a b c d ∧
      hopfY (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
        = hopfY a b c d ∧
      hopfZ (co * a - si * b) (si * a + co * b) (co * c - si * d) (si * c + co * d)
        = hopfZ a b c d :=
  ⟨hopf_phase_X a b c d co si h, hopf_phase_Y a b c d co si h, hopf_phase_Z a b c d co si h⟩

end Circle.S3
