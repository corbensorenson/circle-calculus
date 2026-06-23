# Circle AI ML Engineer Quickstart

This is the shortest path for using the Circle Calculus AI lane without reading
Lean first. It gives you one intuition demo and four proof-carrying finite
contracts.

The goal is not to claim better models. The goal is to make finite structure in
AI systems checkable:

```text
phase feature -> position distinguishability -> cache freshness -> sparse lag coverage -> recurrence schedule accounting
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Lean is only needed when you want to rebuild the formal proof source with
`lake build`. The commands below run from Python.

## 1. Run The Phase Probe

```bash
python scripts/circle_phase_probe_demo.py --backend numpy
```

Expected summary:

```text
circle_phase_probe=READY period=8 backend=numpy train=32 test=16
baseline=raw_position_linear train_accuracy=0.500000 test_accuracy=0.500000
phase=circle_sin_cos_linear train_accuracy=1.000000 test_accuracy=1.000000
non_claimed=This synthetic probe does not prove real model quality, speed, memory, context-length, or reasoning gains.
```

Interpretation: for a synthetic periodic label, circle phase features make the
rule linearly readable while a raw-position ramp does not. This is an intuition
demo, not a proof certificate and not a model benchmark.

## 2. Run RoPE Position Distinguishability

```bash
python scripts/circle_ai_certify.py rope \
  --head-dim 128 \
  --base 10000 \
  --context 131072 \
  --requested-margin 1/328459
```

Expected summary shape:

```text
circle_ai_contract_receipt=proved kind=rope_position_distinguishability ... request_passed=True
proof_status=theorems=55 resolved=True proved=True unresolved=0 unproved=0
decision=verdict=passed assurance=mixed_theorem_and_computation claim_status=proved request_passed=True
rope_d19_request=status=proved theorem_backed=True margin=1/328459 context=131072 ...
rope_d19_bank_bridge=applies=True theorem_backed=True ...
```

Interpretation: this is a theorem-linked D19 first-channel standard-RoPE margin
frontier plus a conditional bank bridge for the stated request. It does not
prove all-channel separation for every RoPE configuration, useful context
length, perplexity, speed, memory, training stability, or deployment behavior.

## 3. Run KV-Cache Ring-Buffer Freshness

```bash
python scripts/circle_ai_certify.py kv-cache \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31 \
  --sink-size 4
```

Expected summary shape:

```text
circle_ai_contract_receipt=proved kind=kv_cache_ring_buffer ... request_passed=True
proof_status=theorems=54 resolved=True proved=True unresolved=0 unproved=0
decision=verdict=passed assurance=theorem_backed claim_status=proved request_passed=True
kv_cache_request=pass=True stale_count=0 first_stale_token=None
kv_cache_sink_window=sink_size=4 token_count=20 ... exact_policy=True tokens_distinct=True ...
```

Interpretation: this proves finite ring-buffer slot, retained-window,
modeled-read, and sink-plus-rolling-window request facts for the declared
fixture. It does not prove paging quality, throughput, memory savings,
retrieval quality, implementation correctness, deployment safety, or model
quality.

## 4. Run Sparse-Attention Coverage

```bash
python scripts/circle_ai_certify.py sparse-attention \
  --context 120 \
  --strides 7,13 \
  --path-length 3 \
  --local-window 4
```

Expected summary shape:

```text
circle_ai_contract_receipt=proved kind=sparse_attention_coverage ... request_passed=False
proof_status=theorems=132 resolved=True proved=True unresolved=0 unproved=0
decision=verdict=failed assurance=theorem_backed claim_status=proved request_passed=False
sparse_attention=coverage_complete=False covered=10 uncovered=109 first_gap=5
sparse_repair=complete_repair_window=119 ... complete_minimal=True complete_witness_lag=119
```

Interpretation: failure is useful here. It is a theorem-backed gap certificate
for the declared sparse plan, with repair fields and witness lags. It does not
claim attention quality, runtime speed, memory savings, training benefit,
optimal sparse layout design, or replacement of full attention.

For a passing coverage gate over the same finite fixture, use the complete
local fallback:

```bash
python scripts/circle_ai_certify.py sparse-attention \
  --context 120 \
  --strides 7,13 \
  --path-length 3 \
  --local-window 119 \
  --require-passed
```

## 5. Run Recurrence Schedule Accounting

```bash
python scripts/circle_ai_certify.py recurrence \
  --period 6 \
  --position 9 \
  --horizon-steps 8 \
  --sequence-length 24 \
  --block-start 6 \
  --block-width 6 \
  --shift-amount 18
```

Expected summary shape:

```text
circle_ai_contract_receipt=proved kind=recurrence_schedule ... request_passed=True
proof_status=theorems=64 resolved=True proved=True unresolved=0 unproved=0
decision=verdict=passed assurance=mixed_theorem_and_computation claim_status=proved request_passed=True
recurrence_work=active=84 inactive=60 saving=60
recurrence_periodic_shift=base_token=23 passes=3 shift=18 shifted_token=41 ... active_at_step_invariant=True
```

Interpretation: this proves finite loop-period, active-token work, post-period
extension, and whole-period shift invariants for the declared schedule. It does
not prove recursive reasoning, adaptive-exit quality, perplexity, throughput,
memory savings, deployment safety, or model quality.

## Python API

Use `circle_math.ai_contracts` for ordinary Python integration:

```python
from circle_math.ai_contracts import (
    build_kv_cache_receipt,
    build_recurrence_receipt,
    build_rope_receipt,
    build_sparse_attention_receipt,
    receipt_summary_lines,
)

receipts = [
    build_rope_receipt(
        head_dim=128,
        base=10000,
        context=131072,
        requested_margin="1/328459",
    ),
    build_kv_cache_receipt(
        cache_size=16,
        current=31,
        token=20,
        batch_tokens=[20, 24, 29, 31],
        sink_size=4,
    ),
    build_sparse_attention_receipt(
        context=120,
        strides=[7, 13],
        path_length=3,
        local_window=4,
    ),
    build_recurrence_receipt(
        loop_period=6,
        sample_index=9,
        max_loops=8,
        token_count=24,
        selected_block_start=6,
        selected_block_width=6,
        shift_passes=3,
    ),
]

for receipt in receipts:
    print(receipt_summary_lines(receipt)[0])
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
    assert receipt["not_claimed"]
```

Read `request_passed` separately from proof status. A sparse receipt can be
fully theorem-backed and still fail the requested coverage property; that is a
valid gap certificate.

## Where To Go Next

- Living Book phase probe: `site/chapters/applications/circle_phase_probe_demo.qmd`
- Living Book AI contract suite: `site/chapters/applications/ai_contract_suite.qmd`
- Runner details: `docs/CIRCLE_AI_CONTRACT_RUNNER.md`
- RoPE details: `docs/ROPE_CERTIFIER_QUICKSTART.md`
- KV-cache details: `docs/KV_CACHE_CERTIFIER_QUICKSTART.md`
- Sparse-attention details: `docs/SPARSE_ATTENTION_CERTIFIER_QUICKSTART.md`
- Recurrence details: `docs/RECURRENCE_SCHEDULE_CERTIFIER_QUICKSTART.md`
