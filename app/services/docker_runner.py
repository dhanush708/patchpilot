# app/services/docker_runner.py
"""
Run tests inside a Docker container.

Exports:
    - _docker_available() -> bool
    - run_in_docker(repo_path: str, timeout: int = 60) -> dict
      returns:
        {
          "exit_code": int,
          "stdout": str,
          "stderr": str,
          "report_json": dict | None,
          "duration": float,
          "timed_out": bool,
          "used_docker": bool,
        }
"""

import json
import os
import subprocess
import time
from typing import Any, Dict, Optional


def _docker_available() -> bool:
    """Return True if `docker` CLI is available."""
    try:
        subprocess.run(
            ["docker", "version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def run_in_docker(repo_path: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Run pytest in a python:3.11-slim container with the given repo mounted at /workspace.

    The container:
      - installs pytest + pytest-json-report
      - runs: pytest -q --json-report --json-report-file=report.json

    We then read /workspace/report.json from the host side.
    """
    start = time.time()

    repo_path = os.path.abspath(repo_path)

    if not os.path.isdir(repo_path):
        return {
            "exit_code": 127,
            "stdout": "",
            "stderr": f"repo_path does not exist or is not a directory: {repo_path}",
            "report_json": None,
            "duration": 0.0,
            "timed_out": False,
            "used_docker": False,
        }

    if not _docker_available():
        return {
            "exit_code": 127,
            "stdout": "",
            "stderr": "docker CLI not available on this system.",
            "report_json": None,
            "duration": 0.0,
            "timed_out": False,
            "used_docker": False,
        }

    # Normalise Windows path for Docker (-v host:container)
    host_path = repo_path.replace("\\", "/")

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{host_path}:/workspace",
        "-w",
        "/workspace",
        "python:3.11-slim",
        "sh",
        "-c",
        "python -m pip install -q pytest pytest-json-report "
        "&& pytest -q --json-report --json-report-file=report.json",
    ]

    timed_out = False
    stdout = ""
    stderr = ""
    exit_code: Optional[int] = None

    try:
        completed = subprocess.run(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        exit_code = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = (exc.stdout or "") if exc.stdout is not None else ""
        stderr = (exc.stderr or "") if exc.stderr is not None else ""
        exit_code = 124  # conventional timeout code

    duration = time.time() - start

    # Read report.json from host side if present
    report_json = None
    report_path = os.path.join(repo_path, "report.json")
    if os.path.isfile(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_json = json.load(f)
        except Exception:
            report_json = None

    return {
        "exit_code": exit_code if exit_code is not None else 124,
        "stdout": stdout,
        "stderr": stderr,
        "report_json": report_json,
        "duration": duration,
        "timed_out": timed_out,
        "used_docker": True,
    }
