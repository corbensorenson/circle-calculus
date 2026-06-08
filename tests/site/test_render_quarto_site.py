from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "site" / "render_quarto_site.py"


def load_render_helper():
    script_dir = str(SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("render_quarto_site_for_test", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_clean_quarto_intermediates_removes_only_generated_render_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    helper = load_render_helper()
    site = tmp_path / "site"
    output = site / "_site"
    quarto_cache = site / ".quarto"

    for path in [
        site / "chapters" / "S1",
        site / "components",
        output,
        quarto_cache,
        site / "site_libs",
        site / "page_files",
    ]:
        path.mkdir(parents=True, exist_ok=True)

    (site / "page.qmd").write_text("---\ntitle: Page\n---\n")
    (site / "page.html").write_text("<html></html>")
    (site / "page_files" / "asset.txt").write_text("generated")
    (site / "chapters" / "S1" / "index.qmd").write_text("---\ntitle: S1\n---\n")
    (site / "chapters" / "S1" / "index.html").write_text("<html></html>")
    (site / "components" / "theorem_box.html").write_text("<div></div>")
    (output / "index.html").write_text("<html></html>")

    monkeypatch.setattr(helper, "SITE", site)
    monkeypatch.setattr(helper, "OUTPUT", output)
    monkeypatch.setattr(helper, "QUARTO_CACHE", quarto_cache)

    helper.clean_quarto_intermediates(include_output=False)

    assert output.exists()
    assert not quarto_cache.exists()
    assert not (site / "site_libs").exists()
    assert not (site / "page.html").exists()
    assert not (site / "page_files").exists()
    assert not (site / "chapters" / "S1" / "index.html").exists()
    assert (site / "components" / "theorem_box.html").exists()

    helper.clean_quarto_intermediates(include_output=True)

    assert not output.exists()


def test_main_recovers_nonzero_quarto_exit_only_after_render_validation(
    monkeypatch,
    capsys,
) -> None:
    helper = load_render_helper()
    calls: list[tuple[str, object]] = []

    def fake_clean(*, include_output: bool) -> None:
        calls.append(("clean", include_output))

    def fake_precreate() -> None:
        calls.append(("precreate", None))

    def fake_run_quarto(quarto: str) -> int:
        calls.append(("run", quarto))
        return 1

    def fake_valid() -> bool:
        calls.append(("validate", None))
        return True

    monkeypatch.setattr(helper, "clean_quarto_intermediates", fake_clean)
    monkeypatch.setattr(helper, "precreate_output_dirs", fake_precreate)
    monkeypatch.setattr(helper, "run_quarto", fake_run_quarto)
    monkeypatch.setattr(helper, "rendered_site_is_valid", fake_valid)
    monkeypatch.setattr(helper.time, "sleep", lambda seconds: calls.append(("sleep", seconds)))
    monkeypatch.setattr(sys, "argv", ["render_quarto_site.py", "fake-quarto"])

    assert helper.main() == 0

    assert calls == [
        ("clean", True),
        ("precreate", None),
        ("run", "fake-quarto"),
        ("sleep", 1),
        ("validate", None),
        ("clean", False),
    ]
    assert "validated _site" in capsys.readouterr().err
