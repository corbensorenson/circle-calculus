# RoPE Real-Phase Margin Notes

This note is a durable audit trail for the real-valued RoPE phase-margin theorem program. It records what is already proved, what mathlib infrastructure appears relevant, and what must not be claimed yet.

## Current Proved Bridge

The real-phase theorem spine currently runs from `AIRA-T0029` through `AIRA-T0033`, then `AIRA-T0037` through `AIRA-T0045`, plus `AIRA-T0047`, `AIRA-T0050`, and `AIRA-T0053`.

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

## Guardrails

- A numerical scan is not a proof.
- Dirichlet-style results give close returns or upper bounds; they do not by themselves prove a margin lower bound.
- An irrational turn ratio does not have a global positive no-return margin.
- An integer turn ratio has zero finite-context margin once adjacent positions are in scope.
- A full real RoPE bank certificate needs channel-wise finite-context lower bounds before the Living Book or certifier can mark the real-phase scan as formally certified.
