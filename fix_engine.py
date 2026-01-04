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


def run_fix_engine(repo_path):
    code, output = run_pytest(repo_path)

    if code == 0:
        return FixResult(
            status="FIXED",
            summary="All tests passed. No fixes required.",
            stdout=output,
            output_path=repo_path
        )

    return FixResult(
        status="FAILED",
        summary="Tests failed. Manual intervention required.",
        stdout=output,
        output_path=repo_path
    )
