# RoPE Certifier Preset Results

These are proof-carrying position-contract reports for declared integer-period phase banks plus numerical real-phase margin scans. They are not model-quality, context-length, speed, memory, perplexity, or deployment claims.

## Named Rational Margin Certificate

| Name | Ratio | Context | Certified margin | Status | Theorem ids |
| --- | --- | ---: | ---: | --- | --- |
| rational_turn_ratio_1_4099_context_4096 | 1/4099 | 4096 | 0.000243961941937 | PASS | AIRA-T0056, AIRA-T0059, AIRA-T0060, AIRA-T0061, AIRA-T0062 |

This is a theorem-backed rational/discretized turn-ratio certificate. It is not a proof of the standard irrational real RoPE schedule unless that schedule is explicitly replaced by the declared rational ratio.

## Named Standard RoPE Interval Seed

| Name | Turn ratio | Context | Certified margin | Pi bounds | Status | Theorem ids |
| --- | --- | ---: | --- | --- | --- | --- |
| standard_rope_channel0_interval_context_65536 | 1/(2*pi) | 65536 | 1/104219 | pi <= 4, 3.14 < pi, pi < 3.15, 3.1415 < pi, pi < 3.1416, 3.141592 < pi, pi < 3.141593, 3.14159265358979323846 < pi, and pi < 3.14159265358979323847 | PASS | AIRA-T0063, AIRA-T0064, AIRA-T0065, AIRA-T0066, AIRA-T0067, AIRA-T0068, AIRA-T0069, AIRA-T0070, AIRA-T0071, AIRA-T0072, AIRA-T0073, AIRA-T0074, AIRA-T0075, AIRA-T0076, AIRA-T0077, AIRA-T0078, AIRA-T0079, AIRA-T0080, AIRA-T0081, AIRA-T0082, AIRA-T0083, AIRA-T0084, AIRA-T0085, AIRA-T0086, AIRA-T0087, AIRA-T0088, AIRA-T0089, AIRA-T0090, AIRA-T0091, AIRA-T0092, AIRA-T0093, AIRA-T0094, AIRA-T0095, AIRA-T0096, AIRA-T0097, AIRA-T0098, AIRA-T0099, AIRA-T0100, AIRA-T0101, AIRA-T0102, AIRA-T0103, AIRA-T0104, AIRA-T0105, AIRA-T0106, AIRA-T0107, AIRA-T0108, AIRA-T0109, AIRA-T0110, AIRA-T0111, AIRA-T0112, AIRA-T0113, AIRA-T0114, AIRA-T0115, AIRA-T0116, AIRA-T0117, AIRA-T0118, AIRA-T0119, AIRA-T0120, AIRA-T0121, AIRA-T0122, AIRA-T0123, AIRA-T0124, AIRA-T0125, AIRA-T0126, AIRA-T0127, AIRA-T0128, AIRA-T0129, AIRA-T0130, AIRA-T0131, AIRA-T0132, AIRA-T0133, AIRA-T0134, AIRA-T0135, AIRA-T0136, AIRA-T0137, AIRA-T0138, AIRA-T0139, AIRA-T0140, AIRA-T0141, AIRA-T0142, AIRA-T0143, AIRA-T0144, AIRA-T0145, AIRA-T0146, AIRA-T0147, AIRA-T0148, AIRA-T0149, AIRA-T0150, AIRA-T0151, AIRA-T0152, AIRA-T0153 |

This is a theorem-backed interval certificate for the genuine standard RoPE channel-0 turn ratio over context 65536, plus conditional one-separating-channel bank bridges. It is not a proof that every standard RoPE channel has a large-context margin, and it does not certify 128k contexts.

## Standard RoPE D12 Bank Bridge Request

| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d12_bank_bridge_request | standard_channel0_first | 8192 | 1/104220 | 8192 | 1/104220 | PASS | AIRA-T0123, AIRA-T0124 |

This is a conditional one-separating-channel bank certificate based on standard channel 0. It is not a full all-channel standard-RoPE margin theorem, not a 128k certificate, and not a model-quality claim.

## Standard RoPE D12 Margin Bracket

| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d12_context8192_margin_bracket | 8192 | 1/104220 | 1/104218 | PASS | AIRA-T0120, AIRA-T0121, AIRA-T0118, AIRA-T0125 |

This is an 8k one-channel standard-RoPE bracket. It is not a full all-channel bank margin theorem, not a 128k certificate, and it does not decide margins strictly between 1/104220 and 1/104218.

## Standard RoPE D13 Bank Bridge Request

| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d13_bank_bridge_request | standard_channel0_first | 8192 | 1/104219 | 8192 | 1/104219 | PASS | AIRA-T0130, AIRA-T0131 |

This is a conditional one-separating-channel bank certificate based on standard channel 0. It is not a full all-channel standard-RoPE margin theorem, not a 128k certificate, and not a model-quality claim.

## Standard RoPE D13 Margin Bracket

| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d13_context8192_margin_bracket | 8192 | 1/104219 | 1/104218 | PASS | AIRA-T0127, AIRA-T0128, AIRA-T0118, AIRA-T0132 |

This is an 8k one-channel standard-RoPE bracket. It is not a full all-channel bank margin theorem, not a 128k certificate, and it does not decide margins strictly between 1/104219 and 1/104218.

## Standard RoPE D14 Bank Bridge Request

| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d14_bank_bridge_request | standard_channel0_first | 16384 | 1/104219 | 16384 | 1/104219 | PASS | AIRA-T0136, AIRA-T0137 |

This is a conditional one-separating-channel bank certificate based on standard channel 0. It is not a full all-channel standard-RoPE margin theorem, not a 128k certificate, and not a model-quality claim.

## Standard RoPE D14 Margin Bracket

| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d14_context16384_margin_bracket | 16384 | 1/104219 | 1/104218 | PASS | AIRA-T0133, AIRA-T0134, AIRA-T0118, AIRA-T0138 |

This is a 16k one-channel standard-RoPE bracket. It is not a full all-channel bank margin theorem, not a 128k certificate, and it does not decide margins strictly between 1/104219 and 1/104218.

## Standard RoPE D16 Bank Bridge Request

| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d16_bank_bridge_request | standard_channel0_first | 65536 | 1/104219 | 65536 | 1/104219 | PASS | AIRA-T0151, AIRA-T0152 |

This is a conditional one-separating-channel bank certificate based on standard channel 0. It is not a full all-channel standard-RoPE margin theorem, not a 128k certificate, and not a model-quality claim.

## Standard RoPE D16 Margin Bracket

| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_d16_context65536_margin_bracket | 65536 | 1/104219 | 1/104218 | PASS | AIRA-T0148, AIRA-T0149, AIRA-T0118, AIRA-T0153 |

This is a 64k one-channel standard-RoPE bracket. It is not a full all-channel bank margin theorem, not a 128k certificate, and it does not decide margins strictly between 1/104219 and 1/104218.

## Standard Channel-0 Frontier Summary

| Proved margin | Proved context | Proved status | Candidate full contexts | Candidate first uncovered gaps | Compression bridge | Frontier status |
| ---: | ---: | --- | --- | --- | --- | --- |
| 1/104219 | 65536 | lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150 |  | 103993 | AIRA-T0139, AIRA-T0140, AIRA-T0141 | candidate_plan_not_lean_proved |

This is a derived sidecar summary of proved and candidate interval plans. It does not upgrade candidate rows to theorem-backed status.

## Standard RoPE Candidate Interval Plans

These exact-rational plans are generated source data for Lean interval certificates. The d4 context-333, d6 context-710, d20 context-4096, d20 context-8192, d20 context-16384, d20 context-32768, and d20 context-65536 plans listed here are now matched by compiled Lean declarations; the 128k-frontier row remains candidate-only until a matching declaration compiles and manifest ids exist.

| Plan | Pi bounds | Planned margin | Covered context | First uncovered gap | Bands | Status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| standard_rope_channel0_interval_plan_d4_margin_1_512_context_333 | 3.1415 < pi and pi < 3.1416 | 1/512 | 333 | 333 | 53 | lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089 |
| standard_rope_channel0_interval_plan_d6_margin_1_1024_context_710 | 3.141592 < pi and pi < 3.141593 | 1/1024 | 710 | 710 | 113 | lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_4096 | 3.14159265358979323846 < pi and pi < 3.14159265358979323847 | 1/104219 | 4096 | none | 652 | lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114 |
| standard_rope_channel0_interval_plan_d20_margin_1_104220_context_8192 | 3.14159265358979323846 < pi and pi < 3.14159265358979323847 | 1/104220 | 8192 | none | 1304 | lean_proved_interval_seed_AIRA-T0120_to_AIRA-T0122 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_8192 | 3.14159265358979323846 < pi and pi < 3.14159265358979323847 | 1/104219 | 8192 | none | 1304 | lean_proved_interval_seed_AIRA-T0127_to_AIRA-T0129 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_16384 | 3.14159265358979323846 < pi and pi < 3.14159265358979323847 | 1/104219 | 16384 | none | 2608 | lean_proved_interval_seed_AIRA-T0133_to_AIRA-T0135 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_32768 | 3.14159265358979323846 < pi and pi < 3.14159265358979323847 | 1/104219 | 32768 | none | 5216 | lean_proved_interval_seed_AIRA-T0142_to_AIRA-T0144 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_65536 | 3.14159265358979323846 < pi and pi < 3.14159265358979323847 | 1/104219 | 65536 | none | 10431 | lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_103993 | 3.14159265358979323846 < pi and pi < 3.14159265358979323847 | 1/104219 | 103993 | 103993 | 16551 | candidate_plan_not_lean_proved |

### Rational-Band Certificate Audits

These executable audits check whether each generated band list has the finite shape needed by the generic compression bridge. They are source-data checks for the next Lean certificate route, not proof-status upgrades for candidate rows.

| Audit | Requested context | Certified context | Bands | Valid bands | Covered gaps | First uncovered gap | Coverage | Endpoint validity | Status | Bridge ids |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| standard_rope_channel0_interval_plan_d4_margin_1_512_context_333 | 333 | 333 | 53 | 53 | 332 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d6_margin_1_1024_context_710 | 710 | 710 | 113 | 113 | 709 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_4096 | 4096 | 4096 | 652 | 652 | 4095 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d20_margin_1_104220_context_8192 | 8192 | 8192 | 1304 | 1304 | 8191 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_8192 | 8192 | 8192 | 1304 | 1304 | 8191 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_16384 | 16384 | 16384 | 2608 | 2608 | 16383 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_32768 | 32768 | 32768 | 5216 | 5216 | 32767 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_65536 | 65536 | 65536 | 10431 | 10431 | 65535 | none | PASS | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_103993 | 131072 | 103993 | 16551 | 16551 | 103992 | 103993 | FAIL | PASS | executable_band_audit_not_lean_proved | AIRA-T0139, AIRA-T0140, AIRA-T0141 |

### Band Endpoint Audit

Each row shows the endpoint inequalities a generator must justify before the Lean bridge `AIRA-T0126` can fill in the intermediate gaps for that band. This table samples the first and last band for each generated plan; rerun the Python planner for the complete deterministic band list.

| Plan | Band | Gap range | Cell | Start lower endpoint | End upper endpoint | Endpoint check | Bridge |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| standard_rope_channel0_interval_plan_d4_margin_1_512_context_333 | first | 1-6 | 0 | 625/3927 | 6000/6283 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d4_margin_1_512_context_333 | last | 327-332 | 52 | 68125/1309 | 332000/6283 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d6_margin_1_1024_context_710 | first | 1-6 | 0 | 500000/3141593 | 375000/392699 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d6_margin_1_1024_context_710 | last | 704-709 | 112 | 352000000/3141593 | 44312500/392699 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_4096 | first | 1-6 | 0 | 50000000000000000000/314159265358979323847 | 150000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_4096 | last | 4091-4095 | 651 | 204550000000000000000000/314159265358979323847 | 102375000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104220_context_8192 | first | 1-6 | 0 | 50000000000000000000/314159265358979323847 | 150000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104220_context_8192 | last | 8187-8191 | 1303 | 409350000000000000000000/314159265358979323847 | 204775000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_8192 | first | 1-6 | 0 | 50000000000000000000/314159265358979323847 | 150000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_8192 | last | 8187-8191 | 1303 | 409350000000000000000000/314159265358979323847 | 204775000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_16384 | first | 1-6 | 0 | 50000000000000000000/314159265358979323847 | 150000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_16384 | last | 16381-16383 | 2607 | 819050000000000000000000/314159265358979323847 | 409575000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_32768 | first | 1-6 | 0 | 50000000000000000000/314159265358979323847 | 150000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_32768 | last | 32767-32767 | 5215 | 1638350000000000000000000/314159265358979323847 | 819175000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_65536 | first | 1-6 | 0 | 50000000000000000000/314159265358979323847 | 150000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_65536 | last | 65534-65535 | 10430 | 3276700000000000000000000/314159265358979323847 | 1638375000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_103993 | first | 1-6 | 0 | 50000000000000000000/314159265358979323847 | 150000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |
| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_103993 | last | 103987-103992 | 16550 | 5199350000000000000000000/314159265358979323847 | 2599800000000000000000000/157079632679489661923 | PASS | AIRA-T0126 |

## RoPE Preset Diagnostics

| Preset | Head dim | Base | Context | Exact discrete | Common collision gap | Common-gap pairs | Total bank pairs | First pass prefix | Smallest pass subfamily | Real margin | Worst gap | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| llama_style_10000_4k | 128 | 10000 | 4096 | PASS | >= context | 0 | 0 | 5 | 1 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| llama_style_10000_128k | 128 | 10000 | 131072 | PASS | >= context | 0 | 0 | 8 | 2 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| llama_style_500000_128k | 128 | 500000 | 131072 | PASS | >= context | 0 | 0 | none | 1 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_single_channel_10000_20 | 2 | 10000 | 20 | FAIL | 6 | 14 | 24 | none | none | PASS (0.150444 rad) | 19 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_two_channel_36_128 | 4 | 36 | 128 | FAIL | 114 | 14 | 14 | none | none | PASS (0.0973355 rad) | 113 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_prefix_pass_4_128 | 8 | 4 | 128 | PASS | >= context | 0 | 0 | 3 | 2 | PASS (0.606456 rad) | 88 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_shared_factor_25_64 | 6 | 25 | 64 | FAIL | 54 | 10 | 10 | none | none | PASS (0.548668 rad) | 56 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |

## Exact Phase-Bank Diagnostics

These exact-only presets exercise quantized/shared-factor and interpolation-style scaled-period boundary cases. They are declared integer-period phase-bank contracts, not real-valued RoPE claims.

| Preset | Periods | Context | Exact discrete | Common collision gap | Total bank pairs | First pass prefix | Smallest pass subfamily | Theorem ids |
| --- | --- | ---: | --- | --- | ---: | --- | --- | --- |
| quantized_shared_factor_256 | 32,48,96 | 256 | FAIL | 96 | 224 | none | none | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| quantized_lcm_boundary_fail_241 | 15,16 | 241 | FAIL | 240 | 1 | none | none | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| interpolated_x4_boundary_pass_960 | 60,64 | 960 | PASS | >= context | 0 | 2 | 2 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| interpolated_x4_boundary_fail_961 | 60,64 | 961 | FAIL | 960 | 1 | none | none | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |

Reproduce with:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
```
