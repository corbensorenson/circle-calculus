import Circle.Generative.SeedRule

/-!
This sidecar imports the Lean source trail for the seed-rule provenance paper.
The checked declarations live in `Circle.Generative.SeedRule`; Python fixtures
remain executable references and do not prove minimality or compression
optimality.
-/

#check Circle.Generative.finiteCircleGenerator_regenerates_nodes
#check Circle.Generative.coilOrbitGenerator_regenerates_orbit
#check Circle.Generative.orbitDecompositionGenerator_regenerates_orbits
#check Circle.Generative.orbitDecompositionGenerator_generatedOrbits_length
#check Circle.Generative.orbitDecompositionGenerator_generatedOrbitFor_length
#check Circle.Generative.orbitDecompositionGenerator_orbitCount_mul_period
#check Circle.Generative.orbitDecompositionGenerator_orbitCount_eq_orbitClassCount
#check Circle.Generative.proofGlyphGenerator_regenerates_certificate
#check Circle.Generative.generatorComparison_requires_exact_regeneration
