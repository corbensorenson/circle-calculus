# Python Reference Model and Tests

Python is for executable sanity checks, examples, visualizations, and manifest validation. Python is not the proof layer.

## Reference model

Recommended `circle_math/finite.py`:

```python
from dataclasses import dataclass
from math import gcd
from typing import Iterator, List

@dataclass(frozen=True)
class Circle:
    n: int

    def __post_init__(self) -> None:
        if self.n <= 0:
            raise ValueError("v0 finite circles require n > 0")

    def node(self, i: int) -> int:
        return i % self.n

    def rot(self, i: int, k: int) -> int:
        return (i + k) % self.n

    def orbit(self, start: int, stride: int) -> List[int]:
        out = []
        seen = set()
        x = self.node(start)
        while x not in seen:
            seen.add(x)
            out.append(x)
            x = self.rot(x, stride)
        return out

    def period(self, stride: int) -> int:
        return self.n // gcd(self.n, stride)

    def is_full_coil(self, stride: int) -> bool:
        return gcd(self.n, stride) == 1
```

## Required tests

### Rotation

For all `1 <= n <= 128` and bounded `a,b,i`:

```text
rot(n,0,i) == i mod n
rot(n,a,rot(n,b,i)) == rot(n,a+b,i)
rot(n,-a,rot(n,a,i)) == i mod n
```

### Period

For all `1 <= n <= 128` and `0 <= k <= 256`:

```text
len(orbit(n,0,k)) == n // gcd(n,k)
period(n,k) == n // gcd(n,k)
```

### Orbit decomposition

For all `1 <= n <= 96` and `0 <= k <= 192`:

```text
number_of_distinct_orbits(n,k) == gcd(n,k)
all_orbits_have_length(n // gcd(n,k))
orbits_partition_nodes
```

### Prime full coils

For primes `p <= 257`:

```text
for all 1 <= k < p:
    is_full_coil(p,k) is True
    len(orbit(p,0,k)) == p
```

For composites `n <= 256`, there should exist at least one nonzero stride `k < n` that is not full.

### Scaling

Define:

```text
scale(n,k,i) = k*i mod n
```

Test:

```text
scale is permutation of nodes iff gcd(n,k)=1
```

## Visualization smoke tests

`render_examples.py` should generate deterministic SVG or PNG outputs for:

```text
C_12 stride 5
C_12 stride 4
C_13 stride 5
C_36 factor/subcoil display
```

Visual outputs are checked only for generation success and stable filenames, not for mathematical proof.
