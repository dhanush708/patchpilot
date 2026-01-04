import os
import subprocess
from typing import Dict, Any

from app.services.log_parser import analyze_run
from app.services.patch_suggester import suggest_patch_from_run
from app.services.failure_classifier import classify_failure
from app.services.generic_patch_engine import generate_patch
from app.services.decision_report import build_decision_report
from app.services.semantic_patch_engine import try_semantic_patch



def _run_pytest(workdir: str) -> Dict[str, Any]:
    proc = subprocess.run(
        ["python", "-m", "pytest", "-q"],
        cwd=workdir,
        capture_output=True,
        text=True
    )

    return {
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def run_patch_pipeline(repo_path: str, max_passes: int = 3) -> Dict[str, Any]:
    history = []
    seen_patches = set()

    for attempt in range(1, max_passes + 1):
        run_result = _run_pytest(repo_path)

        # ✅ SUCCESS
        if run_result["exit_code"] == 0:
            return {
                "status": "fixed",
                "passes_used": attempt - 1,
                "stdout": run_result["stdout"],
                "history": history,
            }

        analysis = analyze_run(run_result)
        failure_class = classify_failure(run_result)

        # 1️⃣ Deterministic patch
        patch = suggest_patch_from_run(
            run_result=run_result,
            repo_path=repo_path,
            failure_class=failure_class,
        )

        # 2️⃣ Generic safe patch
        if not patch:
            patch = generate_patch(
                failure_class=failure_class,
                analysis=analysis,
                repo_path=repo_path,
            )

        # 🚨 Escalate with explanation
        if not patch or "new_contents" not in patch:
            decision = build_decision_report(
                failure_class=failure_class,
                analysis=analysis,
            )

            return {
                "status": "needs_human_fix",
                "analysis": analysis,
                "decision": decision,
                "history": history,
            }

        patch_key = (patch["target_file"], patch["new_contents"])
        if patch_key in seen_patches:
            return {
                "status": "failed",
                "reason": "Patch loop detected",
                "analysis": analysis,
                "history": history,
            }

        seen_patches.add(patch_key)

        # APPLY PATCH
        target_path = os.path.join(repo_path, patch["target_file"])
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        before = ""
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                before = f.read()

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(patch["new_contents"])

        changed = before != patch["new_contents"]

        history.append({
            "attempt": attempt,
            "target": patch["target_file"],
            "changed": changed,
            "justification": patch.get("justification"),
            "failure_class": failure_class,
        })

        if not changed:
            return {
                "status": "failed",
                "reason": "Patch made no changes",
                "analysis": analysis,
                "history": history,
            }

    return {
        "status": "failed",
        "reason": "Max passes reached",
        "history": history,

    }
    if not patch:
        patch = try_semantic_patch(analysis, repo_path)

