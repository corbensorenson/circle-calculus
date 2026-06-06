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

def iteratedSuspensionCounts : Nat -> List Nat -> List Nat
  | 0, counts => counts
  | steps + 1, counts => suspensionCounts (iteratedSuspensionCounts steps counts)

def alternatingSuspensionEuler : Nat -> Int -> Int
  | 0, chi => chi
  | steps + 1, chi => 2 - alternatingSuspensionEuler steps chi

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

theorem iteratedSuspensionEuler (steps : Nat) (counts : List Nat) :
    eulerCharacteristic (iteratedSuspensionCounts steps counts) =
      alternatingSuspensionEuler steps (eulerCharacteristic counts) := by
  induction steps with
  | zero =>
      rfl
  | succ steps ih =>
      simp [iteratedSuspensionCounts, alternatingSuspensionEuler, suspensionEuler, ih]

theorem alternatingSuspensionEuler_two_step (steps : Nat) (chi : Int) :
    alternatingSuspensionEuler (steps + 2) chi =
      alternatingSuspensionEuler steps chi := by
  simp [alternatingSuspensionEuler]
  omega

theorem iteratedSuspensionEuler_two_step (steps : Nat) (counts : List Nat) :
    eulerCharacteristic (iteratedSuspensionCounts (steps + 2) counts) =
      eulerCharacteristic (iteratedSuspensionCounts steps counts) := by
  rw [iteratedSuspensionEuler, iteratedSuspensionEuler]
  exact alternatingSuspensionEuler_two_step steps (eulerCharacteristic counts)

end Circle.Common
