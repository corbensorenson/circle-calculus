# Cyclic Memory Residue/Winding Certifier Quickstart

This certifier packages the finite cyclic-memory fixture as a public Circle AI
contract. It answers one narrow question:

```text
Given a memory bank of size n and an event index t,
which residue slot does t use, which earlier/later events alias that slot,
and which winding number separates those repeated residues?
```

It is useful for auditing ring-style memory, worker-state buckets, context
packet slots, and retrieval traces where slot identity alone hides provenance.

Run the default fixture:

```bash
python scripts/cyclic_memory_certify.py
```

The default text report should include:

```text
cyclic_memory_contract=READY bank_size=8 event_index=23 event_count=32 residue_slot=7 winding=2
alias_class=same_residue_events=(7, 15, 23, 31) same_residue_windings=(0, 1, 2, 3) max_alias_load=4 theorems=AIM-T0001,AIM-T0002,AIM-T0004,AIM-T0005
reconstruction=event_index=23 winding_times_bank_plus_residue=23 exact=True
consumer_check=ready=True required_fields_present=True all_theorem_ids_proved=True missing_fields=0
```

Emit JSON for downstream tools:

```bash
python scripts/cyclic_memory_certify.py --format json
python scripts/cyclic_memory_certify.py --json-out /tmp/cyclic_memory_contract.json
```

Try a smaller custom trace:

```bash
python scripts/cyclic_memory_certify.py --bank-size 5 --event-index 12 --event-count 20
```

Expected evidence fields:

| Field | Meaning |
| --- | --- |
| `bank_size` | Number of cyclic memory slots. |
| `event_index` | Event being decomposed. |
| `event_count` | Size of the finite trace used for alias counting. |
| `residue_slot` | `event_index mod bank_size`. |
| `winding` | Number of full bank passes before the residue. |
| `same_residue_events` | Events in the declared trace that share the slot. |
| `same_residue_windings` | Winding values attached to those aliases. |
| `max_alias_load` | Maximum number of events assigned to any slot. |

The theorem cluster is:

| Theorem id | Role |
| --- | --- |
| `AIM-T0001` | Memory slot is a finite residue. |
| `AIM-T0002` | Adding one full bank pass preserves the memory slot. |
| `AIM-T0004` | Adding any whole number of full bank passes preserves the memory slot. |
| `AIM-T0005` | Normalizing a memory slot twice is the same as normalizing it once. |

The generated contract pack stores the same certificate under
`cyclic_memory_residue_winding`:

```bash
python scripts/export_circle_ai_contracts.py
python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding --digest \
  --field same_residue_events \
  --field same_residue_windings \
  --field max_alias_load
python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding --digest \
  --field max_alias_load \
  --include-recommendations
```

Planner recommendations:

```text
MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE
MEMORY-AUDIT-FINITE-ALIAS-LOAD
```

The first record tells a downstream tool to preserve winding/provenance beside
same-slot aliases. The second records finite slot-load pressure for the
declared trace. Both are fixture-level audit records, not retrieval, memory
capacity, throughput, allocation-policy, or model-quality claims.

Non-claims:

- This is finite indexing and provenance bookkeeping, not a memory-scaling
  theorem.
- It does not prove retrieval quality, model quality, throughput, deployment
  safety, ASI, or usefulness for any trained model.
- The Python report is an executable certificate surface; the formal source is
  still the Lean theorem ids resolved through the manifest.
