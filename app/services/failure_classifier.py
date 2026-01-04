def classify_failure(run_result):
    stdout = run_result.get("stdout", "")

    if "NameError" in stdout:
        return "name_error"

    if "cannot import name" in stdout:
        return "missing_function"

    if "AssertionError" in stdout:
        return "assertion_failure"

    return "unknown"
