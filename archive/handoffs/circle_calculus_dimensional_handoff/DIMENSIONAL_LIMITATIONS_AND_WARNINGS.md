# Dimensional Limitations and Warnings

## 1. Sphere notation confusion

Use topological convention:

```text
S^0 = two points
S^1 = circle
S^2 = ordinary sphere surface
S^3 = 3-sphere / 4D hypersphere
```

Do not call S^3 a 4-sphere. It is the sphere embedded in 4D, but its surface dimension is 3.

## 2. C1 is not S0

```text
C_1 = one-node degenerate circle/address object
S^0 = two-point opposition sphere
```

These must remain separate dictionary entries.

## 3. Cn × Cm is not a sphere

```text
C_n × C_m
```

has two cyclic directions and is torus-like.

A finite sphere grid requires pole collapse.

## 4. S2 is not a group like S1 or S3

S¹ has unit complex multiplication.

S³ has unit quaternion multiplication.

S² does not have a comparable natural pointwise multiplication structure.

## 5. S3 is not globally S2 × S1

The Hopf fibration can be locally product-like, but the global structure is twisted.

## 6. S4-S6 should not be skipped geometrically

S7 is the next major algebraic jackpot after S3, but S4/S5/S6 still belong in the geometric/topological ladder.

## 7. S6 complex-structure claims are delicate

S6 has important almost-complex/octonionic geometry, but do not rely on claims resolving integrable complex structures unless the project explicitly formalizes accepted foundations.

## 8. Unit octonions are not a group

Octonions are nonassociative.

Therefore unit octonions are not a group under ordinary multiplication.

Use caution with group-theoretic APIs and language.

## 9. Higher-dimensional projections are explanatory only

Slices, projections, stereographic pictures, and Hopf visuals are explanations, not proofs.

Every proof must compile to Lean or be explicitly labeled exploratory.

## 10. Do not let future concepts contaminate S1

The lower-dimensional core must remain minimal and reliable.
