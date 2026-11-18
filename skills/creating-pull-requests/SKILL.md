---
name: creating-pull-requests
description: >
  Runs the end-to-end workflow for delivering a feature or bug fix as pull
  requests on git/GitHub: branch from the integration branch, slice large work
  into small cohesive stacked PRs (default budget about 600 reviewable lines),
  show the PR title and body for approval before opening a draft, commit in
  logical steps with checks green before each commit, keep the draft updated,
  and ask before marking it ready. Also covers writing the PR description
  (context, summary visual, before/after evidence, merge danger) and answering
  review feedback. Use whenever the user asks to open a PR, implement a feature
  or fix a bug that will span several commits, split work into stacked PRs,
  write or update a PR description, address PR review comments, or says
  "follow the usual flow". Do not use for one-line edits, questions, or work
  that will not produce a commit.
compatibility: >
  Requires git and the GitHub CLI (gh), authenticated. Stacked PRs optionally
  use the gh-stack extension. Other hosts work with the same flow using their
  own CLI.
metadata:
  version: "1.0"
---

# Creating Pull Requests

## Purpose

Take work from "approved plan" to "PR ready for review" without losing
traceability. Each commit proves one finished, checked step. The draft PR is
updated as work advances. No PR is opened with text the user has not read, and
nothing is marked ready without the user's go-ahead.

Why it matters: a small PR with a clear description lets a reviewer understand
*why* each change happened without rebuilding the reasoning from a giant diff.
If work stops midway, an incrementally updated draft is still usable.

Code-level rules (simplicity, duplication, comments, checks) live in
`programming-guidelines`. Commit message format lives in
`generating-commit-messages`. This skill only adds the delivery workflow.

## When To Use

- The user asks to open a PR, or to implement a feature or bug fix that will span several commits.
- Large work must be split into stacked PRs.
- A PR description must be written or updated.
- Review comments on a PR you own must be answered.
- The user says "follow the usual flow".

## When Not To Use

- One-line edits, questions, explanations, or anything that creates no commit.
- Planning from scratch. If there is no plan or acceptance criteria, resolve that
  first (see [Inputs](#inputs)).

## References (open at the moment shown)

| File | Open when |
|------|-----------|
| [stacked-prs.md](references/stacked-prs.md) | Before creating the branch if the plan may not fit one PR, and whenever you touch a layer that already has an open PR |
| [pr-description.md](references/pr-description.md) | Before showing the PR text to the user (step 2) and when rewriting it |
| [addressing-review-feedback.md](references/addressing-review-feedback.md) | When a reviewer left comments on a PR you own |

## Inputs

You need to know what "done" means: an implementation plan, acceptance
criteria, or described use cases. If the request is vague or has several
reasonable readings, stop and settle it first, because coding without a
definition of done loops forever at step 6.

If the work is large and no spec exists, write one from the conversation before
slicing: problem, solution, user stories, implementation decisions, testing
decisions, out of scope ([pr-description.md](references/pr-description.md),
"From a spec to a PR"). From the plan, list what must be true at the end. Step 6
checks that list.

Then read the repo's conventions. Project instructions beat this skill's defaults.

- `CLAUDE.md` / `AGENTS.md` (root and relevant subfolders).
- `git log --oneline -20`: commit language, convention, trailers.
- Manifest and scripts (`package.json`, `Makefile`, `pyproject.toml`): the test, lint and typecheck commands for the area you will touch; in a monorepo, how to scope them.
- `.github/workflows/`: what CI actually enforces. Mirror that strictness locally.
- Recent PRs (`gh pr list --state all -L 5`, `gh pr view <n>`): title and body format, PR template, attribution lines, whether PRs link tickets.

Do not hardcode a language, package manager, branch name or attribution. Use what this repo does.

## PR rules (apply to every PR you open)

If a rule looks unworkable in the situation, talk to the user before creating the PR. Do not grant yourself the exception.

**1. Size.** Budget: about **600 lines of diff** (additions plus deletions) that need line-by-line review, with up to 25% tolerance when cutting exactly there would break cohesion. Past that, reviewers stop finding defects and approve out of fatigue; three PRs of 500 beat one of 1,500. If splitting would truly break cohesion and the PR will exceed the tolerance, **stop and ask**, saying how many lines, what would break, and which cut you rejected. If the repo states its own budget, use that.

The budget measures review attention, not bytes. Classify by the file's **role**, not its extension:

| Counts fully | Does not count |
|--------------|----------------|
| Source code in any language | Prose: `.md`, `.txt`, `docs/`, README, CHANGELOG, ADR |
| Config that changes behavior: CI/CD workflows, IaC, deploy manifests, feature flags | Bulk data read by sampling: i18n translations, test fixtures and seeds, snapshots |
| Schema migrations and scripts that change production data | Lockfiles and generated code |

A 900-line `deploy.yml` counts in full (leaked secrets and destructive changes hide there); a 900-line translation file does not. When unsure, ask whether the reviewer must judge it line by line.

A documentation-only PR has no ceiling, since splitting a rewritten guide only forces the reviewer to reassemble it. One subject per PR still applies. If a PR leans on the exemption, or its total diff is much larger than the counted lines, say so in its `## Size` section, so the reviewer knows where the real weight is.

**2. Stack when it doesn't fit.** Each part targets the branch of the previous part, so each diff shows only its own layer. Decide **before branching**. See [stacked-prs.md](references/stacked-prs.md). Do not open one giant PR "and split later".

**3. Draft first, and approved text before creating.** Every PR is born as a draft, and its title and body go to the user before it exists on the host. Drafts are visible and notify people.

**4. The description explains the PR to someone who followed nothing.** It is read six months later by someone asking why the code is this way. Follow [pr-description.md](references/pr-description.md). Do not list gaps, pending work or "next steps" that belong to other PRs: the reviewer should judge what is in front of them, and such lists age badly. The only exception is a limitation that affects this PR as it runs now, such as a feature shipping behind a disabled flag.

## Workflow

### 1. Sync and branch from the integration branch

```bash
git status                      # working tree must be clean
git fetch origin <integration-branch>
git checkout -b <type>/<descriptive-slug> origin/<integration-branch>
```

Branch from the freshly fetched remote ref, never a possibly stale local branch. The integration branch is where work converges before production (`develop`, `main`, ...): confirm with `git branch -r` and the README/CLAUDE.md. Branch names follow the repo's prefix convention (`feat/`, `fix/`, or a personal prefix if the repo requires it) plus a short slug that says what is being done.

Resuming an existing branch: `git fetch origin && git merge --ff-only origin/<branch>`. If that fails, the branch diverged: find out what changed remotely before choosing rebase or merge. Never force either side blindly. A second or later layer of a stack branches from the layer below, synced the same way.

### 2. Open a draft PR with the minimum

The host rejects a PR with no commits of difference. So:

1. Make the first logically complete change (a type or contract, a failing test, a skeleton). Commit and push.
2. **Show the user the full title and body, in the real formatting, and wait for approval.** Not a summary of what you intend to write. Obvious text still gets shown.
3. After approval, open it as a draft against the integration branch (or the layer below):

```bash
gh pr create --draft --base <base> --head <branch> --title "<title>" --body-file <approved-body.md>
```

Put the ticket or issue key in the title or body before creating when the project links trackers that way. The body carries the planned scope as a checklist.

### 3. Develop in logical commits

One commit = one cohesive, nameable change, usually one line of the scope checklist. If you had to revert only that change, the commit should allow it cleanly. Commit messages explain *why*; the diff already shows *what*.

Before adding anything new, run the decision ladder in `programming-guidelines` (needs it, already in repo, stdlib, platform, installed dependency, one line, minimum).

Do not save everything for one final commit: you lose the real history of the reasoning and a mid-way error becomes hard to isolate.

**Gate before every commit:** lint, formatting and typecheck pass on what you commit, with the repo's own scripts. Order matters: `git add`, run the formatter, review `git diff` of what it changed (auto-fixes can alter behavior), `git add` again, run typecheck, then commit. Never use `--no-verify`, `any`, a looser config, or an unexplained suppression. Red that predates you: your bar is "no worse", and you report it at delivery.

Refactoring goes in its own commit, and for larger volume in its own layer, **before** the feature that depends on it.

### 4. Run the tests for the section you touched

After each commit (or small group of related commits), run the test command for the touched area, not necessarily the whole suite. If an existing test covering your change broke, fix it before the next step. Do not stack new work on a red base. If the change fixes a bug, add a regression test that fails without the fix. If the area has no test and the change warrants one, write it now.

Validation already done on an unchanged candidate is not repeated. If syncing with the base or review changed code, validate the new candidate in order: tests, then lint and typecheck, then formatting once.

If the change alters a user-visible flow or fixes an end-to-end regression, ask the user whether an integration test should be added before opening or updating the PR.

### 5. Update the PR

After each push, tick finished scope items (`gh pr edit <n> --body-file ...`). If the plan changed shape, update the checklist: the PR is the source of truth for what is happening. Ticking approved items needs no new approval; **rewriting** the scope (new item, dropped item, different approach) does: show the new text first. Check the size of what counts toward the budget as you go. If you approach it with scope left, close this layer and open the next. Commands are in [stacked-prs.md](references/stacked-prs.md), "Measuring size".

### 6. Repeat until the whole scope is done and no bug is known

Go back to step 3 until all of this is true:

- [ ] Every scope item and acceptance criterion is implemented and covered by a test where applicable.
- [ ] Lint, formatting and typecheck are clean across the whole branch, with no new suppression you did not agree on.
- [ ] The test suite for the touched area is green.
- [ ] No dead code, forgotten TODO, temporary mock or loose end that you introduced.
- [ ] The code follows the project's architecture, adds no new duplication, and error paths are logged in the project's pattern.
- [ ] You re-read the diff for skipped steps of the decision ladder: single-use abstraction, option nobody asked for, helper that duplicates the stdlib, new package doing what an installed one does.
- [ ] Remaining comments explain a decision; public APIs have structured docs.
- [ ] For UI or end-to-end changes, you actually ran the app and exercised the happy path and the relevant edges. Tests prove code correctness, not behavior as the user perceives it.
- [ ] The description's evidence (before/after) exists and is real, not described.

If you are unsure whether something counts as an acceptance criterion, ask.

### 7. Security review

Invoke the `security-review` skill on the branch's pending changes. Treat each finding as part of the step 6 checklist: fix, retest, then continue. Do not reimplement that check by hand.

### 8. Final run

Run the relevant suite from scratch (not only what changed since the last commit) and the commit gate over the whole branch diff, not just the last commit. A rebase, a merge of the layer below, or a contract change across packages breaks what no single commit tested. If CI runs something stricter (`--error-on-warnings`, a full build), run that.

### 9. Deliver and ask

Do not mark the PR ready on your own.

1. Summarize for the user what changed and why, and that steps 6-8 passed. Also say, explicitly: any lint or type suppression you left (with reason), any failure that already existed on the base, and any pattern you had to invent (logging, for example).
2. Ask: "Are you satisfied with the result? Did you find a bug or anything that should be different?"
3. Only on a positive answer, ask permission to mark it ready (`gh pr ready <n>`). "It looks good" is not that permission.
4. Hand over the PR link so the user can add a reviewer.

If the user finds a bug, return to step 3. In a stack, fix it in the layer where the code lives, then rebase upward.

## After review starts

Review comments are handled in a plan-first loop: [addressing-review-feedback.md](references/addressing-review-feedback.md). The technical judgment of each comment (verify, ask, no blind agreement) is `receiving-code-review`.

## Quality Checklist

- [ ] Branch started from the freshly fetched integration branch.
- [ ] Plan and definition of done existed before coding.
- [ ] Title and body were approved by the user before the PR was created, and the PR is a draft.
- [ ] Counted diff is within budget, or the user approved an overage, or the PR is documentation-only.
- [ ] Each commit is one cohesive step, with the gate green before it.
- [ ] Description covers context, what changes, non-obvious decisions, evidence and merge danger, and mentions no work for other PRs.
- [ ] Step 6 checklist closed; security review done; final run done.
- [ ] User confirmed satisfaction and permitted `ready`.

## Outputs

- A feature branch (or stack of branches) with logical, gate-checked commits.
- One or more draft PRs with user-approved titles and bodies, kept up to date; marked ready only on the user's permission.
- A delivery summary: what changed and why, suppressions left, pre-existing failures, invented patterns.
- The PR link(s) handed to the user.

## What this is not

Not a ceremony for every request. The sign that it applies is "this will produce more than one commit and someone benefits from following the progress", not "this involves code".
