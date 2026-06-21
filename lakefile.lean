import Lake
open Lake DSL

package circle_calculus where
  version := v!"0.1.0"
  description := "Proof-carrying finite cyclic mathematics, Circle Calculus living-book sources, and reusable Lean theorem surfaces."
  keywords := #[
    "math",
    "formalization",
    "cyclic-groups",
    "modular-arithmetic",
    "software-verification",
    "ai-contracts"
  ]
  homepage := "https://corbensorenson.github.io/circle-calculus/"
  license := "MIT"
  licenseFiles := #["LICENSE"]
  readmeFile := "README.md"
  reservoir := true

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"

@[default_target]
lean_lib Circle
