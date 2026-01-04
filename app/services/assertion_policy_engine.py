from typing import Dict, Any


def try_assertion_autofix(run_result: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
    stdout = run_result.get("stdout", "")

    # Heuristic: simple arithmetic add failure
    if "test_add" in stdout and "add(2,3)" in stdout and "-1 == 5" in stdout:
        return {
            "target_file": "math_utils.py",
            "new_contents": """def add(a, b):
    return a + b
""",
            "justification": "Safe arithmetic assertion fix for add()",
            "failure_class": "assertion_failure",
        }

    return {}
