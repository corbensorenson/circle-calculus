import Circle.Erdos.RothAP

namespace PaperErdos03

/-- Paper-sidecar access to the Roth three-term-AP bridge over naturals. -/
theorem roth_three_ap_nat_bridge
    {n : Nat} {ε : ℝ} (hε : 0 < ε)
    (hG : cornersTheoremBound (ε / 3) ≤ n)
    (A : Finset Nat) (hAn : A ⊆ Finset.range n) (hAε : ε * n ≤ A.card) :
    ¬ ThreeAPFree (A : Set Nat) :=
  Circle.roth_three_ap_nat_bridge hε hG A hAn hAε

/-- Paper-sidecar access to the Roth-number sublinearity bridge. -/
theorem roth_number_sublinear_bridge :
    Asymptotics.IsLittleO Filter.atTop
      (fun N => (rothNumberNat N : ℝ)) (fun N => (N : ℝ)) :=
  Circle.roth_number_sublinear_bridge

end PaperErdos03
