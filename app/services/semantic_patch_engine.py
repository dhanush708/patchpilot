import re
from typing import Dict, Any

SAFE_FUNCTIONS = {
    "add": lambda a, b: f"return {a} + {b}",
    "multiply": lambda a, b: f"return {a} * {b}",
}

def try_semantic_patch(analysis: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
    stdout = analysis.get("stdout", "")

    # detect multiply test
    m = re.search(r"assert\s+(\w+)\((\d+),\s*(\d+)\)\s*==\s*(\d+)", stdout)
    if not m:
        return {}

    func, a, b, expected = m.groups()

    if func not in SAFE_FUNCTIONS:
        return {}

    logic = SAFE_FUNCTIONS[func]("a", "b")

    return {
        "target_file": "math_utils.py",
        "new_contents": f"""
def {func}(a, b):
    {logic}
""".strip(),
        "justification": f"Semantic fix inferred from test for {func}",
        "failure_class": "semantic_logic",
    }
