# Circle Phase Probe Demo

This demo is a small, runnable AI-facing artifact for Circle Calculus. It uses a synthetic periodic label and compares two linear probes:

- `raw_position_linear`: features `[1, x]`
- `circle_sin_cos_linear`: features `[1, cos(2*pi*x/period), sin(2*pi*x/period)]`

The point is narrow: when the target rule is periodic, circle phase coordinates can make that rule linearly readable in a way a raw-position ramp cannot.

Run it with NumPy:

```bash
python scripts/circle_phase_probe_demo.py --backend numpy
```

Expected default output:

```text
circle_phase_probe=READY period=8 backend=numpy train=32 test=16
baseline=raw_position_linear train_accuracy=0.500000 test_accuracy=0.500000
phase=circle_sin_cos_linear train_accuracy=1.000000 test_accuracy=1.000000
target_rule=label(x)=1 iff cos(2*pi*(x mod period)/period) >= 0
non_claimed=This synthetic probe does not prove real model quality, speed, memory, context-length, or reasoning gains.
```

JSON output is available for downstream scripts:

```bash
python scripts/circle_phase_probe_demo.py --backend numpy --format json
```

MLX is optional on Apple Silicon:

```bash
python scripts/circle_phase_probe_demo.py --backend mlx
```

The MLX path constructs the phase tensors with MLX, then uses NumPy least squares for the tiny deterministic probe. This is not an MLX training benchmark.

## Non-Claims

This demo does not prove that circle features improve real transformer quality, inference speed, memory use, context length, or reasoning ability. It is a minimal witness that a known periodic rule can be represented cleanly by circle phase features.

## Relation To Circle Calculus

The feature map sends each position into a finite-period circle coordinate:

```text
x -> (cos(2*pi*x/period), sin(2*pi*x/period))
```

That is the same circle-native idea used by the RoPE and phase-bank contract lane, but here it is presented as a tiny executable learning example rather than a formal proof certificate.
