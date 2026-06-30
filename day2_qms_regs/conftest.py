"""
Collect @pytest.mark.sds("SDS-XXX") markers during a test run and write a
unit-test traceability record (day2_data/data/unit_test_record.md).

Lives at the project root so the hooks fire for both ``pytest src/...`` and the
notebooks' ``%%ipytest`` cells, whose rootdir is this directory.
"""

import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.traceability import write_unit_test_record
# One record per executed test, accumulated across the session.
_records: list[dict] = []


def pytest_sessionstart(session):
    _records.clear()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    marker = item.get_closest_marker("sds")
    _records.append({
        "cls": item.cls.__name__ if item.cls else "",
        "name": item.originalname or item.name,
        "sds": list(marker.args) if marker else [],
        "outcome": report.outcome,
    })


def pytest_sessionfinish(session, exitstatus):
    if _records:
        write_unit_test_record(_records)
