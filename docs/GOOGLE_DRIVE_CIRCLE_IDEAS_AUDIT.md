# Google Drive Circle / AI / Prime Ideas Audit

Date: 2026-06-21

This audit records the Drive search pass for circle, coil, vortex, antinode,
chord, resonance, prime, TreeLLM, RoPE, and AI-architecture ideas that can be
safely ported into the Lean project.  Treat this file as the single project
inbox for Drive-derived ideas: finite claims with precise semantics are ported
into Lean; implementation artifacts are recorded as configuration evidence; and
architecture, performance, metaphysics, and governance claims stay in backlog
until they have executable models or external evidence.

The current port keeps the formal slice finite and combinatorial: abstract
chord interleaving, antinode counts, prime-angle stride criteria, subcoil
counts, TreeLLM byte/anchor arithmetic, and rotary-attention config checks.

## Search Terms

- `circle`
- `coil`
- `coil graph`
- `full coil`
- `subcoil`
- `vortex`
- `antinode`
- `antinodes`
- `anti node`
- `antiNodeCount`
- `nodeConnections`
- `chord`
- `network chords`
- `prime angle`
- `star polygon`
- `standing wave`
- `resonance`
- `harmonic`
- `torus`
- `edCoin`
- `coil map`
- `temporal coil`
- `prime temporal`
- `abyss`
- `tuning generator`
- `circle math`
- `efficient prime`
- `prime engine`
- `primecoin`
- `prime window`
- `Circle AI`
- `TreeLLM`
- `semantic token`
- `root probabilities`
- `universal root lattice`
- `prime ring`
- `CoilLinear`
- `CoilRA`
- `MultiCoil`
- `RoPE`
- `rotary`
- `monkeyReplicator`
- `CoilMoECOT`
- `ORCP`
- `BBVCA`
- `proof of belief`
- `talos protocol`

## High-Value Sources

### vortex

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: contains the original Python sketches for coil objects, prime
  angles, normalized node connections, and antinode counting.
- Ported ideas:
  - endpoint-normalized chord crossings;
  - the old scan predicate reduces to endpoint interleaving;
  - prime-node path family count is `(n - 3) / 2`;
  - prime-node antinode counts match `n.choose 4` for the full diagonal chord
    network.
- Not ported yet:
  - nearest-prime-after-antinode-count searches are empirical;
  - coordinate geometry and inner/outer circle ratio code needs a separate,
    reviewed Euclidean model.

### some antinode data

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: table of prime node counts, unique paths, antinode counts,
  nearest-prime distances, and nearby primes.
- Ported ideas:
  - the first table rows are now Lean-checkable examples:
    `5 -> 5`, `7 -> 35`, `11 -> 330`, `13 -> 715`, `17 -> 2380`,
    `19 -> 3876`, `23 -> 8855`, `29 -> 23751`, `31 -> 31465`;
  - unique path counts for prime sizes are Lean-checkable examples:
    `5 -> 1`, `7 -> 2`, `11 -> 4`, `13 -> 5`, `17 -> 7`,
    `19 -> 8`, `23 -> 10`.
- Not ported yet:
  - the "near another prime" observation should stay an experiment until there
    is a precise theorem statement and evidence beyond the table.

### White paper on (ed)

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: defines coil graph networks, full/prime/composite coil networks,
  subcoil networks on factors, antinodes as intersection objects, and coil maps.
- Ported ideas:
  - finite prime-angle stride predicate;
  - subcoil count as the existing stride-orbit class count;
  - full chord network antinode count as `choose n 4`;
  - FCN/PCN/CCN stride classification as a finite partition;
  - midpoint spokes as excluded non-spoke strides;
  - factor subcoil copy counts, including the 18-node examples;
  - coil-map visible-node expansion, including `18 * 4 = 72` and fixed-width
    concrete blocks for each visible node.
- Not ported yet:
  - additive/multiplicative coil-network expression grammar;
  - tangent-circle and ratio claims, which require a Euclidean geometry track.

### Better explanation of monkeyReplicator / explination of replication idea for Jon

- Source: private Drive notes audited locally; raw URLs intentionally omitted
  from the public repository.
- Relevance: repeats and extends the coil-network vocabulary around FCN, PCN,
  CCN, subcoils, antinodes, coil maps, data entry/exit paths, additive and
  multiplicative coil arithmetic, RAID-like replication, and compression
  architecture.
- Ported ideas:
  - the finite FCN/PCN/CCN partition, prime-angle skip criteria, factor subcoil
    copy counts, and coil-map arithmetic are already covered by
    `Circle/Core/CoilNetwork.lean`;
  - the antinode interpretation as crossing chords is already represented by
    `Circle/Core/Antinode.lean`.
- Not ported yet:
  - the "coil 9 skip 1" data-entry path appears to use a 1-indexed path
    convention where skip 1 behaves like stride 2; this needs terminology
    reconciliation with the white-paper skip-to-stride definition before a Lean
    theorem is safe;
  - RAID/compression and adaptive-accuracy claims need executable semantics,
    not just vocabulary, before proofs can say anything precise.

### white paper for my primecoin

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: gives the clearest skip-based mining definition of a prime angle:
  for `n` nodes, skip `s` means stride `s + 1`; it is prime when the walk
  returns only after all `n` points.
- Ported ideas:
  - white-paper skip-to-stride map `skip + 1`;
  - pre-midpoint skip range, including skip `0` as the base angle;
  - white-paper prime-angle skip as `gcd n (skip + 1) = 1`;
  - the 12-node example: among skips `0..4`, exactly `0` and `4` are prime;
  - the 13-node example: all skips `0..5` are prime because 13 is prime.
- Not ported yet:
  - radian/degree mining schedule, next-angle selection, payout pools,
    challenge rules, and chain mechanics need a separate executable protocol
    model before they can have Lean proofs;
  - "calculate pi" and economics claims are not finite-circle theorems.

### Copy of treellm / treellm / treellm.txt

- Source: private Drive notes audited locally; raw URLs intentionally omitted
  from the public repository.
- Relevance: TreeLLM semantic-token and root-lattice specifications, including
  13 root questions, 32-byte initial token, 76-byte token, and 80-byte variant.
- Ported ideas:
  - `13` root questions is prime;
  - `13 * 24 = 312` path bits, byte-aligned as `39` bytes;
  - 76-byte token layout sum;
  - 80-byte token layout sum;
  - initial 14-bit path id plus 20 int8 residual dimensions fits inside a
    32-byte token;
  - v8 32-byte semantic vector field sum.
- Not ported:
  - claims of optimality, no future retraining, perfect memory, explainability,
    collision probabilities, and hardware throughput are architecture or
    benchmark claims, not Lean theorems yet;
  - the 13 root question meanings need an ontology model before semantic
    proofs are meaningful.

### high level moecot stuff

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: MoECOT ontology plus TreeLLM v8 / Omni-Lattice material:
  Seed Crystal, DKL tiers, sensory anchors, adaptive token caching,
  speculative traversal, recursive loop, and prime-ring / antinode-fusion
  language in the larger AI architecture.
- Ported ideas:
  - 128 semantic anchors with 16 reserved sensory anchors, leaving 112
    non-sensory anchors;
  - sensory-anchor reservation fits inside the total anchor budget;
  - DKL read path has 3 tiers;
  - speculative traversal span `3..5` is a nonempty numeric interval.
- Not ported:
  - O(1) updatability, hallucination reductions, phone/desktop throughput,
    federated-learning quality, and "prime-ring geometry" need either
    executable algorithms or benchmark artifacts;
  - MoECOT core/expert/router/skill governance concepts should become Lean
    only after a typed registry/route semantics exists.

### RoPE / rotary Drive training artifacts

- Source: private Drive artifacts audited locally; raw URLs intentionally
  omitted from the public repository.
- Relevance: MLX/PyTorch training scripts and logs with concrete rotary
  attention guardrails: model dimension divisible by head count, query heads
  divisible by KV heads, even head dimension, and bounded/even RoPE dimensions.
- Ported ideas:
  - `model_dim=512`, `heads=8`, `kv_heads=4`, `rope_dims=16` satisfies the
    finite shape checks;
  - the corresponding head dimension is `64`;
  - `rope_dims=0` defaults to full-head RoPE, also `64`.
- Not ported:
  - validation loss, throughput, compression, and training outcomes remain
    empirical logs;
  - full real-valued RoPE distinguishability is already tracked separately by
    `Circle/Applications/RoPECertifier.lean`.

### Circle Math — Efficient Prime Search (Codex Engineering Handoff)

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: title-level evidence for a prime-search handoff. The connector
  fetch returned no usable body text during this audit.
- Port status: no new Lean statements were taken from the body because the
  body was unavailable. Existing local proof surfaces already cover finite
  prime-horizon containment and next-prime search results in
  `Circle/Core/Horizon.lean`.

### God and consciousness

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: AI governance, ethics, dimensional hierarchy, and metaphysical
  system notes.
- Port status: not ported. Useful future work is a typed governance/protocol
  model if the claims are rewritten as finite rules. Metaphysical assertions
  are not Lean targets for this project without precise mathematical content.

### temporal coil architecture

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: recasts sequence models as prime temporal sets with directed edges
  and antinode-like computational hubs at intersections.
- Ported ideas:
  - prime-node uniqueness is backed by the existing `prime_full_coil` theorem
    and the new prime-angle wrapper;
  - prime temporal-window stride contract: every positive stride below a prime
    window is coprime to that window;
  - the progressive ladder examples `11`, `17`, and `29` are Lean-checked as
    prime;
  - the manifest stride set `1, 2, 3, 5, 8` is Lean-checked for window `29`;
  - "abyss" all-to-all arithmetic for `59` sets and `16,000` vocabulary nodes:
    endpoint tokens have `912,000` outgoing edges, interior tokens have
    `928,000`, and the network-wide pre-sparsity count is `875,520,000,000`.
- Future Lean targets:
  - executable finite graph masks for neighbor/current variants;
  - sparse top-k mask bounds after the full mask is defined as data.

### temporal_coil_research.md

- Source: private Drive artifact audited locally; raw URL intentionally omitted
  from the public repository.
- Relevance: records the manifest-driven temporal-coil A/B process, canonical
  variants, progressive prime ladder, and stride-set configuration.
- Ported ideas:
  - prime ladder and stride-set validation are represented in
    `Circle/Applications/TemporalCoil.lean`.
- Not ported:
  - benchmark deltas, winner frequency, reward shaping, collapse scoring, and
    model-quality interpretations are empirical runtime claims, not Lean
    theorems.

### coil_lag_lanes_for_moecotulp_2026-03-06.md

- Source: private Drive artifact audited locally; raw URL intentionally omitted
  from the public repository.
- Relevance: canonicalizes temporal-coil manifest fields: prime window,
  coprime stride family, CLF/PCTM/ACT decomposition, and anti-coil posture.
- Ported ideas:
  - the prime-window/coprime-stride contract is represented in
    `Circle/Applications/TemporalCoil.lean`.
- Not ported:
  - CLF/PCTM/ACT runtime semantics and anti-coil penalty/inhibition behavior
    need executable semantics before proof statements are meaningful.

### coil_v2_requirements_extracted.md / CoilMoECOT_Whitepaper_v2.0.docx

- Source: private Drive artifacts audited locally; raw URLs intentionally
  omitted from the public repository.
- Relevance: describes CoilMoECOT as a governed specialist lane with prime
  temporal sets, directed inter-set connectivity, optional abyss edges,
  antinode-style aggregation, trace/graph vocabulary, deterministic fail-closed
  integration, and benchmark/shadow deployment requirements.
- Ported ideas:
  - prime temporal windows and coprime stride sets are represented in
    `Circle/Applications/TemporalCoil.lean`;
  - A/B benchmark, routing, and fail-closed rules are recorded as architecture
    constraints, not mathematical theorems.
- Future Lean targets:
  - a typed configuration record proving the default temporal set count is
    prime and at least 3;
  - finite graph predicates for optional abyss edges and antinode-style
    aggregation once the runtime graph semantics are fixed.

### ORCP_MoECOT_Compression_Whitepaper_FINAL_v1.2.md

- Source: private Drive artifact audited locally; raw URL intentionally omitted
  from the public repository.
- Relevance: compression architecture note with coil-lag experts and a concrete
  prime-offset family `[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43,
  47, 53]`.
- Port status: not directly ported into Lean because the document is primarily
  an architecture/compression protocol. The prime-offset list is a good future
  configuration theorem once an ORCP/codec model exists.

### circle as representation for God

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: contains exploratory circle, chord, tangent, and interior-circle
  proof ideas.
- Port status: not directly ported. The useful formal direction is a later
  Euclidean geometry module with explicit hypotheses for chords, tangency, and
  circle intersections. The current project core deliberately models finite
  cyclic address spaces, not continuum geometry.

### tuning generator

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: acoustic resonance and physical design notes.
- Port status: not directly ported. Possible future target is finite phase
  bookkeeping for constructive/destructive interference; material and acoustic
  claims need external physics assumptions.

### agent_c_mlx_arch_03_coil_pctm17.txt

- Source: private Drive artifact audited locally; raw URL intentionally omitted
  from the public repository.
- Relevance: MLX architecture artifact with coil tap selection, coil activation
  pairs, and a local smoke run using `coil_prime_window=17`.
- Port status: not directly ported. The finite tap-selection algorithm could be
  formalized later, but the current file is mainly an implementation artifact
  plus empirical training log.

### stargate

- Source: private Drive note audited locally; raw URL intentionally omitted from
  the public repository.
- Relevance: vortex and torus language with an explicit revised caveat framing.
- Port status: not ported. Keep as speculative/analog-physics inspiration only;
  it is not a source for current finite-circle Lean proofs.

## Current Lean Port

New module:

- `Circle/Core/Antinode.lean`
- `Circle/Core/CoilNetwork.lean`
- `Circle/Applications/TemporalCoil.lean`
- `Circle/Applications/TreeLLM.lean`
- `Circle/Applications/AIConfig.lean`

New finite definitions:

- `Circle.chordCrosses`
- `Circle.oldScanCrosses`
- `Circle.nonSpokeForwardStride`
- `Circle.primeAngleStride`
- `Circle.primeChordPathCount`
- `Circle.fullChordNetworkAntinodeCount`
- `Circle.fullChordAntinodeCertificates`
- `Circle.subcoilCount`
- `Circle.fullCoilNetworkStride`
- `Circle.primeCoilNetworkStride`
- `Circle.compositeCoilNetworkStride`
- `Circle.spokeStride`
- `Circle.whitePaperSkipStride`
- `Circle.whitePaperForwardSkip`
- `Circle.whitePaperPrimeAngleSkip`
- `Circle.factorSubcoilExists`
- `Circle.factorSubcoilCopies`
- `Circle.coilMapTotalNodes`
- `Circle.coilMapBlockStart`
- `Circle.coilMapBlockEnd`
- `Circle.Applications.temporalCoilStride`
- `Circle.Applications.temporalAbyssEndpointNeighborCount`
- `Circle.Applications.temporalAbyssInteriorNeighborCount`
- `Circle.Applications.temporalAbyssEndpointNodeEdges`
- `Circle.Applications.temporalAbyssInteriorNodeEdges`
- `Circle.Applications.temporalAbyssTotalDirectedEdges`
- `Circle.Applications.treeLLMRootQuestionCount`
- `Circle.Applications.treeLLMPathIdBits`
- `Circle.Applications.treeLLMPathIdBytes`
- `Circle.Applications.treeLLM76TokenBytes`
- `Circle.Applications.treeLLM80TokenBytes`
- `Circle.Applications.treeLLMInitialPayloadBits`
- `Circle.Applications.treeLLMV8SemanticVectorBytes`
- `Circle.Applications.treeLLMTotalAnchorCount`
- `Circle.Applications.treeLLMSensoryAnchorCount`
- `Circle.Applications.treeLLMNonSensoryAnchorCount`
- `Circle.Applications.treeLLMDKLTierCount`
- `Circle.Applications.treeLLMSpeculativeHopMin`
- `Circle.Applications.treeLLMSpeculativeHopMax`
- `Circle.Applications.RotaryAttentionConfig`
- `Circle.Applications.rotaryAttentionHeadDim`
- `Circle.Applications.rotaryAttentionConfigWellFormed`
- `Circle.Applications.effectiveRotaryDims`

New proved declarations:

- `Circle.chordCrosses_endpoint_order`
- `Circle.chordCrosses_not_reverse`
- `Circle.oldScanCrosses_iff_chordCrosses_of_sorted`
- `Circle.primeAngleStride_fullCoil`
- `Circle.primeAngleStride_of_prime`
- `Circle.primeChordPathCount_eq`
- `Circle.primeChordPathCount_examples`
- `Circle.fullChordNetworkAntinodeCount_eq_choose`
- `Circle.fullChordAntinodeCertificates_card`
- `Circle.fullChordNetworkAntinodeCount_eq_certificate_card`
- `Circle.fullChordNetworkAntinodeCount_prime_examples`
- `Circle.subcoil_count_eq_gcd`
- `Circle.prime_subcoil_count_one`
- `Circle.primeCoilNetworkStride_full`
- `Circle.primeCoilNetworkStride_fullCoil`
- `Circle.compositeCoilNetworkStride_full`
- `Circle.compositeCoilNetworkStride_not_prime`
- `Circle.fullCoilNetworkStride_iff_prime_or_composite`
- `Circle.primeCircle_fullNetworkStride_is_prime`
- `Circle.spokeStride_not_nonSpokeForwardStride`
- `Circle.whitePaperPrimeAngleSkip_fullCoil`
- `Circle.whitePaperPrimeAngleSkip_of_prime`
- `Circle.whitePaperPrimeAngleSkips12_eq`
- `Circle.whitePaperPrimeAngleSkips13_eq`
- `Circle.whitePaperPrimeAngleSkips13_all_forward`
- `Circle.factorSubcoilCopies_mul`
- `Circle.factorSubcoilCopies_18_examples`
- `Circle.coilMapTotalNodes_18_4`
- `Circle.coilMapBlockWidth`
- `Circle.coilMapBlockStart_lt_blockEnd`
- `Circle.Applications.temporalCoilStride_of_prime`
- `Circle.Applications.temporalPrimeLadder_examples`
- `Circle.Applications.temporalStrideSet29_examples`
- `Circle.Applications.temporalAbyss59EndpointNodeEdges16000`
- `Circle.Applications.temporalAbyss59InteriorNodeEdges16000`
- `Circle.Applications.temporalAbyss59TotalDirectedEdges16000`
- `Circle.Applications.treeLLMRootQuestionCount_prime`
- `Circle.Applications.treeLLMPathIdBits_eq`
- `Circle.Applications.treeLLMPathIdBytes_eq`
- `Circle.Applications.treeLLMPathIdBits_byte_aligned`
- `Circle.Applications.treeLLM76TokenBytes_eq`
- `Circle.Applications.treeLLM80TokenBytes_eq`
- `Circle.Applications.treeLLMInitialPayloadBits_eq`
- `Circle.Applications.treeLLMInitialPayloadFits32Bytes`
- `Circle.Applications.treeLLMV8SemanticVectorBytes_eq`
- `Circle.Applications.treeLLMNonSensoryAnchorCount_eq`
- `Circle.Applications.treeLLMSensoryAnchorCapacity_le_total`
- `Circle.Applications.treeLLMDKLTierCount_eq`
- `Circle.Applications.treeLLMSpeculativeHopSpan_nonempty`
- `Circle.Applications.mlxRotaryConfig512_8_4_16_wellFormed`
- `Circle.Applications.mlxRotaryConfig512_8_4_16_headDim`
- `Circle.Applications.mlxRotaryConfig512_8_4_0_wellFormed`
- `Circle.Applications.mlxRotaryConfig512_8_4_0_effectiveFullHead`

## Follow-Up Proof Candidates

1. A real `Finset` model of diagonal chord networks, with an equivalence between
   increasing 4-tuples and crossing chord pairs.
2. An executable additive/multiplicative coil-expression grammar for examples
   like `(3x4)+(3x4)+(3x4)` and `4x9 = 36`.
3. A reconciled finite orbit theorem for the monkeyReplicator "coil 9 skip 1"
   path after its skip/indexing convention is aligned with the Primecoin
   white-paper convention.
4. A temporal coil graph module for explicit "abyss" masks, neighbor/current
   variants, and sparse top-k reductions.
5. A finite phase-alignment module for the tuning-generator resonance notes,
   limited to phase bookkeeping until physical assumptions are supplied.
6. A Euclidean geometry track for chord/tangent claims, only after the finite
   address-space model and continuum assumptions are separated.
7. A Primecoin protocol model for angle schedules, skip assignment, proof
   submission, challenge overturns, and payout weighting by antinode counts.
8. A TreeLLM lattice/token semantics model: root-question ontology, path
   traversal, collision semantics, and DKL tier precedence before any claims
   about updates, memory, or explainability are formalized.
9. A MoECOT registry/router semantics model for cores, experts, toolsets,
   skills, benchmarks, and promotion gates.
10. A finite MLX/RoPE architecture config library that imports real run manifests
   and proves shape guardrails for each named run.
11. ORCP/CoilMoECOT configuration theorems for prime-offset lists, default
    temporal-set counts, bounded active frontiers, and fail-closed routing after
    the architecture vocabulary is represented as finite data.
