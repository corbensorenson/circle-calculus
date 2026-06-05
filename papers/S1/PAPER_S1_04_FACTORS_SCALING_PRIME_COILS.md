# Circle Calculus S1.4: Factors, Scaling, and Prime Coils

Status: draft with the first scaling theorem spine proved.

## Aim

This paper will connect multiplication, scaling, factors, invertibility, and prime-circle behavior inside `S^1`.

## Target Spine

- `CC-T0008`: `Circle.scale_invertible_iff_coprime`
- `CC-T0028`: `Circle.scale_zero_factor`
- `CC-T0017`: `Circle.scale_one`
- `CC-T0018`: `Circle.scale_comp`
- `CC-T0029`: `Circle.scale_factor_modEq`
- `CC-T0019`: `Circle.scale_rot`
- `CC-T0020`: `Circle.scale_coilStep`
- `CC-T0031`: `Circle.scale_nat_to_coilStep`
- `CC-T0021`: `Circle.prime_scale_bijective`
- `CC-T0022`: `Circle.scale_cofactor_zero`
- `CC-T0023`: `Circle.scale_cofactor_multiple_zero`
- `CC-T0024`: `Circle.scale_add_cofactor_multiple`
- `CC-T0025`: `Circle.scale_nat_eq_zero_iff_dvd_mul`
- `CC-T0030`: `Circle.scale_nat_eq_zero_iff_period_dvd`
- `CC-T0032`: `Circle.scale_period_multiple_zero`
- `CC-T0033`: `Circle.scale_add_period_multiple`
- `CC-T0034`: `Circle.scale_nat_period_normalForm`
- `CC-T0026`: `Circle.scale_nat_eq_iff_mul_modEq`
- `CC-T0035`: `Circle.scale_nat_eq_iff_period_modEq`
- `CC-T0036`: `Circle.scale_nat_period_representatives_injective`
- `CC-T0037`: `Circle.scalePeriodRepresentativeImage_card`
- `CC-T0038`: `Circle.scale_nat_mem_scalePeriodRepresentativeImage`
- `CC-T0039`: `Circle.scaleCircleImage_eq_scalePeriodRepresentativeImage`
- `CC-T0040`: `Circle.scaleCircleImage_card`
- `CC-T0041`: `Circle.scaleKernelRepresentativeSet_eq_periodMultiples`
- `CC-T0042`: `Circle.scaleKernelRepresentativeSet_card`
- `CC-T0043`: `Circle.scaleFiberRepresentativeSet_eq_periodFibers`
- `CC-T0044`: `Circle.scaleFiberRepresentativeSet_card`
- `CC-T0045`: `Circle.nat_mem_scaleKernelSubgroup_iff_period_dvd`
- `CC-T0027`: `Circle.scale_nat_eq_iff_nat_modEq_of_coprime`
- multiplication as repeated rotation or scaling
- scaling invertibility iff coprime
- factor structure through orbit decomposition
- prime rings as full-cycle systems

## Proved Core

`CC-T0028` is proved by `Circle.scale_zero_factor`: scaling by zero sends every finite-circle address to zero.

`CC-T0017` is proved by `Circle.scale_one`: scaling by one is the identity map on every finite circle.

`CC-T0018` is proved by `Circle.scale_comp`: scaling by `b` and then scaling by `a` is the same as scaling once by `a*b`.

`CC-T0029` is proved by `Circle.scale_factor_modEq`: congruent scale factors modulo `n` define the same scaling map on `C_n`.

`CC-T0019` is proved by `Circle.scale_rot`: scaling transports rotation/coils by multiplying the stride. Scaling a node after one stride step is the same as scaling the node first and then rotating by the scaled stride.

`CC-T0020` is proved by `Circle.scale_coilStep`: scaling transports any finite coil step to the corresponding coil step with both start and stride scaled.

`CC-T0031` is proved by `Circle.scale_nat_to_coilStep`: scaling a natural step index by `k` gives the same address as taking that many stride-`k` coil steps from zero.

`CC-T0021` is proved by `Circle.prime_scale_bijective`: if the circle size `p` is prime and the multiplier satisfies `1 <= k < p`, then scaling by `k` is a bijection on `C_p`.

`CC-T0022` is proved by `Circle.scale_cofactor_zero`: if `k` divides `n`, then the cofactor address `n/k` is sent to zero by scaling with `k`.

`CC-T0023` is proved by `Circle.scale_cofactor_multiple_zero`: if `k` divides `n`, then every multiple of the cofactor address `n/k` is also sent to zero by scaling with `k`.

`CC-T0024` is proved by `Circle.scale_add_cofactor_multiple`: if `k` divides `n`, then adding any multiple of `n/k` to an address does not change the result after scaling by `k`.

`CC-T0025` is proved by `Circle.scale_nat_eq_zero_iff_dvd_mul`: a natural address `x` maps to zero under scaling by `k` exactly when `n` divides `k*x`.

`CC-T0030` is proved by `Circle.scale_nat_eq_zero_iff_period_dvd`: for nonzero circle size, a natural address maps to zero under scaling by `k` exactly when the stride period `period(n,k)` divides that address.

`CC-T0032` is proved by `Circle.scale_period_multiple_zero`: every natural multiple of the stride period maps to zero.

`CC-T0033` is proved by `Circle.scale_add_period_multiple`: adding any natural multiple of the stride period to a natural address does not change its scaled value.

`CC-T0034` is proved by `Circle.scale_nat_period_normalForm`: every scaled natural address has the same scaled value as its residue modulo `period(n,k)`.

`CC-T0026` is proved by `Circle.scale_nat_eq_iff_mul_modEq`: two natural addresses have the same scaled value exactly when their scaled products are congruent modulo `n`.

`CC-T0035` is proved by `Circle.scale_nat_eq_iff_period_modEq`: for nonzero circle size, two natural addresses have the same scaled value exactly when they are congruent modulo `period(n,k)`.

`CC-T0036` is proved by `Circle.scale_nat_period_representatives_injective`: after restricting to representatives below `period(n,k)`, scaling by `k` is injective.

`CC-T0037` is proved by `Circle.scalePeriodRepresentativeImage_card`: for nonzero circle size, the scaled image of the canonical representative interval below `period(n,k)` has cardinality `period(n,k)`.

`CC-T0038` is proved by `Circle.scale_nat_mem_scalePeriodRepresentativeImage`: every scaled natural address lands in that period-representative image.

`CC-T0039` is proved by `Circle.scaleCircleImage_eq_scalePeriodRepresentativeImage`: scaling all finite circle representatives has the same image as scaling one period of representatives.

`CC-T0040` is proved by `Circle.scaleCircleImage_card`: for nonzero circle size, the finite image of the scaling map has cardinality `period(n,k)`.

`CC-T0041` is proved by `Circle.scaleKernelRepresentativeSet_eq_periodMultiples`: for nonzero circle size, the canonical representatives that scale to zero are exactly the period multiples indexed by `0 <= m < gcd(n,k)`.

`CC-T0042` is proved by `Circle.scaleKernelRepresentativeSet_card`: for nonzero circle size, the finite zero-fiber representative set has cardinality `gcd(n,k)`.

`CC-T0043` is proved by `Circle.scaleFiberRepresentativeSet_eq_periodFibers`: for nonzero circle size, the canonical representatives in the scaled fiber of `r` are exactly `r % period(n,k)` plus the period multiples indexed by `0 <= m < gcd(n,k)`.

`CC-T0044` is proved by `Circle.scaleFiberRepresentativeSet_card`: for nonzero circle size, every canonical representative fiber of the scaling map has cardinality `gcd(n,k)`.

`CC-T0045` is proved by `Circle.nat_mem_scaleKernelSubgroup_iff_period_dvd`: after scaling is packaged as an additive hom, a natural representative lies in its kernel subgroup exactly when `period(n,k)` divides that representative.

`CC-T0027` is proved by `Circle.scale_nat_eq_iff_nat_modEq_of_coprime`: under the coprime condition, the scaled equality test reduces back to ordinary address congruence.

Together these theorems make scaling into a checked multiplicative action on finite-circle addresses and finite coil steps:

```text
scale(n,0)(x) = 0
scale(n,1)(x) = x
scale(n,a)(scale(n,b)(x)) = scale(n,a*b)(x)
scale(n,k)(x)=scale(n,l)(x) if k congruent l mod n
scale(n,k)(rot(n,stride)(x)) = rot(n,k*stride)(scale(n,k)(x))
scale(n,k)(coil_step(n,stride,start,steps))
  = coil_step(n,k*stride,k*start,steps)
scale(n,k)(steps)=coil_step(n,k,0,steps)
prime(p) and 1 <= k < p imply scale(p,k) is bijective
k divides n implies scale(n,k)(n/k) = 0
k divides n implies scale(n,k)(m*(n/k)) = 0
k divides n implies scale(n,k)(x+m*(n/k)) = scale(n,k)(x)
scale(n,k)(x)=0 iff n divides k*x
n != 0 implies scale(n,k)(x)=0 iff period(n,k) divides x
n != 0 implies scale(n,k)(m*period(n,k)) = 0
n != 0 implies scale(n,k)(x+m*period(n,k)) = scale(n,k)(x)
n != 0 implies scale(n,k)(x)=scale(n,k)(x mod period(n,k))
scale(n,k)(x)=scale(n,k)(y) iff k*x congruent k*y mod n
n != 0 implies scale(n,k)(x)=scale(n,k)(y) iff x congruent y mod period(n,k)
n != 0 and x,y < period(n,k) imply scale(n,k)(x)=scale(n,k)(y) iff x=y
n != 0 implies card(scale_period_representative_image(n,k))=period(n,k)
n != 0 implies scale(n,k)(x) belongs to scale_period_representative_image(n,k)
n != 0 implies scale_circle_image(n,k)=scale_period_representative_image(n,k)
n != 0 implies card(scale_circle_image(n,k))=period(n,k)
n != 0 implies scale_kernel_representative_set(n,k)=scale_period_kernel_representatives(n,k)
n != 0 implies card(scale_kernel_representative_set(n,k))=gcd(n,k)
n != 0 implies scale_fiber_representative_set(n,k,r)=scale_period_fiber_representatives(n,k,r)
n != 0 implies card(scale_fiber_representative_set(n,k,r))=gcd(n,k)
n != 0 implies x in scale_kernel_subgroup(n,k) iff period(n,k) divides x
gcd(n,k)=1 implies scale(n,k)(x)=scale(n,k)(y) iff x congruent y mod n
```

`CC-T0008` is proved by `Circle.scale_invertible_iff_coprime`.

For every modulus `n` and multiplier `k`, the scaling map

```text
scale(n,k)(x) = k*x in C_n
```

is a bijection exactly when `Nat.Coprime n k`. In ordinary gcd language, scaling is reversible exactly when `gcd(n,k)=1`.

The prime-circle theorem is the first checked specialization of that criterion. For a prime modulus, every nonzero residue below the modulus is coprime to it, so every such multiplier gives a reversible readdressing of the circle.

The zero-factor theorem records the degenerate kernel extreme: scaling by zero collapses the whole circle to zero. The scale-factor congruence theorem records the normal form for scale factors: only the residue class of the multiplier modulo `n` matters.

The natural-step theorem is the first explicit image bridge in this paper: the image of natural representatives under scaling by `k` is the same address stream generated by the stride-`k` coil from zero.

The cofactor-zero theorem is the first checked composite-factor collapse fact. The cofactor-multiple theorem extends that witness to the finite cycle generated by the cofactor address. The cofactor-shift theorem then says those kernel witnesses identify addresses after scaling. The divisibility theorem gives the exact zero criterion for natural representatives: the scaled address is zero precisely when the modulus divides the product `k*x`. The period-divisibility theorem translates that zero criterion into the existing coil-period vocabulary: the zero fiber is exactly the natural multiples of `period(n,k)`. The period-multiple and period-shift theorems package that criterion as direct kernel constructors and address-collapse rules. The period-normal-form theorem turns that collapse into a bounded representative statement: every natural input can be reduced modulo the stride period before scaling. The product-congruence equality theorem extends this from zero fibers to arbitrary equal scaled values by reducing equality in `C_n` to congruence of the scaled products. The period-congruence equality theorem then states the quotient directly: for nonzero `n`, scaling by `k` identifies exactly the natural addresses that are congruent modulo `period(n,k)`. The bounded-representative injectivity theorem packages this as a uniqueness statement on the canonical representative interval below the period. The period-representative image theorem turns that uniqueness statement into the first checked image-size fact: the finite image obtained from one period of representatives has exactly `period(n,k)` elements. The image-membership theorem then shows every scaled natural address lands in that finite image by reducing the input modulo the stride period. The circle-image equality and cardinality theorems package this as a finite image statement over the whole circle: scaling the `n` canonical representatives produces exactly the period-representative image, and therefore that image has `period(n,k)` elements. The kernel-representative equality and cardinality theorems count the canonical zero fiber: the representatives below `n` that scale to zero are exactly the period multiples indexed by `0 <= m < gcd(n,k)`, so there are `gcd(n,k)` of them. The fiber-representative equality and cardinality theorems extend that count uniformly: the finite fiber over the scaled value of any representative `r` is exactly the offset period-multiple set based at `r % period(n,k)`, and every such fiber has `gcd(n,k)` representatives. The kernel-subgroup membership theorem packages the zero fiber as the kernel of an additive hom and links natural representatives back to period divisibility. The coprime-reflection theorem records the reversible case: when the scale factor is coprime to the modulus, scaling introduces no new address identifications. These theorems do not yet state the fiber result for arbitrary target nodes outside the scaling image. They establish the kernel subgroup and representative fibers as finite objects and certify a basic divisor witness: when `n = k * (n/k)`, multiplying the cofactor, or any multiple of it, by `k` lands at the zero address of `C_n`.

The Lean proof reduces scaling to left multiplication by `(k : ZMod n)`. Mathlib then supplies the two standard bridges:

- left multiplication is bijective exactly when the multiplier is a unit;
- `(k : ZMod n)` is a unit exactly when `k` is coprime to `n`.

## Dictionary Targets

- `S1-0001`: S1 finite circle core
- `CC-0105`: Scaling
- new factor entries as the proof model matures

## Notes

The remaining factor-structure targets should build on `CC-T0008`, `CC-T0017`, `CC-T0018`, `CC-T0019`, `CC-T0020`, `CC-T0021`, `CC-T0022`, `CC-T0023`, `CC-T0024`, `CC-T0025`, `CC-T0026`, `CC-T0027`, `CC-T0028`, `CC-T0029`, `CC-T0030`, `CC-T0031`, `CC-T0032`, `CC-T0033`, `CC-T0034`, `CC-T0035`, `CC-T0036`, `CC-T0037`, `CC-T0038`, `CC-T0039`, `CC-T0040`, `CC-T0041`, `CC-T0042`, `CC-T0043`, `CC-T0044`, and `CC-T0045` without claiming more than the current finite-circle model proves.
