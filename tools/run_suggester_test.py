import json, os
from app.services.patch_suggester import suggest_patch_from_run

# CHANGE this to the job folder you used
repo_path = r"C:\Users\DHANUSH ANBU\Desktop\patchpilot\workdir\b49c11c1-b445-4082-98be-90e1ef14890f"

report_path = os.path.join(repo_path, "report.json")
run_result = {}
if os.path.exists(report_path):
    with open(report_path, "r", encoding="utf-8") as fh:
        run_result = {"report_json": json.load(fh)}

patch = suggest_patch_from_run(run_result, repo_path)
print(json.dumps(patch, indent=2))
