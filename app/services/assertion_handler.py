from typing import Dict, Any, List


def handle_assertion_failure(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assertion failures are ambiguous by nature.
    We DO NOT auto-patch code here.

    This handler converts the failure into a clean,
    human-actionable response instead of looping.
    """

    stdout = analysis.get("stdout", "")
    failures: List[str] = []

    # Try to extract failing assertion lines
    for line in stdout.splitlines():
        if "assert " in line:
            failures.append(line.strip())

    return {
        "status": "needs_human_fix",
        "failure_class": "assertion_failure",
        "message": (
            "Assertion failure detected.\n"
            "Automatic patching is unsafe because expected behavior is ambiguous."
        ),
        "assertions": failures,
        "suggestions": [
            "Decide whether the test expectation is correct",
            "If test is correct → fix implementation",
            "If implementation is correct → update test",
        ],
    }
