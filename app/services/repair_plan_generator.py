from typing import Dict, Any


def generate_repair_plan(
    failure_class: str,
    analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a human-readable repair plan instead of modifying code.
    Used when automatic patching is unsafe.
    """

    if failure_class == "assertion_failure":
        return {
            "failure_class": failure_class,
            "confidence": "low",
            "reason": "Assertion failures require semantic understanding",
            "suspected_causes": [
                "Incorrect expected value in test",
                "Bug in function logic",
                "Mismatch between test intent and implementation",
            ],
            "recommended_actions": [
                "Print actual function output",
                "Compare expected vs actual values",
                "Inspect test assumptions",
            ],
        }

    return {
        "failure_class": failure_class,
        "confidence": "unknown",
        "recommended_actions": [
            "Manual inspection required"
        ],
    }
