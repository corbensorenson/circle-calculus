import Mathlib.Data.Nat.Prime.Basic

namespace Circle.Applications

/-!
Finite TreeLLM bookkeeping from the Drive notes.

This module ports only arithmetic contracts that are stable enough to prove:
root counts, token-layout byte sums, semantic-anchor counts, tier counts, and
bounded speculative-hop ranges.  Architecture-quality and performance claims
remain benchmark or design-backlog items.
-/

/-- The TreeLLM specs repeatedly use thirteen universal root questions. -/
def treeLLMRootQuestionCount : Nat := 13

/-- Each root path in the 76/80-byte token formats is declared as 24 bits. -/
def treeLLMPathBitsPerRoot : Nat := 24

/-- Byte width used by the binary token layout arithmetic. -/
def treeLLMBitsPerByte : Nat := 8

/-- Total path-id bits across the thirteen roots. -/
def treeLLMPathIdBits : Nat :=
  treeLLMRootQuestionCount * treeLLMPathBitsPerRoot

/-- Total path-id bytes when the 312 path bits are byte-aligned. -/
def treeLLMPathIdBytes : Nat :=
  treeLLMPathIdBits / treeLLMBitsPerByte

theorem treeLLMRootQuestionCount_prime :
    Nat.Prime treeLLMRootQuestionCount := by
  native_decide

theorem treeLLMPathIdBits_eq :
    treeLLMPathIdBits = 312 := by
  native_decide

theorem treeLLMPathIdBytes_eq :
    treeLLMPathIdBytes = 39 := by
  native_decide

theorem treeLLMPathIdBits_byte_aligned :
    treeLLMPathIdBytes * treeLLMBitsPerByte = treeLLMPathIdBits := by
  native_decide

/-- One float8 root probability per universal root. -/
def treeLLMRootProbabilityBytes : Nat :=
  treeLLMRootQuestionCount

/-- Residual fingerprint size shared by the 76-byte and 80-byte layouts. -/
def treeLLMResidualFingerprintBytes : Nat := 16

/-- BLAKE3 suffix size in the 76-byte token format. -/
def treeLLMBlakeHashSuffixBytes : Nat := 8

/-- Covariance/PCA hash size in the 80-byte token format. -/
def treeLLMCovarianceHashBytes : Nat := 4

/-- Post-quantum hash size in the 80-byte token format. -/
def treeLLMKyberHashBytes : Nat := 8

/-- The TreeLLM 76-byte token from the "Absolute Final Specification" tab. -/
def treeLLM76TokenBytes : Nat :=
  treeLLMPathIdBytes +
    treeLLMRootProbabilityBytes +
    treeLLMBlakeHashSuffixBytes +
    treeLLMResidualFingerprintBytes

theorem treeLLM76TokenBytes_eq :
    treeLLM76TokenBytes = 76 := by
  native_decide

/-- The TreeLLM 80-byte token variant with covariance and Kyber hash fields. -/
def treeLLM80TokenBytes : Nat :=
  treeLLMPathIdBytes +
    treeLLMRootProbabilityBytes +
    treeLLMCovarianceHashBytes +
    treeLLMKyberHashBytes +
    treeLLMResidualFingerprintBytes

theorem treeLLM80TokenBytes_eq :
    treeLLM80TokenBytes = 80 := by
  native_decide

/-! ### Earlier and v8 32-byte token layouts -/

def treeLLMInitialTokenBytes : Nat := 32
def treeLLMInitialPathIdBits : Nat := 14
def treeLLMInitialResidualDims : Nat := 20

/-- Initial white-paper payload bits: 14 path bits plus 20 int8 residuals. -/
def treeLLMInitialPayloadBits : Nat :=
  treeLLMInitialPathIdBits + treeLLMInitialResidualDims * treeLLMBitsPerByte

/-- Bit capacity of the initial 32-byte token. -/
def treeLLMInitialTokenBits : Nat :=
  treeLLMInitialTokenBytes * treeLLMBitsPerByte

theorem treeLLMInitialPayloadBits_eq :
    treeLLMInitialPayloadBits = 174 := by
  native_decide

theorem treeLLMInitialPayloadFits32Bytes :
    treeLLMInitialPayloadBits ≤ treeLLMInitialTokenBits := by
  native_decide

def treeLLMV8GraphCoordinateBytes : Nat := 16
def treeLLMV8TypeHeaderBytes : Nat := 4
def treeLLMV8ResidualFingerprintBytes : Nat := 12

/-- TreeLLM v8's 32-byte semantic vector field sum. -/
def treeLLMV8SemanticVectorBytes : Nat :=
  treeLLMV8GraphCoordinateBytes +
    treeLLMV8TypeHeaderBytes +
    treeLLMV8ResidualFingerprintBytes

theorem treeLLMV8SemanticVectorBytes_eq :
    treeLLMV8SemanticVectorBytes = 32 := by
  native_decide

/-! ### Anchor, tier, and traversal counts -/

def treeLLMTotalAnchorCount : Nat := 128
def treeLLMSensoryAnchorCount : Nat := 16
def treeLLMNonSensoryAnchorCount : Nat :=
  treeLLMTotalAnchorCount - treeLLMSensoryAnchorCount

theorem treeLLMNonSensoryAnchorCount_eq :
    treeLLMNonSensoryAnchorCount = 112 := by
  native_decide

theorem treeLLMSensoryAnchorCapacity_le_total :
    treeLLMSensoryAnchorCount ≤ treeLLMTotalAnchorCount := by
  native_decide

/-- TreeLLM v8's read path has global, federated, and user-overlay tiers. -/
def treeLLMDKLTierCount : Nat := 3

theorem treeLLMDKLTierCount_eq :
    treeLLMDKLTierCount = 3 := by
  rfl

/-- The speculative traversal note predicts three to five hops per step. -/
def treeLLMSpeculativeHopMin : Nat := 3

/-- The speculative traversal note predicts three to five hops per step. -/
def treeLLMSpeculativeHopMax : Nat := 5

theorem treeLLMSpeculativeHopSpan_nonempty :
    treeLLMSpeculativeHopMin ≤ treeLLMSpeculativeHopMax := by
  native_decide

end Circle.Applications
