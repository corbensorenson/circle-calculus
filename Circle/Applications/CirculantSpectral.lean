import Circle.Applications.Circulant
import Circle.Core.FiniteFourier

/-!
# Spectral facts for circulant token mixers

This module connects the public finite-Fourier character API to the existing
circulant mixer.  It proves the algebraic contract behind the phrase
"circulant convolution is diagonalized by finite Fourier characters": each
Fourier character coefficient of a circular convolution factors into the
matching kernel coefficient times the matching signal coefficient.
-/

namespace Circle.Applications

variable {n : Nat} {R : Type*} [NeZero n] [CommRing R]

/--
Finite-Fourier diagonalization contract for circular convolution.

For every cyclic character `χ`, the `χ` coefficient of `c ⋆ x` is the product
of the `χ` coefficient of `c` and the `χ` coefficient of `x`.
-/
theorem finiteFourierCoeff_circConv (χ : Circle.CyclicCharacter n R)
    (c x : ZMod n → R) :
    Circle.finiteFourierCoeff χ (circConv c x) =
      Circle.finiteFourierCoeff χ c * Circle.finiteFourierCoeff χ x := by
  unfold Circle.finiteFourierCoeff circConv
  calc
    (∑ i : ZMod n, (∑ j : ZMod n, c j * x (i - j)) * χ i)
        = ∑ i : ZMod n, ∑ j : ZMod n, (c j * x (i - j)) * χ i := by
          refine Finset.sum_congr rfl (fun i _ => ?_)
          rw [Finset.sum_mul]
    _ = ∑ j : ZMod n, ∑ i : ZMod n, (c j * x (i - j)) * χ i := by
          rw [Finset.sum_comm]
    _ = ∑ j : ZMod n, (c j * χ j) * ∑ i : ZMod n, x i * χ i := by
          refine Finset.sum_congr rfl (fun j _ => ?_)
          rw [← Equiv.sum_comp (Equiv.subRight j).symm]
          change
            (∑ i : ZMod n, (c j * x (i + j - j)) * χ (i + j)) =
              (c j * χ j) * ∑ i : ZMod n, x i * χ i
          calc
            (∑ i : ZMod n, (c j * x (i + j - j)) * χ (i + j))
                = ∑ i : ZMod n, (c j * x i) * (χ i * χ j) := by
                  refine Finset.sum_congr rfl (fun i _ => ?_)
                  simp [Circle.CyclicCharacter.map_add]
            _ = ∑ i : ZMod n, (c j * χ j) * (x i * χ i) := by
                  refine Finset.sum_congr rfl (fun i _ => ?_)
                  simp [mul_assoc, mul_comm, mul_left_comm]
            _ = (c j * χ j) * ∑ i : ZMod n, x i * χ i := by
                  rw [Finset.mul_sum]
    _ = (∑ j : ZMod n, c j * χ j) * ∑ i : ZMod n, x i * χ i := by
          rw [Finset.sum_mul]

end Circle.Applications
