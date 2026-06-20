use std::env;
use std::io::{self, BufRead, Write};
use std::process;
use std::sync::mpsc;
use std::thread::{self, JoinHandle};

use circle_prime::{
    effective_parallel_thread_count, effective_prefix_pi_thread_count, inspect_horizon,
    is_prime_u64, next_prime_u64, prime_count_in_range, prime_count_in_range_hybrid_wheel30_marks,
    prime_count_in_range_hybrid_wheel30_marks_parallel, prime_count_in_range_parallel,
    prime_count_in_range_parallel_balanced, prime_count_in_range_parallel_dynamic,
    prime_count_in_range_prefix_pi, prime_count_in_range_prefix_pi_parallel,
    prime_count_in_range_presieve13, prime_count_in_range_presieve13_parallel,
    prime_count_in_range_presieve13_with_scratch, prime_count_in_range_presieve17,
    prime_count_in_range_presieve17_parallel, prime_count_in_range_presieve17_with_scratch,
    prime_count_in_range_wheel30_marks, prime_count_in_range_wheel30_marks_parallel,
    prime_count_in_range_with_scratch, prime_horizon_proof_contract_json,
    prime_range_count_proof_contract_json, primes_in_range, recommended_count_mode,
    recommended_count_segment_size, recommended_segment_size, PrimeCountScratch,
    BASE_PRIME_CACHE_LIMIT,
};

const MAX_INSPECT_N: u128 = 100_000;
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
                "unknown --count-mode {raw:?}; expected segmented, balanced, dynamic, prefix-pi, presieve13, presieve17, wheel30-mark, or hybrid-wheel30-mark"
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
            Self::Presieve17 => "presieve17",
            Self::Wheel30Marks => "wheel30-mark",
            Self::HybridWheel30Marks => "hybrid-wheel30-mark",
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

    fn supports_server_worker_pool(self) -> bool {
        matches!(
            self,
            Self::Segmented
                | Self::Presieve13
                | Self::Presieve17
                | Self::Wheel30Marks
                | Self::HybridWheel30Marks
        )
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
        "next-server" => next_server_command(&args[1..]),
        "range" => range_command(&args[1..]),
        "count-server" => count_server_command(&args[1..]),
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

fn next_server_command(args: &[String]) -> Result<(), String> {
    let json = args.iter().any(|arg| arg == "--json");
    let stdin = io::stdin();
    let mut reader = stdin.lock();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut buffer = Vec::with_capacity(32);
    loop {
        buffer.clear();
        let bytes_read = reader
            .read_until(b'\n', &mut buffer)
            .map_err(|err| format!("failed to read request: {err}"))?;
        if bytes_read == 0 {
            break;
        }
        let request = trim_ascii_bytes(&buffer);
        if request.is_empty() {
            continue;
        }
        if request == b"quit" || request == b"exit" {
            break;
        }
        let start = parse_u64_ascii(request)?;
        let search = next_prime_u64(start);
        if json {
            writeln!(stdout, "{}", search.to_json())
                .map_err(|err| format!("failed to write response: {err}"))?;
        } else if let Some(prime) = search.prime {
            writeln!(stdout, "{prime}")
                .map_err(|err| format!("failed to write response: {err}"))?;
        } else {
            writeln!(stdout, "none").map_err(|err| format!("failed to write response: {err}"))?;
        }
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

fn trim_ascii_bytes(mut bytes: &[u8]) -> &[u8] {
    while bytes
        .first()
        .is_some_and(|byte| matches!(byte, b' ' | b'\t' | b'\r' | b'\n'))
    {
        bytes = &bytes[1..];
    }
    while bytes
        .last()
        .is_some_and(|byte| matches!(byte, b' ' | b'\t' | b'\r' | b'\n'))
    {
        bytes = &bytes[..bytes.len() - 1];
    }
    bytes
}

fn parse_u64_ascii(bytes: &[u8]) -> Result<u64, String> {
    if bytes.is_empty() {
        return Err("next-server request must be START fitting in u64".to_string());
    }
    let mut value = 0u64;
    for &byte in bytes {
        if !byte.is_ascii_digit() {
            return Err("next-server request must be START fitting in u64".to_string());
        }
        value = value
            .checked_mul(10)
            .and_then(|value| value.checked_add(u64::from(byte - b'0')))
            .ok_or_else(|| "next-server request must be START fitting in u64".to_string())?;
    }
    Ok(value)
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
        count_mode.effective_threads(
            low,
            high,
            effective_parallel_thread_count(low, high, segment_size, threads),
            threads,
        )
    } else {
        threads
    };

    if json {
        if count_only {
            println!(
                "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"count_mode\":\"{}\",\"proof_contract\":{},\"count_proof_contract\":{}}}",
                low,
                high,
                count_only,
                segment_size,
                worker_threads,
                threads,
                count_mode.as_str(),
                prime_horizon_proof_contract_json(),
                prime_range_count_proof_contract_json()
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
        count_mode.effective_threads(
            low,
            high,
            effective_parallel_thread_count(low, high, segment_size, threads),
            threads,
        )
    } else {
        threads
    };

    if count_only {
        let count = count_range_with_mode(low, high, segment_size, worker_threads, count_mode)
            .map_err(|err| format!("range sieve failed: {err:?}"))?;
        if json {
            println!(
                "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"count_mode\":\"{}\",\"proof_contract\":{},\"count_proof_contract\":{}}}",
                low,
                high,
                count,
                segment_size,
                worker_threads,
                threads,
                count_mode.as_str(),
                prime_horizon_proof_contract_json(),
                prime_range_count_proof_contract_json()
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

fn count_server_command(args: &[String]) -> Result<(), String> {
    let default_segment_size = optional_value(args, "--segment-size")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--segment-size must fit in u64".to_string())
        })
        .transpose()?;
    let default_threads = optional_value(args, "--threads")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--threads must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(1);
    if default_threads == 0 {
        return Err("--threads must be greater than zero".to_string());
    }
    let default_count_mode = optional_value(args, "--count-mode")
        .map(CountMode::parse)
        .transpose()?;
    let json = args.iter().any(|arg| arg == "--json");

    let stdin = io::stdin();
    let mut reader = stdin.lock();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut buffer = Vec::with_capacity(96);
    let mut worker_pool = CountServerWorkerPool::new();
    let mut plan_cache = None;
    loop {
        buffer.clear();
        let bytes_read = reader
            .read_until(b'\n', &mut buffer)
            .map_err(|err| format!("failed to read request: {err}"))?;
        if bytes_read == 0 {
            break;
        }
        let request_bytes = trim_ascii_bytes(&buffer);
        let request = std::str::from_utf8(request_bytes)
            .map_err(|_| "count-server request must be valid UTF-8".to_string())?;
        if request.is_empty() {
            continue;
        }
        if request == "quit" || request == "exit" {
            break;
        }
        let response = count_server_response_with_pool(
            request,
            default_segment_size,
            default_threads,
            default_count_mode,
            Some(&mut worker_pool),
            Some(&mut plan_cache),
        )?;
        if json {
            writeln!(stdout, "{}", response.to_json())
                .map_err(|err| format!("failed to write response: {err}"))?;
        } else {
            writeln!(stdout, "{}", response.count)
                .map_err(|err| format!("failed to write response: {err}"))?;
        }
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

#[cfg(test)]
fn count_server_request(
    request: &str,
    default_segment_size: Option<u64>,
    default_threads: usize,
    default_count_mode: Option<CountMode>,
) -> Result<usize, String> {
    Ok(count_server_response(
        request,
        default_segment_size,
        default_threads,
        default_count_mode,
    )?
    .count)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct CountServerResponse {
    low: u64,
    high: u64,
    count: usize,
    segment_size: u64,
    threads: usize,
    requested_threads: usize,
    count_mode: CountMode,
}

impl CountServerResponse {
    fn to_json(self) -> String {
        format!(
            "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"count_mode\":\"{}\",\"proof_contract\":{},\"count_proof_contract\":{}}}",
            self.low,
            self.high,
            self.count,
            self.segment_size,
            self.threads,
            self.requested_threads,
            self.count_mode.as_str(),
            prime_horizon_proof_contract_json(),
            prime_range_count_proof_contract_json()
        )
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct CountServerPlan {
    segment_size: u64,
    worker_threads: usize,
    count_mode: CountMode,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct CountServerPlanCache {
    low: u64,
    high: u64,
    requested_threads: usize,
    default_segment_size: Option<u64>,
    default_count_mode: Option<CountMode>,
    plan: CountServerPlan,
}

impl CountServerPlanCache {
    fn matches(
        self,
        low: u64,
        high: u64,
        requested_threads: usize,
        default_segment_size: Option<u64>,
        default_count_mode: Option<CountMode>,
    ) -> bool {
        self.low == low
            && self.high == high
            && self.requested_threads == requested_threads
            && self.default_segment_size == default_segment_size
            && self.default_count_mode == default_count_mode
    }
}

#[cfg(test)]
fn count_server_response(
    request: &str,
    default_segment_size: Option<u64>,
    default_threads: usize,
    default_count_mode: Option<CountMode>,
) -> Result<CountServerResponse, String> {
    count_server_response_with_pool(
        request,
        default_segment_size,
        default_threads,
        default_count_mode,
        None,
        None,
    )
}

fn count_server_response_with_pool(
    request: &str,
    default_segment_size: Option<u64>,
    default_threads: usize,
    default_count_mode: Option<CountMode>,
    mut worker_pool: Option<&mut CountServerWorkerPool>,
    mut plan_cache: Option<&mut Option<CountServerPlanCache>>,
) -> Result<CountServerResponse, String> {
    let mut fields = request.split_whitespace();
    let Some(low_field) = fields.next() else {
        return Err(
            "count-server request must be LOW HIGH [SEGMENT_SIZE] [THREADS] [COUNT_MODE]"
                .to_string(),
        );
    };
    let Some(high_field) = fields.next() else {
        return Err(
            "count-server request must be LOW HIGH [SEGMENT_SIZE] [THREADS] [COUNT_MODE]"
                .to_string(),
        );
    };
    let segment_size_field = fields.next();
    let threads_field = fields.next();
    let count_mode_field = fields.next();
    if fields.next().is_some() {
        return Err(
            "count-server request must be LOW HIGH [SEGMENT_SIZE] [THREADS] [COUNT_MODE]"
                .to_string(),
        );
    }
    let low = low_field
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = high_field
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let requested_threads = threads_field
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "THREADS must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(default_threads);
    if requested_threads == 0 {
        return Err("THREADS must be greater than zero".to_string());
    }
    let explicit_segment_size = segment_size_field
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "SEGMENT_SIZE must fit in u64".to_string())
        })
        .transpose()?;
    let explicit_count_mode = count_mode_field
        .map(|value| CountMode::parse(value))
        .transpose()?;
    let plan = if explicit_segment_size.is_none() && explicit_count_mode.is_none() {
        count_server_cached_plan(
            low,
            high,
            requested_threads,
            default_segment_size,
            default_count_mode,
            plan_cache.as_deref_mut(),
        )
    } else {
        resolve_count_server_plan(
            low,
            high,
            requested_threads,
            explicit_segment_size,
            default_segment_size,
            explicit_count_mode,
            default_count_mode,
        )
    };
    let count = if let Some(pool) = worker_pool.as_mut() {
        match count_range_with_server_pool(
            pool,
            low,
            high,
            plan.segment_size,
            plan.worker_threads,
            plan.count_mode,
        )
        .map_err(|err| format!("range sieve failed: {err:?}"))?
        {
            Some(count) => count,
            None => count_range_with_mode(
                low,
                high,
                plan.segment_size,
                plan.worker_threads,
                plan.count_mode,
            )
            .map_err(|err| format!("range sieve failed: {err:?}"))?,
        }
    } else {
        count_range_with_mode(
            low,
            high,
            plan.segment_size,
            plan.worker_threads,
            plan.count_mode,
        )
        .map_err(|err| format!("range sieve failed: {err:?}"))?
    };
    Ok(CountServerResponse {
        low,
        high,
        count,
        segment_size: plan.segment_size,
        threads: plan.worker_threads,
        requested_threads,
        count_mode: plan.count_mode,
    })
}

fn count_server_cached_plan(
    low: u64,
    high: u64,
    requested_threads: usize,
    default_segment_size: Option<u64>,
    default_count_mode: Option<CountMode>,
    plan_cache: Option<&mut Option<CountServerPlanCache>>,
) -> CountServerPlan {
    if let Some(cache_slot) = plan_cache {
        if let Some(cache) = *cache_slot {
            if cache.matches(
                low,
                high,
                requested_threads,
                default_segment_size,
                default_count_mode,
            ) {
                return cache.plan;
            }
        }
        let plan = resolve_count_server_plan(
            low,
            high,
            requested_threads,
            None,
            default_segment_size,
            None,
            default_count_mode,
        );
        *cache_slot = Some(CountServerPlanCache {
            low,
            high,
            requested_threads,
            default_segment_size,
            default_count_mode,
            plan,
        });
        return plan;
    }

    resolve_count_server_plan(
        low,
        high,
        requested_threads,
        None,
        default_segment_size,
        None,
        default_count_mode,
    )
}

fn resolve_count_server_plan(
    low: u64,
    high: u64,
    requested_threads: usize,
    explicit_segment_size: Option<u64>,
    default_segment_size: Option<u64>,
    explicit_count_mode: Option<CountMode>,
    default_count_mode: Option<CountMode>,
) -> CountServerPlan {
    let segment_size = explicit_segment_size
        .or(default_segment_size)
        .unwrap_or_else(|| recommended_count_segment_size(low, high, requested_threads));
    let count_mode = explicit_count_mode
        .or(default_count_mode)
        .unwrap_or_else(|| {
            CountMode::parse(recommended_count_mode(low, high, requested_threads))
                .expect("compiled count-mode default must be valid")
        });
    let worker_threads = count_mode.effective_threads(
        low,
        high,
        effective_parallel_thread_count(low, high, segment_size, requested_threads),
        requested_threads,
    );
    CountServerPlan {
        segment_size,
        worker_threads,
        count_mode,
    }
}

struct CountServerWorkerPool {
    senders: Vec<mpsc::Sender<CountServerWorkerCommand>>,
    handles: Vec<JoinHandle<()>>,
    result_sender: mpsc::Sender<Result<usize, circle_prime::RangeError>>,
    result_receiver: mpsc::Receiver<Result<usize, circle_prime::RangeError>>,
}

impl CountServerWorkerPool {
    fn new() -> Self {
        let (result_sender, result_receiver) = mpsc::channel();
        Self {
            senders: Vec::new(),
            handles: Vec::new(),
            result_sender,
            result_receiver,
        }
    }

    fn count_chunks(
        &mut self,
        chunks: &[(u64, u64)],
        segment_size: u64,
        count_mode: CountMode,
    ) -> Result<usize, circle_prime::RangeError> {
        self.ensure_worker_count(chunks.len());
        for (worker_index, &(low, high)) in chunks.iter().enumerate() {
            self.senders[worker_index]
                .send(CountServerWorkerCommand::Count {
                    low,
                    high,
                    segment_size,
                    count_mode,
                })
                .map_err(|_| circle_prime::RangeError::WorkerPanic)?;
        }

        let mut total = 0usize;
        for _ in chunks {
            total += self
                .result_receiver
                .recv()
                .map_err(|_| circle_prime::RangeError::WorkerPanic)??;
        }
        Ok(total)
    }

    fn ensure_worker_count(&mut self, worker_count: usize) {
        while self.senders.len() < worker_count {
            let (sender, receiver) = mpsc::channel();
            let result_sender = self.result_sender.clone();
            let handle = thread::spawn(move || count_server_worker_loop(receiver, result_sender));
            self.senders.push(sender);
            self.handles.push(handle);
        }
    }
}

impl Drop for CountServerWorkerPool {
    fn drop(&mut self) {
        for sender in &self.senders {
            let _ = sender.send(CountServerWorkerCommand::Stop);
        }
        while let Some(handle) = self.handles.pop() {
            let _ = handle.join();
        }
    }
}

enum CountServerWorkerCommand {
    Count {
        low: u64,
        high: u64,
        segment_size: u64,
        count_mode: CountMode,
    },
    Stop,
}

fn count_server_worker_loop(
    receiver: mpsc::Receiver<CountServerWorkerCommand>,
    result_sender: mpsc::Sender<Result<usize, circle_prime::RangeError>>,
) {
    let mut scratch = PrimeCountScratch::new();
    while let Ok(command) = receiver.recv() {
        match command {
            CountServerWorkerCommand::Count {
                low,
                high,
                segment_size,
                count_mode,
            } => {
                let result = count_range_with_mode_scratch(
                    low,
                    high,
                    segment_size,
                    1,
                    count_mode,
                    &mut scratch,
                );
                let _ = result_sender.send(result);
            }
            CountServerWorkerCommand::Stop => break,
        }
    }
}

fn count_range_with_server_pool(
    pool: &mut CountServerWorkerPool,
    low: u64,
    high: u64,
    segment_size: u64,
    worker_threads: usize,
    mode: CountMode,
) -> Result<Option<usize>, circle_prime::RangeError> {
    if worker_threads <= 1
        || high <= low
        || segment_size == 0
        || (high - 1).isqrt() > BASE_PRIME_CACHE_LIMIT
        || !mode.supports_server_worker_pool()
    {
        return Ok(None);
    }

    let chunks = split_range_evenly(low, high, worker_threads);
    if chunks.len() <= 1 {
        return Ok(None);
    }
    pool.count_chunks(&chunks, segment_size, mode).map(Some)
}

fn split_range_evenly(low: u64, high: u64, parts: usize) -> Vec<(u64, u64)> {
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

fn count_range_with_mode_scratch(
    low: u64,
    high: u64,
    segment_size: u64,
    worker_threads: usize,
    mode: CountMode,
    scratch: &mut PrimeCountScratch,
) -> Result<usize, circle_prime::RangeError> {
    match mode {
        CountMode::Segmented if worker_threads == 1 => {
            prime_count_in_range_with_scratch(low, high, segment_size, scratch)
        }
        CountMode::Presieve13 if worker_threads == 1 => {
            prime_count_in_range_presieve13_with_scratch(low, high, segment_size, scratch)
        }
        CountMode::Presieve17 if worker_threads == 1 => {
            prime_count_in_range_presieve17_with_scratch(low, high, segment_size, scratch)
        }
        _ => count_range_with_mode(low, high, segment_size, worker_threads, mode),
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
        "  circle-prime next-server [--json]",
        "  circle-prime recommend LOW HIGH [--count] [--json] [--threads N]",
        "  circle-prime range LOW HIGH [--count] [--json] [--segment-size N] [--threads N] [--count-mode MODE]",
        "  circle-prime count-server [--segment-size N] [--threads N] [--count-mode MODE] [--json]",
        "",
        "next-server reads START lines from stdin and writes one next prime, none, or JSON object per line.",
        "count-server reads LOW HIGH [SEGMENT_SIZE] [THREADS] [COUNT_MODE] lines from stdin and writes one count or JSON object per line.",
        "count modes: segmented, balanced, dynamic, prefix-pi, presieve13, presieve17, wheel30-mark, hybrid-wheel30-mark",
    ]
    .join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn count_server_request_counts_reference_range() {
        assert_eq!(
            count_server_request("0 1000", None, 1, Some(CountMode::Segmented)).unwrap(),
            168
        );
    }

    #[test]
    fn count_server_request_accepts_per_line_overrides() {
        assert_eq!(
            count_server_request("0 100000 65536 4 presieve13", None, 1, None).unwrap(),
            9592
        );
    }

    #[test]
    fn count_server_request_trims_and_rejects_extra_fields() {
        assert_eq!(
            count_server_request(" \t0 1000\r\n", None, 1, Some(CountMode::Segmented)).unwrap(),
            168
        );
        assert!(count_server_request("0", None, 1, None).is_err());
        assert!(count_server_request("0 1000 64 1 segmented extra", None, 1, None).is_err());
    }

    #[test]
    fn count_server_worker_pool_matches_direct_parallel_count() {
        let mut pool = CountServerWorkerPool::new();
        let request = "0 1000000 65536 4 presieve13";
        let pooled = count_server_response_with_pool(request, None, 1, None, Some(&mut pool), None)
            .expect("pooled count-server request should succeed");
        let direct = count_server_response(request, None, 1, None)
            .expect("direct count-server request should succeed");

        assert_eq!(pooled.count, direct.count);
        assert_eq!(pooled.segment_size, direct.segment_size);
        assert_eq!(pooled.threads, direct.threads);
        assert_eq!(pooled.count_mode, direct.count_mode);
    }

    #[test]
    fn count_server_caches_repeated_adaptive_default_plan() {
        let mut pool = CountServerWorkerPool::new();
        let mut plan_cache = None;
        let request = "1000000000000 1000010000000";
        let first = count_server_response_with_pool(
            request,
            None,
            8,
            None,
            Some(&mut pool),
            Some(&mut plan_cache),
        )
        .expect("first adaptive request should succeed");
        let cached_plan = plan_cache.expect("adaptive request should populate plan cache");
        let second = count_server_response_with_pool(
            request,
            None,
            8,
            None,
            Some(&mut pool),
            Some(&mut plan_cache),
        )
        .expect("second adaptive request should succeed");

        assert_eq!(first.count, second.count);
        assert_eq!(first.segment_size, second.segment_size);
        assert_eq!(first.threads, second.threads);
        assert_eq!(first.count_mode, second.count_mode);
        assert_eq!(Some(cached_plan), plan_cache);
        assert_eq!(first.segment_size, cached_plan.plan.segment_size);
        assert_eq!(first.count_mode, cached_plan.plan.count_mode);
    }

    #[test]
    fn count_server_worker_pool_accepts_generated_base_prime_limit() {
        let mut pool = CountServerWorkerPool::new();
        let request = "1500000000000 1500001000000 1507328 4 presieve13";
        let pooled_count = count_range_with_server_pool(
            &mut pool,
            1_500_000_000_000,
            1_500_001_000_000,
            1_507_328,
            4,
            CountMode::Presieve13,
        )
        .expect("pooled count should succeed")
        .expect("range should use the widened worker pool path");
        let direct = count_server_response(request, None, 1, None)
            .expect("direct count-server request should succeed");

        assert_eq!(pooled_count, direct.count);
    }

    #[test]
    fn count_server_worker_pool_reuses_result_channel_across_requests() {
        let mut pool = CountServerWorkerPool::new();
        let requests = [
            (1_000_000_000_000, 1_000_001_000_000, 1_507_328, 4),
            (1_500_000_000_000, 1_500_001_000_000, 1_507_328, 4),
            (1_000_000_000_000, 1_000_001_000_000, 1_310_720, 4),
        ];

        for &(low, high, segment_size, threads) in &requests {
            let pooled_count = count_range_with_server_pool(
                &mut pool,
                low,
                high,
                segment_size,
                threads,
                CountMode::Presieve13,
            )
            .expect("pooled count should succeed")
            .expect("range should use the worker pool");
            let direct_count =
                count_range_with_mode(low, high, segment_size, threads, CountMode::Presieve13)
                    .expect("direct parallel count should succeed");

            assert_eq!(pooled_count, direct_count);
        }
    }

    #[test]
    fn next_server_ascii_parser_trims_and_rejects_invalid_requests() {
        assert_eq!(trim_ascii_bytes(b" \t90\r\n"), b"90");
        assert_eq!(parse_u64_ascii(trim_ascii_bytes(b" \t90\r\n")).unwrap(), 90);
        assert_eq!(parse_u64_ascii(b"18446744073709551615").unwrap(), u64::MAX);
        assert!(parse_u64_ascii(b"").is_err());
        assert!(parse_u64_ascii(b"12x").is_err());
        assert!(parse_u64_ascii(b"18446744073709551616").is_err());
    }
}
