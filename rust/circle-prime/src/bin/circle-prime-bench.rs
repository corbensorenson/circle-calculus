use std::collections::BTreeSet;
use std::env;
use std::io::{BufRead, BufReader, Write};
use std::process;
use std::process::Command;
use std::process::Stdio;
use std::time::Instant;

use circle_prime::{
    base_primes, control_primal_sieve_prime_count, control_simple_sieve_prime_count,
    control_trial_division_prime_count, effective_parallel_thread_count,
    effective_prefix_pi_thread_count, is_prime_u64, next_prime_u64, prime_count_in_range,
    prime_count_in_range_bitpacked, prime_count_in_range_hybrid_wheel30_marks,
    prime_count_in_range_hybrid_wheel30_marks_parallel, prime_count_in_range_parallel,
    prime_count_in_range_parallel_balanced, prime_count_in_range_parallel_dynamic,
    prime_count_in_range_prefix_pi, prime_count_in_range_prefix_pi_parallel,
    prime_count_in_range_presieve13, prime_count_in_range_presieve13_parallel,
    prime_count_in_range_presieve17, prime_count_in_range_presieve17_parallel,
    prime_count_in_range_tracked_bytes, prime_count_in_range_wheel30,
    prime_count_in_range_wheel30_marks, prime_count_in_range_wheel30_marks_parallel,
    primes_in_range, recommended_count_mode, recommended_count_segment_size,
    recommended_segment_size,
};

const HIGH_OFFSET_LOW: u64 = 1_000_000_000_000;
const HIGH_OFFSET_HIGH: u64 = 1_000_010_000_000;
const U64_SCALAR_FALLBACK_LOW: u64 = u64::MAX - 100_000;
const U64_SCALAR_FALLBACK_HIGH: u64 = u64::MAX;
const U64_SCALAR_FALLBACK_SEGMENT_SIZE: u64 = 64;
const NEXT_PRIME_SEARCH_BATCH_REPETITIONS: u64 = 4_096;
const BENCH_SECTIONS: [&str; 20] = [
    "scalar",
    "next",
    "base",
    "range",
    "enumerate",
    "wheel30",
    "wheel30-mark",
    "parallel-wheel30-mark",
    "hybrid-wheel30-mark",
    "parallel-hybrid-wheel30-mark",
    "presieve13",
    "presieve17",
    "tracked-byte",
    "bitpacked",
    "parallel",
    "balanced",
    "dynamic",
    "high-offset",
    "cold",
    "controls",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CountMode {
    Segmented,
    Balanced,
    Dynamic,
    PrefixPi,
    Presieve13,
    Presieve17,
    Wheel30Marks,
    HybridWheel30Marks,
}

impl CountMode {
    fn parse(raw: &str) -> Result<Self, String> {
        match raw {
            "segmented" => Ok(Self::Segmented),
            "balanced" => Ok(Self::Balanced),
            "dynamic" => Ok(Self::Dynamic),
            "prefix-pi" | "pi" => Ok(Self::PrefixPi),
            "presieve13" => Ok(Self::Presieve13),
            "presieve17" => Ok(Self::Presieve17),
            "wheel30-mark" | "wheel30-marks" => Ok(Self::Wheel30Marks),
            "hybrid-wheel30-mark" | "hybrid-wheel30-marks" => Ok(Self::HybridWheel30Marks),
            _ => Err(format!(
                "unknown compiled count-mode default {raw:?}; expected segmented, balanced, dynamic, prefix-pi, presieve13, presieve17, wheel30-mark, or hybrid-wheel30-mark"
            )),
        }
    }

    fn effective_threads(
        self,
        low: u64,
        high: u64,
        general_effective_threads: usize,
        requested_threads: usize,
    ) -> usize {
        match self {
            Self::PrefixPi => effective_prefix_pi_thread_count(low, high, requested_threads),
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
    if args.first().map(String::as_str) == Some("--cold-noop-worker") {
        println!("0");
        return Ok(());
    }
    if args.first().map(String::as_str) == Some("--cold-plan-worker") {
        return cold_plan_worker(&args[1..]);
    }
    if args.first().map(String::as_str) == Some("--cold-worker") {
        return cold_worker(&args[1..]);
    }

    let rounds = optional_value(&args, "--rounds")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--rounds must be a positive integer".to_string())
        })
        .transpose()?
        .unwrap_or(5);
    if rounds == 0 {
        return Err("--rounds must be greater than zero".to_string());
    }
    let sections = parse_bench_sections(optional_value(&args, "--only"))?;

    let mut rows = Vec::new();
    if should_run_section(&sections, "scalar") {
        rows.push(bench_scalar_batch(rounds));
    }
    if should_run_section(&sections, "next") {
        rows.extend(bench_next_prime_searches(rounds));
    }
    if should_run_section(&sections, "base") {
        rows.extend(bench_base_prime_generation(rounds));
    }
    if should_run_section(&sections, "range") {
        rows.extend(bench_range_counts(rounds));
    }
    if should_run_section(&sections, "enumerate") {
        rows.extend(bench_range_enumeration(rounds));
    }
    if should_run_section(&sections, "wheel30") {
        rows.extend(bench_wheel30_range_counts(rounds));
    }
    if should_run_section(&sections, "wheel30-mark") {
        rows.extend(bench_wheel30_mark_range_counts(rounds));
    }
    if should_run_section(&sections, "parallel-wheel30-mark") {
        rows.extend(bench_parallel_wheel30_mark_range_counts(rounds));
    }
    if should_run_section(&sections, "hybrid-wheel30-mark") {
        rows.extend(bench_hybrid_wheel30_mark_range_counts(rounds));
    }
    if should_run_section(&sections, "parallel-hybrid-wheel30-mark") {
        rows.extend(bench_parallel_hybrid_wheel30_mark_range_counts(rounds));
    }
    if should_run_section(&sections, "presieve13") {
        rows.extend(bench_presieve13_range_counts(rounds));
    }
    if should_run_section(&sections, "presieve17") {
        rows.extend(bench_presieve17_range_counts(rounds));
    }
    if should_run_section(&sections, "tracked-byte") {
        rows.extend(bench_tracked_byte_range_counts(rounds));
    }
    if should_run_section(&sections, "bitpacked") {
        rows.extend(bench_bitpacked_range_counts(rounds));
    }
    if should_run_section(&sections, "parallel") {
        rows.extend(bench_parallel_range_counts(rounds));
    }
    if should_run_section(&sections, "balanced") {
        rows.extend(bench_parallel_balanced_range_counts(rounds));
    }
    if should_run_section(&sections, "dynamic") {
        rows.extend(bench_parallel_dynamic_range_counts(rounds));
    }
    if should_run_section(&sections, "high-offset") {
        rows.extend(bench_high_offset_range_counts(rounds));
    }
    if should_run_section(&sections, "cold") {
        rows.extend(bench_cold_process_counts(rounds));
    }
    if should_run_section(&sections, "controls") {
        rows.extend(bench_control_counts(rounds));
    }

    println!("kind,name,workload,segment_size,result,rounds,best_ms,rate_per_second,baseline,best_speedup");
    for row in &rows {
        print_timing_row(row);
    }
    print_speedups(&rows, rounds);
    Ok(())
}

fn parse_bench_sections(raw: Option<&str>) -> Result<BTreeSet<&'static str>, String> {
    let Some(raw) = raw else {
        return Ok(BTreeSet::new());
    };
    let mut sections = BTreeSet::new();
    for item in raw.split(',') {
        let section = item.trim();
        if section.is_empty() {
            continue;
        }
        if section == "all" {
            return Ok(BTreeSet::new());
        }
        let Some(&canonical) = BENCH_SECTIONS
            .iter()
            .find(|&&candidate| candidate == section)
        else {
            return Err(format!(
                "unknown --only section {section:?}; expected one of all, {}",
                BENCH_SECTIONS.join(", ")
            ));
        };
        sections.insert(canonical);
    }
    if sections.is_empty() {
        return Err("--only must include at least one benchmark section".to_string());
    }
    Ok(sections)
}

fn should_run_section(sections: &BTreeSet<&'static str>, section: &str) -> bool {
    sections.is_empty() || sections.contains(section)
}

#[derive(Debug, Clone, Copy)]
struct ColdWorkerPlan {
    low: u64,
    high: u64,
    segment_size: u64,
    mode: CountMode,
    worker_threads: usize,
}

fn parse_cold_worker_plan(args: &[String], command: &str) -> Result<ColdWorkerPlan, String> {
    let low = required_value(
        args,
        0,
        &format!("{command} requires LOW HIGH SEGMENT_SIZE"),
    )?
    .parse::<u64>()
    .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = required_value(
        args,
        1,
        &format!("{command} requires LOW HIGH SEGMENT_SIZE"),
    )?
    .parse::<u64>()
    .map_err(|_| "HIGH must fit in u64".to_string())?;
    let segment_size = required_value(
        args,
        2,
        &format!("{command} requires LOW HIGH SEGMENT_SIZE"),
    )?
    .parse::<u64>()
    .map_err(|_| "SEGMENT_SIZE must fit in u64".to_string())?;
    let requested_threads = args
        .get(3)
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "THREADS must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(1);
    if requested_threads == 0 {
        return Err("THREADS must be greater than zero".to_string());
    }

    let mode = match args.get(4).map(String::as_str) {
        Some("default") => CountMode::parse(recommended_count_mode(low, high, requested_threads))
            .expect("compiled count-mode default must be valid"),
        Some(raw) => CountMode::parse(raw)?,
        None => CountMode::Segmented,
    };
    let worker_threads = mode.effective_threads(
        low,
        high,
        effective_parallel_thread_count(low, high, segment_size, requested_threads),
        requested_threads,
    );
    Ok(ColdWorkerPlan {
        low,
        high,
        segment_size,
        mode,
        worker_threads,
    })
}

fn cold_plan_worker(args: &[String]) -> Result<(), String> {
    let plan = parse_cold_worker_plan(args, "--cold-plan-worker")?;
    println!("{}", plan.worker_threads);
    Ok(())
}

fn cold_worker(args: &[String]) -> Result<(), String> {
    let plan = parse_cold_worker_plan(args, "--cold-worker")?;
    let count = if matches!(plan.mode, CountMode::Segmented) && plan.worker_threads == 1 {
        prime_count_in_range(plan.low, plan.high, plan.segment_size)
    } else {
        count_range_with_mode(
            plan.low,
            plan.high,
            plan.segment_size,
            plan.worker_threads,
            plan.mode,
        )
    }
    .map_err(|err| format!("range sieve benchmark failed: {err:?}"))?;
    println!("{count}");
    Ok(())
}

#[derive(Debug, Clone)]
struct BenchRow {
    name: &'static str,
    workload: u64,
    segment_size: u64,
    result: u64,
    rounds: usize,
    best_seconds: f64,
}

fn bench_scalar_batch(rounds: usize) -> BenchRow {
    let candidates = scalar_candidates();
    measure(
        "scalar_u64_batch",
        candidates.len() as u64,
        0,
        rounds,
        || {
            candidates
                .iter()
                .filter(|&&candidate| is_prime_u64(candidate).is_prime())
                .count() as u64
        },
    )
}

fn bench_next_prime_searches(rounds: usize) -> Vec<BenchRow> {
    [
        90u64,
        1_000_000u64,
        4_294_967_000u64,
        1_000_000_000_000u64,
        18_446_744_073_709_551_500u64,
    ]
    .into_iter()
    .map(|start| {
        measure(
            "next_prime_search",
            start,
            NEXT_PRIME_SEARCH_BATCH_REPETITIONS,
            rounds,
            || {
                let mut prime = 0u64;
                for _ in 0..NEXT_PRIME_SEARCH_BATCH_REPETITIONS {
                    prime = next_prime_u64(start).prime.unwrap_or(0);
                }
                prime
            },
        )
    })
    .collect()
}

fn bench_base_prime_generation(rounds: usize) -> Vec<BenchRow> {
    [10_000u64, 1_000_000u64]
        .into_iter()
        .map(|limit| {
            measure("base_prime_generation", limit, 0, rounds, || {
                base_primes(limit)
                    .expect("base prime generation benchmark failed")
                    .len() as u64
            })
        })
        .collect()
}

fn bench_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (1_000_000u64, 1 << 15),
        (1_000_000u64, 3 << 16),
        (1_000_000u64, 1 << 18),
        (1_000_000u64, 1 << 20),
        (10_000_000u64, 1 << 16),
        (10_000_000u64, 3 << 16),
        (10_000_000u64, 1 << 18),
        (10_000_000u64, 1 << 20),
        (100_000_000u64, 1 << 18),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure("segmented_range_count", high, segment_size, rounds, || {
            prime_count_in_range(0, high, segment_size).expect("range sieve benchmark failed")
                as u64
        })
    })
    .collect()
}

fn bench_range_enumeration(rounds: usize) -> Vec<BenchRow> {
    [(1_000_000u64, 1 << 18), (10_000_000u64, 1 << 18)]
        .into_iter()
        .map(|(high, segment_size)| {
            measure("enumerate_range_primes", high, segment_size, rounds, || {
                primes_in_range(0, high, segment_size)
                    .expect("range prime enumeration benchmark failed")
                    .len() as u64
            })
        })
        .collect()
}

fn bench_bitpacked_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (1_000_000u64, 1 << 15),
        (1_000_000u64, 1 << 18),
        (10_000_000u64, 1 << 17),
        (10_000_000u64, 1 << 18),
        (100_000_000u64, 1 << 18),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure("bitpacked_range_count", high, segment_size, rounds, || {
            prime_count_in_range_bitpacked(0, high, segment_size)
                .expect("bitpacked range sieve benchmark failed") as u64
        })
    })
    .collect()
}

fn bench_tracked_byte_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (1_000_000u64, 1 << 15),
        (1_000_000u64, 1 << 18),
        (10_000_000u64, 1 << 17),
        (10_000_000u64, 1 << 18),
        (100_000_000u64, 1 << 18),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure(
            "tracked_byte_range_count",
            high,
            segment_size,
            rounds,
            || {
                prime_count_in_range_tracked_bytes(0, high, segment_size)
                    .expect("tracked byte range sieve benchmark failed") as u64
            },
        )
    })
    .collect()
}

fn bench_presieve13_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (10_000_000u64, 1 << 17),
        (10_000_000u64, 1 << 18),
        (100_000_000u64, 1 << 17),
        (100_000_000u64, 1 << 18),
        (1_000_000_000u64, 3 << 16),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure("presieve13_range_count", high, segment_size, rounds, || {
            prime_count_in_range_presieve13(0, high, segment_size)
                .expect("presieve13 range sieve benchmark failed") as u64
        })
    })
    .collect()
}

fn bench_presieve17_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (10_000_000u64, 1 << 17),
        (10_000_000u64, 1 << 18),
        (100_000_000u64, 1 << 17),
        (100_000_000u64, 1 << 18),
        (1_000_000_000u64, 3 << 16),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure("presieve17_range_count", high, segment_size, rounds, || {
            prime_count_in_range_presieve17(0, high, segment_size)
                .expect("presieve17 range sieve benchmark failed") as u64
        })
    })
    .collect()
}

fn bench_wheel30_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (1_000_000u64, 1 << 15),
        (1_000_000u64, 1 << 18),
        (10_000_000u64, 1 << 17),
        (10_000_000u64, 1 << 18),
        (100_000_000u64, 1 << 18),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure("wheel30_range_count", high, segment_size, rounds, || {
            prime_count_in_range_wheel30(0, high, segment_size)
                .expect("wheel30 range sieve benchmark failed") as u64
        })
    })
    .collect()
}

fn bench_wheel30_mark_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (1_000_000u64, 1 << 15),
        (1_000_000u64, 1 << 18),
        (10_000_000u64, 1 << 17),
        (10_000_000u64, 1 << 18),
        (100_000_000u64, 1 << 18),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure(
            "wheel30_mark_range_count",
            high,
            segment_size,
            rounds,
            || {
                prime_count_in_range_wheel30_marks(0, high, segment_size)
                    .expect("wheel30 mark range sieve benchmark failed") as u64
            },
        )
    })
    .collect()
}

fn bench_parallel_wheel30_mark_range_counts(rounds: usize) -> Vec<BenchRow> {
    let mut rows = Vec::new();
    for high in [100_000_000u64, 1_000_000_000u64] {
        for segment_size in parallel_segment_size_candidates(high) {
            rows.push(measure(
                "parallel_wheel30_mark_range_count_8t",
                high,
                segment_size,
                rounds,
                || {
                    prime_count_in_range_wheel30_marks_parallel(0, high, segment_size, 8)
                        .expect("parallel wheel30 mark range sieve benchmark failed")
                        as u64
                },
            ));
        }
    }
    rows
}

fn bench_hybrid_wheel30_mark_range_counts(rounds: usize) -> Vec<BenchRow> {
    [
        (10_000_000u64, 1 << 17),
        (10_000_000u64, 1 << 18),
        (100_000_000u64, 1 << 18),
        (1_000_000_000u64, 1 << 18),
    ]
    .into_iter()
    .map(|(high, segment_size)| {
        measure(
            "hybrid_wheel30_mark_range_count",
            high,
            segment_size,
            rounds,
            || {
                prime_count_in_range_hybrid_wheel30_marks(0, high, segment_size)
                    .expect("hybrid wheel30 mark range sieve benchmark failed")
                    as u64
            },
        )
    })
    .collect()
}

fn bench_parallel_hybrid_wheel30_mark_range_counts(rounds: usize) -> Vec<BenchRow> {
    let mut rows = Vec::new();
    for high in [100_000_000u64, 1_000_000_000u64] {
        for segment_size in parallel_segment_size_candidates(high) {
            rows.push(measure(
                "parallel_hybrid_wheel30_mark_range_count_8t",
                high,
                segment_size,
                rounds,
                || {
                    prime_count_in_range_hybrid_wheel30_marks_parallel(0, high, segment_size, 8)
                        .expect("parallel hybrid wheel30 mark range sieve benchmark failed")
                        as u64
                },
            ));
        }
    }
    rows
}

fn bench_parallel_range_counts(rounds: usize) -> Vec<BenchRow> {
    let workloads = [10_000_000u64, 100_000_000u64, 1_000_000_000u64];
    let mut rows = Vec::new();
    for high in workloads {
        for segment_size in parallel_segment_size_candidates(high) {
            rows.push(bench_parallel_range_count(
                "parallel_segmented_range_count_2t",
                high,
                segment_size,
                2,
                rounds,
            ));
            rows.push(bench_parallel_range_count(
                "parallel_segmented_range_count_4t",
                high,
                segment_size,
                4,
                rounds,
            ));
            rows.push(bench_parallel_range_count(
                "parallel_segmented_range_count_8t",
                high,
                segment_size,
                8,
                rounds,
            ));
        }
    }
    rows
}

fn bench_parallel_balanced_range_counts(rounds: usize) -> Vec<BenchRow> {
    let mut rows = Vec::new();
    for high in [100_000_000u64, 1_000_000_000u64] {
        for segment_size in parallel_segment_size_candidates(high) {
            rows.push(measure(
                "parallel_balanced_segmented_range_count_8t",
                high,
                segment_size,
                rounds,
                || {
                    prime_count_in_range_parallel_balanced(0, high, segment_size, 8)
                        .expect("balanced parallel range sieve benchmark failed")
                        as u64
                },
            ));
        }
    }
    rows
}

fn bench_parallel_dynamic_range_counts(rounds: usize) -> Vec<BenchRow> {
    let mut rows = Vec::new();
    for high in [10_000_000u64, 100_000_000u64, 1_000_000_000u64] {
        for segment_size in parallel_segment_size_candidates(high) {
            rows.push(measure(
                "parallel_dynamic_segmented_range_count_8t",
                high,
                segment_size,
                rounds,
                || {
                    prime_count_in_range_parallel_dynamic(0, high, segment_size, 8)
                        .expect("dynamic parallel range sieve benchmark failed")
                        as u64
                },
            ));
        }
    }
    rows
}

fn bench_high_offset_range_counts(rounds: usize) -> Vec<BenchRow> {
    let single_segment_size = recommended_segment_size(HIGH_OFFSET_LOW, HIGH_OFFSET_HIGH);
    let parallel_segment_size =
        recommended_count_segment_size(HIGH_OFFSET_LOW, HIGH_OFFSET_HIGH, 8);
    vec![
        measure(
            "high_offset_segmented_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            single_segment_size,
            rounds,
            || {
                prime_count_in_range(HIGH_OFFSET_LOW, HIGH_OFFSET_HIGH, single_segment_size)
                    .expect("high-offset range sieve benchmark failed") as u64
            },
        ),
        measure(
            "parallel_high_offset_segmented_range_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_parallel(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                    8,
                )
                .expect("parallel high-offset range sieve benchmark failed") as u64
            },
        ),
        measure(
            "parallel_high_offset_default_range_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_default(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                    8,
                )
                .expect("default parallel high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "parallel_high_offset_balanced_segmented_range_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_parallel_balanced(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                    8,
                )
                .expect("balanced parallel high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "high_offset_presieve13_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_presieve13(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                )
                .expect("presieve13 high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "parallel_high_offset_presieve13_range_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_presieve13_parallel(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                    8,
                )
                .expect("parallel presieve13 high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "high_offset_presieve17_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_presieve17(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                )
                .expect("presieve17 high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "parallel_high_offset_presieve17_range_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_presieve17_parallel(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                    8,
                )
                .expect("parallel presieve17 high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "high_offset_bitpacked_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_bitpacked(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                )
                .expect("bitpacked high-offset range sieve benchmark failed") as u64
            },
        ),
        measure(
            "high_offset_tracked_byte_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_tracked_bytes(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                )
                .expect("tracked byte high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "high_offset_wheel30_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_wheel30(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                )
                .expect("wheel30 high-offset range sieve benchmark failed") as u64
            },
        ),
        measure(
            "high_offset_wheel30_mark_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_wheel30_marks(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                )
                .expect("wheel30 mark high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "parallel_high_offset_wheel30_mark_range_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_wheel30_marks_parallel(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                    8,
                )
                .expect("parallel wheel30 mark high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "high_offset_hybrid_wheel30_mark_range_count",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_hybrid_wheel30_marks(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                )
                .expect("hybrid wheel30 mark high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "parallel_high_offset_hybrid_wheel30_mark_range_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            parallel_segment_size,
            rounds,
            || {
                prime_count_in_range_hybrid_wheel30_marks_parallel(
                    HIGH_OFFSET_LOW,
                    HIGH_OFFSET_HIGH,
                    parallel_segment_size,
                    8,
                )
                .expect("parallel hybrid wheel30 mark high-offset range sieve benchmark failed")
                    as u64
            },
        ),
        measure(
            "high_offset_u64_scalar_fallback_range_count",
            U64_SCALAR_FALLBACK_HIGH - U64_SCALAR_FALLBACK_LOW,
            U64_SCALAR_FALLBACK_SEGMENT_SIZE,
            rounds,
            || {
                prime_count_in_range(
                    U64_SCALAR_FALLBACK_LOW,
                    U64_SCALAR_FALLBACK_HIGH,
                    U64_SCALAR_FALLBACK_SEGMENT_SIZE,
                )
                .expect("u64 scalar fallback range count benchmark failed") as u64
            },
        ),
        measure(
            "high_offset_u64_scalar_naive_control_count",
            U64_SCALAR_FALLBACK_HIGH - U64_SCALAR_FALLBACK_LOW,
            0,
            rounds,
            || naive_scalar_count(U64_SCALAR_FALLBACK_LOW, U64_SCALAR_FALLBACK_HIGH) as u64,
        ),
    ]
}

fn naive_scalar_count(low: u64, high: u64) -> usize {
    (low..high)
        .filter(|&candidate| is_prime_u64(candidate).is_prime())
        .count()
}

fn parallel_segment_size_candidates(high: u64) -> Vec<u64> {
    let mut candidates = vec![
        1 << 17,
        3 << 16,
        recommended_segment_size(0, high),
        recommended_count_segment_size(0, high, 8),
    ];
    candidates.sort_unstable();
    candidates.dedup();
    candidates
}

fn bench_parallel_range_count(
    name: &'static str,
    high: u64,
    segment_size: u64,
    threads: usize,
    rounds: usize,
) -> BenchRow {
    measure(name, high, segment_size, rounds, || {
        prime_count_in_range_parallel(0, high, segment_size, threads)
            .expect("parallel range sieve benchmark failed") as u64
    })
}

fn bench_cold_process_counts(rounds: usize) -> Vec<BenchRow> {
    let mut rows: Vec<BenchRow> = [1_000_000u64, 10_000_000u64]
        .into_iter()
        .map(|high| {
            let segment_size = recommended_segment_size(0, high);
            measure(
                "cold_process_segmented_range_count",
                high,
                segment_size,
                rounds,
                || cold_process_prime_count(0, high, segment_size, 1, None),
            )
        })
        .collect();

    for high in [10_000_000u64, 100_000_000u64] {
        let segment_size = recommended_count_segment_size(0, high, 8);
        rows.push(measure(
            "cold_process_parallel_segmented_range_count_8t",
            high,
            segment_size,
            rounds,
            || cold_process_prime_count(0, high, segment_size, 8, None),
        ));
        rows.push(measure(
            "cold_cli_parallel_default_range_count_8t",
            high,
            segment_size,
            rounds,
            || cold_cli_prime_count(0, high, segment_size, 8),
        ));
    }

    let high_offset_segment_size =
        recommended_count_segment_size(HIGH_OFFSET_LOW, HIGH_OFFSET_HIGH, 8);
    rows.push(measure(
        "cold_process_high_offset_noop_worker",
        0,
        0,
        rounds,
        cold_process_noop_worker,
    ));
    rows.push(measure(
        "cold_process_high_offset_default_plan_8t",
        HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
        high_offset_segment_size,
        rounds,
        || {
            cold_process_plan_resolution(
                HIGH_OFFSET_LOW,
                HIGH_OFFSET_HIGH,
                high_offset_segment_size,
                8,
                Some("default"),
            )
        },
    ));
    rows.push(measure(
        "cold_count_binary_high_offset_noop",
        0,
        0,
        rounds,
        cold_count_binary_noop,
    ));
    rows.push(measure(
        "cold_count_binary_high_offset_default_plan_8t",
        HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
        high_offset_segment_size,
        rounds,
        || {
            cold_count_binary_plan_resolution(
                HIGH_OFFSET_LOW,
                HIGH_OFFSET_HIGH,
                high_offset_segment_size,
                8,
            )
        },
    ));
    rows.push(measure(
        "cold_process_parallel_high_offset_default_range_count_1t",
        HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
        high_offset_segment_size,
        rounds,
        || {
            cold_process_prime_count(
                HIGH_OFFSET_LOW,
                HIGH_OFFSET_HIGH,
                high_offset_segment_size,
                1,
                Some("default"),
            )
        },
    ));
    rows.push(measure(
        "cold_process_parallel_high_offset_segmented_range_count_8t",
        HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
        high_offset_segment_size,
        rounds,
        || {
            cold_process_prime_count(
                HIGH_OFFSET_LOW,
                HIGH_OFFSET_HIGH,
                high_offset_segment_size,
                8,
                None,
            )
        },
    ));
    rows.push(measure(
        "cold_process_parallel_high_offset_default_range_count_8t",
        HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
        high_offset_segment_size,
        rounds,
        || {
            cold_process_prime_count(
                HIGH_OFFSET_LOW,
                HIGH_OFFSET_HIGH,
                high_offset_segment_size,
                8,
                Some("default"),
            )
        },
    ));
    rows.push(measure(
        "cold_cli_parallel_high_offset_default_range_count_8t",
        HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
        high_offset_segment_size,
        rounds,
        || {
            cold_cli_prime_count(
                HIGH_OFFSET_LOW,
                HIGH_OFFSET_HIGH,
                high_offset_segment_size,
                8,
            )
        },
    ));
    rows.push(measure(
        "cold_count_binary_parallel_high_offset_default_range_count_8t",
        HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
        high_offset_segment_size,
        rounds,
        || {
            cold_count_binary_prime_count(
                HIGH_OFFSET_LOW,
                HIGH_OFFSET_HIGH,
                high_offset_segment_size,
                8,
            )
        },
    ));
    if external_primesieve_available() {
        rows.push(measure(
            "cold_external_primesieve_high_offset_count_8t",
            HIGH_OFFSET_HIGH - HIGH_OFFSET_LOW,
            0,
            rounds,
            || cold_external_primesieve_prime_count(HIGH_OFFSET_LOW, HIGH_OFFSET_HIGH, 8),
        ));
    }
    rows.push(measure_count_server_prime_count(
        "hot_cli_count_server_parallel_high_offset_default_range_count_8t",
        HIGH_OFFSET_LOW,
        HIGH_OFFSET_HIGH,
        high_offset_segment_size,
        8,
        None,
        rounds,
    ));
    rows.push(measure_count_server_prime_count(
        "hot_cli_count_server_parallel_high_offset_segmented_count_8t",
        HIGH_OFFSET_LOW,
        HIGH_OFFSET_HIGH,
        high_offset_segment_size,
        8,
        Some("segmented"),
        rounds,
    ));
    rows.push(measure_count_server_prime_count(
        "hot_cli_count_server_parallel_high_offset_presieve13_count_8t",
        HIGH_OFFSET_LOW,
        HIGH_OFFSET_HIGH,
        high_offset_segment_size,
        8,
        Some("presieve13"),
        rounds,
    ));
    rows.push(measure_count_server_prime_count(
        "hot_cli_count_server_parallel_high_offset_presieve17_count_8t",
        HIGH_OFFSET_LOW,
        HIGH_OFFSET_HIGH,
        high_offset_segment_size,
        8,
        Some("presieve17"),
        rounds,
    ));

    rows
}

fn bench_control_counts(rounds: usize) -> Vec<BenchRow> {
    let mut rows = Vec::new();

    for high in [1_000_000u64, 10_000_000u64] {
        rows.push(measure(
            "control_primal_sieve_count",
            high,
            0,
            rounds,
            || {
                control_primal_sieve_prime_count(0, high)
                    .expect("primal sieve control benchmark failed") as u64
            },
        ));
    }

    for high in [1_000_000u64, 10_000_000u64] {
        rows.push(measure(
            "control_simple_sieve_count",
            high,
            0,
            rounds,
            || {
                control_simple_sieve_prime_count(0, high)
                    .expect("simple sieve control benchmark failed") as u64
            },
        ));
    }

    for high in [100_000u64, 1_000_000u64] {
        rows.push(measure(
            "control_trial_division_count",
            high,
            0,
            rounds,
            || control_trial_division_prime_count(0, high) as u64,
        ));
    }

    rows
}

fn scalar_candidates() -> Vec<u64> {
    let mut candidates = Vec::with_capacity(200_000);
    let mut state = 0x9e37_79b9_7f4a_7c15u64;
    for _ in 0..200_000 {
        state = state
            .wrapping_mul(6_364_136_223_846_793_005)
            .wrapping_add(1_442_695_040_888_963_407);
        candidates.push(state | 1);
    }
    candidates
}

fn measure<F>(
    name: &'static str,
    workload: u64,
    segment_size: u64,
    rounds: usize,
    mut run_once: F,
) -> BenchRow
where
    F: FnMut() -> u64,
{
    let mut expected_result = None;
    let mut best_seconds = f64::INFINITY;

    for _ in 0..rounds {
        let start = Instant::now();
        let result = run_once();
        let elapsed_seconds = start.elapsed().as_secs_f64();
        match expected_result {
            Some(expected) => assert_eq!(
                expected, result,
                "benchmark result changed between rounds for {name}"
            ),
            None => expected_result = Some(result),
        }
        best_seconds = best_seconds.min(elapsed_seconds);
    }

    BenchRow {
        name,
        workload,
        segment_size,
        result: expected_result.expect("rounds must be positive"),
        rounds,
        best_seconds,
    }
}

fn prime_count_in_range_default(
    low: u64,
    high: u64,
    segment_size: u64,
    requested_threads: usize,
) -> Result<usize, circle_prime::RangeError> {
    let mode = CountMode::parse(recommended_count_mode(low, high, requested_threads))
        .expect("compiled count-mode default must be valid");
    let worker_threads = mode.effective_threads(
        low,
        high,
        effective_parallel_thread_count(low, high, segment_size, requested_threads),
        requested_threads,
    );
    count_range_with_mode(low, high, segment_size, worker_threads, mode)
}

fn count_range_with_mode(
    low: u64,
    high: u64,
    segment_size: u64,
    worker_threads: usize,
    mode: CountMode,
) -> Result<usize, circle_prime::RangeError> {
    match mode {
        CountMode::Segmented => {
            if worker_threads == 1 {
                prime_count_in_range(low, high, segment_size)
            } else {
                prime_count_in_range_parallel(low, high, segment_size, worker_threads)
            }
        }
        CountMode::Balanced => {
            if worker_threads == 1 {
                prime_count_in_range(low, high, segment_size)
            } else {
                prime_count_in_range_parallel_balanced(low, high, segment_size, worker_threads)
            }
        }
        CountMode::Dynamic => {
            if worker_threads == 1 {
                prime_count_in_range(low, high, segment_size)
            } else {
                prime_count_in_range_parallel_dynamic(low, high, segment_size, worker_threads)
            }
        }
        CountMode::PrefixPi => {
            if worker_threads == 1 {
                prime_count_in_range_prefix_pi(low, high)
            } else {
                prime_count_in_range_prefix_pi_parallel(low, high, worker_threads)
            }
        }
        CountMode::Presieve13 => {
            if worker_threads == 1 {
                prime_count_in_range_presieve13(low, high, segment_size)
            } else {
                prime_count_in_range_presieve13_parallel(low, high, segment_size, worker_threads)
            }
        }
        CountMode::Presieve17 => {
            if worker_threads == 1 {
                prime_count_in_range_presieve17(low, high, segment_size)
            } else {
                prime_count_in_range_presieve17_parallel(low, high, segment_size, worker_threads)
            }
        }
        CountMode::Wheel30Marks => {
            if worker_threads == 1 {
                prime_count_in_range_wheel30_marks(low, high, segment_size)
            } else {
                prime_count_in_range_wheel30_marks_parallel(low, high, segment_size, worker_threads)
            }
        }
        CountMode::HybridWheel30Marks => {
            if worker_threads == 1 {
                prime_count_in_range_hybrid_wheel30_marks(low, high, segment_size)
            } else {
                prime_count_in_range_hybrid_wheel30_marks_parallel(
                    low,
                    high,
                    segment_size,
                    worker_threads,
                )
            }
        }
    }
}

fn cold_process_prime_count(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
    count_mode: Option<&str>,
) -> u64 {
    let executable = env::current_exe().expect("failed to locate benchmark executable");
    let mut command = Command::new(executable);
    command
        .arg("--cold-worker")
        .arg(low.to_string())
        .arg(high.to_string())
        .arg(segment_size.to_string())
        .arg(threads.to_string());
    if let Some(count_mode) = count_mode {
        command.arg(count_mode);
    }
    let output = command
        .output()
        .expect("failed to spawn cold benchmark worker");
    assert!(
        output.status.success(),
        "cold benchmark worker failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout)
        .expect("cold benchmark worker emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("cold benchmark worker did not emit a count")
}

fn cold_process_noop_worker() -> u64 {
    let executable = env::current_exe().expect("failed to locate benchmark executable");
    let output = Command::new(executable)
        .arg("--cold-noop-worker")
        .output()
        .expect("failed to spawn cold benchmark noop worker");
    assert!(
        output.status.success(),
        "cold benchmark noop worker failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout)
        .expect("cold benchmark noop worker emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("cold benchmark noop worker did not emit a count")
}

fn cold_process_plan_resolution(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
    count_mode: Option<&str>,
) -> u64 {
    let executable = env::current_exe().expect("failed to locate benchmark executable");
    let mut command = Command::new(executable);
    command
        .arg("--cold-plan-worker")
        .arg(low.to_string())
        .arg(high.to_string())
        .arg(segment_size.to_string())
        .arg(threads.to_string());
    if let Some(count_mode) = count_mode {
        command.arg(count_mode);
    }
    let output = command
        .output()
        .expect("failed to spawn cold benchmark plan worker");
    assert!(
        output.status.success(),
        "cold benchmark plan worker failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout)
        .expect("cold benchmark plan worker emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("cold benchmark plan worker did not emit a worker count")
}

fn external_primesieve_available() -> bool {
    match Command::new("primesieve")
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
    {
        Ok(status) => status.success(),
        Err(_) => false,
    }
}

fn cold_external_primesieve_prime_count(low: u64, high: u64, threads: usize) -> u64 {
    assert!(
        high > low,
        "external primesieve benchmark requires nonempty range"
    );
    let output = Command::new("primesieve")
        .arg(low.to_string())
        .arg((high - 1).to_string())
        .arg("--count")
        .arg("--quiet")
        .arg(format!("--threads={threads}"))
        .output()
        .expect("failed to spawn external primesieve");
    assert!(
        output.status.success(),
        "external primesieve failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout)
        .expect("external primesieve emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("external primesieve did not emit a count")
}

fn cold_cli_prime_count(low: u64, high: u64, segment_size: u64, threads: usize) -> u64 {
    let executable = circle_prime_cli_executable();
    let output = Command::new(&executable)
        .arg("range")
        .arg(low.to_string())
        .arg(high.to_string())
        .arg("--count")
        .arg("--segment-size")
        .arg(segment_size.to_string())
        .arg("--threads")
        .arg(threads.to_string())
        .output()
        .expect("failed to spawn cold CLI benchmark worker");
    assert!(
        output.status.success(),
        "cold CLI benchmark worker failed: {}\nexecutable: {}",
        String::from_utf8_lossy(&output.stderr),
        executable.display(),
    );
    String::from_utf8(output.stdout)
        .expect("cold CLI benchmark worker emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("cold CLI benchmark worker did not emit a count")
}

fn cold_count_binary_prime_count(low: u64, high: u64, segment_size: u64, threads: usize) -> u64 {
    let executable = circle_prime_count_executable();
    let output = Command::new(&executable)
        .arg(low.to_string())
        .arg(high.to_string())
        .arg("--segment-size")
        .arg(segment_size.to_string())
        .arg("--threads")
        .arg(threads.to_string())
        .output()
        .expect("failed to spawn cold count-binary benchmark worker");
    assert!(
        output.status.success(),
        "cold count-binary benchmark worker failed: {}\nexecutable: {}",
        String::from_utf8_lossy(&output.stderr),
        executable.display(),
    );
    String::from_utf8(output.stdout)
        .expect("cold count-binary benchmark worker emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("cold count-binary benchmark worker did not emit a count")
}

fn cold_count_binary_noop() -> u64 {
    let executable = circle_prime_count_executable();
    let output = Command::new(&executable)
        .arg("--diagnostic-noop")
        .output()
        .expect("failed to spawn cold count-binary noop worker");
    assert!(
        output.status.success(),
        "cold count-binary noop worker failed: {}\nexecutable: {}",
        String::from_utf8_lossy(&output.stderr),
        executable.display(),
    );
    String::from_utf8(output.stdout)
        .expect("cold count-binary noop worker emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("cold count-binary noop worker did not emit a count")
}

fn cold_count_binary_plan_resolution(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> u64 {
    let executable = circle_prime_count_executable();
    let output = Command::new(&executable)
        .arg("--diagnostic-plan")
        .arg(low.to_string())
        .arg(high.to_string())
        .arg("--segment-size")
        .arg(segment_size.to_string())
        .arg("--threads")
        .arg(threads.to_string())
        .output()
        .expect("failed to spawn cold count-binary plan worker");
    assert!(
        output.status.success(),
        "cold count-binary plan worker failed: {}\nexecutable: {}",
        String::from_utf8_lossy(&output.stderr),
        executable.display(),
    );
    String::from_utf8(output.stdout)
        .expect("cold count-binary plan worker emitted invalid UTF-8")
        .trim()
        .parse::<u64>()
        .expect("cold count-binary plan worker did not emit a worker count")
}

fn measure_count_server_prime_count(
    name: &'static str,
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
    count_mode: Option<&str>,
    rounds: usize,
) -> BenchRow {
    let executable = circle_prime_cli_executable();
    let mut child = Command::new(&executable)
        .arg("count-server")
        .arg("--segment-size")
        .arg(segment_size.to_string())
        .arg("--threads")
        .arg(threads.to_string())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .expect("failed to spawn hot CLI count server");
    let mut stdin = child
        .stdin
        .take()
        .expect("hot CLI count server stdin unavailable");
    let stdout = child
        .stdout
        .take()
        .expect("hot CLI count server stdout unavailable");
    let mut stdout = BufReader::new(stdout);
    let request = if let Some(count_mode) = count_mode {
        format!("{low} {high} {segment_size} {threads} {count_mode}\n")
    } else {
        format!("{low} {high}\n")
    };
    let mut best_seconds = f64::INFINITY;
    let mut result = 0u64;
    let mut response = String::new();

    for _ in 0..rounds {
        response.clear();
        let start = Instant::now();
        stdin
            .write_all(request.as_bytes())
            .expect("failed to write hot CLI count-server request");
        stdin
            .flush()
            .expect("failed to flush hot CLI count-server request");
        let bytes_read = stdout
            .read_line(&mut response)
            .expect("failed to read hot CLI count-server response");
        assert!(bytes_read > 0, "hot CLI count server closed stdout");
        let elapsed = start.elapsed().as_secs_f64();
        best_seconds = best_seconds.min(elapsed);
        result = response
            .trim()
            .parse::<u64>()
            .expect("hot CLI count server did not emit a count");
    }

    drop(stdin);
    let status = child
        .wait()
        .expect("failed to wait for hot CLI count server");
    assert!(
        status.success(),
        "hot CLI count server failed with status {status}"
    );

    BenchRow {
        name,
        workload: high - low,
        segment_size,
        result,
        rounds,
        best_seconds,
    }
}

fn circle_prime_cli_executable() -> std::path::PathBuf {
    let bench_executable = env::current_exe().expect("failed to locate benchmark executable");
    let executable =
        bench_executable.with_file_name(format!("circle-prime{}", env::consts::EXE_SUFFIX));
    assert!(
        executable.exists(),
        "circle-prime CLI not found at {}; build it before running CLI cold benchmarks",
        executable.display()
    );
    executable
}

fn circle_prime_count_executable() -> std::path::PathBuf {
    let bench_executable = env::current_exe().expect("failed to locate benchmark executable");
    let executable =
        bench_executable.with_file_name(format!("circle-prime-count{}", env::consts::EXE_SUFFIX));
    assert!(
        executable.exists(),
        "circle-prime-count CLI not found at {}; build it before running count-binary cold benchmarks",
        executable.display()
    );
    executable
}

fn print_timing_row(row: &BenchRow) {
    println!(
        "timing,{},{},{},{},{},{:.3},{:.3},,",
        row.name,
        row.workload,
        row.segment_size,
        row.result,
        row.rounds,
        row.best_seconds * 1000.0,
        rate_per_second(timing_rate_workload(row), row.best_seconds)
    );
}

fn print_speedups(rows: &[BenchRow], rounds: usize) {
    for segmented in rows.iter().filter(|row| is_circle_count_row(row.name)) {
        for baseline_name in [
            "control_primal_sieve_count",
            "control_simple_sieve_count",
            "control_trial_division_count",
        ] {
            let Some(baseline) = rows.iter().find(|row| {
                row.name == baseline_name
                    && row.workload == segmented.workload
                    && row.result == segmented.result
            }) else {
                continue;
            };
            let speedup = baseline.best_seconds / segmented.best_seconds;
            println!(
                "speedup,{},{},{},{},{},{:.3},{:.3},{},{:.3}",
                segmented.name,
                segmented.workload,
                segmented.segment_size,
                segmented.result,
                rounds,
                segmented.best_seconds * 1000.0,
                rate_per_second(segmented.workload, segmented.best_seconds),
                baseline.name,
                speedup
            );
        }
    }
}

fn is_circle_count_row(name: &str) -> bool {
    name == "segmented_range_count"
        || name.starts_with("parallel_segmented_range_count_")
        || name.starts_with("parallel_balanced_segmented_range_count_")
}

fn rate_per_second(workload: u64, elapsed_seconds: f64) -> f64 {
    if elapsed_seconds == 0.0 {
        f64::INFINITY
    } else {
        workload as f64 / elapsed_seconds
    }
}

fn timing_rate_workload(row: &BenchRow) -> u64 {
    if row.name == "next_prime_search" {
        row.segment_size
    } else {
        row.workload
    }
}

fn optional_value<'a>(args: &'a [String], flag: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|window| window[0] == flag)
        .map(|window| window[1].as_str())
}

fn required_value<'a>(args: &'a [String], index: usize, message: &str) -> Result<&'a str, String> {
    args.get(index)
        .map(String::as_str)
        .ok_or_else(|| message.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bench_section_filter_defaults_to_all() {
        let sections = parse_bench_sections(None).unwrap();
        assert!(sections.is_empty());
        assert!(should_run_section(&sections, "scalar"));
        assert!(should_run_section(&sections, "next"));
        assert!(should_run_section(&sections, "high-offset"));
    }

    #[test]
    fn bench_section_filter_accepts_named_sections() {
        let sections = parse_bench_sections(Some("scalar, next, high-offset")).unwrap();
        assert!(should_run_section(&sections, "scalar"));
        assert!(should_run_section(&sections, "next"));
        assert!(should_run_section(&sections, "high-offset"));
        assert!(!should_run_section(&sections, "parallel"));
    }

    #[test]
    fn bench_section_filter_rejects_unknown_or_empty_values() {
        assert!(parse_bench_sections(Some("scalar,nope")).is_err());
        assert!(parse_bench_sections(Some(" , ")).is_err());
    }
}
