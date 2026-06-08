# Circle Calculus Generative 1: Seed-Rule Provenance

Status: draft with a Lean-proved finite regeneration spine plus exploratory Python comparison fixtures.

## Aim

This paper starts the generative-structure lane. The idea is simple: sometimes the most useful representation of an object is not the finished object but a small seed, a rule set, an iteration schedule, a closure condition, and a certificate that the object can be regenerated.

The ordinary baseline is value-only storage:

```text
object = all nodes, all orbit elements, all diagram fields
```

The Circle Calculus version records a construction:

```text
seed + rules + schedule + closure condition
  -> generated object
  -> theorem ids
  -> dictionary ids
  -> source-linked regeneration check
```

This is not a universal compression claim. It is a provenance interface. Some objects become shorter and clearer as seed-plus-rules records. Small objects can become longer because the provenance metadata has overhead.

## Source Trail

The sidecar registered in the paper manifest is:

```text
sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE
```

The Lean sidecar is:

```text
sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/lean/PaperGen01.lean
```

The checked finite seed declarations live in:

```text
Circle/Generative/SeedRule.lean
```

The Python examples are:

```text
sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/python/test_seed_rule_provenance_examples.py
```

The proof status boundary is strict: Lean declarations determine formal theorem status. Python examples check exact regeneration and comparison behavior; they are not formal proofs and do not establish optimality.

## Dictionary Vocabulary

- `COMMON-0064`: seed-rule provenance.
- `COMMON-0065`: generator comparison fixture.
- `COMMON-0066`: regenerative certificate.
- `COMMON-0033`: proof glyph certificate.

The paper links back to finite circles, coils, orbit decompositions, and proof-carrying glyphs. It should eventually feed the Living Book so generated diagrams expose their seed, rules, theorem ids, dictionary ids, and status badges.

## Theorem Spine

- `GEN-T0001`: `Circle.Generative.finiteCircleGenerator_regenerates_nodes`, a finite circle generator regenerates the listed nodes of `C_n`.
- `GEN-T0002`: `Circle.Generative.coilOrbitGenerator_regenerates_orbit`, a coil generator regenerates the period-indexed stride orbit schedule from `n`, `stride`, and `start`.
- `GEN-T0003`: `Circle.Generative.orbitDecompositionGenerator_regenerates_orbits`, an orbit-decomposition generator regenerates its representative-indexed finite stride-orbit schedules.
- `GEN-T0004`: `Circle.Generative.proofGlyphGenerator_regenerates_certificate`, a proof-glyph generator regenerates the theorem/glyph/Lean-name record.
- `GEN-T0005`: `Circle.Generative.generatorComparison_requires_exact_regeneration`, generator comparison checks exact regeneration before reporting length comparison.
- `GEN-T0006`: `Circle.Generative.orbitDecompositionGenerator_generatedOrbits_length`, the representative-indexed orbit-decomposition generator produces `gcd(n,stride)` orbit schedules.
- `GEN-T0007`: `Circle.Generative.orbitDecompositionGenerator_generatedOrbitFor_length`, each generated representative orbit schedule has length equal to the finite coil period.
- `GEN-T0008`: `Circle.Generative.orbitDecompositionGenerator_orbitCount_mul_period`, for `n != 0`, representative count times generated orbit period equals the circle size.
- `GEN-T0009`: `Circle.Generative.orbitDecompositionGenerator_orbitCount_eq_orbitClassCount`, for `n != 0`, the generator's representative count agrees with the formal stride-orbit class count.
- `GEN-T0010`: `Circle.Generative.orbitDecompositionGenerator_modRepresentative_lt_orbitCount`, a modulo representative is inside the orbit-decomposition generator's representative range when the range is positive.
- `GEN-T0011`: `Circle.Generative.orbitDecompositionGenerator_modRepresentative_covers`, every natural node is in the same finite stride-orbit class as its modulo-gcd representative.
- `GEN-T0012`: `Circle.Generative.orbitDecompositionGenerator_representatives_sameOrbit_iff_eq`, two canonical finite representatives are in the same stride-orbit class exactly when the representatives are equal.
- `GEN-T0013`: `Circle.Generative.orbitDecompositionGenerator_distinct_representatives_disjoint`, distinct canonical finite representatives are disjoint at the stride-orbit class level.
- `GEN-T0014`: `Circle.Generative.generatorComparison_self_exact`, a generator comparison from an artifact to itself has exact regeneration.
- `GEN-T0015`: `Circle.Generative.generatorComparison_exact_regeneration_symm`, exact regeneration is symmetric for generator comparison records.
- `GEN-T0016`: `Circle.Generative.generatorComparison_exact_regeneration_trans`, exact regeneration is transitive across generator comparison records.
- `GEN-T0017`: `Circle.Generative.generatorComparison_exact_regeneration_iff_fields_eq`, exact regeneration for a constructed comparison is equivalent to equality of its regenerated and generated fields.
- `GEN-T0018`: `Circle.Generative.generatorComparison_exact_regeneration_fields_eq`, an exact-regeneration witness for a constructed comparison gives equality of those fields.
- `GEN-T0019`: `Circle.Generative.generatorComparison_not_exact_of_ne`, unequal regenerated and generated values cannot pass the exact-regeneration check.
- `GEN-T0020`: `Circle.Generative.finiteCircleGenerator_generatedNodes_length`, a finite-circle seed-rule record generates exactly `n` node entries.
- `GEN-T0021`: `Circle.Generative.coilOrbitGenerator_generatedOrbit_length`, a coil seed-rule record generates an orbit schedule whose length is the formal finite coil period.
- `GEN-T0022`: `Circle.Generative.emptyBoundedGeneratorSearch_candidateCount`, an empty declared finite generator search space has zero candidate records.
- `GEN-T0023`: `Circle.Generative.emptyBoundedGeneratorSearch_exactCandidateCount`, an empty declared finite generator search space has zero exact-regeneration candidates.
- `GEN-T0024`: `Circle.Generative.emptyBoundedGeneratorSearch_bestExact_none`, an empty declared finite generator search space has no best exact-regeneration candidate.
- `GEN-T0025`: `Circle.Generative.boundedGeneratorSearch_bestExact_mem_exactCandidates`, any returned best exact candidate belongs to the declared exact-candidate list.
- `GEN-T0026`: `Circle.Generative.boundedGeneratorSearch_bestExact_mem_candidates`, any returned best exact candidate belongs to the declared finite candidate search space.
- `GEN-T0027`: `Circle.Generative.boundedGeneratorSearch_bestExact_exact`, any returned best exact candidate satisfies the exact-regeneration predicate.
- `GEN-T0028`: `Circle.Generative.boundedGeneratorSearch_bestExact_none_iff_exactCandidates_empty`, no best exact candidate is returned exactly when the declared exact-candidate list is empty.
- `GEN-T0029`: `Circle.Generative.boundedGeneratorSearch_bestExact_none_iff_exactCandidateCount_zero`, no best exact candidate is returned exactly when the exact-candidate count is zero.
- `GEN-T0030`: `Circle.Generative.boundedGeneratorSearch_bestExact_some_exactCandidateCount_pos`, any returned best exact candidate implies a positive exact-candidate count.

`GEN-T0001` through `GEN-T0030` are Lean-proved finite seeds in `Circle.Generative.SeedRule`.
`GEN-T0003` proves exact regeneration of the declared representative-indexed list model. `GEN-T0006` through `GEN-T0013` strengthen that model with count, period, coverage, formal orbit-class agreement, canonical representative coverage, and representative disjointness facts. `GEN-T0014` through `GEN-T0019` make exact regeneration reusable as a reflexive, symmetric, transitive, and field-equality-gated relation for constructed generator comparisons. `GEN-T0020` and `GEN-T0021` add direct generated-list length certificates for finite-circle nodes and single coil-orbit schedules. `GEN-T0022` through `GEN-T0024` prove the empty declared-search boundary: zero candidates, zero exact candidates, and no best exact candidate. `GEN-T0025` through `GEN-T0027` prove the nonempty soundness boundary for any returned best exact candidate: it comes from the declared exact list, it comes from the declared finite candidate list, and it is exact. `GEN-T0028` through `GEN-T0030` connect best-exact absence or presence to exact-candidate emptiness and count gates. They do not prove that the list is an optimal or minimal compression.

## Seed-Rule Record

The Python fixture stores:

```text
artifact_id
seed
rules
iteration_schedule
closure_condition
generated_object
theorem_ids
dictionary_ids
note
```

The fixture currently supports six artifacts:

```text
finite_circle
finite_circle_diagram
physics_loop_diagram
coil_orbit
orbit_decomposition
proof_glyph
```

Each record regenerates its object deterministically. The finite-circle diagram generator returns node labels and successor edges from the same `n` seed, theorem ids, and dictionary ids as the node generator. The physics-loop diagram generator returns a finite square plaquette diagram with normalized link phases, closed-loop status, holonomy, physics theorem ids, and dictionary ids. A comparison fixture serializes the regenerated explicit object and the seed-rule record, then reports whether the generator description is shorter. Exact regeneration is checked before any length result is trusted, and the Lean comparison facts now expose the exact check as equality of the regenerated/generated fields for constructed comparison records.

The Python sidecar also includes a bounded generator-search fixture. It ranks only a declared finite candidate list, reports how many candidates regenerate exactly, and separates the shortest exact candidate from the shortest exact candidate that is also shorter than explicit storage. The empty-search fixture records the zero-candidate boundary explicitly. The best-candidate soundness theorems record the nonempty boundary: if the bounded search returns a best exact candidate, that candidate is exact, comes from the declared finite search space, and has a positive exact-candidate count. If no best exact candidate exists, the declared exact-candidate list and count are empty. This is a scoped search report, not a proof of global minimality.

The Living Book page for generative structures now includes a static `seed_rule_diagram_generator` widget. It renders the finite-circle and finite physics-loop diagram records with visible seeds, rules, theorem-status badges, and dictionary links. The widget is an explanation layer; its diagram output is not a proof, and its description-length display is not a minimality theorem.

## Positive And Negative Cases

The large finite-circle case gives a positive example: listing every node of `C_128` is longer than storing the seed and rule record. The tiny circle case gives a negative example: a single-node circle is shorter as an explicit object because the provenance record has fixed metadata overhead.

That negative case matters. It prevents the project from treating "generator" as a magic word. Generator records are useful when they improve explanation, reconstruction, or proof linkage, not because every generated description is automatically smaller.

## Circle Calculus Framing

Circle Calculus already treats coils as generated motion:

```text
start node
  -> stride rule
  -> repeated rotation
  -> closed orbit
```

Seed-rule provenance turns that construction into a first-class object. It can carry theorem ids, dictionary ids, source links, proof-glyph metadata, and regeneration tests. The same idea can later support generative diagrams in the Living Book: readers should be able to see the seed and rules that produced a diagram rather than only the finished image.

## Limits

This paper does not prove Kolmogorov complexity results, optimal compression, universal generative modeling, or that smaller descriptions are always better. It gives a finite, auditable interface for exact regeneration and provenance.

The next formal step is to extend the generated-diagram contract toward orbit-family and proof-glyph records, while keeping compression-minimality claims out of scope until a precise search space exists. Bounded Python searches may suggest candidates, but only Lean-backed finite statements should be promoted to theorem status.
