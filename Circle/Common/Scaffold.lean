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

theorem suspensionTailEuler (previous : Nat) (counts : List Nat) :
    eulerCharacteristic (suspensionTail previous counts) =
      (2 * previous : Int) - eulerCharacteristic counts := by
  induction counts generalizing previous with
  | nil =>
      simp [suspensionTail, eulerCharacteristic]
  | cons count rest ih =>
      simp [suspensionTail, eulerCharacteristic, ih]
      omega

theorem suspensionEuler (counts : List Nat) :
    eulerCharacteristic (suspensionCounts counts) =
      2 - eulerCharacteristic counts := by
  cases counts with
  | nil =>
      simp [suspensionCounts, eulerCharacteristic]
  | cons count rest =>
      simp [suspensionCounts, eulerCharacteristic, suspensionTailEuler]
      omega

end Circle.Common
