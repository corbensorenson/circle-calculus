use std::convert::TryFrom;
use std::env;
use std::fs;
use std::io::{self, BufRead, Write};
use std::process;
use std::sync::mpsc;
use std::thread::{self, JoinHandle};

use num_bigint::BigUint;

use circle_prime::{
    big_fuzzy_any_prime_search, big_fuzzy_any_prime_value, effective_parallel_thread_count,
    effective_prefix_pi_thread_count, fuzzy_any_prime_value_with_score_limit,
    fuzzy_search_with_score_limit, inspect_horizon, is_bpsw_probable_prime_biguint, is_prime_u64,
    is_probable_prime_biguint, next_bpsw_probable_prime_biguint, next_prime_u64,
    next_prime_value_u64, next_probable_prime_biguint, parse_biguint, prime_count_in_range,
    prime_count_in_range_hybrid_wheel30_marks, prime_count_in_range_hybrid_wheel30_marks_parallel,
    prime_count_in_range_parallel, prime_count_in_range_parallel_balanced,
    prime_count_in_range_parallel_dynamic, prime_count_in_range_prefix_pi,
    prime_count_in_range_prefix_pi_parallel, prime_count_in_range_presieve13,
    prime_count_in_range_presieve13_parallel, prime_count_in_range_presieve13_with_scratch,
    prime_count_in_range_presieve17, prime_count_in_range_presieve17_parallel,
    prime_count_in_range_presieve17_with_scratch, prime_count_in_range_small_prefix_pi,
    prime_count_in_range_wheel30_marks, prime_count_in_range_wheel30_marks_parallel,
    prime_count_in_range_with_scratch, prime_count_shifted_single_segment_presieve13_with_scratch,
    prime_count_shifted_single_segment_presieve17_with_scratch, prime_horizon_proof_contract_json,
    prime_range_count_proof_contract_json, primes_in_range, recommended_count_mode,
    recommended_count_segment_size, recommended_segment_size, warm_small_prefix_pi_cache,
    BigFuzzyPrimeModel, FuzzyPrimeModel, FuzzySearchMode, PrimeCountScratch,
    BASE_PRIME_CACHE_LIMIT, DEFAULT_BIG_FUZZY_CANDIDATE_WINDOW, DEFAULT_BIG_MILLER_RABIN_ROUNDS,
    DEFAULT_BIG_NEXT_MAX_CANDIDATES, PARALLEL_EDGE_HIGH_OFFSET_MIN_BASE_LIMIT,
    PARALLEL_LOWER_HIGH_OFFSET_BASE_LIMIT, PARALLEL_LOWER_HIGH_OFFSET_MIN_BASE_LIMIT,
};

const MAX_INSPECT_N: u128 = 100_000;
const SHIFTED_EDGE_HIGH_OFFSET_SEGMENT_SIZE: u64 = 1_638_400;
const SHIFTED_LOWER_HIGH_OFFSET_SEGMENT_SIZE: u64 = 1_835_008;
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

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum BigPrimeProfile {
    MillerRabin,
    BailliePsw,
}

impl BigPrimeProfile {
    fn parse(raw: &str) -> Result<Self, String> {
        match raw {
            "mr" | "miller-rabin" => Ok(Self::MillerRabin),
            "bpsw" | "baillie-psw" => Ok(Self::BailliePsw),
            _ => Err("big prime profile must be mr or bpsw".to_string()),
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
        "next-server" => next_server_command(&args[1..]),
        "big-test" => big_test_command(&args[1..]),
        "big-next" => big_next_command(&args[1..]),
        "big-fuzzy-search" => big_fuzzy_search_command(&args[1..]),
        "big-test-server" => big_test_server_command(&args[1..]),
        "big-next-server" => big_next_server_command(&args[1..]),
        "big-fuzzy-server" => big_fuzzy_server_command(&args[1..]),
        "fuzzy-search" => fuzzy_search_command(&args[1..]),
        "fuzzy-server" => fuzzy_server_command(&args[1..]),
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

fn big_test_command(args: &[String]) -> Result<(), String> {
    let n = parse_biguint(required_arg(args, 0, "big-test requires N")?)?;
    let rounds = big_rounds_arg(args)?;
    let profile = big_profile_arg(args)?;
    let json = args.iter().any(|arg| arg == "--json");
    let decision = big_prime_decision(&n, profile, rounds)?;
    if json {
        println!("{}", decision.to_json());
    } else {
        println!("n = {}", decision.n);
        println!("bit_length = {}", decision.bit_length);
        println!("status = {:?}", decision.status);
        println!("method = {}", decision.method);
        println!("stage = {}", decision.stage);
        println!("miller_rabin_rounds = {}", decision.miller_rabin_rounds);
        if let Some(factor) = decision.factor {
            println!("factor = {factor}");
        }
        if let Some(base) = decision.witness_base {
            println!("witness_base = {base}");
        }
    }
    Ok(())
}

fn big_test_server_command(args: &[String]) -> Result<(), String> {
    let rounds = big_rounds_arg(args)?;
    let profile = big_profile_arg(args)?;
    let json = args.iter().any(|arg| arg == "--json");
    let stdin = io::stdin();
    let mut reader = stdin.lock();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut buffer = Vec::with_capacity(256);
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
        let (n, repetitions) = parse_big_server_request(request, "big-test-server")?;
        for _ in 0..repetitions {
            let decision = big_prime_decision(&n, profile, rounds)?;
            if json {
                writeln!(stdout, "{}", decision.to_json())
                    .map_err(|err| format!("failed to write response: {err}"))?;
            } else {
                let status = match decision.status {
                    circle_prime::BigPrimeStatus::Composite => "composite",
                    circle_prime::BigPrimeStatus::Prime => "prime",
                    circle_prime::BigPrimeStatus::ProbablePrime => "probable_prime",
                };
                writeln!(stdout, "{status}")
                    .map_err(|err| format!("failed to write response: {err}"))?;
            }
        }
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

fn big_next_command(args: &[String]) -> Result<(), String> {
    let start = parse_biguint(required_arg(args, 0, "big-next requires START")?)?;
    let rounds = big_rounds_arg(args)?;
    let profile = big_profile_arg(args)?;
    let max_candidates = optional_value(args, "--max-candidates")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--max-candidates must fit in u64".to_string())
        })
        .transpose()?
        .unwrap_or(DEFAULT_BIG_NEXT_MAX_CANDIDATES);
    let json = args.iter().any(|arg| arg == "--json");
    let search = big_next_search(&start, profile, rounds, max_candidates)?;
    if json {
        println!("{}", search.to_json());
    } else if let Some(prime) = search.prime {
        println!("{prime}");
    } else {
        println!("none");
    }
    Ok(())
}

fn big_next_server_command(args: &[String]) -> Result<(), String> {
    let rounds = big_rounds_arg(args)?;
    let profile = big_profile_arg(args)?;
    let max_candidates = optional_value(args, "--max-candidates")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--max-candidates must fit in u64".to_string())
        })
        .transpose()?
        .unwrap_or(DEFAULT_BIG_NEXT_MAX_CANDIDATES);
    let json = args.iter().any(|arg| arg == "--json");
    let stdin = io::stdin();
    let mut reader = stdin.lock();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut buffer = Vec::with_capacity(256);
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
        let (start, repetitions) = parse_big_server_request(request, "big-next-server")?;
        for _ in 0..repetitions {
            let search = big_next_search(&start, profile, rounds, max_candidates)?;
            if json {
                writeln!(stdout, "{}", search.to_json())
                    .map_err(|err| format!("failed to write response: {err}"))?;
            } else if let Some(prime) = search.prime {
                writeln!(stdout, "{prime}")
                    .map_err(|err| format!("failed to write response: {err}"))?;
            } else {
                stdout
                    .write_all(b"none\n")
                    .map_err(|err| format!("failed to write response: {err}"))?;
            }
        }
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

fn big_fuzzy_search_command(args: &[String]) -> Result<(), String> {
    let model_path = required_arg(args, 0, "big-fuzzy-search requires MODEL START")?;
    let start = parse_biguint(required_arg(
        args,
        1,
        "big-fuzzy-search requires MODEL START",
    )?)?;
    let rounds = big_rounds_arg(args)?;
    let candidate_window = optional_value(args, "--candidate-window")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--candidate-window must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(DEFAULT_BIG_FUZZY_CANDIDATE_WINDOW);
    let top_k = optional_value(args, "--top-k")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--top-k must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(32);
    let score_limit = optional_value(args, "--score-limit")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--score-limit must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(usize::MAX);
    let json = args.iter().any(|arg| arg == "--json");
    let raw_model = fs::read_to_string(model_path)
        .map_err(|err| format!("failed to read fuzzy model {model_path:?}: {err}"))?;
    let model = BigFuzzyPrimeModel::from_text(&raw_model)?;
    if json {
        let search = big_fuzzy_any_prime_search(
            &model,
            &start,
            candidate_window,
            top_k,
            score_limit,
            rounds,
        )?;
        println!("{}", search.to_json(&model));
    } else {
        match big_fuzzy_any_prime_value(
            &model,
            &start,
            candidate_window,
            top_k,
            score_limit,
            rounds,
        )? {
            Some(prime) => println!("{prime}"),
            None => println!("none"),
        }
    }
    Ok(())
}

fn big_fuzzy_server_command(args: &[String]) -> Result<(), String> {
    let model_path = required_arg(args, 0, "big-fuzzy-server requires MODEL")?;
    let rounds = big_rounds_arg(args)?;
    let candidate_window = optional_value(args, "--candidate-window")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--candidate-window must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(DEFAULT_BIG_FUZZY_CANDIDATE_WINDOW);
    let top_k = optional_value(args, "--top-k")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--top-k must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(32);
    let score_limit = optional_value(args, "--score-limit")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--score-limit must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(usize::MAX);
    let json = args.iter().any(|arg| arg == "--json");
    let raw_model = fs::read_to_string(model_path)
        .map_err(|err| format!("failed to read fuzzy model {model_path:?}: {err}"))?;
    let model = BigFuzzyPrimeModel::from_text(&raw_model)?;
    let stdin = io::stdin();
    let mut reader = stdin.lock();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut buffer = Vec::with_capacity(256);
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
        let (start, repetitions) = parse_big_server_request(request, "big-fuzzy-server")?;
        for _ in 0..repetitions {
            if json {
                let search = big_fuzzy_any_prime_search(
                    &model,
                    &start,
                    candidate_window,
                    top_k,
                    score_limit,
                    rounds,
                )?;
                writeln!(stdout, "{}", search.to_json(&model))
                    .map_err(|err| format!("failed to write response: {err}"))?;
            } else {
                match big_fuzzy_any_prime_value(
                    &model,
                    &start,
                    candidate_window,
                    top_k,
                    score_limit,
                    rounds,
                )? {
                    Some(prime) => writeln!(stdout, "{prime}")
                        .map_err(|err| format!("failed to write response: {err}"))?,
                    None => stdout
                        .write_all(b"none\n")
                        .map_err(|err| format!("failed to write response: {err}"))?,
                }
            }
        }
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

fn fuzzy_search_command(args: &[String]) -> Result<(), String> {
    let model_path = required_arg(args, 0, "fuzzy-search requires MODEL START")?;
    let start = required_arg(args, 1, "fuzzy-search requires MODEL START")?
        .parse::<u64>()
        .map_err(|_| "fuzzy-search START must fit in u64".to_string())?;
    let mode = optional_value(args, "--mode")
        .map(FuzzySearchMode::parse)
        .transpose()?
        .unwrap_or(FuzzySearchMode::ExactNext);
    let window = optional_value(args, "--window")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--window must fit in u64".to_string())
        })
        .transpose()?
        .unwrap_or(512);
    let top_k = optional_value(args, "--top-k")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--top-k must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(32);
    let score_limit = optional_value(args, "--score-limit")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--score-limit must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(usize::MAX);
    let json = args.iter().any(|arg| arg == "--json");
    let raw_model = fs::read_to_string(model_path)
        .map_err(|err| format!("failed to read fuzzy model {model_path:?}: {err}"))?;
    let model = FuzzyPrimeModel::from_text(&raw_model)?;
    let search = fuzzy_search_with_score_limit(&model, mode, start, window, top_k, score_limit)?;
    if json {
        println!("{}", search.to_json(&model));
    } else if let Some(prime) = search.reported_prime {
        println!("{prime}");
    } else {
        println!("none");
    }
    Ok(())
}

fn big_rounds_arg(args: &[String]) -> Result<usize, String> {
    optional_value(args, "--rounds")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--rounds must fit in usize".to_string())
        })
        .transpose()
        .map(|rounds| rounds.unwrap_or(DEFAULT_BIG_MILLER_RABIN_ROUNDS))
}

fn big_profile_arg(args: &[String]) -> Result<BigPrimeProfile, String> {
    optional_value(args, "--profile")
        .map(BigPrimeProfile::parse)
        .transpose()
        .map(|profile| profile.unwrap_or(BigPrimeProfile::MillerRabin))
}

fn big_prime_decision(
    n: &BigUint,
    profile: BigPrimeProfile,
    rounds: usize,
) -> Result<circle_prime::BigPrimeDecision, String> {
    match profile {
        BigPrimeProfile::MillerRabin => is_probable_prime_biguint(n, rounds),
        BigPrimeProfile::BailliePsw => is_bpsw_probable_prime_biguint(n),
    }
}

fn big_next_search(
    start: &BigUint,
    profile: BigPrimeProfile,
    rounds: usize,
    max_candidates: u64,
) -> Result<circle_prime::BigNextPrimeSearch, String> {
    match profile {
        BigPrimeProfile::MillerRabin => next_probable_prime_biguint(start, rounds, max_candidates),
        BigPrimeProfile::BailliePsw => next_bpsw_probable_prime_biguint(start, max_candidates),
    }
}

fn fuzzy_server_command(args: &[String]) -> Result<(), String> {
    let model_path = required_arg(args, 0, "fuzzy-server requires MODEL")?;
    let mode = optional_value(args, "--mode")
        .map(FuzzySearchMode::parse)
        .transpose()?
        .unwrap_or(FuzzySearchMode::ExactNext);
    let window = optional_value(args, "--window")
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|_| "--window must fit in u64".to_string())
        })
        .transpose()?
        .unwrap_or(512);
    let top_k = optional_value(args, "--top-k")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--top-k must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(32);
    let score_limit = optional_value(args, "--score-limit")
        .map(|value| {
            value
                .parse::<usize>()
                .map_err(|_| "--score-limit must fit in usize".to_string())
        })
        .transpose()?
        .unwrap_or(usize::MAX);
    let json = args.iter().any(|arg| arg == "--json");
    let raw_model = fs::read_to_string(model_path)
        .map_err(|err| format!("failed to read fuzzy model {model_path:?}: {err}"))?;
    let model = FuzzyPrimeModel::from_text(&raw_model)?;
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
        let (start, repetitions) = parse_next_server_request_ascii(request)?;
        for _ in 0..repetitions {
            if json {
                let search =
                    fuzzy_search_with_score_limit(&model, mode, start, window, top_k, score_limit)?;
                writeln!(stdout, "{}", search.to_json(&model))
                    .map_err(|err| format!("failed to write response: {err}"))?;
            } else {
                let prime = match mode {
                    FuzzySearchMode::AnyPrime => fuzzy_any_prime_value_with_score_limit(
                        &model,
                        start,
                        window,
                        top_k,
                        score_limit,
                    )?,
                    FuzzySearchMode::ExactNext => {
                        fuzzy_search_with_score_limit(
                            &model,
                            mode,
                            start,
                            window,
                            top_k,
                            score_limit,
                        )?
                        .reported_prime
                    }
                };
                if let Some(prime) = prime {
                    write_u64_line(&mut stdout, prime)?;
                } else {
                    stdout
                        .write_all(b"none\n")
                        .map_err(|err| format!("failed to write response: {err}"))?;
                }
            }
        }
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

fn next_command(args: &[String]) -> Result<(), String> {
    let start = required_arg(args, 0, "next requires N")?
        .parse::<u64>()
        .map_err(|_| "next N must fit in the documented u64 domain".to_string())?;
    let json = args.iter().any(|arg| arg == "--json");
    if json {
        let search = next_prime_u64(start);
        println!("{}", search.to_json());
    } else if let Some(prime) = next_prime_value_u64(start) {
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
        let batch = parse_next_server_batch_request_ascii(request)?;
        write_next_server_batch_responses(&mut stdout, batch, json)?;
        stdout
            .flush()
            .map_err(|err| format!("failed to flush response: {err}"))?;
    }
    Ok(())
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum NextServerBatchRequest {
    Repeat {
        start: u64,
        repetitions: usize,
    },
    Shifted {
        start: u64,
        repetitions: usize,
        shift: u64,
    },
}

impl NextServerBatchRequest {
    fn repetitions(self) -> usize {
        match self {
            Self::Repeat { repetitions, .. } | Self::Shifted { repetitions, .. } => repetitions,
        }
    }

    fn start_at(self, index: usize) -> Result<u64, String> {
        match self {
            Self::Repeat { start, .. } => Ok(start),
            Self::Shifted { start, shift, .. } => shifted_next_server_start(start, shift, index),
        }
    }
}

fn write_next_server_batch_responses<W: Write>(
    stdout: &mut W,
    batch: NextServerBatchRequest,
    json: bool,
) -> Result<(), String> {
    for index in 0..batch.repetitions() {
        let start = batch.start_at(index)?;
        if json {
            let search = next_prime_u64(start);
            writeln!(stdout, "{}", search.to_json())
                .map_err(|err| format!("failed to write response: {err}"))?;
        } else if let Some(prime) = next_prime_value_u64(start) {
            write_u64_line(stdout, prime)?;
        } else {
            stdout
                .write_all(b"none\n")
                .map_err(|err| format!("failed to write response: {err}"))?;
        }
    }
    Ok(())
}

fn shifted_next_server_start(start: u64, shift: u64, index: usize) -> Result<u64, String> {
    let index = u64::try_from(index).map_err(|_| "shifted next-server index overflowed u64")?;
    let offset = shift
        .checked_mul(index)
        .ok_or_else(|| "shifted next-server offset overflowed u64".to_string())?;
    start
        .checked_add(offset)
        .ok_or_else(|| "shifted next-server START overflowed u64".to_string())
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

fn parse_next_server_request_count_ascii(bytes: &[u8]) -> Result<usize, String> {
    let count = parse_u64_ascii(bytes)?;
    let count =
        usize::try_from(count).map_err(|_| "next-server COUNT must fit in usize".to_string())?;
    if count == 0 {
        return Err("next-server request COUNT must be positive".to_string());
    }
    Ok(count)
}

fn parse_next_server_batch_request_ascii(
    bytes: &[u8],
) -> Result<NextServerBatchRequest, String> {
    let mut parts = bytes
        .split(|byte| matches!(byte, b' ' | b'\t'))
        .filter(|part| !part.is_empty());
    let first = parts
        .next()
        .ok_or_else(|| "next-server request must include START".to_string())?;
    if first == b"shifted" {
        let repetitions = parse_next_server_request_count_ascii(
            parts.next().ok_or_else(|| {
                "shifted next-server request must be: shifted COUNT SHIFT START".to_string()
            })?,
        )?;
        let shift = parse_u64_ascii(parts.next().ok_or_else(|| {
            "shifted next-server request must be: shifted COUNT SHIFT START".to_string()
        })?)?;
        let start = parse_u64_ascii(parts.next().ok_or_else(|| {
            "shifted next-server request must be: shifted COUNT SHIFT START".to_string()
        })?)?;
        if parts.next().is_some() {
            return Err(
                "shifted next-server request must be: shifted COUNT SHIFT START".to_string(),
            );
        }
        return Ok(NextServerBatchRequest::Shifted {
            start,
            repetitions,
            shift,
        });
    }

    let start = parse_u64_ascii(first)?;
    let repetitions = match parts.next() {
        Some(raw) if !raw.is_empty() => parse_next_server_request_count_ascii(raw)?,
        Some(_) => {
            return Err("next-server request COUNT must be positive".to_string());
        }
        None => 1,
    };
    if parts.next().is_some() {
        return Err("next-server request must be START or START COUNT".to_string());
    }
    Ok(NextServerBatchRequest::Repeat { start, repetitions })
}

fn parse_next_server_request_ascii(bytes: &[u8]) -> Result<(u64, usize), String> {
    match parse_next_server_batch_request_ascii(bytes)? {
        NextServerBatchRequest::Repeat { start, repetitions } => Ok((start, repetitions)),
        NextServerBatchRequest::Shifted { .. } => {
            Err("next-server request must be START or START COUNT".to_string())
        }
    }
}

fn parse_big_server_request(bytes: &[u8], command: &str) -> Result<(BigUint, usize), String> {
    let request =
        std::str::from_utf8(bytes).map_err(|_| format!("{command} request must be valid UTF-8"))?;
    let mut parts = request.split_whitespace();
    let n = parse_biguint(
        parts
            .next()
            .ok_or_else(|| format!("{command} request must include N"))?,
    )?;
    let repetitions = match parts.next() {
        Some(raw) if !raw.is_empty() => raw
            .parse::<usize>()
            .map_err(|_| format!("{command} COUNT must fit in usize"))?,
        Some(_) => {
            return Err(format!("{command} request COUNT must be positive"));
        }
        None => 1,
    };
    if parts.next().is_some() {
        return Err(format!("{command} request must be N or N COUNT"));
    }
    if repetitions == 0 {
        return Err(format!("{command} request COUNT must be positive"));
    }
    Ok((n, repetitions))
}

fn write_u64_line<W: Write>(writer: &mut W, mut value: u64) -> Result<(), String> {
    if value < 100 {
        let mut buffer = [0u8; 3];
        if value < 10 {
            buffer[0] = b'0' + value as u8;
            buffer[1] = b'\n';
            return writer
                .write_all(&buffer[..2])
                .map_err(|err| format!("failed to write response: {err}"));
        }
        buffer[0] = b'0' + (value / 10) as u8;
        buffer[1] = b'0' + (value % 10) as u8;
        buffer[2] = b'\n';
        return writer
            .write_all(&buffer)
            .map_err(|err| format!("failed to write response: {err}"));
    }

    let mut buffer = [0u8; 21];
    buffer[20] = b'\n';
    let mut index = 20;
    while value != 0 {
        index -= 1;
        buffer[index] = b'0' + (value % 10) as u8;
        value /= 10;
    }
    writer
        .write_all(&buffer[index..])
        .map_err(|err| format!("failed to write response: {err}"))
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
    if args.iter().any(|arg| arg == "--warm-prefix-pi-cache") {
        warm_small_prefix_pi_cache();
    }

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
        let batch_request = count_server_batch_request(request)?;
        match batch_request {
            CountServerBatchRequest::Identical {
                inner_request,
                repetitions,
            } => {
                for _ in 0..repetitions {
                    let response = count_server_response_with_pool(
                        &inner_request,
                        default_segment_size,
                        default_threads,
                        default_count_mode,
                        Some(&mut worker_pool),
                        Some(&mut plan_cache),
                    )?;
                    write_count_server_response(&mut stdout, response, json)?;
                }
            }
            CountServerBatchRequest::Shifted {
                inner_request,
                repetitions,
                shift,
            } => {
                let parsed = parse_count_server_request(&inner_request, default_threads)?;
                for response in count_server_shifted_responses_with_pool(
                    parsed,
                    default_segment_size,
                    default_count_mode,
                    Some(&mut worker_pool),
                    repetitions,
                    shift,
                )? {
                    write_count_server_response(&mut stdout, response, json)?;
                }
            }
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
    let parsed = parse_count_server_request(request, default_threads)?;
    count_server_response_for_bounds(
        parsed,
        parsed.low,
        parsed.high,
        default_segment_size,
        default_count_mode,
        worker_pool.as_deref_mut(),
        plan_cache.as_deref_mut(),
    )
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct ParsedCountServerRequest {
    low: u64,
    high: u64,
    requested_threads: usize,
    explicit_segment_size: Option<u64>,
    explicit_count_mode: Option<CountMode>,
}

fn parse_count_server_request(
    request: &str,
    default_threads: usize,
) -> Result<ParsedCountServerRequest, String> {
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
    Ok(ParsedCountServerRequest {
        low,
        high,
        requested_threads,
        explicit_segment_size,
        explicit_count_mode,
    })
}

fn count_server_response_for_bounds(
    parsed: ParsedCountServerRequest,
    low: u64,
    high: u64,
    default_segment_size: Option<u64>,
    default_count_mode: Option<CountMode>,
    mut worker_pool: Option<&mut CountServerWorkerPool>,
    mut plan_cache: Option<&mut Option<CountServerPlanCache>>,
) -> Result<CountServerResponse, String> {
    let plan = if parsed.explicit_segment_size.is_none() && parsed.explicit_count_mode.is_none() {
        count_server_cached_plan(
            low,
            high,
            parsed.requested_threads,
            default_segment_size,
            default_count_mode,
            plan_cache.as_deref_mut(),
        )
    } else {
        resolve_count_server_plan(
            low,
            high,
            parsed.requested_threads,
            parsed.explicit_segment_size,
            default_segment_size,
            parsed.explicit_count_mode,
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
        requested_threads: parsed.requested_threads,
        count_mode: plan.count_mode,
    })
}

fn count_server_shifted_responses_with_pool(
    parsed: ParsedCountServerRequest,
    default_segment_size: Option<u64>,
    default_count_mode: Option<CountMode>,
    mut worker_pool: Option<&mut CountServerWorkerPool>,
    repetitions: usize,
    shift: u64,
) -> Result<Vec<CountServerResponse>, String> {
    if repetitions == 0 {
        return Ok(Vec::new());
    }
    let (_, final_high) = shifted_bounds(parsed.low, parsed.high, shift, repetitions - 1)?;
    let mut bounds = Vec::with_capacity(repetitions);
    let mut plans = Vec::with_capacity(repetitions);
    for index in 0..repetitions {
        let (low, high) = shifted_bounds(parsed.low, parsed.high, shift, index)?;
        let plan = resolve_count_server_shifted_plan(
            low,
            high,
            final_high,
            parsed.requested_threads,
            parsed.explicit_segment_size,
            default_segment_size,
            parsed.explicit_count_mode,
            default_count_mode,
        );
        bounds.push((low, high));
        plans.push(plan);
    }

    if let (Some(pool), Some(first_plan)) = (worker_pool.as_deref_mut(), plans.first().copied()) {
        if plans.iter().all(|&plan| plan == first_plan) {
            if let Some(counts) = count_range_shifted_with_server_pool(
                pool,
                parsed.low,
                parsed.high,
                first_plan.segment_size,
                first_plan.worker_threads,
                first_plan.count_mode,
                repetitions,
                shift,
            )
            .map_err(|err| format!("range sieve failed: {err:?}"))?
            {
                return Ok(bounds
                    .into_iter()
                    .zip(counts)
                    .map(|((low, high), count)| CountServerResponse {
                        low,
                        high,
                        count,
                        segment_size: first_plan.segment_size,
                        threads: first_plan.worker_threads,
                        requested_threads: parsed.requested_threads,
                        count_mode: first_plan.count_mode,
                    })
                    .collect());
            }
        }
    }

    let mut responses = Vec::with_capacity(repetitions);
    for ((low, high), plan) in bounds.into_iter().zip(plans) {
        let count = count_range_with_mode(
            low,
            high,
            plan.segment_size,
            plan.worker_threads,
            plan.count_mode,
        )
        .map_err(|err| format!("range sieve failed: {err:?}"))?;
        responses.push(CountServerResponse {
            low,
            high,
            count,
            segment_size: plan.segment_size,
            threads: plan.worker_threads,
            requested_threads: parsed.requested_threads,
            count_mode: plan.count_mode,
        });
    }
    Ok(responses)
}

fn write_count_server_response<W: Write>(
    stdout: &mut W,
    response: CountServerResponse,
    json: bool,
) -> Result<(), String> {
    if json {
        writeln!(stdout, "{}", response.to_json())
            .map_err(|err| format!("failed to write response: {err}"))
    } else {
        writeln!(stdout, "{}", response.count)
            .map_err(|err| format!("failed to write response: {err}"))
    }
}

enum CountServerBatchRequest {
    Identical {
        inner_request: String,
        repetitions: usize,
    },
    Shifted {
        inner_request: String,
        repetitions: usize,
        shift: u64,
    },
}

fn count_server_batch_request(request: &str) -> Result<CountServerBatchRequest, String> {
    let mut fields = request.split_whitespace();
    if fields.next() != Some("shifted") {
        let (inner_request, repetitions) = count_server_repeated_request(request)?;
        return Ok(CountServerBatchRequest::Identical {
            inner_request,
            repetitions,
        });
    }
    let Some(count_field) = fields.next() else {
        return Err("shifted request must be: shifted COUNT SHIFT LOW HIGH ...".to_string());
    };
    let repetitions = count_field
        .parse::<usize>()
        .map_err(|_| "shifted COUNT must fit in usize".to_string())?;
    if repetitions == 0 {
        return Err("shifted COUNT must be positive".to_string());
    }
    let Some(shift_field) = fields.next() else {
        return Err("shifted request must be: shifted COUNT SHIFT LOW HIGH ...".to_string());
    };
    let shift = shift_field
        .parse::<u64>()
        .map_err(|_| "shifted SHIFT must fit in u64".to_string())?;
    let inner_fields = fields.collect::<Vec<_>>();
    if inner_fields.is_empty() {
        return Err("shifted request must include an inner count-server request".to_string());
    }
    Ok(CountServerBatchRequest::Shifted {
        inner_request: inner_fields.join(" "),
        repetitions,
        shift,
    })
}

#[cfg(test)]
fn count_server_shifted_inner_request(
    inner_request: &str,
    shift: u64,
    index: usize,
) -> Result<String, String> {
    let mut fields = inner_request.split_whitespace();
    let Some(low_field) = fields.next() else {
        return Err("shifted request must include LOW HIGH ...".to_string());
    };
    let Some(high_field) = fields.next() else {
        return Err("shifted request must include LOW HIGH ...".to_string());
    };
    let low = low_field
        .parse::<u64>()
        .map_err(|_| "LOW must fit in u64".to_string())?;
    let high = high_field
        .parse::<u64>()
        .map_err(|_| "HIGH must fit in u64".to_string())?;
    let (shifted_low, shifted_high) = shifted_bounds(low, high, shift, index)?;
    let mut shifted = format!("{shifted_low} {shifted_high}");
    for field in fields {
        shifted.push(' ');
        shifted.push_str(field);
    }
    Ok(shifted)
}

fn shifted_bounds(low: u64, high: u64, shift: u64, index: usize) -> Result<(u64, u64), String> {
    let index = u64::try_from(index).map_err(|_| "shifted request index overflowed u64")?;
    let delta = shift
        .checked_mul(index)
        .ok_or_else(|| "shifted request offset overflowed u64".to_string())?;
    let shifted_low = low
        .checked_add(delta)
        .ok_or_else(|| "shifted LOW overflowed u64".to_string())?;
    let shifted_high = high
        .checked_add(delta)
        .ok_or_else(|| "shifted HIGH overflowed u64".to_string())?;
    Ok((shifted_low, shifted_high))
}

fn count_server_repeated_request(request: &str) -> Result<(String, usize), String> {
    let mut fields = request.split_whitespace();
    if fields.next() != Some("repeat") {
        return Ok((request.to_string(), 1));
    }
    let Some(count_field) = fields.next() else {
        return Err("repeat request must be: repeat COUNT LOW HIGH ...".to_string());
    };
    let repetitions = count_field
        .parse::<usize>()
        .map_err(|_| "repeat COUNT must fit in usize".to_string())?;
    if repetitions == 0 {
        return Err("repeat COUNT must be positive".to_string());
    }
    let inner_fields = fields.collect::<Vec<_>>();
    if inner_fields.is_empty() {
        return Err("repeat request must include an inner count-server request".to_string());
    }
    Ok((inner_fields.join(" "), repetitions))
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

fn resolve_count_server_shifted_plan(
    low: u64,
    high: u64,
    final_high: u64,
    requested_threads: usize,
    explicit_segment_size: Option<u64>,
    default_segment_size: Option<u64>,
    explicit_count_mode: Option<CountMode>,
    default_count_mode: Option<CountMode>,
) -> CountServerPlan {
    if explicit_segment_size.is_none()
        && default_segment_size.is_none()
        && explicit_count_mode.is_none()
        && default_count_mode.is_none()
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
            let count_mode = CountMode::Presieve13;
            let segment_size = SHIFTED_EDGE_HIGH_OFFSET_SEGMENT_SIZE;
            let worker_threads = count_mode.effective_threads(
                low,
                high,
                effective_parallel_thread_count(low, high, segment_size, requested_threads),
                requested_threads,
            );
            return CountServerPlan {
                segment_size,
                worker_threads,
                count_mode,
            };
        }
        if span <= 16_000_000
            && base_limit >= PARALLEL_LOWER_HIGH_OFFSET_MIN_BASE_LIMIT
            && final_base_limit < PARALLEL_LOWER_HIGH_OFFSET_BASE_LIMIT
        {
            let count_mode = CountMode::Presieve13;
            let segment_size = SHIFTED_LOWER_HIGH_OFFSET_SEGMENT_SIZE;
            let worker_threads = count_mode.effective_threads(
                low,
                high,
                effective_parallel_thread_count(low, high, segment_size, requested_threads),
                requested_threads,
            );
            return CountServerPlan {
                segment_size,
                worker_threads,
                count_mode,
            };
        }
    }

    resolve_count_server_plan(
        low,
        high,
        requested_threads,
        explicit_segment_size,
        default_segment_size,
        explicit_count_mode,
        default_count_mode,
    )
}

struct CountServerWorkerPool {
    senders: Vec<mpsc::Sender<CountServerWorkerCommand>>,
    handles: Vec<JoinHandle<()>>,
    result_sender: mpsc::Sender<Result<CountServerWorkerReply, circle_prime::RangeError>>,
    result_receiver: mpsc::Receiver<Result<CountServerWorkerReply, circle_prime::RangeError>>,
    caller_scratch: PrimeCountScratch,
}

impl CountServerWorkerPool {
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
        count_mode: CountMode,
    ) -> Result<usize, circle_prime::RangeError> {
        let Some((&caller_chunk, worker_chunks)) = chunks.split_first() else {
            return Ok(0);
        };

        self.ensure_worker_count(worker_chunks.len());
        for (worker_index, &(low, high)) in worker_chunks.iter().enumerate() {
            self.senders[worker_index]
                .send(CountServerWorkerCommand::Count {
                    low,
                    high,
                    segment_size,
                    count_mode,
                })
                .map_err(|_| circle_prime::RangeError::WorkerPanic)?;
        }

        let mut total = count_range_with_mode_scratch(
            caller_chunk.0,
            caller_chunk.1,
            segment_size,
            1,
            count_mode,
            &mut self.caller_scratch,
        )?;
        for _ in worker_chunks {
            match self
                .result_receiver
                .recv()
                .map_err(|_| circle_prime::RangeError::WorkerPanic)??
            {
                CountServerWorkerReply::Count(count) => total += count,
                CountServerWorkerReply::Shifted(_) => {
                    return Err(circle_prime::RangeError::WorkerPanic);
                }
            }
        }
        Ok(total)
    }

    fn count_shifted_chunks(
        &mut self,
        chunks: &[(u64, u64)],
        segment_size: u64,
        count_mode: CountMode,
        repetitions: usize,
        shift: u64,
    ) -> Result<Vec<usize>, circle_prime::RangeError> {
        let Some((&caller_chunk, worker_chunks)) = chunks.split_first() else {
            return Ok(vec![0; repetitions]);
        };

        self.ensure_worker_count(worker_chunks.len());
        for (worker_index, &(low, high)) in worker_chunks.iter().enumerate() {
            self.senders[worker_index]
                .send(CountServerWorkerCommand::ShiftedCount {
                    low,
                    high,
                    segment_size,
                    count_mode,
                    repetitions,
                    shift,
                })
                .map_err(|_| circle_prime::RangeError::WorkerPanic)?;
        }

        let mut totals = count_shifted_range_with_mode_scratch(
            caller_chunk.0,
            caller_chunk.1,
            segment_size,
            count_mode,
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
                CountServerWorkerReply::Shifted(counts) => {
                    if counts.len() != totals.len() {
                        return Err(circle_prime::RangeError::WorkerPanic);
                    }
                    for (total, count) in totals.iter_mut().zip(counts) {
                        *total += count;
                    }
                }
                CountServerWorkerReply::Count(_) => {
                    return Err(circle_prime::RangeError::WorkerPanic)
                }
            }
        }
        Ok(totals)
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
    ShiftedCount {
        low: u64,
        high: u64,
        segment_size: u64,
        count_mode: CountMode,
        repetitions: usize,
        shift: u64,
    },
    Stop,
}

enum CountServerWorkerReply {
    Count(usize),
    Shifted(Vec<usize>),
}

fn count_server_worker_loop(
    receiver: mpsc::Receiver<CountServerWorkerCommand>,
    result_sender: mpsc::Sender<Result<CountServerWorkerReply, circle_prime::RangeError>>,
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
                let _ = result_sender.send(result.map(CountServerWorkerReply::Count));
            }
            CountServerWorkerCommand::ShiftedCount {
                low,
                high,
                segment_size,
                count_mode,
                repetitions,
                shift,
            } => {
                let result = count_shifted_range_with_mode_scratch(
                    low,
                    high,
                    segment_size,
                    count_mode,
                    repetitions,
                    shift,
                    &mut scratch,
                );
                let _ = result_sender.send(result.map(CountServerWorkerReply::Shifted));
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
    if mode == CountMode::PrefixPi {
        return Ok(prime_count_in_range_small_prefix_pi(low, high));
    }
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

fn count_range_shifted_with_server_pool(
    pool: &mut CountServerWorkerPool,
    low: u64,
    high: u64,
    segment_size: u64,
    worker_threads: usize,
    mode: CountMode,
    repetitions: usize,
    shift: u64,
) -> Result<Option<Vec<usize>>, circle_prime::RangeError> {
    if repetitions == 0 {
        return Ok(Some(Vec::new()));
    }
    if mode == CountMode::PrefixPi {
        let mut counts = Vec::with_capacity(repetitions);
        for index in 0..repetitions {
            let (request_low, request_high) = shifted_bounds_range_error(low, high, shift, index)?;
            counts.push(
                prime_count_in_range_small_prefix_pi(request_low, request_high)
                    .ok_or(circle_prime::RangeError::BaseLimitTooLarge)?,
            );
        }
        return Ok(Some(counts));
    }
    if worker_threads <= 1
        || high <= low
        || segment_size == 0
        || !mode.supports_server_worker_pool()
    {
        return Ok(None);
    }
    let (_, final_high) = shifted_bounds_range_error(low, high, shift, repetitions - 1)?;
    if (final_high - 1).isqrt() > BASE_PRIME_CACHE_LIMIT {
        return Ok(None);
    }

    let chunks = split_range_evenly(low, high, worker_threads);
    if chunks.len() <= 1 {
        return Ok(None);
    }
    pool.count_shifted_chunks(&chunks, segment_size, mode, repetitions, shift)
        .map(Some)
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
        let (request_low, request_high) = shifted_bounds_range_error(low, high, shift, index)?;
        counts.push(count_range_with_mode_scratch(
            request_low,
            request_high,
            segment_size,
            1,
            mode,
            scratch,
        )?);
    }
    Ok(counts)
}

fn shifted_bounds_range_error(
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
        "  circle-prime big-test N [--profile mr|bpsw] [--rounds N] [--json]",
        "  circle-prime big-next START [--profile mr|bpsw] [--rounds N] [--max-candidates N] [--json]",
        "  circle-prime big-fuzzy-search MODEL START [--candidate-window N] [--top-k N] [--score-limit N] [--rounds N] [--json]",
        "  circle-prime big-test-server [--profile mr|bpsw] [--rounds N] [--json]",
        "  circle-prime big-next-server [--profile mr|bpsw] [--rounds N] [--max-candidates N] [--json]",
        "  circle-prime big-fuzzy-server MODEL [--candidate-window N] [--top-k N] [--score-limit N] [--rounds N] [--json]",
        "  circle-prime fuzzy-search MODEL START [--mode exact-next|any-prime] [--window N] [--top-k N] [--json]",
        "  circle-prime fuzzy-server MODEL [--mode exact-next|any-prime] [--window N] [--top-k N] [--json]",
        "  circle-prime recommend LOW HIGH [--count] [--json] [--threads N]",
        "  circle-prime range LOW HIGH [--count] [--json] [--segment-size N] [--threads N] [--count-mode MODE]",
        "  circle-prime count-server [--segment-size N] [--threads N] [--count-mode MODE] [--warm-prefix-pi-cache] [--json]",
        "",
        "next-server reads START, START COUNT, or shifted COUNT SHIFT START lines from stdin and writes one next prime, none, or JSON object per requested search.",
        "big-test-server, big-next-server, and big-fuzzy-server read N or N COUNT lines from stdin and keep the arbitrary-precision engine hot between requests.",
        "big-test/big-next use arbitrary-precision BigUint arithmetic. --profile mr uses fixed Miller-Rabin bases; --profile bpsw uses base-2 Miller-Rabin plus strong Lucas-Selfridge. Results above u64 are probable-prime decisions, not formal primality certificates.",
        "big-fuzzy-search uses a tiny bit/residue model only to rank arbitrary-precision candidates; every reported candidate still passes the configured BigUint probable-prime verifier.",
        "fuzzy-search/fuzzy-server read a tiny exported model, use it only to rank candidates, and accept reported primes only after deterministic verification. exact-next mode also verifies every earlier candidate in the bounded window.",
        "count-server reads LOW HIGH [SEGMENT_SIZE] [THREADS] [COUNT_MODE], repeat COUNT LOW HIGH ..., or shifted COUNT SHIFT LOW HIGH ... lines from stdin and writes one count or JSON object per requested count. --warm-prefix-pi-cache prebuilds the reusable small-prefix pi table before reading requests.",
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
        assert_eq!(
            count_server_repeated_request("repeat 3 0 1000 64 1 segmented").unwrap(),
            ("0 1000 64 1 segmented".to_string(), 3)
        );
        match count_server_batch_request("shifted 3 1000 0 1000 64 1 segmented").unwrap() {
            CountServerBatchRequest::Shifted {
                inner_request,
                repetitions,
                shift,
            } => {
                assert_eq!(inner_request, "0 1000 64 1 segmented");
                assert_eq!(repetitions, 3);
                assert_eq!(shift, 1000);
            }
            CountServerBatchRequest::Identical { .. } => {
                panic!("shifted request should parse as shifted")
            }
        }
        assert_eq!(
            count_server_shifted_inner_request("0 1000 64 1 segmented", 1000, 2).unwrap(),
            "2000 3000 64 1 segmented"
        );
        assert!(count_server_repeated_request("repeat 0 0 1000").is_err());
        assert!(count_server_repeated_request("repeat 3").is_err());
        assert!(count_server_batch_request("shifted 0 1000 0 1000").is_err());
        assert!(count_server_batch_request("shifted 3").is_err());
        assert!(count_server_shifted_inner_request(
            "18446744073709551615 18446744073709551615",
            1,
            1
        )
        .is_err());
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
    fn count_server_shifted_batch_uses_worker_pool_and_matches_direct_counts() {
        let mut pool = CountServerWorkerPool::new();
        let parsed =
            parse_count_server_request("0 100000 65536 4 presieve13", 1).expect("valid request");
        let responses = count_server_shifted_responses_with_pool(
            parsed,
            None,
            None,
            Some(&mut pool),
            3,
            10_000,
        )
        .expect("shifted batch should succeed");

        assert_eq!(
            responses
                .iter()
                .map(|response| (response.low, response.high))
                .collect::<Vec<_>>(),
            vec![(0, 100_000), (10_000, 110_000), (20_000, 120_000)]
        );
        for response in responses {
            let direct = count_range_with_mode(
                response.low,
                response.high,
                response.segment_size,
                response.threads,
                response.count_mode,
            )
            .expect("direct count should succeed");
            assert_eq!(response.count, direct);
        }
    }

    #[test]
    fn shifted_default_plan_uses_measured_edge_high_offset_candidate() {
        let low = 1_000_000_000_000;
        let high = 1_000_010_000_000;
        let final_high = high + 79 * 10_000_000;

        let normal = resolve_count_server_plan(low, high, 8, None, None, None, None);
        let shifted =
            resolve_count_server_shifted_plan(low, high, final_high, 8, None, None, None, None);

        assert_eq!(normal.segment_size, 1_310_720);
        assert_eq!(normal.worker_threads, 8);
        assert_eq!(normal.count_mode, CountMode::Presieve13);
        assert_eq!(shifted.segment_size, SHIFTED_EDGE_HIGH_OFFSET_SEGMENT_SIZE);
        assert_eq!(shifted.worker_threads, 7);
        assert_eq!(shifted.count_mode, CountMode::Presieve13);
    }

    #[test]
    fn shifted_default_plan_respects_explicit_overrides_and_lower_band() {
        let edge_low = 1_000_000_000_000;
        let edge_high = 1_000_010_000_000;
        let edge_final_high = edge_high + 79 * 10_000_000;
        let explicit = resolve_count_server_shifted_plan(
            edge_low,
            edge_high,
            edge_final_high,
            8,
            Some(65_536),
            None,
            Some(CountMode::Segmented),
            None,
        );
        assert_eq!(explicit.segment_size, 65_536);
        assert_eq!(explicit.count_mode, CountMode::Segmented);

        let lower_low = 1_500_000_000_000;
        let lower_high = 1_500_010_000_000;
        let lower_final_high = lower_high + 79 * 10_000_000;
        let lower = resolve_count_server_shifted_plan(
            lower_low,
            lower_high,
            lower_final_high,
            8,
            None,
            None,
            None,
            None,
        );
        assert_eq!(lower.segment_size, SHIFTED_LOWER_HIGH_OFFSET_SEGMENT_SIZE);
        assert_eq!(lower.worker_threads, 6);
        assert_eq!(lower.count_mode, CountMode::Presieve13);
    }

    #[test]
    fn shifted_worker_pool_declines_when_last_shift_exceeds_base_cache() {
        let mut pool = CountServerWorkerPool::new();
        let cache_boundary_square = BASE_PRIME_CACHE_LIMIT * BASE_PRIME_CACHE_LIMIT;
        let low = cache_boundary_square - 3_000_000;
        let high = cache_boundary_square + 1;
        let next_square_gap = 2 * BASE_PRIME_CACHE_LIMIT + 1;

        assert_eq!((high - 1).isqrt(), BASE_PRIME_CACHE_LIMIT);
        assert!((high + next_square_gap - 1).isqrt() > BASE_PRIME_CACHE_LIMIT);

        let result = count_range_shifted_with_server_pool(
            &mut pool,
            low,
            high,
            1_500_000,
            2,
            CountMode::Presieve13,
            2,
            next_square_gap,
        )
        .expect("eligibility check should not fail");

        assert_eq!(result, None);
    }

    #[test]
    fn shifted_worker_pool_declines_empty_range_before_final_high_check() {
        let mut pool = CountServerWorkerPool::new();

        let result = count_range_shifted_with_server_pool(
            &mut pool,
            0,
            0,
            65_536,
            4,
            CountMode::Presieve13,
            2,
            1,
        )
        .expect("empty range should decline worker pool without underflow");

        assert_eq!(result, None);
    }

    #[test]
    fn next_server_ascii_parser_trims_and_rejects_invalid_requests() {
        assert_eq!(trim_ascii_bytes(b" \t90\r\n"), b"90");
        assert_eq!(parse_u64_ascii(trim_ascii_bytes(b" \t90\r\n")).unwrap(), 90);
        assert_eq!(parse_u64_ascii(b"18446744073709551615").unwrap(), u64::MAX);
        assert_eq!(parse_next_server_request_ascii(b"90").unwrap(), (90, 1));
        assert_eq!(parse_next_server_request_ascii(b"90 50").unwrap(), (90, 50));
        assert_eq!(
            parse_next_server_request_ascii(b"90   50").unwrap(),
            (90, 50)
        );
        assert_eq!(
            parse_next_server_batch_request_ascii(b"shifted 3 10 90").unwrap(),
            NextServerBatchRequest::Shifted {
                start: 90,
                repetitions: 3,
                shift: 10
            }
        );
        assert_eq!(
            shifted_next_server_start(90, 10, 2).expect("shifted start should fit"),
            110
        );
        assert!(parse_u64_ascii(b"").is_err());
        assert!(parse_u64_ascii(b"12x").is_err());
        assert!(parse_u64_ascii(b"18446744073709551616").is_err());
        assert!(parse_next_server_request_ascii(b"90 0").is_err());
        assert!(parse_next_server_request_ascii(b"90 50 extra").is_err());
        assert!(parse_next_server_batch_request_ascii(b"shifted 0 10 90").is_err());
        assert!(parse_next_server_batch_request_ascii(b"shifted 3 10").is_err());
        assert!(shifted_next_server_start(u64::MAX, 1, 1).is_err());
    }

    #[test]
    fn next_server_u64_writer_matches_decimal_lines() {
        for value in [0, 7, 97, 1000, u64::MAX] {
            let mut output = Vec::new();
            write_u64_line(&mut output, value).expect("u64 line write should succeed");
            assert_eq!(output, format!("{value}\n").as_bytes(), "value={value}");
        }
    }
}
