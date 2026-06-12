# Paper Rules and Template

## Hard rule

A theorem appearing in a paper must be one of:

1. Informal motivation, clearly labeled as intuition.
2. A standard known theorem cited as background.
3. A Circle Calculus theorem with a theorem manifest id and Lean theorem name.
4. A conjecture, clearly labeled as conjecture.
5. A future target, clearly labeled as deferred.

No theorem may be presented as established unless it is `proved` in `theorem_manifest.yaml`.

## Template

```markdown
# Paper N — Title

## Abstract

State the contribution and the exact formal scope.

## Status

- Dictionary version:
- Manifest version:
- Lean build hash:
- Theorem ids proved:
- Theorem ids assumed:
- Theorem ids deferred:

## 1. Motivation

Use philosophical/geometric language here, but do not rely on it for formal proof.

## 2. Dictionary Additions

Table of term ids introduced or modified.

## 3. Formal Definitions

Every definition cites dictionary ids.

## 4. Main Theorems

| Theorem id | Lean name | Statement | Status |
|---|---|---|---|

## 5. Proof Sketches

Explain each theorem in ordinary prose and point to Lean source.

## 6. Executable Examples

Show Python-generated examples, clearly labeled as examples/tests rather than proofs.

## 7. Translation to Standard Mathematics

Explain the standard interpretation.

## 8. Limitations

State exactly what is not proven.

## 9. Next Paper Dependencies

List the theorem ids needed by the next paper.
```

## Minimum standard for Paper 1

Paper 1 is complete only when these theorem ids are proved:

- CC-T0001
- CC-T0002
- CC-T0003
- CC-T0004

Paper 1 is strong when these are also proved:

- CC-T0005
- CC-T0006
- CC-T0007
