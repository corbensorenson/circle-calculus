import Circle.Basic
import Mathlib.Combinatorics.HalesJewett

universe u v

namespace Circle

/-- Hales-Jewett bridge: every finite coloring of a high-dimensional word cube
contains a monochromatic combinatorial line.
-/
theorem hales_jewett_bridge (α : Type u) [Finite α] (κ : Type v) [Finite κ] :
    ∃ (ι : Type) (_ : Fintype ι), ∀ C : (ι → α) → κ,
      ∃ l : Combinatorics.Line α ι, l.IsMono C := by
  exact Combinatorics.Line.exists_mono_in_high_dimension α κ

/-- Van der Waerden/Hales-Jewett bridge: finite colorings of an additive
commutative monoid contain a monochromatic homothetic copy of any finite shape.
-/
theorem van_der_waerden_homothetic_bridge
    {M κ : Type*} [AddCommMonoid M] (S : Finset M) [Finite κ] (C : M → κ) :
    ∃ a > 0, ∃ (b : M) (c : κ), ∀ s ∈ S, C (a • s + b) = c := by
  exact Combinatorics.exists_mono_homothetic_copy S C

end Circle
