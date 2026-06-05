namespace Circle.Common

structure CellCounts where
  counts : List Nat
deriving DecidableEq, Repr

def plannedEulerCharacteristicName : String :=
  "COMMON-T0001"

def plannedSuspensionName : String :=
  "COMMON-T0002"

end Circle.Common

