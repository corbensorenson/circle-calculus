# RoPE Certifier Quickstart

This quickstart is for ML engineers who want to inspect a RoPE-like positional configuration without reading Lean code first.

The certifier answers a narrow contract question:

```text
Under a declared integer-period phase-bank model, do any two positions inside this context collide in every channel?
```

It also prints a numerical real-phase margin scan for ordinary RoPE frequencies. That scan is useful engineering evidence, but it is not a formal proof.

## Install

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Lean is not required to run the Python certifier. Lean is required only if you want to rebuild the formal proof source with `lake build`.

## Run A Preset

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
```

Available presets:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --preset llama_style_10000_128k
python scripts/rope_certify.py --preset llama_style_500000_128k
python scripts/rope_certify.py --preset diagnostic_single_channel_10000_20
python scripts/rope_certify.py --preset diagnostic_two_channel_36_128
python scripts/rope_certify.py --preset diagnostic_prefix_pass_4_128
python scripts/rope_certify.py --preset diagnostic_shared_factor_25_64
```

The `llama_style_*` preset names are public-safe configuration labels. They are not claims about a particular vendor checkpoint. The `diagnostic_*` presets are small exact-discrete cases for checking collision-count, prefix-pass, and shared-factor failure fields.

## Run A Custom Config

```bash
python scripts/rope_certify.py --head-dim 128 --base 10000 --context 32768 --tolerance 1e-6
```

Key flags:

- `--head-dim`: RoPE head dimension. It must be even because RoPE uses dimension pairs.
- `--base`: the RoPE base, such as `10000` or `500000`.
- `--context`: the inspected context length.
- `--tolerance`: numerical real-phase margin threshold in radians.
- `--discretization`: one of `round`, `floor`, or `ceil`, controlling how real period estimates become integer periods for the exact Lean-backed contract.

## Run An Explicit Integer Phase Bank

When you already have declared integer periods from a quantized, rationalized, or diagnostic phase bank, use the exact-only CLI:

```bash
python scripts/phase_bank_certify.py --periods 6,9,13,18 --context 128
```

This command emits the theorem-linked exact discrete certificate only. It does not compute or claim any real-valued RoPE margin.

Named exact-only diagnostics are also available:

```bash
python scripts/phase_bank_certify.py --preset quantized_shared_factor_256
python scripts/phase_bank_certify.py --preset quantized_lcm_boundary_fail_241
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_pass_960
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_fail_961
```

The `quantized_*` presets exercise shared-factor and one-token-past-boundary failures for declared integer periods. The `interpolated_x4_*` presets use the exact integer-period analogue of slowing phase advance by multiplying declared periods by `4`; they show the pass/fail boundary at LCM `960`. `AIRA-T0199` through `AIRA-T0202` certify the concrete count values for those exact phase-bank diagnostic rows, while `AIRA-T0198` certifies the shared-factor RoPE diagnostic count. `AIRA-T0206` proves the reusable first-repeat-only count formula, `AIRA-T0207` proves the one-token-past-boundary count is exactly `1`, `AIRA-T0210` proves the quotient bound for how many positive multiples of the common gap fit inside the inspected context, `AIRA-T0211` proves the total positive-multiple count equals the sum over that fitting range, `AIRA-T0212` proves the doubled triangular closed-form numerator for that count, and `AIRA-T0213` proves the exact divided closed form. `AIRA-T0204` certifies the single-period threshold, and `AIRA-T0203`/`AIRA-T0205` certify the zero-count/no-collision and positive-count/witness meanings of each single-period count. These are exact phase-bank contracts, not real-valued interpolation proofs.

## Read The Output

The text output has two different evidence layers:

```text
proof_layers=exact_integer_period_phase_bank:PASS,rational_discretized_finite_margin:AVAILABLE_NAMED_PRESET,interval_backed_standard_rope:AVAILABLE_SEED_CONTEXT_196608,numerical_real_phase_scan:PASS
exact_discrete_contract=PASS common_collision_gap=>= context
guaranteed_common_gap_collision_pair_count=0 common_gap_fitting_multiple_count=0 common_gap_collision_pair_count_closed_form_numerator=0 guaranteed_common_gap_multiple_pair_count=0 total_bank_collision_pair_count=0
prefix_collision_reports=... first_exact_pass_prefix_length=...
subfamily_pass_reports=... smallest_pass_subfamily_size=...
real_phase_margin=PASS worst_margin_radians=...
real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031,AIRA-T0032,AIRA-T0033,AIRA-T0037,AIRA-T0038,AIRA-T0039,AIRA-T0040,AIRA-T0041,AIRA-T0042,AIRA-T0043,AIRA-T0044,AIRA-T0045,AIRA-T0047,AIRA-T0050,AIRA-T0053,AIRA-T0054,AIRA-T0055,AIRA-T0056,AIRA-T0057,AIRA-T0058,AIRA-T0059,AIRA-T0182,AIRA-T0183,AIRA-T0214,AIRA-T0177,AIRA-T0186,AIRA-T0178,AIRA-T0181,AIRA-T0196,AIRA-T0197,AIRA-T0209,AIRA-T0216,AIRA-T0217,AIRA-T0218,AIRA-T0219,AIRA-T0220,AIRA-T0221,AIRA-T0233,AIRA-T0234,AIRA-T0235,AIRA-T0236,AIRA-T0237,AIRA-T0232,AIRA-T0238,AIRA-T0239,AIRA-T0222,AIRA-T0223,AIRA-T0224,AIRA-T0225,AIRA-T0226,AIRA-T0227,AIRA-T0228,AIRA-T0229,AIRA-T0230,AIRA-T0231,AIRA-T0126,AIRA-T0139,AIRA-T0140,AIRA-T0141 (unwrapped, signed full-turn, turn-separation, bank-level no-near-turn, turn-ratio scaling, finite-context margin consequence, context-plus-margin transfer, integer/rational-turn-ratio guardrails, positive rational finite-context certificate and exact rational boundary, generated-gap enumeration, floor/ceiling nearest-integer, scalar nearest-gap margin, exact weakest-gap report contract, finite certificate iff, positive no-zero bridge, negative obstruction iff, scaled no-near-turn iff, certificate-object no-near-turn iff, finite-certificate bank bridge, context-range obstruction bridge, request-level D19 classifier bridge, classifier threshold ordering and branch-disjointness guards, exact open-gap/exhaustive classifier guards, in-range semantic trichotomy, proved-branch first-channel bank transfer, context-wide request scope, ordinary-radian-bank transfer, request semantic trichotomy transfer, exact D19 open-gap width, public undecided-probe open-gap guard, finite-context Dirichlet upper-bound guardrail, reduced-rational exact weakest-gap, full-denominator threshold, request-obstruction contracts, and exact weakest-gap request thresholds, plus band-endpoint and band-list compression bridge precursors only; not a positive Diophantine margin proof)
theorem_ids=AIRA-T0021,AIRA-T0022,AIRA-T0023,AIRA-T0024,AIRA-T0025,AIRA-T0026,AIRA-T0027,AIRA-T0028,AIRA-T0034,AIRA-T0035,AIRA-T0036,AIRA-T0179,AIRA-T0180,AIRA-T0184,AIRA-T0046,AIRA-T0048,AIRA-T0049,AIRA-T0051,AIRA-T0052,AIRA-T0174,AIRA-T0175,AIRA-T0176,AIRA-T0203,AIRA-T0204,AIRA-T0205,AIRA-T0206,AIRA-T0207,AIRA-T0210,AIRA-T0211,AIRA-T0212,AIRA-T0213
```

`exact_discrete_contract=PASS` means the integer-period phase bank has no all-channel collision among unequal positions inside the inspected context. The Lean-backed theorem spine proves that all-channel collision is equivalent to the period-bank LCM dividing the position gap, `AIRA-T0179` proves the positive-period input policy gives a positive LCM, and `AIRA-T0180` proves the exact pass/fail iff: no unequal all-channel collision in the context exactly when that LCM reaches the context.

`real_phase_margin=PASS` means the numerical scan did not find a real-valued near-collision below the chosen tolerance. This is not a Lean proof over real trigonometric RoPE.

`proof_layers=...` separates the evidence types. The exact integer-period layer is theorem-backed for the declared discretized phase-bank model. The rational/discretized finite-margin layer points to the named `1/4099` preset. The interval-backed standard-RoPE layer points to the bounded channel-0 context-196608 seed. The numerical scan remains diagnostic even when it passes.

`real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031,AIRA-T0032,AIRA-T0033,AIRA-T0037,AIRA-T0038,AIRA-T0039,AIRA-T0040,AIRA-T0041,AIRA-T0042,AIRA-T0043,AIRA-T0044,AIRA-T0045,AIRA-T0047,AIRA-T0050,AIRA-T0053,AIRA-T0054,AIRA-T0055,AIRA-T0056,AIRA-T0057,AIRA-T0058,AIRA-T0059,AIRA-T0182,AIRA-T0183,AIRA-T0214,AIRA-T0177,AIRA-T0186,AIRA-T0178,AIRA-T0181,AIRA-T0196,AIRA-T0197,AIRA-T0209,AIRA-T0216,AIRA-T0217,AIRA-T0218,AIRA-T0219,AIRA-T0220,AIRA-T0221,AIRA-T0233,AIRA-T0234,AIRA-T0235,AIRA-T0236,AIRA-T0237,AIRA-T0232,AIRA-T0238,AIRA-T0239,AIRA-T0222,AIRA-T0223,AIRA-T0224,AIRA-T0225,AIRA-T0226,AIRA-T0227,AIRA-T0228,AIRA-T0229,AIRA-T0230,AIRA-T0231,AIRA-T0126,AIRA-T0139,AIRA-T0140,AIRA-T0141` means Lean has proved the unwrapped one-channel real phase-gap arithmetic, signed full-turn-multiple window precursors, the bank-level theorem shape that one proved separating channel rules out an all-channel near-turn collision at smaller tolerance, the turn-ratio scaling bridge into nearest-integer Diophantine error, the one-channel and bank-level consequences of a finite-context turn-ratio margin certificate, conservative context/margin/context-plus-margin transfer laws, the guardrails that integer and natural-rational turn ratios cannot provide a positive finite-context margin once their exact-return gap is in scope, the positive `1 / denominator` finite-context certificate for reduced natural rational ratios before the denominator gap enters scope, the exact boundary saying that certificate holds iff the inspected context stays at or below the denominator, the bridge from the abstract finite-context predicate to generated positive gaps in `List.range context`, the floor/ceiling witness bridge reducing each fixed-gap integer-turn check to two nearest-integer witnesses, the scalar nearest-gap margin bridge for reporting one weakest-gap number, the exact weakest-gap report bridge, the bidirectional bridge between finite nearest-integer certificate objects and the abstract finite-context margin predicate, the positive no-zero bridge, the iff saying finite-margin failure is exactly an explicit below-margin gap/turn witness, the iff saying a one-channel finite margin is exactly absence of all in-context near-turn witnesses below the scaled tolerance, the theorem saying the finite certificate object itself is equivalent to that no-near-turn contract, the bank-level bridge from one certified channel to all-channel no-near-turn after context and margin downgrades, the context-range obstruction bridge, the request-level D19 classifier bridge, the classifier threshold ordering, branch-disjointness, open-gap, exhaustive-status, in-range semantic trichotomy, proved-branch first-channel bank transfer, context-wide request scope, ordinary-radian-bank transfer, request semantic trichotomy transfer, exact-width guards, public undecided-probe open-gap guard, and the Dirichlet finite-context upper-bound guardrail that every nontrivial context has some gap with nearest-integer error at most `1/context`, the reduced-rational exact weakest-gap, full-denominator exact-threshold, request-obstruction contracts, exact weakest-gap request-threshold contracts, and the band-endpoint plus band-list compression bridges for generated interval certificates. It is not a positive Diophantine proof that arbitrary RoPE gaps satisfy the margin predicate and does not certify the numerical scan.

## Named Rational Margin Certificate

The first end-to-end real-phase-margin-shaped certificate is a rational/discretized turn-ratio preset, not the standard irrational RoPE schedule:

```python
from circle_math.applications import certify_rational_preset_4099

certificate = certify_rational_preset_4099()
print(certificate.name)
print(certificate.pass_certificate)
print(certificate.certified_margin)
print(certificate.exact_nearest_gap_margin)
print(certificate.exact_nearest_gap)
print(certificate.theorem_ids)
```

Expected meaning:

```text
rational_turn_ratio_1_4099_context_4096
True
1 / 4099, represented as a Python float
1/4099
1
AIRA-T0056,AIRA-T0059,AIRA-T0182,AIRA-T0183,AIRA-T0214,AIRA-T0060,AIRA-T0177,AIRA-T0186,AIRA-T0061,AIRA-T0185,AIRA-T0215,AIRA-T0222,AIRA-T0223,AIRA-T0187,AIRA-T0196,AIRA-T0062
```

Lean proves that the declared turn ratio `1/4099` has finite-context nearest-integer margin `1/4099` for every positive gap below context `4096`, proves that the scalar nearest-gap margin can stand in for the floor/ceiling witness pair, proves the reusable exact-weakest-gap report contract, proves that the named gap `1` realizes the exact reported margin, proves that the finite nearest-integer certificate object is equivalent to the abstract margin predicate, proves that the certificate object is equivalent to the one-channel no-near-turn contract, then proves the corresponding named no-near-turn consequence. This is useful as the first complete certificate shape. It is not a proof that the standard `1 / (2π)` RoPE channel has the same kind of finite-context margin.

For reduced rational turn ratios at the full denominator context, the certifier
also cites the full-denominator existence theorem:

```python
from circle_math.applications import certify_rational_turn_ratio_finite_margin

certificate = certify_rational_turn_ratio_finite_margin(
    numerator=3,
    denominator=7,
    context_length=7,
)
print(certificate.exact_nearest_gap_margin)
print(certificate.exact_nearest_gap)
print(certificate.theorem_ids)
```

Expected meaning:

```text
1/7
2
AIRA-T0056,AIRA-T0057,AIRA-T0182,AIRA-T0183,AIRA-T0224,AIRA-T0225,AIRA-T0226,AIRA-T0227,AIRA-T0228,AIRA-T0229,AIRA-T0230,AIRA-T0231
```

`AIRA-T0224` through `AIRA-T0226` prove that a supplied plus-or-minus-one
modular-inverse gap realizes the exact weakest scalar margin. `AIRA-T0227`
adds the full-denominator existence result: for a reduced natural-rational turn
ratio, some positive gap below the denominator realizes that exact margin.
`AIRA-T0228` adds the exact full-denominator threshold: at context
`denominator`, advertised margins above `1/denominator` fail. `AIRA-T0229`
adds the explicit failure witness used by request reports: above the threshold,
some positive gap below the denominator has nearest-integer error below the
requested margin. `AIRA-T0230` and `AIRA-T0231` generalize this request
threshold to any exact weakest-gap certificate, not only reduced-rational
full-denominator reports.

When a request includes `requested_margin`, the Python certificate now exposes
`requested_margin_status`:

- `proved`: the requested margin is covered by a theorem-backed lower bound.
- `impossible`: an exact weakest-gap threshold or exact zero-gap witness rules out the requested positive margin.
- `unproved_above_certified_lower_bound`: the request is above the conservative certified lower bound, but this report has not proved it impossible.
- `unproved`: no positive margin certificate is available for the declared rational row.

## Named Standard RoPE Interval Seed

The theorem-backed certificate for the genuine standard channel is bounded and explicit:

```python
from circle_math.applications import certify_standard_channel0_interval_seed

certificate = certify_standard_channel0_interval_seed()
print(certificate.name)
print(certificate.pass_certificate)
print(certificate.certified_margin)
print(certificate.theorem_ids)
```

Expected meaning:

```text
standard_rope_channel0_interval_context_196608
True
1/328459
AIRA-T0063,AIRA-T0064,AIRA-T0065,...,AIRA-T0173
```

Lean proves that channel 0 with standard turn ratio `1 / (2π)` has finite-context nearest-integer margin `1/328459` for gaps `1` through `196607`. The D19 192k seed uses the 20-decimal enclosure `10^20*gap/628318530717958647694 <= gap/(2π) <= 10^20*gap/628318530717958647692`, split across computed integer cells `0` through `31290`. Lean also proves the sharper 64k bracket at margin `1/104219`, while every advertised margin at or above `1/104218` is impossible there because of gap `710`. `AIRA-T0154` and `AIRA-T0155` add the adjacent obstruction for the lower-margin family: gap `103993` is already within `1/328458` of integer turn `16551`, so `1/328458` and larger margins are impossible once that gap is in scope. `AIRA-T0156` through `AIRA-T0161` are the generated D17 128k interval certificate, bank bridges, and bracket; `AIRA-T0162` through `AIRA-T0167` extend the same margin to the generated D18 160k seed; `AIRA-T0168` through `AIRA-T0173` extend it to the generated D19 192k seed; `AIRA-T0209` proves the generic context-range bridge from one certified horizon plus one obstruction gap; `AIRA-T0208` specializes that bridge to the D19 range bracket for every `103993 < context <= 196608`; `AIRA-T0216`/`AIRA-T0217` expose that range as a request-level classifier; `AIRA-T0218`/`AIRA-T0219` prove that the classifier thresholds are ordered and its proved/impossible branches are disjoint; `AIRA-T0234` packages the proved request branch as a conditional first-channel finite-bank no-near-turn guarantee; `AIRA-T0235` packages the same proved branch as a context-wide statement over every ordered unequal pair inside the requested context; `AIRA-T0236` specializes that context-wide statement to the ordinary radian bank form whose first frequency is `1` and whose full turn is `2π`; `AIRA-T0237` packages the whole in-range request trichotomy with the radian first-channel bank consequence in the proved branch; and `AIRA-T0238` proves the public `2/656917` undecided probe lies strictly inside the open gap. This is real standard-RoPE theorem content, but still channel-0 based; it does not turn the impossible one-channel branch into a whole-bank collision theorem.

To ask the strongest concrete D19 bank-bridge request directly:

```python
from fractions import Fraction
from circle_math.applications import certify_standard_channel0_d19_bank_request

request = certify_standard_channel0_d19_bank_request(
    requested_context=196608,
    requested_margin=Fraction(1, 328459),
)
request.pass_certificate  # True
request.theorem_ids       # AIRA-T0171,AIRA-T0172,AIRA-T0234,AIRA-T0235,AIRA-T0236,AIRA-T0237
request.tolerance_rule    # tolerance < fullTurn * requestedMargin
```

This request certificate checks only that the requested context and margin fit inside the D19 seed and that the bank has the stated standard-channel-0 shape. It does not prove every channel has an independent margin.

To read the D19 margin bracket directly:

```python
from circle_math.applications import certify_standard_channel0_d19_margin_bracket

bracket = certify_standard_channel0_d19_margin_bracket()
bracket.context_length             # 196608
bracket.proved_margin              # 1/328459
bracket.impossible_margin_floor    # 1/328458
bracket.theorem_ids                # AIRA-T0168,AIRA-T0169,AIRA-T0155,AIRA-T0173,AIRA-T0209,AIRA-T0208
```

The range bracket applies to every requested context satisfying `103993 < context <= 196608`.
It leaves margins strictly between `1/328459` and `1/328458` unresolved.

To classify a single D19 one-channel margin request:

```python
from fractions import Fraction
from circle_math.applications import (
    certify_standard_channel0_d19_range_request_margin_bracket,
)

request = certify_standard_channel0_d19_range_request_margin_bracket(
    requested_context=131072,
    requested_margin=Fraction(1, 328458),
)
request.request_status  # impossible
request.theorem_ids     # AIRA-T0216,AIRA-T0217,AIRA-T0218,AIRA-T0219,AIRA-T0220,AIRA-T0221,AIRA-T0233,AIRA-T0232,AIRA-T0238
request.margin_thresholds_ordered  # True
request.proved_impossible_branches_disjoint  # True
request.margin_status_exhaustive  # True
request.in_range_semantic_trichotomy  # True
request.requested_margin_relation  # at_or_above_impossible_floor
request.undecided_margin_interval_width  # 1/107884986222
```

The classifier returns `proved` at or below `1/328459`, `impossible` at or above `1/328458`, `undecided_margin_gap` between those rationals, and `outside_range` outside `103993 < context <= 196608`. It also exposes `requested_margin_relation`, `margin_thresholds_ordered`, `proved_impossible_branches_disjoint`, `undecided_margin_open_gap`, `undecided_margin_interval_width`, `margin_status_exhaustive`, `in_range_semantic_trichotomy`, and the first-channel bank-transfer fields so report consumers can audit that the proved and impossible branches cannot overlap, that the remaining in-range margin status is exactly the deliberate open gap of width `1/107884986222`, and that every in-range request is in exactly one semantic branch. `AIRA-T0233` backs that semantic trichotomy; `AIRA-T0232` backs the exact width; `AIRA-T0238` backs that the public `2/656917` undecided probe lies inside the open gap; `AIRA-T0234` backs the proved branch's conditional first-channel bank no-near-turn transfer; `AIRA-T0235` backs the context-wide pair scope; `AIRA-T0236` backs the ordinary radian first-channel form exposed by the contract pack; and `AIRA-T0237` combines the in-range branch classifier with that radian first-channel consequence.

For a copy-safe downstream digest from the public AI contract pack:

```bash
python scripts/circle_ai_contract_ready.py \
  --kind rope_position_distinguishability \
  --digest \
  --field d19_proved_request_status \
  --field d19_impossible_request_status \
  --field d19_undecided_request_status \
  --field d19_proved_first_channel_bank_transfer \
  --field d19_proved_first_channel_bank_shape --field d19_proved_first_channel_pair_scope \
  --field d19_proved_first_channel_context_wide_contract \
  --field d19_proved_first_channel_radian_bank_form \
  --field d19_proved_first_channel_bank_tolerance_rule \
  --include-recommendations
```

For a strict CI receipt that fails if the proved first-channel bank transfer or
its theorem pin disappears:

```bash
python scripts/circle_ai_contract_ready.py \
  --kind rope_position_distinguishability \
  --receipt \
  --format json \
  --field d19_proved_request_status \
  --field d19_impossible_request_status \
  --field d19_undecided_request_status \
  --field d19_proved_first_channel_bank_transfer \
  --field d19_proved_first_channel_bank_shape --field d19_proved_first_channel_pair_scope \
  --field d19_proved_first_channel_context_wide_contract \
  --field d19_proved_first_channel_radian_bank_form \
  --field d19_proved_first_channel_bank_tolerance_rule \
  --require-theorem AIRA-T0171 \
  --require-theorem AIRA-T0172 \
  --require-theorem AIRA-T0234 --require-theorem AIRA-T0235 --require-theorem AIRA-T0236 --require-theorem AIRA-T0237 \
  --require-recommendation ROPE-USE-D19-MARGIN-FRONTIER \
  --require-recommendation-evidence-field ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_bank_transfer --require-recommendation-evidence-field ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_context_wide_contract \
  --require-recommendation-evidence-field ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_radian_bank_form \
  --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234 --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235 --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0236 --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0237 \
  --require-recommendation-action-parameter ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer \
  --require-recommendation-action-parameter-path ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.applies --require-recommendation-action-parameter-path ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.context_wide_contract --require-recommendation-action-parameter-path ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.radian_bank_form \
  --require-recommendation-action-parameter-path ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.theorem_ids
```

The RoPE planner recommendations are:

- `ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK`: audit the declared integer-period phase-bank collision boundary with `exact_discrete_pass`, `common_collision_gap`, and `total_bank_collision_pair_count`.
- `ROPE-USE-D19-MARGIN-FRONTIER`: use the D19 standard-channel-0 theorem-backed request frontier where `1/328459` is proved, `1/328458` is impossible, and `2/656917` is in the deliberate open undecided gap at context `131072`; the planner payload also exposes the exact undecided interval width `1/107884986222`, the `d19_undecided_probe_margin_in_open_gap` guard backed by `AIRA-T0238`, the in-range semantic trichotomy guard, and the proved-branch first-channel context-wide bank-transfer fields backed by `AIRA-T0234`, `AIRA-T0235`, `AIRA-T0236`, and `AIRA-T0237`.

Both records are integration hints over theorem-backed fields. They are not a full all-channel real-RoPE proof, not a Diophantine theorem for arbitrary RoPE channels, and not a model-quality or context-extension claim.

For audit and future Lean work, the sidecar also exposes interval plans and rational-band audits:

```python
from fractions import Fraction
from circle_math.applications import (
    audit_standard_channel0_rational_band_certificate,
    plan_standard_channel0_interval_bands,
)

plan_standard_channel0_interval_bands(
    pi_bound_preset="d4",
    margin=Fraction(1, 512),
).theorem_status  # lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089

plan_standard_channel0_interval_bands(
    pi_bound_preset="d6",
    margin=Fraction(1, 1024),
).theorem_status  # lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
).theorem_status  # lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104220),
    max_context_length=8192,
).theorem_status  # lean_proved_interval_seed_AIRA-T0120_to_AIRA-T0122

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
    max_context_length=8192,
).theorem_status  # lean_proved_interval_seed_AIRA-T0127_to_AIRA-T0129

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
    max_context_length=16384,
).theorem_status  # lean_proved_interval_seed_AIRA-T0133_to_AIRA-T0135

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
    max_context_length=32768,
).theorem_status  # lean_proved_interval_seed_AIRA-T0142_to_AIRA-T0144

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
    max_context_length=65536,
).theorem_status  # lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
    max_context_length=131072,
).first_uncovered_gap  # 103993

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 328459),
    max_context_length=131072,
).theorem_status  # lean_proved_interval_seed_AIRA-T0156_to_AIRA-T0158

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 328459),
    max_context_length=163840,
).theorem_status  # lean_proved_interval_seed_AIRA-T0162_to_AIRA-T0164

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 328459),
    max_context_length=196608,
).theorem_status  # lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170

d20_64k = plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
    max_context_length=65536,
)
audit_standard_channel0_rational_band_certificate(
    d20_64k,
    requested_context_length=65536,
).pass_audit  # True

d20_128k_frontier = plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
    max_context_length=131072,
)
audit_standard_channel0_rational_band_certificate(
    d20_128k_frontier,
    requested_context_length=131072,
).first_uncovered_gap  # 103993
```

Each emitted band also records `start_lower_value`, `end_upper_value`, `endpoint_cell_margin_ok`, and `bridge_theorem_id=AIRA-T0126`. Those fields are the executable sidecar version of the Lean band-endpoint bridge: a generator can prove the band endpoints stay inside one integer cell, then use `AIRA-T0126` to justify every intermediate gap in that band.

For example, the first d4 band records `start_gap=1`, `end_gap=6`, `cell=0`, `start_lower_value=625/3927`, `end_upper_value=6000/6283`, and `endpoint_cell_margin_ok=true`. That means the band endpoints fit safely inside the integer cell from `0` to `1` with the advertised margin, so the monotone band theorem covers gaps `1` through `6`.

The generated Markdown and JSON sidecars include `Rational-Band Certificate Audits`, which check whether each generated band list is positive, contiguous from gap `1`, endpoint-valid, and sufficient for the requested context. They also include `Band Endpoint Audit` summaries with the first and last band of each standard interval plan. Rerun `plan_standard_channel0_interval_bands(...)` for the complete deterministic band list.

The d4, d6, conservative d20 `1/131072`, tighter d20 `1/105000`, sharp 4k d20 `1/104219`, weaker 8k d20 `1/104220`, sharp 8k d20 `1/104219`, sharp 16k d20 `1/104219`, sharp 32k d20 `1/104219`, sharp 64k d20 `1/104219`, D17 128k d20 `1/328459`, D18 160k d20 `1/328459`, and D19 192k d20 `1/328459` plans have been converted into Lean proof. The stronger 128k request at margin `1/104219` still reaches first uncovered gap `103993`, so its audit remains a failed frontier comparison.

If the exact discrete contract fails, the output includes a common collision gap and sample colliding pairs.
It also reports `guaranteed_common_gap_collision_pair_count`, the number of starts whose paired position is exactly the common collision gap ahead; `common_gap_fitting_multiple_count`, the number of positive multiples of that gap still inside the inspected context; `common_gap_collision_pair_count_closed_form_numerator`, the checked numerator equal to twice the positive-multiple count; and `guaranteed_common_gap_multiple_pair_count`, the corresponding guaranteed family summed over those positive in-context multiples. `total_bank_collision_pair_count` is the exact all-channel count for the declared integer-period bank, backed by the period-bank LCM theorem. `AIRA-T0210` proves the quotient bound behind `common_gap_fitting_multiple_count`, `AIRA-T0211` proves the positive-multiple sum can be restricted to that fitting range, `AIRA-T0212` proves the doubled closed-form numerator, and `AIRA-T0213` proves the exact divided closed-form count used by the executable helper. `AIRA-T0179` proves the positive-period input policy gives the positive LCM required by the witness/count theorems, `AIRA-T0180` packages the exact context pass/fail iff, `AIRA-T0048` proves the LCM-gap collision family, `AIRA-T0049` proves that a positive LCM below the context gives an explicit unequal collision witness, `AIRA-T0174`/`AIRA-T0175` prove the positive-multiple count is zero exactly in the LCM-reaches-context pass case, and `AIRA-T0176` proves the nonzero count is equivalent to an unequal all-channel collision witness. It is not a real-valued RoPE collision count.

For each declared integer period, the JSON certificate includes `single_period_collision_pair_counts`. These are exact single-channel counts, not all-channel bank collision counts. `AIRA-T0204` proves the threshold condition: no unequal in-context collision exists exactly when `context_length <= period`. `AIRA-T0203` proves that a zero count is equivalent to no unequal in-context collision for that one positive period, and `AIRA-T0205` proves that a positive count is equivalent to an actual unequal in-context collision witness. `AIRA-T0206` gives the closed form `context_length - period` when the first repeat fits but the second repeat does not, `AIRA-T0207` specializes that to count `1` at `context_length = period + 1`, `AIRA-T0210` proves the quotient loop bound used when multiple repeats fit, `AIRA-T0211` proves the count equals the fitting-range sum, `AIRA-T0212` proves the doubled triangular closed-form numerator, and `AIRA-T0213` proves the exact divided closed form.

The JSON certificate also includes `prefix_collision_reports`, bounded summaries for the first few channel prefixes. Each prefix report reuses the same `AIRA-T0036`/`AIRA-T0046`/`AIRA-T0048`/`AIRA-T0049`/`AIRA-T0174`/`AIRA-T0175`/`AIRA-T0176`/`AIRA-T0210`/`AIRA-T0211`/`AIRA-T0212`/`AIRA-T0213` LCM theorem spine as the full bank, and `AIRA-T0051` proves that adding suffix channels cannot create an unequal collision once a prefix LCM reaches the inspected context. `first_exact_pass_prefix_length` tells you the first declared prefix whose integer-bank LCM already reaches the inspected context; `AIRA-T0190` proves a certified first passing prefix length is unique, and `AIRA-T0191` turns such a first-prefix certificate into a full-bank no-collision bridge.

The certificate also includes bounded `subfamily_pass_reports` for small selected subbanks whose LCM reaches the context. `AIRA-T0052` proves the unordered selected-subbank bridge. When a report carries an explicit smallest-subfamily certificate, `AIRA-T0193` proves the minimal size is unique and `AIRA-T0194` turns that minimal-size certificate into a full-bank no-collision bridge. These are still integer-period sub-bank reports, not real-valued RoPE collision proofs.

## Machine-Readable Output

Print JSON to stdout:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k --format json
```

Write JSON to a file:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k --json-out /tmp/rope_certificate.json
```

The JSON includes:

- config assumptions;
- theorem ids;
- Lean declaration names;
- discretized periods;
- exact single-period collision counts for each discretized period;
- exact all-channel bank collision count for the declared integer-period bank;
- bounded prefix collision reports and the first prefix that already passes, when one appears in the reported bound;
- bounded selected-subfamily pass reports for small declared subbanks;
- a proof-layer inventory distinguishing exact integer-period, rational/discretized, interval-backed standard-RoPE, and numerical diagnostic layers;
- rational-band audit rows for standard channel-0 frontier plans;
- exact discrete pass/fail;
- sample exact collisions when present;
- numerical real-phase margin data;
- a claim boundary.

The full CLI JSON is intentionally verbose. The paper sidecar fixture uses compact certificate summaries so the committed results stay readable while preserving pass/fail status, periods, collision gaps, counts, samples, proof layers, theorem ids, and claim boundaries.

## Reproduce The Preset Results Table

The paper sidecar can emit the preset results used by the paper and Living Book:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
```

To regenerate the committed result fixtures:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py \
  --json-out sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.json \
  --markdown-out sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md
```

## What The Certifier Does Not Claim

The certifier does not claim:

- that standard real-valued RoPE has exact integer periods;
- that a model's context length improves;
- that perplexity, reasoning quality, speed, memory, or training stability improves;
- that numerical scans replace Lean proofs;
- that a pass is enough to deploy a positional scheme.

The useful claim is narrower: the exact discrete contract is theorem-linked, reproducible, and explicit about its assumptions.
