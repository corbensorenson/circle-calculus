# CI and Verification Contract

## Required commands

```bash
lake build
python -m pytest
python scripts/check_manifest.py
python scripts/check_dictionary.py
python scripts/check_no_fake_proofs.py
python scripts/check_paper_theorem_links.py
```

## Fake-proof scanner

The scanner must fail on these in proved Lean files:

```text
sorry
admit
by?
axiom
unsafe
set_option autoImplicit true
```

`axiom` and `unsafe` may appear only in whitelisted files, and no theorem depending on them may be marked `proved` unless explicitly classified as axiomatic/metatheoretic.

## Manifest checker

The manifest checker must verify:

- theorem ids are unique,
- Lean names are unique,
- every dictionary dependency exists,
- every paper reference exists,
- every `proved` theorem has a Lean name,
- every `proved` theorem is found in compiled Lean output or checked declaration list,
- no theorem is `proved` if its Lean file contains forbidden placeholders.

## Dictionary checker

The dictionary checker must verify:

- ids are unique,
- required fields exist,
- dependencies exist,
- forbidden meanings are nonempty for overloaded terms,
- Lean declarations referenced by dictionary entries exist when status is proved.

## Paper link checker

The paper checker must verify:

- each `CC-T####` in papers exists in theorem manifest,
- each `CC-####` dictionary id in papers exists,
- no `planned`, `blocked`, or `deferred` theorem is described as proven,
- every formal theorem table includes Lean theorem names.

## CI success definition

The repository is green only when all commands pass.
