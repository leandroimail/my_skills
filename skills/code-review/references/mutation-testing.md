# Mutation Testing in Code Review — mutmut for Python

## Table of Contents

- [What Reviewers Check](#what-reviewers-check)
- [Installation](#installation)
- [Running mutmut on Changed Code](#running-mutmut-on-changed-code)
- [Interpreting Results](#interpreting-results)
- [Score Thresholds and Severity](#score-thresholds-and-severity)
- [Formatting Mutation Findings](#formatting-mutation-findings)
- [Common Weak Test Patterns](#common-weak-test-patterns)

---

## What Reviewers Check

Three checks in order:

1. **Was mutmut run?** — Check for `html/` report or CI run results. If absent, run it yourself on the changed modules.
2. **Is the score ≥ 30%?** — Minimum accepted gate. Score below 30% = 🟡 Important finding.
3. **Do critical paths have survived mutants on comparison operators or return values?** — Flag individually even if the aggregate score passes.

Mutation testing complements line coverage. A module can have 80% line coverage and 0% mutation score — tests execute the code but never verify its behavior.

---

## Installation

```bash
# Add as dev dependency (if not already present)
uv add --dev mutmut
```

Configure scope in `pyproject.toml` to avoid running on test files or boilerplate:

```toml
[tool.mutmut]
paths_to_mutate = "src/"
tests_dir = "tests/"
runner = "uv run pytest -x -q"
```

`-x` makes mutmut exit on first failure per mutant — critical for keeping review runs fast.

---

## Running mutmut on Changed Code

**Never run on all of `src/` during a review** — it can take hours. Scope to the files changed in the PR.

```bash
# Step 1: identify changed source files
git diff --name-only HEAD~1 | grep "^src/.*\.py$"

# Step 2: run mutmut only on those files
uv run mutmut run --paths-to-mutate src/models/pricing.py

# For a changed directory
uv run mutmut run --paths-to-mutate src/models/

# Step 3: view results summary
uv run mutmut results

# Step 4: inspect individual surviving mutant
uv run mutmut show <id>

# Step 5: generate HTML report (optional, useful for large PRs)
uv run mutmut html && open html/index.html
```

If the PR has no `pyproject.toml` `[tool.mutmut]` section, pass the test runner explicitly:

```bash
uv run mutmut run --paths-to-mutate src/models/pricing.py \
  --test-command "uv run pytest tests/ -x -q"
```

---

## Interpreting Results

```
Found 42 mutants, now testing
- Killed:       36  ✅ tests caught these — good
- Survived:      4  ❌ tests missed these — flag in review
- Timeout:       1  treated as killed
- No coverage:   1  no test executes this line — flag as missing coverage
Mutation score: 90%   (= 36 / (36+4) × 100%)
```

Key terms:

| Term | Meaning |
|------|---------|
| **Killed** | A test failed when this mutation was applied. The test is effective. |
| **Survived** | All tests passed with the mutation. The test doesn't verify this behavior. |
| **Timeout** | Mutation caused an infinite loop. Treated as killed. |
| **No coverage** | No test exercises this line at all. Separate from mutation score — report as a coverage gap. |
| **Equivalent mutant** | Mutation changes code but not behavior (e.g., `i += 1` → `i = i + 1`). Cannot be killed. Exclude from score. |

Mutation score only counts killed and survived — timeouts and no-coverage mutants are excluded.

---

## Score Thresholds and Severity

| Score | Status | Severity | Action |
|-------|--------|----------|--------|
| ≥ 80% | Excellent | ✅ Pass | No action |
| ≥ 30% | Minimum accepted | ✅ Pass | Note score in review |
| < 30% | Below minimum | 🟡 Important | Strengthen tests before merge |
| Never run | Not evaluated | 🟡 Important | Run mutmut and bring to ≥ 30% |

**Note:** 30% is the minimum review gate. For business-critical modules (auth, pricing, data pipelines), target 80%+. Flag the gap as 🟢 Suggestion even if the 30% gate passes.

---

## Formatting Mutation Findings

Use the standard review finding format: `[SEVERITY] File:line — Issue → Suggested fix`

**Below minimum score:**
```
🟡 src/models/pricing.py — Mutation score 12% (below 30% minimum)
   Run: uv run mutmut run --paths-to-mutate src/models/pricing.py
   → Strengthen assertions; current tests execute code but don't pin values
```

**Specific surviving mutant:**
```
🟡 src/models/pricing.py:34 — Survived mutant: `price > 0` → `price >= 0`
   uv run mutmut show 7
   → Add boundary test: assert calculate_price(0) raises ValueError
     (currently only tested with price=100)
```

**Never run:**
```
🟡 src/services/discount.py — No mutation testing found for this module
   Run: uv run mutmut run --paths-to-mutate src/services/discount.py
   → Score must be ≥ 30% before merge
```

---

## Common Weak Test Patterns

These patterns almost always produce surviving mutants. Flag them even without running mutmut:

### Truthiness assertions only

```python
# ❌ Survives arithmetic and return-value mutations
assert result is not None
assert len(items) > 0
assert response.ok
```

Replace with exact value assertions: `assert result == expected_value`

### Single-path tests for comparison operators

```python
# ❌ Survives `price > 0` → `price >= 0` because test uses price=100
def test_valid_price():
    assert is_valid_price(100) is True
```

Add boundary tests: at threshold, just above, just below.

```python
# ✅ Kills the >= mutation
def test_valid_price_boundary():
    assert is_valid_price(1)  is True   # just above zero
    assert is_valid_price(0)  is False  # at zero — kills >= mutation
    assert is_valid_price(-1) is False  # below zero
```

### Boolean conditions tested only with both true

```python
# ❌ Survives `active and verified` → `active or verified`
def test_user_eligible():
    user = User(active=True, verified=True)
    assert is_eligible(user) is True
```

Add cases where exactly one condition is false to kill the `or` mutation.

### No inverse assertion

```python
# ❌ Survives column rename mutations — old name may still exist
def test_column_renamed():
    result = transform(df)
    assert "new_col" in result.columns  # Weak: only checks presence
```

Add: `assert "old_col" not in result.columns` — catches mutations that add but don't remove.
