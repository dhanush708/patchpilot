# app/services/patch_applier.py
import os
import subprocess
from typing import Dict, Any


def apply_patch_and_test(patch: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
    """
    Apply the suggested patch and re-run pytest.
    """
    target = patch.get("target_file")
    new_contents = patch.get("new_contents")

    if not target or not new_contents:
        return {
            "applied": False,
            "reason": "No patch to apply"
        }

    abs_target = os.path.join(repo_path, target)

    # Safety check
    if not os.path.exists(abs_target):
        return {
            "applied": False,
            "reason": f"Target file not found: {abs_target}"
        }

    # Backup
    backup_path = abs_target + ".bak"
    if not os.path.exists(backup_path):
        with open(abs_target, "r", encoding="utf-8") as f:
            original = f.read()
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original)

    # Apply patch
    with open(abs_target, "w", encoding="utf-8") as f:
        f.write(new_contents)

    # Re-run pytest
    result = subprocess.run(
        ["python", "-m", "pytest", "-q"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    return {
        "applied": True,
        "pytest_exit_code": result.returncode,
        "pytest_stdout": result.stdout,
        "pytest_stderr": result.stderr,
        "fixed": result.returncode == 0
    }
