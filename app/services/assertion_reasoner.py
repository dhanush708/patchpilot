import re
from typing import Dict, Any, List


def reason_about_assertion(analysis: Dict[str, Any]) -> List[str]:
    """
    Analyze assertion failure and produce human-readable suggestions.
    """
    output = analysis.get("stdout", "")

    suggestions = []

    # Detect simple equality assertion
    m = re.search(r"assert\s+(\w+)\s*==\s*['\"](.+?)['\"]", output)
    if m:
        var = m.group(1)
        expected = m.group(2)

        suggestions.append(
            f"Define variable '{var}' with value '{expected}'"
        )
        suggestions.append(
            f"Check where '{var}' is assigned; it may be missing or incorrect"
        )
        suggestions.append(
            "Verify whether the test expectation is correct"
        )

    else:
        suggestions.append(
            "Assertion failed but pattern could not be analyzed automatically"
        )

    return suggestions
