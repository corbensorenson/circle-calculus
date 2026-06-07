import Circle.Basic
import Mathlib.Combinatorics.Additive.CauchyDavenport

namespace Circle

open scoped Pointwise

/-- Circle-form statement of the Cauchy-Davenport theorem.

For nonempty finite sets of addresses in a prime-size circle `C p`, the sumset
has size at least `min p (|s| + |t| - 1)`.
-/
theorem cauchy_davenport_prime_circle
    {p : Nat} (hp : p.Prime) {s t : Finset (C p)}
    (hs : s.Nonempty) (ht : t.Nonempty) :
    min p (s.card + t.card - 1) ≤ (s + t).card := by
  simpa [C] using ZMod.cauchy_davenport hp (s := s) (t := t) hs ht

end Circle
