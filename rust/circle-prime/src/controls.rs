use std::convert::TryFrom;

use crate::segmented::RangeError;

pub fn control_primal_sieve_prime_count(low: u64, high: u64) -> Result<usize, RangeError> {
    if high <= low || high <= 2 {
        return Ok(0);
    }

    let limit = usize::try_from(high - 1).map_err(|_| RangeError::BaseLimitTooLarge)?;
    let start = usize::try_from(low.max(2)).map_err(|_| RangeError::BaseLimitTooLarge)?;
    let sieve = primal::Sieve::new(limit);
    Ok(sieve
        .primes_from(start)
        .take_while(|&prime| prime < high as usize)
        .count())
}

pub fn control_simple_sieve_prime_count(low: u64, high: u64) -> Result<usize, RangeError> {
    if high <= low || high <= 2 {
        return Ok(0);
    }

    let len = usize::try_from(high).map_err(|_| RangeError::BaseLimitTooLarge)?;
    let mut sieve = vec![true; len];
    sieve[0] = false;
    if high > 1 {
        sieve[1] = false;
    }

    let stop = (high - 1).isqrt();
    for p in 2..=stop {
        if sieve[p as usize] {
            let mut multiple = p * p;
            while multiple < high {
                sieve[multiple as usize] = false;
                multiple += p;
            }
        }
    }

    let start = usize::try_from(low.max(2)).map_err(|_| RangeError::BaseLimitTooLarge)?;
    Ok(sieve[start..].iter().filter(|&&is_prime| is_prime).count())
}

pub fn control_trial_division_prime_count_checked(
    low: u64,
    high: u64,
    max_span: u64,
) -> Result<usize, String> {
    if high.saturating_sub(low) > max_span {
        return Err(format!(
            "trial division control refused span {}; max_span is {}",
            high.saturating_sub(low),
            max_span
        ));
    }
    Ok(control_trial_division_prime_count(low, high))
}

pub fn control_trial_division_prime_count(low: u64, high: u64) -> usize {
    (low..high)
        .filter(|&candidate| trial_division_is_prime(candidate))
        .count()
}

fn trial_division_is_prime(n: u64) -> bool {
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
    while divisor <= n / divisor {
        if n % divisor == 0 {
            return false;
        }
        divisor += 2;
    }
    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::segmented::prime_count_in_range;

    #[test]
    fn simple_sieve_control_matches_segmented_counts() {
        for (low, high) in [
            (0, 100),
            (0, 1_000),
            (1_000, 10_000),
            (1_000_000, 1_010_000),
        ] {
            let control = control_simple_sieve_prime_count(low, high).unwrap();
            let segmented = prime_count_in_range(low, high, 1 << 12).unwrap();
            assert_eq!(control, segmented, "range=[{low},{high})");
        }
    }

    #[test]
    fn primal_sieve_control_matches_segmented_counts() {
        for (low, high) in [
            (0, 100),
            (0, 1_000),
            (1_000, 10_000),
            (1_000_000, 1_010_000),
        ] {
            let control = control_primal_sieve_prime_count(low, high).unwrap();
            let segmented = prime_count_in_range(low, high, 1 << 12).unwrap();
            assert_eq!(control, segmented, "range=[{low},{high})");
        }
    }

    #[test]
    fn trial_division_control_matches_segmented_counts() {
        for (low, high) in [(0, 100), (0, 1_000), (1_000, 2_000), (99_000, 100_000)] {
            let control = control_trial_division_prime_count(low, high);
            let segmented = prime_count_in_range(low, high, 1 << 12).unwrap();
            assert_eq!(control, segmented, "range=[{low},{high})");
        }
    }

    #[test]
    fn checked_trial_division_refuses_large_spans() {
        let error = control_trial_division_prime_count_checked(0, 1_000_001, 1_000_000)
            .expect_err("expected span guard to reject the trial control");
        assert!(error.contains("refused span"));
    }
}
