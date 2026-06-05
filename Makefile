LAKE := $(shell command -v lake 2>/dev/null || printf "%s/.elan/bin/lake" "$$HOME")

.PHONY: check lean sidecarlean test manifest dictionary paperlinks nofake examples

check: lean sidecarlean test manifest dictionary paperlinks nofake

lean:
	$(LAKE) build

sidecarlean:
	python scripts/check_lean_sidecars.py

test:
	python -m pytest

manifest:
	python scripts/check_manifest.py

dictionary:
	python scripts/check_dictionary.py

paperlinks:
	python scripts/check_paper_theorem_links.py

nofake:
	python scripts/check_no_fake_proofs.py

examples:
	python scripts/render_examples.py
