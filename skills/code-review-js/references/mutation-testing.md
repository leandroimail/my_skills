# Mutation Testing in Code Review — StrykerJS for TypeScript/JavaScript

## Table of Contents

- [What Reviewers Check](#what-reviewers-check)
- [Installation](#installation)
- [Running Stryker on Changed Code](#running-stryker-on-changed-code)
- [Interpreting Results](#interpreting-results)
- [Score Thresholds and Severity](#score-thresholds-and-severity)
- [Formatting Mutation Findings](#formatting-mutation-findings)
- [Common Weak Test Patterns](#common-weak-test-patterns)

---

## What Reviewers Check

Three checks in order:

1. **Was Stryker run?** — Check for `reports/mutation/` output or CI run results. If absent, run it yourself on the changed modules.
2. **Is the score ≥ 30%?** — Minimum accepted gate. Score below 30% = 🟡 Important finding.
3. **Do critical paths have survived mutants on comparison operators or return values?** — Flag individually even if the aggregate score passes.

Mutation testing complements line coverage. A module can have 80% line coverage and 0% mutation score — tests execute the code but never verify its behavior.

---

## Installation

```bash
# Add as dev dependencies (if not already present)
npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner
# For Vitest projects: @stryker-mutator/vitest-runner
```

Configure scope in `stryker.config.json` to avoid mutating test files or boilerplate:

```json
{
  "$schema": "https://raw.githubusercontent.com/stryker-mutator/stryker-js/master/packages/api/schema/stryker-core.json",
  "testRunner": "jest",
  "mutate": ["src/**/*.ts", "!src/**/*.spec.ts", "!src/**/*.test.ts", "!src/**/*.d.ts"],
  "coverageAnalysis": "perTest",
  "reporters": ["html", "clear-text", "progress"],
  "thresholds": { "high": 80, "low": 60, "break": 30 }
}
```

`coverageAnalysis: "perTest"` runs only the tests covering each mutant — critical for keeping review runs fast. `thresholds.break` makes the run exit non-zero below the gate.

---

## Running Stryker on Changed Code

**Never run on all of `src/` during a review** — it can take hours. Scope to the files changed in the PR.

```bash
# Step 1: identify changed source files
git diff --name-only HEAD~1 | grep -E "^(src|apps|libs)/.*\.tsx?$" | grep -v ".spec."

# Step 2: run Stryker only on those files
npx stryker run --mutate "src/services/pricing.ts"

# For a changed directory
npx stryker run --mutate "src/services/**/*.ts"

# Step 3: open the report (lists every mutant with status)
open reports/mutation/mutation.html

# Incremental mode: reuses previous results, only re-tests affected mutants
npx stryker run --incremental
```

In an Nx monorepo, run per project with a project-level `stryker.config.json`
(e.g. `apps/core/stryker.config.json`) so `mutate` globs and the Jest config
resolve within that project.

---

## Interpreting Results

```
Ran 4.12 tests per mutant on average.
------------------|---------|----------|-----------|------------|----------|
File              | % score | # killed | # timeout | # survived | # no cov |
------------------|---------|----------|-----------|------------|----------|
src/pricing.ts    |   90.00 |       36 |         1 |          4 |        1 |
```

Key terms:

| Term | Meaning |
|------|---------|
| **Killed** | A test failed when this mutation was applied. The test is effective. |
| **Survived** | All tests passed with the mutation. The test doesn't verify this behavior. |
| **Timeout** | Mutation caused an infinite loop. Treated as killed. |
| **No coverage** | No test exercises this line at all. Separate from mutation score — report as a coverage gap. |
| **Equivalent mutant** | Mutation changes code but not behavior (e.g., `i += 1` → `i = i + 1`). Cannot be killed. Exclude from score with a `// Stryker disable next-line` comment plus reason. |

The mutation score = killed / (killed + survived) × 100. Timeouts count as killed; no-coverage mutants are reported separately (they lower the "score based on covered code" vs total score distinction in the report).

---

## Score Thresholds and Severity

| Score | Status | Severity | Action |
|-------|--------|----------|--------|
| ≥ 80% | Excellent | ✅ Pass | No action |
| ≥ 30% | Minimum accepted | ✅ Pass | Note score in review |
| < 30% | Below minimum | 🟡 Important | Strengthen tests before merge |
| Never run | Not evaluated | 🟡 Important | Run Stryker and bring to ≥ 30% |

**Note:** 30% is the minimum review gate. For business-critical modules (auth, pricing, billing, data access), target 80%+. Flag the gap as 🟢 Suggestion even if the 30% gate passes.

---

## Formatting Mutation Findings

Use the standard review finding format: `[SEVERITY] File:line — Issue → Suggested fix`

**Below minimum score:**
```
🟡 src/services/pricing.ts — Mutation score 12% (below 30% minimum)
   Run: npx stryker run --mutate "src/services/pricing.ts"
   → Strengthen assertions; current tests execute code but don't pin values
```

**Specific surviving mutant:**
```
🟡 src/services/pricing.ts:34 — Survived mutant: `price > 0` → `price >= 0`
   (see reports/mutation/mutation.html)
   → Add boundary test: expect(calculatePrice(0)).toThrow()
     (currently only tested with price=100)
```

**Never run:**
```
🟡 src/services/discount.ts — No mutation testing found for this module
   Run: npx stryker run --mutate "src/services/discount.ts"
   → Score must be ≥ 30% before merge
```

---

## Common Weak Test Patterns

These patterns almost always produce surviving mutants. Flag them even without running Stryker:

### Truthiness assertions only

```typescript
// ❌ Survives arithmetic and return-value mutations
expect(result).toBeDefined();
expect(items.length).toBeGreaterThan(0);
expect(response.ok).toBeTruthy();
```

Replace with exact value assertions: `expect(result).toEqual(expectedValue)` /
`expect(items).toHaveLength(3)`.

### Single-path tests for comparison operators

```typescript
// ❌ Survives `price > 0` → `price >= 0` because test uses price=100
it('accepts a valid price', () => {
  expect(isValidPrice(100)).toBe(true);
});
```

Add boundary tests: at threshold, just above, just below.

```typescript
// ✅ Kills the >= mutation
it('validates price at the zero boundary', () => {
  expect(isValidPrice(1)).toBe(true);   // just above zero
  expect(isValidPrice(0)).toBe(false);  // at zero — kills >= mutation
  expect(isValidPrice(-1)).toBe(false); // below zero
});
```

### Boolean conditions tested only with both true

```typescript
// ❌ Survives `active && verified` → `active || verified`
it('marks user as eligible', () => {
  const user = { active: true, verified: true };
  expect(isEligible(user)).toBe(true);
});
```

Add cases where exactly one condition is false to kill the `||` mutation.

### No inverse assertion

```typescript
// ❌ Survives rename mutations — old key may still exist
it('renames the column', () => {
  const result = transform(payload);
  expect(result).toHaveProperty('newField'); // Weak: only checks presence
});
```

Add: `expect(result).not.toHaveProperty('oldField')` — catches mutations that add but don't remove.

### Optional chaining and nullish defaults never exercised

```typescript
// ❌ Survives `??` → `||` and `?.` removal — tests never pass null/0/''
it('formats the label', () => {
  expect(formatLabel({ name: 'X' })).toBe('X');
});
```

Add cases with `undefined`, `null`, `0`, and `''` inputs — `??` vs `||`
mutations only die when a falsy-but-defined value flows through.
