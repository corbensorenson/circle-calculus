use num_bigint::BigUint;
use num_traits::{One, ToPrimitive, Zero};

use crate::scalar::{is_prime_u64, PrimeStatus};

const BIG_WHEEL30_GAPS: [u64; 8] = [6, 4, 2, 4, 2, 4, 6, 2];
const BIG_WHEEL30_DELTA_BY_RESIDUE: [u64; 30] = [
    1, 0, 5, 4, 3, 2, 1, 0, 3, 2, 1, 0, 1, 0, 3, 2, 1, 0, 1, 0, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0,
];
const BIG_WHEEL30_INDEX_BY_RESIDUE: [usize; 30] = [
    0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7,
];
const BIG_SMALL_PRIME_TRIAL_DIVISORS: [u64; 64] = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
    101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
    197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307,
    311,
];
const BIG_SMALL_PRIME_TRIAL_DIVISOR_COUNT: usize = BIG_SMALL_PRIME_TRIAL_DIVISORS.len();
const BIG_MILLER_RABIN_BASES: [u64; 64] = BIG_SMALL_PRIME_TRIAL_DIVISORS;
const MAX_BIG_FUZZY_BIT_WIDTH: u32 = 16_384;

pub const DEFAULT_BIG_MILLER_RABIN_ROUNDS: usize = 64;
pub const DEFAULT_BIG_NEXT_MAX_CANDIDATES: u64 = 1_000_000;
pub const DEFAULT_BIG_FUZZY_CANDIDATE_WINDOW: usize = 256;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BigPrimeStatus {
    Composite,
    Prime,
    ProbablePrime,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BigPrimeDecision {
    pub n: BigUint,
    pub status: BigPrimeStatus,
    pub method: &'static str,
    pub stage: &'static str,
    pub factor: Option<u64>,
    pub witness_base: Option<u64>,
    pub checked_small_prime_limit: u64,
    pub miller_rabin_rounds: usize,
    pub bit_length: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BigNextPrimeSearch {
    pub start: BigUint,
    pub prime: Option<BigUint>,
    pub candidate_count: u64,
    pub max_candidates: u64,
    pub decision: Option<BigPrimeDecision>,
    pub exact_certified: bool,
}

#[derive(Debug, Clone, PartialEq)]
pub struct BigFuzzyPrimeModel {
    pub bit_width: u32,
    pub residue_moduli: Vec<u64>,
    pub weights: Vec<f64>,
    pub bias: f64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct BigFuzzyAnyPrimeCore {
    reported_prime: Option<BigUint>,
    reported_decision: Option<BigPrimeDecision>,
    checked_count: u64,
    used_fallback: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BigFuzzySearch {
    pub search_kind: &'static str,
    pub start: BigUint,
    pub candidate_window: usize,
    pub top_k: usize,
    pub score_limit: usize,
    pub miller_rabin_rounds: usize,
    pub reported_prime: Option<BigUint>,
    pub probable_prime_verified: bool,
    pub deterministically_verified: bool,
    pub hybrid_probable_checks: u64,
    pub baseline_first_prime: Option<BigUint>,
    pub baseline_sequential_checks_to_first_prime: u64,
    pub reported_prime_is_baseline_first_prime: bool,
    pub used_probable_fallback: bool,
}

impl BigPrimeDecision {
    pub fn is_prime_like(&self) -> bool {
        matches!(
            self.status,
            BigPrimeStatus::Prime | BigPrimeStatus::ProbablePrime
        )
    }

    pub fn is_exact_prime(&self) -> bool {
        self.status == BigPrimeStatus::Prime
    }

    pub fn to_json(&self) -> String {
        let status = match self.status {
            BigPrimeStatus::Composite => "composite",
            BigPrimeStatus::Prime => "prime",
            BigPrimeStatus::ProbablePrime => "probable_prime",
        };
        format!(
            "{{\"n\":{},\"bit_length\":{},\"status\":\"{}\",\"method\":\"{}\",\"stage\":\"{}\",\"factor\":{},\"witness_base\":{},\"checked_small_prime_limit\":{},\"miller_rabin_rounds\":{},\"proof_contract\":{}}}",
            biguint_json(&self.n),
            self.bit_length,
            status,
            self.method,
            self.stage,
            optional_u64_json(self.factor),
            optional_u64_json(self.witness_base),
            self.checked_small_prime_limit,
            self.miller_rabin_rounds,
            big_probable_prime_contract_json()
        )
    }
}

impl BigNextPrimeSearch {
    pub fn to_json(&self) -> String {
        let status = if self.prime.is_some() {
            "found"
        } else {
            "not_found"
        };
        let decision = self
            .decision
            .as_ref()
            .map_or_else(|| "null".to_string(), BigPrimeDecision::to_json);
        format!(
            "{{\"start\":{},\"status\":\"{}\",\"prime\":{},\"candidate_count\":{},\"max_candidates\":{},\"exact_certified\":{},\"decision\":{},\"proof_contract\":{}}}",
            biguint_json(&self.start),
            status,
            optional_biguint_json(self.prime.as_ref()),
            self.candidate_count,
            self.max_candidates,
            self.exact_certified,
            decision,
            big_probable_prime_contract_json()
        )
    }
}

impl BigFuzzyPrimeModel {
    pub fn from_text(raw: &str) -> Result<Self, String> {
        let mut version_seen = false;
        let mut bit_width = None;
        let mut residue_moduli = None;
        let mut weights = None;
        let mut bias = None;
        for line in raw.lines() {
            let trimmed = line.trim();
            if trimmed.is_empty() || trimmed.starts_with('#') {
                continue;
            }
            if trimmed == "circle_fuzzy_model_v0" {
                version_seen = true;
                continue;
            }
            let Some((key, value)) = trimmed.split_once(' ') else {
                return Err(format!("invalid fuzzy model line: {trimmed:?}"));
            };
            match key {
                "bit_width" => {
                    bit_width = Some(
                        value
                            .parse::<u32>()
                            .map_err(|_| "bit_width must fit in u32".to_string())?,
                    );
                }
                "residue_moduli" => {
                    residue_moduli = Some(parse_u64_list(value)?);
                }
                "weights" => {
                    weights = Some(parse_f64_list(value)?);
                }
                "bias" => {
                    bias = Some(
                        value
                            .parse::<f64>()
                            .map_err(|_| "bias must be a finite float".to_string())?,
                    );
                }
                _ => return Err(format!("unknown fuzzy model key: {key}")),
            }
        }
        if !version_seen {
            return Err("fuzzy model is missing circle_fuzzy_model_v0 header".to_string());
        }
        let bit_width = bit_width.ok_or_else(|| "fuzzy model missing bit_width".to_string())?;
        if bit_width == 0 || bit_width > MAX_BIG_FUZZY_BIT_WIDTH {
            return Err(format!(
                "bit_width must be in 1..={MAX_BIG_FUZZY_BIT_WIDTH} for big fuzzy search"
            ));
        }
        let residue_moduli =
            residue_moduli.ok_or_else(|| "fuzzy model missing residue_moduli".to_string())?;
        if residue_moduli.iter().any(|&modulus| modulus <= 1) {
            return Err("residue_moduli entries must be greater than 1".to_string());
        }
        let weights = weights.ok_or_else(|| "fuzzy model missing weights".to_string())?;
        let bias = bias.ok_or_else(|| "fuzzy model missing bias".to_string())?;
        if !bias.is_finite() || weights.iter().any(|weight| !weight.is_finite()) {
            return Err("fuzzy model weights and bias must be finite".to_string());
        }
        let expected = bit_width as usize + residue_moduli.len();
        if weights.len() != expected {
            return Err(format!(
                "fuzzy model has {} weights but expected {expected}",
                weights.len()
            ));
        }
        Ok(Self {
            bit_width,
            residue_moduli,
            weights,
            bias,
        })
    }

    pub fn logit_score(&self, n: &BigUint) -> Result<f64, String> {
        if n.bits() > u64::from(self.bit_width) {
            return Err(format!(
                "n={} has bit_length={} and does not fit fuzzy model bit_width={}",
                n,
                n.bits(),
                self.bit_width
            ));
        }
        let mut z = self.bias;
        for index in 0..self.bit_width {
            if n.bit(u64::from(index)) {
                z += self.weights[index as usize];
            }
        }
        let digits = n.to_u64_digits();
        let residue_offset = self.bit_width as usize;
        for (index, &modulus) in self.residue_moduli.iter().enumerate() {
            if biguint_digits_mod_u64(&digits, modulus) != 0 {
                z += self.weights[residue_offset + index];
            }
        }
        Ok(z)
    }

    pub fn to_json(&self) -> String {
        format!(
            "{{\"kind\":\"tiny_bit_residue_logistic_biguint\",\"bit_width\":{},\"feature_count\":{},\"parameter_count\":{},\"residue_moduli\":[{}],\"weights\":[{}],\"bias\":{:.17}}}",
            self.bit_width,
            self.weights.len(),
            self.weights.len() + 1,
            join_u64(&self.residue_moduli),
            join_f64(&self.weights),
            self.bias
        )
    }
}

impl BigFuzzySearch {
    pub fn to_json(&self, model: &BigFuzzyPrimeModel) -> String {
        format!(
            "{{\"search_kind\":\"{}\",\"start\":{},\"candidate_window\":{},\"top_k\":{},\"score_limit\":{},\"miller_rabin_rounds\":{},\"reported_prime\":{},\"probable_prime_verified\":{},\"deterministically_verified\":{},\"hybrid_probable_checks\":{},\"baseline_first_prime\":{},\"baseline_sequential_checks_to_first_prime\":{},\"reported_prime_is_baseline_first_prime\":{},\"used_probable_fallback\":{},\"model\":{},\"hybrid_proof_contract\":{},\"proof_contract\":{}}}",
            self.search_kind,
            biguint_json(&self.start),
            self.candidate_window,
            self.top_k,
            self.score_limit,
            self.miller_rabin_rounds,
            optional_biguint_json(self.reported_prime.as_ref()),
            self.probable_prime_verified,
            self.deterministically_verified,
            self.hybrid_probable_checks,
            optional_biguint_json(self.baseline_first_prime.as_ref()),
            self.baseline_sequential_checks_to_first_prime,
            self.reported_prime_is_baseline_first_prime,
            self.used_probable_fallback,
            model.to_json(),
            big_fuzzy_hybrid_contract_json(),
            big_probable_prime_contract_json()
        )
    }
}

pub fn big_probable_prime_contract_json() -> &'static str {
    "{\"name\":\"prime_bigint_probable_prime_search_v0\",\"lean_module\":\"Circle.Core.Horizon\",\"rust_domain\":\"arbitrary_precision_biguint_probable_prime\",\"scope\":\"Rust implements arbitrary-precision candidate arithmetic, exact composite witnesses from trial division, Miller-Rabin witnesses, perfect-square checks, or strong Lucas-Selfridge witnesses, and probable-prime acceptance under the selected fixed-base Miller-Rabin or BPSW profile. The current Lean boundary documents the divisibility target but does not certify arbitrary-precision prime results.\",\"not_claimed\":[\"arbitrary-precision primality certificate\",\"deterministic primality for all BigUint inputs\",\"learned model correctness\"]}"
}

pub fn big_fuzzy_hybrid_contract_json() -> &'static str {
    "{\"name\":\"prime_bigint_fuzzy_hybrid_probable_prime_search_v0\",\"lean_module\":\"Circle.Core.Horizon\",\"rust_domain\":\"arbitrary_precision_biguint_probable_prime\",\"neural_role\":\"candidate_ordering_only\",\"acceptance_rule\":\"a reported large candidate is accepted only after the configured BigUint probable-prime verifier accepts it; exact u64 inputs still route through the deterministic u64 path\",\"not_claimed\":[\"model weights are theorem proved\",\"probable-prime acceptance is a formal primality certificate\",\"exact next-prime proof for arbitrary-precision inputs\"]}"
}

pub fn parse_biguint(raw: &str) -> Result<BigUint, String> {
    let trimmed = raw.trim();
    if trimmed.is_empty() {
        return Err("big integer input must not be empty".to_string());
    }
    let (digits, radix) = if let Some(hex) = trimmed
        .strip_prefix("0x")
        .or_else(|| trimmed.strip_prefix("0X"))
    {
        (hex, 16)
    } else {
        (trimmed, 10)
    };
    if digits.is_empty() {
        return Err("big integer input has no digits".to_string());
    }
    BigUint::parse_bytes(digits.as_bytes(), radix)
        .ok_or_else(|| "big integer input must be unsigned decimal or 0x-prefixed hex".to_string())
}

pub fn max_big_miller_rabin_rounds() -> usize {
    BIG_MILLER_RABIN_BASES.len()
}

pub fn is_probable_prime_biguint(n: &BigUint, rounds: usize) -> Result<BigPrimeDecision, String> {
    validate_big_miller_rabin_rounds(rounds)?;
    if let Some(value) = n.to_u64() {
        let decision = is_prime_u64(value);
        let status = match decision.status {
            PrimeStatus::Composite => BigPrimeStatus::Composite,
            PrimeStatus::Prime => BigPrimeStatus::Prime,
            PrimeStatus::ProbablePrime => BigPrimeStatus::ProbablePrime,
        };
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status,
            method: "u64_exact_bridge",
            stage: decision.stage,
            factor: decision.factor,
            witness_base: decision.witness_base,
            checked_small_prime_limit: 79,
            miller_rabin_rounds: 0,
            bit_length: n.bits(),
        });
    }

    let two = BigUint::from(2u8);
    if n < &two {
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status: BigPrimeStatus::Composite,
            method: "boundary",
            stage: "below_two",
            factor: None,
            witness_base: None,
            checked_small_prime_limit: 0,
            miller_rabin_rounds: 0,
            bit_length: n.bits(),
        });
    }

    let digits = n.to_u64_digits();
    for &prime in &BIG_SMALL_PRIME_TRIAL_DIVISORS {
        if biguint_digits_mod_u64(&digits, prime) == 0 {
            return Ok(BigPrimeDecision {
                n: n.clone(),
                status: BigPrimeStatus::Composite,
                method: "small_prime_trial_division",
                stage: "small_factor_found",
                factor: Some(prime),
                witness_base: None,
                checked_small_prime_limit: prime,
                miller_rabin_rounds: 0,
                bit_length: n.bits(),
            });
        }
    }

    let one = BigUint::one();
    let n_minus_one = n - &one;
    let mut d = n_minus_one.clone();
    let mut s = 0u32;
    while !d.bit(0) {
        d >>= 1usize;
        s += 1;
    }

    for &base in &BIG_MILLER_RABIN_BASES[..rounds] {
        if !miller_rabin_round_biguint(n, base, &d, s, &n_minus_one) {
            return Ok(BigPrimeDecision {
                n: n.clone(),
                status: BigPrimeStatus::Composite,
                method: "miller_rabin_biguint_fixed_bases",
                stage: "witness_found",
                factor: None,
                witness_base: Some(base),
                checked_small_prime_limit: *BIG_SMALL_PRIME_TRIAL_DIVISORS
                    .last()
                    .expect("trial divisor list is nonempty"),
                miller_rabin_rounds: rounds,
                bit_length: n.bits(),
            });
        }
    }

    Ok(BigPrimeDecision {
        n: n.clone(),
        status: BigPrimeStatus::ProbablePrime,
        method: "miller_rabin_biguint_fixed_bases",
        stage: "all_configured_bases_passed",
        factor: None,
        witness_base: None,
        checked_small_prime_limit: *BIG_SMALL_PRIME_TRIAL_DIVISORS
            .last()
            .expect("trial divisor list is nonempty"),
        miller_rabin_rounds: rounds,
        bit_length: n.bits(),
    })
}

pub fn is_bpsw_probable_prime_biguint(n: &BigUint) -> Result<BigPrimeDecision, String> {
    if let Some(value) = n.to_u64() {
        let decision = is_prime_u64(value);
        let status = match decision.status {
            PrimeStatus::Composite => BigPrimeStatus::Composite,
            PrimeStatus::Prime => BigPrimeStatus::Prime,
            PrimeStatus::ProbablePrime => BigPrimeStatus::ProbablePrime,
        };
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status,
            method: "u64_exact_bridge",
            stage: decision.stage,
            factor: decision.factor,
            witness_base: decision.witness_base,
            checked_small_prime_limit: 79,
            miller_rabin_rounds: 0,
            bit_length: n.bits(),
        });
    }

    let two = BigUint::from(2u8);
    if n < &two {
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status: BigPrimeStatus::Composite,
            method: "boundary",
            stage: "below_two",
            factor: None,
            witness_base: None,
            checked_small_prime_limit: 0,
            miller_rabin_rounds: 0,
            bit_length: n.bits(),
        });
    }

    let digits = n.to_u64_digits();
    for &prime in &BIG_SMALL_PRIME_TRIAL_DIVISORS {
        if biguint_digits_mod_u64(&digits, prime) == 0 {
            return Ok(BigPrimeDecision {
                n: n.clone(),
                status: BigPrimeStatus::Composite,
                method: "small_prime_trial_division",
                stage: "small_factor_found",
                factor: Some(prime),
                witness_base: None,
                checked_small_prime_limit: prime,
                miller_rabin_rounds: 0,
                bit_length: n.bits(),
            });
        }
    }

    if is_square_biguint(n) {
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status: BigPrimeStatus::Composite,
            method: "baillie_psw_biguint",
            stage: "perfect_square_found",
            factor: None,
            witness_base: None,
            checked_small_prime_limit: *BIG_SMALL_PRIME_TRIAL_DIVISORS
                .last()
                .expect("trial divisor list is nonempty"),
            miller_rabin_rounds: 0,
            bit_length: n.bits(),
        });
    }

    let (d, s, n_minus_one) = miller_rabin_decomposition(n);
    if !miller_rabin_round_biguint(n, 2, &d, s, &n_minus_one) {
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status: BigPrimeStatus::Composite,
            method: "baillie_psw_biguint",
            stage: "base2_miller_rabin_witness_found",
            factor: None,
            witness_base: Some(2),
            checked_small_prime_limit: *BIG_SMALL_PRIME_TRIAL_DIVISORS
                .last()
                .expect("trial divisor list is nonempty"),
            miller_rabin_rounds: 1,
            bit_length: n.bits(),
        });
    }

    let Some((selfridge_d, selfridge_q)) = selfridge_lucas_parameters(n) else {
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status: BigPrimeStatus::Composite,
            method: "baillie_psw_biguint",
            stage: "selfridge_parameter_factor_found",
            factor: None,
            witness_base: None,
            checked_small_prime_limit: *BIG_SMALL_PRIME_TRIAL_DIVISORS
                .last()
                .expect("trial divisor list is nonempty"),
            miller_rabin_rounds: 1,
            bit_length: n.bits(),
        });
    };

    if !strong_lucas_selfridge_prp(n, selfridge_d, selfridge_q) {
        return Ok(BigPrimeDecision {
            n: n.clone(),
            status: BigPrimeStatus::Composite,
            method: "baillie_psw_biguint",
            stage: "strong_lucas_selfridge_witness_found",
            factor: None,
            witness_base: None,
            checked_small_prime_limit: *BIG_SMALL_PRIME_TRIAL_DIVISORS
                .last()
                .expect("trial divisor list is nonempty"),
            miller_rabin_rounds: 1,
            bit_length: n.bits(),
        });
    }

    Ok(BigPrimeDecision {
        n: n.clone(),
        status: BigPrimeStatus::ProbablePrime,
        method: "baillie_psw_biguint",
        stage: "base2_miller_rabin_and_strong_lucas_selfridge_passed",
        factor: None,
        witness_base: Some(2),
        checked_small_prime_limit: *BIG_SMALL_PRIME_TRIAL_DIVISORS
            .last()
            .expect("trial divisor list is nonempty"),
        miller_rabin_rounds: 1,
        bit_length: n.bits(),
    })
}

pub fn next_probable_prime_biguint(
    start: &BigUint,
    rounds: usize,
    max_candidates: u64,
) -> Result<BigNextPrimeSearch, String> {
    validate_big_miller_rabin_rounds(rounds)?;
    next_probable_prime_biguint_by(start, max_candidates, |candidate| {
        is_probable_prime_biguint(candidate, rounds)
    })
}

fn next_probable_prime_biguint_by<F>(
    start: &BigUint,
    max_candidates: u64,
    verifier: F,
) -> Result<BigNextPrimeSearch, String>
where
    F: Fn(&BigUint) -> Result<BigPrimeDecision, String>,
{
    if max_candidates == 0 {
        return Err("big-next --max-candidates must be positive".to_string());
    }
    for &prime in &[2u64, 3, 5] {
        let prime_big = BigUint::from(prime);
        if start <= &prime_big {
            let decision = verifier(&prime_big)?;
            return Ok(BigNextPrimeSearch {
                start: start.clone(),
                prime: Some(prime_big),
                candidate_count: 1,
                max_candidates,
                exact_certified: true,
                decision: Some(decision),
            });
        }
    }

    let seven = BigUint::from(7u64);
    let search_start = if start < &seven { &seven } else { start };
    let (mut candidate, mut wheel_index) = first_big_wheel30_candidate_at_or_above(search_start);
    let mut small_prime_residues = small_prime_trial_residues(&candidate);
    let mut candidate_count = 0u64;
    while candidate_count < max_candidates {
        candidate_count += 1;
        if first_small_factor_from_residues(&small_prime_residues).is_none() {
            let decision = verifier(&candidate)?;
            if decision.is_prime_like() {
                let exact_certified = decision.is_exact_prime();
                return Ok(BigNextPrimeSearch {
                    start: start.clone(),
                    prime: Some(candidate),
                    candidate_count,
                    max_candidates,
                    exact_certified,
                    decision: Some(decision),
                });
            }
        }
        let gap = BIG_WHEEL30_GAPS[wheel_index];
        candidate += BigUint::from(gap);
        advance_small_prime_trial_residues(&mut small_prime_residues, gap);
        wheel_index = (wheel_index + 1) % BIG_WHEEL30_GAPS.len();
    }
    Ok(BigNextPrimeSearch {
        start: start.clone(),
        prime: None,
        candidate_count,
        max_candidates,
        exact_certified: false,
        decision: None,
    })
}

pub fn next_bpsw_probable_prime_biguint(
    start: &BigUint,
    max_candidates: u64,
) -> Result<BigNextPrimeSearch, String> {
    next_probable_prime_biguint_by(start, max_candidates, is_bpsw_probable_prime_biguint)
}

pub fn big_fuzzy_any_prime_search(
    model: &BigFuzzyPrimeModel,
    start: &BigUint,
    candidate_window: usize,
    top_k: usize,
    score_limit: usize,
    rounds: usize,
) -> Result<BigFuzzySearch, String> {
    validate_big_miller_rabin_rounds(rounds)?;
    if candidate_window == 0 {
        return Err("big fuzzy candidate window must be positive".to_string());
    }
    if top_k == 0 {
        return Err("big fuzzy top_k must be positive".to_string());
    }
    if score_limit == 0 {
        return Err("big fuzzy score_limit must be positive".to_string());
    }
    let candidates = big_candidate_sequence(start, candidate_window);
    let effective_score_limit = score_limit.min(candidates.len());
    let core = big_fuzzy_any_prime_core(model, &candidates, top_k, effective_score_limit, rounds)?;
    let (baseline_prime, baseline_checks) = baseline_first_probable_prime(&candidates, rounds)?;
    let deterministically_verified = core
        .reported_decision
        .as_ref()
        .is_some_and(BigPrimeDecision::is_exact_prime);
    Ok(BigFuzzySearch {
        search_kind: "rust_biguint_fuzzy_any_probable_prime_in_candidate_window",
        start: start.clone(),
        candidate_window,
        top_k,
        score_limit: effective_score_limit,
        miller_rabin_rounds: rounds,
        reported_prime: core.reported_prime.clone(),
        probable_prime_verified: core.reported_prime.is_some(),
        deterministically_verified,
        hybrid_probable_checks: core.checked_count,
        baseline_first_prime: baseline_prime.clone(),
        baseline_sequential_checks_to_first_prime: baseline_checks,
        reported_prime_is_baseline_first_prime: core.reported_prime == baseline_prime,
        used_probable_fallback: core.used_fallback,
    })
}

pub fn big_fuzzy_any_prime_value(
    model: &BigFuzzyPrimeModel,
    start: &BigUint,
    candidate_window: usize,
    top_k: usize,
    score_limit: usize,
    rounds: usize,
) -> Result<Option<BigUint>, String> {
    validate_big_miller_rabin_rounds(rounds)?;
    if candidate_window == 0 {
        return Err("big fuzzy candidate window must be positive".to_string());
    }
    if top_k == 0 {
        return Err("big fuzzy top_k must be positive".to_string());
    }
    if score_limit == 0 {
        return Err("big fuzzy score_limit must be positive".to_string());
    }
    let candidates = big_candidate_sequence(start, candidate_window);
    let effective_score_limit = score_limit.min(candidates.len());
    Ok(
        big_fuzzy_any_prime_core(model, &candidates, top_k, effective_score_limit, rounds)?
            .reported_prime,
    )
}

fn validate_big_miller_rabin_rounds(rounds: usize) -> Result<(), String> {
    if rounds == 0 {
        return Err("Miller-Rabin rounds must be positive".to_string());
    }
    if rounds > BIG_MILLER_RABIN_BASES.len() {
        return Err(format!(
            "Miller-Rabin rounds must be <= {} for the fixed-base big-int verifier",
            BIG_MILLER_RABIN_BASES.len()
        ));
    }
    Ok(())
}

fn miller_rabin_decomposition(n: &BigUint) -> (BigUint, u32, BigUint) {
    let one = BigUint::one();
    let n_minus_one = n - &one;
    let mut d = n_minus_one.clone();
    let mut s = 0u32;
    while !d.bit(0) {
        d >>= 1usize;
        s += 1;
    }
    (d, s, n_minus_one)
}

fn miller_rabin_round_biguint(
    n: &BigUint,
    base: u64,
    d: &BigUint,
    s: u32,
    n_minus_one: &BigUint,
) -> bool {
    let one = BigUint::one();
    let a = BigUint::from(base);

    let mut x = a.modpow(d, n);
    if x == one || x == *n_minus_one {
        return true;
    }

    for _ in 1..s {
        x = (&x * &x) % n;
        if x == *n_minus_one {
            return true;
        }
    }

    false
}

fn is_square_biguint(n: &BigUint) -> bool {
    let root = n.sqrt();
    (&root * &root) == *n
}

fn selfridge_lucas_parameters(n: &BigUint) -> Option<(i64, i64)> {
    let mut abs_d = 5i64;
    let mut sign = 1i64;
    loop {
        let d = sign * abs_d;
        match jacobi_i64_biguint(d, n) {
            -1 => return Some((d, (1 - d) / 4)),
            0 => return None,
            _ => {}
        }
        abs_d += 2;
        sign = -sign;
        if abs_d > 10_000 {
            return None;
        }
    }
}

fn strong_lucas_selfridge_prp(n: &BigUint, d_param: i64, q_param: i64) -> bool {
    let one = BigUint::one();
    let mut lucas_d = n + &one;
    let mut s = 0u32;
    while !lucas_d.bit(0) {
        lucas_d >>= 1usize;
        s += 1;
    }

    let (u, mut v, mut q_k) = lucas_uv_q_mod(n, d_param, q_param, &lucas_d);
    if u.is_zero() || v.is_zero() {
        return true;
    }
    for _ in 1..s {
        let v_squared = (&v * &v) % n;
        let two_q = (&q_k << 1usize) % n;
        v = mod_sub_biguint(&v_squared, &two_q, n);
        q_k = (&q_k * &q_k) % n;
        if v.is_zero() {
            return true;
        }
    }
    false
}

fn lucas_uv_q_mod(
    n: &BigUint,
    d_param: i64,
    q_param: i64,
    k: &BigUint,
) -> (BigUint, BigUint, BigUint) {
    let mut u = BigUint::zero();
    let mut v = BigUint::from(2u8) % n;
    let mut q_k = BigUint::one();
    let q_mod = signed_i64_mod_biguint(q_param, n);

    for bit_index in (0..k.bits()).rev() {
        let doubled_u = (&u * &v) % n;
        let v_squared = (&v * &v) % n;
        let two_q = (&q_k << 1usize) % n;
        let doubled_v = mod_sub_biguint(&v_squared, &two_q, n);
        let doubled_q = (&q_k * &q_k) % n;
        u = doubled_u;
        v = doubled_v;
        q_k = doubled_q;

        if k.bit(bit_index) {
            let u_next = half_mod_odd_modulus(&((&u + &v) % n), n);
            let v_next = half_mod_odd_modulus(&signed_mul_add_mod(d_param, &u, &v, n), n);
            let q_next = (&q_k * &q_mod) % n;
            u = u_next;
            v = v_next;
            q_k = q_next;
        }
    }

    (u, v, q_k)
}

fn jacobi_i64_biguint(a: i64, n: &BigUint) -> i32 {
    debug_assert!(n.bit(0));
    let mut a = signed_i64_mod_biguint(a, n);
    let mut n = n.clone();
    let mut t = 1i32;

    while !a.is_zero() {
        while !a.bit(0) {
            a >>= 1usize;
            let residue = biguint_mod_u64(&n, 8);
            if residue == 3 || residue == 5 {
                t = -t;
            }
        }
        std::mem::swap(&mut a, &mut n);
        if biguint_mod_u64(&a, 4) == 3 && biguint_mod_u64(&n, 4) == 3 {
            t = -t;
        }
        a %= &n;
    }

    if n.is_one() {
        t
    } else {
        0
    }
}

fn signed_i64_mod_biguint(value: i64, modulus: &BigUint) -> BigUint {
    if value >= 0 {
        BigUint::from(value as u64) % modulus
    } else {
        let positive = BigUint::from(value.unsigned_abs()) % modulus;
        if positive.is_zero() {
            positive
        } else {
            modulus - positive
        }
    }
}

fn signed_mul_add_mod(
    coefficient: i64,
    value: &BigUint,
    addend: &BigUint,
    modulus: &BigUint,
) -> BigUint {
    let product = (value * BigUint::from(coefficient.unsigned_abs())) % modulus;
    if coefficient >= 0 {
        (product + addend) % modulus
    } else {
        mod_sub_biguint(addend, &product, modulus)
    }
}

fn half_mod_odd_modulus(value: &BigUint, modulus: &BigUint) -> BigUint {
    if value.bit(0) {
        (value + modulus) >> 1usize
    } else {
        value >> 1usize
    }
}

fn mod_sub_biguint(left: &BigUint, right: &BigUint, modulus: &BigUint) -> BigUint {
    if left >= right {
        left - right
    } else {
        (left + modulus) - right
    }
}

fn big_fuzzy_any_prime_core(
    model: &BigFuzzyPrimeModel,
    candidates: &[BigUint],
    top_k: usize,
    score_limit: usize,
    rounds: usize,
) -> Result<BigFuzzyAnyPrimeCore, String> {
    let scored = top_scored_big_candidates(model, &candidates[..score_limit], top_k)?;
    let mut checked_indices = Vec::new();
    let mut reported_prime = None;
    let mut reported_decision = None;
    let mut used_fallback = false;
    for &(_, index) in &scored {
        checked_indices.push(index);
        let decision = is_probable_prime_biguint(&candidates[index], rounds)?;
        if decision.is_prime_like() {
            reported_prime = Some(candidates[index].clone());
            reported_decision = Some(decision);
            break;
        }
    }
    if reported_prime.is_none() {
        used_fallback = true;
        for (index, candidate) in candidates.iter().enumerate() {
            if checked_indices.contains(&index) {
                continue;
            }
            checked_indices.push(index);
            let decision = is_probable_prime_biguint(candidate, rounds)?;
            if decision.is_prime_like() {
                reported_prime = Some(candidate.clone());
                reported_decision = Some(decision);
                break;
            }
        }
    }
    Ok(BigFuzzyAnyPrimeCore {
        reported_prime,
        reported_decision,
        checked_count: checked_indices.len() as u64,
        used_fallback,
    })
}

fn top_scored_big_candidates(
    model: &BigFuzzyPrimeModel,
    candidates: &[BigUint],
    top_k: usize,
) -> Result<Vec<(f64, usize)>, String> {
    let mut top: Vec<(f64, usize)> = Vec::with_capacity(top_k.min(candidates.len()));
    for (index, candidate) in candidates.iter().enumerate() {
        let scored = (model.logit_score(candidate)?, index);
        let insertion = top.partition_point(|&(score, existing)| {
            score > scored.0 || (score == scored.0 && existing < scored.1)
        });
        if insertion < top_k {
            top.insert(insertion, scored);
            if top.len() > top_k {
                top.pop();
            }
        }
    }
    Ok(top)
}

fn baseline_first_probable_prime(
    candidates: &[BigUint],
    rounds: usize,
) -> Result<(Option<BigUint>, u64), String> {
    let mut checks = 0u64;
    for candidate in candidates {
        checks += 1;
        if is_probable_prime_biguint(candidate, rounds)?.is_prime_like() {
            return Ok((Some(candidate.clone()), checks));
        }
    }
    Ok((None, checks))
}

fn big_candidate_sequence(start: &BigUint, count: usize) -> Vec<BigUint> {
    let mut candidates = Vec::with_capacity(count);
    for &prime in &[2u64, 3, 5] {
        let prime_big = BigUint::from(prime);
        if start <= &prime_big {
            candidates.push(prime_big);
            if candidates.len() == count {
                return candidates;
            }
        }
    }
    let seven = BigUint::from(7u64);
    let search_start = if start < &seven { &seven } else { start };
    let (mut candidate, mut wheel_index) = first_big_wheel30_candidate_at_or_above(search_start);
    while candidates.len() < count {
        candidates.push(candidate.clone());
        candidate += BigUint::from(BIG_WHEEL30_GAPS[wheel_index]);
        wheel_index = (wheel_index + 1) % BIG_WHEEL30_GAPS.len();
    }
    candidates
}

fn first_big_wheel30_candidate_at_or_above(start: &BigUint) -> (BigUint, usize) {
    let residue = biguint_mod_u64(start, 30) as usize;
    let delta = BIG_WHEEL30_DELTA_BY_RESIDUE[residue];
    let index = BIG_WHEEL30_INDEX_BY_RESIDUE[residue];
    let mut candidate = start.clone();
    if delta != 0 {
        candidate += BigUint::from(delta);
    }
    (candidate, index)
}

fn small_prime_trial_residues(n: &BigUint) -> [u64; BIG_SMALL_PRIME_TRIAL_DIVISOR_COUNT] {
    let digits = n.to_u64_digits();
    let mut residues = [0u64; BIG_SMALL_PRIME_TRIAL_DIVISOR_COUNT];
    for (index, &prime) in BIG_SMALL_PRIME_TRIAL_DIVISORS.iter().enumerate() {
        residues[index] = biguint_digits_mod_u64(&digits, prime);
    }
    residues
}

fn first_small_factor_from_residues(
    residues: &[u64; BIG_SMALL_PRIME_TRIAL_DIVISOR_COUNT],
) -> Option<u64> {
    BIG_SMALL_PRIME_TRIAL_DIVISORS
        .iter()
        .zip(residues.iter())
        .find_map(|(&prime, &residue)| (residue == 0).then_some(prime))
}

fn advance_small_prime_trial_residues(
    residues: &mut [u64; BIG_SMALL_PRIME_TRIAL_DIVISOR_COUNT],
    gap: u64,
) {
    for (residue, &prime) in residues
        .iter_mut()
        .zip(BIG_SMALL_PRIME_TRIAL_DIVISORS.iter())
    {
        *residue += gap;
        if *residue >= prime {
            *residue %= prime;
        }
    }
}

fn biguint_mod_u64(n: &BigUint, modulus: u64) -> u64 {
    let digits = n.to_u64_digits();
    biguint_digits_mod_u64(&digits, modulus)
}

fn biguint_digits_mod_u64(digits: &[u64], modulus: u64) -> u64 {
    debug_assert!(modulus > 0);
    let modulus = u128::from(modulus);
    let mut remainder = 0u128;
    for limb in digits.iter().rev() {
        remainder = (((remainder << 64) + u128::from(*limb)) % modulus) as u128;
    }
    remainder as u64
}

fn parse_u64_list(raw: &str) -> Result<Vec<u64>, String> {
    if raw.trim().is_empty() || raw.trim() == "none" {
        return Ok(Vec::new());
    }
    raw.split(',')
        .filter(|item| !item.trim().is_empty())
        .map(|item| {
            item.trim()
                .parse::<u64>()
                .map_err(|_| format!("invalid u64 list entry: {item:?}"))
        })
        .collect()
}

fn parse_f64_list(raw: &str) -> Result<Vec<f64>, String> {
    if raw.trim().is_empty() {
        return Ok(Vec::new());
    }
    raw.split(',')
        .filter(|item| !item.trim().is_empty())
        .map(|item| {
            item.trim()
                .parse::<f64>()
                .map_err(|_| format!("invalid float list entry: {item:?}"))
        })
        .collect()
}

fn join_u64(values: &[u64]) -> String {
    values
        .iter()
        .map(u64::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn join_f64(values: &[f64]) -> String {
    values
        .iter()
        .map(|value| format!("{value:.17}"))
        .collect::<Vec<_>>()
        .join(",")
}

fn biguint_json(value: &BigUint) -> String {
    format!("\"{value}\"")
}

fn optional_biguint_json(value: Option<&BigUint>) -> String {
    value.map_or_else(|| "null".to_string(), biguint_json)
}

fn optional_u64_json(value: Option<u64>) -> String {
    value.map_or_else(|| "null".to_string(), |n| n.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn zero_model(bit_width: u32) -> BigFuzzyPrimeModel {
        BigFuzzyPrimeModel {
            bit_width,
            residue_moduli: vec![3, 5, 7],
            weights: vec![0.0; bit_width as usize + 3],
            bias: 0.0,
        }
    }

    #[test]
    fn parses_decimal_and_hex_bigints() {
        assert_eq!(parse_biguint("97").unwrap(), BigUint::from(97u64));
        assert_eq!(parse_biguint("0x61").unwrap(), BigUint::from(97u64));
    }

    #[test]
    fn delegates_u64_to_exact_classifier() {
        let decision = is_probable_prime_biguint(&BigUint::from(97u64), 8).unwrap();
        assert_eq!(decision.status, BigPrimeStatus::Prime);
        assert_eq!(decision.method, "u64_exact_bridge");
    }

    #[test]
    fn classifies_large_mersenne_prime_as_probable_prime() {
        let n = (BigUint::one() << 127usize) - BigUint::one();
        let decision = is_probable_prime_biguint(&n, 16).unwrap();
        assert_eq!(decision.status, BigPrimeStatus::ProbablePrime);
    }

    #[test]
    fn bpsw_classifies_selected_large_primes_as_probable_prime() {
        let cases = [
            (BigUint::one() << 127usize) - BigUint::one(),
            (BigUint::one() << 255usize) - BigUint::from(19u64),
            (BigUint::one() << 256usize) - (BigUint::one() << 32usize) - BigUint::from(977u64),
        ];
        for n in cases {
            let decision = is_bpsw_probable_prime_biguint(&n).unwrap();
            assert_eq!(decision.status, BigPrimeStatus::ProbablePrime);
            assert_eq!(decision.method, "baillie_psw_biguint");
        }
    }

    #[test]
    fn bpsw_rejects_large_square() {
        let prime = (BigUint::one() << 127usize) - BigUint::one();
        let square = &prime * &prime;
        let decision = is_bpsw_probable_prime_biguint(&square).unwrap();
        assert_eq!(decision.status, BigPrimeStatus::Composite);
        assert_eq!(decision.stage, "perfect_square_found");
    }

    #[test]
    fn bpsw_classifies_large_mersenne_prime_as_probable_prime() {
        let n = (BigUint::one() << 127usize) - BigUint::one();
        let decision = is_bpsw_probable_prime_biguint(&n).unwrap();
        assert_eq!(decision.status, BigPrimeStatus::ProbablePrime);
        assert_eq!(decision.method, "baillie_psw_biguint");
        assert_eq!(
            decision.stage,
            "base2_miller_rabin_and_strong_lucas_selfridge_passed"
        );
        assert_eq!(decision.miller_rabin_rounds, 1);
    }

    #[test]
    fn bpsw_rejects_large_perfect_square_before_lucas_step() {
        let root = (BigUint::one() << 127usize) - BigUint::one();
        let n = &root * &root;
        let decision = is_bpsw_probable_prime_biguint(&n).unwrap();
        assert_eq!(decision.status, BigPrimeStatus::Composite);
        assert_eq!(decision.method, "baillie_psw_biguint");
        assert_eq!(decision.stage, "perfect_square_found");
    }

    #[test]
    fn finds_next_large_probable_prime() {
        let start = BigUint::one() << 127usize;
        let search = next_probable_prime_biguint(&start, 16, 1024).unwrap();
        assert!(search.prime.is_some());
        assert!(!search.exact_certified);
    }

    #[test]
    fn bpsw_finds_same_next_large_probable_prime_as_miller_rabin() {
        let start = BigUint::one() << 127usize;
        let mr = next_probable_prime_biguint(&start, 16, 1024).unwrap();
        let bpsw = next_bpsw_probable_prime_biguint(&start, 1024).unwrap();
        assert_eq!(bpsw.prime, mr.prime);
        assert!(!bpsw.exact_certified);
    }

    #[test]
    fn bpsw_next_search_finds_large_probable_prime() {
        let start = BigUint::one() << 127usize;
        let search = next_bpsw_probable_prime_biguint(&start, 1024).unwrap();
        assert_eq!(
            search.prime,
            Some(parse_biguint("170141183460469231731687303715884105757").unwrap())
        );
        assert!(!search.exact_certified);
        assert_eq!(
            search.decision.as_ref().map(|decision| decision.method),
            Some("baillie_psw_biguint")
        );
    }

    #[test]
    fn fuzzy_big_search_keeps_probable_verifier_in_charge() {
        let start = BigUint::one() << 127usize;
        let search = big_fuzzy_any_prime_search(&zero_model(128), &start, 128, 8, 32, 16).unwrap();
        assert!(search.reported_prime.is_some());
        assert!(search.probable_prime_verified);
        assert!(!search.deterministically_verified);
    }

    #[test]
    fn fuzzy_model_rejects_values_outside_bit_width() {
        let model = zero_model(8);
        let err = model.logit_score(&BigUint::from(257u64)).unwrap_err();
        assert!(err.contains("does not fit"));
    }
}
