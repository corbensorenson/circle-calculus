import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.ZMod.Basic

/-!
# Circulant token-mixing layer: proved structural guarantees

A circulant (cyclic-convolution) token mixer over a length-`n` context is the operation
`(c ⋆ x) i = ∑ j, c j · x (i − j)` on signals `x : C n → R`, with a single learned kernel
`c : C n → R`. This is the math behind FNet / long-convolution / state-space mixing, and it
is exactly the `C n` group algebra.

This file proves the **structural** facts that make a circulant mixer well-behaved — the
kind of guarantees that matter for an architecture and that Lean can certify (as opposed to
model quality, which is empirical and out of scope):

* `circConv_shift_equivariant` — the mixer **commutes with cyclic shift** (translation
  equivariance): shifting the input shifts the output identically;
* `circConv_comm` — circular convolution is commutative (circulant operators commute);
* `circConv_add` — the mixer is additive (linear) in its input signal;
* `shiftBy_zero`, `shiftBy_add` — the cyclic shift is a genuine `C n` group action.

Shift-equivariance is the structural property that justifies treating a circulant mixer as
position-aware and translation-respecting. The usual `n`-kernel versus dense `n²` parameter
comparison is an implementation/design observation, not the theorem proved here.
-/

namespace Circle.Applications

variable {n : ℕ} {R : Type*}

/-- Cyclic shift of a signal by `s` positions on `C n`. -/
def shiftBy (s : ZMod n) (x : ZMod n → R) : ZMod n → R := fun i => x (i - s)

/-- A zero shift is the identity. -/
@[simp] theorem shiftBy_zero (x : ZMod n → R) : shiftBy (0 : ZMod n) x = x := by
  funext i; simp [shiftBy]

/-- Shifts compose additively: the cyclic shift is a `C n` group action. -/
theorem shiftBy_add (s t : ZMod n) (x : ZMod n → R) :
    shiftBy (s + t) x = shiftBy s (shiftBy t x) := by
  funext i
  unfold shiftBy
  rw [sub_add_eq_sub_sub]

variable [NeZero n] [CommRing R]

/-- Circulant (cyclic-convolution) token mixing with kernel `c`:
`(c ⋆ x) i = ∑ j, c j · x (i − j)`. -/
def circConv (c x : ZMod n → R) : ZMod n → R := fun i => ∑ j : ZMod n, c j * x (i - j)

/-- **Shift-equivariance.** A circulant mixer commutes with cyclic shift: shifting the
input by any amount `s` shifts the output by the same amount. This is the translation
equivariance that makes circulant mixing a principled, position-respecting token mixer. -/
theorem circConv_shift_equivariant (s : ZMod n) (c x : ZMod n → R) :
    circConv c (shiftBy s x) = shiftBy s (circConv c x) := by
  funext i
  unfold circConv shiftBy
  refine Finset.sum_congr rfl (fun j _ => ?_)
  rw [sub_right_comm]

/-- **Commutativity.** Circular convolution is commutative — circulant operators all
commute, since they are simultaneously diagonalized by the discrete Fourier transform. -/
theorem circConv_comm (c x : ZMod n → R) : circConv c x = circConv x c := by
  funext i
  unfold circConv
  rw [← Equiv.sum_comp (Equiv.subLeft i)]
  refine Finset.sum_congr rfl (fun j _ => ?_)
  simp only [Equiv.subLeft_apply]
  rw [sub_sub_cancel, mul_comm]

/-- **Linearity.** A circulant mixer is additive in its input signal. -/
theorem circConv_add (c x y : ZMod n → R) :
    circConv c (x + y) = circConv c x + circConv c y := by
  funext i
  simp only [circConv, Pi.add_apply, mul_add]
  rw [Finset.sum_add_distrib]

end Circle.Applications
