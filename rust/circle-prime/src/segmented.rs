use std::collections::HashMap;
use std::convert::TryFrom;
use std::ptr;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::OnceLock;
use std::thread;

use crate::scalar::is_prime_u64;
use crate::tables::{STATIC_BASE_PRIMES_U64, STATIC_BASE_PRIME_LIMIT};

const PRESIEVE13_MODULUS: u64 = 30_030;
const PRESIEVE13_ODD_PERIOD: usize = (PRESIEVE13_MODULUS as usize) / 2;
const PRESIEVE17_MODULUS: u64 = 510_510;
const PRESIEVE17_ODD_PERIOD: usize = (PRESIEVE17_MODULUS as usize) / 2;
const PRESIEVE19_MODULUS: u64 = 9_699_690;
const PRESIEVE19_ODD_PERIOD: usize = (PRESIEVE19_MODULUS as usize) / 2;
const WHEEL30_COUNT_BELOW_RESIDUE: [u8; 30] = [
    0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7,
];
const WHEEL30_INDEX_BY_RESIDUE: [i8; 30] = [
    -1, 0, -1, -1, -1, -1, -1, 1, -1, -1, -1, 2, -1, 3, -1, -1, -1, 4, -1, 5, -1, -1, -1, 6, -1,
    -1, -1, -1, -1, 7,
];
const WHEEL30_GAP_BY_RESIDUE: [u8; 30] = [
    0, 6, 0, 0, 0, 0, 0, 4, 0, 0, 0, 2, 0, 4, 0, 0, 0, 2, 0, 4, 0, 0, 0, 6, 0, 0, 0, 0, 0, 2,
];
const WHEEL30_HALF_GAP_BY_INDEX: [usize; 8] = [3, 2, 1, 2, 1, 2, 3, 1];
const BASE_PRIME_ODD_BYTE_LIMIT: u64 = 10_000_000;
const BASE_PRIME_BITSET_LIMIT: u64 = 100_000_000;
const SCALAR_RANGE_FALLBACK_SPAN_LIMIT: u64 = 1_000_000;
const DENSE_MARKING_BASE_LIMIT: u64 = 300_000;
const HYBRID_DENSE_STEP_DIVISOR: usize = 4;
const DYNAMIC_PARALLEL_MAX_SEGMENTS_PER_BATCH: u64 = 64;
const DYNAMIC_PARALLEL_TARGET_BATCHES_PER_WORKER: u64 = 4;
const PRIME_PI_PHI_SMALL_PRIME_COUNT: usize = 6;
const PRIME_PI_PHI_SMALL_MODULUS: u64 = 30_030;
const PREFIX_PI_DEFAULT_SPAN_LIMIT: u64 = 1_000_000_000;
const PREFIX_PI_RANGE_DEFAULT_SPAN_FLOOR: u64 = 128_000_000;
const PREFIX_PI_RANGE_DEFAULT_HIGH_LIMIT: u64 = 3_000_000_000;
pub const DEFAULT_SEGMENT_SIZE: u64 = 1 << 18;
include!(concat!(env!("OUT_DIR"), "/prime_engine_defaults.rs"));
pub const HIGH_OFFSET_SEGMENT_SIZE: u64 = 1 << 20;
pub const VERY_HIGH_OFFSET_SEGMENT_SIZE: u64 = 1 << 22;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RangeError {
    SegmentSizeZero,
    ThreadCountZero,
    SegmentTooLarge,
    BaseLimitTooLarge,
    WorkerPanic,
}

#[derive(Debug, Clone)]
struct SieveCursor {
    q: usize,
    square: u64,
    next: u64,
}

#[derive(Debug, Clone)]
struct Wheel30MarkCursor {
    q: usize,
    square: u64,
    next: u64,
    gap_index: u8,
}

#[derive(Debug, Clone)]
struct Wheel30Cursor {
    q: u64,
    next: u64,
    next_index: u64,
    multiplier_residue: u8,
}

pub fn base_primes(limit: u64) -> Result<Vec<u64>, RangeError> {
    if limit <= STATIC_BASE_PRIME_LIMIT {
        Ok(base_primes_static(limit))
    } else if limit <= BASE_PRIME_ODD_BYTE_LIMIT {
        base_primes_odd_bytes(limit)
    } else if limit <= BASE_PRIME_BITSET_LIMIT {
        base_primes_bitset(limit)
    } else {
        Err(RangeError::BaseLimitTooLarge)
    }
}

fn base_primes_static(limit: u64) -> Vec<u64> {
    base_primes_static_slice(limit).to_vec()
}

fn base_primes_static_slice(limit: u64) -> &'static [u64] {
    let count = if limit >= STATIC_BASE_PRIME_LIMIT {
        STATIC_BASE_PRIMES_U64.len()
    } else {
        STATIC_BASE_PRIMES_U64.partition_point(|&prime| prime <= limit)
    };
    &STATIC_BASE_PRIMES_U64[..count]
}

fn with_base_primes<R, F>(limit: u64, f: F) -> Result<R, RangeError>
where
    F: FnOnce(&[u64]) -> Result<R, RangeError>,
{
    if limit <= STATIC_BASE_PRIME_LIMIT {
        f(base_primes_static_slice(limit))
    } else {
        let base = base_primes(limit)?;
        f(&base)
    }
}

fn active_sieving_base_primes(base: &[u64], limit: u64, presieved_through: u64) -> &[u64] {
    let start = base.partition_point(|&q| q <= presieved_through);
    let end = start + base[start..].partition_point(|&q| q <= limit);
    &base[start..end]
}

fn split_base_primes_by_dense_step(
    active_base: &[u64],
    dense_step_limit: usize,
) -> (&[u64], &[u64]) {
    let split = active_base.partition_point(|&q| q <= dense_step_limit as u64);
    active_base.split_at(split)
}

fn base_primes_odd_bytes(limit: u64) -> Result<Vec<u64>, RangeError> {
    if limit < 2 {
        return Ok(Vec::new());
    }
    if limit == 2 {
        return Ok(vec![2]);
    }

    let odd_count =
        usize::try_from(((limit - 3) / 2) + 1).map_err(|_| RangeError::BaseLimitTooLarge)?;
    let mut sieve = vec![1u8; odd_count];

    let stop = limit.isqrt();
    let mut index = 0usize;
    while 2 * index as u64 + 3 <= stop {
        if sieve[index] != 0 {
            let p = 2 * index as u64 + 3;
            let mut multiple_index =
                usize::try_from((p * p - 3) / 2).map_err(|_| RangeError::BaseLimitTooLarge)?;
            let step = usize::try_from(p).map_err(|_| RangeError::BaseLimitTooLarge)?;
            while multiple_index < odd_count {
                sieve[multiple_index] = 0;
                multiple_index += step;
            }
        }
        index += 1;
    }

    let mut primes = Vec::new();
    primes.push(2);
    primes.extend(
        sieve
            .into_iter()
            .enumerate()
            .filter_map(|(index, is_prime)| (is_prime != 0).then_some(2 * index as u64 + 3)),
    );
    Ok(primes)
}

fn base_primes_bitset(limit: u64) -> Result<Vec<u64>, RangeError> {
    if limit < 2 {
        return Ok(Vec::new());
    }
    let len = usize::try_from(limit + 1).map_err(|_| RangeError::BaseLimitTooLarge)?;
    let mut sieve = vec![true; len];
    sieve[0] = false;
    sieve[1] = false;

    let stop = limit.isqrt();
    for p in 2..=stop {
        if sieve[p as usize] {
            let mut multiple = p * p;
            while multiple <= limit {
                sieve[multiple as usize] = false;
                multiple += p;
            }
        }
    }

    Ok(sieve
        .into_iter()
        .enumerate()
        .filter_map(|(index, is_prime)| is_prime.then_some(index as u64))
        .collect())
}

struct PrimePiCounter {
    primes: Vec<u64>,
    pi_memo: HashMap<u64, u64>,
    phi_memo: HashMap<(u64, usize), u64>,
}

impl PrimePiCounter {
    fn new(primes: Vec<u64>) -> Self {
        Self {
            primes,
            pi_memo: HashMap::new(),
            phi_memo: HashMap::new(),
        }
    }

    fn pi(&mut self, n: u64) -> u64 {
        if n < 2 {
            return 0;
        }
        if n <= STATIC_BASE_PRIME_LIMIT {
            return static_base_prime_pi(n);
        }
        if let Some(&count) = self.pi_memo.get(&n) {
            return count;
        }

        let a = self.pi(n.isqrt().isqrt()) as usize;
        let b = self.pi(n.isqrt()) as usize;
        let c = self.pi(integer_cuberoot(n)) as usize;
        let a_u64 = a as u64;
        let b_u64 = b as u64;
        let mut count = self.phi(n, a) + ((b_u64 + a_u64 - 2) * (b_u64 - a_u64 + 1)) / 2;

        for i in a..b {
            let w = n / self.primes[i];
            count -= self.pi(w);
            if i < c {
                let limit = self.pi(w.isqrt()) as usize;
                for j in i..limit {
                    count -= self.pi(w / self.primes[j]) - j as u64;
                }
            }
        }

        self.pi_memo.insert(n, count);
        count
    }

    fn phi(&mut self, x: u64, a: usize) -> u64 {
        if a == 0 {
            return x;
        }
        if a == PRIME_PI_PHI_SMALL_PRIME_COUNT {
            return prime_pi_phi_small(x);
        }
        if a < PRIME_PI_PHI_SMALL_PRIME_COUNT {
            return self.phi(x, a - 1) - self.phi(x / self.primes[a - 1], a - 1);
        }
        if let Some(&count) = self.phi_memo.get(&(x, a)) {
            return count;
        }

        let mut count = prime_pi_phi_small(x);
        for i in PRIME_PI_PHI_SMALL_PRIME_COUNT..a {
            let prime = self.primes[i];
            if prime > x {
                break;
            }
            count -= self.phi(x / prime, i);
        }

        self.phi_memo.insert((x, a), count);
        count
    }
}

fn static_base_prime_pi(n: u64) -> u64 {
    STATIC_BASE_PRIMES_U64.partition_point(|&prime| prime <= n) as u64
}

fn prime_pi_phi_small(x: u64) -> u64 {
    let prefix = prime_pi_phi_small_prefix();
    let full_periods = x / PRIME_PI_PHI_SMALL_MODULUS;
    let remainder = (x % PRIME_PI_PHI_SMALL_MODULUS) as usize;
    let period_count = u64::from(prefix[PRIME_PI_PHI_SMALL_MODULUS as usize]);
    full_periods * period_count + u64::from(prefix[remainder])
}

fn prime_pi_phi_small_prefix() -> &'static [u16] {
    static PREFIX: OnceLock<Vec<u16>> = OnceLock::new();
    PREFIX.get_or_init(|| {
        let mut prefix = Vec::with_capacity(PRIME_PI_PHI_SMALL_MODULUS as usize + 1);
        let mut count = 0u16;
        prefix.push(count);
        for value in 1..=PRIME_PI_PHI_SMALL_MODULUS {
            if [2, 3, 5, 7, 11, 13].iter().all(|&prime| value % prime != 0) {
                count += 1;
            }
            prefix.push(count);
        }
        prefix
    })
}

fn integer_cuberoot(n: u64) -> u64 {
    let mut low = 0u64;
    let mut high = 1u64;
    while cube_leq(high, n) {
        high = high.saturating_mul(2);
    }
    while low + 1 < high {
        let mid = low + (high - low) / 2;
        if cube_leq(mid, n) {
            low = mid;
        } else {
            high = mid;
        }
    }
    low
}

fn cube_leq(value: u64, limit: u64) -> bool {
    let value = value as u128;
    value * value * value <= limit as u128
}

pub fn for_each_prime_in_range<F>(
    mut low: u64,
    high: u64,
    segment_size: u64,
    mut on_prime: F,
) -> Result<(), RangeError>
where
    F: FnMut(u64),
{
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(());
    }
    if use_scalar_range_fallback(low, high) {
        return for_each_prime_in_range_scalar(low, high, on_prime);
    }

    for prime in [2, 3, 5, 7, 11, 13, 17, 19] {
        if low <= prime && prime < high {
            on_prime(prime);
        }
    }
    if high <= 23 {
        return Ok(());
    }

    low = low.max(23);
    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        for_each_presieved_odd_prime_with_base(low, high, segment_size, base, on_prime)
    })
}

pub fn prime_count_in_range(low: u64, high: u64, segment_size: u64) -> Result<usize, RangeError> {
    prime_count_in_range_odd_bytes(low, high, segment_size)
}

pub fn prime_pi_u64(n: u64) -> Result<usize, RangeError> {
    if n < 2 {
        return Ok(0);
    }

    let base = base_primes(n.isqrt())?;
    prime_pi_u64_with_base(n, base)
}

fn prime_pi_u64_with_base(n: u64, base: Vec<u64>) -> Result<usize, RangeError> {
    let mut counter = PrimePiCounter::new(base);
    usize::try_from(counter.pi(n)).map_err(|_| RangeError::BaseLimitTooLarge)
}

pub fn prime_count_in_range_prefix_pi(low: u64, high: u64) -> Result<usize, RangeError> {
    if high <= low {
        return Ok(0);
    }

    let base = base_primes((high - 1).isqrt())?;
    let mut counter = PrimePiCounter::new(base);
    let high_count = counter.pi(high - 1);
    let low_count = if low == 0 { 0 } else { counter.pi(low - 1) };
    usize::try_from(high_count - low_count).map_err(|_| RangeError::BaseLimitTooLarge)
}

pub fn effective_prefix_pi_thread_count(low: u64, high: u64, requested_threads: usize) -> usize {
    if requested_threads == 0 {
        return 0;
    }
    if low > 0
        && high > low
        && high - low >= PREFIX_PI_RANGE_DEFAULT_SPAN_FLOOR
        && requested_threads > 1
    {
        requested_threads.min(2)
    } else {
        1
    }
}

pub fn prime_count_in_range_prefix_pi_parallel(
    low: u64,
    high: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if effective_prefix_pi_thread_count(low, high, threads) <= 1 {
        return prime_count_in_range_prefix_pi(low, high);
    }

    let base = base_primes((high - 1).isqrt())?;
    let low_base = base.clone();

    thread::scope(|scope| {
        let high_handle = scope.spawn(move || prime_pi_u64_with_base(high - 1, base));
        let low_handle = scope.spawn(move || prime_pi_u64_with_base(low - 1, low_base));
        let high_count = high_handle.join().map_err(|_| RangeError::WorkerPanic)??;
        let low_count = low_handle.join().map_err(|_| RangeError::WorkerPanic)??;
        Ok(high_count - low_count)
    })
}

pub fn prime_count_in_range_bitpacked(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_bitpacked_with_base(low, high, segment_size, base)
    })
}

pub fn prime_count_in_range_tracked_bytes(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_tracked_bytes_with_base(low, high, segment_size, base)
    })
}

pub fn prime_count_in_range_presieve13(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_odd_bytes_presieve13_with_base(low, high, segment_size, base)
    })
}

pub fn prime_count_in_range_presieve13_parallel(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if threads == 1 || high <= low {
        return prime_count_in_range_presieve13(low, high, segment_size);
    }
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    let workers = effective_parallel_thread_count(low, high, segment_size, threads);
    if workers <= 1 {
        return prime_count_in_range_presieve13(low, high, segment_size);
    }
    if use_scalar_range_fallback(low, high) {
        return prime_count_in_range_scalar_parallel(low, high, workers);
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        let chunks = split_range(low, high, workers);
        thread::scope(|scope| {
            let mut handles = Vec::with_capacity(chunks.len());
            for (chunk_low, chunk_high) in chunks {
                handles.push(scope.spawn(move || {
                    prime_count_in_range_odd_bytes_presieve13_with_base(
                        chunk_low,
                        chunk_high,
                        segment_size,
                        base,
                    )
                }));
            }

            let mut total = 0usize;
            for handle in handles {
                total += handle.join().map_err(|_| RangeError::WorkerPanic)??;
            }
            Ok(total)
        })
    })
}

pub fn prime_count_in_range_presieve17(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_odd_bytes_presieve17_with_base(low, high, segment_size, base)
    })
}

pub fn prime_count_in_range_presieve17_parallel(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if threads == 1 || high <= low {
        return prime_count_in_range_presieve17(low, high, segment_size);
    }
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    let workers = effective_parallel_thread_count(low, high, segment_size, threads);
    if workers <= 1 {
        return prime_count_in_range_presieve17(low, high, segment_size);
    }
    if use_scalar_range_fallback(low, high) {
        return prime_count_in_range_scalar_parallel(low, high, workers);
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        let chunks = split_range(low, high, workers);
        thread::scope(|scope| {
            let mut handles = Vec::with_capacity(chunks.len());
            for (chunk_low, chunk_high) in chunks {
                handles.push(scope.spawn(move || {
                    prime_count_in_range_odd_bytes_presieve17_with_base(
                        chunk_low,
                        chunk_high,
                        segment_size,
                        base,
                    )
                }));
            }

            let mut total = 0usize;
            for handle in handles {
                total += handle.join().map_err(|_| RangeError::WorkerPanic)??;
            }
            Ok(total)
        })
    })
}

pub fn prime_count_in_range_wheel30(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_wheel30_with_base(low, high, segment_size, base)
    })
}

pub fn prime_count_in_range_wheel30_marks(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_wheel30_marks_with_base(low, high, segment_size, base)
    })
}

pub fn prime_count_in_range_wheel30_marks_parallel(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if threads == 1 || high <= low {
        return prime_count_in_range_wheel30_marks(low, high, segment_size);
    }
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    let workers = effective_parallel_thread_count(low, high, segment_size, threads);
    if workers <= 1 {
        return prime_count_in_range_wheel30_marks(low, high, segment_size);
    }
    if use_scalar_range_fallback(low, high) {
        return prime_count_in_range_scalar_parallel(low, high, workers);
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        let chunks = split_range(low, high, workers);
        thread::scope(|scope| {
            let mut handles = Vec::with_capacity(chunks.len());
            for (chunk_low, chunk_high) in chunks {
                handles.push(scope.spawn(move || {
                    prime_count_in_range_wheel30_marks_with_base(
                        chunk_low,
                        chunk_high,
                        segment_size,
                        base,
                    )
                }));
            }

            let mut total = 0usize;
            for handle in handles {
                total += handle.join().map_err(|_| RangeError::WorkerPanic)??;
            }
            Ok(total)
        })
    })
}

pub fn prime_count_in_range_hybrid_wheel30_marks(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_hybrid_wheel30_marks_with_base(low, high, segment_size, base)
    })
}

pub fn prime_count_in_range_hybrid_wheel30_marks_parallel(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if threads == 1 || high <= low {
        return prime_count_in_range_hybrid_wheel30_marks(low, high, segment_size);
    }
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    let workers = effective_parallel_thread_count(low, high, segment_size, threads);
    if workers <= 1 {
        return prime_count_in_range_hybrid_wheel30_marks(low, high, segment_size);
    }
    if use_scalar_range_fallback(low, high) {
        return prime_count_in_range_scalar_parallel(low, high, workers);
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        let chunks = split_range(low, high, workers);
        thread::scope(|scope| {
            let mut handles = Vec::with_capacity(chunks.len());
            for (chunk_low, chunk_high) in chunks {
                handles.push(scope.spawn(move || {
                    prime_count_in_range_hybrid_wheel30_marks_with_base(
                        chunk_low,
                        chunk_high,
                        segment_size,
                        base,
                    )
                }));
            }

            let mut total = 0usize;
            for handle in handles {
                total += handle.join().map_err(|_| RangeError::WorkerPanic)??;
            }
            Ok(total)
        })
    })
}

pub fn prime_count_in_range_parallel(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if threads == 1 || high <= low {
        return prime_count_in_range(low, high, segment_size);
    }
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    let workers = effective_parallel_thread_count(low, high, segment_size, threads);
    if workers <= 1 {
        return prime_count_in_range(low, high, segment_size);
    }
    if use_scalar_range_fallback(low, high) {
        return prime_count_in_range_scalar_parallel(low, high, workers);
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        let chunks = split_range(low, high, workers);
        thread::scope(|scope| {
            let mut handles = Vec::with_capacity(chunks.len());
            for (chunk_low, chunk_high) in chunks {
                handles.push(scope.spawn(move || {
                    prime_count_in_range_odd_bytes_with_base(
                        chunk_low,
                        chunk_high,
                        segment_size,
                        base,
                    )
                }));
            }

            let mut total = 0usize;
            for handle in handles {
                total += handle.join().map_err(|_| RangeError::WorkerPanic)??;
            }
            Ok(total)
        })
    })
}

pub fn prime_count_in_range_parallel_balanced(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if threads == 1 || high <= low {
        return prime_count_in_range(low, high, segment_size);
    }
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    let workers = effective_parallel_thread_count(low, high, segment_size, threads);
    if workers <= 1 {
        return prime_count_in_range(low, high, segment_size);
    }
    if use_scalar_range_fallback(low, high) {
        return prime_count_in_range_scalar_parallel(low, high, workers);
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        let chunks = split_range_by_sieve_work(low, high, workers);
        thread::scope(|scope| {
            let mut handles = Vec::with_capacity(chunks.len());
            for (chunk_low, chunk_high) in chunks {
                handles.push(scope.spawn(move || {
                    prime_count_in_range_odd_bytes_with_base(
                        chunk_low,
                        chunk_high,
                        segment_size,
                        base,
                    )
                }));
            }

            let mut total = 0usize;
            for handle in handles {
                total += handle.join().map_err(|_| RangeError::WorkerPanic)??;
            }
            Ok(total)
        })
    })
}

pub fn prime_count_in_range_parallel_dynamic(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads == 0 {
        return Err(RangeError::ThreadCountZero);
    }
    if threads == 1 || high <= low {
        return prime_count_in_range(low, high, segment_size);
    }
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    let workers = effective_parallel_thread_count(low, high, segment_size, threads);
    if workers <= 1 {
        return prime_count_in_range(low, high, segment_size);
    }
    if use_scalar_range_fallback(low, high) {
        return prime_count_in_range_scalar_parallel(low, high, workers);
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        let span = high - low;
        let segment_count = span.div_ceil(segment_size);
        let segments_per_batch = dynamic_parallel_segments_per_batch(segment_count, workers);
        let batch_count = segment_count.div_ceil(segments_per_batch);

        let next_batch = AtomicU64::new(0);
        thread::scope(|scope| {
            let mut handles = Vec::with_capacity(workers);
            for _ in 0..workers {
                let next_batch = &next_batch;
                handles.push(scope.spawn(move || {
                    let mut subtotal = 0usize;
                    loop {
                        let batch_index = next_batch.fetch_add(1, Ordering::Relaxed);
                        if batch_index >= batch_count {
                            break;
                        }
                        let start_segment = batch_index.saturating_mul(segments_per_batch);
                        let end_segment = start_segment
                            .saturating_add(segments_per_batch)
                            .min(segment_count);
                        let chunk_low = low + start_segment.saturating_mul(segment_size).min(span);
                        let chunk_high = low + end_segment.saturating_mul(segment_size).min(span);
                        if chunk_low < chunk_high {
                            subtotal += prime_count_in_range_odd_bytes_with_base(
                                chunk_low,
                                chunk_high,
                                segment_size,
                                base,
                            )?;
                        }
                    }
                    Ok(subtotal)
                }));
            }

            let mut total = 0usize;
            for handle in handles {
                total += handle.join().map_err(|_| RangeError::WorkerPanic)??;
            }
            Ok(total)
        })
    })
}

fn dynamic_parallel_segments_per_batch(segment_count: u64, workers: usize) -> u64 {
    let worker_count = u64::try_from(workers).unwrap_or(u64::MAX).max(1);
    let target_batches = worker_count
        .saturating_mul(DYNAMIC_PARALLEL_TARGET_BATCHES_PER_WORKER)
        .max(1);
    segment_count
        .div_ceil(target_batches)
        .clamp(1, DYNAMIC_PARALLEL_MAX_SEGMENTS_PER_BATCH)
}

pub fn effective_parallel_thread_count(
    low: u64,
    high: u64,
    segment_size: u64,
    requested_threads: usize,
) -> usize {
    if requested_threads == 0 || segment_size == 0 || high <= low {
        return requested_threads;
    }
    let segment_count = (high - low).div_ceil(segment_size);
    requested_threads.min(usize::try_from(segment_count).unwrap_or(usize::MAX).max(1))
}

pub fn recommended_segment_size(_low: u64, high: u64) -> u64 {
    let Some(last) = high.checked_sub(1) else {
        return DEFAULT_SEGMENT_SIZE;
    };
    let base_limit = last.isqrt();
    if base_limit >= 1_000_000 {
        VERY_HIGH_OFFSET_SEGMENT_SIZE
    } else if base_limit >= 300_000 {
        HIGH_OFFSET_SEGMENT_SIZE
    } else {
        DEFAULT_SEGMENT_SIZE
    }
}

pub fn recommended_count_segment_size(low: u64, high: u64, requested_threads: usize) -> u64 {
    let single_thread = recommended_segment_size(low, high);
    if requested_threads <= 1 || high <= low {
        return single_thread;
    }

    let span = high - low;
    let base_limit = (high - 1).isqrt();
    if base_limit >= 1_000_000 && span <= 16_000_000 {
        PARALLEL_VERY_HIGH_OFFSET_SEGMENT_SIZE
    } else if base_limit < 300_000 && span <= 2_000_000 {
        PARALLEL_TINY_PREFIX_SEGMENT_SIZE
    } else if base_limit < 300_000 && span <= 16_000_000 {
        PARALLEL_SMALL_PREFIX_SEGMENT_SIZE
    } else if base_limit < 300_000 && span <= 128_000_000 {
        PARALLEL_MEDIUM_PREFIX_SEGMENT_SIZE
    } else {
        single_thread
    }
}

pub fn recommended_count_mode(low: u64, high: u64, requested_threads: usize) -> &'static str {
    if high <= low {
        return "segmented";
    }

    let span = high - low;
    let base_limit = (high - 1).isqrt();
    if low == 0 && base_limit < 300_000 && span <= 2_000_000 {
        PARALLEL_TINY_PREFIX_COUNT_MODE
    } else if low == 0 && base_limit < 300_000 && span <= 16_000_000 {
        PARALLEL_SMALL_PREFIX_COUNT_MODE
    } else if low == 0 && base_limit < 300_000 && span <= 128_000_000 {
        PARALLEL_MEDIUM_PREFIX_COUNT_MODE
    } else if low == 0 && base_limit < 300_000 && span <= PREFIX_PI_DEFAULT_SPAN_LIMIT {
        "prefix-pi"
    } else if low > 0
        && base_limit < 100_000
        && span >= PREFIX_PI_RANGE_DEFAULT_SPAN_FLOOR
        && high <= PREFIX_PI_RANGE_DEFAULT_HIGH_LIMIT
    {
        "prefix-pi"
    } else if requested_threads <= 1 {
        "segmented"
    } else if base_limit >= 1_000_000 && span <= 16_000_000 {
        PARALLEL_VERY_HIGH_OFFSET_COUNT_MODE
    } else if base_limit < 300_000 && span <= 128_000_000 {
        "dynamic"
    } else {
        "segmented"
    }
}

pub fn primes_in_range(low: u64, high: u64, segment_size: u64) -> Result<Vec<u64>, RangeError> {
    let mut primes = Vec::new();
    for_each_prime_in_range(low, high, segment_size, |prime| {
        primes.push(prime);
    })?;
    Ok(primes)
}

fn use_scalar_range_fallback(low: u64, high: u64) -> bool {
    if high <= low || high - low > SCALAR_RANGE_FALLBACK_SPAN_LIMIT {
        return false;
    }
    high.checked_sub(1)
        .map(|last| last.isqrt() > BASE_PRIME_BITSET_LIMIT)
        .unwrap_or(false)
}

fn prime_count_in_range_scalar(low: u64, high: u64) -> usize {
    (low..high)
        .filter(|&candidate| is_prime_u64(candidate).is_prime())
        .count()
}

fn prime_count_in_range_scalar_parallel(
    low: u64,
    high: u64,
    threads: usize,
) -> Result<usize, RangeError> {
    if threads <= 1 || high <= low {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let chunks = split_range(low, high, threads);
    thread::scope(|scope| {
        let mut handles = Vec::with_capacity(chunks.len());
        for (chunk_low, chunk_high) in chunks {
            handles.push(scope.spawn(move || prime_count_in_range_scalar(chunk_low, chunk_high)));
        }

        let mut total = 0usize;
        for handle in handles {
            total += handle.join().map_err(|_| RangeError::WorkerPanic)?;
        }
        Ok(total)
    })
}

fn for_each_prime_in_range_scalar<F>(low: u64, high: u64, mut on_prime: F) -> Result<(), RangeError>
where
    F: FnMut(u64),
{
    for candidate in low..high {
        if is_prime_u64(candidate).is_prime() {
            on_prime(candidate);
        }
    }
    Ok(())
}

fn prime_count_in_range_odd_bytes(
    low: u64,
    high: u64,
    segment_size: u64,
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }
    if use_scalar_range_fallback(low, high) {
        return Ok(prime_count_in_range_scalar(low, high));
    }

    let limit = (high - 1).isqrt();
    with_base_primes(limit, |base| {
        prime_count_in_range_odd_bytes_with_base(low, high, segment_size, base)
    })
}

fn prime_count_in_range_odd_bytes_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = small_prime_count_in_range(low, high);
    if high <= 23 {
        return Ok(count);
    }

    low = low.max(23);
    if high - low <= segment_size {
        return Ok(count + prime_count_single_odd_segment_with_base(low, high, base)?);
    }

    let mut segment_low = low;
    let mut flags = Vec::<u8>::new();
    let dense_marking = use_dense_odd_byte_marking(high);
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let mut cursors = initial_sieve_cursors(base, first_odd_low, high)?;

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            refill_presieved_odd_flags(&mut flags, odd_low, odd_count);

            mark_active_sieve_cursors(
                &mut flags,
                &mut cursors,
                odd_low,
                segment_high,
                dense_marking,
            );

            count += count_flag_bytes(&flags);
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn for_each_presieved_odd_prime_with_base<F>(
    low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
    mut on_prime: F,
) -> Result<(), RangeError>
where
    F: FnMut(u64),
{
    let mut segment_low = low;
    let mut flags = Vec::<u8>::new();
    let dense_marking = use_dense_odd_byte_marking(high);
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let mut cursors = initial_sieve_cursors(base, first_odd_low, high)?;

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            refill_presieved_odd_flags(&mut flags, odd_low, odd_count);

            mark_active_sieve_cursors(
                &mut flags,
                &mut cursors,
                odd_low,
                segment_high,
                dense_marking,
            );

            for (index, &is_prime) in flags.iter().enumerate() {
                if is_prime != 0 {
                    on_prime(odd_low + 2 * index as u64);
                }
            }
        }

        segment_low = segment_high;
    }

    Ok(())
}

fn prime_count_single_odd_segment_with_base(
    low: u64,
    high: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    let odd_low = if low % 2 == 0 { low + 1 } else { low };
    if odd_low >= high {
        return Ok(0);
    }

    let odd_count_u64 = ((high - odd_low) + 1) / 2;
    let odd_count = usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
    let mut flags = Vec::<u8>::with_capacity(odd_count);
    refill_presieved_odd_flags(&mut flags, odd_low, odd_count);
    let dense_marking = use_dense_odd_byte_marking(high);

    mark_single_segment_base_multiples(&mut flags, odd_low, high, base, dense_marking)?;

    Ok(count_flag_bytes(&flags))
}

fn prime_count_in_range_odd_bytes_presieve13_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = small_prime_count_in_range_through(low, high, 13);
    if high <= 17 {
        return Ok(count);
    }

    low = low.max(17);
    if high - low <= segment_size {
        let odd_low = if low % 2 == 0 { low + 1 } else { low };
        if odd_low >= high {
            return Ok(count);
        }

        let odd_count_u64 = ((high - odd_low) + 1) / 2;
        let odd_count = usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
        let mut flags = Vec::<u8>::with_capacity(odd_count);
        refill_presieved13_odd_flags(&mut flags, odd_low, odd_count);
        let dense_marking = use_dense_odd_byte_marking(high);
        mark_single_segment_base_multiples_after(
            &mut flags,
            odd_low,
            high,
            base,
            dense_marking,
            13,
        )?;
        return Ok(count + count_flag_bytes(&flags));
    }

    let mut segment_low = low;
    let mut flags = Vec::<u8>::new();
    let dense_marking = use_dense_odd_byte_marking(high);
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let mut cursors = initial_sieve_cursors_after(base, first_odd_low, high, 13)?;

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            refill_presieved13_odd_flags(&mut flags, odd_low, odd_count);

            mark_active_sieve_cursors(
                &mut flags,
                &mut cursors,
                odd_low,
                segment_high,
                dense_marking,
            );

            count += count_flag_bytes(&flags);
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn prime_count_in_range_odd_bytes_presieve17_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = small_prime_count_in_range_through(low, high, 17);
    if high <= 19 {
        return Ok(count);
    }

    low = low.max(19);
    if high - low <= segment_size {
        let odd_low = if low % 2 == 0 { low + 1 } else { low };
        if odd_low >= high {
            return Ok(count);
        }

        let odd_count_u64 = ((high - odd_low) + 1) / 2;
        let odd_count = usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
        let mut flags = Vec::<u8>::with_capacity(odd_count);
        refill_presieved17_odd_flags(&mut flags, odd_low, odd_count);
        let dense_marking = use_dense_odd_byte_marking(high);
        mark_single_segment_base_multiples_after(
            &mut flags,
            odd_low,
            high,
            base,
            dense_marking,
            17,
        )?;
        return Ok(count + count_flag_bytes(&flags));
    }

    let mut segment_low = low;
    let mut flags = Vec::<u8>::new();
    let dense_marking = use_dense_odd_byte_marking(high);
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let mut cursors = initial_sieve_cursors_after(base, first_odd_low, high, 17)?;

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            refill_presieved17_odd_flags(&mut flags, odd_low, odd_count);

            mark_active_sieve_cursors(
                &mut flags,
                &mut cursors,
                odd_low,
                segment_high,
                dense_marking,
            );

            count += count_flag_bytes(&flags);
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn prime_count_in_range_bitpacked_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = small_prime_count_in_range(low, high);
    if high <= 23 {
        return Ok(count);
    }

    low = low.max(23);
    let mut segment_low = low;
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let mut cursors = initial_sieve_cursors(base, first_odd_low, high)?;
    let mut words = Vec::<u64>::new();

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            fill_presieved_odd_words(&mut words, odd_low, odd_count);

            let active_count = active_sieve_cursor_count(&cursors, segment_high);
            for cursor in &mut cursors[..active_count] {
                if cursor.next >= segment_high {
                    continue;
                }

                let mut index = ((cursor.next - odd_low) / 2) as usize;
                while index < odd_count {
                    clear_candidate_bit(&mut words, index);
                    index += cursor.q;
                }
                cursor.next = odd_low.saturating_add(2 * index as u64);
            }

            count += count_flag_bits(&words);
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn prime_count_in_range_tracked_bytes_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = small_prime_count_in_range(low, high);
    if high <= 23 {
        return Ok(count);
    }

    low = low.max(23);
    let mut segment_low = low;
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let mut cursors = initial_sieve_cursors(base, first_odd_low, high)?;
    let mut flags = Vec::<u8>::new();

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            refill_presieved_odd_flags(&mut flags, odd_low, odd_count);
            let mut segment_count = count_presieved_odd_window(odd_low, odd_count);

            let active_count = active_sieve_cursor_count(&cursors, segment_high);
            for cursor in &mut cursors[..active_count] {
                if cursor.next >= segment_high {
                    continue;
                }

                let mut index = ((cursor.next - odd_low) / 2) as usize;
                while index < odd_count {
                    if flags[index] != 0 {
                        flags[index] = 0;
                        segment_count -= 1;
                    }
                    index += cursor.q;
                }
                cursor.next = odd_low.saturating_add(2 * index as u64);
            }

            count += segment_count;
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn prime_count_in_range_wheel30_marks_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = small_prime_count_in_range(low, high);
    if high <= 23 {
        return Ok(count);
    }

    low = low.max(23);
    let mut segment_low = low;
    let mut flags = Vec::<u8>::new();
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let mut cursors = initial_wheel30_mark_cursors(base, first_odd_low, high)?;

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            refill_presieved_odd_flags(&mut flags, odd_low, odd_count);

            mark_active_wheel30_cursors(&mut flags, &mut cursors, odd_low, segment_high);

            count += count_flag_bytes(&flags);
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn prime_count_in_range_hybrid_wheel30_marks_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = small_prime_count_in_range(low, high);
    if high <= 23 {
        return Ok(count);
    }

    low = low.max(23);
    let mut segment_low = low;
    let mut flags = Vec::<u8>::new();
    let dense_marking = use_dense_odd_byte_marking(high);
    let first_odd_low = if segment_low % 2 == 0 {
        segment_low + 1
    } else {
        segment_low
    };
    let dense_step_limit = hybrid_dense_step_limit(segment_size)?;
    let (mut dense_cursors, mut wheel_cursors) =
        initial_hybrid_wheel30_mark_cursors(base, first_odd_low, high, dense_step_limit)?;

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let odd_low = if segment_low % 2 == 0 {
            segment_low + 1
        } else {
            segment_low
        };

        if odd_low < segment_high {
            let odd_count_u64 = ((segment_high - odd_low) + 1) / 2;
            let odd_count =
                usize::try_from(odd_count_u64).map_err(|_| RangeError::SegmentTooLarge)?;
            refill_presieved_odd_flags(&mut flags, odd_low, odd_count);

            mark_active_sieve_cursors(
                &mut flags,
                &mut dense_cursors,
                odd_low,
                segment_high,
                dense_marking,
            );
            mark_active_wheel30_cursors(&mut flags, &mut wheel_cursors, odd_low, segment_high);

            count += count_flag_bytes(&flags);
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn prime_count_in_range_wheel30_with_base(
    mut low: u64,
    high: u64,
    segment_size: u64,
    base: &[u64],
) -> Result<usize, RangeError> {
    if segment_size == 0 {
        return Err(RangeError::SegmentSizeZero);
    }
    if high <= low {
        return Ok(0);
    }

    let mut count = [2, 3, 5]
        .into_iter()
        .filter(|&prime| low <= prime && prime < high)
        .count();
    if high <= 7 {
        return Ok(count);
    }

    low = low.max(7);
    let first_candidate = first_wheel30_candidate_at_or_after(low);
    let mut cursors = if first_candidate < high {
        initial_wheel30_cursors(base, first_candidate, high)?
    } else {
        Vec::new()
    };
    let mut segment_low = low;
    let mut flags = Vec::<u8>::new();

    while segment_low < high {
        let segment_high = segment_low.saturating_add(segment_size).min(high);
        let candidate_low = first_wheel30_candidate_at_or_after(segment_low);

        if candidate_low < segment_high {
            let start_rank = wheel30_candidate_count_below(candidate_low);
            let end_rank = wheel30_candidate_count_below(segment_high);
            let candidate_count =
                usize::try_from(end_rank - start_rank).map_err(|_| RangeError::SegmentTooLarge)?;
            flags.resize(candidate_count, 1);
            flags.fill(1);

            for cursor in &mut cursors {
                if cursor.next >= segment_high {
                    continue;
                }

                while cursor.next < segment_high {
                    let index = usize::try_from(cursor.next_index - start_rank)
                        .map_err(|_| RangeError::SegmentTooLarge)?;
                    flags[index] = 0;

                    advance_wheel30_cursor(cursor);
                }
            }

            count += count_flag_bytes(&flags);
        }

        segment_low = segment_high;
    }

    Ok(count)
}

fn initial_sieve_cursors(
    base: &[u64],
    odd_low: u64,
    high: u64,
) -> Result<Vec<SieveCursor>, RangeError> {
    initial_sieve_cursors_after(base, odd_low, high, 19)
}

fn initial_sieve_cursors_after(
    base: &[u64],
    odd_low: u64,
    high: u64,
    presieved_through: u64,
) -> Result<Vec<SieveCursor>, RangeError> {
    let limit = (high - 1).isqrt();
    let mut cursors = Vec::with_capacity(base.len());
    for &q in base {
        if q <= presieved_through {
            continue;
        }
        if q > limit {
            break;
        }
        let q_usize = usize::try_from(q).map_err(|_| RangeError::SegmentTooLarge)?;
        cursors.push(SieveCursor {
            q: q_usize,
            square: q * q,
            next: first_odd_multiple_at_or_after(q, odd_low),
        });
    }
    Ok(cursors)
}

fn active_sieve_cursor_count(cursors: &[SieveCursor], segment_high: u64) -> usize {
    cursors.partition_point(|cursor| cursor.square < segment_high)
}

fn mark_active_sieve_cursors(
    flags: &mut [u8],
    cursors: &mut [SieveCursor],
    odd_low: u64,
    segment_high: u64,
    dense_marking: bool,
) {
    let active_count = active_sieve_cursor_count(cursors, segment_high);
    let active = &mut cursors[..active_count];
    if dense_marking {
        for cursor in active {
            if cursor.next >= segment_high {
                continue;
            }
            let index = mark_dense_odd_byte_multiples(
                flags,
                ((cursor.next - odd_low) / 2) as usize,
                cursor.q,
            );
            cursor.next = odd_low.saturating_add(2 * index as u64);
        }
    } else {
        for cursor in active {
            if cursor.next >= segment_high {
                continue;
            }
            let index =
                mark_odd_byte_multiples(flags, ((cursor.next - odd_low) / 2) as usize, cursor.q);
            cursor.next = odd_low.saturating_add(2 * index as u64);
        }
    }
}

fn mark_single_segment_base_multiples(
    flags: &mut [u8],
    odd_low: u64,
    high: u64,
    base: &[u64],
    dense_marking: bool,
) -> Result<(), RangeError> {
    mark_single_segment_base_multiples_after(flags, odd_low, high, base, dense_marking, 19)
}

fn mark_single_segment_base_multiples_after(
    flags: &mut [u8],
    odd_low: u64,
    high: u64,
    base: &[u64],
    dense_marking: bool,
    presieved_through: u64,
) -> Result<(), RangeError> {
    let limit = (high - 1).isqrt();
    let active_base = active_sieving_base_primes(base, limit, presieved_through);
    if dense_marking {
        for &q in active_base {
            let index = first_odd_multiple_index_at_or_after(q, odd_low)?;
            let step = usize::try_from(q).map_err(|_| RangeError::SegmentTooLarge)?;
            mark_dense_odd_byte_multiples(flags, index, step);
        }
    } else {
        let dense_step_limit = flags.len() / HYBRID_DENSE_STEP_DIVISOR;
        let (dense_base, sparse_base) =
            split_base_primes_by_dense_step(active_base, dense_step_limit);
        for &q in dense_base {
            let index = first_odd_multiple_index_at_or_after(q, odd_low)?;
            let step = usize::try_from(q).map_err(|_| RangeError::SegmentTooLarge)?;
            mark_dense_odd_byte_multiples(flags, index, step);
        }

        let len = flags.len();
        let ptr = flags.as_mut_ptr();
        for &q in sparse_base {
            let index = first_odd_multiple_index_at_or_after(q, odd_low)?;
            let step = usize::try_from(q).map_err(|_| RangeError::SegmentTooLarge)?;
            mark_odd_byte_multiples_checked_unroll(ptr, len, index, step);
        }
    }
    Ok(())
}

fn initial_wheel30_mark_cursors(
    base: &[u64],
    odd_low: u64,
    high: u64,
) -> Result<Vec<Wheel30MarkCursor>, RangeError> {
    let limit = (high - 1).isqrt();
    let mut cursors = Vec::with_capacity(base.len());
    for &q in base {
        if q <= 19 {
            continue;
        }
        if q > limit {
            break;
        }
        let q_usize = usize::try_from(q).map_err(|_| RangeError::SegmentTooLarge)?;
        if let Some((next, multiplier_residue)) =
            first_wheel30_multiplier_multiple_at_or_after(q, odd_low, high)
        {
            cursors.push(Wheel30MarkCursor {
                q: q_usize,
                square: q * q,
                next,
                gap_index: wheel30_gap_index_after_residue(multiplier_residue),
            });
        }
    }
    Ok(cursors)
}

fn initial_hybrid_wheel30_mark_cursors(
    base: &[u64],
    odd_low: u64,
    high: u64,
    dense_step_limit: usize,
) -> Result<(Vec<SieveCursor>, Vec<Wheel30MarkCursor>), RangeError> {
    let limit = (high - 1).isqrt();
    let mut dense_cursors = Vec::with_capacity(base.len());
    let mut wheel_cursors = Vec::with_capacity(base.len());
    for &q in base {
        if q <= 19 {
            continue;
        }
        if q > limit {
            break;
        }
        let q_usize = usize::try_from(q).map_err(|_| RangeError::SegmentTooLarge)?;
        if q_usize <= dense_step_limit {
            dense_cursors.push(SieveCursor {
                q: q_usize,
                square: q * q,
                next: first_odd_multiple_at_or_after(q, odd_low),
            });
        } else if let Some((next, multiplier_residue)) =
            first_wheel30_multiplier_multiple_at_or_after(q, odd_low, high)
        {
            wheel_cursors.push(Wheel30MarkCursor {
                q: q_usize,
                square: q * q,
                next,
                gap_index: wheel30_gap_index_after_residue(multiplier_residue),
            });
        }
    }
    Ok((dense_cursors, wheel_cursors))
}

fn active_wheel30_mark_cursor_count(cursors: &[Wheel30MarkCursor], segment_high: u64) -> usize {
    cursors.partition_point(|cursor| cursor.square < segment_high)
}

fn mark_active_wheel30_cursors(
    flags: &mut [u8],
    cursors: &mut [Wheel30MarkCursor],
    odd_low: u64,
    segment_high: u64,
) {
    let active_count = active_wheel30_mark_cursor_count(cursors, segment_high);
    for cursor in &mut cursors[..active_count] {
        if cursor.next >= segment_high {
            continue;
        }

        let (index, gap_index) = mark_wheel30_odd_byte_multiples(
            flags,
            ((cursor.next - odd_low) / 2) as usize,
            cursor.q,
            cursor.gap_index,
        );
        cursor.next = odd_low.saturating_add(2 * index as u64);
        cursor.gap_index = gap_index;
    }
}

fn initial_wheel30_cursors(
    base: &[u64],
    candidate_low: u64,
    high: u64,
) -> Result<Vec<Wheel30Cursor>, RangeError> {
    let limit = (high - 1).isqrt();
    let mut cursors = Vec::with_capacity(base.len());
    for &q in base {
        if q <= 5 {
            continue;
        }
        if q > limit {
            break;
        }
        if let Some((next, multiplier_residue)) =
            first_wheel30_multiple_at_or_after(q, candidate_low, high)
        {
            let next_index = wheel30_candidate_count_below(next);
            cursors.push(Wheel30Cursor {
                q,
                next,
                next_index,
                multiplier_residue,
            });
        }
    }
    Ok(cursors)
}

fn split_range(low: u64, high: u64, parts: usize) -> Vec<(u64, u64)> {
    if high <= low {
        return Vec::new();
    }

    let span = high - low;
    let parts_u64 = u64::try_from(parts).unwrap_or(u64::MAX).min(span).max(1);
    let base_width = span / parts_u64;
    let remainder = span % parts_u64;
    let mut chunks = Vec::with_capacity(parts_u64 as usize);
    let mut chunk_low = low;
    for index in 0..parts_u64 {
        let width = base_width + u64::from(index < remainder);
        let chunk_high = chunk_low + width;
        chunks.push((chunk_low, chunk_high));
        chunk_low = chunk_high;
    }
    chunks
}

fn split_range_by_sieve_work(low: u64, high: u64, parts: usize) -> Vec<(u64, u64)> {
    if high <= low {
        return Vec::new();
    }
    let span = high - low;
    let parts_u64 = u64::try_from(parts).unwrap_or(u64::MAX).min(span).max(1);
    if parts_u64 == 1 {
        return vec![(low, high)];
    }

    let low_work = sieve_work_estimate(low);
    let high_work = sieve_work_estimate(high);
    let total_work = high_work - low_work;
    if !total_work.is_finite() || total_work <= 0.0 {
        return split_range(low, high, parts);
    }

    let mut chunks = Vec::with_capacity(parts_u64 as usize);
    let mut chunk_low = low;
    for index in 1..parts_u64 {
        let target_work = low_work + total_work * (index as f64 / parts_u64 as f64);
        let estimated = inverse_sieve_work_estimate(target_work);
        let remaining_chunks = parts_u64 - index;
        let min_high = chunk_low.saturating_add(1);
        let max_high = high.saturating_sub(remaining_chunks);
        let chunk_high = estimated.clamp(min_high, max_high);
        chunks.push((chunk_low, chunk_high));
        chunk_low = chunk_high;
    }
    chunks.push((chunk_low, high));
    chunks
}

fn sieve_work_estimate(n: u64) -> f64 {
    (n as f64).powf(1.5)
}

fn inverse_sieve_work_estimate(work: f64) -> u64 {
    if !work.is_finite() || work <= 0.0 {
        return 0;
    }
    work.powf(2.0 / 3.0).round() as u64
}

fn first_odd_multiple_at_or_after(q: u64, low: u64) -> u64 {
    debug_assert_eq!(q % 2, 1);
    let q_squared = q * q;
    if q_squared >= low {
        return q_squared;
    }

    let remainder = low % q;
    let delta = if remainder == 0 { 0 } else { q - remainder };
    let odd_delta = if (low ^ delta) & 1 == 1 {
        delta
    } else {
        delta + q
    };
    low.saturating_add(odd_delta)
}

fn first_odd_multiple_index_at_or_after(q: u64, odd_low: u64) -> Result<usize, RangeError> {
    debug_assert_eq!(q % 2, 1);
    debug_assert_eq!(odd_low % 2, 1);
    let q_squared = q * q;
    let delta = if q_squared >= odd_low {
        q_squared - odd_low
    } else {
        let remainder = odd_low % q;
        if remainder == 0 {
            0
        } else {
            let delta = q - remainder;
            if delta & 1 == 0 {
                delta
            } else {
                delta + q
            }
        }
    };
    usize::try_from(delta / 2).map_err(|_| RangeError::SegmentTooLarge)
}

fn ceil_multiple_saturating(n: u64, divisor: u64) -> u64 {
    let remainder = n % divisor;
    if remainder == 0 {
        n
    } else {
        n.saturating_add(divisor - remainder)
    }
}

fn first_wheel30_multiple_at_or_after(q: u64, low: u64, high: u64) -> Option<(u64, u8)> {
    let q_squared = q * q;
    let mut start = q_squared.max(ceil_multiple_saturating(low, q));
    while start < high {
        if is_wheel30_candidate(start) {
            let multiplier_residue = ((start / q) % 30) as u8;
            debug_assert!(is_wheel30_candidate(u64::from(multiplier_residue)));
            return Some((start, multiplier_residue));
        }
        start = start.checked_add(q)?;
    }
    None
}

fn first_wheel30_multiplier_multiple_at_or_after(q: u64, low: u64, high: u64) -> Option<(u64, u8)> {
    let mut start = first_odd_multiple_at_or_after(q, low);
    let step = q.checked_mul(2)?;
    let mut multiplier = start / q;
    while start < high {
        if is_wheel30_candidate(multiplier) {
            return Some((start, (multiplier % 30) as u8));
        }
        start = start.checked_add(step)?;
        multiplier += 2;
    }
    None
}

fn first_wheel30_candidate_at_or_after(mut n: u64) -> u64 {
    while !is_wheel30_candidate(n) {
        let Some(next) = n.checked_add(1) else {
            return u64::MAX;
        };
        n = next;
    }
    n
}

fn is_wheel30_candidate(n: u64) -> bool {
    WHEEL30_INDEX_BY_RESIDUE[(n % 30) as usize] >= 0
}

fn wheel30_candidate_count_below(n: u64) -> u64 {
    let block_count = n / 30;
    let residue_count = u64::from(WHEEL30_COUNT_BELOW_RESIDUE[(n % 30) as usize]);
    block_count * 8 + residue_count
}

fn advance_wheel30_cursor(cursor: &mut Wheel30Cursor) {
    let gap = u64::from(wheel30_gap_after_residue(cursor.multiplier_residue));
    let step = cursor.q * gap;
    cursor.next_index += wheel30_candidate_index_delta(cursor.next, step);
    cursor.next = cursor.next.saturating_add(step);
    cursor.multiplier_residue = ((u64::from(cursor.multiplier_residue) + gap) % 30) as u8;
}

fn wheel30_candidate_index_delta(n: u64, step: u64) -> u64 {
    let start_residue = n % 30;
    let end = start_residue + step;
    let block_delta = end / 30;
    let end_residue = (end % 30) as usize;
    block_delta * 8 + u64::from(WHEEL30_COUNT_BELOW_RESIDUE[end_residue])
        - u64::from(WHEEL30_COUNT_BELOW_RESIDUE[start_residue as usize])
}

fn wheel30_gap_after_residue(residue: u8) -> u8 {
    let gap = WHEEL30_GAP_BY_RESIDUE[usize::from(residue)];
    debug_assert!(gap > 0);
    gap
}

fn wheel30_gap_index_after_residue(residue: u8) -> u8 {
    let index = WHEEL30_INDEX_BY_RESIDUE[usize::from(residue)];
    debug_assert!(index >= 0);
    index as u8
}

fn hybrid_dense_step_limit(segment_size: u64) -> Result<usize, RangeError> {
    let odd_capacity =
        usize::try_from(segment_size.div_ceil(2)).map_err(|_| RangeError::SegmentTooLarge)?;
    Ok(odd_capacity / HYBRID_DENSE_STEP_DIVISOR)
}

#[cfg(test)]
fn fill_presieved_odd_flags(flags: &mut [u8], odd_low: u64) {
    let pattern = presieve_3_5_7_11_13_17_19_pattern();
    let mut phase = ((odd_low % PRESIEVE19_MODULUS) / 2) as usize;
    let mut offset = 0usize;
    while offset < flags.len() {
        let take = (flags.len() - offset).min(PRESIEVE19_ODD_PERIOD - phase);
        flags[offset..offset + take].copy_from_slice(&pattern[phase..phase + take]);
        offset += take;
        phase = 0;
    }
}

fn refill_presieved_odd_flags(flags: &mut Vec<u8>, odd_low: u64, odd_count: usize) {
    refill_presieved_odd_flags_from(
        flags,
        odd_low,
        odd_count,
        presieve_3_5_7_11_13_17_19_pattern(),
        PRESIEVE19_MODULUS,
        PRESIEVE19_ODD_PERIOD,
    );
}

fn refill_presieved13_odd_flags(flags: &mut Vec<u8>, odd_low: u64, odd_count: usize) {
    refill_presieved_odd_flags_from(
        flags,
        odd_low,
        odd_count,
        presieve_3_5_7_11_13_pattern(),
        PRESIEVE13_MODULUS,
        PRESIEVE13_ODD_PERIOD,
    );
}

fn refill_presieved17_odd_flags(flags: &mut Vec<u8>, odd_low: u64, odd_count: usize) {
    refill_presieved_odd_flags_from(
        flags,
        odd_low,
        odd_count,
        presieve_3_5_7_11_13_17_pattern(),
        PRESIEVE17_MODULUS,
        PRESIEVE17_ODD_PERIOD,
    );
}

fn refill_presieved_odd_flags_from(
    flags: &mut Vec<u8>,
    odd_low: u64,
    odd_count: usize,
    pattern: &[u8],
    modulus: u64,
    odd_period: usize,
) {
    flags.clear();
    flags.reserve(odd_count);

    let mut phase = ((odd_low % modulus) / 2) as usize;
    let mut offset = 0usize;
    while offset < odd_count {
        let take = (odd_count - offset).min(odd_period - phase);
        // SAFETY: reserve() ensures capacity for odd_count bytes. Each copied
        // range is within that capacity, non-overlapping with the static
        // pattern, and every byte up to odd_count is initialized before set_len.
        unsafe {
            ptr::copy_nonoverlapping(
                pattern.as_ptr().add(phase),
                flags.as_mut_ptr().add(offset),
                take,
            );
        }
        offset += take;
        phase = 0;
    }

    // SAFETY: the loop above initialized exactly odd_count bytes.
    unsafe {
        flags.set_len(odd_count);
    }
}

fn fill_presieved_odd_words(words: &mut Vec<u64>, odd_low: u64, odd_count: usize) {
    let word_count = odd_count.div_ceil(64);
    words.clear();
    words.reserve(word_count);

    let mut phase = ((odd_low % PRESIEVE19_MODULUS) / 2) as usize;
    for _ in 0..word_count {
        words.push(presieve_window_word(phase));
        phase += 64;
        if phase >= PRESIEVE19_ODD_PERIOD {
            phase %= PRESIEVE19_ODD_PERIOD;
        }
    }

    if let Some(last) = words.last_mut() {
        let remainder = odd_count & 63;
        if remainder != 0 {
            *last &= (1u64 << remainder) - 1;
        }
    }
}

fn presieve_3_5_7_11_13_17_19_pattern() -> &'static [u8] {
    include_bytes!(concat!(env!("OUT_DIR"), "/presieve_3_5_7_11_13_17_19.bin"))
}

fn presieve_3_5_7_11_13_pattern() -> &'static [u8] {
    include_bytes!(concat!(env!("OUT_DIR"), "/presieve_3_5_7_11_13.bin"))
}

fn presieve_3_5_7_11_13_17_pattern() -> &'static [u8] {
    include_bytes!(concat!(env!("OUT_DIR"), "/presieve_3_5_7_11_13_17.bin"))
}

fn presieve_3_5_7_11_13_17_19_words() -> &'static [u64] {
    static WORDS: OnceLock<Vec<u64>> = OnceLock::new();
    WORDS
        .get_or_init(|| {
            let pattern = presieve_3_5_7_11_13_17_19_pattern();
            let mut words = vec![0u64; pattern.len().div_ceil(64)];
            for (index, &flag) in pattern.iter().enumerate() {
                if flag != 0 {
                    words[index >> 6] |= 1u64 << (index & 63);
                }
            }
            words
        })
        .as_slice()
}

fn presieve_3_5_7_11_13_17_19_prefix_counts() -> &'static [u32] {
    static PREFIX_COUNTS: OnceLock<Vec<u32>> = OnceLock::new();
    PREFIX_COUNTS
        .get_or_init(|| {
            let pattern = presieve_3_5_7_11_13_17_19_pattern();
            let mut prefix_counts = Vec::with_capacity(pattern.len() + 1);
            prefix_counts.push(0);
            for &flag in pattern {
                let next = prefix_counts.last().copied().unwrap() + u32::from(flag != 0);
                prefix_counts.push(next);
            }
            prefix_counts
        })
        .as_slice()
}

fn count_presieved_odd_window(odd_low: u64, mut odd_count: usize) -> usize {
    let prefix_counts = presieve_3_5_7_11_13_17_19_prefix_counts();
    let mut phase = ((odd_low % PRESIEVE19_MODULUS) / 2) as usize;
    let mut count = 0usize;

    while odd_count > 0 {
        let take = odd_count.min(PRESIEVE19_ODD_PERIOD - phase);
        count += (prefix_counts[phase + take] - prefix_counts[phase]) as usize;
        odd_count -= take;
        phase = 0;
    }

    count
}

fn presieve_window_word(phase: usize) -> u64 {
    debug_assert!(phase < PRESIEVE19_ODD_PERIOD);
    let remaining = PRESIEVE19_ODD_PERIOD - phase;
    if remaining >= 64 {
        read_presieve_bits_nonwrapping(phase, 64)
    } else {
        let lower = read_presieve_bits_nonwrapping(phase, remaining);
        let upper = read_presieve_bits_nonwrapping(0, 64 - remaining);
        lower | (upper << remaining)
    }
}

fn read_presieve_bits_nonwrapping(phase: usize, len: usize) -> u64 {
    debug_assert!(len <= 64);
    debug_assert!(phase + len <= PRESIEVE19_ODD_PERIOD);
    if len == 0 {
        return 0;
    }

    let source = presieve_3_5_7_11_13_17_19_words();
    let word_index = phase >> 6;
    let bit_offset = phase & 63;
    let mut value = source[word_index] >> bit_offset;
    if bit_offset != 0 && word_index + 1 < source.len() {
        value |= source[word_index + 1] << (64 - bit_offset);
    }

    if len == 64 {
        value
    } else {
        value & ((1u64 << len) - 1)
    }
}

fn clear_candidate_bit(words: &mut [u64], index: usize) {
    words[index >> 6] &= !(1u64 << (index & 63));
}

#[inline(always)]
fn mark_odd_byte_multiples(flags: &mut [u8], mut index: usize, step: usize) -> usize {
    debug_assert!(step > 0);
    while index < flags.len() {
        flags[index] = 0;
        index += step;
    }
    index
}

#[inline(always)]
fn mark_dense_odd_byte_multiples(flags: &mut [u8], mut index: usize, step: usize) -> usize {
    debug_assert!(step > 0);
    let len = flags.len();
    let ptr = flags.as_mut_ptr();

    if step > len / 4 {
        return mark_odd_byte_multiples_checked_unroll(ptr, len, index, step);
    }

    let triple_step = step * 3;
    let batch_step = step * 4;
    let batch_limit = len - 1 - triple_step;
    while index <= batch_limit {
        // SAFETY: index <= len - 1 - 3 * step, so every batched write is
        // inside this exclusive mutable slice. step is positive.
        unsafe {
            ptr.add(index).write(0);
            ptr.add(index + step).write(0);
            ptr.add(index + 2 * step).write(0);
            ptr.add(index + triple_step).write(0);
        }
        index += batch_step;
    }

    while index < len {
        // SAFETY: every tail write is preceded by index < len.
        unsafe {
            ptr.add(index).write(0);
        }
        index += step;
    }
    index
}

#[inline(always)]
fn mark_wheel30_odd_byte_multiples(
    flags: &mut [u8],
    mut index: usize,
    step: usize,
    mut gap_index: u8,
) -> (usize, u8) {
    debug_assert!(step > 0);
    debug_assert!(gap_index < 8);
    let len = flags.len();
    let ptr = flags.as_mut_ptr();
    if step > usize::MAX / 3 {
        while index < len {
            // SAFETY: every write is preceded by index < len, and the caller has
            // exclusive access to this segment buffer.
            unsafe {
                ptr.add(index).write(0);
            }
            let half_gap = WHEEL30_HALF_GAP_BY_INDEX[usize::from(gap_index)];
            index = index.saturating_add(step.saturating_mul(half_gap));
            gap_index = (gap_index + 1) & 7;
        }
        return (index, gap_index);
    }

    let step1 = step;
    let step2 = step * 2;
    let step3 = step * 3;

    while index < len && gap_index != 0 {
        // SAFETY: every write is preceded by index < len, and the caller has
        // exclusive access to this segment buffer.
        unsafe {
            ptr.add(index).write(0);
        }
        let half_gap = WHEEL30_HALF_GAP_BY_INDEX[usize::from(gap_index)];
        index += step * half_gap;
        gap_index = (gap_index + 1) & 7;
    }
    if index >= len {
        return (index, gap_index);
    }

    while index < len {
        // SAFETY: each write is guarded by the preceding index < len check.
        unsafe {
            ptr.add(index).write(0);
        }
        index += step3;
        if index >= len {
            return (index, 1);
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step2;
        if index >= len {
            return (index, 2);
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step1;
        if index >= len {
            return (index, 3);
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step2;
        if index >= len {
            return (index, 4);
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step1;
        if index >= len {
            return (index, 5);
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step2;
        if index >= len {
            return (index, 6);
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step3;
        if index >= len {
            return (index, 7);
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step1;
    }

    (index, 0)
}

fn use_dense_odd_byte_marking(high: u64) -> bool {
    high.checked_sub(1)
        .map(|last| last.isqrt() < DENSE_MARKING_BASE_LIMIT)
        .unwrap_or(false)
}

#[inline(always)]
fn mark_odd_byte_multiples_checked_unroll(
    ptr: *mut u8,
    len: usize,
    mut index: usize,
    step: usize,
) -> usize {
    while index < len {
        // SAFETY: every write is preceded by index < len, step is positive,
        // and all writes stay within the caller's exclusive mutable slice.
        unsafe {
            ptr.add(index).write(0);
        }
        index += step;
        if index >= len {
            break;
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step;
        if index >= len {
            break;
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step;
        if index >= len {
            break;
        }
        unsafe {
            ptr.add(index).write(0);
        }
        index += step;
    }
    index
}

fn small_prime_count_in_range(low: u64, high: u64) -> usize {
    small_prime_count_in_range_through(low, high, 19)
}

fn small_prime_count_in_range_through(low: u64, high: u64, max_prime: u64) -> usize {
    [2, 3, 5, 7, 11, 13, 17, 19]
        .into_iter()
        .take_while(|&prime| prime <= max_prime)
        .filter(|&prime| low <= prime && prime < high)
        .count()
}

fn count_flag_bytes(flags: &[u8]) -> usize {
    // The sieve stores only 0/1 bytes. All u64 bit patterns are valid, and
    // align_to returns unaligned prefix/suffix bytes separately.
    let (prefix, words, suffix) = unsafe { flags.align_to::<u64>() };
    prefix.iter().map(|&flag| usize::from(flag)).sum::<usize>()
        + words
            .iter()
            .map(|word| word.count_ones() as usize)
            .sum::<usize>()
        + suffix.iter().map(|&flag| usize::from(flag)).sum::<usize>()
}

fn count_flag_bits(words: &[u64]) -> usize {
    words
        .iter()
        .map(|word| word.count_ones() as usize)
        .sum::<usize>()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn base_prime_generation_matches_known_prefix() {
        assert_eq!(
            base_primes(30).unwrap(),
            vec![2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        );
    }

    #[test]
    fn odd_byte_base_prime_generation_matches_bitset_fallback() {
        for limit in [0, 1, 2, 3, 4, 5, 30, 97, 1_000, 10_000, 100_000, 1_000_000] {
            assert_eq!(
                base_primes_odd_bytes(limit).unwrap(),
                base_primes_bitset(limit).unwrap(),
                "limit={limit}"
            );
        }
    }

    #[test]
    fn static_base_prime_table_matches_odd_byte_generation() {
        for limit in [
            0,
            1,
            2,
            3,
            30,
            10_000,
            1_000_000,
            STATIC_BASE_PRIME_LIMIT - 1,
            STATIC_BASE_PRIME_LIMIT,
        ] {
            assert_eq!(
                base_primes_static(limit),
                base_primes_odd_bytes(limit).unwrap(),
                "limit={limit}"
            );
        }
    }

    #[test]
    fn cached_static_base_prime_slice_matches_owned_generation() {
        for limit in [
            0,
            1,
            2,
            3,
            30,
            10_000,
            1_000_000,
            STATIC_BASE_PRIME_LIMIT - 1,
            STATIC_BASE_PRIME_LIMIT,
        ] {
            assert_eq!(base_primes_static_slice(limit), base_primes_static(limit));
        }
    }

    #[test]
    fn active_sieving_base_prime_slice_tracks_presieve_and_limit_bounds() {
        let base = base_primes(100).unwrap();

        assert_eq!(active_sieving_base_primes(&base, 29, 13), &[17, 19, 23, 29]);
        assert_eq!(active_sieving_base_primes(&base, 29, 29), &[]);
        assert_eq!(active_sieving_base_primes(&base, 101, 97), &[]);
        assert_eq!(active_sieving_base_primes(&base, 1, 0), &[]);
    }

    #[test]
    fn base_prime_dense_step_split_tracks_sorted_boundary() {
        let active_base = [17, 19, 23, 29, 31];

        assert_eq!(
            split_base_primes_by_dense_step(&active_base, 16),
            (&[][..], &[17, 19, 23, 29, 31][..])
        );
        assert_eq!(
            split_base_primes_by_dense_step(&active_base, 23),
            (&[17, 19, 23][..], &[29, 31][..])
        );
        assert_eq!(
            split_base_primes_by_dense_step(&active_base, 31),
            (&[17, 19, 23, 29, 31][..], &[][..])
        );
    }

    #[test]
    fn base_prime_generation_matches_known_count() {
        assert_eq!(base_primes(1_000_000).unwrap().len(), 78_498);
    }

    #[test]
    fn base_prime_generation_refuses_unbounded_tables() {
        assert_eq!(
            base_primes(BASE_PRIME_BITSET_LIMIT + 1),
            Err(RangeError::BaseLimitTooLarge)
        );
    }

    #[test]
    fn ceil_multiple_saturating_handles_boundaries() {
        assert_eq!(ceil_multiple_saturating(0, 7), 0);
        assert_eq!(ceil_multiple_saturating(21, 7), 21);
        assert_eq!(ceil_multiple_saturating(22, 7), 28);
        assert_eq!(ceil_multiple_saturating(u64::MAX - 1, 3), u64::MAX);
    }

    #[test]
    fn first_odd_multiple_skips_division_when_square_is_in_range() {
        assert_eq!(first_odd_multiple_at_or_after(23, 23), 529);
        assert_eq!(first_odd_multiple_at_or_after(23, 529), 529);
        assert_eq!(first_odd_multiple_at_or_after(23, 530), 575);
        assert_eq!(first_odd_multiple_at_or_after(29, 900), 957);
    }

    #[test]
    fn first_odd_multiple_index_matches_materialized_multiple() {
        for q in [23, 29, 31, 97, 997, 65_537] {
            for odd_low in [23, 529, 575, 10_001, 1_000_000_000_001] {
                let start = first_odd_multiple_at_or_after(q, odd_low);
                let index = first_odd_multiple_index_at_or_after(q, odd_low).unwrap();
                assert_eq!(
                    odd_low + 2 * index as u64,
                    start,
                    "q={q}, odd_low={odd_low}"
                );
            }
        }
    }

    #[test]
    fn active_sieve_cursor_count_tracks_square_boundary() {
        let base = base_primes(100).unwrap();
        let cursors = initial_sieve_cursors(&base, 23, 10_000).unwrap();

        assert_eq!(active_sieve_cursor_count(&cursors, 529), 0);
        assert_eq!(active_sieve_cursor_count(&cursors, 530), 1);
        assert_eq!(active_sieve_cursor_count(&cursors, 841), 1);
        assert_eq!(active_sieve_cursor_count(&cursors, 842), 2);
        assert_eq!(active_sieve_cursor_count(&cursors, 10_000), cursors.len());
    }

    #[test]
    fn segmented_sieve_matches_known_prime_counts() {
        for (high, expected_count) in [
            (10, 4),
            (100, 25),
            (1_000, 168),
            (10_000, 1_229),
            (100_000, 9_592),
            (1_000_000, 78_498),
        ] {
            let primes = primes_in_range(0, high, 1 << 15).unwrap();
            assert_eq!(primes.len(), expected_count, "high={high}");
        }
    }

    #[test]
    fn direct_count_matches_materialized_primes() {
        for (low, high) in [
            (0, 10),
            (0, 1_000),
            (1_000, 10_000),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_000_010_000),
        ] {
            for segment_size in [64, 1 << 12, 1 << 16] {
                let primes = primes_in_range(low, high, segment_size).unwrap();
                let count = prime_count_in_range(low, high, segment_size).unwrap();
                assert_eq!(
                    count,
                    primes.len(),
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn single_segment_count_matches_multi_segment_count() {
        for (low, high) in [
            (23, 1_000),
            (1_000_000, 1_003_333),
            (1_000_000_000_000, 1_000_000_250_000),
        ] {
            let single_segment = prime_count_in_range(low, high, high - low).unwrap();
            let multi_segment = prime_count_in_range(low, high, 4096).unwrap();
            assert_eq!(single_segment, multi_segment, "range=[{low},{high})");
        }
    }

    #[test]
    fn bitpacked_count_matches_byte_count() {
        for (low, high) in [
            (0, 10),
            (0, 1_000),
            (7, 2_003),
            (999, 10_001),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_000_050_000),
        ] {
            for segment_size in [64, 1 << 12, 3 << 14, 1 << 16] {
                let expected = prime_count_in_range(low, high, segment_size).unwrap();
                let actual = prime_count_in_range_bitpacked(low, high, segment_size).unwrap();
                assert_eq!(
                    actual, expected,
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn tracked_byte_count_matches_byte_count() {
        for (low, high) in [
            (0, 10),
            (0, 1_000),
            (7, 2_003),
            (999, 10_001),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_000_050_000),
        ] {
            for segment_size in [64, 1 << 12, 3 << 14, 1 << 16] {
                let expected = prime_count_in_range(low, high, segment_size).unwrap();
                let actual = prime_count_in_range_tracked_bytes(low, high, segment_size).unwrap();
                assert_eq!(
                    actual, expected,
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn presieve13_count_matches_byte_count() {
        for (low, high) in [
            (0, 10),
            (0, 1_000),
            (7, 2_003),
            (999, 10_001),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_000_050_000),
            (1_000_000_000_000, 1_000_000_250_000),
        ] {
            for segment_size in [64, 1 << 12, 3 << 14, 1 << 16] {
                let expected = prime_count_in_range(low, high, segment_size).unwrap();
                let actual = prime_count_in_range_presieve13(low, high, segment_size).unwrap();
                assert_eq!(
                    actual, expected,
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn parallel_presieve13_count_matches_byte_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (0, 10_000_000),
            (1_000_000_000_000, 1_000_001_000_000),
        ] {
            let segment_size = recommended_count_segment_size(low, high, 8);
            let expected = prime_count_in_range(low, high, segment_size).unwrap();
            let actual =
                prime_count_in_range_presieve13_parallel(low, high, segment_size, 8).unwrap();
            assert_eq!(actual, expected, "range=[{low},{high})");
        }
    }

    #[test]
    fn presieve17_count_matches_byte_count() {
        for (low, high) in [
            (0, 10),
            (0, 1_000),
            (7, 2_003),
            (999, 10_001),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_000_050_000),
            (1_000_000_000_000, 1_000_000_250_000),
        ] {
            for segment_size in [64, 1 << 12, 3 << 14, 1 << 16] {
                let expected = prime_count_in_range(low, high, segment_size).unwrap();
                let actual = prime_count_in_range_presieve17(low, high, segment_size).unwrap();
                assert_eq!(
                    actual, expected,
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn parallel_presieve17_count_matches_byte_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (0, 10_000_000),
            (1_000_000_000_000, 1_000_001_000_000),
        ] {
            let segment_size = recommended_count_segment_size(low, high, 8);
            let expected = prime_count_in_range(low, high, segment_size).unwrap();
            let actual =
                prime_count_in_range_presieve17_parallel(low, high, segment_size, 8).unwrap();
            assert_eq!(actual, expected, "range=[{low},{high})");
        }
    }

    #[test]
    fn wheel30_count_matches_byte_count() {
        for (low, high) in [
            (0, 10),
            (0, 1_000),
            (7, 2_003),
            (999, 10_001),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_000_050_000),
        ] {
            for segment_size in [64, 1 << 12, 3 << 14, 1 << 16] {
                let expected = prime_count_in_range(low, high, segment_size).unwrap();
                let actual = prime_count_in_range_wheel30(low, high, segment_size).unwrap();
                assert_eq!(
                    actual, expected,
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn wheel30_mark_count_matches_byte_count() {
        for (low, high) in [
            (0, 10),
            (0, 1_000),
            (7, 2_003),
            (999, 10_001),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_000_050_000),
            (1_000_000_000_000, 1_000_000_250_000),
        ] {
            for segment_size in [64, 1 << 12, 3 << 14, 1 << 16] {
                let expected = prime_count_in_range(low, high, segment_size).unwrap();
                let actual = prime_count_in_range_wheel30_marks(low, high, segment_size).unwrap();
                assert_eq!(
                    actual, expected,
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn parallel_wheel30_mark_count_matches_byte_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (0, 10_000_000),
            (1_000_000_000_000, 1_000_001_000_000),
        ] {
            let segment_size = recommended_count_segment_size(low, high, 8);
            let expected = prime_count_in_range(low, high, segment_size).unwrap();
            let actual =
                prime_count_in_range_wheel30_marks_parallel(low, high, segment_size, 8).unwrap();
            assert_eq!(actual, expected, "range=[{low},{high})");
        }
    }

    #[test]
    fn hybrid_wheel30_mark_count_matches_byte_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (0, 10_000_000),
            (1_000_000_000, 1_000_050_000),
            (1_000_000_000_000, 1_000_000_250_000),
        ] {
            for segment_size in [64, 1 << 12, 3 << 14, 1 << 16] {
                let expected = prime_count_in_range(low, high, segment_size).unwrap();
                let actual =
                    prime_count_in_range_hybrid_wheel30_marks(low, high, segment_size).unwrap();
                assert_eq!(
                    actual, expected,
                    "range=[{low},{high}), segment_size={segment_size}"
                );
            }
        }
    }

    #[test]
    fn parallel_hybrid_wheel30_mark_count_matches_byte_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (0, 10_000_000),
            (1_000_000_000_000, 1_000_001_000_000),
        ] {
            let segment_size = recommended_count_segment_size(low, high, 8);
            let expected = prime_count_in_range(low, high, segment_size).unwrap();
            let actual =
                prime_count_in_range_hybrid_wheel30_marks_parallel(low, high, segment_size, 8)
                    .unwrap();
            assert_eq!(actual, expected, "range=[{low},{high})");
        }
    }

    #[test]
    fn first_wheel30_multiplier_multiple_skips_presieved_multipliers() {
        for q in [23, 29, 31, 97, 1_009] {
            for low in [0, q * q, q * q + 1, 1_000_000_001] {
                let (multiple, residue) =
                    first_wheel30_multiplier_multiple_at_or_after(q, low, u64::MAX).unwrap();
                assert!(multiple >= low, "q={q}, low={low}");
                assert_eq!(multiple % q, 0, "q={q}, low={low}");
                assert_eq!((multiple / q) % 2, 1, "q={q}, low={low}");
                assert!(is_wheel30_candidate(multiple / q), "q={q}, low={low}");
                assert_eq!(u64::from(residue), (multiple / q) % 30, "q={q}, low={low}");
            }
        }
    }

    #[test]
    fn wheel30_boundary_helpers_stop_at_u64_ceiling() {
        assert_eq!(first_wheel30_candidate_at_or_after(u64::MAX - 1), u64::MAX);
        assert!(first_wheel30_multiple_at_or_after(23, u64::MAX - 1, u64::MAX).is_none());
        assert!(
            first_wheel30_multiplier_multiple_at_or_after(23, u64::MAX - 1, u64::MAX).is_none()
        );
    }

    #[test]
    fn wheel30_candidate_rank_matches_materialized_candidates() {
        let candidates = (0u64..300)
            .filter(|&candidate| is_wheel30_candidate(candidate))
            .collect::<Vec<_>>();
        for n in 0u64..300 {
            assert_eq!(
                wheel30_candidate_count_below(n),
                candidates
                    .iter()
                    .filter(|&&candidate| candidate < n)
                    .count() as u64,
                "n={n}"
            );
        }
    }

    #[test]
    fn wheel30_index_delta_matches_rank_difference() {
        for n in (0u64..300).filter(|&candidate| is_wheel30_candidate(candidate)) {
            for step in [2, 4, 6, 14, 30, 58, 210] {
                let target = n + step;
                if is_wheel30_candidate(target) {
                    assert_eq!(
                        wheel30_candidate_index_delta(n, step),
                        wheel30_candidate_count_below(target) - wheel30_candidate_count_below(n),
                        "n={n}, step={step}"
                    );
                }
            }
        }
    }

    #[test]
    fn bitpacked_presieve_fill_matches_byte_presieve_fill() {
        for odd_low in [1, 3, 23, 101, 1_000_001, 9_699_689, 19_399_379] {
            for odd_count in [1usize, 7, 63, 64, 65, 1_001] {
                let mut flags = vec![0u8; odd_count];
                fill_presieved_odd_flags(&mut flags, odd_low);
                let mut words = Vec::new();
                fill_presieved_odd_words(&mut words, odd_low, odd_count);
                for (index, flag) in flags.into_iter().enumerate() {
                    let bit = (words[index >> 6] >> (index & 63)) & 1;
                    assert_eq!(
                        bit as u8, flag,
                        "odd_low={odd_low}, odd_count={odd_count}, index={index}"
                    );
                }
            }
        }
    }

    #[test]
    fn refill_presieved_odd_flags_matches_slice_fill_across_resizes() {
        let mut reusable = Vec::new();
        for (odd_low, odd_count) in [
            (1, 1usize),
            (101, 65),
            (1_000_001, 7),
            (9_699_689, PRESIEVE19_ODD_PERIOD + 97),
            (19_399_379, 1_001),
        ] {
            let mut expected = vec![0u8; odd_count];
            fill_presieved_odd_flags(&mut expected, odd_low);
            refill_presieved_odd_flags(&mut reusable, odd_low, odd_count);
            assert_eq!(
                reusable, expected,
                "odd_low={odd_low}, odd_count={odd_count}"
            );
        }
    }

    #[test]
    fn mark_odd_byte_multiples_returns_first_out_of_range_index() {
        for len in 0..80 {
            for step in 1..20 {
                for start in 0..80 {
                    let mut flags = vec![1u8; len];
                    let actual = mark_odd_byte_multiples(&mut flags, start, step);
                    let mut dense_flags = vec![1u8; len];
                    let dense_actual = mark_dense_odd_byte_multiples(&mut dense_flags, start, step);
                    let mut expected_flags = vec![1u8; len];
                    let mut expected = start;
                    while expected < len {
                        expected_flags[expected] = 0;
                        expected += step;
                    }
                    assert_eq!(actual, expected, "len={len}, step={step}, start={start}");
                    assert_eq!(
                        dense_actual, expected,
                        "dense len={len}, step={step}, start={start}"
                    );
                    assert_eq!(
                        flags, expected_flags,
                        "len={len}, step={step}, start={start}"
                    );
                    assert_eq!(
                        dense_flags, expected_flags,
                        "dense len={len}, step={step}, start={start}"
                    );
                }
            }
        }
    }

    #[test]
    fn presieve_window_count_matches_byte_presieve_fill() {
        for odd_low in [1, 3, 23, 101, 1_000_001, 9_699_689, 19_399_379] {
            for odd_count in [1usize, 7, 63, 64, 65, 1_001, PRESIEVE19_ODD_PERIOD + 97] {
                let mut flags = vec![0u8; odd_count];
                fill_presieved_odd_flags(&mut flags, odd_low);
                assert_eq!(
                    count_presieved_odd_window(odd_low, odd_count),
                    flags.into_iter().filter(|&flag| flag != 0).count(),
                    "odd_low={odd_low}, odd_count={odd_count}"
                );
            }
        }
    }

    #[test]
    fn segmented_sieve_handles_offset_ranges() {
        let primes = primes_in_range(1_000, 1_100, 64).unwrap();
        assert_eq!(
            primes,
            vec![
                1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091,
                1093, 1097
            ]
        );
    }

    #[test]
    fn prime_enumeration_preserves_small_prime_boundaries_and_order() {
        assert_eq!(
            primes_in_range(0, 30, 7).unwrap(),
            vec![2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        );
        assert_eq!(primes_in_range(20, 30, 3).unwrap(), vec![23, 29]);
        assert_eq!(primes_in_range(23, 24, 64).unwrap(), vec![23]);
        assert_eq!(primes_in_range(24, 30, 64).unwrap(), vec![29]);
    }

    #[test]
    fn direct_count_handles_small_and_boundary_ranges() {
        for (low, high, expected) in [
            (0, 0, 0),
            (0, 2, 0),
            (0, 3, 1),
            (2, 3, 1),
            (3, 5, 1),
            (5, 7, 1),
            (6, 8, 1),
            (7, 8, 1),
            (8, 30, 6),
            (29, 31, 1),
            (30, 32, 1),
        ] {
            assert_eq!(
                prime_count_in_range(low, high, 7).unwrap(),
                expected,
                "range=[{low},{high})"
            );
        }
    }

    #[test]
    fn scalar_fallback_preserves_prime_boundaries() {
        for (low, high) in [
            (0, 2),
            (0, 41),
            (2, 42),
            (37, 42),
            (38, 100),
            (u64::MAX - 1_000, u64::MAX),
        ] {
            let expected = (low..high)
                .filter(|&candidate| is_prime_u64(candidate).is_prime())
                .collect::<Vec<_>>();
            let mut enumerated = Vec::new();
            for_each_prime_in_range_scalar(low, high, |prime| enumerated.push(prime)).unwrap();

            assert_eq!(
                prime_count_in_range_scalar(low, high),
                expected.len(),
                "range=[{low},{high})"
            );
            assert_eq!(enumerated, expected, "range=[{low},{high})");
        }
    }

    #[test]
    fn prime_pi_matches_known_reference_counts() {
        for (n, expected) in [
            (0, 0),
            (1, 0),
            (2, 1),
            (10, 4),
            (100, 25),
            (1_000, 168),
            (1_000_000, 78_498),
            (10_000_000, 664_579),
            (100_000_000, 5_761_455),
            (1_000_000_000, 50_847_534),
        ] {
            assert_eq!(prime_pi_u64(n).unwrap(), expected, "pi({n})");
        }
    }

    #[test]
    fn prefix_pi_range_count_matches_segmented_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (10_000, 1_000_000),
            (1_000_000_000, 1_001_000_000),
        ] {
            let expected =
                prime_count_in_range(low, high, recommended_segment_size(low, high)).unwrap();
            assert_eq!(
                prime_count_in_range_prefix_pi(low, high).unwrap(),
                expected,
                "range=[{low},{high})"
            );
        }
    }

    #[test]
    fn parallel_prefix_pi_range_count_matches_serial_count() {
        for (low, high, threads, expected_threads) in [
            (0, 1_000_000_000, 8, 1),
            (1_000_000, 2_000_000, 8, 1),
            (1_000_000_000, 2_000_000_000, 8, 2),
            (2_000_000_000, 3_000_000_000, 1, 1),
        ] {
            assert_eq!(
                effective_prefix_pi_thread_count(low, high, threads),
                expected_threads
            );
            assert_eq!(
                prime_count_in_range_prefix_pi_parallel(low, high, threads).unwrap(),
                prime_count_in_range_prefix_pi(low, high).unwrap(),
                "range=[{low},{high})"
            );
        }
        assert_eq!(
            prime_count_in_range_prefix_pi_parallel(1_000, 2_000, 0),
            Err(RangeError::ThreadCountZero)
        );
    }

    #[test]
    fn high_u64_tiny_ranges_match_scalar_fallback() {
        let low = u64::MAX - 1_000;
        let high = u64::MAX;
        let expected_primes = (low..high)
            .filter(|&candidate| is_prime_u64(candidate).is_prime())
            .collect::<Vec<_>>();
        let expected = expected_primes.len();

        assert!(use_scalar_range_fallback(low, high));
        assert_eq!(primes_in_range(low, high, 64).unwrap(), expected_primes);
        assert_eq!(prime_count_in_range(low, high, 64).unwrap(), expected);
        assert_eq!(
            prime_count_in_range(low, high, high - low).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_bitpacked(low, high, 64).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_tracked_bytes(low, high, 64).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_presieve13(low, high, 64).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_presieve17(low, high, 64).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_wheel30(low, high, 64).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_wheel30_marks(low, high, 64).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_hybrid_wheel30_marks(low, high, 64).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_parallel(low, high, 64, 4).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_parallel_balanced(low, high, 64, 4).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_parallel_dynamic(low, high, 64, 4).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_wheel30_marks_parallel(low, high, 64, 4).unwrap(),
            expected
        );
        assert_eq!(
            prime_count_in_range_hybrid_wheel30_marks_parallel(low, high, 64, 4).unwrap(),
            expected
        );
    }

    #[test]
    fn high_u64_empty_range_stays_empty() {
        assert_eq!(prime_count_in_range(u64::MAX, u64::MAX, 64).unwrap(), 0);
        assert_eq!(
            primes_in_range(u64::MAX, u64::MAX, 64).unwrap(),
            Vec::<u64>::new()
        );
    }

    #[test]
    fn recommended_segment_size_tracks_base_prime_pressure() {
        assert_eq!(
            recommended_segment_size(0, 100_000_000),
            DEFAULT_SEGMENT_SIZE
        );
        assert_eq!(
            recommended_segment_size(100_000_000_000, 100_010_000_000),
            HIGH_OFFSET_SEGMENT_SIZE
        );
        assert_eq!(
            recommended_segment_size(1_000_000_000_000, 1_000_010_000_000),
            VERY_HIGH_OFFSET_SEGMENT_SIZE
        );
    }

    #[test]
    fn recommended_count_segment_size_uses_tuned_parallel_small_range() {
        assert_eq!(
            recommended_count_segment_size(0, 1_000_000, 8),
            PARALLEL_TINY_PREFIX_SEGMENT_SIZE
        );
        assert_eq!(
            recommended_count_segment_size(0, 10_000_000, 8),
            PARALLEL_SMALL_PREFIX_SEGMENT_SIZE
        );
        assert_eq!(
            recommended_count_segment_size(0, 100_000_000, 8),
            PARALLEL_MEDIUM_PREFIX_SEGMENT_SIZE
        );
        assert_eq!(
            recommended_count_segment_size(1_000_000_000_000, 1_000_010_000_000, 8),
            PARALLEL_VERY_HIGH_OFFSET_SEGMENT_SIZE
        );
        assert_eq!(
            recommended_count_segment_size(1_000_000_000_000, 1_000_010_000_000, 1),
            VERY_HIGH_OFFSET_SEGMENT_SIZE
        );
        assert_eq!(
            recommended_count_segment_size(0, 10_000_000, 1),
            DEFAULT_SEGMENT_SIZE
        );
    }

    #[test]
    fn recommended_count_mode_uses_structured_parallel_defaults() {
        assert_eq!(
            recommended_count_mode(0, 10_000_000, 1),
            PARALLEL_SMALL_PREFIX_COUNT_MODE
        );
        assert_eq!(
            recommended_count_mode(0, 1_000_000, 8),
            PARALLEL_TINY_PREFIX_COUNT_MODE
        );
        assert_eq!(
            recommended_count_mode(0, 10_000_000, 8),
            PARALLEL_SMALL_PREFIX_COUNT_MODE
        );
        assert_eq!(
            recommended_count_mode(0, 100_000_000, 8),
            PARALLEL_MEDIUM_PREFIX_COUNT_MODE
        );
        assert_eq!(recommended_count_mode(0, 1_000_000_000, 8), "prefix-pi");
        assert_eq!(recommended_count_mode(0, 1_000_000_001, 8), "segmented");
        assert_eq!(
            recommended_count_mode(1_000_000_000, 2_000_000_000, 8),
            "prefix-pi"
        );
        assert_eq!(
            recommended_count_mode(2_000_000_000, 3_000_000_000, 8),
            "prefix-pi"
        );
        assert_eq!(
            recommended_count_mode(2_000_000_000, 3_000_000_001, 8),
            "segmented"
        );
        assert_eq!(
            recommended_count_mode(3_000_000_000, 4_000_000_000, 8),
            "segmented"
        );
        assert_eq!(
            recommended_count_mode(1_000_000_000_000, 1_000_010_000_000, 8),
            PARALLEL_VERY_HIGH_OFFSET_COUNT_MODE
        );
        assert_eq!(recommended_count_mode(1_000_000, 2_000_000, 8), "dynamic");
    }

    #[test]
    fn parallel_count_matches_single_thread_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (1_000_000, 1_010_000),
            (1_000_000_000, 1_010_000_000),
        ] {
            let segment_size = recommended_segment_size(low, high);
            let expected = prime_count_in_range(low, high, segment_size).unwrap();
            for threads in [1, 2, 3, 4, 8] {
                assert_eq!(
                    prime_count_in_range_parallel(low, high, segment_size, threads).unwrap(),
                    expected,
                    "range=[{low},{high}), threads={threads}"
                );
            }
        }
    }

    #[test]
    fn balanced_split_covers_range_without_overlap() {
        for (low, high, parts) in [
            (0, 10, 3),
            (0, 1_000_000_000, 8),
            (1_000_000_000_000, 1_000_010_000_000, 8),
        ] {
            let chunks = split_range_by_sieve_work(low, high, parts);
            assert_eq!(chunks.first().map(|chunk| chunk.0), Some(low));
            assert_eq!(chunks.last().map(|chunk| chunk.1), Some(high));

            let mut cursor = low;
            for &(chunk_low, chunk_high) in &chunks {
                assert_eq!(chunk_low, cursor);
                assert!(chunk_low < chunk_high);
                cursor = chunk_high;
            }
            assert_eq!(cursor, high);
        }
    }

    #[test]
    fn balanced_parallel_count_matches_single_thread_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (0, 10_000_000),
            (1_000_000_000_000, 1_000_001_000_000),
        ] {
            let segment_size = recommended_count_segment_size(low, high, 8);
            let expected = prime_count_in_range(low, high, segment_size).unwrap();
            let actual =
                prime_count_in_range_parallel_balanced(low, high, segment_size, 8).unwrap();
            assert_eq!(actual, expected, "range=[{low},{high})");
        }
    }

    #[test]
    fn dynamic_parallel_count_matches_single_thread_count() {
        for (low, high) in [
            (0, 1_000),
            (0, 1_000_000),
            (0, 10_000_000),
            (0, 100_000_000),
            (1_000_000_000_000, 1_000_001_000_000),
        ] {
            let segment_size = recommended_count_segment_size(low, high, 8);
            let expected = prime_count_in_range(low, high, segment_size).unwrap();
            let actual = prime_count_in_range_parallel_dynamic(low, high, segment_size, 8).unwrap();
            assert_eq!(actual, expected, "range=[{low},{high})");
        }
    }

    #[test]
    fn dynamic_parallel_batch_size_keeps_small_ranges_parallelizable() {
        assert_eq!(dynamic_parallel_segments_per_batch(1, 8), 1);
        assert_eq!(dynamic_parallel_segments_per_batch(3, 8), 1);
        assert_eq!(dynamic_parallel_segments_per_batch(32, 8), 1);
        assert_eq!(dynamic_parallel_segments_per_batch(153, 8), 5);
        assert_eq!(dynamic_parallel_segments_per_batch(509, 8), 16);
        assert_eq!(dynamic_parallel_segments_per_batch(10_000, 8), 64);
    }

    #[test]
    fn parallel_count_rejects_zero_threads() {
        assert_eq!(
            prime_count_in_range_parallel(0, 100, 64, 0),
            Err(RangeError::ThreadCountZero)
        );
        assert_eq!(
            prime_count_in_range_parallel_dynamic(0, 100, 64, 0),
            Err(RangeError::ThreadCountZero)
        );
    }

    #[test]
    fn effective_parallel_thread_count_caps_to_segment_count() {
        assert_eq!(
            effective_parallel_thread_count(0, 10_000_000, 262_144, 8),
            8
        );
        let high_offset_span = 10_000_000u64;
        let high_offset_expected_workers =
            high_offset_span.div_ceil(PARALLEL_VERY_HIGH_OFFSET_SEGMENT_SIZE) as usize;
        assert_eq!(
            effective_parallel_thread_count(
                1_000_000_000_000,
                1_000_010_000_000,
                PARALLEL_VERY_HIGH_OFFSET_SEGMENT_SIZE,
                8
            ),
            high_offset_expected_workers
        );
        assert_eq!(
            effective_parallel_thread_count(1_000_000_000_000, 1_000_010_000_000, 4_194_304, 3),
            3
        );
    }
}
