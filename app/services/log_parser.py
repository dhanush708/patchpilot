def analyze_run(run_result):
    return {
        "stdout": run_result.get("stdout", ""),
        "stderr": run_result.get("stderr", ""),
    }