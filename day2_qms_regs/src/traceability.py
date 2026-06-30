"""
Generate a unit-test traceability record from @pytest.mark.sds markers.

Each test marked ``@pytest.mark.sds("SDS-001")`` is linked back to a System
Design Specification item. ``conftest.py`` collects one record per test during a
normal test run and calls :func:`write_unit_test_record`, which renders a
markdown table grouping tests under their SDS item (with the SDS title pulled
from the QMS data) so a reader can see, at a glance, which design specs are
covered by which tests and whether they pass.
"""

from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_REQUIREMENTS = "day2_data/data/requirements.yml"
DEFAULT_OUTPUT = "day2_data/release/unit_test_record.md"

_RESULT_ICON = {"passed": "✅ passed", "failed": "❌ failed", "skipped": "⚪ skipped"}


def _load_sds_titles(requirements_path: str) -> dict[str, str]:
    """Return ``{"SDS-001": title, ...}`` from a requirements YAML file."""
    path = Path(requirements_path)
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {item["id"]: item.get("title", "") for item in data.get("sys_des_spec", [])}


def write_unit_test_record(
    records: list[dict],
    out_path: str = DEFAULT_OUTPUT,
    requirements_path: str = DEFAULT_REQUIREMENTS,
) -> str:
    """Write a markdown unit-test traceability record and return its text.

    Parameters
    ----------
    records:
        One dict per test, each with keys ``cls`` (class name, may be ""),
        ``name`` (method name), ``sds`` (list of SDS IDs, may be empty) and
        ``outcome`` ("passed" / "failed" / "skipped").
    out_path:
        Where to write the markdown file.
    requirements_path:
        QMS requirements YAML used to look up SDS titles.
    """
    titles = _load_sds_titles(requirements_path)

    # Group test rows under each SDS ID they are marked against. Unmarked tests
    # fall under "Untraced" so missing traceability is visible, not hidden.
    groups: dict[str, list[dict]] = {}
    for rec in records:
        for sds_id in rec["sds"] or ["Untraced"]:
            groups.setdefault(sds_id, []).append(rec)

    lines = [
        "# Unit Test Record",
        "",
        "Traceability from each unit test to the System Design Specification (SDS) "
        "item it verifies. Generated automatically from `@pytest.mark.sds(...)` "
        "markers when the tests run.",
        "",
    ]

    for sds_id in sorted(groups):
        if sds_id == "Untraced":
            lines.append("## Untraced (no `sds` marker)")
        else:
            title = titles.get(sds_id, "— unknown SDS —")
            lines.append(f"## {sds_id} — {title}")
        lines += ["", "| Test | Result |", "| --- | --- |"]
        for rec in groups[sds_id]:
            test = f"{rec['cls']}::{rec['name']}" if rec["cls"] else rec["name"]
            icon = _RESULT_ICON.get(rec["outcome"], rec["outcome"])
            lines.append(f"| `{test}` | {icon} |")
        lines.append("")

    text = "\n".join(lines)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return text
