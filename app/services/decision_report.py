from typing import Dict, Any, List


def build_decision_report(
    failure_class: str,
    analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a structured explanation of why auto-fix stopped
    and what decision is required from a human.
    """

    stdout = analysis.get("stdout", "")

    report = {
        "failure_class": failure_class,
        "auto_fix_stopped": True,
        "reason": "",
        "required_human_action": "",
        "confidence": "high",
    }

    # ------------------------------
    # Assertion / semantic failures
    # ------------------------------
    if "AssertionError" in stdout or "NotImplementedError" in stdout:
        report["reason"] = (
            "Test failure requires semantic understanding. "
            "Automatic fixes may change intended behavior."
        )
        report["required_human_action"] = (
            "Decide correct business logic and implement function accordingly."
        )
        return report

    # ------------------------------
    # Unknown failures
    # ------------------------------
    report["reason"] = "Failure could not be safely classified."
    report["required_human_action"] = "Manual investigation required."

    return report
