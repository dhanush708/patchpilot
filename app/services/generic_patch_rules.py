import os
import re
from typing import Dict, Any


def generate_patch(
    failure_class: str,
    analysis: Dict[str, Any],
    repo_path: str
) -> Dict[str, Any]:
    """
    Safe generic patch rules.
    NEVER assumes analysis["failures"] exists.
    """

    stdout = analysis.get("stdout", "")

    # ---------- NAME ERROR ----------
    if failure_class == "name_error":
        m = re.search(r"name '(\w+)' is not defined", stdout)
        if not m:
            return {}

        missing = m.group(1)

        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if missing in content:
                        fixed = content.replace(missing, "name")
                        return {
                            "target_file": os.path.relpath(path, repo_path),
                            "new_contents": fixed,
                            "justification": f"Fixed NameError: {missing} → name",
                            "failure_class": "name_error",
                        }

    # ---------- MODULE NOT FOUND ----------
    if failure_class == "module_not_found":
        m = re.search(r"No module named '(.+)'", stdout)
        if not m:
            return {}

        module = m.group(1)
        return {
            "target_file": f"{module}.py",
            "new_contents": "# auto-created module\n",
            "justification": f"Created missing module {module}",
            "failure_class": "module_not_found",
        }

    # ---------- ASSERTION FAILURE ----------
    # ❌ DO NOT AUTO-FIX
    return {}
