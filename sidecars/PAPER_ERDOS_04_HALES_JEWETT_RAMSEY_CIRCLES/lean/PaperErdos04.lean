import Circle.Erdos.RamseyHJ

universe u v

namespace PaperErdos04

/-- Paper-sidecar access to the Hales-Jewett bridge. -/
theorem hales_jewett_bridge (α : Type u) [Finite α] (κ : Type v) [Finite κ] :
    ∃ (ι : Type) (_ : Fintype ι), ∀ C : (ι → α) → κ,
      ∃ l : Combinatorics.Line α ι, l.IsMono C :=
  Circle.hales_jewett_bridge α κ

/-- Paper-sidecar access to the Van der Waerden homothetic-copy bridge. -/
theorem van_der_waerden_homothetic_bridge
    {M κ : Type*} [AddCommMonoid M] (S : Finset M) [Finite κ] (C : M → κ) :
    ∃ a > 0, ∃ (b : M) (c : κ), ∀ s ∈ S, C (a • s + b) = c :=
  Circle.van_der_waerden_homothetic_bridge S C

end PaperErdos04
