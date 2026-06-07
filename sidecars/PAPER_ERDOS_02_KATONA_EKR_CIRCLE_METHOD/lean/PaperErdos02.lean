import Circle.Erdos.KatonaEKR

namespace PaperErdos02

/-- Paper-sidecar access to the Katona prefix-density bridge. -/
theorem katona_prefixed_density_bridge
    {X : Type*} [Fintype X] [DecidableEq X] (s : Finset X) :
    (Numbering.prefixed s).dens = ((Fintype.card X).choose s.card : ℚ≥0)⁻¹ :=
  Circle.katona_prefixed_density_bridge s

/-- Paper-sidecar access to the Erdős-Ko-Rado circle-method bridge. -/
theorem erdos_ko_rado_circle_bridge
    {n r : Nat} {𝒜 : Finset (Finset (Fin n))}
    (h𝒜 : (𝒜 : Set (Finset (Fin n))).Intersecting)
    (hSized : (𝒜 : Set (Finset (Fin n))).Sized r)
    (hr : r ≤ n / 2) :
    𝒜.card ≤ (n - 1).choose (r - 1) :=
  Circle.erdos_ko_rado_circle_bridge h𝒜 hSized hr

end PaperErdos02
