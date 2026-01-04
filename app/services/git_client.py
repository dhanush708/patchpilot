# app/services/git_client.py
# Responsible for:
#   - Creating a unique job directory for each analysis
#   - Cloning a Git repo into that directory OR
#   - Extracting a .zip (either from upload or from a saved path)

import os
import uuid
import zipfile
from typing import Tuple

try:
    # GitPython import. It needs "git" installed on your system.
    from git import Repo
except ImportError:
    Repo = None  # We'll handle this gracefully later.


def _create_job_dir(base_workdir: str) -> Tuple[str, str]:
    """
    Create a unique job directory inside the base workdir.
    Returns (job_id, job_dir_path).

    Example:
        base_workdir = "C:/Users/You/Desktop/patchpilot/workdir"
        -> job_id = "d9f2-..."
        -> job_dir = "C:/.../patchpilot/workdir/d9f2-..."
    """
    job_id = str(uuid.uuid4())  # Random unique ID like 'd9f2...'
    job_dir = os.path.join(base_workdir, job_id)
    os.makedirs(job_dir, exist_ok=True)
    return job_id, job_dir


def clone_git_repo(base_workdir: str, repo_url: str) -> Tuple[str, str]:
    """
    Clone a Git repository into a new job directory.

    Returns:
        (job_id, repo_path)
    where:
        - job_id is the unique ID of this analysis
        - repo_path is the directory where the repo was cloned
    """
    if Repo is None:
        raise RuntimeError("GitPython is not installed or git is not available.")

    job_id, job_dir = _create_job_dir(base_workdir)
    repo_path = os.path.join(job_dir, "repo")

    # Clone the remote repository into repo_path
    Repo.clone_from(repo_url, repo_path)

    return job_id, repo_path


def extract_zip_upload(base_workdir: str, file_storage) -> Tuple[str, str]:
    """
    Save an uploaded .zip file and extract it into a new job directory.

    This was used in the *synchronous* flow (early version).
    For the Celery (async) flow, we now prefer:
        - save the zip in the route (routes.py)
        - pass only its path to 'extract_zip_path'.
    """
    job_id, job_dir = _create_job_dir(base_workdir)

    # Save the uploaded zip to disk inside the job directory
    zip_path = os.path.join(job_dir, "upload.zip")
    file_storage.save(zip_path)

    # Extract all contents of the zip into the job_dir
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(job_dir)

    extracted_path = job_dir
    return job_id, extracted_path


def extract_zip_path(base_workdir: str, zip_path: str) -> Tuple[str, str]:
    """
    Take an existing .zip file path (already saved on disk)
    and extract it into a new job directory.

    This is what the Celery worker uses, because the web process
    (in routes.py) saves the uploaded file and passes only the path.

    Returns:
        (job_id, extracted_path)
    where:
        - job_id is a unique ID for this analysis
        - extracted_path is the directory where the zip was extracted
    """
    # Create a fresh job directory inside base_workdir
    job_id, job_dir = _create_job_dir(base_workdir)

    # Extract zip_path into job_dir
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(job_dir)

    extracted_path = job_dir
    return job_id, extracted_path
