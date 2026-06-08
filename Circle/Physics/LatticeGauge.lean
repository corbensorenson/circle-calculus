import Mathlib.Data.ZMod.Basic

/-!
Finite lattice-gauge seeds for Circle Calculus physics tracks.

This module models only bounded modular phase bookkeeping: path holonomy,
path reversal, endpoint gauge shifts, closed-loop invariance, and a square
plaquette specialization. It is not a continuum gauge theory or physics claim.
-/

namespace Circle.Physics

def pathHolonomy (phases : List (ZMod n)) : ZMod n :=
  phases.sum

def reversePhases (phases : List (ZMod n)) : List (ZMod n) :=
  phases.reverse.map Neg.neg

structure GaugePath (n : Nat) where
  phases : List (ZMod n)
  sourceGauge : ZMod n
  targetGauge : ZMod n

def gaugeTransformHolonomy (path : GaugePath n) : ZMod n :=
  pathHolonomy path.phases + path.sourceGauge - path.targetGauge

structure Plaquette (n : Nat) where
  bottom : ZMod n
  right : ZMod n
  top : ZMod n
  left : ZMod n
  baseGauge : ZMod n

def Plaquette.phases (p : Plaquette n) : List (ZMod n) :=
  [p.bottom, p.right, p.top, p.left]

def Plaquette.path (p : Plaquette n) : GaugePath n :=
  { phases := p.phases, sourceGauge := p.baseGauge, targetGauge := p.baseGauge }

theorem pathHolonomy_concat (left right : List (ZMod n)) :
    pathHolonomy (left ++ right) = pathHolonomy left + pathHolonomy right := by
  unfold pathHolonomy
  simp [List.sum_append]

theorem pathHolonomy_sum_neg (phases : List (ZMod n)) :
    (phases.map Neg.neg).sum = - phases.sum := by
  induction phases with
  | nil => simp
  | cons x xs ih =>
      simp [ih]
      ac_rfl

theorem pathHolonomy_reverse (phases : List (ZMod n)) :
    pathHolonomy (reversePhases phases) = - pathHolonomy phases := by
  unfold pathHolonomy reversePhases
  rw [pathHolonomy_sum_neg]
  simp

structure GaugeLink (n : Nat) where
  source : Nat
  target : Nat
  phase : ZMod n

def GaugeLink.reverse (link : GaugeLink n) : GaugeLink n :=
  { source := link.target, target := link.source, phase := -link.phase }

theorem gaugeLink_reverse_reverse (link : GaugeLink n) :
    link.reverse.reverse = link := by
  cases link
  simp [GaugeLink.reverse]

theorem gaugeLink_reverse_reverse_list (links : List (GaugeLink n)) :
    links.map (GaugeLink.reverse ∘ GaugeLink.reverse) = links := by
  induction links with
  | nil => simp
  | cons link rest ih =>
      change link.reverse.reverse ::
          rest.map (GaugeLink.reverse ∘ GaugeLink.reverse) = link :: rest
      rw [ih, gaugeLink_reverse_reverse]

structure GaugeLinkPath (n : Nat) where
  links : List (GaugeLink n)

def GaugeLinkPath.empty (n : Nat) : GaugeLinkPath n :=
  { links := [] }

def GaugeLinkPath.phases (path : GaugeLinkPath n) : List (ZMod n) :=
  path.links.map GaugeLink.phase

def GaugeLinkPath.holonomy (path : GaugeLinkPath n) : ZMod n :=
  pathHolonomy path.phases

def GaugeLinkPath.concat (left right : GaugeLinkPath n) : GaugeLinkPath n :=
  { links := left.links ++ right.links }

def GaugeLinkPath.reverse (path : GaugeLinkPath n) : GaugeLinkPath n :=
  { links := path.links.reverse.map GaugeLink.reverse }

def linksComposable : List (GaugeLink n) -> Prop
  | [] => True
  | [_] => True
  | first :: second :: rest => first.target = second.source ∧ linksComposable (second :: rest)

def GaugeLinkPath.composable (path : GaugeLinkPath n) : Prop :=
  linksComposable path.links

def firstSource? : List (GaugeLink n) -> Option Nat
  | [] => none
  | link :: _ => some link.source

def lastTarget? : List (GaugeLink n) -> Option Nat
  | [] => none
  | [link] => some link.target
  | _ :: second :: rest => lastTarget? (second :: rest)

def linksBoundaryComposable (left right : List (GaugeLink n)) : Prop :=
  match lastTarget? left, firstSource? right with
  | some target, some source => target = source
  | _, _ => True

def GaugeLinkPath.source? (path : GaugeLinkPath n) : Option Nat :=
  firstSource? path.links

def GaugeLinkPath.target? (path : GaugeLinkPath n) : Option Nat :=
  lastTarget? path.links

def GaugeLinkPath.boundaryComposable (left right : GaugeLinkPath n) : Prop :=
  linksBoundaryComposable left.links right.links

theorem gaugeLinkPathHolonomy_concat (left right : GaugeLinkPath n) :
    (left.concat right).holonomy = left.holonomy + right.holonomy := by
  unfold GaugeLinkPath.holonomy GaugeLinkPath.concat GaugeLinkPath.phases
  simp [pathHolonomy_concat]

theorem gaugeLinkPath_concat_empty_left (path : GaugeLinkPath n) :
    (GaugeLinkPath.empty n).concat path = path := by
  cases path with
  | mk links =>
      simp [GaugeLinkPath.empty, GaugeLinkPath.concat]

theorem gaugeLinkPath_concat_empty_right (path : GaugeLinkPath n) :
    path.concat (GaugeLinkPath.empty n) = path := by
  cases path with
  | mk links =>
      simp [GaugeLinkPath.empty, GaugeLinkPath.concat]

theorem gaugeLinkPath_concat_assoc
    (left middle right : GaugeLinkPath n) :
    (left.concat middle).concat right = left.concat (middle.concat right) := by
  cases left with
  | mk leftLinks =>
      cases middle with
      | mk middleLinks =>
          cases right with
          | mk rightLinks =>
              simp [GaugeLinkPath.concat, List.append_assoc]

theorem lastTarget?_append_cons
    (left : List (GaugeLink n)) (link : GaugeLink n) (right : List (GaugeLink n)) :
    lastTarget? (left ++ link :: right) = lastTarget? (link :: right) := by
  induction left with
  | nil =>
      simp
  | cons first rest ih =>
      cases rest with
      | nil =>
          simp [lastTarget?]
      | cons second tail =>
          simpa [lastTarget?] using ih

theorem linksComposable_cons_of_boundary
    (first : GaugeLink n) (rest : List (GaugeLink n))
    (hrest : linksComposable rest)
    (hboundary : linksBoundaryComposable [first] rest) :
    linksComposable (first :: rest) := by
  cases rest with
  | nil =>
      simp [linksComposable]
  | cons second tail =>
      simp [linksComposable, linksBoundaryComposable, firstSource?, lastTarget?] at hboundary ⊢
      exact ⟨hboundary, hrest⟩

theorem linksComposable_append_of_composable
    (left right : List (GaugeLink n))
    (hleft : linksComposable left)
    (hright : linksComposable right)
    (hboundary : linksBoundaryComposable left right) :
    linksComposable (left ++ right) := by
  induction left with
  | nil =>
      simpa using hright
  | cons first rest ih =>
      cases rest with
      | nil =>
          simpa using
            linksComposable_cons_of_boundary first right hright hboundary
      | cons second tail =>
          simp [linksComposable] at hleft ⊢
          refine ⟨hleft.1, ?_⟩
          exact ih hleft.2 (by
            simpa [linksBoundaryComposable, lastTarget?] using hboundary)

theorem gaugeLinkPath_concat_composable_of_boundary
    (left right : GaugeLinkPath n)
    (hleft : left.composable)
    (hright : right.composable)
    (hboundary : left.boundaryComposable right) :
    (left.concat right).composable := by
  exact linksComposable_append_of_composable
    left.links right.links hleft hright hboundary

theorem gaugeLinkPath_sourceOpt_concat_cons_left
    (first : GaugeLink n) (leftRest : List (GaugeLink n)) (right : GaugeLinkPath n) :
    ((GaugeLinkPath.mk (first :: leftRest)).concat right).source? =
      some first.source := by
  simp [GaugeLinkPath.source?, GaugeLinkPath.concat, firstSource?]

theorem gaugeLinkPath_targetOpt_concat_cons_right
    (left : GaugeLinkPath n) (first : GaugeLink n) (rightRest : List (GaugeLink n)) :
    (left.concat (GaugeLinkPath.mk (first :: rightRest))).target? =
      (GaugeLinkPath.mk (first :: rightRest)).target? := by
  cases left with
  | mk leftLinks =>
      simp [GaugeLinkPath.target?, GaugeLinkPath.concat, lastTarget?_append_cons]

def linksHaveEndpoints
    (source target : Nat) : List (GaugeLink n) -> Prop
  | [] => source = target
  | first :: rest => first.source = source ∧ lastTarget? (first :: rest) = some target

theorem linksBoundaryComposable_of_endpoints
    {leftSource leftTarget rightSource rightTarget : Nat}
    {left right : List (GaugeLink n)}
    (hleft : linksHaveEndpoints leftSource leftTarget left)
    (hright : linksHaveEndpoints rightSource rightTarget right)
    (hboundary : leftTarget = rightSource) :
    linksBoundaryComposable left right := by
  cases left with
  | nil =>
      simp [linksBoundaryComposable, lastTarget?]
  | cons leftFirst leftRest =>
      cases right with
      | nil =>
          simp [linksBoundaryComposable, firstSource?]
      | cons rightFirst rightRest =>
          simp [linksHaveEndpoints] at hleft hright
          simp [linksBoundaryComposable, firstSource?, hleft.2, hright.1, hboundary]

theorem linksHaveEndpoints_append
    {source middle target : Nat}
    {left right : List (GaugeLink n)}
    (hleft : linksHaveEndpoints source middle left)
    (hright : linksHaveEndpoints middle target right) :
    linksHaveEndpoints source target (left ++ right) := by
  cases left with
  | nil =>
      cases right with
      | nil =>
          simp [linksHaveEndpoints] at hleft hright ⊢
          exact hleft.trans hright
      | cons rightFirst rightRest =>
          simp [linksHaveEndpoints] at hleft hright ⊢
          exact ⟨hright.1.trans hleft.symm, hright.2⟩
  | cons leftFirst leftRest =>
      cases right with
      | nil =>
          simp [linksHaveEndpoints] at hleft hright ⊢
          exact ⟨hleft.1, by simpa [hright] using hleft.2⟩
      | cons rightFirst rightRest =>
          simp [linksHaveEndpoints] at hleft hright ⊢
          exact ⟨hleft.1, by
            change lastTarget? ((leftFirst :: leftRest) ++ rightFirst :: rightRest) = some target
            rw [lastTarget?_append_cons]
            exact hright.2⟩

structure CheckedGaugePath (n : Nat) where
  source : Nat
  target : Nat
  links : List (GaugeLink n)
  composable : linksComposable links
  endpoints : linksHaveEndpoints source target links

def CheckedGaugePath.identity (n vertex : Nat) : CheckedGaugePath n :=
  { source := vertex,
    target := vertex,
    links := [],
    composable := by simp [linksComposable],
    endpoints := by simp [linksHaveEndpoints] }

def CheckedGaugePath.singleton (link : GaugeLink n) : CheckedGaugePath n :=
  { source := link.source,
    target := link.target,
    links := [link],
    composable := by simp [linksComposable],
    endpoints := by simp [linksHaveEndpoints, lastTarget?] }

def CheckedGaugePath.concat
    (left right : CheckedGaugePath n)
    (hboundary : left.target = right.source) : CheckedGaugePath n :=
  { source := left.source,
    target := right.target,
    links := left.links ++ right.links,
    composable :=
      linksComposable_append_of_composable
        left.links
        right.links
        left.composable
        right.composable
        (linksBoundaryComposable_of_endpoints
          left.endpoints
          right.endpoints
          hboundary),
    endpoints := linksHaveEndpoints_append left.endpoints
      (by simpa [hboundary] using right.endpoints) }

def CheckedGaugePath.holonomy (path : CheckedGaugePath n) : ZMod n :=
  pathHolonomy (path.links.map GaugeLink.phase)

def CheckedGaugePath.toLinkPath (path : CheckedGaugePath n) : GaugeLinkPath n :=
  { links := path.links }

def CheckedGaugePath.closed (path : CheckedGaugePath n) : Prop :=
  path.source = path.target

def CheckedGaugePath.gaugeShiftedHolonomy
    (path : CheckedGaugePath n) (gauge : Nat → ZMod n) : ZMod n :=
  path.holonomy + gauge path.source - gauge path.target

theorem checkedGaugePath_identity_source (n vertex : Nat) :
    (CheckedGaugePath.identity n vertex).source = vertex := by
  rfl

theorem checkedGaugePath_identity_target (n vertex : Nat) :
    (CheckedGaugePath.identity n vertex).target = vertex := by
  rfl

theorem checkedGaugePath_singleton_source (link : GaugeLink n) :
    (CheckedGaugePath.singleton link).source = link.source := by
  rfl

theorem checkedGaugePath_singleton_target (link : GaugeLink n) :
    (CheckedGaugePath.singleton link).target = link.target := by
  rfl

theorem checkedGaugePath_concat_source
    (left right : CheckedGaugePath n) (hboundary : left.target = right.source) :
    (left.concat right hboundary).source = left.source := by
  rfl

theorem checkedGaugePath_concat_target
    (left right : CheckedGaugePath n) (hboundary : left.target = right.source) :
    (left.concat right hboundary).target = right.target := by
  rfl

theorem checkedGaugePath_concat_identity_left (path : CheckedGaugePath n) :
    (CheckedGaugePath.identity n path.source).concat path rfl = path := by
  cases path
  simp [CheckedGaugePath.identity, CheckedGaugePath.concat]

theorem checkedGaugePath_concat_identity_right (path : CheckedGaugePath n) :
    path.concat (CheckedGaugePath.identity n path.target) rfl = path := by
  cases path
  simp [CheckedGaugePath.identity, CheckedGaugePath.concat]

theorem checkedGaugePath_concat_assoc
    (left middle right : CheckedGaugePath n)
    (hleft : left.target = middle.source)
    (hright : middle.target = right.source) :
    (left.concat middle hleft).concat right
        (by simpa [CheckedGaugePath.concat] using hright) =
      left.concat (middle.concat right hright)
        (by simpa [CheckedGaugePath.concat] using hleft) := by
  cases left
  cases middle
  cases right
  simp [CheckedGaugePath.concat, List.append_assoc]

theorem checkedGaugePath_identity_holonomy (n vertex : Nat) :
    (CheckedGaugePath.identity n vertex).holonomy = 0 := by
  simp [CheckedGaugePath.holonomy, CheckedGaugePath.identity, pathHolonomy]

theorem checkedGaugePath_singleton_holonomy (link : GaugeLink n) :
    (CheckedGaugePath.singleton link).holonomy = link.phase := by
  simp [CheckedGaugePath.holonomy, CheckedGaugePath.singleton, pathHolonomy]

theorem checkedGaugePath_concat_holonomy
    (left right : CheckedGaugePath n) (hboundary : left.target = right.source) :
    (left.concat right hboundary).holonomy = left.holonomy + right.holonomy := by
  cases left
  cases right
  simp [CheckedGaugePath.holonomy, CheckedGaugePath.concat, pathHolonomy, List.sum_append]

theorem checkedGaugePath_toLinkPath_composable (path : CheckedGaugePath n) :
    path.toLinkPath.composable := by
  exact path.composable

theorem checkedGaugePath_toLinkPath_holonomy (path : CheckedGaugePath n) :
    path.toLinkPath.holonomy = path.holonomy := by
  rfl

theorem checkedGaugePath_toLinkPath_concat
    (left right : CheckedGaugePath n) (hboundary : left.target = right.source) :
    (left.concat right hboundary).toLinkPath =
      left.toLinkPath.concat right.toLinkPath := by
  rfl

theorem checkedGaugePath_identity_closed (n vertex : Nat) :
    (CheckedGaugePath.identity n vertex).closed := by
  rfl

theorem checkedGaugePath_concat_closed_of_cycle
    (left right : CheckedGaugePath n)
    (hforward : left.target = right.source)
    (hback : right.target = left.source) :
    (left.concat right hforward).closed := by
  unfold CheckedGaugePath.closed
  simpa [CheckedGaugePath.concat] using hback.symm

theorem checkedGaugePath_closed_gaugeInvariant
    (path : CheckedGaugePath n) (gauge : Nat → ZMod n)
    (hclosed : path.closed) :
    path.gaugeShiftedHolonomy gauge = path.holonomy := by
  unfold CheckedGaugePath.gaugeShiftedHolonomy CheckedGaugePath.closed at *
  rw [hclosed]
  simp

theorem checkedGaugePath_concat_cycle_gaugeInvariant
    (left right : CheckedGaugePath n)
    (hforward : left.target = right.source)
    (hback : right.target = left.source)
    (gauge : Nat → ZMod n) :
    (left.concat right hforward).gaugeShiftedHolonomy gauge =
      (left.concat right hforward).holonomy := by
  apply checkedGaugePath_closed_gaugeInvariant
  exact checkedGaugePath_concat_closed_of_cycle left right hforward hback

theorem gaugeLinkPath_reverse_phases (path : GaugeLinkPath n) :
    path.reverse.phases = reversePhases path.phases := by
  unfold GaugeLinkPath.reverse GaugeLinkPath.phases reversePhases GaugeLink.reverse
  simp [List.map_map]

theorem gaugeLinkPathHolonomy_reverse (path : GaugeLinkPath n) :
    path.reverse.holonomy = -path.holonomy := by
  unfold GaugeLinkPath.holonomy
  rw [gaugeLinkPath_reverse_phases]
  exact pathHolonomy_reverse path.phases

theorem gaugeLinkPath_reverse_reverse (path : GaugeLinkPath n) :
    path.reverse.reverse = path := by
  cases path with
  | mk links =>
      simp [GaugeLinkPath.reverse, List.map_map, gaugeLink_reverse_reverse_list]

theorem gaugeLinkPath_reverse_concat (left right : GaugeLinkPath n) :
    (left.concat right).reverse = right.reverse.concat left.reverse := by
  cases left with
  | mk leftLinks =>
      cases right with
      | mk rightLinks =>
          simp [GaugeLinkPath.reverse, GaugeLinkPath.concat, List.map_append]

theorem gaugeLinkPath_singleton_composable (link : GaugeLink n) :
    (GaugeLinkPath.mk [link]).composable := by
  simp [GaugeLinkPath.composable, linksComposable]

theorem gaugeLinkPath_empty_composable (n : Nat) :
    (GaugeLinkPath.empty n).composable := by
  simp [GaugeLinkPath.empty, GaugeLinkPath.composable, linksComposable]

theorem gaugeLinkPath_concat_empty_left_composable (path : GaugeLinkPath n) :
    ((GaugeLinkPath.empty n).concat path).composable ↔ path.composable := by
  cases path with
  | mk links =>
      simp [GaugeLinkPath.empty, GaugeLinkPath.concat, GaugeLinkPath.composable]

theorem gaugeLinkPath_concat_empty_right_composable (path : GaugeLinkPath n) :
    (path.concat (GaugeLinkPath.empty n)).composable ↔ path.composable := by
  cases path with
  | mk links =>
      simp [GaugeLinkPath.empty, GaugeLinkPath.concat, GaugeLinkPath.composable]

theorem gaugeLinkPath_pair_composable_iff (first second : GaugeLink n) :
    (GaugeLinkPath.mk [first, second]).composable ↔ first.target = second.source := by
  simp [GaugeLinkPath.composable, linksComposable]

theorem gaugeLinkPath_concat_singletons_composable_iff (first second : GaugeLink n) :
    ((GaugeLinkPath.mk [first]).concat (GaugeLinkPath.mk [second])).composable ↔
      first.target = second.source := by
  simp [GaugeLinkPath.concat, GaugeLinkPath.composable, linksComposable]

theorem gaugeLinkPath_triple_composable_iff
    (first second third : GaugeLink n) :
    (GaugeLinkPath.mk [first, second, third]).composable ↔
      first.target = second.source ∧ second.target = third.source := by
  simp [GaugeLinkPath.composable, linksComposable]

theorem gaugeLinkPath_quad_composable_iff
    (first second third fourth : GaugeLink n) :
    (GaugeLinkPath.mk [first, second, third, fourth]).composable ↔
      first.target = second.source ∧
        second.target = third.source ∧
        third.target = fourth.source := by
  simp [GaugeLinkPath.composable, linksComposable]

theorem gaugeTransform_pathHolonomy_endpoints (path : GaugePath n) :
    gaugeTransformHolonomy path =
      pathHolonomy path.phases + path.sourceGauge - path.targetGauge := by
  rfl

theorem closedWilsonLoop_gaugeInvariant (path : GaugePath n)
    (h : path.sourceGauge = path.targetGauge) :
    gaugeTransformHolonomy path = pathHolonomy path.phases := by
  unfold gaugeTransformHolonomy
  rw [h]
  simp

theorem plaquetteHolonomy_gaugeInvariant (p : Plaquette n) :
    gaugeTransformHolonomy p.path = pathHolonomy p.phases := by
  apply closedWilsonLoop_gaugeInvariant
  rfl

end Circle.Physics
