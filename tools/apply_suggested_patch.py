import json, os
from app.services.patch_suggester import suggest_patch_from_run

repo_path = r"C:\Users\DHANUSH ANBU\Desktop\patchpilot\workdir\b49c11c1-b445-4082-98be-90e1ef14890f"
report_path = os.path.join(repo_path, "report.json")
run_result = {}
if os.path.exists(report_path):
    with open(report_path, "r", encoding="utf-8") as fh:
        run_result = {"report_json": json.load(fh)}

patch = suggest_patch_from_run(run_result, repo_path)

if patch.get("target_file") and patch.get("new_contents"):
    abs_target = os.path.join(repo_path, patch["target_file"])
    os.makedirs(os.path.dirname(abs_target), exist_ok=True)
    if os.path.exists(abs_target):
        os.rename(abs_target, abs_target + ".bak")
    with open(abs_target, "w", encoding="utf-8") as fh:
        fh.write(patch["new_contents"])
    print("WROTE:", abs_target)
    print("Justification:", patch.get("justification"))
else:
    print("No patch suggested.")
