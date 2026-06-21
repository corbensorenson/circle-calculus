use std::env;
use std::fs;
use std::path::PathBuf;

const PRESIEVE13_MODULUS: usize = 30_030;
const PRESIEVE13_ODD_PERIOD: usize = PRESIEVE13_MODULUS / 2;
const PRESIEVE17_MODULUS: usize = 510_510;
const PRESIEVE17_ODD_PERIOD: usize = PRESIEVE17_MODULUS / 2;
const STATIC_BASE_PRIME_LIMIT: usize = 1_010_000;
const STATIC_BASE_PRIME_INDEX_BLOCK_SIZE: usize = 1024;

fn main() {
    let out_dir = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR is set by Cargo"));
    write_presieve13_table(&out_dir);
    write_presieve17_table(&out_dir);
    write_prime_pi_phi_prefix_tables(&out_dir);
    write_static_base_prime_table(&out_dir);
    write_prime_engine_defaults(&out_dir);
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed=prime_engine_defaults.json");
}

fn write_presieve13_table(out_dir: &PathBuf) {
    let path = out_dir.join("presieve_3_5_7_11_13.bin");
    let mut pattern = Vec::with_capacity(PRESIEVE13_ODD_PERIOD);

    for index in 0..PRESIEVE13_ODD_PERIOD {
        let residue = 1 + 2 * index;
        pattern.push(u8::from(
            residue % 3 != 0
                && residue % 5 != 0
                && residue % 7 != 0
                && residue % 11 != 0
                && residue % 13 != 0,
        ));
    }

    fs::write(path, pattern).expect("write generated pre-sieve 13 table");
}

fn write_presieve17_table(out_dir: &PathBuf) {
    let path = out_dir.join("presieve_3_5_7_11_13_17.bin");
    let mut pattern = Vec::with_capacity(PRESIEVE17_ODD_PERIOD);

    for index in 0..PRESIEVE17_ODD_PERIOD {
        let residue = 1 + 2 * index;
        pattern.push(u8::from(
            residue % 3 != 0
                && residue % 5 != 0
                && residue % 7 != 0
                && residue % 11 != 0
                && residue % 13 != 0
                && residue % 17 != 0,
        ));
    }

    fs::write(path, pattern).expect("write generated pre-sieve 17 table");
}

fn write_prime_pi_phi_prefix_tables(out_dir: &PathBuf) {
    let phi6 = prefix_counts_u16(PRESIEVE13_MODULUS, &[2, 3, 5, 7, 11, 13]);
    fs::write(out_dir.join("prime_pi_phi6_prefix_u16.bin"), phi6)
        .expect("write generated phi6 prefix table");

    let phi7 = prefix_counts_u32(PRESIEVE17_MODULUS, &[2, 3, 5, 7, 11, 13, 17]);
    fs::write(out_dir.join("prime_pi_phi7_prefix_u32.bin"), phi7)
        .expect("write generated phi7 prefix table");
}

fn prefix_counts_u16(modulus: usize, primes: &[usize]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity((modulus + 1) * 2);
    let mut count = 0u16;
    bytes.extend_from_slice(&count.to_le_bytes());
    for value in 1..=modulus {
        if primes.iter().all(|&prime| value % prime != 0) {
            count += 1;
        }
        bytes.extend_from_slice(&count.to_le_bytes());
    }
    bytes
}

fn prefix_counts_u32(modulus: usize, primes: &[usize]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity((modulus + 1) * 4);
    let mut count = 0u32;
    bytes.extend_from_slice(&count.to_le_bytes());
    for value in 1..=modulus {
        if primes.iter().all(|&prime| value % prime != 0) {
            count += 1;
        }
        bytes.extend_from_slice(&count.to_le_bytes());
    }
    bytes
}

fn write_static_base_prime_table(out_dir: &PathBuf) {
    fs::write(
        out_dir.join("base_prime_static_metadata.rs"),
        format!(
            "pub(crate) const STATIC_BASE_PRIME_LIMIT: u64 = {STATIC_BASE_PRIME_LIMIT};\n\
pub(crate) const STATIC_BASE_PRIME_INDEX_BLOCK_SIZE: usize = {STATIC_BASE_PRIME_INDEX_BLOCK_SIZE};\n"
        ),
    )
    .expect("write generated base-prime static metadata");

    let mut sieve = vec![true; STATIC_BASE_PRIME_LIMIT + 1];
    sieve[0] = false;
    sieve[1] = false;

    let mut p = 2usize;
    while p * p <= STATIC_BASE_PRIME_LIMIT {
        if sieve[p] {
            let mut multiple = p * p;
            while multiple <= STATIC_BASE_PRIME_LIMIT {
                sieve[multiple] = false;
                multiple += p;
            }
        }
        p += 1;
    }

    let primes: Vec<usize> = sieve
        .into_iter()
        .enumerate()
        .filter_map(|(n, is_prime)| is_prime.then_some(n))
        .collect();

    let mut rust_table_u64 =
        String::from("pub(crate) static STATIC_BASE_PRIMES_U64: &[u64] = &[\n");
    for prime in &primes {
        rust_table_u64.push_str("    ");
        rust_table_u64.push_str(&prime.to_string());
        rust_table_u64.push_str(",\n");
    }
    rust_table_u64.push_str("];\n");

    fs::write(out_dir.join("base_primes_static_u64.rs"), rust_table_u64)
        .expect("write generated u64 base-prime Rust table");

    let block_count = STATIC_BASE_PRIME_LIMIT / STATIC_BASE_PRIME_INDEX_BLOCK_SIZE + 2;
    let mut prime_index = 0usize;
    let mut rust_index =
        String::from("pub(crate) static STATIC_BASE_PRIME_INDEX_BY_1024_BLOCK: &[u32] = &[\n");
    for block in 0..block_count {
        let block_start = block * STATIC_BASE_PRIME_INDEX_BLOCK_SIZE;
        while prime_index < primes.len() && primes[prime_index] < block_start {
            prime_index += 1;
        }
        rust_index.push_str("    ");
        rust_index.push_str(&prime_index.to_string());
        rust_index.push_str(",\n");
    }
    rust_index.push_str("];\n");

    fs::write(
        out_dir.join("base_prime_static_index_by_1024_block.rs"),
        rust_index,
    )
    .expect("write generated base-prime block index");
}

fn write_prime_engine_defaults(out_dir: &PathBuf) {
    let defaults =
        fs::read_to_string("prime_engine_defaults.json").expect("read prime_engine_defaults.json");
    let tiny = json_u64(&defaults, "parallel_tiny_prefix_segment_size");
    let small = json_u64(&defaults, "parallel_small_prefix_segment_size");
    let medium = json_u64(&defaults, "parallel_medium_prefix_segment_size");
    let edge_high_min_base_limit = json_u64(&defaults, "parallel_edge_high_offset_min_base_limit");
    let edge_high = json_u64(&defaults, "parallel_edge_high_offset_segment_size");
    let lower_high_base_limit = json_u64(&defaults, "parallel_lower_high_offset_base_limit");
    let lower_high_min_base_limit =
        json_u64(&defaults, "parallel_lower_high_offset_min_base_limit");
    let upper_high_min_base_limit =
        json_u64(&defaults, "parallel_upper_high_offset_min_base_limit");
    let upper_high = json_u64(&defaults, "parallel_upper_high_offset_segment_size");
    let very_high = json_u64(&defaults, "parallel_very_high_offset_segment_size");
    let tiny_mode = json_count_mode(&defaults, "parallel_tiny_prefix_count_mode");
    let small_mode = json_count_mode(&defaults, "parallel_small_prefix_count_mode");
    let medium_mode = json_count_mode(&defaults, "parallel_medium_prefix_count_mode");
    let edge_high_mode = json_count_mode(&defaults, "parallel_edge_high_offset_count_mode");
    let lower_high_mode = json_count_mode(&defaults, "parallel_lower_high_offset_count_mode");
    let upper_high_mode = json_count_mode(&defaults, "parallel_upper_high_offset_count_mode");
    let very_high_mode = json_count_mode(&defaults, "parallel_very_high_offset_count_mode");
    let rendered = format!(
        "\
pub const PARALLEL_EDGE_HIGH_OFFSET_COUNT_MODE: &str = \"{edge_high_mode}\";
pub const PARALLEL_EDGE_HIGH_OFFSET_MIN_BASE_LIMIT: u64 = {edge_high_min_base_limit};
pub const PARALLEL_EDGE_HIGH_OFFSET_SEGMENT_SIZE: u64 = {edge_high};
pub const PARALLEL_LOWER_HIGH_OFFSET_BASE_LIMIT: u64 = {lower_high_base_limit};
pub const PARALLEL_LOWER_HIGH_OFFSET_COUNT_MODE: &str = \"{lower_high_mode}\";
pub const PARALLEL_LOWER_HIGH_OFFSET_MIN_BASE_LIMIT: u64 = {lower_high_min_base_limit};
pub const PARALLEL_UPPER_HIGH_OFFSET_COUNT_MODE: &str = \"{upper_high_mode}\";
pub const PARALLEL_UPPER_HIGH_OFFSET_MIN_BASE_LIMIT: u64 = {upper_high_min_base_limit};
pub const PARALLEL_UPPER_HIGH_OFFSET_SEGMENT_SIZE: u64 = {upper_high};
pub const PARALLEL_TINY_PREFIX_COUNT_MODE: &str = \"{tiny_mode}\";
pub const PARALLEL_TINY_PREFIX_SEGMENT_SIZE: u64 = {tiny};
pub const PARALLEL_SMALL_PREFIX_COUNT_MODE: &str = \"{small_mode}\";
pub const PARALLEL_SMALL_PREFIX_SEGMENT_SIZE: u64 = {small};
pub const PARALLEL_MEDIUM_PREFIX_COUNT_MODE: &str = \"{medium_mode}\";
pub const PARALLEL_MEDIUM_PREFIX_SEGMENT_SIZE: u64 = {medium};
pub const PARALLEL_VERY_HIGH_OFFSET_COUNT_MODE: &str = \"{very_high_mode}\";
pub const PARALLEL_VERY_HIGH_OFFSET_SEGMENT_SIZE: u64 = {very_high};
"
    );
    fs::write(out_dir.join("prime_engine_defaults.rs"), rendered)
        .expect("write generated prime engine defaults");
}

fn json_u64(document: &str, key: &str) -> u64 {
    let quoted_key = format!("\"{key}\"");
    let key_start = document
        .find(&quoted_key)
        .unwrap_or_else(|| panic!("missing {key} in prime_engine_defaults.json"));
    let after_key = &document[key_start + quoted_key.len()..];
    let colon = after_key
        .find(':')
        .unwrap_or_else(|| panic!("missing ':' after {key} in prime_engine_defaults.json"));
    let value_start = key_start + quoted_key.len() + colon + 1;
    let value = document[value_start..].trim_start();
    let end = value
        .find(|ch: char| !ch.is_ascii_digit())
        .unwrap_or(value.len());
    if end == 0 {
        panic!("{key} must be an integer in prime_engine_defaults.json");
    }
    value[..end]
        .parse()
        .unwrap_or_else(|_| panic!("{key} must fit in u64"))
}

fn json_count_mode(document: &str, key: &str) -> String {
    let value = json_string(document, key);
    match value.as_str() {
        "segmented" | "balanced" | "dynamic" | "prefix-pi" | "presieve13" | "presieve17"
        | "wheel30-mark" | "hybrid-wheel30-mark" => value,
        _ => panic!(
            "{key} must be one of segmented, balanced, dynamic, prefix-pi, presieve13, presieve17, wheel30-mark, hybrid-wheel30-mark"
        ),
    }
}

fn json_string(document: &str, key: &str) -> String {
    let quoted_key = format!("\"{key}\"");
    let key_start = document
        .find(&quoted_key)
        .unwrap_or_else(|| panic!("missing {key} in prime_engine_defaults.json"));
    let after_key = &document[key_start + quoted_key.len()..];
    let colon = after_key
        .find(':')
        .unwrap_or_else(|| panic!("missing ':' after {key} in prime_engine_defaults.json"));
    let value_start = key_start + quoted_key.len() + colon + 1;
    let value = document[value_start..].trim_start();
    let Some(rest) = value.strip_prefix('"') else {
        panic!("{key} must be a string in prime_engine_defaults.json");
    };
    let Some(end) = rest.find('"') else {
        panic!("{key} must be a terminated string in prime_engine_defaults.json");
    };
    rest[..end].to_string()
}
