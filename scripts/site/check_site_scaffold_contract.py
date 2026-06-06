from __future__ import annotations

import re
import sys
from pathlib import Path

from site_lib import SITE, repo_relative


SCAFFOLD_ROOTS = [
    "chapters/S2",
    "chapters/S3",
    "chapters/S4_S6",
    "chapters/S7",
    "chapters/S15",
    "chapters/phase2",
    "chapters/applications",
]

SECTION_INDEXES = [
    "chapters/S2/index.qmd",
    "chapters/S3/index.qmd",
    "chapters/S4_S6/index.qmd",
    "chapters/S7/index.qmd",
    "chapters/S15/index.qmd",
    "chapters/phase2/index.qmd",
    "chapters/applications/index.qmd",
]

SCAFFOLD_GUARDRAILS = [
    "scaffold",
    "placeholder",
    "future work",
    "future-facing",
    "future horizon",
    "remain future",
    "remains future",
    "roadmap",
    "does not claim",
    "do not prove",
    "not proof",
    "not proofs",
    "not proof artifacts",
    "not performance claims",
    "not model-quality claims",
    "not real-data usefulness claim",
    "separate from lean proof status",
    "theorem cards are the status source",
    "theorem cards and generated target indexes determine",
    "theorem card says otherwise",
    "proof source of truth",
    "warning-sensitive",
]

WIDGET_GUARDRAILS = [
    "placeholder",
    "scaffold",
    "future work",
    "does not add proof status",
    "not proof",
]

APPLICATION_GUARDRAILS = [
    "not proof",
    "not performance claims",
    "not model-quality claims",
    "not real-data usefulness claim",
    "executable references",
    "separate from lean proof status",
]


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def has_any(text: str, phrases: list[str]) -> bool:
    norm = normalized(text)
    return any(phrase in norm for phrase in phrases)


def scaffold_pages() -> list[Path]:
    pages: list[Path] = []
    for root in SCAFFOLD_ROOTS:
        pages.extend(sorted((SITE / root).glob("*.qmd")))
    return pages


def check_page_guardrails(failures: list[str]) -> None:
    for path in scaffold_pages():
        text = path.read_text()
        if not has_any(text, SCAFFOLD_GUARDRAILS):
            failures.append(
                f"{repo_relative(path)}: missing scaffold/future/non-proof guardrail"
            )
        if "data-widget=" in text and not has_any(text, WIDGET_GUARDRAILS):
            failures.append(
                f"{repo_relative(path)}: widget scaffold page lacks widget non-proof/future guardrail"
            )
        if "theorem-box" in text and 'src="../../widgets/shared/widget_base.js"' not in text:
            failures.append(
                f"{repo_relative(path)}: theorem cards require shared widget_base script"
            )


def check_section_indexes(failures: list[str]) -> None:
    for rel_path in SECTION_INDEXES:
        path = SITE / rel_path
        text = path.read_text()
        if "warning-box" not in text:
            failures.append(f"{repo_relative(path)}: section index lacks warning box")
        if "theorem card" not in normalized(text):
            failures.append(f"{repo_relative(path)}: section index must point readers to theorem-card status")


def check_application_guardrails(failures: list[str]) -> None:
    for path in sorted((SITE / "chapters" / "applications").glob("*.qmd")):
        text = path.read_text()
        lower = normalized(text)
        if any(term in lower for term in ["benchmark", "fixture", "performance", "mlx"]):
            if not has_any(text, APPLICATION_GUARDRAILS):
                failures.append(
                    f"{repo_relative(path)}: application benchmark/fixture language lacks non-proof guardrail"
                )


def check_s15_future_scope(failures: list[str]) -> None:
    for path in sorted((SITE / "chapters" / "S15").glob("*.qmd")):
        text = path.read_text()
        if not has_any(text, ["future", "roadmap"]):
            failures.append(f"{repo_relative(path)}: S15 page must stay future/roadmap scoped")


def main() -> int:
    failures: list[str] = []
    check_page_guardrails(failures)
    check_section_indexes(failures)
    check_application_guardrails(failures)
    check_s15_future_scope(failures)

    if failures:
        print("site scaffold contract failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("site scaffold contract ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
