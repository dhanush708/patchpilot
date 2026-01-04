# PatchPilot — Engineering Design & Internals

This document describes the **engineering decisions, constraints, and internal architecture** of PatchPilot.

PatchPilot is not a generic auto-fix tool.  
It is a **verification-driven system** that prioritizes correctness and safety over automation coverage.

---

## 1. Design Philosophy

PatchPilot follows three core principles:

1. **Verification over modification**
2. **Safety over coverage**
3. **Explicit failure over silent guessing**

Any automated change must:
- Be deterministic
- Be non-semantic
- Be fully verifiable via tests

If these conditions are not met, PatchPilot **intentionally stops**.

---

## 2. High-Level Architecture

```
User Upload (.zip)
        |
        v
Repository Extraction
        |
        v
Pytest Execution
        |
        v
Failure Classification
        |
        +--> Safe Fix Available?
                |
        +-------+-------+
        |               |
       YES              NO
        |               |
        v               v
 Apply Fix           FAILED
        |
        v
 Re-run Tests
        |
        v
 Tests Pass?
        |
   +----+----+
   |         |
  YES        NO
   |         |
 FIXED     FAILED
```

There is **no retry loop** and **no heuristic guessing**.

---

## 3. Execution Flow

### Step 1: Repository Isolation

- Uploaded `.zip` is extracted into a unique `workdir/<uuid>`
- Each run is fully isolated
- No shared state between executions

### Step 2: Pytest Execution

- `pytest` is executed via `subprocess`
- `PYTHONPATH` is explicitly set to the repository root
- Both stdout and stderr are captured

This ensures:
- Correct import resolution
- Full visibility into test failures

---

## 4. Failure Classification

PatchPilot currently recognizes **one class of safe auto-fix**.

### 4.1 Missing Package Initialization

Example failure:
```text
ModuleNotFoundError: No module named 'package'
```

This often indicates:
- Missing `__init__.py`
- Incorrect package discovery

#### Safe Fix Criteria

A fix is considered safe only if:
- It does not modify executable logic
- It only affects package structure
- It does not require guessing import intent

#### Implementation

- Traverse repository directories
- Add missing `__init__.py` files
- Re-run tests to verify correctness

If tests still fail → **FAILED**

---

## 5. Why PatchPilot Refuses Certain Fixes

Example refused case:
```python
from app.calculator import divide
```

When:
- The module path does not exist
- Multiple possible fixes exist
- Fix requires architectural assumptions

PatchPilot stops because:
- Choosing a path would be semantic
- Automated guessing is unsafe
- Human intent is required

This refusal is intentional and correct.

---

## 6. Output Semantics

PatchPilot reports **exactly one** of the following states:

### FIXED
- Tests passed
- Either no fixes were required, or
- A safe fix was applied and verified

### FAILED
- Tests failed
- No safe automated fix exists
- Full pytest output is provided

There is **no partial success state**.

---

## 7. Why There Is No “NEEDS_HUMAN_FIX” State Internally

Internally, PatchPilot collapses ambiguity into **FAILED**.

Rationale:
- From an engineering perspective, ambiguous = unsafe
- From a CI perspective, failed is explicit and actionable
- UI labels are secondary to correctness

---

## 8. Security & Isolation Guarantees

- No internet access during execution
- No dependency installation at runtime
- No shell injection surface
- No modification outside the working directory

PatchPilot is safe to run locally or inside CI sandboxes.

---

## 9. Limitations (By Design)

- Python repositories only
- Requires pytest-based tests
- Structural fixes only
- No semantic refactors
- No dependency resolution
- No speculative repair

These are **deliberate constraints**, not missing features.

---

## 10. Extensibility

PatchPilot is designed to be extended via:
- Additional failure classifiers
- Explicit fix rules per classifier
- Mandatory verification after each fix

Any extension must preserve:
- Determinism
- Verifiability
- Zero-guess policy

---

## 11. Intended Use Cases

- CI pre-validation
- Failure triage automation
- Repair system evaluation
- Engineering judgment assessment

PatchPilot is **not** a replacement for developers.  
It is a **guardrail against unsafe automation**.

---

## 12. Author Notes

PatchPilot was designed, implemented, tested, and validated as a **solo engineering project**.

The primary goal was **not feature breadth**, but **engineering correctness and restraint**.

This project intentionally demonstrates:
- Systems thinking
- Safety-first automation
- Real-world CI failure handling
- Knowing when **not** to automate
Build by Dhanush A
