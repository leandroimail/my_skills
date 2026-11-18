# Mutation Testing with StrykerJS

Line coverage proves tests *execute* code. Mutation testing proves tests
*enforce behavior*: Stryker introduces small bugs (mutants) into your source
and checks whether the suite fails. Surviving mutants = assertions you don't
have.

## Table of Contents

- [Installation and Configuration](#installation-and-configuration)
- [Workflow](#workflow)
- [Mutation Types](#mutation-types)
- [Reading the Report](#reading-the-report)
- [Killing Surviving Mutants](#killing-surviving-mutants)
- [Equivalent Mutants](#equivalent-mutants)
- [Performance Tuning](#performance-tuning)
- [CI Integration](#ci-integration)

## Installation and Configuration

```bash
npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner
# Vitest projects: @stryker-mutator/vitest-runner
```

```json
// stryker.config.json
{
  "$schema": "https://raw.githubusercontent.com/stryker-mutator/stryker-js/master/packages/api/schema/stryker-core.json",
  "testRunner": "jest",
  "jest": { "configFile": "jest.config.js" },
  "mutate": [
    "src/**/*.ts",
    "!src/**/*.spec.ts",
    "!src/**/*.test.ts",
    "!src/**/*.d.ts",
    "!src/**/mocks/**",
    "!src/**/index.ts"
  ],
  "coverageAnalysis": "perTest",
  "reporters": ["html", "clear-text", "progress"],
  "thresholds": { "high": 80, "low": 60, "break": 30 }
}
```

Key options:
- `coverageAnalysis: "perTest"` — runs only the tests covering each mutant (order-of-magnitude speedup)
- `thresholds.break` — exit non-zero below this score (the CI gate)
- Nx monorepo: one `stryker.config.json` per app/lib so `mutate` globs and the
  Jest config resolve locally

## Workflow

```bash
# 1. Reach solid line coverage first (mutation testing on uncovered code is noise)
npx jest --coverage

# 2. Run Stryker scoped to the module you're hardening
npx stryker run --mutate "src/lib/services/pricing.service.ts"

# 3. Open the report and walk the survivors
open reports/mutation/mutation.html

# 4. For each survivor: add the missing assertion, re-run the focused test
npx jest src/lib/__tests__/pricing.service.test.ts

# 5. Re-run Stryker incrementally until clean
npx stryker run --incremental
```

**Order matters:** line coverage → mutation score. A survivor on an uncovered
line is a coverage gap, not an assertion gap.

## Mutation Types

The mutants Stryker injects, and the test that kills each:

| Mutator | Example | Killing test |
|---------|---------|--------------|
| Arithmetic | `a + b` → `a - b` | exact-value assertion |
| Equality | `>` → `>=`, `===` → `!==` | boundary cases (at/above/below) |
| Logical | `&&` → `\|\|`, `??` → `&&` | each operand false independently; nullish vs falsy inputs |
| Conditional | `if (cond)` → `if (true)` / `if (false)` | both branches asserted |
| String literal | `'ok'` → `''` | assert the exact string |
| Array/Object | `[a, b]` → `[]`, method call removed | assert contents, not just length |
| Boolean | `true` → `false` | assert the flag's observable effect |
| Optional chaining | `a?.b` → `a.b` | pass `undefined`/`null` through the path |
| Return value | `return x` → `return undefined` | assert on the returned value |
| Block statement | function body emptied | any observable-effect assertion |

## Reading the Report

```
------------------|---------|----------|-----------|------------|----------|
File              | % score | # killed | # timeout | # survived | # no cov |
------------------|---------|----------|-----------|------------|----------|
pricing.service.ts|   72.00 |       36 |         1 |         10 |        4 |
```

| Status | Meaning | Your action |
|--------|---------|-------------|
| Killed | a test failed under the mutation | none — good |
| Survived | all tests passed with the bug present | add/strengthen an assertion |
| No coverage | no test runs this line | write the missing test first |
| Timeout | mutant caused a hang | counted as killed |
| Runtime/Compile error | mutant broke compilation | ignored by score |

Score = killed / (killed + survived). The HTML report shows each mutant's
exact diff at the line — always read the diff before writing the fix.

## Killing Surviving Mutants

Match the fix to the mutant class:

**Survivor: `price > 0` → `price >= 0`** — missing boundary:

```typescript
it('rejects a zero price (boundary)', () => {
  expect(isValidPrice(1)).toBe(true);
  expect(isValidPrice(0)).toBe(false);  // kills >= mutant
  expect(isValidPrice(-1)).toBe(false);
});
```

**Survivor: `active && verified` → `active || verified`** — operands never
varied independently:

```typescript
it.each([
  [true, true, true],
  [true, false, false],   // kills || mutant
  [false, true, false],   // kills || mutant
  [false, false, false],
])('eligibility(active=%s, verified=%s) → %s', (active, verified, expected) => {
  expect(isEligible({ active, verified })).toBe(expected);
});
```

**Survivor: `return total` → `return undefined`** — truthiness-only assertion:

```typescript
// ❌ was: expect(calculateTotal(items)).toBeDefined();
expect(calculateTotal(items)).toBe(129.9);
```

**Survivor: `label ?? 'default'` → `label || 'default'`** — falsy-but-defined
never tested:

```typescript
expect(formatLabel({ label: '' })).toBe('');        // kills || mutant
expect(formatLabel({ label: undefined })).toBe('default');
```

**Survivor: method call removed (e.g. `.sort()` dropped)** — assert order, not membership:

```typescript
expect(listRecords(input).map((r) => r.id)).toEqual([1, 2, 3]); // not arrayContaining
```

General rules:
1. Assert through public APIs — don't test the implementation line directly
2. Prefer exact values (`toBe`, `toEqual`) over truthiness (`toBeDefined`, `toBeGreaterThan(0)`)
3. Add the inverse assertion (`not.toHaveProperty('oldField')`) for transformations
4. One targeted test per surviving behavior — no mega-tests

## Equivalent Mutants

Some mutants change code but not behavior (e.g. `i++` → `++i` as a statement,
or a performance-only short-circuit). They cannot be killed.

- Confirm equivalence by reading the diff and reasoning about observable behavior
- Suppress with a comment and justification:

```typescript
// Stryker disable next-line EqualityOperator: <= equivalent here — loop bound unreachable
for (let i = 0; i < items.length; i++) {
```

Never suppress to make the score pass — a suppression without a reasoned
comment is a review finding.

## Performance Tuning

- Scope with `--mutate` to changed files during development; full runs are for CI/nightly
- `--incremental` reuses the previous run, re-testing only affected mutants
  (state lives in `reports/stryker-incremental.json` — gitignore `reports/`)
- `coverageAnalysis: "perTest"` is essential for Jest/Vitest projects
- `--concurrency N` defaults to cores-1; lower it on shared CI runners
- Exclude generated code, barrels, DTO-only files, and config from `mutate`

## CI Integration

```yaml
# run on changed modules in PRs; full run nightly
- run: npx stryker run --incremental
```

- Gate PRs with `thresholds.break` (start at 30, raise per critical module)
- Publish `reports/mutation/` as a build artifact
- Track score per module, not just globally — a 90% global score can hide a
  0% pricing module

**Targets:** 30% minimum everywhere; 80%+ on business-critical modules
(auth, billing, validation, data access) after they reach 100% line coverage.
