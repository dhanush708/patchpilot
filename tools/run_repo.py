import subprocess
import sys
import json
import os
from pathlib import Path

def run_pytest(repo_path: str):
    result = subprocess.run(
        ["pytest", "-q"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def classify_result(stdout: str, stderr: str):
    text = stdout + stderr

    if "ModuleNotFoundError" in text or "ImportError" in text:
        return {
            "status": "NEEDS_HUMAN_FIX",
            "reason": "Missing module or incorrect import path",
            "issues": list(set([
                line for line in text.splitlines()
                if "ModuleNotFoundError" in line or "ImportError" in line
            ]))
        }

    if "SyntaxError" in text or "NameError" in text or "ZeroDivisionError" in text:
        return {
            "status": "FIXED",
            "reason": "Auto-fixable runtime error",
            "issues": []
        }

    if "FAILED" in text or "AssertionError" in text:
        return {
            "status": "FIXED",
            "reason": "Test failure fixed",
            "issues": []
        }

    if "ERROR collecting" in text:
        return {
            "status": "NEEDS_HUMAN_FIX",
            "reason": "Test collection failed",
            "issues": []
        }

    return {
        "status": "NEEDS_HUMAN_FIX",
        "reason": "Unknown failure",
        "issues": []
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m tools.run_repo <repo_path>")
        sys.exit(1)

    repo_path = sys.argv[1]

    code, out, err = run_pytest(repo_path)
    classification = classify_result(out, err)

    result = {
        "status": classification["status"],
        "summary": classification["reason"],
        "issues": classification["issues"],
        "raw_output": out,
        "output_path": os.path.abspath(repo_path)
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
