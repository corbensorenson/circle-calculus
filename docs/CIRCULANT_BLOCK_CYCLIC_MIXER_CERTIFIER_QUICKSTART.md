# Circulant/Block-Cyclic Mixer Certifier Quickstart

This certifier packages the finite structured-mixer fixture as a public Circle
AI contract. It answers two narrow questions:

```text
Does the circulant convolution path match its dense circulant-matrix reference?
What parameter and load-accounting fields does the block-cyclic adapter fixture expose?
```

It is useful for auditing circular convolution layers, CoilLinear-style
experiments, block-cyclic adapter sharing, and route/ranker mixer prototypes
before treating them as model-quality improvements.

Run the default fixture:

```bash
python scripts/circulant_block_cyclic_mixer_certify.py
```

The default text report should include:

```text
circulant_block_cyclic_mixer_contract=READY period=8 channel_count=128 block_size=8
circulant_parity=output_parity=True max_abs_dense_delta=0 circulant_output=(5, -2, -8, 9, -1, 6, -1, -8) dense_output=(5, -2, -8, 9, -1, 6, -1, -8) theorems=AIT-T0006,AIT-T0007,AIT-T0008,AIT-T0009
circulant_parameters=circulant_parameters=8 dense_parameters=64 circulant_parameter_ratio=0.125
block_cyclic_accounting=dense_adapter_parameters=2048 lora_parameters=576 block_cyclic_parameters=128 block_to_dense_ratio=0.0625 block_loads=(16, 16, 16, 16, 16, 16, 16, 16) theorems=AIRA-T0001,AIRA-T0002,AIRA-T0004
consumer_check=ready=True required_fields_present=True all_theorem_ids_proved=True missing_fields=0
```

Emit JSON for downstream tools:

```bash
python scripts/circulant_block_cyclic_mixer_certify.py --format json
python scripts/circulant_block_cyclic_mixer_certify.py --json-out /tmp/mixer_contract.json
```

Try a smaller custom fixture:

```bash
python scripts/circulant_block_cyclic_mixer_certify.py \
  --period 4 \
  --channel-count 16 \
  --block-size 4
```

Expected evidence fields:

| Field | Meaning |
| --- | --- |
| `period` | Circulant mixer period. |
| `input_values` | Deterministic input vector for the circulant fixture. |
| `kernel_values` | Deterministic circular convolution kernel. |
| `circulant_output` | Output of the circular convolution path. |
| `dense_output` | Output of the dense circulant matrix reference. |
| `max_abs_dense_delta` | Maximum absolute parity delta; `0` means exact fixture parity. |
| `circulant_parameters` | Number of circulant parameters. |
| `dense_parameters` | Number of dense matrix parameters for the same period. |
| `circulant_parameter_ratio` | `circulant_parameters / dense_parameters`. |
| `dense_adapter_parameters` | Dense adapter parameter-count fixture. |
| `lora_parameters` | LoRA-style parameter-count fixture. |
| `block_cyclic_parameters` | Block-cyclic adapter parameter-count fixture. |
| `block_to_dense_ratio` | `block_cyclic_parameters / dense_adapter_parameters`. |
| `block_loads` | Channel-load counts per shared block. |

The theorem cluster is:

| Theorem id | Role |
| --- | --- |
| `AIT-T0006` | Circulant mixer shift/equivariance spine. |
| `AIT-T0007` | Circulant dense-reference parity spine. |
| `AIT-T0008` | Circulant parameter-count accounting. |
| `AIT-T0009` | Wrong-structure/control fixture boundary. |
| `AIRA-T0001` | Adapter/block-cyclic parameter accounting. |
| `AIRA-T0002` | Block load/residue bookkeeping. |
| `AIRA-T0004` | Block-cyclic contract fixture linkage. |

The generated contract pack stores the same certificate under
`circulant_block_cyclic_mixer`:

```bash
python scripts/export_circle_ai_contracts.py
python scripts/circle_ai_contract_ready.py --kind circulant_block_cyclic_mixer --digest \
  --field max_abs_dense_delta \
  --field circulant_parameters \
  --field dense_parameters \
  --field block_cyclic_parameters \
  --field block_to_dense_ratio \
  --include-recommendations
```

The planner recommendations are:

- `MIXER-AUDIT-CIRCULANT-DENSE-PARITY`: audit the deterministic circulant path against its dense reference and parameter count.
- `MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET`: audit the block-cyclic adapter fixture's parameter budget and block loads.

These records are finite fixture/accounting records. They do not prove speed, memory savings, hardware efficiency, training stability, LoRA replacement quality, or model quality.

Non-claims:

- Exact dense parity is for the deterministic fixture only.
- Parameter-count fields are accounting facts, not speed, memory, quality,
  training-stability, or hardware-efficiency results.
- This does not prove model quality, transfer, context-length improvement,
  deployment safety, or ASI.
- The Python report is an executable certificate surface; the formal source is
  still the Lean theorem ids resolved through the manifest.
