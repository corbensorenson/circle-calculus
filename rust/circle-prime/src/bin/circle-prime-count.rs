use std::env;
use std::fs;
use std::io::{self, BufRead, Write};
#[cfg(unix)]
use std::os::unix::net::{UnixListener, UnixStream};
use std::process;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::mpsc;
use std::thread::{self, JoinHandle};

use circle_prime::{
    diagnostic_scoped_parallel_worker_spawn, effective_parallel_thread_count,
    prime_count_adjacent_shifted_presieve13_with_scratch,
    prime_count_adjacent_shifted_presieve17_with_scratch, prime_count_in_range,
    prime_count_in_range_parallel, prime_count_in_range_parallel_balanced,
    prime_count_in_range_parallel_dynamic, prime_count_in_range_presieve13,
    prime_count_in_range_presieve13_parallel, prime_count_in_range_presieve13_with_scratch,
    prime_count_in_range_presieve17, prime_count_in_range_presieve17_parallel,
    prime_count_in_range_presieve17_with_scratch, prime_count_in_range_with_scratch,
    prime_count_shifted_single_segment_presieve13_with_scratch,
    prime_count_shifted_single_segment_presieve17_with_scratch,
    prime_range_count_proof_contract_json, recommended_count_mode, recommended_count_segment_size,
    PrimeCountScratch, BASE_PRIME_CACHE_LIMIT, PARALLEL_EDGE_HIGH_OFFSET_MIN_BASE_LIMIT,
    PARALLEL_LOWER_HIGH_OFFSET_BASE_LIMIT, PARALLEL_LOWER_HIGH_OFFSET_MIN_BASE_LIMIT,
};

const SHIFTED_EDGE_HIGH_OFFSET_SEGMENT_SIZE: u64 = 1_310_720;
const SHIFTED_LOWER_HIGH_OFFSET_SEGMENT_SIZE: u64 = 1_835_008;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CountMode {
    Segmented,
    Balanced,
    Dynamic,
    Presieve13,
    Presieve17,
}

impl CountMode {
    fn parse(raw: &str) -> Result<Self, String> {
        match raw {
            "segmented" => Ok(Self::Segmented),
            "balanced" => Ok(Self::Balanced),
            "dynamic" => Ok(Self::Dynamic),
            "presieve13" => Ok(Self::Presieve13),
            "presieve17" => Ok(Self::Presieve17),
            _ => Err(format!(
                "unknown --count-mode {raw:?}; circle-prime-count supports default, segmented, balanced, dynamic, presieve13, and presieve17"
            )),
        }
    }

    fn as_str(self) -> &'static str {
        match self {
            Self::Segmented => "segmented",
            Self::Balanced => "balanced",
            Self::Dynamic => "dynamic",
            Self::Presieve13 => "presieve13",
            Self::Presieve17 => "presieve17",
        }
    }

    fn supports_worker_pool(self) -> bool {
        matches!(self, Self::Segmented | Self::Presieve13 | Self::Presieve17)
    }
}

fn main() {
    if let Err(message) = run_args(env::args().skip(1)) {
        eprintln!("{message}");
        process::exit(2);
    }
}

fn run_args(mut args: impl Iterator<Item = String>) -> Result<(), String> {
    let Some(first) = args.next() else {
        return Err("circle-prime-count requires LOW HIGH".to_string());
    };
    if first == "--diagnostic-noop" {
        println!("0");
        return Ok(());
    }
    if first == "--diagnostic-plan" {
        return diagnostic_plan_command(args);
    }
    if first == "--diagnostic-spawn" {
        return diagnostic_spawn_command(args);
    }
    if matches!(first.as_str(), "--help" | "-h") {
        println!("{}", usage());
        return Ok(());
    }
    if matches!(first.as_str(), "count-server" | "server") {
        let server_args = args.collect::<Vec<_>>();
        if server_args
            .iter()
            .any(|arg| matches!(arg.as_str(), "--help" | "-h"))
        {
            println!("{}", usage());
            return Ok(());
        }
        return count_server_command(&server_args);
    }
    if matches!(first.as_str(), "socket-server" | "daemon-server") {
        let server_args = args.collect::<Vec<_>>();
        return socket_server_command(&server_args);
    }
    if matches!(first.as_str(), "socket-client" | "daemon-client") {
        let client_args = args.collect::<Vec<_>>();
        return socket_client_command(&client_args);
    }

    let low = first
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = args
        .next()
        .filter(|arg| !arg.starts_with("--"))
        .ok_or_else(|| "circle-prime-count requires LOW HIGH".to_string())?
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let mut json = false;
    let mut requested_threads = 1usize;
    let mut explicit_segment_size = None;
    let mut explicit_mode = None;
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--help" | "-h" => {
                println!("{}", usage());
                return Ok(());
            }
            "--json" => json = true,
            "--threads" => {
                let Some(value) = args.next() else {
                    continue;
                };
                requested_threads = value
                    .parse::<usize>()
                    .map_err(|_| "--threads must fit in usize".to_string())?;
            }
            "--segment-size" => {
                let Some(value) = args.next() else {
                    continue;
                };
                explicit_segment_size = Some(
                    value
                        .parse::<u64>()
                        .map_err(|_| "--segment-size must fit in u64".to_string())?,
                );
            }
            "--count-mode" => {
                let Some(value) = args.next() else {
                    continue;
                };
                explicit_mode = parse_count_mode_override(&value)?;
            }
            _ => {}
        }
    }
    if requested_threads == 0 {
        return Err("--threads must be greater than zero".to_string());
    }

    let plan = resolve_count_plan(
        low,
        high,
        explicit_segment_size,
        requested_threads,
        explicit_mode,
    );
    let count = count_range_with_mode(
        plan.low,
        plan.high,
        plan.segment_size,
        plan.threads,
        plan.mode,
    )
    .map_err(|err| format!("range sieve failed: {err:?}"))?;

    if json {
        println!("{}", count_json(&plan, count));
    } else {
        println!("{count}");
    }
    Ok(())
}

fn diagnostic_plan_command(mut args: impl Iterator<Item = String>) -> Result<(), String> {
    let Some(first) = args.next() else {
        return Err("--diagnostic-plan requires LOW HIGH".to_string());
    };
    let low = first
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = args
        .next()
        .filter(|arg| !arg.starts_with("--"))
        .ok_or_else(|| "--diagnostic-plan requires LOW HIGH".to_string())?
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let mut requested_threads = 1usize;
    let mut explicit_segment_size = None;
    let mut explicit_mode = None;
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--threads" => {
                let Some(value) = args.next() else {
                    continue;
                };
                requested_threads = value
                    .parse::<usize>()
                    .map_err(|_| "--threads must fit in usize".to_string())?;
            }
            "--segment-size" => {
                let Some(value) = args.next() else {
                    continue;
                };
                explicit_segment_size = Some(
                    value
                        .parse::<u64>()
                        .map_err(|_| "--segment-size must fit in u64".to_string())?,
                );
            }
            "--count-mode" => {
                let Some(value) = args.next() else {
                    continue;
                };
                explicit_mode = parse_count_mode_override(&value)?;
            }
            _ => {}
        }
    }
    if requested_threads == 0 {
        return Err("--threads must be greater than zero".to_string());
    }
    let plan = resolve_count_plan(
        low,
        high,
        explicit_segment_size,
        requested_threads,
        explicit_mode,
    );
    println!("{}", plan.threads);
    Ok(())
}

fn diagnostic_spawn_command(mut args: impl Iterator<Item = String>) -> Result<(), String> {
    let Some(first) = args.next() else {
        return Err("--diagnostic-spawn requires LOW HIGH".to_string());
    };
    let low = first
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = args
        .next()
        .filter(|arg| !arg.starts_with("--"))
        .ok_or_else(|| "--diagnostic-spawn requires LOW HIGH".to_string())?
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let mut requested_threads = 1usize;
    let mut explicit_segment_size = None;
    let mut explicit_mode = None;
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--threads" => {
                let Some(value) = args.next() else {
                    continue;
                };
                requested_threads = value
                    .parse::<usize>()
                    .map_err(|_| "--threads must fit in usize".to_string())?;
            }
            "--segment-size" => {
                let Some(value) = args.next() else {
                    continue;
                };
                explicit_segment_size = Some(
                    value
                        .parse::<u64>()
                        .map_err(|_| "--segment-size must fit in u64".to_string())?,
                );
            }
            "--count-mode" => {
                let Some(value) = args.next() else {
                    continue;
                };
                explicit_mode = parse_count_mode_override(&value)?;
            }
            _ => {}
        }
    }
    if requested_threads == 0 {
        return Err("--threads must be greater than zero".to_string());
    }
    let plan = resolve_count_plan(
        low,
        high,
        explicit_segment_size,
        requested_threads,
        explicit_mode,
    );
    let worker_count = diagnostic_scoped_parallel_worker_spawn(plan.threads)
        .map_err(|err| format!("diagnostic scoped worker spawn failed: {err:?}"))?;
    println!("{worker_count}");
    Ok(())
}

#[derive(Debug, Clone, Copy)]
struct CountPlan {
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
    requested_threads: usize,
    mode: CountMode,
}

fn resolve_count_plan(
    low: u64,
    high: u64,
    explicit_segment_size: Option<u64>,
    requested_threads: usize,
    explicit_mode: Option<CountMode>,
) -> CountPlan {
    let segment_size = explicit_segment_size
        .unwrap_or_else(|| recommended_count_segment_size(low, high, requested_threads));
    let mode = explicit_mode.unwrap_or_else(|| {
        CountMode::parse(recommended_count_mode(low, high, requested_threads))
            .unwrap_or(CountMode::Presieve13)
    });
    let threads = effective_parallel_thread_count(low, high, segment_size, requested_threads);
    CountPlan {
        low,
        high,
        segment_size,
        threads,
        requested_threads,
        mode,
    }
}

fn count_json(plan: &CountPlan, count: usize) -> String {
    format!(
        "{{\"low\":{},\"high\":{},\"count\":{},\"segment_size\":{},\"threads\":{},\"requested_threads\":{},\"count_mode\":\"{}\",\"count_proof_contract\":{}}}",
        plan.low,
        plan.high,
        count,
        plan.segment_size,
        plan.threads,
        plan.requested_threads,
        plan.mode.as_str(),
        prime_range_count_proof_contract_json()
    )
}

fn count_server_command(args: &[String]) -> Result<(), String> {
    let json = args.iter().any(|arg| arg == "--json");
    let defaults = count_server_defaults_from_args(args)?;

    let stdin = io::stdin();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut pool = CountWorkerPool::new();
    for line in stdin.lock().lines() {
        let line = line.map_err(|err| format!("failed to read request: {err}"))?;
        let request = line.trim();
        if request.is_empty() {
            continue;
        }
        if matches!(request, "quit" | "exit") {
            break;
        }

        handle_count_server_request(request, defaults, &mut pool, &mut stdout, json)?;
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

#[derive(Clone, Copy)]
struct CountServerDefaults {
    segment_size: Option<u64>,
    requested_threads: usize,
    mode: Option<CountMode>,
}

fn count_server_defaults_from_args(args: &[String]) -> Result<CountServerDefaults, String> {
    let requested_threads = optional_value(args, "--threads")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--threads must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(1);
    if requested_threads == 0 {
        return Err("--threads must be greater than zero".to_string());
    }
    let segment_size = optional_value(args, "--segment-size")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--segment-size must fit in u64".to_string())
        })
        .transpose()?;
    let mode = optional_value(args, "--count-mode")
        .map(parse_count_mode_override)
        .transpose()?
        .flatten();
    Ok(CountServerDefaults {
        segment_size,
        requested_threads,
        mode,
    })
}

fn handle_count_server_request<W: Write>(
    request: &str,
    defaults: CountServerDefaults,
    pool: &mut CountWorkerPool,
    stdout: &mut W,
    json: bool,
) -> Result<(), String> {
    match parse_count_server_batch_request(request)? {
        CountServerBatchRequest::Identical {
            repetitions,
            raw_request,
        } => {
            let plan = parse_count_server_request(
                &raw_request,
                defaults.segment_size,
                defaults.requested_threads,
                defaults.mode,
            )?;
            let count = count_range_with_pool(pool, &plan)
                .map_err(|err| format!("range sieve failed: {err:?}"))?;
            for _ in 0..repetitions {
                write_count_response(stdout, &plan, count, json)?;
            }
        }
        CountServerBatchRequest::Shifted {
            repetitions,
            shift,
            raw_request,
        } => {
            let plans = shifted_count_plans(
                &raw_request,
                defaults.segment_size,
                defaults.requested_threads,
                defaults.mode,
                repetitions,
                shift,
            )?;
            let counts = count_shifted_plans_with_pool(pool, &plans, shift)
                .map_err(|err| format!("range sieve failed: {err:?}"))?;
            for (plan, count) in plans.iter().zip(counts) {
                write_count_response(stdout, plan, count, json)?;
            }
        }
    }
    Ok(())
}

#[cfg(unix)]
fn socket_server_command(args: &[String]) -> Result<(), String> {
    if args.iter().any(|arg| matches!(arg.as_str(), "--help" | "-h")) {
        println!("{}", usage());
        return Ok(());
    }
    let socket_path = args
        .first()
        .filter(|arg| !arg.starts_with("--"))
        .ok_or_else(|| "socket-server requires SOCKET_PATH".to_string())?;
    let json = args.iter().any(|arg| arg == "--json");
    let defaults = count_server_defaults_from_args(args)?;
    let _ = fs::remove_file(socket_path);
    let listener = UnixListener::bind(socket_path)
        .map_err(|err| format!("failed to bind socket {socket_path}: {err}"))?;
    let mut pool = CountWorkerPool::new();

    for stream in listener.incoming() {
        let stream = stream.map_err(|err| format!("failed to accept socket request: {err}"))?;
        let mut reader = io::BufReader::new(stream);
        let mut request = String::new();
        reader
            .read_line(&mut request)
            .map_err(|err| format!("failed to read socket request: {err}"))?;
        let request = request.trim();
        let mut stream = reader.into_inner();
        if request.is_empty() {
            continue;
        }
        if matches!(request, "quit" | "exit") {
            writeln!(stream, "bye").map_err(|err| format!("failed to write response: {err}"))?;
            break;
        }
        handle_count_server_request(request, defaults, &mut pool, &mut stream, json)?;
        stream
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }

    let _ = fs::remove_file(socket_path);
    Ok(())
}

#[cfg(not(unix))]
fn socket_server_command(_args: &[String]) -> Result<(), String> {
    Err("socket-server is only supported on Unix platforms".to_string())
}

#[cfg(unix)]
fn socket_client_command(args: &[String]) -> Result<(), String> {
    if args.iter().any(|arg| matches!(arg.as_str(), "--help" | "-h")) {
        println!("{}", usage());
        return Ok(());
    }
    let socket_path = args
        .first()
        .ok_or_else(|| "socket-client requires SOCKET_PATH LOW HIGH".to_string())?;
    if args.get(1).is_some_and(|arg| matches!(arg.as_str(), "quit" | "exit")) {
        return socket_client_send_request(socket_path, args[1].as_str());
    }
    let low = args
        .get(1)
        .ok_or_else(|| "socket-client requires SOCKET_PATH LOW HIGH".to_string())?
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = args
        .get(2)
        .ok_or_else(|| "socket-client requires SOCKET_PATH LOW HIGH".to_string())?
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let requested_threads = optional_value(args, "--threads")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--threads must fit in usize".to_string())
        })
        .transpose()?;
    let explicit_segment_size = optional_value(args, "--segment-size")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--segment-size must fit in u64".to_string())
        })
        .transpose()?;
    let explicit_mode = optional_value(args, "--count-mode")
        .map(parse_count_mode_override)
        .transpose()?
        .flatten();
    let request = if requested_threads.is_some()
        || explicit_segment_size.is_some()
        || explicit_mode.is_some()
    {
        let threads = requested_threads.unwrap_or(1);
        if threads == 0 {
            return Err("--threads must be greater than zero".to_string());
        }
        let segment_size = explicit_segment_size
            .unwrap_or_else(|| recommended_count_segment_size(low, high, threads));
        let mode = explicit_mode.unwrap_or_else(|| {
            CountMode::parse(recommended_count_mode(low, high, threads))
                .unwrap_or(CountMode::Presieve13)
        });
        format!("{low} {high} {segment_size} {threads} {}", mode.as_str())
    } else {
        format!("{low} {high}")
    };
    socket_client_send_request(socket_path, &request)
}

#[cfg(not(unix))]
fn socket_client_command(_args: &[String]) -> Result<(), String> {
    Err("socket-client is only supported on Unix platforms".to_string())
}

#[cfg(unix)]
fn socket_client_send_request(socket_path: &str, request: &str) -> Result<(), String> {
    let mut stream = UnixStream::connect(socket_path)
        .map_err(|err| format!("failed to connect to socket {socket_path}: {err}"))?;
    writeln!(stream, "{request}").map_err(|err| format!("failed to write request: {err}"))?;
    let mut reader = io::BufReader::new(stream);
    let mut response = String::new();
    reader
        .read_line(&mut response)
        .map_err(|err| format!("failed to read response: {err}"))?;
    print!("{response}");
    Ok(())
}

fn write_count_response<W: Write>(
    stdout: &mut W,
    plan: &CountPlan,
    count: usize,
    json: bool,
) -> Result<(), String> {
    if json {
        writeln!(stdout, "{}", count_json(plan, count))
    } else {
        writeln!(stdout, "{count}")
    }
    .map_err(|err| format!("failed to write response: {err}"))
}

enum CountServerBatchRequest {
    Identical {
        repetitions: usize,
        raw_request: String,
    },
    Shifted {
        repetitions: usize,
        shift: u64,
        raw_request: String,
    },
}

fn parse_count_server_batch_request(request: &str) -> Result<CountServerBatchRequest, String> {
    let mut parts = request.split_whitespace();
    match parts.next() {
        Some("repeat") => parse_repeated_count_request(parts),
        Some("shifted") => parse_shifted_count_request(parts),
        _ => Ok(CountServerBatchRequest::Identical {
            repetitions: 1,
            raw_request: request.to_string(),
        }),
    }
}

fn parse_repeated_count_request<'a>(
    mut parts: impl Iterator<Item = &'a str>,
) -> Result<CountServerBatchRequest, String> {
    let repetitions = parts
        .next()
        .ok_or_else(|| "repeat request requires COUNT LOW HIGH".to_string())?
        .parse::<usize>()
        .map_err(|_| "repeat COUNT must fit in usize".to_string())?;
    if repetitions == 0 {
        return Err("repeat COUNT must be greater than zero".to_string());
    }
    let rest = parts.collect::<Vec<_>>().join(" ");
    if rest.is_empty() {
        return Err("repeat request requires LOW HIGH".to_string());
    }
    Ok(CountServerBatchRequest::Identical {
        repetitions,
        raw_request: rest,
    })
}

fn parse_shifted_count_request<'a>(
    mut parts: impl Iterator<Item = &'a str>,
) -> Result<CountServerBatchRequest, String> {
    let repetitions = parts
        .next()
        .ok_or_else(|| "shifted request requires COUNT SHIFT LOW HIGH".to_string())?
        .parse::<usize>()
        .map_err(|_| "shifted COUNT must fit in usize".to_string())?;
    if repetitions == 0 {
        return Err("shifted COUNT must be greater than zero".to_string());
    }
    let shift = parts
        .next()
        .ok_or_else(|| "shifted request requires COUNT SHIFT LOW HIGH".to_string())?
        .parse::<u64>()
        .map_err(|_| "shifted SHIFT must fit in u64".to_string())?;
    let rest = parts.collect::<Vec<_>>().join(" ");
    if rest.is_empty() {
        return Err("shifted request requires LOW HIGH".to_string());
    }
    Ok(CountServerBatchRequest::Shifted {
        repetitions,
        shift,
        raw_request: rest,
    })
}

fn parse_count_server_request(
    request: &str,
    default_segment_size: Option<u64>,
    default_requested_threads: usize,
    default_mode: Option<CountMode>,
) -> Result<CountPlan, String> {
    let request = parse_count_server_request_options(
        request,
        default_segment_size,
        default_requested_threads,
        default_mode,
    )?;
    Ok(resolve_count_plan(
        request.low,
        request.high,
        request.explicit_segment_size,
        request.requested_threads,
        request.explicit_mode,
    ))
}

#[derive(Debug, Clone, Copy)]
struct CountRequestOptions {
    low: u64,
    high: u64,
    explicit_segment_size: Option<u64>,
    requested_threads: usize,
    explicit_mode: Option<CountMode>,
}

fn parse_count_server_request_options(
    request: &str,
    default_segment_size: Option<u64>,
    default_requested_threads: usize,
    default_mode: Option<CountMode>,
) -> Result<CountRequestOptions, String> {
    let parts = request.split_whitespace().collect::<Vec<_>>();
    if parts.len() != 2 && parts.len() != 5 {
        return Err(
            "count-server requests must be LOW HIGH or LOW HIGH SEGMENT_SIZE THREADS MODE"
                .to_string(),
        );
    }
    let low = parts[0]
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = parts[1]
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let explicit_segment_size = if parts.len() == 5 {
        Some(
            parts[2]
                .parse::<u64>()
                .map_err(|_| "SEGMENT_SIZE must fit in u64".to_string())?,
        )
    } else {
        default_segment_size
    };
    let requested_threads = if parts.len() == 5 {
        parts[3]
            .parse::<usize>()
            .map_err(|_| "THREADS must fit in usize".to_string())?
    } else {
        default_requested_threads
    };
    if requested_threads == 0 {
        return Err("THREADS must be greater than zero".to_string());
    }
    let explicit_mode = if parts.len() == 5 {
        parse_count_mode_override(parts[4])?
    } else {
        default_mode
    };
    Ok(CountRequestOptions {
        low,
        high,
        explicit_segment_size,
        requested_threads,
        explicit_mode,
    })
}

fn shifted_count_plans(
    request: &str,
    default_segment_size: Option<u64>,
    default_requested_threads: usize,
    default_mode: Option<CountMode>,
    repetitions: usize,
    shift: u64,
) -> Result<Vec<CountPlan>, String> {
    let request = parse_count_server_request_options(
        request,
        default_segment_size,
        default_requested_threads,
        default_mode,
    )?;
    let (_, final_high) = shifted_bounds(request.low, request.high, shift, repetitions - 1)
        .map_err(|err| format!("shifted request overflowed: {err:?}"))?;
    let mut plans = Vec::with_capacity(repetitions);
    for index in 0..repetitions {
        let (low, high) = shifted_bounds(request.low, request.high, shift, index)
            .map_err(|err| format!("shifted request overflowed: {err:?}"))?;
        plans.push(resolve_shifted_count_plan(
            low,
            high,
            final_high,
            request.explicit_segment_size,
            request.requested_threads,
            request.explicit_mode,
        ));
    }
    Ok(plans)
}

fn resolve_shifted_count_plan(
    low: u64,
    high: u64,
    final_high: u64,
    explicit_segment_size: Option<u64>,
    requested_threads: usize,
    explicit_mode: Option<CountMode>,
) -> CountPlan {
    if explicit_segment_size.is_none()
        && explicit_mode.is_none()
        && requested_threads >= 7
        && high > low
    {
        let span = high - low;
        let base_limit = (high - 1).isqrt();
        let final_base_limit = (final_high - 1).isqrt();
        if span <= 16_000_000
            && base_limit >= PARALLEL_EDGE_HIGH_OFFSET_MIN_BASE_LIMIT
            && final_base_limit < PARALLEL_LOWER_HIGH_OFFSET_MIN_BASE_LIMIT
        {
            let segment_size = SHIFTED_EDGE_HIGH_OFFSET_SEGMENT_SIZE;
            let mode = CountMode::Presieve13;
            let threads =
                effective_parallel_thread_count(low, high, segment_size, requested_threads);
            return CountPlan {
                low,
                high,
                segment_size,
                threads,
                requested_threads,
                mode,
            };
        }
        if span <= 16_000_000
            && base_limit >= PARALLEL_LOWER_HIGH_OFFSET_MIN_BASE_LIMIT
            && final_base_limit < PARALLEL_LOWER_HIGH_OFFSET_BASE_LIMIT
        {
            let segment_size = SHIFTED_LOWER_HIGH_OFFSET_SEGMENT_SIZE;
            let mode = CountMode::Presieve13;
            let threads =
                effective_parallel_thread_count(low, high, segment_size, requested_threads);
            return CountPlan {
                low,
                high,
                segment_size,
                threads,
                requested_threads,
                mode,
            };
        }
    }

    resolve_count_plan(
        low,
        high,
        explicit_segment_size,
        requested_threads,
        explicit_mode,
    )
}

struct CountWorkerPool {
    senders: Vec<mpsc::Sender<CountWorkerCommand>>,
    handles: Vec<JoinHandle<()>>,
    result_sender: mpsc::Sender<Result<CountWorkerReply, circle_prime::RangeError>>,
    result_receiver: mpsc::Receiver<Result<CountWorkerReply, circle_prime::RangeError>>,
    caller_scratch: PrimeCountScratch,
}

impl CountWorkerPool {
    fn new() -> Self {
        let (result_sender, result_receiver) = mpsc::channel();
        Self {
            senders: Vec::new(),
            handles: Vec::new(),
            result_sender,
            result_receiver,
            caller_scratch: PrimeCountScratch::new(),
        }
    }

    fn count_chunks(
        &mut self,
        chunks: &[(u64, u64)],
        segment_size: u64,
        mode: CountMode,
    ) -> Result<usize, circle_prime::RangeError> {
        let Some((&caller_chunk, worker_chunks)) = chunks.split_first() else {
            return Ok(0);
        };

        self.ensure_worker_count(worker_chunks.len());
        for (worker_index, &(low, high)) in worker_chunks.iter().enumerate() {
            self.senders[worker_index]
                .send(CountWorkerCommand::Count {
                    low,
                    high,
                    segment_size,
                    mode,
                })
                .map_err(|_| circle_prime::RangeError::WorkerPanic)?;
        }

        let mut total = count_range_with_mode_scratch(
            caller_chunk.0,
            caller_chunk.1,
            segment_size,
            mode,
            &mut self.caller_scratch,
        )?;
        for _ in worker_chunks {
            match self
                .result_receiver
                .recv()
                .map_err(|_| circle_prime::RangeError::WorkerPanic)??
            {
                CountWorkerReply::Count(count) => total += count,
                CountWorkerReply::Shifted(_) => return Err(circle_prime::RangeError::WorkerPanic),
            }
        }
        Ok(total)
    }

    fn count_shifted_chunks(
        &mut self,
        chunks: &[(u64, u64)],
        segment_size: u64,
        mode: CountMode,
        repetitions: usize,
        shift: u64,
    ) -> Result<Vec<usize>, circle_prime::RangeError> {
        let Some((&caller_chunk, worker_chunks)) = chunks.split_first() else {
            return Ok(vec![0; repetitions]);
        };

        self.ensure_worker_count(worker_chunks.len());
        for (worker_index, &(low, high)) in worker_chunks.iter().enumerate() {
            self.senders[worker_index]
                .send(CountWorkerCommand::ShiftedCount {
                    low,
                    high,
                    segment_size,
                    mode,
                    repetitions,
                    shift,
                })
                .map_err(|_| circle_prime::RangeError::WorkerPanic)?;
        }

        let mut totals = count_shifted_range_with_mode_scratch(
            caller_chunk.0,
            caller_chunk.1,
            segment_size,
            mode,
            repetitions,
            shift,
            &mut self.caller_scratch,
        )?;
        for _ in worker_chunks {
            match self
                .result_receiver
                .recv()
                .map_err(|_| circle_prime::RangeError::WorkerPanic)??
            {
                CountWorkerReply::Shifted(counts) => {
                    if counts.len() != totals.len() {
                        return Err(circle_prime::RangeError::WorkerPanic);
                    }
                    for (total, count) in totals.iter_mut().zip(counts) {
                        *total += count;
                    }
                }
                CountWorkerReply::Count(_) => return Err(circle_prime::RangeError::WorkerPanic),
            }
        }
        Ok(totals)
    }

    fn count_adjacent_shifted_chunks(
        &mut self,
        chunks: &[(u64, u64)],
        batch_low: u64,
        span: u64,
        segment_size: u64,
        mode: CountMode,
        repetitions: usize,
    ) -> Result<Vec<usize>, circle_prime::RangeError> {
        let Some((&caller_chunk, worker_chunks)) = chunks.split_first() else {
            return Ok(vec![0; repetitions]);
        };

        self.ensure_worker_count(worker_chunks.len());
        for (worker_index, &(low, high)) in worker_chunks.iter().enumerate() {
            self.senders[worker_index]
                .send(CountWorkerCommand::AdjacentShiftedCount {
                    batch_low,
                    span,
                    low,
                    high,
                    segment_size,
                    mode,
                    repetitions,
                })
                .map_err(|_| circle_prime::RangeError::WorkerPanic)?;
        }

        let mut totals = count_adjacent_shifted_range_with_mode_scratch(
            batch_low,
            span,
            caller_chunk.0,
            caller_chunk.1,
            segment_size,
            mode,
            repetitions,
            &mut self.caller_scratch,
        )?;
        for _ in worker_chunks {
            match self
                .result_receiver
                .recv()
                .map_err(|_| circle_prime::RangeError::WorkerPanic)??
            {
                CountWorkerReply::Shifted(counts) => {
                    if counts.len() != totals.len() {
                        return Err(circle_prime::RangeError::WorkerPanic);
                    }
                    for (total, count) in totals.iter_mut().zip(counts) {
                        *total += count;
                    }
                }
                CountWorkerReply::Count(_) => return Err(circle_prime::RangeError::WorkerPanic),
            }
        }
        Ok(totals)
    }

    fn ensure_worker_count(&mut self, worker_count: usize) {
        while self.senders.len() < worker_count {
            let (sender, receiver) = mpsc::channel();
            let result_sender = self.result_sender.clone();
            let handle = thread::spawn(move || count_worker_loop(receiver, result_sender));
            self.senders.push(sender);
            self.handles.push(handle);
        }
    }
}

impl Drop for CountWorkerPool {
    fn drop(&mut self) {
        for sender in &self.senders {
            let _ = sender.send(CountWorkerCommand::Stop);
        }
        while let Some(handle) = self.handles.pop() {
            let _ = handle.join();
        }
    }
}

enum CountWorkerCommand {
    Count {
        low: u64,
        high: u64,
        segment_size: u64,
        mode: CountMode,
    },
    ShiftedCount {
        low: u64,
        high: u64,
        segment_size: u64,
        mode: CountMode,
        repetitions: usize,
        shift: u64,
    },
    AdjacentShiftedCount {
        batch_low: u64,
        span: u64,
        low: u64,
        high: u64,
        segment_size: u64,
        mode: CountMode,
        repetitions: usize,
    },
    Stop,
}

enum CountWorkerReply {
    Count(usize),
    Shifted(Vec<usize>),
}

fn count_worker_loop(
    receiver: mpsc::Receiver<CountWorkerCommand>,
    result_sender: mpsc::Sender<Result<CountWorkerReply, circle_prime::RangeError>>,
) {
    let mut scratch = PrimeCountScratch::new();
    while let Ok(command) = receiver.recv() {
        match command {
            CountWorkerCommand::Count {
                low,
                high,
                segment_size,
                mode,
            } => {
                let result =
                    count_range_with_mode_scratch(low, high, segment_size, mode, &mut scratch);
                let _ = result_sender.send(result.map(CountWorkerReply::Count));
            }
            CountWorkerCommand::ShiftedCount {
                low,
                high,
                segment_size,
                mode,
                repetitions,
                shift,
            } => {
                let result = count_shifted_range_with_mode_scratch(
                    low,
                    high,
                    segment_size,
                    mode,
                    repetitions,
                    shift,
                    &mut scratch,
                );
                let _ = result_sender.send(result.map(CountWorkerReply::Shifted));
            }
            CountWorkerCommand::AdjacentShiftedCount {
                batch_low,
                span,
                low,
                high,
                segment_size,
                mode,
                repetitions,
            } => {
                let result = count_adjacent_shifted_range_with_mode_scratch(
                    batch_low,
                    span,
                    low,
                    high,
                    segment_size,
                    mode,
                    repetitions,
                    &mut scratch,
                );
                let _ = result_sender.send(result.map(CountWorkerReply::Shifted));
            }
            CountWorkerCommand::Stop => break,
        }
    }
}

fn count_range_with_pool(
    pool: &mut CountWorkerPool,
    plan: &CountPlan,
) -> Result<usize, circle_prime::RangeError> {
    if plan.threads <= 1
        || plan.high <= plan.low
        || plan.segment_size == 0
        || !plan.mode.supports_worker_pool()
        || (plan.high - 1).isqrt() > BASE_PRIME_CACHE_LIMIT
    {
        return count_range_with_mode(
            plan.low,
            plan.high,
            plan.segment_size,
            plan.threads,
            plan.mode,
        );
    }

    let chunks = split_range_evenly(plan.low, plan.high, plan.threads);
    if chunks.len() <= 1 {
        return count_range_with_mode(plan.low, plan.high, plan.segment_size, 1, plan.mode);
    }
    pool.count_chunks(&chunks, plan.segment_size, plan.mode)
}

fn count_shifted_plans_with_pool(
    pool: &mut CountWorkerPool,
    plans: &[CountPlan],
    shift: u64,
) -> Result<Vec<usize>, circle_prime::RangeError> {
    let Some(first_plan) = plans.first().copied() else {
        return Ok(Vec::new());
    };
    if plans.iter().all(|plan| {
        plan.segment_size == first_plan.segment_size
            && plan.threads == first_plan.threads
            && plan.requested_threads == first_plan.requested_threads
            && plan.mode == first_plan.mode
            && plan.high.saturating_sub(plan.low) == first_plan.high.saturating_sub(first_plan.low)
    }) {
        if let Some(counts) = count_shifted_with_pool(pool, &first_plan, plans.len(), shift)? {
            return Ok(counts);
        }
    }

    plans
        .iter()
        .map(|plan| count_range_with_pool(pool, plan))
        .collect()
}

fn count_shifted_with_pool(
    pool: &mut CountWorkerPool,
    plan: &CountPlan,
    repetitions: usize,
    shift: u64,
) -> Result<Option<Vec<usize>>, circle_prime::RangeError> {
    if repetitions == 0 {
        return Ok(Some(Vec::new()));
    }
    if !matches!(plan.mode, CountMode::Presieve13 | CountMode::Presieve17)
        || plan.high <= plan.low
        || plan.segment_size == 0
    {
        return Ok(None);
    }
    let (_, final_high) = shifted_bounds(plan.low, plan.high, shift, repetitions - 1)?;
    if (final_high - 1).isqrt() > BASE_PRIME_CACHE_LIMIT {
        return Ok(None);
    }
    let span = plan.high - plan.low;
    if shift == span {
        if plan.threads <= 1 {
            return count_adjacent_shifted_range_with_mode_scratch(
                plan.low,
                span,
                plan.low,
                final_high,
                plan.segment_size,
                plan.mode,
                repetitions,
                &mut pool.caller_scratch,
            )
            .map(Some);
        }

        let chunk_count = adjacent_shifted_dynamic_chunk_count(
            plan.low,
            final_high,
            plan.segment_size,
            plan.threads,
        );
        let chunks = split_range_evenly(plan.low, final_high, chunk_count);
        if chunks.len() <= 1 {
            return Ok(None);
        }
        if chunks.len() > plan.threads {
            return count_adjacent_shifted_chunks_scoped(
                &chunks,
                plan.low,
                span,
                plan.segment_size,
                plan.mode,
                repetitions,
                plan.threads,
            )
            .map(Some);
        }
        return pool
            .count_adjacent_shifted_chunks(
                &chunks,
                plan.low,
                span,
                plan.segment_size,
                plan.mode,
                repetitions,
            )
            .map(Some);
    }
    if plan.threads <= 1 {
        return count_shifted_range_with_mode_scratch(
            plan.low,
            plan.high,
            plan.segment_size,
            plan.mode,
            repetitions,
            shift,
            &mut pool.caller_scratch,
        )
        .map(Some);
    }

    let chunks = split_range_evenly(plan.low, plan.high, plan.threads);
    if chunks.len() <= 1 {
        return Ok(None);
    }
    pool.count_shifted_chunks(&chunks, plan.segment_size, plan.mode, repetitions, shift)
        .map(Some)
}

fn adjacent_shifted_dynamic_chunk_count(
    low: u64,
    high: u64,
    segment_size: u64,
    threads: usize,
) -> usize {
    let workers = threads.max(1);
    if high <= low || segment_size == 0 {
        return workers;
    }
    let segment_count = (high - low).div_ceil(segment_size);
    let target_chunks = workers.saturating_mul(4).max(workers);
    usize::try_from(segment_count)
        .unwrap_or(usize::MAX)
        .min(target_chunks)
        .max(workers)
}

fn count_adjacent_shifted_chunks_scoped(
    chunks: &[(u64, u64)],
    batch_low: u64,
    span: u64,
    segment_size: u64,
    mode: CountMode,
    repetitions: usize,
    threads: usize,
) -> Result<Vec<usize>, circle_prime::RangeError> {
    if chunks.is_empty() {
        return Ok(vec![0; repetitions]);
    }
    let worker_count = threads.max(1).min(chunks.len());
    let next_chunk = AtomicUsize::new(0);
    thread::scope(|scope| {
        let mut handles = Vec::with_capacity(worker_count);
        for _ in 0..worker_count {
            handles.push(scope.spawn(|| {
                let mut scratch = PrimeCountScratch::new();
                let mut totals = vec![0usize; repetitions];
                loop {
                    let chunk_index = next_chunk.fetch_add(1, Ordering::Relaxed);
                    let Some(&(low, high)) = chunks.get(chunk_index) else {
                        break;
                    };
                    let counts = count_adjacent_shifted_range_with_mode_scratch(
                        batch_low,
                        span,
                        low,
                        high,
                        segment_size,
                        mode,
                        repetitions,
                        &mut scratch,
                    )?;
                    if counts.len() != totals.len() {
                        return Err(circle_prime::RangeError::WorkerPanic);
                    }
                    for (total, count) in totals.iter_mut().zip(counts) {
                        *total += count;
                    }
                }
                Ok(totals)
            }));
        }

        let mut totals = vec![0usize; repetitions];
        for handle in handles {
            let counts = handle
                .join()
                .map_err(|_| circle_prime::RangeError::WorkerPanic)??;
            if counts.len() != totals.len() {
                return Err(circle_prime::RangeError::WorkerPanic);
            }
            for (total, count) in totals.iter_mut().zip(counts) {
                *total += count;
            }
        }
        Ok(totals)
    })
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

fn shifted_bounds(
    low: u64,
    high: u64,
    shift: u64,
    index: usize,
) -> Result<(u64, u64), circle_prime::RangeError> {
    let index = u64::try_from(index).map_err(|_| circle_prime::RangeError::SegmentTooLarge)?;
    let delta = shift
        .checked_mul(index)
        .ok_or(circle_prime::RangeError::SegmentTooLarge)?;
    let shifted_low = low
        .checked_add(delta)
        .ok_or(circle_prime::RangeError::SegmentTooLarge)?;
    let shifted_high = high
        .checked_add(delta)
        .ok_or(circle_prime::RangeError::SegmentTooLarge)?;
    Ok((shifted_low, shifted_high))
}

fn count_shifted_range_with_mode_scratch(
    low: u64,
    high: u64,
    segment_size: u64,
    mode: CountMode,
    repetitions: usize,
    shift: u64,
    scratch: &mut PrimeCountScratch,
) -> Result<Vec<usize>, circle_prime::RangeError> {
    if mode == CountMode::Presieve13 {
        if let Some(counts) = prime_count_shifted_single_segment_presieve13_with_scratch(
            low,
            high,
            segment_size,
            repetitions,
            shift,
            scratch,
        )? {
            return Ok(counts);
        }
    }
    if mode == CountMode::Presieve17 {
        if let Some(counts) = prime_count_shifted_single_segment_presieve17_with_scratch(
            low,
            high,
            segment_size,
            repetitions,
            shift,
            scratch,
        )? {
            return Ok(counts);
        }
    }

    let mut counts = Vec::with_capacity(repetitions);
    for index in 0..repetitions {
        let (request_low, request_high) = shifted_bounds(low, high, shift, index)?;
        counts.push(count_range_with_mode_scratch(
            request_low,
            request_high,
            segment_size,
            mode,
            scratch,
        )?);
    }
    Ok(counts)
}

fn count_adjacent_shifted_range_with_mode_scratch(
    batch_low: u64,
    span: u64,
    range_low: u64,
    range_high: u64,
    segment_size: u64,
    mode: CountMode,
    repetitions: usize,
    scratch: &mut PrimeCountScratch,
) -> Result<Vec<usize>, circle_prime::RangeError> {
    match mode {
        CountMode::Presieve13 => {
            if let Some(counts) = prime_count_adjacent_shifted_presieve13_with_scratch(
                batch_low,
                span,
                repetitions,
                range_low,
                range_high,
                segment_size,
                scratch,
            )? {
                return Ok(counts);
            }
        }
        CountMode::Presieve17 => {
            if let Some(counts) = prime_count_adjacent_shifted_presieve17_with_scratch(
                batch_low,
                span,
                repetitions,
                range_low,
                range_high,
                segment_size,
                scratch,
            )? {
                return Ok(counts);
            }
        }
        CountMode::Segmented | CountMode::Balanced | CountMode::Dynamic => {}
    }

    let mut counts = vec![0; repetitions];
    for index in 0..repetitions {
        let bin_low = batch_low
            .checked_add(
                span.checked_mul(
                    u64::try_from(index).map_err(|_| circle_prime::RangeError::SegmentTooLarge)?,
                )
                .ok_or(circle_prime::RangeError::SegmentTooLarge)?,
            )
            .ok_or(circle_prime::RangeError::SegmentTooLarge)?;
        let bin_high = bin_low
            .checked_add(span)
            .ok_or(circle_prime::RangeError::SegmentTooLarge)?;
        let overlap_low = range_low.max(bin_low);
        let overlap_high = range_high.min(bin_high);
        if overlap_low < overlap_high {
            counts[index] = count_range_with_mode_scratch(
                overlap_low,
                overlap_high,
                segment_size,
                mode,
                scratch,
            )?;
        }
    }
    Ok(counts)
}

fn count_range_with_mode_scratch(
    low: u64,
    high: u64,
    segment_size: u64,
    mode: CountMode,
    scratch: &mut PrimeCountScratch,
) -> Result<usize, circle_prime::RangeError> {
    match mode {
        CountMode::Segmented => prime_count_in_range_with_scratch(low, high, segment_size, scratch),
        CountMode::Balanced | CountMode::Dynamic => {
            count_range_with_mode(low, high, segment_size, 1, mode)
        }
        CountMode::Presieve13 => {
            prime_count_in_range_presieve13_with_scratch(low, high, segment_size, scratch)
        }
        CountMode::Presieve17 => {
            prime_count_in_range_presieve17_with_scratch(low, high, segment_size, scratch)
        }
    }
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
    }
}

fn optional_value<'a>(args: &'a [String], flag: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|window| window[0] == flag)
        .map(|window| window[1].as_str())
}

fn parse_count_mode_override(raw: &str) -> Result<Option<CountMode>, String> {
    if raw == "default" {
        Ok(None)
    } else {
        CountMode::parse(raw).map(Some)
    }
}

fn usage() -> String {
    [
        "usage:",
        "  circle-prime-count LOW HIGH [--json] [--segment-size N] [--threads N] [--count-mode MODE]",
        "  circle-prime-count count-server [--json] [--segment-size N] [--threads N] [--count-mode MODE]",
        "  circle-prime-count socket-server SOCKET_PATH [--json] [--segment-size N] [--threads N] [--count-mode MODE]",
        "  circle-prime-count socket-client SOCKET_PATH LOW HIGH [--segment-size N] [--threads N] [--count-mode MODE]",
        "",
        "count-server request: LOW HIGH or LOW HIGH SEGMENT_SIZE THREADS MODE",
        "count-server repeat request: repeat COUNT LOW HIGH [SEGMENT_SIZE THREADS MODE] (replays the same computed response)",
        "count-server shifted request: shifted COUNT SHIFT LOW HIGH [SEGMENT_SIZE THREADS MODE]",
        "socket-server exposes the same request protocol over a Unix socket for prewarmed local clients",
        "count modes: default, segmented, balanced, dynamic, presieve13, presieve17",
    ]
    .join("\n")
}
