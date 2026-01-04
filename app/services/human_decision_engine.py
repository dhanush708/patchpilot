from typing import Dict, Any, List

def propose_human_fixes(analysis: Dict[str, Any]) -> List[str]:
    """
    Suggest next steps when automatic patching is unsafe.
    """

    stdout = analysis.get("stdout", "")

    suggestions = []

    if "AssertionError" in stdout:
        suggestions.extend([
            "Check whether the test expectation is correct",
            "Verify the function logic that produces the asserted value",
            "Decide whether the test or implementation should change",
        ])

    elif "ImportError" in stdout or "ModuleNotFoundError" in stdout:
        suggestions.extend([
            "Check missing imports or undefined functions",
            "Verify module filenames and exported symbols",
            "Add the missing function or correct the import",
        ])

    elif "NameError" in stdout:
        suggestions.extend([
            "Check for variable or function name typos",
            "Ensure variables are defined before use",
        ])

    else:
        suggestions.append("Manual inspection required")

    return suggestions
