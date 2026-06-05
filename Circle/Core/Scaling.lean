import Circle.Core.Finite

namespace Circle

/-- Scaling multiplies a node by `k` in `C n`. -/
def scale (n k : Nat) (x : C n) : C n :=
  (k : ZMod n) * x

end Circle

