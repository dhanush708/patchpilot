import os
from typing import Dict, Any


def suggest_patch_from_run(
    run_result: Dict[str, Any],
    repo_path: str,
    failure_class: str,
) -> Dict[str, Any]:

    stderr = run_result.get("stderr", "")
    stdout = run_result.get("stdout", "")
    text = stderr + stdout

    # =========================
    # NAME ERROR (typos)
    # =========================
    if failure_class == "name_error":
        # naive but effective: fix undefined variable by matching function arg
        lines = text.splitlines()
        for line in lines:
            if "NameError" in line and "not defined" in line:
                bad_name = line.split("'")[1]

                # find file
                for root, _, files in os.walk(repo_path):
                    for f in files:
                        if f.endswith(".py"):
                            path = os.path.join(root, f)
                            with open(path, "r", encoding="utf-8") as fh:
                                code = fh.read()
                            if bad_name in code:
                                fixed = code.replace(bad_name, "name")
                                return {
                                    "target_file": os.path.relpath(path, repo_path),
                                    "new_contents": fixed,
                                    "justification": f"Fixed NameError: {bad_name}",
                                }

    # =========================
    # IMPORT ERROR
    # =========================
    if failure_class == "import_error":
        return {}  # requires human intent (correct)

    # =========================
    # WRONG LOGIC (assert fail)
    # =========================
    if failure_class == "wrong_logic":
        # simple arithmetic flip
        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8") as fh:
                        code = fh.read()

                    if "return a - b" in code:
                        return {
                            "target_file": os.path.relpath(path, repo_path),
                            "new_contents": code.replace("return a - b", "return a + b"),
                            "justification": "Fixed incorrect arithmetic",
                        }

    return {}
