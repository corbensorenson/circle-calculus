# Dimensional Paper Roadmap

## Current active volume: S¹ Circle Core

S¹ remains the active foundation.

### S1.1 — Finite Circles, Rotations, and Coils

Formalizes:

- finite cyclic address spaces C_n,
- nodes,
- rotations,
- coils/orbits,
- closure,
- period,
- prime full-coil behavior.

Do not modify this paper until its Lean theorem dependencies are green.

### S1.2 — Winding, Lifted Circles, and Natural Numbers

Formalizes:

- winding/residue representation,
- successor as unit rotation with carry,
- addition as path concatenation,
- natural-number arithmetic.

### S1.3 — Integers, Orientation, and Reversible Motion

Formalizes:

- clockwise/counterclockwise orientation,
- signed winding,
- integer addition and inverses.

### S1.4 — Factors, Scaling, and Prime Coils

Formalizes:

- multiplication as repeated rotation/scaling,
- invertibility iff coprime,
- prime rings as full-cycle systems.

---

## S⁰ Backfill: Opposition and Sign

This is optional and should not block S¹.

### S0.1 — Two-Point Opposition

Purpose:

- distinguish S^0 from C_1,
- formalize sign/opposition,
- define boundary-of-interval intuition carefully.

Important distinction:

```text
C_1 = one-node point-circle / degenerate address object
S^0 = two-point sphere / opposition pair
```

This prevents confusion when moving up the topological sphere ladder.

---

## S² Volume: Sphere Calculus

S² is the first genuine surface layer.

### S2.1 — Suspended Circles and the First Finite Sphere

Core construction:

```text
SuspC(n) = suspension of C_n
```

For n >= 3:

```text
V = n + 2
E = 3n
F = 2n
χ = V - E + F = 2
```

Main result:

```text
The suspension of a finite circle has Euler characteristic 2.
```

This is the S² analog of the S¹ period theorem: small, exact, visual, and foundational.

### S2.2 — Sphere Grids, Latitude Rings, and Pole Collapse

Core construction:

```text
SphereGrid(n,r) = {N,S} ∪ {(j,i) | 1 ≤ j ≤ r, i ∈ C_n}
```

For n >= 3 and r >= 1:

```text
V = nr + 2
E = n(2r + 1)
F = n(r + 1)
χ = 2
```

Main results:

- every non-pole latitude ring is C_n-like,
- longitude rotation fixes poles,
- latitude rotation period is n / gcd(n,k),
- longitude is undefined at poles.

### S2.3 — Antipodes, Axes, Surface Closure, and Antinodes

This is a later S² paper.

It should introduce:

- antipodal map,
- axis as antipodal pair,
- meridians,
- great-circle roadmap,
- spherical antinodes,
- surface closure.

Do not force continuous geometry too early.

---

## S³ Volume: Hypersphere, Quaternions, and Hopf Coils

S³ is the next major algebraic jump.

### S3.1 — Finite 3-Spheres by Suspending Spheres

Core construction:

```text
Susp(K)
```

If K has cell counts:

```text
V, E, F
```

then Susp(K) has:

```text
V' = V + 2
E' = E + 2V
F' = F + 2E
T' = 2F
χ' = V' - E' + F' - T'
```

If χ(K)=2, then:

```text
χ(Susp(K)) = 0
```

For K = SuspC(n):

```text
V' = n + 4
E' = 5n + 4
F' = 8n
T' = 4n
χ' = 0
```

### S3.2 — Quaternion Coils and Unit-Quaternion Hypersphere

Core idea:

```text
S^3 = unit quaternions
```

Formal goals:

- define or import quaternions,
- norm,
- conjugate,
- multiplication,
- unit quaternions,
- closure under multiplication,
- inverse via conjugate,
- noncommutativity examples.

Important:

```text
S¹: phase matters
S³: order matters
```

S³ is not merely a visual 4D sphere. It is the first higher sphere with a powerful native multiplication.

### S3.3 — Hopf Coils: S¹ → S³ → S²

Core idea:

```text
S¹ fiber → S³ total space → S² base
```

Hopf map model:

```text
(z0,z1) ∈ C²
|z0|² + |z1|² = 1

h(z0,z1) =
(
  2 Re(z0 * conj(z1)),
  2 Im(z0 * conj(z1)),
  |z0|² - |z1|²
)
```

Main staged targets:

- h maps S³ points to S²,
- simultaneous phase rotation preserves h,
- each visible S² point corresponds to a hidden S¹ fiber,
- do not claim S³ is globally S² × S¹.

This paper should begin with Python numeric tests and only move to Lean proofs when supporting real/complex analysis infrastructure is ready.

### S3.4 — Spin, Double Covers, and Rotation Quotients

Later paper.

Core target:

```text
q and -q represent the same 3D rotation
```

This belongs after quaternion basics, not before.

---

## S⁴-S⁶ Volume: Geometric Higher-Sphere Bridge

These dimensions should not be skipped geometrically.

They are less immediately magical algebraically than S³ and S⁷, but they are part of the dimensional ladder.

### S456.1 — General Suspension and Euler Parity

Main theorem:

```text
χ(Susp(K)) = 2 - χ(K)
```

Iterated sphere result:

```text
χ(S^d) = 1 + (-1)^d
```

for the finite suspension-count model.

This paper can cover S⁴, S⁵, and S⁶ as geometric/topological dimensions.

### S4.1 — S⁴ as Base of Quaternionic Hopf Structure

S⁴ matters because the quaternionic Hopf fibration has base S⁴:

```text
S³ → S⁷ → S⁴
```

Do not attempt full quaternionic Hopf formalization until S³ quaternion calculus is solid.

### S5.1 — S⁵ as Complex Projective Bridge

S⁵ matters as a complex higher-sphere layer, especially through circle bundles over complex projective space.

Keep this paper mostly roadmap/specification unless formal projective geometry is available.

### S6.1 — S⁶ as Octonion Shadow and Warning Layer

S⁶ is related to octonionic geometry and almost complex structures.

Hard rule:

- Do not claim a resolved integrable complex structure on S⁶.
- Treat complex-structure claims as warnings/speculative unless formalized from accepted foundations.

S⁶ is a bridge to S⁷, not a shortcut.

---

## S⁷ Volume: Octonionic and Quaternionic-Hopf Layer

S⁷ is the next major algebraic jackpot after S³.

### S7.1 — Topological 7-Sphere by Iterated Suspension

Formalizes S⁷ first as a finite combinatorial sphere by iterated suspension.

Main result:

```text
χ(S⁷) = 0
```

This should be proved before octonion algebra enters.

### S7.2 — Quaternionic Hopf Fibration: S³ → S⁷ → S⁴

Core idea:

```text
fiber S³
total S⁷
base S⁴
```

This extends the Hopf-coil idea from hidden circle phase to hidden quaternionic phase.

This is advanced. Start with roadmap, Python models, and theorem statements.

### S7.3 — Octonionic Units and Nonassociative Coils

Core idea:

```text
S⁷ = unit octonions
```

Important:

- octonions are noncommutative,
- octonions are nonassociative,
- unit octonions are not a group,
- operation order and grouping both matter.

Project-language escalation:

```text
S¹: phase matters
S³: order matters
S⁷: order and grouping matter
```

Formalization should be cautious. If mathlib does not provide octonions, implement a minimal custom exploratory model first and do not mark core theorems as proved until the formalization is robust.

---

## Future S¹⁵ Volume

Do not implement early.

S¹⁵ appears in the octonionic Hopf fibration:

```text
S⁷ → S¹⁵ → S⁸
```

This belongs after S⁷ has stable topological and algebraic foundations.
