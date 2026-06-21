//! Prime and horizon utilities for Circle Calculus.
//!
//! This crate is intentionally focused on prime decisions, prime counts,
//! horizon/coil inspection, and command-line support for the public Circle
//! Calculus proof-contract artifacts. It is not the home for the Lean theorem
//! corpus or the Python reference models.

pub mod bigint;
pub mod coil;
pub mod controls;
pub mod fuzzy;
pub mod scalar;
pub mod segmented;
mod tables;

pub use bigint::{
    big_fuzzy_any_prime_search, big_fuzzy_any_prime_value, big_fuzzy_hybrid_contract_json,
    big_probable_prime_contract_json, is_bpsw_probable_prime_biguint, is_probable_prime_biguint,
    max_big_miller_rabin_rounds, next_bpsw_probable_prime_biguint, next_probable_prime_biguint,
    parse_biguint, BigFuzzyPrimeModel, BigFuzzySearch, BigNextPrimeSearch, BigPrimeDecision,
    BigPrimeStatus, DEFAULT_BIG_FUZZY_CANDIDATE_WINDOW, DEFAULT_BIG_MILLER_RABIN_ROUNDS,
    DEFAULT_BIG_NEXT_MAX_CANDIDATES,
};
pub use coil::{
    coil_signature, coil_spectrum, contains_horizon, contains_smaller_horizon, horizon_collision,
    inspect_horizon, literal_orbit, CoilSignature, HorizonCollision, HorizonInspection,
};
pub use controls::{
    control_primal_sieve_prime_count, control_simple_sieve_prime_count,
    control_trial_division_prime_count, control_trial_division_prime_count_checked,
};
pub use fuzzy::{
    fuzzy_any_prime_value, fuzzy_any_prime_value_with_score_limit,
    fuzzy_hybrid_proof_contract_json, fuzzy_search, fuzzy_search_with_score_limit, FuzzyPrimeModel,
    FuzzySearch, FuzzySearchMode,
};
pub use scalar::{
    is_prime_u64, miller_rabin_round, next_prime_proof_contract_json, next_prime_u64,
    next_prime_value_u64, prime_horizon_proof_contract_json, prime_range_count_proof_contract_json,
    NextPrimeSearch, PrimeDecision, PrimeStatus, ANGLE_BUNDLE_HORIZON_MAX,
    ANGLE_BUNDLE_HORIZON_PRODUCTS, MR64_BASES, NEXT_PRIME_LEAN_NAMES, NEXT_PRIME_THEOREM_IDS,
    PRIME_HORIZON_LEAN_NAMES, PRIME_HORIZON_THEOREM_IDS, PRIME_RANGE_COUNT_LEAN_NAMES,
    PRIME_RANGE_COUNT_THEOREM_IDS, SMALL_PRIME_HORIZONS,
};
pub use segmented::{
    base_primes, effective_parallel_thread_count, effective_prefix_pi_thread_count,
    for_each_prime_in_range, prime_count_in_range, prime_count_in_range_bitpacked,
    prime_count_in_range_hybrid_wheel30_marks, prime_count_in_range_hybrid_wheel30_marks_parallel,
    prime_count_in_range_parallel, prime_count_in_range_parallel_balanced,
    prime_count_in_range_parallel_dynamic, prime_count_in_range_prefix_pi,
    prime_count_in_range_prefix_pi_parallel, prime_count_in_range_presieve13,
    prime_count_in_range_presieve13_parallel, prime_count_in_range_presieve13_with_scratch,
    prime_count_in_range_presieve17, prime_count_in_range_presieve17_parallel,
    prime_count_in_range_presieve17_with_scratch, prime_count_in_range_small_prefix_pi,
    prime_count_in_range_tracked_bytes, prime_count_in_range_wheel30,
    prime_count_in_range_wheel30_marks, prime_count_in_range_wheel30_marks_parallel,
    prime_count_in_range_with_scratch, prime_count_shifted_single_segment_presieve13_with_scratch,
    prime_count_shifted_single_segment_presieve17_with_scratch, prime_pi_u64, primes_in_range,
    recommended_count_mode, recommended_count_segment_size, recommended_segment_size,
    small_prefix_pi_cache_limit, warm_small_prefix_pi_cache, PrimeCountScratch, RangeError,
    BASE_PRIME_CACHE_LIMIT, DEFAULT_SEGMENT_SIZE, HIGH_OFFSET_SEGMENT_SIZE,
    PARALLEL_EDGE_HIGH_OFFSET_COUNT_MODE, PARALLEL_EDGE_HIGH_OFFSET_MIN_BASE_LIMIT,
    PARALLEL_LOWER_HIGH_OFFSET_BASE_LIMIT, PARALLEL_LOWER_HIGH_OFFSET_COUNT_MODE,
    PARALLEL_LOWER_HIGH_OFFSET_MIN_BASE_LIMIT, PARALLEL_MEDIUM_PREFIX_COUNT_MODE,
    PARALLEL_MEDIUM_PREFIX_SEGMENT_SIZE, PARALLEL_SMALL_PREFIX_COUNT_MODE,
    PARALLEL_SMALL_PREFIX_SEGMENT_SIZE, PARALLEL_TINY_PREFIX_COUNT_MODE,
    PARALLEL_TINY_PREFIX_SEGMENT_SIZE, PARALLEL_UPPER_HIGH_OFFSET_COUNT_MODE,
    PARALLEL_UPPER_HIGH_OFFSET_MIN_BASE_LIMIT, PARALLEL_UPPER_HIGH_OFFSET_SEGMENT_SIZE,
    PARALLEL_VERY_HIGH_OFFSET_COUNT_MODE, PARALLEL_VERY_HIGH_OFFSET_SEGMENT_SIZE,
    SMALL_PREFIX_PI_CACHE_LIMIT, SMALL_PREFIX_PI_CACHE_LIMIT_ENV, SMALL_PREFIX_PI_CACHE_MAX_LIMIT,
    VERY_HIGH_OFFSET_SEGMENT_SIZE,
};
