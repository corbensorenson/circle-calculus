# Circle Methods And Extremal Combinatorics Program

Date: 2026-06-07

## Goal

The near-term mathematical goal is not to claim a new solution to an open Erdos problem. The goal is to make Circle Calculus credible to mathematicians by building a proof-carrying extremal-combinatorics program: compiled Lean theorem bridges, honest source trails, finite executable examples, and clear claim boundaries.

The current program has five lanes.

## Lane 1: Zero-Sum And Sumsets

- Paper: `papers/erdos/PAPER_ERDOS_01_ZERO_SUM_CIRCLES.md`
- Lean: `Circle/Erdos/EGZ.lean`, `Circle/Erdos/CauchyDavenport.lean`
- Theorems: `CC-T0062`, `CC-T0063`
- Point: `C_n = ZMod n`, so EGZ and Cauchy-Davenport are direct Circle-facing additive-combinatorics bridges.

This is the best first public claim: small, recognized, and formally checkable.

## Lane 2: Katona And Erdos-Ko-Rado

- Paper: `papers/erdos/PAPER_ERDOS_02_KATONA_EKR_CIRCLE_METHOD.md`
- Lean: `Circle/Erdos/KatonaEKR.lean`
- Theorems: `CC-T0064`, `CC-T0065`
- Point: the Katona circle method is the most literal "circle method" bridge: arrange finite sets around a circle, count prefix/interval events, and recover a classical extremal theorem.

This is the best excitement lane for explaining Circle Math to combinatorialists.

## Lane 3: Roth And Three-Term Progressions

- Paper: `papers/erdos/PAPER_ERDOS_03_ROTH_THREE_AP_CIRCLES.md`
- Lean: `Circle/Erdos/RothAP.lean`
- Theorems: `CC-T0066`, `CC-T0067`
- Point: Roth gives Circle Math a deep density/additive-combinatorics theorem without claiming open-problem progress.

This lane should grow cyclic AP definitions, density vocabulary, and transfer examples.

## Lane 4: Hales-Jewett And Ramsey Lines

- Paper: `papers/erdos/PAPER_ERDOS_04_HALES_JEWETT_RAMSEY_CIRCLES.md`
- Lean: `Circle/Erdos/RamseyHJ.lean`
- Theorems: `CC-T0068`, `CC-T0069`
- Point: Ramsey theory shows unavoidable structure in finite colorings. Circle Math can present this through word-cube lines, homothetic copies, and finite search fixtures.

This lane is strongest as an educational and visual bridge unless new formal cyclic-coloring theorems are added.

## Lane 5: Unit-Distance Circulant Graphs

- Paper: `papers/erdos/PAPER_ERDOS_05_UNIT_DISTANCE_CIRCULANT_GRAPHS.md`
- Lean: `Circle/Erdos/GraphLab.lean`
- Theorems: `CC-T0070`, `CC-T0071`, `CC-T0072`
- Point: circulant graphs are genuinely cyclic graph objects. They provide an honest graph-geometry starting point before attempting anything as hard as unit-distance or distinct-distance problems.

This lane should stay conservative: cycles, circulants, Cayley graphs, embeddings, and only then harder Euclidean geometry.

## What Counts As Progress

Progress means:

- a theorem id points to a compiled Lean declaration;
- the paper states the proof source and proof-status boundary;
- Python examples are executable support, not proof substitutes;
- the claim says exactly what was proved and what remains exploratory.

## Next Mathematical Bar

The next serious upgrade is not another broad survey. It is to prove one small Circle-native lemma in Lean that is not merely a wrapper:

- EGZ sharpness family over `C_n`;
- finite cyclic three-term AP witness equivalence;
- star-family sharpness for EKR examples;
- cycle/circulant graph edge equality as a project-native finite computation theorem.

Any of those would move Circle Math from "good proof-linked interface" toward "contributing useful local formalization."
