# app/services/pytest_parser.py
#
# Turn raw pytest stdout/stderr into a structured dict.
# This is deliberately simple but robust:
#   - Counts passed/failed tests
#   - Extracts each failing test from the "short test summary info" section.

from __future__ import annotations

import re
from typing import Any, Dict, List


def _extract_counts(stdout: str) -> Dict[str, int]:
    """
    Look for lines like:
        4 passed in 0.28s
        2 failed, 3 passed in 0.41s
    and return passed/failed/total.
    """
    passed = 0
    failed = 0

    for line in stdout.splitlines():
        line = line.strip()
        if "passed" in line or "failed" in line:
            m_failed = re.search(r"(\d+)\s+failed", line)
            m_passed = re.search(r"(\d+)\s+passed", line)
            if m_failed:
                failed = int(m_failed.group(1))
            if m_passed:
                passed = int(m_passed.group(1))

    total = passed + failed
    return {
        "passed_tests": passed,
        "failed_tests": failed,
        "total_tests": total,
    }


def _extract_failures(stdout: str) -> List[Dict[str, Any]]:
    """
    Parse the 'short test summary info' lines, e.g.:

        FAILED calculator_buggy/test_calculator.py::test_add - assert -1 == 5
        FAILED calculator_buggy/test_calculator.py::test_subtract - assert -3 == 3

    Returns a list of dicts with keys: file, test_name, message.
    """
    failures: List[Dict[str, Any]] = []

    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("FAILED "):
            continue

        # Try to match: FAILED <file>::<test_name> - <message>
        m = re.match(r"^FAILED\s+(.+?)::([^\s]+)\s*-\s*(.+)$", line)
        if not m:
            # Fallback: maybe there's no " - message" part
            m2 = re.match(r"^FAILED\s+(.+?)::([^\s]+)\s*$", line)
            if m2:
                file_path, test_name = m2.groups()
                failures.append(
                    {
                        "file": file_path,
                        "test_name": test_name,
                        "message": "",
                    }
                )
            continue

        file_path, test_name, message = m.groups()
        failures.append(
            {
                "file": file_path,
                "test_name": test_name,
                "message": message.strip(),
            }
        )

    return failures


def parse_pytest_output(stdout: str, stderr: str) -> Dict[str, Any]:
    """
    Public entrypoint used by Celery.

    Returns dict with at least:
        - total_tests
        - passed_tests
        - failed_tests
        - failures: list of {file, test_name, message}
        - raw_stdout / raw_stderr (for debugging)
    """
    counts = _extract_counts(stdout)
    failures = _extract_failures(stdout)

    # If pytest clearly printed failures but we didn't see counts,
    # backfill failed_tests from the length of failures.
    if failures and counts["failed_tests"] == 0:
        counts["failed_tests"] = len(failures)
        counts["total_tests"] = counts["passed_tests"] + counts["failed_tests"]

    return {
        **counts,
        "failures": failures,
        "raw_stdout": stdout,
        "raw_stderr": stderr,
    }
