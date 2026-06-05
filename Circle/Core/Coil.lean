import Circle.Core.Rotation

namespace Circle

/-- The node reached after `steps` repeated rotations by `stride`. -/
def coilStep (n : Nat) (stride start steps : Nat) : C n :=
  (start : ZMod n) + ((steps * stride : Nat) : ZMod n)

/-- Closure at `steps` means the repeated rotation returns to the start node. -/
def closesAt (n : Nat) (stride start steps : Nat) : Prop :=
  coilStep n stride start steps = (start : ZMod n)

theorem closesAt_iff_stride_multiple_zero
    (n stride start steps : Nat) :
    closesAt n stride start steps ↔ ((steps * stride : Nat) : ZMod n) = 0 := by
  unfold closesAt coilStep
  constructor
  · intro h
    have h' :
        (start : ZMod n) + ((steps * stride : Nat) : ZMod n) =
          (start : ZMod n) + 0 := by
      simpa using h
    exact add_left_cancel h'
  · intro h
    simp [h]

end Circle
