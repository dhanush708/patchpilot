from typing import Dict, Any


def summarize_repo_failure(run_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce a human-readable explanation of why the repo could not be fixed safely.
    """

    stdout = run_result.get("stdout", "")
    summary = {
        "reason": "Automatic fixing stopped to avoid unsafe changes",
        "detected_issues": [],
        "recommendation": [],
    }

    if "AssertionError" in stdout:
        summary["detected_issues"].append(
            "Assertion failures indicate unclear expected behavior"
        )
        summary["recommendation"].append(
            "Decide whether the implementation or the test is correct"
        )

    if "NameError" in stdout:
        summary["detected_issues"].append(
            "NameError indicates a variable or symbol mismatch"
        )
        summary["recommendation"].append(
            "Rename variables consistently or correct the reference"
        )

    if not summary["detected_issues"]:
        summary["detected_issues"].append(
            "Failure type could not be classified safely"
        )
        summary["recommendation"].append(
            "Manual inspection required"
        )

    return summary
