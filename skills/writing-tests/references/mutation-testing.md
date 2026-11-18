# Mutation Testing with mutmut for Python

## Table of Contents

- [Core Concepts](#core-concepts)
- [Installation and Configuration](#installation-and-configuration)
- [Running mutmut](#running-mutmut)
- [Understanding Results](#understanding-results)
- [Mutation Score Targets](#mutation-score-targets)
- [Improving Weak Tests](#improving-weak-tests)
- [Common Python Mutation Types](#common-python-mutation-types)
- [Workflow](#workflow)
- [Best Practices](#best-practices)

---

## Core Concepts

| Term | Meaning | Desired Outcome |
|------|---------|-----------------|
| **Mutant** | Automated small code change (e.g., `>` → `>=`) | — |
| **Killed** | Test fails when mutant is active | ✅ Good — test detected the bug |
| **Survived** | Test passes despite the mutation | ❌ Bad — weak or missing assertion |
| **Timeout** | Mutant causes an infinite loop | Treated as killed |
| **No coverage** | No test exercises the mutated line | Fix coverage first |
| **Equivalent** | Mutation changes code but not behavior | Mark to exclude from score |
| **Score** | `killed / (killed + survived)` × 100% | Target 80%+ |

Survived mutants are not bugs in production code — they are gaps in your test suite. Each one reveals an assertion you haven't written.

---

## Installation and Configuration

```bash
# Add mutmut as a dev dependency
pip install mutmut
```

Configure mutmut scope in `pyproject.toml` to target only production code:

```toml
[tool.mutmut]
paths_to_mutate = "src/"
tests_dir = "tests/"
runner = "pytest -x -q"
```

`-x` (stop on first failure) is critical — it makes mutmut exit as soon as a test catches the mutant, keeping runs fast. `-q` reduces output noise per mutant run.

To target a single module with stricter coverage:

```toml
[tool.mutmut]
paths_to_mutate = "src/myproject/processing.py"
tests_dir = "tests/unit/"
runner = "pytest -x -q --no-header"
```

> Using the `uv` runner? Set `runner = "uv run pytest -x -q"` and prefix the
> mutmut commands below with `uv run`.

---

## Running mutmut

```bash
# Run mutation testing on all configured source paths
mutmut run

# Run on a single module only (overrides pyproject.toml paths_to_mutate)
mutmut run --paths-to-mutate src/myproject/processing.py

# Show summary of all results
mutmut results

# Inspect a specific surviving mutant diff
mutmut show 42

# Apply a surviving mutant to the source tree for manual inspection
mutmut apply 42
# Undo the applied mutant
mutmut unapply 42

# Generate HTML report (opens as html/index.html)
mutmut html
open html/index.html
```

---

## Understanding Results

```
Found 42 mutants, now testing
- Killed:      36  ✅ tests caught these
- Survived:     4  ❌ tests missed these — these need your attention
- Timeout:      1  treated as killed
- No coverage:  1  not reachable by any test
Mutation score: 90%
```

For each surviving mutant, `mutmut show <id>` shows the exact diff:

```diff
# mutmut show 7
--- src/myproject/service.py
+++ src/myproject/service.py
@@ -12,7 +12,7 @@
-    if value > 70:
+    if value >= 70:
         return "HIGH"
```

This tells you: your test suite passes even when the HIGH boundary shifts from `> 70` to `>= 70`. A record with value exactly 70 would be wrongly classified as HIGH in production — and your test wouldn't catch it.

---

## Mutation Score Targets

| Score | Quality | Action |
|-------|---------|--------|
| 90%+ | Excellent | Maintain — minor refinements only |
| 80–89% | Good | Review survived mutants for easy boundary wins |
| 70–79% | Acceptable | Focus on comparison and return-value assertions |
| 60–69% | Poor | Tests check execution, not behavior — add exact assertions |
| < 60% | Critical | Tests are structural scaffolding, not quality gates |

Critical modules with 100% line coverage (e.g. `processing.py`, `service.py`) should also target 80%+ mutation score.

---

## Improving Weak Tests

### Pattern: Missing Exact Value Assertions

The most common cause of surviving mutants: test executes the code path but never pins the output.

```python
# ❌ WEAK: Column rename logic survives any mutation
def test_column_rename():
    df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=3, freq="h")})
    result = normalize_records(df)
    assert result is not None  # Any output passes — mutations invisible

# ✅ STRONG: Pins the exact output column name
def test_column_rename_time_to_timestamp():
    df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=3, freq="h")})
    result = normalize_records(df)
    assert "timestamp" in result.columns      # Must rename to "timestamp"
    assert "time" not in result.columns        # Must remove original column too
```

### Pattern: Missing Boundary Assertions for Comparisons

Arithmetic and comparison mutations always survive without boundary tests.

```python
# ❌ WEAK: value > 70 → value >= 70 mutation survives
def test_classify_high():
    label = classify_value(80, threshold_high=70, threshold_low=30)
    assert label == "HIGH"  # 80 also qualifies under >=70 — mutation invisible

# ✅ STRONG: Pins the boundary — value exactly at 70 must NOT classify as HIGH
def test_classify_high_boundary():
    label_above = classify_value(71, threshold_high=70, threshold_low=30)  # just above
    label_at    = classify_value(70, threshold_high=70, threshold_low=30)  # at threshold
    label_below = classify_value(69, threshold_high=70, threshold_low=30)  # just below

    assert label_above == "HIGH"    # > 70: classifies HIGH
    assert label_at    != "HIGH"    # = 70: boundary, must NOT classify HIGH (catches >= mutation)
    assert label_below != "HIGH"    # < 70: not HIGH
```

### Pattern: Boolean Logic Mutations

`and` → `or` mutations survive without tests that differentiate partial conditions.

```python
# ❌ WEAK: `min_value <= value and value <= max_value` → `... or ...` survives
def test_valid_record():
    record = {"min_value": 99.0, "value": 100.5, "max_value": 101.0}
    assert is_valid_record(record) is True  # Only tests the happy path

# ✅ STRONG: Tests cases where only one condition is true
def test_valid_record_requires_both_conditions():
    valid     = {"min_value": 99.0,  "value": 100.5, "max_value": 101.0}
    too_low   = {"min_value": 101.0, "value": 100.5, "max_value": 102.0}  # value < min_value
    too_high  = {"min_value": 99.0,  "value": 100.5, "max_value": 100.0}  # value > max_value

    assert is_valid_record(valid)    is True
    assert is_valid_record(too_low)  is False  # kills `or` mutation
    assert is_valid_record(too_high) is False  # kills `or` mutation on second condition
```

### Pattern: Return Value Mutations

`return result` → `return None` or `return 0` mutations survive when tests only check truthiness.

```python
# ❌ WEAK: return 0 → return 1 mutation for empty input survives
def test_count_words_empty():
    assert count_words("") is not None  # None is also "not None" — useless

# ✅ STRONG: Pins the exact expected return value
def test_count_words_empty():
    assert count_words("") == 0         # Only 0 kills the mutation to 1
    assert count_words("   ") == 0      # Whitespace-only also zero
```

---

## Common Python Mutation Types

| Type | Example Mutation | What assertion pins it |
|------|-----------------|------------------------|
| Arithmetic | `price - fee` → `price + fee` | Exact numeric result |
| Comparison | `value > 70` → `value >= 70` | Value at boundary (70 itself) |
| Comparison | `len(df) == 0` → `len(df) != 0` | Test both empty and non-empty |
| Boolean logic | `a and b` → `a or b` | Case where only one side is true |
| Boolean logic | `not active` → `active` | Test both True and False input |
| Return value | `return result` → `return None` | `assert result == expected_value` |
| Constant | `return 0` → `return 1` | `assert result == 0`, not `assert result >= 0` |
| String | `"HIGH"` → `"XXHIGHXX"` | `assert label == "HIGH"` exactly |
| Slice | `text[:max_len]` → `text[:max_len + 1]` | Assert length and content exactly |

---

## Workflow

Mutation testing requires good line coverage first — uncovered lines produce "no coverage" mutants that inflate the survived count without revealing real test gaps. See [advanced-techniques.md](advanced-techniques.md#coverage-configuration) for pytest-cov setup.

```bash
# Step 1 — Verify ≥80% line coverage before running mutmut
pytest --cov=src --cov-fail-under=80 --cov-report=term-missing

# Step 2 — Run mutation testing on the target module
mutmut run --paths-to-mutate src/myproject/processing.py

# Step 3 — Review which mutants survived
mutmut results

# Step 4 — Inspect each survivor
mutmut show <id>   # read the diff, understand what assertion is missing

# Step 5 — Write targeted assertions to kill each surviving mutant
# Then re-run to confirm:
mutmut run --paths-to-mutate src/myproject/processing.py

# Step 6 — Generate HTML report for PR review
mutmut html && open html/index.html
```

> Using the `uv` runner? Prefix each command with `uv run`.

---

## Best Practices

### ✅ DO

- Target critical business logic first: `service.py` (classification/decision logic), `processing.py` (column mapping)
- Aim for 80%+ mutation score on all modules with 100% coverage targets
- Test boundary values explicitly: at, just above, and just below every threshold
- Assert both the positive and inverse case (column IS renamed AND old name IS absent)
- Mark equivalent mutants with a comment so the score remains interpretable
- Run `--paths-to-mutate` in CI for high-priority modules to catch regressions

### ❌ DON'T

- Run mutation testing before 80%+ line coverage — fix coverage gaps first
- Start by running mutmut on all of `src/` — pick one critical module, fix it, expand
- Accept `is not None`, `> 0`, or `toBeDefined()` as sufficient assertions
- Ignore equivalent mutants — mark them so the reported score is meaningful
- Run mutation testing on `__init__.py`, generated code, or config files
- Chase 100% mutation score — equivalent mutants make it structurally unreachable
