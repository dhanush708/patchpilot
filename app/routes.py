import os
import uuid
import shutil
import subprocess
from flask import Blueprint, render_template, request

bp = Blueprint("main", __name__)

WORKDIR = "workdir"
UPLOADS = "uploads"

os.makedirs(WORKDIR, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/run", methods=["POST"])
def run_patchpilot():
    file = request.files.get("repo")

    if not file:
        return render_template("result.html", result={
            "status": "ERROR",
            "summary": "No repository uploaded",
            "reason": "Missing input",
            "issues": [],
            "output_path": None
        })

    if not file.filename.endswith(".zip"):
        return render_template("result.html", result={
            "status": "ERROR",
            "summary": "Invalid file format",
            "reason": "Only .zip repositories are allowed",
            "issues": [],
            "output_path": None
        })

    run_id = str(uuid.uuid4())
    zip_path = os.path.join(UPLOADS, f"{run_id}.zip")
    extract_path = os.path.join(WORKDIR, run_id)

    file.save(zip_path)
    shutil.unpack_archive(zip_path, extract_path)

    result = run_pytest(extract_path)

    return render_template("result.html", result=result)


def run_pytest(repo_path):
    try:
        proc = subprocess.run(
            ["pytest"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if proc.returncode == 0:
            return {
                "status": "FIXED",
                "summary": "All tests passed successfully",
                "reason": None,
                "issues": [],
                "output_path": repo_path
            }

        issues = []

        if "ModuleNotFoundError" in proc.stdout:
            issues.append("Missing module or incorrect import path")

        if "AssertionError" in proc.stdout:
            issues.append("Test assertion failure")

        return {
            "status": "NEEDS_HUMAN_FIX",
            "summary": "Automatic patching stopped",
            "reason": "Failure could not be safely fixed",
            "issues": issues,
            "output_path": repo_path
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "ERROR",
            "summary": "Execution timed out",
            "reason": "Tests took too long",
            "issues": [],
            "output_path": None
        }
