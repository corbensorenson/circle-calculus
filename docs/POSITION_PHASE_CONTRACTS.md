# Position Phase Contracts

Claim boundary: this note records exact finite integer phase-bank contracts. It
does not claim real-valued RoPE, xPos, YaRN, LongRoPE, or 2D RoPE performance,
model quality, or continuous phase-margin guarantees.

`Circle.Applications.PositionPhase` factors the integer residue layer out of
the RoPE-specific certifier. A phase channel is represented by a declared
period, and a position is observed by its residue modulo that period. This
gives a reusable proof surface for positional encodings that can export
declared finite periods.

The proved layer covers:

- single-channel collision iff the declared period divides the ordered gap;
- single-channel distinguishability iff the declared period does not divide
  the ordered gap;
- injectivity inside a context that fits within one declared period;
- phase-bank collision iff every declared period divides the ordered gap;
- phase-bank distinguishability iff some declared period does not divide the
  ordered gap;
- distinguishability when the bank contains a period at least as large as the
  inspected context;
- monotonicity of collision and distinguishability under adding channels;
- 2D grid collision as conjunction of the two axis banks;
- positive scale preserving positive declared periods.

These theorems are useful as a generic contract vocabulary for AI architecture
receipts. Numerical or real-valued phase-margin claims must stay in the RoPE
frontier/certifier layer and must not be upgraded to these exact integer
claims.
