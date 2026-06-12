# Theorem Targets by Dimension

## Common theorem targets

### COMMON-T0001 — Euler characteristic of cell-count list

Define:

```text
χ(c_0, c_1, ..., c_d) = Σ_i (-1)^i c_i
```

Status: planned

### COMMON-T0002 — Suspension cell-count transform

For a finite cell-count model K with counts c_i:

```text
Susp(K)_0 = c_0 + 2
Susp(K)_k = c_k + 2c_{k-1} for 1 ≤ k ≤ d
Susp(K)_{d+1} = 2c_d
```

Status: planned

### COMMON-T0003 — Suspension Euler transform

```text
χ(Susp(K)) = 2 - χ(K)
```

Status: planned

---

## S0 targets

### S0-T0001 — S0 has two points

```text
|S0| = 2
```

### S0-T0002 — Antipodal map on S0 has order 2

```text
antipode(antipode(x)) = x
```

### S0-W0001 — C1 is not S0

Dictionary warning, not mathematical theorem.

---

## S1 targets

Keep the existing S¹ finite-circle theorem ids.

Minimum expected S¹ spine:

```text
rotation identity
rotation composition
rotation inverse
coil closure iff m*k ≡ 0 mod n
period = n / gcd(n,k)
prime full-coil behavior
scaling invertible iff coprime
winding/residue uniqueness
```

---

## S2 targets

### S2-T0001 — Suspended circle counts

For n ≥ 3:

```text
V = n + 2
E = 3n
F = 2n
```

### S2-T0002 — Suspended circle Euler characteristic

```text
χ(SuspC(n)) = 2
```

### S2-T0003 — SphereGrid counts

For n ≥ 3 and r ≥ 1:

```text
V = nr + 2
E = n(2r + 1)
F = n(r + 1)
```

### S2-T0004 — SphereGrid Euler characteristic

```text
χ(SphereGrid(n,r)) = 2
```

### S2-T0005 — Latitude ring is C_n-like

Every non-pole latitude ring is isomorphic to the finite circle C_n.

### S2-T0006 — Longitude rotation fixes poles

A latitude/longitude rotation acts on ring nodes but fixes N and S.

### S2-T0007 — Latitude coil period inherited from S1

For a fixed latitude ring:

```text
period = n / gcd(n,k)
```

### S2-W0001 — Torus confusion warning

```text
C_n × C_m is torus-like, not a sphere.
```

### S2-W0002 — Pole singularity warning

Longitude is not a meaningful coordinate at the collapsed poles.

### S2-W0003 — S2 group fallacy warning

S² does not have the same natural pointwise multiplication structure as S¹ or S³.

---

## S3 combinatorial targets

### S3C-T0001 — Suspension of sphere counts

If K has counts V,E,F, then Susp(K) has:

```text
V' = V + 2
E' = E + 2V
F' = F + 2E
T' = 2F
```

### S3C-T0002 — Suspension of sphere Euler characteristic

If χ(K)=2, then:

```text
χ(Susp(K)) = 0
```

### S3C-T0003 — Susp(SuspC(n)) counts

For n ≥ 3:

```text
V = n + 4
E = 5n + 4
F = 8n
T = 4n
```

### S3C-T0004 — Susp(SuspC(n)) Euler characteristic

```text
χ = 0
```

---

## S3 quaternion targets

### S3Q-T0001 — Quaternion norm definition

Define norm or squared norm for quaternions.

### S3Q-T0002 — Unit quaternions are closed under multiplication

If p and q are unit quaternions:

```text
|pq| = 1
```

### S3Q-T0003 — Unit quaternion inverse

For unit q:

```text
q⁻¹ = conjugate(q)
```

### S3Q-T0004 — Quaternion multiplication is noncommutative

Produce a formal example:

```text
i*j ≠ j*i
```

### S3Q-T0005 — Quaternion multiplication is associative

This distinguishes S³ from S⁷.

---

## S3 Hopf targets

### S3H-T0001 — Hopf map lands on S²

For:

```text
|z0|² + |z1|² = 1
```

prove:

```text
||h(z0,z1)|| = 1
```

### S3H-T0002 — Hopf map phase invariance

For unit complex phase u:

```text
h(u*z0, u*z1) = h(z0,z1)
```

### S3H-T0003 — Hopf fiber is S¹-like

For a fixed point under h, the phase orbit is circle-like.

### S3H-W0001 — Not product warning

Do not claim:

```text
S³ = S² × S¹
```

The Hopf fibration is locally product-like but globally twisted.

---

## S4-S6 targets

### S456-T0001 — Iterated suspension Euler parity

For the finite suspension model:

```text
χ(S^d) = 1 + (-1)^d
```

### S4-T0001 — S4 Euler characteristic

```text
χ(S^4) = 2
```

### S5-T0001 — S5 Euler characteristic

```text
χ(S^5) = 0
```

### S6-T0001 — S6 Euler characteristic

```text
χ(S^6) = 2
```

### S6-W0001 — Complex-structure warning

Do not rely on claims that settle the integrable complex structure question for S6 unless the project explicitly formalizes accepted sources.

---

## S7 topological targets

### S7C-T0001 — S7 by iterated suspension

Construct finite S7 as an iterated suspension model.

### S7C-T0002 — S7 Euler characteristic

```text
χ(S^7) = 0
```

---

## S7 quaternionic Hopf targets

### S7QH-T0001 — Quaternionic Hopf fibration roadmap

The intended structure is:

```text
S³ → S⁷ → S⁴
```

Start as roadmap/exploratory.

### S7QH-T0002 — Quaternionic phase invariance

Analog of complex phase invariance, but with unit quaternions.

Defer until S3 quaternion calculus is stable.

---

## S7 octonion targets

### S7O-T0001 — Octonion basis/multiplication table

Define or import octonions.

### S7O-T0002 — Octonion conjugate and norm

Define conjugate and norm.

### S7O-T0003 — Octonion norm multiplicativity

```text
|xy| = |x||y|
```

### S7O-T0004 — Unit octonions closed under multiplication

If x and y are unit octonions:

```text
|xy| = 1
```

### S7O-T0005 — Octonion noncommutativity example

Produce a formal example.

### S7O-T0006 — Octonion nonassociativity example

Produce a formal example:

```text
(xy)z ≠ x(yz)
```

### S7O-W0001 — Unit octonions are not a group

Do not use group APIs or group language unless quotienting/restriction/formal alternatives justify it.

### S7O-W0002 — Bracketing matters

In S7 octonion calculus, operation grouping is part of the proof object.
