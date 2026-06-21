import Mathlib.Data.Nat.Prime.Basic

namespace Circle.Applications

/-!
Finite temporal-coil bookkeeping.

This module ports only the stable arithmetic contract from the Drive temporal
coil notes: prime windows, coprime strides, and the "abyss" all-to-all edge
counts. It does not assert model-quality or training-performance claims.
-/

/-- A temporal-coil stride is a nonzero coprime stride below the window size. -/
def temporalCoilStride (window stride : Nat) : Prop :=
  0 < stride ∧ stride < window ∧ Nat.Coprime window stride

theorem temporalCoilStride_of_prime {window stride : Nat} (hp : Nat.Prime window)
    (hs0 : 0 < stride) (hsw : stride < window) :
    temporalCoilStride window stride := by
  refine ⟨hs0, hsw, ?_⟩
  exact Nat.coprime_of_lt_prime hs0.ne' hsw hp

theorem temporalPrimeLadder_examples :
    Nat.Prime 11 ∧ Nat.Prime 17 ∧ Nat.Prime 29 := by
  native_decide

theorem temporalStrideSet29_examples :
    temporalCoilStride 29 1 ∧
      temporalCoilStride 29 2 ∧
      temporalCoilStride 29 3 ∧
      temporalCoilStride 29 5 ∧
      temporalCoilStride 29 8 := by
  have hp : Nat.Prime 29 := by native_decide
  exact ⟨temporalCoilStride_of_prime hp (by decide) (by decide),
    temporalCoilStride_of_prime hp (by decide) (by decide),
    temporalCoilStride_of_prime hp (by decide) (by decide),
    temporalCoilStride_of_prime hp (by decide) (by decide),
    temporalCoilStride_of_prime hp (by decide) (by decide)⟩

/-- Number of temporal sets visible from either endpoint when the abyss edge is omitted. -/
def temporalAbyssEndpointNeighborCount (setCount : Nat) : Nat :=
  setCount - 2

/-- Number of temporal sets visible from an interior set when only self-targeting is omitted. -/
def temporalAbyssInteriorNeighborCount (setCount : Nat) : Nat :=
  setCount - 1

/-- Per-token outgoing edges for an endpoint temporal set. -/
def temporalAbyssEndpointNodeEdges (setCount vocab : Nat) : Nat :=
  temporalAbyssEndpointNeighborCount setCount * vocab

/-- Per-token outgoing edges for an interior temporal set. -/
def temporalAbyssInteriorNodeEdges (setCount vocab : Nat) : Nat :=
  temporalAbyssInteriorNeighborCount setCount * vocab

/--
Network-wide directed token edges when the two endpoint sets omit the abyss
target and every interior set omits only self-targeting.
-/
def temporalAbyssTotalDirectedEdges (setCount vocab : Nat) : Nat :=
  2 * vocab * temporalAbyssEndpointNodeEdges setCount vocab +
    (setCount - 2) * vocab * temporalAbyssInteriorNodeEdges setCount vocab

theorem temporalAbyss59EndpointNodeEdges16000 :
    temporalAbyssEndpointNodeEdges 59 16000 = 912000 := by
  native_decide

theorem temporalAbyss59InteriorNodeEdges16000 :
    temporalAbyssInteriorNodeEdges 59 16000 = 928000 := by
  native_decide

theorem temporalAbyss59TotalDirectedEdges16000 :
    temporalAbyssTotalDirectedEdges 59 16000 = 875520000000 := by
  native_decide

end Circle.Applications
