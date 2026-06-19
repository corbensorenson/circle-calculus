use std::env;
use std::process;

use circle_prime::{
    effective_parallel_thread_count, inspect_horizon, is_prime_u64, next_prime_u64,
    prime_count_in_range, prime_count_in_range_hybrid_wheel30_marks,
    prime_count_in_range_hybrid_wheel30_marks_parallel, prime_count_in_range_parallel,
    prime_count_in_range_parallel_balanced, prime_count_in_range_parallel_dynamic,
    prime_count_in_range_prefix_pi, prime_count_in_range_presieve13,
    prime_count_in_range_wheel30_marks, prime_count_in_range_wheel30_marks_parallel,
    prime_horizon_proof_contract_json, primes_in_range, recommended_count_mode,
    recommended_count_segment_size, recommended_segment_size,
};

const MAX_INSPECT_N: u128 = 100_000;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CountMode {
    Segmented,
    Balanced,
    Dynamic,
    PrefixPi,
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
            "prefix-pi" | "pi" => Ok(Self::PrefixPi),
            "presieve13" => Ok(Self::Presieve13),
            "wheel30-mark" | "wheel30-marks" => Ok(Self::Wheel30Marks),
            "hybrid-wheel30-mark" | "hybrid-wheel30-marks" => Ok(Self::HybridWheel30Marks),
            _ => Err(format!(
                "unknown --count-mode {raw:?}; expected segmented, balanced, dynamic, prefix-pi, presieve13, wheel30-mark, or hybrid-wheel30-mark"
            )),
        }
    }

    fn as_str(self) -> &'static str {
        match self {
            Self::Segmented => "segmented",
            Self::Balanced => "balanced",
            Self::Dynamic => "dynamic",
            Self::PrefixPi => "prefix-pi",
            Self::Presieve13 => "presieve13",
            Self::Wheel30Marks => "wheel30-mark",
            Self::HybridWheel30Marks => "hybrid-wheel30-mark",
        }
    }

    fn effective_threads(self, general_effective_threads: usize) -> usize {
        match self {
            Self::PrefixPi | Self::Presieve13 => 1,
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
    let Some(command) = args.first().map(String::as_str) else {
        return Err(usage());
    };

    match command {
        "inspect" => inspect_command(&args[1..]),
        "test" => test_command(&args[1..]),
        "next" => next_command(&args[1..]),
        "range" => range_command(&args[1..]),
        "recommend" => recommend_command(&args[1..]),
        "help" | "--help" | "-h" => {
            println!("{}", usage());
            Ok(())
        }
        _ => Err(usage()),
    }
}

fn next_command(args: &[String]) -> Result<(), String> {
    let start = required_arg(args, 0, "next requires N")?
        .parse::<u64>()
        .map_err(|_| "next N must fit in the documented u64 domain".to_string())?;
    let json = args.iter().any(|arg| arg == "--json");
    let search = next_prime_u64(start);
    if json {
        println!("{}", search.to_json());
    } else if let Some(prime) = search.prime {
        println!("{prime}");
    } else {
        println!("none");
    }
    Ok(())
}

fn inspect_command(args: &[String]) -> Result<(), String> {
    let n = required_arg(args, 0, "inspect requires N")?
        .parse::<u128>()
        .map_err(|_| {
            "inspect N must be an integer that fits in the Rust u128 domain".to_string()
        })?;
    let json = args.iter().any(|arg| arg == "--json");
    if n > MAX_INSPECT_N {
        return Err(format!(
            "inspect enumerates the half-spectrum; refusing n > {MAX_INSPECT_N}"
        ));
    }

    let inspection = inspect_horizon(n)?;
    if json {
        println!(
            "{{\"n\":{},\"unique_skip_count\":{},\"full_length_count\":{},\"fractured_count\":{},\"contained_primitive_horizons\":[{}],\"proof_contract\":{}}}",
            inspection.n,
            inspection.unique_skip_count,
            inspection.full_length_count,
            inspection.fractured_count,
            join_u128(&inspection.contained_primitive_horizons),
            prime_horizon_proof_contract_json()
        );
    } else {
        println!("n = {}", inspection.n);
        println!("base_angle_turns = 1/{}", inspection.n);
        println!("unique_skip_count = {}", inspection.unique_skip_count);
        println!("full_length_count = {}", inspection.full_length_count);
        println!("fractured_count = {}", inspection.fractured_count);
        println!(
            "contained_primitive_horizons = {}",
            if inspection.contained_primitive_horizons.is_empty() {
                "(none)".to_string()
            } else {
                join_u128(&inspection.contained_primitive_horizons)
            }
        );
    }
    Ok(())
}

fn test_command(args: &[String]) -> Result<(), String> {
    let n = required_arg(args, 0, "test requires N")?
        .parse::<u64>()
        .map_err(|_| "test N must fit in the documented u64 domain".to_string())?;
    let json = args.iter().any(|arg| arg == "--json");
    let decision = is_prime_u64(n);
    if json {
        println!("{}", decision.to_json());
    } else {
        println!("n = {}", decision.n);
        println!("status = {:?}", decision.status);
        println!("method = {}", decision.method);
        println!("stage = {}", decision.stage);
        if let Some(factor) = decision.factor {
            println!("factor = {factor}");
        }
        if let Some(base) = decision.witness_base {
            println!("witness_base = {base}");
        }
    }
    Ok(())
}

fn recommend_command(args: &[String]) -> Result<(), String> {
    let low = required_arg(args, 0, "recommend requires LOW HIGH")?
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = required_arg(args, 1, "recommend requires LOW HIGH")?
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let count_only = args.iter().any(|arg| arg == "--count");
    let json = args.iter().any(|arg| arg == "--json");
    let threads = optional_value(args, "--threads")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--threads must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(1);
    if threads == 0 {
        return Err("--threads must be greater than zero".to_string());
    }
    if !count_only && threads != 1 {
        return Err("--threads is currently supported only with --count".to_string());
    }

    let segment_size = if count_only {
        recommended_count_segment_size(low, high, threads)
    } else {
        recommended_segment_size(low, high)
    };
    let count_mode = if count_only {
        CountMode::parse(recommended_count_mode(low, high, threads))?
    } else {
        CountMode::Segmented
    };
    let worker_threads = if count_only {
        count_mode.effective_threads(effective_parallel_thread_count(
            low,
            high,
            segment_size,
            threads,
        ))
    } else {
        threads
    };

    if json {
        if count_only {
            println!(
                "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"count_mode\":\"{}\",\"proof_contract\":{}}}",
                low,
                high,
                count_only,
                segment_size,
                worker_threads,
                threads,
                count_mode.as_str(),
                prime_horizon_proof_contract_json()
            );
        } else {
            println!(
                "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"proof_contract\":{}}}",
                low,
                high,
                count_only,
                segment_size,
                worker_threads,
                threads,
                prime_horizon_proof_contract_json()
            );
        }
    } else {
        println!("segment_size = {segment_size}");
        println!("threads = {worker_threads}");
        println!("requested_threads = {threads}");
        println!("count = {count_only}");
        if count_only {
            println!("count_mode = {}", count_mode.as_str());
        }
    }
    Ok(())
}

fn range_command(args: &[String]) -> Result<(), String> {
    let low = required_arg(args, 0, "range requires LOW HIGH")?
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = required_arg(args, 1, "range requires LOW HIGH")?
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let count_only = args.iter().any(|arg| arg == "--count");
    let json = args.iter().any(|arg| arg == "--json");
    let segment_size_override = optional_value(args, "--segment-size")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--segment-size must fit in u64".to_string())
        })
        .transpose()?;
    let threads = optional_value(args, "--threads")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--threads must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(1);
    if threads == 0 {
        return Err("--threads must be greater than zero".to_string());
    }
    let count_mode_override = optional_value(args, "--count-mode")
        .map(CountMode::parse)
        .transpose()?;
    let count_mode = count_mode_override.unwrap_or_else(|| {
        if count_only {
            CountMode::parse(recommended_count_mode(low, high, threads))
                .expect("compiled count-mode default must be valid")
        } else {
            CountMode::Segmented
        }
    });
    if !count_only && count_mode != CountMode::Segmented {
        return Err("--count-mode is currently supported only with --count".to_string());
    }
    let segment_size = segment_size_override.unwrap_or_else(|| {
        if count_only {
            recommended_count_segment_size(low, high, threads)
        } else {
            recommended_segment_size(low, high)
        }
    });
    let worker_threads = if count_only {
        count_mode.effective_threads(effective_parallel_thread_count(
            low,
            high,
            segment_size,
            threads,
        ))
    } else {
        threads
    };

    if count_only {
        let count = count_range_with_mode(low, high, segment_size, worker_threads, count_mode)
            .map_err(|err| format!("range sieve failed: {err:?}"))?;
        if json {
            println!(
                "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"count_mode\":\"{}\",\"proof_contract\":{}}}",
                low,
                high,
                count,
                segment_size,
                worker_threads,
                threads,
                count_mode.as_str(),
                prime_horizon_proof_contract_json()
            );
        } else {
            println!("{count}");
        }
        return Ok(());
    }

    if threads != 1 {
        return Err("--threads is currently supported only with --count".to_string());
    }

    let primes = primes_in_range(low, high, segment_size)
        .map_err(|err| format!("range sieve failed: {err:?}"))?;
    if json {
        if count_only {
            println!(
                "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"proof_contract\":{}}}",
                low,
                high,
                primes.len(),
                segment_size,
                worker_threads,
                threads,
                prime_horizon_proof_contract_json()
            );
        } else {
            println!(
                "{{\"low\":{},\"high\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"primes\":[{}],\"proof_contract\":{}}}",
                low,
                high,
                segment_size,
                worker_threads,
                threads,
                join_u64(&primes),
                prime_horizon_proof_contract_json()
            );
        }
    } else {
        for prime in primes {
            println!("{prime}");
        }
    }
    Ok(())
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
        CountMode::PrefixPi => prime_count_in_range_prefix_pi(low, high),
        CountMode::Presieve13 => prime_count_in_range_presieve13(low, high, segment_size),
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

fn required_arg<'a>(args: &'a [String], index: usize, message: &str) -> Result<&'a str, String> {
    args.get(index)
        .map(String::as_str)
        .filter(|arg| !arg.starts_with("--"))
        .ok_or_else(|| message.to_string())
}

fn optional_value<'a>(args: &'a [String], flag: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|window| window[0] == flag)
        .map(|window| window[1].as_str())
}

fn join_u64(values: &[u64]) -> String {
    values
        .iter()
        .map(u64::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn join_u128(values: &[u128]) -> String {
    values
        .iter()
        .map(u128::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn usage() -> String {
    [
        "usage:",
        "  circle-prime inspect N [--json]",
        "  circle-prime test N [--json]",
        "  circle-prime next N [--json]",
        "  circle-prime recommend LOW HIGH [--count] [--json] [--threads N]",
        "  circle-prime range LOW HIGH [--count] [--json] [--segment-size N] [--threads N] [--count-mode MODE]",
        "",
        "count modes: segmented, balanced, dynamic, prefix-pi, presieve13, wheel30-mark, hybrid-wheel30-mark",
    ]
    .join("\n")
}
