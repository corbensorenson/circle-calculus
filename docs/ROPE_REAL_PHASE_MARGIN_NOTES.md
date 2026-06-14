# RoPE Real-Phase Margin Notes

This note is a durable audit trail for the real-valued RoPE phase-margin theorem program. It records what is already proved, what mathlib infrastructure appears relevant, and what must not be claimed yet.

## Current Proved Bridge

The real-phase theorem spine currently runs from `AIRA-T0029` through `AIRA-T0033`, then `AIRA-T0037` through `AIRA-T0045`, plus `AIRA-T0047`, `AIRA-T0050`, and `AIRA-T0053` through `AIRA-T0138`.

`AIRA-T0041` is the Diophantine-scaling bridge:

```text
|gap * frequency - turns * fullTurn|
=
fullTurn * |gap * (frequency / fullTurn) - turns|
```

under ordered positions, nonnegative frequency, and positive `fullTurn`. It rewrites RoPE near-turn error as the ordinary nearest-integer Diophantine error for the turn ratio:

```text
alpha = frequency / fullTurn
```

This is not a lower-bound theorem. It is the normalization step that makes the next theorem program precise.

`AIRA-T0042` defines `ropeTurnRatioFiniteMargin alpha margin context` and proves that such a finite-context margin rules out one-channel real near-turn collision below the scaled tolerance `fullTurn * margin`. It is conditional: it does not prove that a concrete RoPE turn ratio has the margin.

`AIRA-T0043` lifts the finite-context margin consequence to a finite real-phase bank. One member channel with a proved finite-context margin is enough to rule out an all-channel near-turn collision below the same scaled tolerance.

`AIRA-T0044` proves the monotonic context-transfer law: a finite-context margin certified for a larger horizon applies to every smaller requested horizon. `AIRA-T0047` proves margin-value monotonicity: a larger certified lower bound also proves any smaller advertised margin over the same context. `AIRA-T0045` packages context transfer at the bank level, so a channel margin certified up to `certifiedContext` can be reused for any `requestedContext <= certifiedContext`. `AIRA-T0050` packages both transfers at the bank level, so a larger-context, larger-margin channel certificate can be reused for a smaller requested context and smaller advertised margin in one final no-near-turn statement.

`AIRA-T0053` proves a negative guardrail: if the turn ratio is an integer number of full turns per position and the context includes adjacent positions, then the finite-context margin predicate is equivalent to a nonpositive advertised margin. Whole-turn channels therefore cannot supply a positive real-phase separation certificate.

`AIRA-T0055` extends the same negative guardrail to natural rational turn ratios. If `turnRatio = numerator / denominator` and the inspected context includes the denominator gap, then that gap lands exactly on `numerator` full turns, so the finite-context margin predicate is again equivalent to a nonpositive advertised margin. Rationalized or periodic channels therefore cannot supply a positive finite-context margin once their denominator gap is inside the context.

`AIRA-T0056` gives the positive reduced-rational companion. If `numerator` and `denominator` are coprime and the inspected context is at most the denominator, then every positive inspected gap has nearest-integer error at least `1 / denominator`. `AIRA-T0057` packages the exact boundary: for a reduced natural rational turn ratio, that `1 / denominator` margin holds iff the inspected context stays at or below the denominator. These are theorem-backed finite rational certificates for bounded contexts below the exact-return denominator gap. They are useful for rationalized phase policies, but they are not the irrational/nonperiodic RoPE Diophantine theorem.

`AIRA-T0054` proves the generated-gap bridge: the finite-context margin predicate is equivalent to checking the same lower bound for every positive gap in `List.range context`.

`AIRA-T0058` and `AIRA-T0059` prove the finite nearest-integer witness bridge. For a fixed real value, checking a lower bound against the integer floor and integer ceiling is equivalent to checking it against every integer. Applied to every generated positive gap, this makes `ropeTurnRatioFiniteMargin alpha margin context` equivalent to two floor/ceiling checks per gap. This is a bounded integer-turn search theorem, not yet a lower-bound theorem for a concrete irrational or nonperiodic RoPE turn ratio.

`AIRA-T0060` introduces the proof-carrying certificate interface: a `RopeTurnRatioFiniteMarginCertificate` whose payload is the nearest-integer witness predicate proves the corresponding `ropeTurnRatioFiniteMargin`. `AIRA-T0061` is the first named end-to-end finite-margin certificate: the rational/discretized turn ratio `1/4099` has margin `1/4099` over context `4096`. `AIRA-T0062` applies that certificate to rule out one-channel near-turn collisions below the certified margin. This is a complete theorem-backed certificate for a declared rational/discretized turn ratio, not a proof for the standard irrational `1 / (2π)` RoPE channel.

`AIRA-T0063` and `AIRA-T0064` introduce the interval-certificate route for genuine nonperiodic turn ratios. A single rational interval witness proves all integer-turn lower bounds for one generated gap when the enclosure lies inside one integer cell and stays at least `margin` from both endpoints. A finite table of those witnesses proves `ropeTurnRatioFiniteMargin alpha margin context`.

`AIRA-T0065` through `AIRA-T0067` are the first named standard-RoPE interval seed. For channel 0, where `alpha = 1 / (2π)`, Lean proves a context-6 margin `1/8` using the elementary bounds `3 < π <= 4`. `AIRA-T0068` through `AIRA-T0126` build the interval-certificate route through four-decimal, six-decimal, and 20-decimal rational `π` enclosures, the gap-`710` obstruction family, margin monotonicity, bank transfer, and reusable endpoint-band bridge. `AIRA-T0127` through `AIRA-T0132` certify the sharper 8k standard-channel seed and bracket at margin `1/104219`. `AIRA-T0133` through `AIRA-T0138` extend the same margin to context `16384`, add the D14 one-channel no-near-turn theorem, add D14 conditional bank transfers, and package the 16k bracket: margin `1/104219` is proved, while any margin at or above `1/104218` is impossible for context `16384`; margins strictly between those two rationals remain unresolved. This is theorem-backed standard-RoPE infrastructure, but still channel-0 based. It does not certify 128k or prove margins for every channel in a multi-channel standard-RoPE bank.

The Python sidecar still emits exact-rational interval plans for audit and future work. The four-decimal `π` plan through context `333`, the six-decimal `π` plan through context `710`, the 20-decimal context-4096 plans through margin `1/104219`, the 20-decimal context-8192 plans at margins `1/104220` and `1/104219`, and the 20-decimal context-16384 plan at margin `1/104219` have now been converted into Lean declarations. The sidecar also emits `standard_channel0_frontier_summary`: theorem-backed context `16384` at margin `1/104219`, candidate full-context rows at `32768` and `65536`, and first uncovered gap `103993` for the larger request. The frontier rows are deterministic source data only until matching declarations compile and manifest ids are marked proved.

## Local Mathlib Anchors

The following names exist in the local mathlib checkout and look relevant.

`Mathlib/NumberTheory/DiophantineApproximation/Basic.lean`:

- `Real.exists_int_int_abs_mul_sub_le`
- `Real.exists_nat_abs_mul_sub_round_le`
- `Real.exists_rat_abs_sub_le_and_den_le`
- `Real.infinite_rat_abs_sub_lt_one_div_den_sq_of_irrational`
- `Real.exists_rat_eq_convergent`

`Mathlib/NumberTheory/DiophantineApproximation/ContinuedFractions.lean`:

- `Real.exists_convs_eq_rat`

`Mathlib/Algebra/ContinuedFractions/Computation/Approximations.lean`:

- `GenContFract.abs_sub_convs_le`

`Mathlib/Algebra/ContinuedFractions/Computation/ApproximationCorollaries.lean`:

- `GenContFract.of_convergence_epsilon`
- `GenContFract.of_convergence`

The important warning is `Real.infinite_rat_abs_sub_lt_one_div_den_sq_of_irrational`: for irrational turn ratios, there is no global positive margin across all gaps. Any useful RoPE certifier theorem must be finite-context, conditional, or tied to a bounded search/convergent certificate.

## Honest Route

1. Normalize to the turn ratio `alpha = frequency / fullTurn` with `AIRA-T0041`.
2. Use `ropeTurnRatioFiniteMargin alpha margin L` as the finite-context nearest-integer margin over gaps `1 <= gap < L`.
3. Use continued fractions to restrict near-turn candidates to convergent denominators or an explicitly bounded set of checks.
4. Prove and compute a finite-context certificate for each channel.
5. Use `AIRA-T0043` to lift a channel-wise finite-context lower bound to a bank-level no-near-turn theorem.
6. Use `AIRA-T0044` and `AIRA-T0045` to reuse a larger certified horizon for smaller requested contexts without rerunning the formal transfer argument.
7. Use `AIRA-T0047` to report a conservative smaller margin from a stronger certified lower bound.
8. Use `AIRA-T0050` when both the requested context and advertised margin are smaller than the certified channel certificate.
9. Use `AIRA-T0053` to reject integer turn-ratio channels as positive finite-margin witnesses once the unit gap is in scope.
10. Use `AIRA-T0055` to reject natural rational turn-ratio channels as positive finite-margin witnesses once their denominator gap is in scope.
11. Use `AIRA-T0056` to certify reduced natural rational turn ratios with margin `1 / denominator` when the inspected context stays at or below the denominator.
12. Use `AIRA-T0057` for the exact reduced-rational boundary: the `1 / denominator` certificate is available exactly up to the denominator horizon.
13. Use `AIRA-T0054` to connect generated gap lists to the abstract finite-context margin predicate.
14. Use `AIRA-T0058` and `AIRA-T0059` to reduce the integer-turn obligation for each generated gap to the floor and ceiling witnesses of `gap * alpha`.
15. Use `AIRA-T0060` to package a finite nearest-integer witness payload as a proof-carrying certificate.
16. Use `AIRA-T0061` and `AIRA-T0062` as the first fully proved rational/discretized named preset: `1/4099`, context `4096`, margin `1/4099`, and no near-turn collision below that margin.
17. Use `AIRA-T0063` and `AIRA-T0064` to turn exact rational interval witness tables into finite-context margin proofs.
18. Use `AIRA-T0065` through `AIRA-T0067` as the first standard-RoPE seed: channel 0, `alpha = 1 / (2π)`, context `6`, margin `1/8`, no near-turn below that margin.
19. Use `AIRA-T0068` through `AIRA-T0070` as the strengthened standard-RoPE seed: channel 0, `alpha = 1 / (2π)`, context `7`, margin `1/32`, no near-turn below that margin.
20. Use `AIRA-T0071` through `AIRA-T0073` as the next strengthened standard-RoPE seed: channel 0, `alpha = 1 / (2π)`, context `8`, margin `1/32`, with gap `7` certified in integer cell `1`.
21. Use `AIRA-T0074` through `AIRA-T0076` as the larger standard-RoPE seed: channel 0, `alpha = 1 / (2π)`, context `19`, margin `1/32`, with gaps through `18` split across integer cells `0`, `1`, and `2`.
22. Use `AIRA-T0077` and `AIRA-T0078` to lower advertised interval-certificate margins without rebuilding already-certified gaps.
23. Use `AIRA-T0079` through `AIRA-T0081` as the context-44 standard-RoPE seed: channel 0, `alpha = 1 / (2π)`, context `44`, margin `1/64`, with gaps through `43` split across integer cells `0` through `6`.
24. Use `AIRA-T0082` and `AIRA-T0083` as the four-decimal rational enclosure for standard channel 0.
25. Use `AIRA-T0084` through `AIRA-T0086` as the context-57 standard-RoPE seed: channel 0, `alpha = 1 / (2π)`, margin `1/512`, with gaps `44` through `56` split across integer cells `7` and `8`.
26. Use `AIRA-T0087` through `AIRA-T0089` as the context-333 standard-channel seed: channel 0, `alpha = 1 / (2π)`, margin `1/512`, with generated d4 bands covering gaps `1` through `332` in cells `0` through `52`.
27. Use `AIRA-T0090` through `AIRA-T0094` as the context-710 standard-channel seed: channel 0, `alpha = 1 / (2π)`, context `710`, margin `1/1024`, with generated d6 bands covering gaps `1` through `709` in cells `0` through `112`.
28. Use `AIRA-T0095` and `AIRA-T0096` as the stop certificate for that exact margin: gap `710` is within margin `1/1024` of integer turn `113`, so context `711` and beyond cannot keep the same lower bound.
29. Use `AIRA-T0097` through `AIRA-T0101` as the conservative context-4096 standard-channel seed: channel 0, `alpha = 1 / (2π)`, margin `1/131072`, with generated d20 bands covering gaps `1` through `4095` in cells `0` through `651`.
30. Use `AIRA-T0102` as the conditional bank-level transfer when the finite real-phase bank contains the standard channel-0 angular frequency and the requested context/margin are below the D9 seed.
31. Use `AIRA-T0103` and `AIRA-T0104` as the sharper D9 margin stop: gap `710` is already within `1/65536` of integer turn `113`, so the context-4096 seed cannot simply double its advertised margin.
32. Use `AIRA-T0105` through `AIRA-T0108` as the D10 standard-channel seed: channel 0, `alpha = 1 / (2π)`, context `4096`, margin `1/105000`, with the same generated d20 bands and a D10 bank-level transfer.
33. Use `AIRA-T0109` and `AIRA-T0110` as the D10 nearby margin stop: gap `710` is already within `1/104000` of integer turn `113`, so the D10 seed cannot simply raise its advertised margin to that value.
34. Use `AIRA-T0111` through `AIRA-T0114` as the sharp 4k standard-channel seed: channel 0, `alpha = 1 / (2π)`, context `4096`, margin `1/104219`, with the same generated d20 bands and a D11 bank-level transfer.
35. Use `AIRA-T0115` and `AIRA-T0116` as the adjacent D11 margin stop: gap `710` is already within `1/104218` of integer turn `113`, so the current seed cannot simply raise its advertised margin to that value.
36. Use `AIRA-T0117` when the real-phase bank is explicitly represented as standard channel 0 followed by extra frequencies, eliminating a manual membership premise for that common bank shape.
37. Use `AIRA-T0118` and `AIRA-T0119` as the 4k engineering-facing bracket: context `4096`, proved margin `1/104219`, and no possible advertised margin at or above `1/104218`.
38. Use `AIRA-T0120` through `AIRA-T0122` as the longer 8k standard-channel seed: channel 0, `alpha = 1 / (2π)`, context `8192`, margin `1/104220`, with the same generated d20 band method.
39. Use `AIRA-T0123` and `AIRA-T0124` as the D12 bank-transfer bridge: a bank containing standard channel 0, or whose first channel is standard channel 0, inherits the no-near-turn consequence below any downgraded requested margin and context inside the D12 seed.
40. Use `AIRA-T0125` as the 8k margin bracket: the D12 seed proves margin `1/104220`, while the existing gap-`710` obstruction rules out every advertised margin at or above `1/104218`.
41. Use `AIRA-T0126` to compress future generated interval certificates: prove the band endpoints stay inside one integer cell, then Lean fills in every intermediate gap by monotonicity.
42. Use `AIRA-T0127` through `AIRA-T0132` as the sharper 8k standard-channel seed, one-channel consequence, D13 bank bridge, and 8k bracket at margin `1/104219`.
43. Use `AIRA-T0133` through `AIRA-T0138` as the 16k standard-channel seed, one-channel consequence, D14 bank bridge, and 16k bracket at margin `1/104219`.
44. Treat the Python 32k and 64k interval plans as proof-frontier source data, not proved theorem ids.
45. Scale from one channel to broader channel-wise/full-bank statements, or add sharper generated/continued-fraction machinery for larger contexts.

## Guardrails

- A numerical scan is not a proof.
- Dirichlet-style results give close returns or upper bounds; they do not by themselves prove a margin lower bound.
- An irrational turn ratio does not have a global positive no-return margin.
- An integer turn ratio has zero finite-context margin once adjacent positions are in scope.
- A natural rational turn ratio has zero finite-context margin once its denominator gap is in scope.
- A reduced natural rational turn ratio has a positive `1 / denominator` finite-context margin only before that denominator gap enters scope.
- A generated gap list only handles the finite `gap` domain; it does not by itself discharge the integer-turn lower-bound obligation.
- The floor/ceiling witness bridge discharges the infinite integer-turn quantifier for each fixed gap, but it does not prove that a concrete irrational or nonperiodic RoPE turn ratio has a positive lower bound.
- The `1/4099` preset certificate is theorem-backed, but it is a rational/discretized turn-ratio certificate, not a standard irrational RoPE certificate.
- The longest current standard channel-0 interval seed is theorem-backed for context 16384 only; the earlier `1/1024` margin is theorem-blocked beyond gap 710, the doubled D9 margin `1/65536` is theorem-blocked for any context containing gap 710, the nearby D10 margin `1/104000` is theorem-blocked at that gap, and the adjacent D11 margin `1/104218` plus every larger advertised margin is theorem-blocked there too. The 32k and 64k planner rows are not proofs until a compressed Lean proof route is compiled.
- Candidate interval plans from Python are planning data, not formal proof unless the plan explicitly cites matching compiled Lean declarations and manifest ids marked proved.
- A full standard real RoPE bank certificate needs channel-wise finite-context lower bounds before the Living Book or certifier can mark the ordinary real-phase scan as formally certified.
