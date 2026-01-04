# app/tasks.py

from typing import Any, Dict

from celery_app import celery
from app.services.git_client import extract_zip_path
from app.services.pytest_runner import run_tests
from app.services.log_parser import analyze_run


def _format_test_result_before(exit_code: int, stdout: str, stderr: str) -> str:
    return (
        f"Exit code: {exit_code}\n\n"
        "--- Pytest STDOUT ---\n"
        f"{stdout.strip() or '(empty)'}\n\n"
        "--- Pytest STDERR ---\n"
        f"{stderr.strip() or '(empty)'}"
    )


def _build_patch_suggestion(parsed: Dict[str, Any], exit_code: int) -> str:
    failures = parsed.get("failures") or []

    if exit_code == 0 and not failures:
        return (
            "All tests passed. No patch needed.\n"
            "If you expected failures, double-check that your tests are written correctly."
        )

    if exit_code != 0 and not failures:
        return (
            "Pytest exited with a non-zero status, but PatchPilot could not parse "
            "individual failing tests. Check raw pytest output below."
        )

    lines = [
        "Status: FAILED",
        "Detected error types: AssertionError",
        "",
        "- AssertionError detected: review expected vs actual values.",
        "",
        "Relevant failure lines from pytest:",
    ]

    for f in failures:
        file_path = f.get("file", "(unknown)")
        test_name = f.get("test_name", "(unknown)")
        msg = (f.get("message") or "").strip()
        if msg:
            lines.append(f"  {file_path}::{test_name} - {msg}")
        else:
            lines.append(f"  {file_path}::{test_name}")

    return "\n".join(lines)


def _build_generated_test(parsed: Dict[str, Any], status_label: str) -> str:
    failures = parsed.get("failures") or []

    lines = [
        "import pytest",
        "",
        "def test_auto_generated_fix():",
        '    """',
        "    Auto-generated test skeleton by PatchPilot.",
        "",
        f"    Detected status: {status_label}",
    ]

    if failures:
        lines.append("    Detected error types: AssertionError")
        lines.append("")
        lines.append("    Failure context (from pytest):")
        for f in failures:
            for line in f.get("message", "").splitlines():
                lines.append(f"    # {line}")
    else:
        lines.append("    Detected error types: unspecified error type")
        lines.append("")
        lines.append("    Failure context:")
        lines.append("    # No failure lines detected.")

    lines += [
        '    """',
        "    assert False, 'Replace with real assertions'",
        "",
    ]

    return "\n".join(lines)


@celery.task(bind=True, name="app.tasks.run_analysis_task")
def run_analysis_task(self, job_data: Dict[str, Any]) -> Dict[str, Any]:

    # progress -> preparing
    self.update_state(state="STARTED", meta={"step": "Preparing project..."})

    base_workdir = job_data["base_workdir"]
    zip_path = job_data["payload"]["zip_path"]

    # extract zip
    job_id, project_path = extract_zip_path(base_workdir, zip_path)

    # define target_label (was missing in your file)
    target_label = "(zip upload)"

    # progress -> running tests
    self.update_state(state="STARTED", meta={"step": "Running tests with pytest..."})

    # run tests (docker or local runner implemented elsewhere)
    run_result = run_tests(project_path, use_docker=True)

    stdout = run_result.get("stdout", "")
    stderr = run_result.get("stderr", "")
    exit_code = run_result.get("exit_code") if run_result.get("exit_code") is not None else 1

    # formatted raw output for UI
    test_result_before = _format_test_result_before(exit_code, stdout, stderr)

    # parse/analyze run (defensive)
    try:
        parsed = analyze_run(run_result)
        parse_error = None
    except Exception as exc:
        parse_error = str(exc)
        parsed = {
            "stats": {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0},
            "failures": [],
            "root_cause": None,
        }

    summary = (
        "All tests passed successfully. No failures were detected."
        if exit_code == 0
        else "Some tests failed. See details below."
    )
    status_label = "passed" if exit_code == 0 else "failed"

    # build suggestion + generated test (guaranteed defined)
    patch_suggestion = _build_patch_suggestion(parsed, exit_code)
    generated_test = _build_generated_test(parsed, status_label)

    return {
        "job_id": job_id,
        "project_path": project_path,
        "repo_url": target_label,
        "summary": summary,
        "stats": parsed.get("stats") or {"total": 0, "passed": 0, "failed": 0},
        "failures": parsed.get("failures") or [],
        "root_cause": parsed.get("root_cause"),
        "patch_suggestion": patch_suggestion,
        "generated_test": generated_test,
        "test_result_before": test_result_before,
        "test_result_after": "Patch not applied yet.",
        "parse_error": parse_error,
    }
