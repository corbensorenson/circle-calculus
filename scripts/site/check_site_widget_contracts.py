from __future__ import annotations

import re
import sys
from pathlib import Path

from site_lib import GENERATED, ROOT, SITE, load_json, repo_relative


WIDGET_ATTR_RE = re.compile(r'data-widget="([^"]+)"')
MOUNT_RE = re.compile(r'mountWidgets\("([^"]+)"')


def site_pages() -> list[Path]:
    return sorted(SITE.glob("**/*.qmd"))


def mounted_widgets_by_page() -> dict[Path, set[str]]:
    out: dict[Path, set[str]] = {}
    for path in site_pages():
        widgets = set(WIDGET_ATTR_RE.findall(path.read_text()))
        if widgets:
            out[path] = widgets
    return out


def js_mount_ids(path: Path) -> set[str]:
    return set(MOUNT_RE.findall(path.read_text()))


def main() -> int:
    failures: list[str] = []
    widget_index = load_json(GENERATED / "widget_index.json")
    widgets = widget_index.get("widgets", [])
    widget_ids = [widget.get("id", "") for widget in widgets]
    duplicate_ids = sorted({widget_id for widget_id in widget_ids if widget_ids.count(widget_id) > 1})
    if duplicate_ids:
        failures.append(f"duplicate widget ids: {duplicate_ids}")

    by_id = {widget["id"]: widget for widget in widgets}
    page_mounts = mounted_widgets_by_page()
    mounted_ids = set().union(*page_mounts.values()) if page_mounts else set()
    js_ids: set[str] = set()

    for widget_id, widget in sorted(by_id.items()):
        path = ROOT / widget.get("path", "")
        if not path.exists():
            failures.append(f"widget {widget_id}: missing script {widget.get('path', '')}")
            continue
        mounts = js_mount_ids(path)
        js_ids.update(mounts)
        if widget_id not in mounts:
            failures.append(
                f"widget {widget_id}: {widget.get('path', '')} does not call mountWidgets(\"{widget_id}\")"
            )

    for page, widgets_on_page in sorted(page_mounts.items()):
        text = page.read_text()
        for widget_id in sorted(widgets_on_page):
            widget = by_id.get(widget_id)
            if widget is None:
                failures.append(f"{repo_relative(page)}: data-widget references unknown widget {widget_id}")
                continue
            script_suffix = widget.get("path", "").removeprefix("site/")
            if script_suffix and script_suffix not in text:
                failures.append(
                    f"{repo_relative(page)}: widget {widget_id} missing script for {script_suffix}"
                )

    indexed_not_mounted = sorted(set(by_id) - mounted_ids)
    if indexed_not_mounted:
        failures.append(f"widget_index entries not mounted by any page: {indexed_not_mounted}")

    mounted_without_index = sorted(mounted_ids - set(by_id))
    if mounted_without_index:
        failures.append(f"page widget mounts missing from widget_index: {mounted_without_index}")

    js_without_index = sorted(js_ids - set(by_id))
    if js_without_index:
        failures.append(f"mountWidgets calls missing from widget_index: {js_without_index}")

    if failures:
        print("site widget contract failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"site widget contracts ok: {len(by_id)} widgets, {len(page_mounts)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
