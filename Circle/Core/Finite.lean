import Mathlib.Data.ZMod.Basic

namespace Circle

/-- The v0 circle is a cyclic address space, modeled as integers modulo `n`. -/
abbrev C (n : Nat) := ZMod n

/-- A node is an address in `C n`. -/
abbrev Node (n : Nat) := C n

end Circle

