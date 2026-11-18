---
name: programming-guidelines
description: >
  Applies behavioral guidelines that reduce common LLM coding mistakes:
  overcomplication, unrequested changes, silent assumptions, and unverified
  work. Use whenever planning, writing, reviewing, debugging, or refactoring
  code, adding a dependency or abstraction, fixing a bug, or preparing a commit,
  to keep changes minimal and surgical, surface assumptions, and define
  verifiable success criteria, even if the user does not name this skill.
license: MIT
---

# Programming Guidelines

## Purpose

Reduce common LLM coding mistakes: guessing instead of asking, writing more than was requested, editing code that was not part of the task, and declaring success without evidence.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## When To Use

- Planning, writing, reviewing, debugging, or refactoring code.
- Before adding a file, abstraction, option, or dependency.
- Before committing or handing work off.

## When Not To Use

- Non-code work (prose, data analysis with no code changes).
- Trivial one-line edits where the full ladder below would cost more than the change.

## Inputs

- The user's request and any stated constraints.
- The repo's conventions: the project's agent instruction files, recent history, manifest scripts, CI config.

## Method

Work through the five guideline sections below in order.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- Read the repo's conventions before assuming yours: the project's agent instruction files (e.g. `AGENTS.md`, `CLAUDE.md`), recent `git log`, the manifest and its scripts, and the CI config. Project instructions override these defaults.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

Before adding a file, function, abstraction, option or dependency, go down this ladder and stop at the first step that answers:
1. Does it need to exist? Name the requirement it serves. If you can't, don't write it.
2. Does the repo already have it? Search by domain noun and verb, and read the closest sibling module.
3. Does the standard library do it?
4. Does the platform already provide it (framework, database constraint, browser feature, runtime)?
5. Does an already-declared direct dependency do it? Never rely on a transitive package.
6. Does it fit in one clear line? Then write one line, not a class and a factory. Clear, not clever.
7. Only then write the minimum that meets the requirement. Minimum in scope, not in quality: real error paths, tests and project conventions stay.

Keep the search to seconds and to the code you are writing. A new dependency is the owner's decision: stop and propose it, with what it solves and why steps 1-5 did not. If you skip a step on purpose, say why in a comment or in the PR.

Simple means fitting the project's architecture. Bypassing an existing layer (repository, injection, service) because it is shorter is not simplicity. If the design looks wrong, raise it; don't redesign inside a feature.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

Duplication:
- DRY is about duplicated knowledge, not similar-looking lines. Merging two rules that only look alike couples things that will diverge.
- Duplication you are about to create: don't. Reuse or extract now, while the code is yours.
- Existing duplication: touch it only if it sits in code your task must change. Otherwise mention it and leave it.
- Before unifying existing copies, map their callers, their tests and where they differ. If regression risk is above low (many callers, thin tests, subtle divergence, critical domain), ask first. Add characterization tests before, prefer extending (an optional parameter) over rewriting, and keep refactors and behavior changes in separate commits.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Tests and root causes:
- Watch a new test fail for the expected reason before you fix anything. A test that fails for another reason proves nothing.
- Fix the cause, not the symptom. A guard that only hides the crash is not a fix.
- If two fixes that share one premise fail the same check, stop. Write that premise in one sentence, look for new evidence, and revise it before a third attempt.
- A test you wrote or are touching whose assertions could not fail for the behavior it names (no assertion on the result or effect it exists to protect) cannot detect a broken contract. A test whose contract is "accepts valid input without raising" is legitimate. Strengthen it with a case that does fail. Tests of "does nothing" behavior (idempotency, no notification when disabled) are legitimate; pair them with a positive case. Remove a test only when it is redundant, and leave unrelated old tests alone and mention them.
- If an honest test is impractical, say so and name the alternative check (manual repro, type check, contract). Do not write a weak test.

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

### 5. Comments, Checks and Handoff

**Comments explain why, not what.** If deleting the comment loses nothing the code doesn't already carry, don't write it. Worth a comment: a non-obvious design decision (and the alternative you rejected), a business or regulatory limit, the root cause behind a bug fix, a counter-intuitive workaround. A long comment usually means extracting a well-named function. Fix or delete a comment your change made false. Public APIs get the structured doc the language and repo use (docstring, JSDoc, Javadoc); private helpers don't. `TODO`/`FIXME`/`NOTE` carry context ("TODO: move to X once Y exists"); a TODO you could finish inside the task is unfinished work.

**Checks before each commit.** Lint, formatting and type checks pass on what you commit, using the repo's own scripts; the CI is the reference for strictness. A type error usually means the change is incomplete, so fix the cause. Never bypass with `--no-verify`, `any`, a looser config or an unexplained suppression. If a rule seems wrong for the case, ask. If the base was already red, the bar is "no worse"; don't clean unrelated debt.

**Handoff.** Tell the reader what the diff can't show: suppressions you left (with reasons), failures that predate your change, patterns you had to invent (logging, for example), and observations about out-of-scope code.

## Quality Checklist

- [ ] Assumptions were stated; ambiguity was asked about, not guessed.
- [ ] No feature, abstraction, option, or dependency beyond the request.
- [ ] Every changed line traces to the request; only your own orphans were removed.
- [ ] Success criteria were defined and verified (a new test failed first, then passed).
- [ ] Lint, formatting, and type checks pass without bypasses.
- [ ] The handoff lists suppressions, pre-existing failures, invented patterns, and out-of-scope observations.

## Outputs

- A minimal, verified change that follows the project's conventions.
- A brief plan with verification steps for multi-step tasks.
- A handoff note covering what the diff cannot show.
