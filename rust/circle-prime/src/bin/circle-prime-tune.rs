use std::collections::HashMap;
use std::env;
use std::io::{self, Write};
use std::process;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use circle_prime::{
    effective_parallel_thread_count, prime_count_in_range,
    prime_count_in_range_hybrid_wheel30_marks, prime_count_in_range_hybrid_wheel30_marks_parallel,
    prime_count_in_range_parallel, prime_count_in_range_parallel_balanced,
    prime_count_in_range_parallel_dynamic, prime_count_in_range_presieve13,
    prime_count_in_range_wheel30_marks, prime_count_in_range_wheel30_marks_parallel,
};

const DEFAULT_RANGES: &str = "0:1000000,0:10000000,1000000000:1010000000";
const DEFAULT_SEGMENT_SIZES: &str =
    "4096,8192,16384,32768,65536,131072,196608,262144,524288,1048576,2097152,3145728,4194304";
const DEFAULT_THREAD_COUNTS: &str = "1";
const DEFAULT_COUNT_MODES: &str = "segmented";

#[derive(Debug, Clone, Copy)]
struct RangeSpec {
    low: u64,
    high: u64,
}

#[derive(Debug, Clone, Copy)]
struct TuneRow {
    pass: u64,
    count_mode: CountMode,
    range: RangeSpec,
    segment_size: u64,
    requested_threads: usize,
    threads: usize,
    rounds: usize,
    count: u64,
    best_seconds: f64,
    median_seconds: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum CountMode {
    Segmented,
    Balanced,
    Dynamic,
    Presieve13,
    Wheel30Marks,
    HybridWheel30Marks,
}

impl CountMode {
    fn parse(raw: &str) -> Result<Self, String> {
        match raw {
            "segmented" => Ok(Self::Segmented),
            "balanced" => Ok(Self::Balanced),
            "dynamic" => Ok(Self::Dynamic),
            "presieve13" => Ok(Self::Presieve13),
            "wheel30-mark" | "wheel30-marks" => Ok(Self::Wheel30Marks),
            "hybrid-wheel30-mark" | "hybrid-wheel30-marks" => Ok(Self::HybridWheel30Marks),
            _ => Err(format!(
                "unknown count mode {raw:?}; expected segmented, balanced, dynamic, presieve13, wheel30-mark, or hybrid-wheel30-mark"
            )),
        }
    }

    fn as_str(self) -> &'static str {
        match self {
            Self::Segmented => "segmented",
            Self::Balanced => "balanced",
            Self::Dynamic => "dynamic",
            Self::Presieve13 => "presieve13",
            Self::Wheel30Marks => "wheel30-mark",
            Self::HybridWheel30Marks => "hybrid-wheel30-mark",
        }
    }

    fn effective_threads(self, general_effective_threads: usize) -> usize {
        match self {
            Self::Presieve13 => 1,
            _ => general_effective_threads,
        }
    }
}

fn main() {
    if let Err(message) = run(env::args().skip(1).collect()) {
        eprintln!("{message}");
        process::exit(2);
    }
}

fn run(args: Vec<String>) -> Result<(), String> {
    let seconds = optional_value(&args, "--seconds")
        .map(|value| {
            value
                .parse::<f64>()
                .map_err(|_| "--seconds must be a nonnegative number".to_string())
        })
        .transpose()?
        .unwrap_or(0.0);
    if seconds < 0.0 {
        return Err("--seconds must be nonnegative".to_string());
    }

    let rounds = optional_value(&args, "--rounds")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--rounds must be a positive integer".to_string())
        })
        .transpose()?
        .unwrap_or(3);
    if rounds == 0 {
        return Err("--rounds must be greater than zero".to_string());
    }

    let ranges = parse_ranges(optional_value(&args, "--ranges").unwrap_or(DEFAULT_RANGES))?;
    let segment_sizes = parse_segment_sizes(
        optional_value(&args, "--segment-sizes").unwrap_or(DEFAULT_SEGMENT_SIZES),
    )?;
    let thread_counts = parse_thread_counts(
        optional_value(&args, "--thread-counts").unwrap_or(DEFAULT_THREAD_COUNTS),
    )?;
    let count_modes =
        parse_count_modes(optional_value(&args, "--count-modes").unwrap_or(DEFAULT_COUNT_MODES))?;

    println!(
        "kind,timestamp_unix,pass,count_mode,low,high,span,segment_size,requested_threads,threads,rounds,count,best_ms,median_ms,rate_per_second,median_rate_per_second"
    );

    let started = Instant::now();
    let duration = (seconds > 0.0).then(|| Duration::from_secs_f64(seconds));
    let mut expected_counts: HashMap<(u64, u64), u64> = HashMap::new();
    let mut pass = 0u64;

    loop {
        pass += 1;
        for range in &ranges {
            for &segment_size in &segment_sizes {
                for &requested_threads in &thread_counts {
                    for &count_mode in &count_modes {
                        let row = measure(
                            *range,
                            segment_size,
                            requested_threads,
                            count_mode,
                            rounds,
                            pass,
                        )?;
                        match expected_counts.get(&(range.low, range.high)) {
                            Some(&expected) if expected != row.count => {
                                return Err(format!(
                                    "count changed for range [{},{}): expected {}, got {} at segment_size={}, threads={}, mode={}",
                                    range.low,
                                    range.high,
                                    expected,
                                    row.count,
                                    segment_size,
                                    requested_threads,
                                    count_mode.as_str(),
                                ));
                            }
                            Some(_) => {}
                            None => {
                                expected_counts.insert((range.low, range.high), row.count);
                            }
                        }
                        print_row(row)?;
                        if duration.is_some_and(|limit| started.elapsed() >= limit) {
                            return Ok(());
                        }
                    }
                }
            }
        }

        if duration.is_none() {
            return Ok(());
        }
    }
}

fn measure(
    range: RangeSpec,
    segment_size: u64,
    requested_threads: usize,
    count_mode: CountMode,
    rounds: usize,
    pass: u64,
) -> Result<TuneRow, String> {
    let mut best_seconds = f64::INFINITY;
    let threads = count_mode.effective_threads(effective_parallel_thread_count(
        range.low,
        range.high,
        segment_size,
        requested_threads,
    ));
    let expected_count = count_range_with_mode(range, segment_size, threads, count_mode)
        .map_err(|err| format!("range sieve warm-up failed: {err:?}"))?
        as u64;
    let mut timings = Vec::with_capacity(rounds);

    for _ in 0..rounds {
        let start = Instant::now();
        let count = count_range_with_mode(range, segment_size, threads, count_mode)
            .map_err(|err| format!("range sieve failed: {err:?}"))? as u64;
        let elapsed_seconds = start.elapsed().as_secs_f64();
        if expected_count != count {
            return Err(format!(
                "count changed between warm-up and timed round for [{},{}), segment_size={}, threads={}, mode={}: expected {}, got {}",
                range.low,
                range.high,
                segment_size,
                requested_threads,
                count_mode.as_str(),
                expected_count,
                count,
            ));
        }
        best_seconds = best_seconds.min(elapsed_seconds);
        timings.push(elapsed_seconds);
    }
    timings.sort_by(f64::total_cmp);
    let midpoint = timings.len() / 2;
    let median_seconds = if timings.len() % 2 == 0 {
        (timings[midpoint - 1] + timings[midpoint]) / 2.0
    } else {
        timings[midpoint]
    };

    Ok(TuneRow {
        pass,
        count_mode,
        range,
        segment_size,
        requested_threads,
        threads,
        rounds,
        count: expected_count,
        best_seconds,
        median_seconds,
    })
}

fn count_range_with_mode(
    range: RangeSpec,
    segment_size: u64,
    threads: usize,
    mode: CountMode,
) -> Result<usize, circle_prime::RangeError> {
    match mode {
        CountMode::Segmented => {
            if threads == 1 {
                prime_count_in_range(range.low, range.high, segment_size)
            } else {
                prime_count_in_range_parallel(range.low, range.high, segment_size, threads)
            }
        }
        CountMode::Balanced => {
            if threads == 1 {
                prime_count_in_range(range.low, range.high, segment_size)
            } else {
                prime_count_in_range_parallel_balanced(range.low, range.high, segment_size, threads)
            }
        }
        CountMode::Dynamic => {
            if threads == 1 {
                prime_count_in_range(range.low, range.high, segment_size)
            } else {
                prime_count_in_range_parallel_dynamic(range.low, range.high, segment_size, threads)
            }
        }
        CountMode::Presieve13 => {
            prime_count_in_range_presieve13(range.low, range.high, segment_size)
        }
        CountMode::Wheel30Marks => {
            if threads == 1 {
                prime_count_in_range_wheel30_marks(range.low, range.high, segment_size)
            } else {
                prime_count_in_range_wheel30_marks_parallel(
                    range.low,
                    range.high,
                    segment_size,
                    threads,
                )
            }
        }
        CountMode::HybridWheel30Marks => {
            if threads == 1 {
                prime_count_in_range_hybrid_wheel30_marks(range.low, range.high, segment_size)
            } else {
                prime_count_in_range_hybrid_wheel30_marks_parallel(
                    range.low,
                    range.high,
                    segment_size,
                    threads,
                )
            }
        }
    }
}

fn print_row(row: TuneRow) -> Result<(), String> {
    let span = row.range.high - row.range.low;
    let best_rate = if row.best_seconds == 0.0 {
        f64::INFINITY
    } else {
        span as f64 / row.best_seconds
    };
    let median_rate = if row.median_seconds == 0.0 {
        f64::INFINITY
    } else {
        span as f64 / row.median_seconds
    };
    println!(
        "tuning,{},{},{},{},{},{},{},{},{},{},{},{:.6},{:.6},{:.3},{:.3}",
        timestamp_unix(),
        row.pass,
        row.count_mode.as_str(),
        row.range.low,
        row.range.high,
        span,
        row.segment_size,
        row.requested_threads,
        row.threads,
        row.rounds,
        row.count,
        row.best_seconds * 1000.0,
        row.median_seconds * 1000.0,
        best_rate,
        median_rate
    );
    io::stdout()
        .flush()
        .map_err(|err| format!("failed to flush stdout: {err}"))
}

fn parse_ranges(raw: &str) -> Result<Vec<RangeSpec>, String> {
    let mut ranges = Vec::new();
    for item in split_csv(raw) {
        let Some((low_raw, high_raw)) = item.split_once(':') else {
            return Err(format!("range must be LOW:HIGH, got {item:?}"));
        };
        let low = parse_u64(low_raw, "LOW")?;
        let high = parse_u64(high_raw, "HIGH")?;
        if high <= low {
            return Err(format!("HIGH must be greater than LOW in {item:?}"));
        }
        ranges.push(RangeSpec { low, high });
    }
    if ranges.is_empty() {
        return Err("at least one range is required".to_string());
    }
    Ok(ranges)
}

fn parse_segment_sizes(raw: &str) -> Result<Vec<u64>, String> {
    let mut values = split_csv(raw)
        .into_iter()
        .map(|item| parse_u64(&item, "segment size"))
        .collect::<Result<Vec<_>, _>>()?;
    values.sort_unstable();
    values.dedup();
    if values.is_empty() {
        return Err("at least one segment size is required".to_string());
    }
    if values[0] == 0 {
        return Err("segment sizes must be positive".to_string());
    }
    Ok(values)
}

fn parse_thread_counts(raw: &str) -> Result<Vec<usize>, String> {
    let mut values = split_csv(raw)
        .into_iter()
        .map(|item| parse_usize(&item, "thread count"))
        .collect::<Result<Vec<_>, _>>()?;
    values.sort_unstable();
    values.dedup();
    if values.is_empty() {
        return Err("at least one thread count is required".to_string());
    }
    if values[0] == 0 {
        return Err("thread counts must be positive".to_string());
    }
    Ok(values)
}

fn parse_count_modes(raw: &str) -> Result<Vec<CountMode>, String> {
    let mut values = split_csv(raw)
        .into_iter()
        .map(|item| CountMode::parse(&item))
        .collect::<Result<Vec<_>, _>>()?;
    values.sort_unstable();
    values.dedup();
    if values.is_empty() {
        return Err("at least one count mode is required".to_string());
    }
    Ok(values)
}

fn parse_u64(raw: &str, label: &str) -> Result<u64, String> {
    raw.parse::<u64>()
        .map_err(|_| format!("{label} must fit in u64: {raw:?}"))
}

fn parse_usize(raw: &str, label: &str) -> Result<usize, String> {
    raw.parse::<usize>()
        .map_err(|_| format!("{label} must fit in usize: {raw:?}"))
}

fn split_csv(raw: &str) -> Vec<String> {
    raw.split(',')
        .map(str::trim)
        .filter(|item| !item.is_empty())
        .map(str::to_string)
        .collect()
}

fn optional_value<'a>(args: &'a [String], flag: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|window| window[0] == flag)
        .map(|window| window[1].as_str())
}

fn timestamp_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_secs())
        .unwrap_or(0)
}
