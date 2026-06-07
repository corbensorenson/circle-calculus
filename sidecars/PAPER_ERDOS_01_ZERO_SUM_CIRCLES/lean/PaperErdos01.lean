import Circle.Erdos.EGZ
import Circle.Erdos.CauchyDavenport

namespace PaperErdos01

open scoped Pointwise

/-- Paper-sidecar access to the Circle-form Erdős-Ginzburg-Ziv bridge. -/
theorem egz_bridge
    {ι : Type*} {n : Nat} {s : Finset ι} (a : ι → Circle.C n)
    (hs : 2 * n - 1 ≤ s.card) :
    ∃ t ⊆ s, t.card = n ∧ ∑ i ∈ t, a i = 0 :=
  Circle.erdos_ginzburg_ziv a hs

/-- Paper-sidecar access to the Circle-form Cauchy-Davenport bridge. -/
theorem cauchy_davenport_bridge
    {p : Nat} (hp : p.Prime) {s t : Finset (Circle.C p)}
    (hs : s.Nonempty) (ht : t.Nonempty) :
    min p (s.card + t.card - 1) ≤ (s + t).card :=
  Circle.cauchy_davenport_prime_circle hp hs ht

end PaperErdos01
