namespace Circle.Common

structure CellCounts where
  counts : List Nat
deriving DecidableEq, Repr

def eulerCharacteristic : List Nat -> Int
  | [] => 0
  | count :: rest => (count : Int) - eulerCharacteristic rest

def suspensionTail (previous : Nat) : List Nat -> List Nat
  | [] => [2 * previous]
  | count :: rest => (count + 2 * previous) :: suspensionTail count rest

def suspensionCounts : List Nat -> List Nat
  | [] => [2]
  | count :: rest => (count + 2) :: suspensionTail count rest

end Circle.Common
