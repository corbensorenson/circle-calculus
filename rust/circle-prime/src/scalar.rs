use crate::tables::{
    STATIC_BASE_PRIMES_U64, STATIC_BASE_PRIME_INDEX_BLOCK_SIZE,
    STATIC_BASE_PRIME_INDEX_BY_1024_BLOCK, STATIC_BASE_PRIME_LIMIT,
};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PrimeStatus {
    Composite,
    Prime,
    ProbablePrime,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PrimeDecision {
    pub n: u64,
    pub status: PrimeStatus,
    pub method: &'static str,
    pub stage: &'static str,
    pub factor: Option<u64>,
    pub witness_base: Option<u64>,
    pub checked_horizon_bound: Option<u64>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NextPrimeSearch {
    pub start: u64,
    pub prime: Option<u64>,
    pub candidate_count: u64,
    pub decision: Option<PrimeDecision>,
}

impl PrimeDecision {
    pub fn is_prime(&self) -> bool {
        self.status == PrimeStatus::Prime
    }

    pub fn to_json(&self) -> String {
        let status = match self.status {
            PrimeStatus::Composite => "composite",
            PrimeStatus::Prime => "prime",
            PrimeStatus::ProbablePrime => "probable_prime",
        };
        format!(
            "{{\"n\":{},\"status\":\"{}\",\"method\":\"{}\",\"stage\":\"{}\",\"factor\":{},\"witness_base\":{},\"checked_horizon_bound\":{},\"proof_contract\":{}}}",
            self.n,
            status,
            self.method,
            self.stage,
            optional_u64_json(self.factor),
            optional_u64_json(self.witness_base),
            optional_u64_json(self.checked_horizon_bound),
            prime_horizon_proof_contract_json()
        )
    }
}

impl NextPrimeSearch {
    pub fn to_json(&self) -> String {
        let status = if self.prime.is_some() {
            "found"
        } else {
            "not_found"
        };
        let decision = self
            .decision
            .as_ref()
            .map_or_else(|| "null".to_string(), PrimeDecision::to_json);
        format!(
            "{{\"start\":{},\"status\":\"{}\",\"prime\":{},\"candidate_count\":{},\"decision\":{},\"proof_contract\":{},\"next_proof_contract\":{}}}",
            self.start,
            status,
            optional_u64_json(self.prime),
            self.candidate_count,
            decision,
            prime_horizon_proof_contract_json(),
            next_prime_proof_contract_json()
        )
    }
}

pub const PRIME_HORIZON_THEOREM_IDS: [&str; 5] =
    ["CC-T0073", "CC-T0074", "CC-T0075", "CC-T0076", "CC-T0077"];
pub const PRIME_HORIZON_LEAN_NAMES: [&str; 5] = [
    "Circle.primitiveHorizonContained_iff_dvd",
    "Circle.primeHorizon_iff_no_smaller_contained",
    "Circle.primeHorizon_iff_no_sqrt_contained",
    "Circle.primeHorizon_of_no_sqrt_contained",
    "Circle.not_primeHorizon_has_sqrt_contained",
];
pub const PRIME_RANGE_COUNT_THEOREM_IDS: [&str; 2] = ["CC-T0078", "CC-T0079"];
pub const PRIME_RANGE_COUNT_LEAN_NAMES: [&str; 2] = [
    "Circle.mem_primeHorizonsInRange_iff",
    "Circle.primeHorizonRangeCount_eq_filter_card",
];
pub const NEXT_PRIME_THEOREM_IDS: [&str; 2] = ["CC-T0080", "CC-T0081"];
pub const NEXT_PRIME_LEAN_NAMES: [&str; 2] = [
    "Circle.nextPrimeHorizonResultUpTo_some_iff",
    "Circle.nextPrimeHorizonResultUpTo_none_iff",
];
pub const SMALL_PRIME_HORIZONS: [u64; 12] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37];
const SMALL_PRIME_HORIZON_MAX: u64 = 37;
const WHEEL30_FILTERED_SMALL_PRIME_HORIZONS: [u64; 9] = [7, 11, 13, 17, 19, 23, 29, 31, 37];
#[cfg(test)]
const NEXT_PRIME_WHEEL30_RESIDUES: [u64; 8] = [1, 7, 11, 13, 17, 19, 23, 29];
const NEXT_PRIME_WHEEL30_GAPS: [u64; 8] = [6, 4, 2, 4, 2, 4, 6, 2];
const NEXT_PRIME_WHEEL30_DELTA_BY_RESIDUE: [u64; 30] = [
    1, 0, 5, 4, 3, 2, 1, 0, 3, 2, 1, 0, 1, 0, 3, 2, 1, 0, 1, 0, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0,
];
const NEXT_PRIME_WHEEL30_INDEX_BY_RESIDUE: [usize; 30] = [
    0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7,
];
const SMALL_NEXT_PRIME_THRESHOLDS: [u64; 42] = [
    41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
    139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239,
    241, 251,
];
pub const ANGLE_BUNDLE_HORIZON_PRODUCTS: [u64; 1] = [
    433_601_713_048_867_373, // 41..79
];
pub const ANGLE_BUNDLE_HORIZON_MAX: u64 = 79;
pub const MR64_BASES: [u64; 7] = [2, 325, 9_375, 28_178, 450_775, 9_780_504, 1_795_265_022];

pub fn prime_horizon_proof_contract_json() -> &'static str {
    "{\"name\":\"prime_horizon_sqrt_containment\",\"lean_module\":\"Circle.Core.Horizon\",\"theorem_ids\":[\"CC-T0073\",\"CC-T0074\",\"CC-T0075\",\"CC-T0076\",\"CC-T0077\"],\"lean_names\":[\"Circle.primitiveHorizonContained_iff_dvd\",\"Circle.primeHorizon_iff_no_smaller_contained\",\"Circle.primeHorizon_iff_no_sqrt_contained\",\"Circle.primeHorizon_of_no_sqrt_contained\",\"Circle.not_primeHorizon_has_sqrt_contained\"],\"rust_domain\":\"u64_exact_arithmetic\",\"scope\":\"Lean proves the prime-horizon/divisibility contract; Rust supplies exact u64 arithmetic, sieving, and deterministic Miller-Rabin classification.\"}"
}

pub fn prime_range_count_proof_contract_json() -> &'static str {
    "{\"name\":\"prime_horizon_range_count_spec\",\"lean_module\":\"Circle.Core.Horizon\",\"theorem_ids\":[\"CC-T0078\",\"CC-T0079\"],\"lean_names\":[\"Circle.mem_primeHorizonsInRange_iff\",\"Circle.primeHorizonRangeCount_eq_filter_card\"],\"rust_domain\":\"u64_exact_arithmetic\",\"scope\":\"Lean specifies the half-open prime-horizon range-count target; Rust count modes implement the finite interval cardinality with exact u64 arithmetic and externally checked controls.\"}"
}

pub fn next_prime_proof_contract_json() -> &'static str {
    "{\"name\":\"prime_horizon_next_search_spec\",\"lean_module\":\"Circle.Core.Horizon\",\"theorem_ids\":[\"CC-T0080\",\"CC-T0081\"],\"lean_names\":[\"Circle.nextPrimeHorizonResultUpTo_some_iff\",\"Circle.nextPrimeHorizonResultUpTo_none_iff\"],\"rust_domain\":\"u64_exact_arithmetic\",\"scope\":\"Lean specifies found and not-found next-prime results over a finite domain ceiling; Rust implements the u64 search with exact arithmetic and externally checked controls.\"}"
}

fn optional_u64_json(value: Option<u64>) -> String {
    value.map_or_else(|| "null".to_string(), |n| n.to_string())
}

fn gcd_u64(mut left: u64, mut right: u64) -> u64 {
    while right != 0 {
        let next = left % right;
        left = right;
        right = next;
    }
    left
}

fn mul_mod(left: u64, right: u64, modulus: u64) -> u64 {
    (((left as u128) * (right as u128)) % (modulus as u128)) as u64
}

fn pow_mod(mut base: u64, mut exponent: u64, modulus: u64) -> u64 {
    let mut result = 1u64;
    base %= modulus;
    while exponent > 0 {
        if exponent & 1 == 1 {
            result = mul_mod(result, base, modulus);
        }
        base = mul_mod(base, base, modulus);
        exponent >>= 1;
    }
    result
}

pub fn miller_rabin_round(n: u64, base: u64, d: u64, s: u32) -> bool {
    let a = base % n;
    if a == 0 {
        return true;
    }

    let mut x = pow_mod(a, d, n);
    if x == 1 || x == n - 1 {
        return true;
    }

    for _ in 1..s {
        x = mul_mod(x, x, n);
        if x == n - 1 {
            return true;
        }
    }

    false
}

pub fn is_prime_u64(n: u64) -> PrimeDecision {
    if n < 2 {
        return PrimeDecision {
            n,
            status: PrimeStatus::Composite,
            method: "boundary",
            stage: "below_two",
            factor: None,
            witness_base: None,
            checked_horizon_bound: None,
        };
    }

    for q in SMALL_PRIME_HORIZONS {
        if n == q {
            return PrimeDecision {
                n,
                status: PrimeStatus::Prime,
                method: "small_horizon",
                stage: "exact_small_prime",
                factor: None,
                witness_base: None,
                checked_horizon_bound: Some(q),
            };
        }
        if n % q == 0 {
            return PrimeDecision {
                n,
                status: PrimeStatus::Composite,
                method: "small_horizon",
                stage: "contained_primitive_horizon",
                factor: Some(q),
                witness_base: None,
                checked_horizon_bound: Some(q),
            };
        }
    }

    classify_after_small_horizon_checks(n)
}

#[inline]
fn is_prime_wheel30_candidate_u64(n: u64) -> PrimeDecision {
    debug_assert!(n > *SMALL_PRIME_HORIZONS.last().expect("small primes exist"));
    debug_assert!(is_wheel30_residue(n));

    for q in WHEEL30_FILTERED_SMALL_PRIME_HORIZONS {
        if n % q == 0 {
            return PrimeDecision {
                n,
                status: PrimeStatus::Composite,
                method: "small_horizon",
                stage: "contained_primitive_horizon",
                factor: Some(q),
                witness_base: None,
                checked_horizon_bound: Some(q),
            };
        }
    }

    classify_after_small_horizon_checks(n)
}

#[inline]
fn classify_after_small_horizon_checks(n: u64) -> PrimeDecision {
    for bundle in ANGLE_BUNDLE_HORIZON_PRODUCTS {
        let factor = gcd_u64(n, bundle);
        if factor > 1 && factor < n {
            return PrimeDecision {
                n,
                status: PrimeStatus::Composite,
                method: "angle_bundle_gcd",
                stage: "contained_bundled_primitive_horizon",
                factor: Some(factor),
                witness_base: None,
                checked_horizon_bound: Some(ANGLE_BUNDLE_HORIZON_MAX),
            };
        }
    }

    let mut d = n - 1;
    let mut s = 0u32;
    while d % 2 == 0 {
        d /= 2;
        s += 1;
    }

    for base in MR64_BASES {
        if !miller_rabin_round(n, base, d, s) {
            return PrimeDecision {
                n,
                status: PrimeStatus::Composite,
                method: "miller_rabin_u64",
                stage: "witness_found",
                factor: None,
                witness_base: Some(base),
                checked_horizon_bound: Some(ANGLE_BUNDLE_HORIZON_MAX),
            };
        }
    }

    PrimeDecision {
        n,
        status: PrimeStatus::Prime,
        method: "miller_rabin_u64",
        stage: "all_deterministic_bases_passed",
        factor: None,
        witness_base: None,
        checked_horizon_bound: Some(ANGLE_BUNDLE_HORIZON_MAX),
    }
}

pub fn next_prime_u64(start: u64) -> NextPrimeSearch {
    if start <= SMALL_PRIME_HORIZON_MAX {
        for q in SMALL_PRIME_HORIZONS {
            if start <= q {
                let decision = is_prime_u64(q);
                return NextPrimeSearch {
                    start,
                    prime: Some(q),
                    candidate_count: 1,
                    decision: Some(decision),
                };
            }
        }
    }

    if let Some(search) = next_prime_from_static_table(start) {
        return search;
    }

    let Some((mut candidate, mut wheel_index)) = first_wheel30_candidate_at_or_above(start) else {
        return NextPrimeSearch {
            start,
            prime: None,
            candidate_count: 0,
            decision: None,
        };
    };
    let mut candidate_count = 0u64;
    loop {
        candidate_count += 1;
        let decision = is_prime_wheel30_candidate_u64(candidate);
        if decision.is_prime() {
            return NextPrimeSearch {
                start,
                prime: Some(candidate),
                candidate_count,
                decision: Some(decision),
            };
        }
        let gap = NEXT_PRIME_WHEEL30_GAPS[wheel_index];
        let Some(next_candidate) = candidate.checked_add(gap) else {
            return NextPrimeSearch {
                start,
                prime: None,
                candidate_count,
                decision: None,
            };
        };
        candidate = next_candidate;
        wheel_index = (wheel_index + 1) % NEXT_PRIME_WHEEL30_GAPS.len();
    }
}

pub fn next_prime_value_u64(start: u64) -> Option<u64> {
    if start <= SMALL_PRIME_HORIZON_MAX {
        for q in SMALL_PRIME_HORIZONS {
            if start <= q {
                return Some(q);
            }
        }
    }

    if let Some(prime) = next_prime_value_from_small_thresholds(start) {
        return Some(prime);
    }

    if let Some(prime) = next_prime_value_from_static_table(start) {
        return Some(prime);
    }

    let (mut candidate, mut wheel_index) = first_wheel30_candidate_at_or_above(start)?;
    loop {
        if is_prime_wheel30_candidate_value_u64(candidate) {
            return Some(candidate);
        }
        let gap = NEXT_PRIME_WHEEL30_GAPS[wheel_index];
        candidate = candidate.checked_add(gap)?;
        wheel_index = (wheel_index + 1) % NEXT_PRIME_WHEEL30_GAPS.len();
    }
}

#[inline]
fn next_prime_value_from_small_thresholds(start: u64) -> Option<u64> {
    if start
        > *SMALL_NEXT_PRIME_THRESHOLDS
            .last()
            .expect("small next-prime thresholds are nonempty")
    {
        return None;
    }
    let index = SMALL_NEXT_PRIME_THRESHOLDS.partition_point(|&prime| prime < start);
    SMALL_NEXT_PRIME_THRESHOLDS.get(index).copied()
}

fn next_prime_from_static_table(start: u64) -> Option<NextPrimeSearch> {
    let table_index = static_prime_table_lower_bound_index(start)?;
    let &prime = STATIC_BASE_PRIMES_U64.get(table_index)?;
    let candidate_count = wheel30_candidate_count_inclusive(start, prime)?;
    Some(NextPrimeSearch {
        start,
        prime: Some(prime),
        candidate_count,
        decision: Some(PrimeDecision {
            n: prime,
            status: PrimeStatus::Prime,
            method: "static_prime_table",
            stage: "exact_generated_sieve",
            factor: None,
            witness_base: None,
            checked_horizon_bound: Some(prime.isqrt()),
        }),
    })
}

fn next_prime_value_from_static_table(start: u64) -> Option<u64> {
    if start > STATIC_BASE_PRIME_LIMIT {
        return None;
    }
    let table_index = static_prime_table_lower_bound_index(start)?;
    STATIC_BASE_PRIMES_U64.get(table_index).copied()
}

#[inline]
fn static_prime_table_lower_bound_index(start: u64) -> Option<usize> {
    if start > STATIC_BASE_PRIME_LIMIT {
        return None;
    }
    let block = start as usize / STATIC_BASE_PRIME_INDEX_BLOCK_SIZE;
    let lower = STATIC_BASE_PRIME_INDEX_BY_1024_BLOCK
        .get(block)
        .copied()
        .map(|index| index as usize)?;
    let upper = STATIC_BASE_PRIME_INDEX_BY_1024_BLOCK
        .get(block + 1)
        .copied()
        .map_or(STATIC_BASE_PRIMES_U64.len(), |index| index as usize);
    let local_index = STATIC_BASE_PRIMES_U64[lower..upper].partition_point(|&prime| prime < start);
    Some(lower + local_index)
}

#[inline]
fn is_prime_wheel30_candidate_value_u64(n: u64) -> bool {
    debug_assert!(n > *SMALL_PRIME_HORIZONS.last().expect("small primes exist"));
    debug_assert!(is_wheel30_residue(n));

    for q in WHEEL30_FILTERED_SMALL_PRIME_HORIZONS {
        if n % q == 0 {
            return false;
        }
    }

    for bundle in ANGLE_BUNDLE_HORIZON_PRODUCTS {
        let factor = gcd_u64(n, bundle);
        if factor > 1 && factor < n {
            return false;
        }
    }

    let mut d = n - 1;
    let mut s = 0u32;
    while d % 2 == 0 {
        d /= 2;
        s += 1;
    }

    MR64_BASES
        .into_iter()
        .all(|base| miller_rabin_round(n, base, d, s))
}

fn wheel30_candidate_count_inclusive(start: u64, end: u64) -> Option<u64> {
    let (mut candidate, mut wheel_index) = first_wheel30_candidate_at_or_above(start)?;
    let mut count = 0u64;
    while candidate <= end {
        count += 1;
        if candidate == end {
            return Some(count);
        }
        let gap = NEXT_PRIME_WHEEL30_GAPS[wheel_index];
        candidate = candidate.checked_add(gap)?;
        wheel_index = (wheel_index + 1) % NEXT_PRIME_WHEEL30_GAPS.len();
    }
    None
}

fn first_wheel30_candidate_at_or_above(start: u64) -> Option<(u64, usize)> {
    let residue = (start % 30) as usize;
    let delta = NEXT_PRIME_WHEEL30_DELTA_BY_RESIDUE[residue];
    let index = NEXT_PRIME_WHEEL30_INDEX_BY_RESIDUE[residue];
    start.checked_add(delta).map(|candidate| (candidate, index))
}

fn is_wheel30_residue(n: u64) -> bool {
    matches!(n % 30, 1 | 7 | 11 | 13 | 17 | 19 | 23 | 29)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn trial_is_prime(n: u64) -> bool {
        if n < 2 {
            return false;
        }
        if n == 2 {
            return true;
        }
        if n % 2 == 0 {
            return false;
        }
        let mut divisor = 3u64;
        while divisor * divisor <= n {
            if n % divisor == 0 {
                return false;
            }
            divisor += 2;
        }
        true
    }

    #[test]
    fn agrees_with_trial_division_on_small_range() {
        for n in 0..100_000 {
            assert_eq!(is_prime_u64(n).is_prime(), trial_is_prime(n), "n={n}");
        }
    }

    #[test]
    fn rejects_carmichael_numbers_and_pseudoprimes() {
        for n in [341, 561, 1105, 1729, 2465, 2821, 6601] {
            let decision = is_prime_u64(n);
            assert_eq!(decision.status, PrimeStatus::Composite);
        }
    }

    #[test]
    fn accepts_large_known_u64_prime() {
        let decision = is_prime_u64(18_446_744_073_709_551_557);
        assert_eq!(decision.status, PrimeStatus::Prime);
    }

    #[test]
    fn rejects_large_known_u64_composite() {
        let decision = is_prime_u64(18_446_744_073_709_551_615);
        assert_eq!(decision.status, PrimeStatus::Composite);
    }

    #[test]
    fn angle_bundle_gcd_keeps_bundled_primes_prime() {
        for n in [41, 43, 47, 53, 59, 61, 67, 71, 73, 79] {
            let decision = is_prime_u64(n);
            assert_eq!(decision.status, PrimeStatus::Prime, "n={n}");
        }
    }

    #[test]
    fn angle_bundle_gcd_rejects_composites_before_miller_rabin() {
        for (n, factor) in [
            (41 * 1_000_000_007u64, 41),
            (43 * 1_000_000_007u64, 43),
            (47 * 1_000_000_007u64, 47),
            (79 * 1_000_000_007u64, 79),
        ] {
            let decision = is_prime_u64(n);
            assert_eq!(decision.status, PrimeStatus::Composite, "n={n}");
            assert_eq!(decision.method, "angle_bundle_gcd", "n={n}");
            assert_eq!(decision.factor, Some(factor), "n={n}");
            assert_eq!(
                decision.checked_horizon_bound,
                Some(ANGLE_BUNDLE_HORIZON_MAX)
            );
        }
    }

    #[test]
    fn next_prime_wheel30_classifier_matches_general_status() {
        for n in [
            41,
            49,
            77,
            83,
            83 * 1_000_000_007u64,
            127 * 1_000_000_007u64,
            293 * 1_000_000_007u64,
            1_000_003,
            4_294_967_029,
            1_000_000_000_039,
            18_446_744_073_709_551_521,
        ] {
            assert!(n > 37, "n={n}");
            assert!(is_wheel30_residue(n), "n={n}");
            assert_eq!(
                is_prime_wheel30_candidate_u64(n).status,
                is_prime_u64(n).status,
                "n={n}"
            );
        }
    }

    #[test]
    fn first_wheel30_candidate_lookup_matches_residue_table() {
        for start in 0..300u64 {
            let (candidate, index) = first_wheel30_candidate_at_or_above(start).unwrap();
            assert!(candidate >= start, "start={start}");
            assert!(
                is_wheel30_residue(candidate),
                "start={start}, candidate={candidate}"
            );
            assert_eq!(
                candidate % 30,
                NEXT_PRIME_WHEEL30_RESIDUES[index],
                "start={start}"
            );
            assert!(
                (start..candidate).all(|skipped| !is_wheel30_residue(skipped)),
                "start={start}, candidate={candidate}"
            );
        }
    }

    #[test]
    fn first_wheel30_candidate_lookup_handles_u64_ceiling() {
        assert_eq!(first_wheel30_candidate_at_or_above(u64::MAX), None);
        assert_eq!(first_wheel30_candidate_at_or_above(u64::MAX - 1), None);
        assert_eq!(
            first_wheel30_candidate_at_or_above(18_446_744_073_709_551_557),
            Some((18_446_744_073_709_551_557, 4))
        );
    }

    #[test]
    fn uses_full_u64_deterministic_miller_rabin_bases() {
        assert_eq!(
            MR64_BASES,
            [2, 325, 9_375, 28_178, 450_775, 9_780_504, 1_795_265_022]
        );
    }

    #[test]
    fn next_prime_uses_wheel30_candidates_and_exact_decision() {
        let search = next_prime_u64(38);
        assert_eq!(search.prime, Some(41));
        assert_eq!(search.candidate_count, 1);
        assert_eq!(
            search.decision.as_ref().map(|decision| decision.status),
            Some(PrimeStatus::Prime)
        );

        assert_eq!(next_prime_u64(0).prime, Some(2));
        assert_eq!(next_prime_u64(97).prime, Some(97));
        assert_eq!(next_prime_u64(98).prime, Some(101));
    }

    #[test]
    fn next_prime_uses_static_prime_table_for_small_starts() {
        let search = next_prime_u64(90);
        assert_eq!(search.prime, Some(97));
        assert_eq!(search.candidate_count, 2);
        let decision = search.decision.expect("static-table search has a decision");
        assert_eq!(decision.status, PrimeStatus::Prime);
        assert_eq!(decision.method, "static_prime_table");
        assert_eq!(decision.stage, "exact_generated_sieve");
        assert_eq!(decision.checked_horizon_bound, Some(9));

        let million = next_prime_u64(1_000_000);
        assert_eq!(million.prime, Some(1_000_003));
        assert_eq!(million.candidate_count, 2);
        assert_eq!(
            million.decision.as_ref().map(|decision| decision.method),
            Some("static_prime_table")
        );
    }

    #[test]
    fn next_prime_value_matches_structured_search() {
        for start in [
            0,
            2,
            38,
            41,
            42,
            90,
            98,
            250,
            251,
            252,
            1_000_000,
            STATIC_BASE_PRIME_LIMIT,
            STATIC_BASE_PRIME_LIMIT + 1,
            4_294_967_000,
            1_000_000_000_000,
            18_446_744_073_709_551_500,
            18_446_744_073_709_551_558,
            u64::MAX,
        ] {
            assert_eq!(
                next_prime_value_u64(start),
                next_prime_u64(start).prime,
                "start={start}"
            );
        }
    }

    #[test]
    fn static_prime_table_path_declines_after_last_table_prime() {
        let last_static_prime = *STATIC_BASE_PRIMES_U64.last().expect("static primes");
        assert_eq!(
            next_prime_u64(last_static_prime).prime,
            Some(last_static_prime)
        );
        assert_eq!(
            next_prime_u64(last_static_prime)
                .decision
                .as_ref()
                .map(|decision| decision.method),
            Some("static_prime_table")
        );

        let search = next_prime_u64(last_static_prime + 1);
        assert!(search.prime.is_some());
        assert_ne!(
            search.decision.as_ref().map(|decision| decision.method),
            Some("static_prime_table")
        );
    }

    #[test]
    fn static_prime_table_block_index_matches_full_lower_bound() {
        for start in [
            0,
            2,
            251,
            1023,
            1024,
            1025,
            1_000_000,
            1_000_003,
            1_000_004,
            STATIC_BASE_PRIME_LIMIT - 1,
            STATIC_BASE_PRIME_LIMIT,
        ] {
            assert_eq!(
                static_prime_table_lower_bound_index(start),
                Some(STATIC_BASE_PRIMES_U64.partition_point(|&prime| prime < start)),
                "start={start}"
            );
        }
    }

    #[test]
    fn next_prime_reports_none_above_largest_u64_prime() {
        assert_eq!(
            next_prime_u64(18_446_744_073_709_551_557).prime,
            Some(18_446_744_073_709_551_557)
        );
        let search = next_prime_u64(18_446_744_073_709_551_558);
        assert_eq!(search.prime, None);
        assert!(search.candidate_count > 0);
    }
}
