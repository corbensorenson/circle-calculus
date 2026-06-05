namespace Circle

/-- A lifted node records full windings plus a residue. -/
structure LiftedNode where
  modulus : Nat
  winding : Nat
  residue : Nat
deriving Repr, DecidableEq

/-- Interpret a lifted node as an ordinary natural count. -/
def LiftedNode.value (x : LiftedNode) : Nat :=
  x.winding * x.modulus + x.residue

/-- The winding component of the canonical lifted representation of a natural count. -/
def liftWinding (modulus value : Nat) : Nat :=
  value / modulus

/-- The residue component of the canonical lifted representation of a natural count. -/
def liftResidue (modulus value : Nat) : Nat :=
  value % modulus

theorem lift_decomposition (modulus value : Nat) :
    modulus * liftWinding modulus value + liftResidue modulus value = value := by
  exact Nat.div_add_mod value modulus

theorem lift_residue_lt {modulus value : Nat} (hmod : modulus ≠ 0) :
    liftResidue modulus value < modulus := by
  exact Nat.mod_lt value (Nat.pos_of_ne_zero hmod)

theorem lift_exists {modulus value : Nat} (hmod : modulus ≠ 0) :
    liftWinding modulus value * modulus + liftResidue modulus value = value ∧
      liftResidue modulus value < modulus := by
  constructor
  · rw [Nat.mul_comm]
    exact lift_decomposition modulus value
  · exact lift_residue_lt hmod

theorem lift_unique {modulus value winding residue : Nat} (hmod : modulus ≠ 0)
    (hresidue : residue < modulus) (hvalue : winding * modulus + residue = value) :
    winding = liftWinding modulus value ∧ residue = liftResidue modulus value := by
  have hq : value / modulus = winding := by
    rw [← hvalue, Nat.mul_comm winding modulus, Nat.mul_add_div (Nat.pos_of_ne_zero hmod),
      Nat.div_eq_of_lt hresidue, Nat.add_zero]
  have hr : value % modulus = residue := by
    rw [← hvalue]
    simp [Nat.mod_eq_of_lt hresidue]
  exact ⟨hq.symm, hr.symm⟩

/-- Carry produced when successor moves past the last residue address. -/
def liftSuccCarry (modulus value : Nat) : Nat :=
  (liftResidue modulus value + 1) / modulus

/-- Winding component after one successor step. -/
def liftSuccWinding (modulus value : Nat) : Nat :=
  liftWinding modulus value + liftSuccCarry modulus value

/-- Residue component after one successor step. -/
def liftSuccResidue (modulus value : Nat) : Nat :=
  (liftResidue modulus value + 1) % modulus

theorem lift_successor_decomposition {modulus value : Nat} (hmod : modulus ≠ 0) :
    liftSuccWinding modulus value * modulus + liftSuccResidue modulus value = value + 1 ∧
      liftSuccResidue modulus value < modulus := by
  have hpos : 0 < modulus := Nat.pos_of_ne_zero hmod
  have hdec : liftWinding modulus value * modulus + liftResidue modulus value = value := by
    rw [Nat.mul_comm]
    exact lift_decomposition modulus value
  have hstep : liftSuccCarry modulus value * modulus + liftSuccResidue modulus value =
      liftResidue modulus value + 1 := by
    unfold liftSuccCarry liftSuccResidue
    rw [Nat.mul_comm]
    exact Nat.div_add_mod (liftResidue modulus value + 1) modulus
  have hreslt : liftSuccResidue modulus value < modulus := by
    unfold liftSuccResidue
    exact Nat.mod_lt _ hpos
  constructor
  · unfold liftSuccWinding
    calc
      (liftWinding modulus value + liftSuccCarry modulus value) * modulus +
          liftSuccResidue modulus value
          = liftWinding modulus value * modulus +
              (liftSuccCarry modulus value * modulus + liftSuccResidue modulus value) := by
              rw [Nat.add_mul, Nat.add_assoc]
      _ = liftWinding modulus value * modulus + (liftResidue modulus value + 1) := by
              rw [hstep]
      _ = (liftWinding modulus value * modulus + liftResidue modulus value) + 1 := by
              rw [Nat.add_assoc]
      _ = value + 1 := by
              rw [hdec]
  · exact hreslt

/-- Carry produced when concatenating two lifted paths. -/
def liftAddCarry (modulus left right : Nat) : Nat :=
  (liftResidue modulus left + liftResidue modulus right) / modulus

/-- Winding component after concatenating two lifted paths. -/
def liftAddWinding (modulus left right : Nat) : Nat :=
  liftWinding modulus left + liftWinding modulus right + liftAddCarry modulus left right

/-- Residue component after concatenating two lifted paths. -/
def liftAddResidue (modulus left right : Nat) : Nat :=
  (liftResidue modulus left + liftResidue modulus right) % modulus

theorem lift_add_decomposition {modulus left right : Nat} (hmod : modulus ≠ 0) :
    liftAddWinding modulus left right * modulus + liftAddResidue modulus left right =
        left + right ∧
      liftAddResidue modulus left right < modulus := by
  have hpos : 0 < modulus := Nat.pos_of_ne_zero hmod
  have hleft : liftWinding modulus left * modulus + liftResidue modulus left = left := by
    rw [Nat.mul_comm]
    exact lift_decomposition modulus left
  have hright : liftWinding modulus right * modulus + liftResidue modulus right = right := by
    rw [Nat.mul_comm]
    exact lift_decomposition modulus right
  have hres : liftAddCarry modulus left right * modulus + liftAddResidue modulus left right =
      liftResidue modulus left + liftResidue modulus right := by
    unfold liftAddCarry liftAddResidue
    rw [Nat.mul_comm]
    exact Nat.div_add_mod (liftResidue modulus left + liftResidue modulus right) modulus
  have hreslt : liftAddResidue modulus left right < modulus := by
    unfold liftAddResidue
    exact Nat.mod_lt _ hpos
  constructor
  · unfold liftAddWinding
    rw [Nat.add_mul, Nat.add_mul]
    omega
  · exact hreslt

theorem lift_add_zero_right {modulus value : Nat} (_hmod : modulus ≠ 0) :
    liftAddWinding modulus value 0 = liftWinding modulus value ∧
      liftAddResidue modulus value 0 = liftResidue modulus value := by
  have hzero : liftWinding modulus 0 = 0 := by
    unfold liftWinding
    simp
  constructor
  · unfold liftAddWinding liftAddCarry
    simp [liftResidue, hzero]
  · unfold liftAddResidue
    simp [liftResidue]

theorem lift_add_zero_left {modulus value : Nat} (_hmod : modulus ≠ 0) :
    liftAddWinding modulus 0 value = liftWinding modulus value ∧
      liftAddResidue modulus 0 value = liftResidue modulus value := by
  have hzero : liftWinding modulus 0 = 0 := by
    unfold liftWinding
    simp
  constructor
  · unfold liftAddWinding liftAddCarry
    simp [liftResidue, hzero]
  · unfold liftAddResidue
    simp [liftResidue]

theorem lift_add_assoc_value {modulus left middle right : Nat} (hmod : modulus ≠ 0) :
    liftAddWinding modulus (left + middle) right * modulus +
        liftAddResidue modulus (left + middle) right =
      liftAddWinding modulus left (middle + right) * modulus +
        liftAddResidue modulus left (middle + right) := by
  have hleft := (lift_add_decomposition (modulus := modulus) (left := left + middle)
    (right := right) hmod).1
  have hright := (lift_add_decomposition (modulus := modulus) (left := left)
    (right := middle + right) hmod).1
  rw [hleft, hright]
  omega

/-- One successor step on an arbitrary lifted `(winding, residue)` state. -/
def liftSuccPair (modulus : Nat) (state : Nat × Nat) : Nat × Nat :=
  (state.1 + ((state.2 + 1) / modulus), (state.2 + 1) % modulus)

/-- Iterate the lifted successor transition. -/
def liftIterSuccPair (modulus steps : Nat) (state : Nat × Nat) : Nat × Nat :=
  match steps with
  | 0 => state
  | Nat.succ previous => liftSuccPair modulus (liftIterSuccPair modulus previous state)

theorem lift_succ_pair_decomposition {modulus winding residue value : Nat}
    (hmod : modulus ≠ 0) (hvalue : winding * modulus + residue = value) :
    (liftSuccPair modulus (winding, residue)).1 * modulus +
        (liftSuccPair modulus (winding, residue)).2 = value + 1 ∧
      (liftSuccPair modulus (winding, residue)).2 < modulus := by
  have hpos : 0 < modulus := Nat.pos_of_ne_zero hmod
  have hstep : ((residue + 1) / modulus) * modulus + ((residue + 1) % modulus) =
      residue + 1 := by
    rw [Nat.mul_comm]
    exact Nat.div_add_mod (residue + 1) modulus
  constructor
  · simp [liftSuccPair]
    rw [Nat.add_mul, Nat.add_assoc]
    omega
  · simp [liftSuccPair]
    exact Nat.mod_lt _ hpos

theorem lift_iter_successor_decomposition {modulus winding residue value steps : Nat}
    (hmod : modulus ≠ 0) (hresidue : residue < modulus)
    (hvalue : winding * modulus + residue = value) :
    (liftIterSuccPair modulus steps (winding, residue)).1 * modulus +
        (liftIterSuccPair modulus steps (winding, residue)).2 = value + steps ∧
      (liftIterSuccPair modulus steps (winding, residue)).2 < modulus := by
  induction steps with
  | zero =>
      simp [liftIterSuccPair, hvalue, hresidue]
  | succ previous ih =>
      dsimp [liftIterSuccPair]
      have hsucc := lift_succ_pair_decomposition (modulus := modulus)
        (winding := (liftIterSuccPair modulus previous (winding, residue)).1)
        (residue := (liftIterSuccPair modulus previous (winding, residue)).2)
        (value := value + previous) hmod ih.1
      simpa [Nat.add_assoc] using hsucc

end Circle
