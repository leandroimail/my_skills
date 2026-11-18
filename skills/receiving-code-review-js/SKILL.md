---
name: receiving-code-review-js
description: >
  Runs a lightweight inline code review automatically after every code
  creation or modification task, acting as a self-review subagent before
  delivering any implementation. Checks correctness, security basics, type
  safety, test coverage, and mutation-testing feedback on the immediate change
  only. Use this on every coding task, especially when review comments mention
  Jest coverage, StrykerJS, mutation testing, or surviving mutants. Also handles
  receiving and evaluating external review feedback with technical rigor —
  verify before implementing, ask before assuming, never blind agreement. Do NOT
  use as a substitute for the `code-review-js` skill, which performs full PR-level
  review covering TypeScript, React, NestJS, and SQL with the complete static
  analysis toolchain (eslint, prettier, tsc, npm audit, knip, jest, StrykerJS).
---

# Code Review Reception

## Purpose

Code review requires technical evaluation, not emotional performance.

**Core principle:** Verify before implementing. Ask before assuming. Technical correctness over social comfort.

## When To Use

- After every code creation or modification task, as a self-review before delivering.
- When review feedback arrives (from a team lead, external reviewer, or CI) and must be evaluated before acting.
- When a comment mentions CRAP or duplication scores, weak tests, mutation testing, or surviving mutants.

## When Not To Use

- For full PR-level review with the complete static analysis toolchain: use the `code-review-js` skill.
- For greenfield design questions with no feedback or change to evaluate.

## Inputs

- The change just made, or the review feedback text (inline comments, PR threads, reviewer messages).
- Access to the codebase, so each claim can be verified against it.
- The source of the feedback (team lead, external reviewer), because it sets how much to trust it.

## Method

### The Response Pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## Forbidden Responses

**NEVER:**
- "You're absolutely right!" (violates the project's agent instruction files, e.g. AGENTS.md, CLAUDE.md)
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)

**INSTEAD:**
- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if wrong
- Just start working (actions > words)

## Handling Unclear Feedback

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**Example:**
```
team lead: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

❌ WRONG: Implement 1,2,3,6 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## Source-Specific Handling

### From your team lead / project owner
- **Trusted** - implement after understanding
- **Still ask** if scope unclear
- **No performative agreement**
- **Skip to action** or technical acknowledgment

### From External Reviewers
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with prior architectural decisions:
  Stop and discuss with the team lead first
```

**Rule:** External feedback should be evaluated skeptically but checked carefully.

## YAGNI Check for "Professional" Features

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**Rule:** Do not add unused features. If code is not called, propose removal (YAGNI).
`knip` can confirm unused exports and dependencies mechanically: `npx knip`.

## Implementation Order

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Order the items:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. For each item, in that order:
     - Bug report: reproduce it, see the relevant failure, then fix the cause
     - Test the fix individually
  4. Verify no regressions
```

## Metric Feedback (CRAP, Duplication)

When a reviewer cites a CRAP score or a duplication score (the `code-review-js` skill documents how to install the tools, under "Installing the tools"):

1. Reproduce it. Run the tool, or estimate it and label the result "estimate".
2. Check that the metric is valid. CRAP needs coverage that ran, is current, and matches the paths; if not, it is unavailable. Duplication needs the right set of files and a parsed language; a coverage failure does not affect it.
3. A score is a candidate. Open the code and confirm a real problem.
4. A high score in code unrelated to this change is an observation, not a fix to add here. If you can show that code causes the issue under review, it is in scope.

## Mutation Testing Feedback

Use this section when a review comment mentions weak tests, mutation testing,
StrykerJS, surviving mutants, or asks whether mutation tests were executed.

### Verify Configuration First

Before running mutation tests:

1. Check whether `@stryker-mutator/core` (and the runner plugin, e.g.
   `@stryker-mutator/jest-runner`) is installed in the project dev dependencies.
2. Check whether the project has a `stryker.config.json` / `stryker.config.mjs`.
3. Verify `mutate` targets production files, not test files, specs, or configs.
4. Verify the scope is narrow enough to finish in a review loop (use
   `--mutate` overrides for changed files only).

Recommended project commands:

```bash
npx stryker run
npx stryker run --mutate "src/services/pricing.ts"
```

If StrykerJS is not installed and the task requires mutation testing, add it to
`devDependencies` and update the lockfile through the project package manager
(`npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner`).
Do not vendor generated `reports/mutation/` output.

### Interpret Results Correctly

Mutation testing passing does not mean there are no surviving mutants. Report:

- killed mutants
- survived mutants
- no-coverage mutants when shown by the tool
- whether the configured `thresholds.break` gate passed
- the highest-risk surviving mutants that still need stronger tests

Treat surviving mutants in files changed by the current task as actionable test
gaps unless they are equivalent mutants or outside the requested scope. If a
survivor is likely equivalent, explain why with the exact mutant behavior.

### Improve Tests

When strengthening tests for mutation coverage:

1. Add assertions that observe behavior through public APIs.
2. Avoid tests that duplicate implementation logic.
3. Prefer small targeted Jest cases for each surviving behavior.
4. Re-run the focused test file (`npx jest path/to/file.spec.ts`) before
   re-running Stryker.
5. Re-run `npx stryker run` and inspect the HTML report at
   `reports/mutation/mutation.html`.

A surviving mutant can point to dead code. Report it with the evidence that it
is dead (no callers, not exported); a survivor alone does not prove it. Remove it
only when the removal is in scope; do not delete pre-existing dead code unasked.

Only claim "mutation clean" when there are no relevant surviving mutants for
the configured mutation scope.

## When To Push Back

Push back when:
- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Legacy/compatibility reasons exist
- Conflicts with prior architectural decisions

**How to push back:**
- Use technical reasoning, not defensiveness
- Ask specific questions
- Reference working tests/code
- Involve the team lead if architectural

**If uncomfortable pushing back:** State clearly that you need a second opinion or more time to verify.

## Acknowledging Correct Feedback

When feedback IS correct:
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ "Thanks for [anything]"
❌ ANY gratitude expression
```

**Why no thanks:** Actions speak. Just fix it. The code itself shows you heard the feedback.

**If you catch yourself about to write "Thanks":** DELETE IT. State the fix instead.

## Gracefully Correcting Your Pushback

If you pushed back and were wrong:
```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

State the correction factually and move on.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Assuming reviewer is right | Check if breaks things |
| Avoiding pushback | Technical correctness > comfort |
| Partial implementation | Clarify all items first |
| Can't verify, proceed anyway | State limitation, ask for direction |

## Real Examples

**Performative Agreement (Bad):**
```
Reviewer: "Remove legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**Technical Verification (Good):**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is Node 18+, this polyfill targets Node 14. Need it only if the CLI still supports 14. package.json engines says >=18 — removing."
```

**YAGNI (Good):**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

**Unclear Item (Good):**
```
team lead: "Fix items 1-6"
You understand 1,2,3,6. Unclear on 4,5.
✅ "Understand 1,2,3,6. Need clarification on 4 and 5 before implementing."
```

## GitHub Thread Replies

When using GitHub, reply to inline review comments in the comment thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level PR comment. Adapt accordingly for other VCS platforms (Azure DevOps, GitLab, Bitbucket, etc.).

## Quality Checklist

- [ ] Every feedback item was verified against the codebase before implementing.
- [ ] Unclear items were clarified before any implementation started.
- [ ] No performative agreement or gratitude in responses.
- [ ] Items were fixed one at a time, each tested, with no regressions.
- [ ] Pushback (if any) cites technical reasoning, tests, or code.
- [ ] Mutation or metric claims state what was actually run.

## Outputs

- A technical acknowledgment, a clarifying question, or reasoned pushback for each feedback item.
- The implemented fixes, verified one at a time.
- For mutation or metric feedback: the killed/survived counts, gate result, and the highest-risk survivors (or "metric unavailable").

## The Bottom Line

**External feedback = suggestions to evaluate, not orders to follow.**

Verify. Question. Then implement.

No performative agreement. Technical rigor always.
