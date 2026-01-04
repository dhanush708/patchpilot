from typing import Dict, Any, List
import re

def propose_semantic_fixes(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    stdout = analysis.get("stdout", "")
    proposals = []

    # Detect NotImplementedError from stub
    match = re.search(
        r"NotImplementedError: Function '(\w+)' not implemented",
        stdout
    )

    if match:
        func = match.group(1)
        proposals.append({
            "type": "semantic_logic_required",
            "message": f"The function '{func}' is missing real logic.",
            "suggestion": f"Implement '{func}' according to test expectations.",
            "confidence": "high"
        })

    # Detect assertion mismatches
    if "AssertionError" in stdout:
        proposals.append({
            "type": "assertion_failure",
            "message": "Test assertion failed.",
            "suggestion": "Decide whether test or implementation is correct.",
            "confidence": "medium"
        })

    return proposals