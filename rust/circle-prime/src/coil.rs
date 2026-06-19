#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CoilSignature {
    pub n: u128,
    pub skip: u128,
    pub canonical_skip: u128,
    pub mirror_skip: u128,
    pub gcd: u128,
    pub period: u128,
    pub ring_count: u128,
    pub full_length: bool,
    pub directed_numerator: u128,
    pub canonical_numerator: u128,
    pub denominator: u128,
    pub primitive_horizon: Option<u128>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HorizonCollision {
    pub n: u128,
    pub contained_horizon: u128,
    pub skip: u128,
    pub numerator: u128,
    pub denominator: u128,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HorizonInspection {
    pub n: u128,
    pub unique_skip_count: u128,
    pub full_length_count: u128,
    pub fractured_count: u128,
    pub contained_primitive_horizons: Vec<u128>,
    pub signatures: Vec<CoilSignature>,
}

pub fn gcd_u128(mut left: u128, mut right: u128) -> u128 {
    while right != 0 {
        let next = left % right;
        left = right;
        right = next;
    }
    left
}

pub fn coil_signature(n: u128, skip: u128) -> Result<CoilSignature, String> {
    if n < 2 {
        return Err("n must be at least 2".to_string());
    }

    let k = skip % n;
    if k == 0 {
        return Err("skip must be nonzero modulo n".to_string());
    }

    let mirror_skip = n - k;
    let canonical_skip = k.min(mirror_skip);
    let divisor = gcd_u128(n, k);
    let period = n / divisor;
    let directed_numerator = k / divisor;
    let canonical_numerator = canonical_skip / divisor;
    let primitive_horizon = if canonical_numerator == 1 {
        Some(period)
    } else {
        None
    };

    Ok(CoilSignature {
        n,
        skip: k,
        canonical_skip,
        mirror_skip,
        gcd: divisor,
        period,
        ring_count: divisor,
        full_length: divisor == 1,
        directed_numerator,
        canonical_numerator,
        denominator: period,
        primitive_horizon,
    })
}

pub fn coil_spectrum(n: u128, unique_only: bool) -> Result<Vec<CoilSignature>, String> {
    if n < 2 {
        return Err("n must be at least 2".to_string());
    }
    let stop = if unique_only { n / 2 } else { n - 1 };
    let mut signatures = Vec::with_capacity(stop.min(usize::MAX as u128) as usize);
    for skip in 1..=stop {
        signatures.push(coil_signature(n, skip)?);
    }
    Ok(signatures)
}

pub fn literal_orbit(n: u128, skip: u128) -> Result<Vec<u128>, String> {
    if n < 2 {
        return Err("n must be at least 2".to_string());
    }
    let k = skip % n;
    if k == 0 {
        return Err("skip must be nonzero modulo n".to_string());
    }

    let mut orbit = vec![0];
    let mut current = 0;
    loop {
        current = (current + k) % n;
        orbit.push(current);
        if current == 0 {
            return Ok(orbit);
        }
    }
}

pub fn contains_horizon(n: u128, d: u128) -> Result<bool, String> {
    if n < 2 {
        return Err("n must be at least 2".to_string());
    }
    if d < 2 {
        return Err("d must be at least 2".to_string());
    }
    Ok(n % d == 0)
}

pub fn contains_smaller_horizon(n: u128, d: u128) -> Result<bool, String> {
    Ok(d < n && contains_horizon(n, d)?)
}

pub fn horizon_collision(n: u128, d: u128) -> Result<Option<HorizonCollision>, String> {
    if !contains_smaller_horizon(n, d)? {
        return Ok(None);
    }
    Ok(Some(HorizonCollision {
        n,
        contained_horizon: d,
        skip: n / d,
        numerator: 1,
        denominator: d,
    }))
}

pub fn inspect_horizon(n: u128) -> Result<HorizonInspection, String> {
    let signatures = coil_spectrum(n, true)?;
    let full_length_count = signatures
        .iter()
        .filter(|signature| signature.full_length)
        .count() as u128;
    let unique_skip_count = signatures.len() as u128;
    let mut contained_primitive_horizons = signatures
        .iter()
        .filter_map(|signature| signature.primitive_horizon)
        .filter(|d| *d < n)
        .collect::<Vec<_>>();
    contained_primitive_horizons.sort_unstable();
    contained_primitive_horizons.dedup();

    Ok(HorizonInspection {
        n,
        unique_skip_count,
        full_length_count,
        fractured_count: unique_skip_count - full_length_count,
        contained_primitive_horizons,
        signatures,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signature_uses_gcd_period_and_ring_count() {
        let signature = coil_signature(12, 4).unwrap();
        assert_eq!(signature.gcd, 4);
        assert_eq!(signature.period, 3);
        assert_eq!(signature.ring_count, 4);
        assert!(!signature.full_length);
        assert_eq!(signature.primitive_horizon, Some(3));
    }

    #[test]
    fn mirror_skips_share_the_same_undirected_signature() {
        for n in 2..128 {
            for k in 1..n {
                let left = coil_signature(n, k).unwrap();
                let right = coil_signature(n, n - k).unwrap();
                assert_eq!(left.period, right.period);
                assert_eq!(left.ring_count, right.ring_count);
                assert_eq!(left.canonical_skip, right.canonical_skip);
            }
        }
    }

    #[test]
    fn literal_orbit_first_return_matches_gcd_period() {
        for n in 2..96 {
            for k in 1..n {
                let signature = coil_signature(n, k).unwrap();
                let orbit = literal_orbit(n, k).unwrap();
                assert_eq!(orbit.len() as u128 - 1, signature.period);
            }
        }
    }

    #[test]
    fn horizon_containment_is_divisibility() {
        for n in 2..200 {
            for d in 2..200 {
                assert_eq!(contains_horizon(n, d).unwrap(), n % d == 0);
            }
        }
        let collision = horizon_collision(77, 11).unwrap().unwrap();
        assert_eq!(collision.skip, 7);
        assert_eq!(collision.denominator, 11);
    }

    #[test]
    fn inspect_records_composite_subhorizons() {
        let inspection = inspect_horizon(16).unwrap();
        assert_eq!(inspection.unique_skip_count, 8);
        assert_eq!(inspection.contained_primitive_horizons, vec![2, 4, 8]);
    }
}
