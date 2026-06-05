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

theorem boundaryBoundaryInterval_zero (interval : DirectedInterval) :
    pointBoundary (intervalBoundary interval) = 0 := by
  rfl

theorem intervalBoundary_reverse (interval : DirectedInterval) :
    intervalBoundary (reverseInterval interval) = -intervalBoundary interval := by
  cases interval
  simp [intervalBoundary, reverseInterval]
  omega

end Circle.Phase2
