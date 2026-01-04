{
  "repo": "real_repo_example",
  "status": "needs_human_decision",
  "failure_class": "semantic_logic_required",
  "failed_test": "test_multiply",
  "error": "multiply(2,3) returned NotImplementedError",
  "auto_actions_taken": [
    "Detected missing function multiply",
    "Created safe stub",
    "Re-ran tests"
  ],
  "why_automation_stopped": "Function logic cannot be inferred safely from tests alone",
  "human_options": [
    {
      "option": "Implement multiply as arithmetic multiplication",
      "risk": "Low",
      "example_patch": "def multiply(a, b): return a * b"
    },
    {
      "option": "Confirm multiply behavior with domain owner",
      "risk": "None",
      "example_patch": "Pending clarification"
    }
  ],
  "recommended_action": "Option 1"
}
