namespace Circle.Applications

/-!
Finite AI configuration checks from Drive MLX/PyTorch artifacts.

The training logs and scripts contain useful guardrails around rotary attention
configuration.  This module keeps only shape arithmetic; it does not claim model
quality, convergence, or benchmark superiority.
-/

structure RotaryAttentionConfig where
  modelDim : Nat
  numHeads : Nat
  numKVHeads : Nat
  ropeDims : Nat
deriving DecidableEq, Repr

/-- Integer head dimension used by the local attention implementations. -/
def rotaryAttentionHeadDim (cfg : RotaryAttentionConfig) : Nat :=
  cfg.modelDim / cfg.numHeads

/--
Finite well-formedness checks matching the Drive scripts' rotary-attention
guards.  `ropeDims = 0` is allowed by the implementation as "use the full head
dimension"; nonzero values must be even and fit inside the head.
-/
def rotaryAttentionConfigWellFormed (cfg : RotaryAttentionConfig) : Prop :=
  0 < cfg.numHeads ∧
    0 < cfg.numKVHeads ∧
    cfg.modelDim % cfg.numHeads = 0 ∧
    cfg.numHeads % cfg.numKVHeads = 0 ∧
    rotaryAttentionHeadDim cfg % 2 = 0 ∧
    (cfg.ropeDims = 0 ∨
      (cfg.ropeDims ≤ rotaryAttentionHeadDim cfg ∧ cfg.ropeDims % 2 = 0))

instance rotaryAttentionConfigWellFormed_decidable (cfg : RotaryAttentionConfig) :
    Decidable (rotaryAttentionConfigWellFormed cfg) := by
  unfold rotaryAttentionConfigWellFormed
  infer_instance

/-- Concrete RoPE-enabled config found in the Drive training artifacts. -/
def mlxRotaryConfig512_8_4_16 : RotaryAttentionConfig :=
  { modelDim := 512, numHeads := 8, numKVHeads := 4, ropeDims := 16 }

/-- Concrete MLX config where `ropeDims = 0` selects the full head dimension. -/
def mlxRotaryConfig512_8_4_0 : RotaryAttentionConfig :=
  { modelDim := 512, numHeads := 8, numKVHeads := 4, ropeDims := 0 }

theorem mlxRotaryConfig512_8_4_16_wellFormed :
    rotaryAttentionConfigWellFormed mlxRotaryConfig512_8_4_16 := by
  native_decide

theorem mlxRotaryConfig512_8_4_16_headDim :
    rotaryAttentionHeadDim mlxRotaryConfig512_8_4_16 = 64 := by
  native_decide

theorem mlxRotaryConfig512_8_4_0_wellFormed :
    rotaryAttentionConfigWellFormed mlxRotaryConfig512_8_4_0 := by
  native_decide

/-- Effective rotary dimension after applying the `ropeDims = 0` default. -/
def effectiveRotaryDims (headDim ropeDims : Nat) : Nat :=
  if ropeDims = 0 then headDim else ropeDims

theorem mlxRotaryConfig512_8_4_0_effectiveFullHead :
    effectiveRotaryDims (rotaryAttentionHeadDim mlxRotaryConfig512_8_4_0)
        mlxRotaryConfig512_8_4_0.ropeDims = 64 := by
  native_decide

end Circle.Applications
