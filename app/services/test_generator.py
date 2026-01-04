# app/services/test_generator.py
# Responsible for generating a simple test template based on failure info.
# We're not doing full AI here; just a helpful starting point.

from typing import Dict


def generate_test_template(parsed_log: Dict) -> str:
    """
    Build a small pytest-style test template that the user can copy into their repo.
    """
    overall_status = parsed_log.get("overall_status", "unknown")
    error_types = parsed_log.get("error_types", [])
    lines = parsed_log.get("interesting_lines", [])

    error_comment = ", ".join(error_types) if error_types else "unspecified error type"
    failure_context = "\n    # ".join(lines[:5]) if lines else "No failure lines captured."

    template = f"""import pytest

def test_auto_generated_fix():
    \"\"\"
    Auto-generated test skeleton by PatchPilot.

    Detected status: {overall_status}
    Detected error types: {error_comment}

    Failure context (from pytest):
    # {failure_context}
    \"\"\"
    # TODO: Reproduce the failing scenario here by:
    #   1. Calling the function that failed.
    #   2. Asserting the correct expected behavior.
    # Then remove the 'assert False' below.
    assert False, "Replace this with real assertions for the fixed behavior."
"""
    return template
