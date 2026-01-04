import sys
from app.services.patch_pipeline import run_patch_pipeline

JOBDIR = sys.argv[1] if len(sys.argv) > 1 else "workdir/demo_bug"

result = run_patch_pipeline(JOBDIR)
print(result)
