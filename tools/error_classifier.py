def classify_failure(pytest_output: str):
    if "ModuleNotFoundError" in pytest_output:
        return {
            "class": "import_error",
            "auto_fix": True,
            "reason": "Missing module or incorrect import path"
        }

    if "AssertionError" in pytest_output:
        return {
            "class": "test_assertion_failure",
            "auto_fix": True,
            "reason": "Logic error detected by tests"
        }

    if "SyntaxError" in pytest_output:
        return {
            "class": "syntax_error",
            "auto_fix": True,
            "reason": "Invalid Python syntax"
        }

    return {
        "class": "unknown",
        "auto_fix": False,
        "reason": "Failure could not be safely classified"
    }
