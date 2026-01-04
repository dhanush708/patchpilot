# PatchPilot 🚀
Verification-Driven Auto-Patching for Python Repositories

PatchPilot is a **local analysis system** that runs tests, attempts **only safe automated fixes**, and **stops immediately when human judgment is required**.

This project is intentionally conservative.  
If a fix cannot be applied with high confidence, PatchPilot **refuses to guess**.

---

## Why PatchPilot Exists

In real-world Python projects, CI pipelines frequently fail due to:

- Broken import paths
- Missing `__init__.py` files
- Incorrect package structure
- Test discovery failures

Most auto-fix tools either:
- Apply unsafe changes, or
- Hide failures behind false “success” states

**PatchPilot does neither.**

It exists to answer one question reliably:

> *“Is this failure safe to fix automatically — or should a human step in?”*

---

## What PatchPilot Does

- Runs `pytest` automatically on an uploaded repository
- Captures full test output (stdout + stderr)
- Applies **deterministic, non-semantic fixes only**
- Re-runs tests to verify every applied fix
- Stops immediately when ambiguity is detected
- Never loops infinitely
- Never installs dependencies
- Never accesses the internet

---

## What PatchPilot Does *Not* Do

- No semantic code changes
- No logic refactors
- No dependency installation
- No architectural guessing
- No silent retries

If a fix would require assumptions → **PatchPilot stops**.

---

## Output States

PatchPilot reports one of the following final states:

### ✅ FIXED
- All tests passed
- Either no fix was required, or
- A safe automated fix was applied and verified

### ❌ FAILED
- Tests failed
- No safe automated fix exists
- Full test output is shown for human review

There is **no “partial success” state**.

---

## Example of a Refused Fix (Intentional)

```python
from app.calculator import divide
```

If:
- The module path does not exist
- Multiple fixes are possible
- Fixing requires guessing intent

PatchPilot refuses to act.

This is a design decision, not a limitation.

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
python server.py
```

### 3. Use the Web UI
Open http://127.0.0.1:5000

- Upload a `.zip` Python repository containing `pytest` tests
- View the execution result and output location

---

## Limitations (Intentional)

- Python repositories only
- `.zip` uploads only (`.rar` blocked)
- Requires pytest-based tests
- No internet access during execution
- Structural fixes only
- Complex logic requires human review

These constraints are intentional safeguards, not missing features.

---

## Who This Project Is For

- Backend engineers
- CI/CD maintainers
- Teams evaluating automated repair systems
- Recruiters assessing real-world engineering judgment

PatchPilot is designed to demonstrate **when automation should stop**, not just when it should act.

---

## Engineering Details

For a deep, engineering-level explanation of:
- Architecture
- Failure classification
- Safety guarantees
- Fix verification logic
- Design trade-offs

👉 See **ENGINEERING.md**

---

## Project Status

- Fully local
- Fully deterministic
- No external services
- Safe by design

This project prioritizes **correctness over coverage**.

---

## Author

Built entirely by **Dhanush**  
Designed, implemented, tested, and validated end-to-end as a **solo engineering project**.

---

## License

See `LICENSE` for details.
