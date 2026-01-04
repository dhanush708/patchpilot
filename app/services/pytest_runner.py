# app/services/pytest_runner.py
"""
High-level pytest runner.

Exports:
    - run_tests(repo_path: str, use_docker: bool = True, timeout: int = 60) -> dict

Return dict shape:
    {
      "exit_code": int,
      "stdout": str,
      "stderr": str,
      "report_json": dict | None,
      "duration": float,
      "used_docker": bool,
    }
"""

import json
import os
import subprocess
import time
from typing import Any, Dict

from .docker_runner import run_in_docker, _docker_available


def _run_local_pytest(repo_path: str, timeout: int = 60) -> Dict[str, Any]:
    """Fallback: run pytest directly on the host machine (no Docker)."""
    start = time.time()
    repo_path = os.path.abspath(repo_path)

    if not os.path.isdir(repo_path):
        return {
            "exit_code": 127,
            "stdout": "",
            "stderr": f"repo_path does not exist or is not a directory: {repo_path}",
            "report_json": None,
            "duration": 0.0,
            "used_docker": False,
        }

    # Try to run pytest with json-report; if plugin missing, it will error.
    cmd = [
        "pytest",
        "-q",
        "--json-report",
        "--json-report-file=report.json",
    ]

    try:
        completed = subprocess.run(
            cmd,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        exit_code = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stdout = (exc.stdout or "") if exc.stdout is not None else ""
        stderr = (exc.stderr or "") if exc.stderr is not None else ""

    duration = time.time() - start

    report_json = None
    report_path = os.path.join(repo_path, "report.json")
    if os.path.isfile(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_json = json.load(f)
        except Exception:
            report_json = None

    return {
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "report_json": report_json,
        "duration": duration,
        "used_docker": False,
    }


def run_tests(repo_path: str, use_docker: bool = True, timeout: int = 60) -> Dict[str, Any]:
    """
    Main public entrypoint.

    If use_docker and docker is available -> run_in_docker.
    Otherwise -> run locally.
    """
    if use_docker and _docker_available():
        return run_in_docker(repo_path, timeout=timeout)
    else:
        return _run_local_pytest(repo_path, timeout=timeout)
