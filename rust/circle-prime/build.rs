use std::env;
use std::fs;
use std::path::PathBuf;

const PRESIEVE13_MODULUS: usize = 30_030;
const PRESIEVE13_ODD_PERIOD: usize = PRESIEVE13_MODULUS / 2;
const PRESIEVE19_MODULUS: usize = 9_699_690;
const PRESIEVE19_ODD_PERIOD: usize = PRESIEVE19_MODULUS / 2;
const STATIC_BASE_PRIME_LIMIT: usize = 1_100_000;

fn main() {
    let out_dir = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR is set by Cargo"));
    write_presieve13_table(&out_dir);
    write_presieve19_table(&out_dir);
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

fn write_presieve19_table(out_dir: &PathBuf) {
    let path = out_dir.join("presieve_3_5_7_11_13_17_19.bin");
    let mut pattern = Vec::with_capacity(PRESIEVE19_ODD_PERIOD);

    for index in 0..PRESIEVE19_ODD_PERIOD {
        let residue = 1 + 2 * index;
        pattern.push(u8::from(
            residue % 3 != 0
                && residue % 5 != 0
                && residue % 7 != 0
                && residue % 11 != 0
                && residue % 13 != 0
                && residue % 17 != 0
                && residue % 19 != 0,
        ));
    }

    fs::write(path, pattern).expect("write generated pre-sieve 19 table");
}

fn write_static_base_prime_table(out_dir: &PathBuf) {
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

    let mut bytes = Vec::new();
    let mut rust_table = String::from("static STATIC_BASE_PRIMES_U32: &[u32] = &[\n");
    for (n, is_prime) in sieve.into_iter().enumerate() {
        if is_prime {
            bytes.extend_from_slice(&(n as u32).to_le_bytes());
            rust_table.push_str("    ");
            rust_table.push_str(&n.to_string());
            rust_table.push_str(",\n");
        }
    }
    rust_table.push_str("];\n");

    fs::write(out_dir.join("base_primes_upto_1100000_u32le.bin"), bytes)
        .expect("write generated base-prime binary table");
    fs::write(out_dir.join("base_primes_upto_1100000_u32.rs"), rust_table)
        .expect("write generated base-prime Rust table");
}

fn write_prime_engine_defaults(out_dir: &PathBuf) {
    let defaults =
        fs::read_to_string("prime_engine_defaults.json").expect("read prime_engine_defaults.json");
    let tiny = json_u64(&defaults, "parallel_tiny_prefix_segment_size");
    let small = json_u64(&defaults, "parallel_small_prefix_segment_size");
    let medium = json_u64(&defaults, "parallel_medium_prefix_segment_size");
    let very_high = json_u64(&defaults, "parallel_very_high_offset_segment_size");
    let tiny_mode = json_count_mode(&defaults, "parallel_tiny_prefix_count_mode");
    let small_mode = json_count_mode(&defaults, "parallel_small_prefix_count_mode");
    let medium_mode = json_count_mode(&defaults, "parallel_medium_prefix_count_mode");
    let very_high_mode = json_count_mode(&defaults, "parallel_very_high_offset_count_mode");
    let rendered = format!(
        "\
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
        "segmented" | "balanced" | "dynamic" | "presieve13" | "wheel30-mark"
        | "hybrid-wheel30-mark" => value,
        _ => panic!(
            "{key} must be one of segmented, balanced, dynamic, presieve13, wheel30-mark, hybrid-wheel30-mark"
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
