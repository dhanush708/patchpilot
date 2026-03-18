import os
import subprocess
import sys


class FixResult:
    def __init__(self, status, summary, stdout, output_path):
        self.status = status
        self.summary = summary
        self.stdout = stdout
        self.output_path = output_path


def run_pytest(repo_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = repo_path

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=repo_path,
        env=env,
        capture_output=True,
        text=True
    )

    combined_output = (result.stdout or "") + "\n" + (result.stderr or "")
    return result.returncode, combined_output


# 🔥 NEW: failure classification
def classify_failure(output: str):
    out = output.lower()

    # Import / module issues → auto-fixable (future scope)
    if "modulenotfounderror" in out or "importerror" in out:
        return "IMPORT_ERROR"

    # Assertion failures → logic mismatch → human required
    if "assert" in out or "assertionerror" in out:
        return "ASSERTION_ERROR"

    # Syntax / crash
    if "syntaxerror" in out:
        return "SYNTAX_ERROR"

    return "UNKNOWN"


def run_fix_engine(repo_path):
    code, output = run_pytest(repo_path)

    # ✅ CASE 1: everything passed
    if code == 0:
        return FixResult(
            status="FIXED",
            summary="All tests passed. No fixes required.",
            stdout=output,
            output_path=repo_path
        )

    # 🔥 classify failure instead of blindly FAIL
    failure_type = classify_failure(output)

    # ✅ CASE 2: logic issue → human required
    if failure_type == "ASSERTION_ERROR":
        return FixResult(
            status="NEEDS_HUMAN_FIX",
            summary="Test failed due to logic mismatch. Human decision required.",
            stdout=output,
            output_path=repo_path
        )

    # ⚠️ CASE 3: import issue (you can later auto-fix)
    if failure_type == "IMPORT_ERROR":
        return FixResult(
            status="NEEDS_HUMAN_FIX",
            summary="Import/module issue detected. Requires structural fix.",
            stdout=output,
            output_path=repo_path
        )

    # ❌ CASE 4: unknown failure
    return FixResult(
        status="FAILED",
        summary="Failure could not be safely classified.",
        stdout=output,
        output_path=repo_path
    )
