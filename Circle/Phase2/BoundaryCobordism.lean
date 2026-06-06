/-!
Phase II boundary/cobordism seed.

This module formalizes a tiny directed-interval boundary model. It proves only
the first combinatorial boundary laws needed for the paper roadmap.
-/

namespace Circle.Phase2

structure DirectedInterval where
  source : Int
  target : Int

def intervalBoundary (interval : DirectedInterval) : Int :=
  interval.target - interval.source

def pointBoundary (_chain : Int) : Int :=
  0

def reverseInterval (interval : DirectedInterval) : DirectedInterval :=
  { source := interval.target, target := interval.source }

def constantInterval (point : Int) : DirectedInterval :=
  { source := point, target := point }

def intervalBetween (source target : Int) : DirectedInterval :=
  { source := source, target := target }

theorem boundaryBoundaryInterval_zero (interval : DirectedInterval) :
    pointBoundary (intervalBoundary interval) = 0 := by
  rfl

theorem intervalBoundary_reverse (interval : DirectedInterval) :
    intervalBoundary (reverseInterval interval) = -intervalBoundary interval := by
  cases interval
  simp [intervalBoundary, reverseInterval]
  omega

theorem reverseInterval_involutive (interval : DirectedInterval) :
    reverseInterval (reverseInterval interval) = interval := by
  cases interval
  rfl

theorem intervalBoundary_constant_zero (point : Int) :
    intervalBoundary (constantInterval point) = 0 := by
  simp [intervalBoundary, constantInterval]

theorem intervalBoundary_between_add (source mid target : Int) :
    intervalBoundary (intervalBetween source target) =
      intervalBoundary (intervalBetween source mid) +
        intervalBoundary (intervalBetween mid target) := by
  simp [intervalBoundary, intervalBetween]
  omega

end Circle.Phase2
