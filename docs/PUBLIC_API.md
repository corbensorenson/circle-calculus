# Public API Surfaces

This file records the intended stable entry points for users who treat Circle
Calculus as a library.

## Stability Rule

Stable APIs are allowed to grow, but they should not be removed or renamed
without a version bump and migration note. Research modules may change faster.

Stable:

- Python: `circle_math.core`, `circle_math.contracts`, `circle_math.ai_contracts`
- Lean: `Circle.Core`, `Circle.Applications.Public`, `Circle.Contracts`
- Rust: the `circle-prime` crate root and documented binaries

Research/internal:

- large generated Lean certificate modules except through `Circle.Contracts`;
- repository maintenance scripts under `scripts/`;
- sidecar benchmark scripts and raw result fixtures;
- private-transfer compatibility lanes.

## Python Core

Use `circle_math.core` for finite cyclic mathematics:

```python
from circle_math.core import finite_orbit, finite_period, is_full_coil

assert finite_orbit(12, 5)[0:4] == [0, 5, 10, 3]
assert finite_period(12, 5) == 12
assert is_full_coil(12, 5) is True
```

## Python Contracts

Use `circle_math.ai_contracts` to build public contract fixtures and receipts:

```python
from circle_math.ai_contracts import build_contract_pack, build_rope_receipt

pack = build_contract_pack()
receipt = build_rope_receipt(context=4096, pack=pack)
assert receipt["decision"]["all_theorem_ids_proved"] is True
```

Use `circle_math.contracts` to consume an already exported pack:

```python
from circle_math.contracts import load_contract_pack, require_ready_contract

pack = load_contract_pack("site/data/generated/circle_ai_contract_pack.json")
contract = require_ready_contract(pack, "sparse_attention_coverage")
print(contract["id"])
```

## Lean Imports

Finite cyclic mathematics:

```lean
import Circle.Core
```

Application facts without huge generated certificate imports:

```lean
import Circle.Applications.Public
```

All public proof-carrying application contracts, including generated RoPE
certificate facts:

```lean
import Circle.Contracts
```

## Rust

The Rust workspace package stays focused on prime and horizon utilities:

```bash
cargo run -p circle-prime -- --help
cargo run -p circle-prime --bin circle-prime-count -- --help
cargo doc -p circle-prime --no-deps
```

Keep new Rust API additions in that scope unless the project deliberately
creates a separate crate.
