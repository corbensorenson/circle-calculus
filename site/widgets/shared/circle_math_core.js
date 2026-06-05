export function positiveInt(value, fallback, min = 1, max = 96) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, parsed));
}

export function mod(value, n) {
  return ((value % n) + n) % n;
}

export function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y !== 0) {
    const next = x % y;
    x = y;
    y = next;
  }
  return x;
}

export function rot(n, k, x) {
  return mod(x + k, n);
}

export function period(n, k) {
  return n / gcd(n, k);
}

export function orbit(n, stride, start) {
  const seen = new Set();
  const out = [];
  let x = mod(start, n);
  while (!seen.has(x)) {
    seen.add(x);
    out.push(x);
    x = rot(n, stride, x);
  }
  return out;
}

export function orbitDecomposition(n, stride) {
  const remaining = new Set(Array.from({ length: n }, (_, i) => i));
  const cycles = [];
  while (remaining.size > 0) {
    const start = Math.min(...remaining);
    const cycle = orbit(n, stride, start);
    cycles.push(cycle);
    for (const node of cycle) remaining.delete(node);
  }
  return cycles;
}

export function isPrime(n) {
  if (n < 2) return false;
  for (let d = 2; d * d <= n; d += 1) {
    if (n % d === 0) return false;
  }
  return true;
}

export function windingLift(n, value) {
  const q = Math.floor(value / n);
  const r = mod(value, n);
  return { q, r, value: q * n + r };
}
