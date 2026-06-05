from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DICTIONARY = ROOT / "dictionary" / "circle_dictionary.yaml"
DICTIONARY_SCHEMA = ROOT / "dictionary" / "circle_dictionary.schema.json"
THEOREM_MANIFEST = ROOT / "manifests" / "theorem_manifest.yaml"
THEOREM_SCHEMA = ROOT / "manifests" / "theorem_manifest.schema.json"
PAPER_MANIFEST = ROOT / "manifests" / "paper_manifest.yaml"
DIMENSION_INDEX = ROOT / "manifests" / "dimensions" / "dimension_index.yaml"
DIMENSION_MANIFESTS = ROOT / "manifests" / "dimensions"
DIMENSION_DICTIONARIES = ROOT / "dictionary" / "dimensions"
PAPERS = ROOT / "papers"
SIDECARS = ROOT / "sidecars"
