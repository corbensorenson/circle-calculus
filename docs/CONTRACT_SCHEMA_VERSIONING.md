# Contract Schema And Versioning Policy

Circle contract artifacts are public protocols, not loose JSON dumps.

## Current Public Schema

The public Circle AI contract pack uses:

```text
circle_calculus.ai_contract_pack.v0
```

The parameterized runner surface currently publishes:

```text
circle_calculus.ai_contract_request.v0
circle_calculus.ai_contract_request_validation.v0
circle_calculus.ai_contract_receipt.v0
circle_calculus.ai_contract_compact_receipt.v0
circle_calculus.ai_contract_runner_check.v0
```

The compact receipt is a downstream view over a validated full receipt. It must
carry the full receipt fingerprint and non-claims; it is not the archival audit
object for reproducing a contract run.

The generated pack and schemas are written under:

```text
site/data/generated/
```

Regenerate and validate them with:

```bash
make circle-ai-contracts
make circle-ai-contracts-check
make circle-ai-contracts-ready
```

## Versioning Rule

Use additive changes within `v0` when consumers can ignore the new field:

- adding optional metadata;
- adding new contract kinds;
- adding recommendation records;
- adding source links or documentation links;
- adding stronger proof-status summaries while preserving old keys.

Start a new schema id when consumers must change code:

- renaming required keys;
- changing value types for required keys;
- removing fields;
- changing readiness semantics;
- changing fingerprint semantics;
- changing claim-boundary or theorem-status interpretation.

## Consumer Compatibility Rule

Consumers should gate on:

```python
contract["consumer_check"]["ready_for_downstream_fixture_use"] is True
contract["proof_status"]["all_theorem_ids_resolved"] is True
contract["proof_status"]["all_theorem_ids_proved"] is True
```

Consumers should log:

- pack schema id;
- pack content fingerprint;
- contract id;
- contract kind;
- contract content fingerprint;
- theorem ids;
- not-claimed boundary.

## Non-Claim Boundary

A contract receipt proves only the finite structural field it names. It does not
prove model quality, speed, memory use, context length, deployment safety,
business value, physics, or universal compression.

## Release Gate

Before publishing a release that changes contract artifacts, run:

```bash
make circle-ai-contracts
make circle-ai-contracts-check
make circle-ai-contracts-ready
python scripts/example_validate_circle_ai_contract_pack_schema.py --summary
python scripts/check_downstream_ci_acceptance_example.py --summary
```
