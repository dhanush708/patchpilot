import os
import re
from typing import Dict, Any


def generate_patch(
    failure_class: str,
    analysis: Dict[str, Any],
    repo_path: str
) -> Dict[str, Any]:
    """
    Generic patch generator for SAFE, deterministic fixes only.
    This engine MUST NOT guess business logic.
    """

    stdout = analysis.get("stdout", "")

    # ==================================================
    # NAME ERROR: variable typo (safe)
    # ==================================================
    if failure_class == "name_error":
        match = re.search(r"name '(\w+)' is not defined", stdout)
        if not match:
            return {}

        missing_name = match.group(1)

        for root, _, files in os.walk(repo_path):
            for file in files:
                if not file.endswith(".py"):
                    continue

                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Very conservative replacement
                if missing_name in content and "def " not in missing_name:
                    fixed = content.replace(missing_name, "name")

                    if fixed != content:
                        return {
                            "target_file": os.path.relpath(path, repo_path),
                            "new_contents": fixed,
                            "justification": f"Fixed NameError: {missing_name} → name",
                            "failure_class": "name_error",
                        }

        return {}

    # ==================================================
    # MISSING FUNCTION (Phase 6A – SAFE STUB ONLY)
    # ==================================================
    match = re.search(
        r"cannot import name '(\w+)' from '(\w+)'",
        stdout
    )
    if match:
        func_name, module_name = match.groups()
        target_file = f"{module_name}.py"
        target_path = os.path.join(repo_path, target_file)

        existing = ""
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                existing = f.read()

        # Prevent duplicate stubs
        if f"def {func_name}(" in existing:
            return {}

        stub = (
            f"\n\n"
            f"def {func_name}(*args, **kwargs):\n"
            f"    \"\"\"Auto-generated stub. Logic requires human decision.\"\"\"\n"
            f"    raise NotImplementedError(\n"
            f"        \"Function '{func_name}' requires semantic implementation\"\n"
            f"    )\n"
        )

        return {
            "target_file": target_file,
            "new_contents": existing + stub,
            "justification": f"Created stub for missing function '{func_name}'",
            "failure_class": "missing_function",
        }

    # ==================================================
    # EVERYTHING ELSE IS UNSAFE
    # ==================================================
    return {}
