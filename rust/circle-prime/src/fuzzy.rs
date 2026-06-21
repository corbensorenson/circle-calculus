use crate::scalar::{
    is_prime_u64, next_prime_proof_contract_json, next_prime_u64, prime_horizon_proof_contract_json,
};

const FUZZY_WHEEL30_GAPS: [u64; 8] = [6, 4, 2, 4, 2, 4, 6, 2];
const FUZZY_WHEEL30_DELTA_BY_RESIDUE: [u64; 30] = [
    1, 0, 5, 4, 3, 2, 1, 0, 3, 2, 1, 0, 1, 0, 3, 2, 1, 0, 1, 0, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0,
];
const FUZZY_WHEEL30_INDEX_BY_RESIDUE: [usize; 30] = [
    0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7,
];

#[derive(Debug, Clone, PartialEq)]
pub struct FuzzyPrimeModel {
    pub bit_width: u32,
    pub residue_moduli: Vec<u64>,
    pub weights: Vec<f64>,
    pub bias: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub struct FuzzySearch {
    pub search_kind: &'static str,
    pub start: u64,
    pub window: u64,
    pub top_k: usize,
    pub score_limit: usize,
    pub candidate_count: usize,
    pub reported_prime: Option<u64>,
    pub deterministically_verified: bool,
    pub hinted_prime: Option<u64>,
    pub hinted_prime_was_next: Option<bool>,
    pub hybrid_deterministic_checks: u64,
    pub baseline_first_prime: Option<u64>,
    pub baseline_sequential_checks_to_first_prime: u64,
    pub reported_prime_is_baseline_first_prime: bool,
    pub used_deterministic_fallback: bool,
    pub exact_next_certified: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct FuzzyAnyPrimeCore {
    reported_prime: Option<u64>,
    checked_count: u64,
    used_fallback: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FuzzySearchMode {
    AnyPrime,
    ExactNext,
}

impl FuzzySearchMode {
    pub fn parse(raw: &str) -> Result<Self, String> {
        match raw {
            "any-prime" => Ok(Self::AnyPrime),
            "exact-next" => Ok(Self::ExactNext),
            _ => Err("fuzzy search mode must be any-prime or exact-next".to_string()),
        }
    }
}

impl FuzzyPrimeModel {
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
        if bit_width == 0 || bit_width > 64 {
            return Err("bit_width must be in 1..=64".to_string());
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

    pub fn to_text(&self) -> String {
        let residue_moduli = if self.residue_moduli.is_empty() {
            "none".to_string()
        } else {
            join_u64(&self.residue_moduli)
        };
        format!(
            "circle_fuzzy_model_v0\nbit_width {}\nresidue_moduli {}\nweights {}\nbias {:.17}\n",
            self.bit_width,
            residue_moduli,
            join_f64(&self.weights),
            self.bias
        )
    }

    pub fn score(&self, n: u64) -> Result<f64, String> {
        self.logit_score(n).map(sigmoid)
    }

    pub fn logit_score(&self, n: u64) -> Result<f64, String> {
        if self.bit_width < 64 && n >= (1u64 << self.bit_width) {
            return Err(format!(
                "n={n} does not fit fuzzy model bit_width={}",
                self.bit_width
            ));
        }
        let mut z = self.bias;
        for index in 0..self.bit_width {
            if ((n >> index) & 1) == 1 {
                z += self.weights[index as usize];
            }
        }
        let residue_offset = self.bit_width as usize;
        for (index, &modulus) in self.residue_moduli.iter().enumerate() {
            if n % modulus != 0 {
                z += self.weights[residue_offset + index];
            }
        }
        Ok(z)
    }

    pub fn to_json(&self) -> String {
        format!(
            "{{\"kind\":\"tiny_bit_residue_logistic\",\"bit_width\":{},\"feature_count\":{},\"parameter_count\":{},\"residue_moduli\":[{}],\"weights\":[{}],\"bias\":{:.17}}}",
            self.bit_width,
            self.weights.len(),
            self.weights.len() + 1,
            join_u64(&self.residue_moduli),
            join_f64(&self.weights),
            self.bias
        )
    }
}

impl FuzzySearch {
    pub fn to_json(&self, model: &FuzzyPrimeModel) -> String {
        format!(
            "{{\"search_kind\":\"{}\",\"start\":{},\"window\":{},\"top_k\":{},\"score_limit\":{},\"candidate_count\":{},\"reported_prime\":{},\"deterministically_verified\":{},\"hinted_prime\":{},\"hinted_prime_was_next\":{},\"hybrid_deterministic_checks\":{},\"baseline_first_prime\":{},\"baseline_sequential_checks_to_first_prime\":{},\"reported_prime_is_baseline_first_prime\":{},\"used_deterministic_fallback\":{},\"exact_next_certified\":{},\"model\":{},\"hybrid_proof_contract\":{},\"proof_contract\":{},\"next_proof_contract\":{}}}",
            self.search_kind,
            self.start,
            self.window,
            self.top_k,
            self.score_limit,
            self.candidate_count,
            optional_u64_json(self.reported_prime),
            self.deterministically_verified,
            optional_u64_json(self.hinted_prime),
            optional_bool_json(self.hinted_prime_was_next),
            self.hybrid_deterministic_checks,
            optional_u64_json(self.baseline_first_prime),
            self.baseline_sequential_checks_to_first_prime,
            self.reported_prime_is_baseline_first_prime,
            self.used_deterministic_fallback,
            self.exact_next_certified,
            model.to_json(),
            fuzzy_hybrid_proof_contract_json(),
            prime_horizon_proof_contract_json(),
            next_prime_proof_contract_json()
        )
    }
}

pub fn fuzzy_hybrid_proof_contract_json() -> &'static str {
    "{\"name\":\"prime_fuzzy_hybrid_verified_prime_search_v0\",\"lean_module\":\"Circle.Core.Horizon\",\"theorem_ids\":[\"CC-T0073\",\"CC-T0074\",\"CC-T0075\",\"CC-T0076\",\"CC-T0077\"],\"lean_names\":[\"Circle.primeHorizon_iff_no_sqrt_contained\",\"Circle.primeHorizon_no_factor_below_sqrt\",\"Circle.primeHorizon_factor_bound\",\"Circle.primeHorizon_contains_prime\",\"Circle.primeHorizon_prime_of_contains\"],\"rust_domain\":\"u64_exact_arithmetic\",\"neural_role\":\"candidate_ordering_only\",\"deterministic_prefilter\":\"2/3/5 wheel candidates; skipped values are deterministically divisible by 2, 3, or 5 except handled small primes\",\"acceptance_rule\":\"a reported prime is accepted only after deterministic next-prime verification; exact-next claims use the Circle deterministic next-prime proof path, including static exact tables or verification of every earlier deterministic wheel candidate in the bounded window\",\"not_claimed\":[\"model weights are not theorem proved\",\"false positives and false negatives are expected and measured\",\"no candidate may be silently discarded in exact count/enumeration workflows\"]}"
}

pub fn fuzzy_search(
    model: &FuzzyPrimeModel,
    mode: FuzzySearchMode,
    start: u64,
    window: u64,
    top_k: usize,
) -> Result<FuzzySearch, String> {
    fuzzy_search_with_score_limit(model, mode, start, window, top_k, usize::MAX)
}

pub fn fuzzy_search_with_score_limit(
    model: &FuzzyPrimeModel,
    mode: FuzzySearchMode,
    start: u64,
    window: u64,
    top_k: usize,
    score_limit: usize,
) -> Result<FuzzySearch, String> {
    if window == 0 {
        return Err("fuzzy search window must be positive".to_string());
    }
    if top_k == 0 {
        return Err("fuzzy search top_k must be positive".to_string());
    }
    if score_limit == 0 {
        return Err("fuzzy search score_limit must be positive".to_string());
    }
    match mode {
        FuzzySearchMode::AnyPrime => {
            fuzzy_any_prime_search(model, start, window, top_k, score_limit)
        }
        FuzzySearchMode::ExactNext => fuzzy_exact_next_search(model, start, window, top_k),
    }
}

pub fn fuzzy_any_prime_value(
    model: &FuzzyPrimeModel,
    start: u64,
    window: u64,
    top_k: usize,
) -> Result<Option<u64>, String> {
    fuzzy_any_prime_value_with_score_limit(model, start, window, top_k, usize::MAX)
}

pub fn fuzzy_any_prime_value_with_score_limit(
    model: &FuzzyPrimeModel,
    start: u64,
    window: u64,
    top_k: usize,
    score_limit: usize,
) -> Result<Option<u64>, String> {
    if window == 0 {
        return Err("fuzzy search window must be positive".to_string());
    }
    if top_k == 0 {
        return Err("fuzzy search top_k must be positive".to_string());
    }
    if score_limit == 0 {
        return Err("fuzzy search score_limit must be positive".to_string());
    }
    Ok(fuzzy_any_prime_core(model, start, window, top_k, score_limit)?.reported_prime)
}

fn fuzzy_any_prime_search(
    model: &FuzzyPrimeModel,
    start: u64,
    window: u64,
    top_k: usize,
    score_limit: usize,
) -> Result<FuzzySearch, String> {
    let candidates = candidate_sequence(start, window)?;
    let effective_score_limit = score_limit.min(candidates.len());
    let core =
        fuzzy_any_prime_core_for_candidates(model, &candidates, top_k, effective_score_limit)?;
    let (baseline_prime, baseline_checks) = baseline_first_prime(&candidates);
    Ok(FuzzySearch {
        search_kind: "rust_fuzzy_any_prime_in_window",
        start,
        window,
        top_k,
        score_limit: effective_score_limit,
        candidate_count: candidates.len(),
        reported_prime: core.reported_prime,
        deterministically_verified: core.reported_prime.is_some(),
        hinted_prime: core.reported_prime,
        hinted_prime_was_next: Some(core.reported_prime == baseline_prime),
        hybrid_deterministic_checks: core.checked_count,
        baseline_first_prime: baseline_prime,
        baseline_sequential_checks_to_first_prime: baseline_checks,
        reported_prime_is_baseline_first_prime: core.reported_prime == baseline_prime,
        used_deterministic_fallback: core.used_fallback,
        exact_next_certified: false,
    })
}

fn fuzzy_any_prime_core(
    model: &FuzzyPrimeModel,
    start: u64,
    window: u64,
    top_k: usize,
    score_limit: usize,
) -> Result<FuzzyAnyPrimeCore, String> {
    let candidates = candidate_sequence(start, window)?;
    let effective_score_limit = score_limit.min(candidates.len());
    fuzzy_any_prime_core_for_candidates(model, &candidates, top_k, effective_score_limit)
}

fn fuzzy_any_prime_core_for_candidates(
    model: &FuzzyPrimeModel,
    candidates: &[u64],
    top_k: usize,
    score_limit: usize,
) -> Result<FuzzyAnyPrimeCore, String> {
    let scored = top_scored_candidates(model, &candidates[..score_limit], top_k)?;
    let mut checked = Vec::new();
    let mut reported_prime = None;
    let mut used_fallback = false;
    for &(_, candidate) in &scored {
        checked.push(candidate);
        if is_prime_u64(candidate).is_prime() {
            reported_prime = Some(candidate);
            break;
        }
    }
    if reported_prime.is_none() {
        used_fallback = true;
        for &candidate in candidates {
            if checked.contains(&candidate) {
                continue;
            }
            checked.push(candidate);
            if is_prime_u64(candidate).is_prime() {
                reported_prime = Some(candidate);
                break;
            }
        }
    }
    Ok(FuzzyAnyPrimeCore {
        reported_prime,
        checked_count: checked.len() as u64,
        used_fallback,
    })
}

fn fuzzy_exact_next_search(
    model: &FuzzyPrimeModel,
    start: u64,
    window: u64,
    top_k: usize,
) -> Result<FuzzySearch, String> {
    let high = start
        .checked_add(window)
        .ok_or_else(|| "fuzzy search window exceeds u64 range".to_string())?;
    let candidates = candidate_sequence(start, window)?;
    let hint_limit = top_k.min(candidates.len());

    let deterministic = next_prime_u64(start);
    let exact_next = deterministic.prime.filter(|&prime| prime < high);
    let baseline_checks = if exact_next.is_some() {
        deterministic.candidate_count
    } else {
        candidates.len() as u64
    };

    let hinted_candidate = best_scored_candidate(model, &candidates[..hint_limit])?;
    let hinted_prime = if hinted_candidate == exact_next {
        exact_next
    } else {
        None
    };

    Ok(FuzzySearch {
        search_kind: "rust_fuzzy_exact_next_prime_in_window",
        start,
        window,
        top_k,
        score_limit: hint_limit,
        candidate_count: candidates.len(),
        reported_prime: exact_next,
        deterministically_verified: exact_next.is_some(),
        hinted_prime,
        hinted_prime_was_next: Some(hinted_prime == exact_next),
        hybrid_deterministic_checks: baseline_checks,
        baseline_first_prime: exact_next,
        baseline_sequential_checks_to_first_prime: baseline_checks,
        reported_prime_is_baseline_first_prime: true,
        used_deterministic_fallback: hinted_prime.is_none(),
        exact_next_certified: exact_next.is_some(),
    })
}

fn top_scored_candidates(
    model: &FuzzyPrimeModel,
    candidates: &[u64],
    top_k: usize,
) -> Result<Vec<(f64, u64)>, String> {
    let mut top: Vec<(f64, u64)> = Vec::with_capacity(top_k.min(candidates.len()));
    for &candidate in candidates {
        let scored = (model.logit_score(candidate)?, candidate);
        let index = top.partition_point(|&(score, existing)| {
            score > scored.0 || (score == scored.0 && existing < scored.1)
        });
        if index < top_k {
            top.insert(index, scored);
            if top.len() > top_k {
                top.pop();
            }
        }
    }
    Ok(top)
}

fn best_scored_candidate(
    model: &FuzzyPrimeModel,
    candidates: &[u64],
) -> Result<Option<u64>, String> {
    let mut best: Option<(f64, u64)> = None;
    for &candidate in candidates {
        let score = model.logit_score(candidate)?;
        match best {
            Some((best_score, best_candidate))
                if score < best_score || (score == best_score && candidate >= best_candidate) => {}
            _ => best = Some((score, candidate)),
        }
    }
    Ok(best.map(|(_, candidate)| candidate))
}

fn candidate_sequence(start: u64, window: u64) -> Result<Vec<u64>, String> {
    let high = start
        .checked_add(window)
        .ok_or_else(|| "fuzzy search window exceeds u64 range".to_string())?;
    let mut candidates = Vec::new();
    for small_prime in [2, 3, 5] {
        if start <= small_prime && small_prime < high {
            candidates.push(small_prime);
        }
    }
    let Some((mut candidate, mut wheel_index)) =
        first_fuzzy_wheel30_candidate_at_or_above(start.max(7))
    else {
        return Ok(candidates);
    };
    while candidate < high {
        candidates.push(candidate);
        let gap = FUZZY_WHEEL30_GAPS[wheel_index];
        let Some(next_candidate) = candidate.checked_add(gap) else {
            break;
        };
        candidate = next_candidate;
        wheel_index = (wheel_index + 1) % FUZZY_WHEEL30_GAPS.len();
    }
    Ok(candidates)
}

fn first_fuzzy_wheel30_candidate_at_or_above(start: u64) -> Option<(u64, usize)> {
    let residue = (start % 30) as usize;
    let delta = FUZZY_WHEEL30_DELTA_BY_RESIDUE[residue];
    let index = FUZZY_WHEEL30_INDEX_BY_RESIDUE[residue];
    start.checked_add(delta).map(|candidate| (candidate, index))
}

fn baseline_first_prime(candidates: &[u64]) -> (Option<u64>, u64) {
    let mut checks = 0u64;
    for &candidate in candidates {
        checks += 1;
        if is_prime_u64(candidate).is_prime() {
            return (Some(candidate), checks);
        }
    }
    (None, checks)
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

fn sigmoid(x: f64) -> f64 {
    if x >= 0.0 {
        let z = (-x).exp();
        1.0 / (1.0 + z)
    } else {
        let z = x.exp();
        z / (1.0 + z)
    }
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

fn optional_u64_json(value: Option<u64>) -> String {
    value.map_or_else(|| "null".to_string(), |n| n.to_string())
}

fn optional_bool_json(value: Option<bool>) -> String {
    value.map_or_else(|| "null".to_string(), |flag| flag.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_model() -> FuzzyPrimeModel {
        FuzzyPrimeModel {
            bit_width: 8,
            residue_moduli: vec![3, 5],
            weights: vec![0.0; 10],
            bias: 0.0,
        }
    }

    #[test]
    fn model_text_round_trips() {
        let model = test_model();
        let parsed = FuzzyPrimeModel::from_text(&model.to_text()).unwrap();
        assert_eq!(parsed, model);
    }

    #[test]
    fn model_text_round_trips_empty_residue_list() {
        let model = FuzzyPrimeModel {
            bit_width: 8,
            residue_moduli: Vec::new(),
            weights: vec![0.0; 8],
            bias: 0.0,
        };
        let text = model.to_text();
        assert!(text.contains("residue_moduli none\n"));
        let parsed = FuzzyPrimeModel::from_text(&text).unwrap();
        assert_eq!(parsed, model);
    }

    #[test]
    fn rejects_wrong_weight_count() {
        let raw = "circle_fuzzy_model_v0\nbit_width 8\nresidue_moduli 3,5\nweights 0,0\nbias 0\n";
        assert!(FuzzyPrimeModel::from_text(raw)
            .unwrap_err()
            .contains("expected 10"));
    }

    #[test]
    fn exact_next_certifies_first_prime() {
        let search = fuzzy_search(&test_model(), FuzzySearchMode::ExactNext, 14, 16, 3).unwrap();
        assert_eq!(search.reported_prime, Some(17));
        assert!(search.exact_next_certified);
        assert!(search.reported_prime_is_baseline_first_prime);
    }

    #[test]
    fn deterministic_prefilter_uses_wheel_candidates() {
        let search = fuzzy_search(&test_model(), FuzzySearchMode::ExactNext, 100, 32, 4).unwrap();
        assert_eq!(search.reported_prime, Some(101));
        assert_eq!(search.candidate_count, 9);
        assert!(search.exact_next_certified);
    }
}
