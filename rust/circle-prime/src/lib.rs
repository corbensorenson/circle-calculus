pub mod coil;
pub mod controls;
pub mod scalar;
pub mod segmented;
mod tables;

pub use coil::{
    coil_signature, coil_spectrum, contains_horizon, contains_smaller_horizon, horizon_collision,
    inspect_horizon, literal_orbit, CoilSignature, HorizonCollision, HorizonInspection,
};
pub use controls::{
    control_primal_sieve_prime_count, control_simple_sieve_prime_count,
    control_trial_division_prime_count, control_trial_division_prime_count_checked,
};
pub use scalar::{
    is_prime_u64, miller_rabin_round, next_prime_u64, prime_horizon_proof_contract_json,
    prime_range_count_proof_contract_json, NextPrimeSearch, PrimeDecision, PrimeStatus,
    ANGLE_BUNDLE_HORIZON_MAX, ANGLE_BUNDLE_HORIZON_PRODUCTS, MR64_BASES, PRIME_HORIZON_LEAN_NAMES,
    PRIME_HORIZON_THEOREM_IDS, PRIME_RANGE_COUNT_LEAN_NAMES, PRIME_RANGE_COUNT_THEOREM_IDS,
    SMALL_PRIME_HORIZONS,
};
pub use segmented::{
    base_primes, effective_parallel_thread_count, for_each_prime_in_range, prime_count_in_range,
    prime_count_in_range_bitpacked, prime_count_in_range_hybrid_wheel30_marks,
    prime_count_in_range_hybrid_wheel30_marks_parallel, prime_count_in_range_parallel,
    prime_count_in_range_parallel_balanced, prime_count_in_range_parallel_dynamic,
    prime_count_in_range_prefix_pi, prime_count_in_range_presieve13,
    prime_count_in_range_presieve13_parallel, prime_count_in_range_presieve17,
    prime_count_in_range_presieve17_parallel, prime_count_in_range_tracked_bytes,
    prime_count_in_range_wheel30, prime_count_in_range_wheel30_marks,
    prime_count_in_range_wheel30_marks_parallel, prime_pi_u64, primes_in_range,
    recommended_count_mode, recommended_count_segment_size, recommended_segment_size, RangeError,
    DEFAULT_SEGMENT_SIZE, HIGH_OFFSET_SEGMENT_SIZE, PARALLEL_MEDIUM_PREFIX_COUNT_MODE,
    PARALLEL_MEDIUM_PREFIX_SEGMENT_SIZE, PARALLEL_SMALL_PREFIX_COUNT_MODE,
    PARALLEL_SMALL_PREFIX_SEGMENT_SIZE, PARALLEL_TINY_PREFIX_COUNT_MODE,
    PARALLEL_TINY_PREFIX_SEGMENT_SIZE, PARALLEL_VERY_HIGH_OFFSET_COUNT_MODE,
    PARALLEL_VERY_HIGH_OFFSET_SEGMENT_SIZE, VERY_HIGH_OFFSET_SEGMENT_SIZE,
};
