# Writing the PR Description

Open this before showing the PR text to the user (step 2) and whenever you
rewrite it. The body is the document someone reads six months later asking why
the code is this way.

## Table of Contents

- [Template](#template)
- [Section rules](#section-rules)
- [Summary: pick the smallest visual](#summary-pick-the-smallest-visual)
- [Evidence](#evidence)
- [Merge danger](#merge-danger)
- [What never goes in the body](#what-never-goes-in-the-body)
- [From a spec to a PR](#from-a-spec-to-a-pr)
- [Titles, trackers and attribution](#titles-trackers-and-attribution)

---

## Template

If the repo has a PR template (`.github/pull_request_template.md`), use it and
fold the sections below into it. Otherwise use this skeleton. It is a skeleton,
not a form to fill with the minimum: the test is that someone who followed
nothing can tell what changed, why, and why this way.

```markdown
## Context
<why this PR exists: the need, the request, the decision behind it.
 For a bug fix: the wrong behavior, how it shows up for users, the root cause.>

## What changes
<what was done, for real: flows and files affected, and the practical effect.
 For a bug fix: how the change attacks the root cause, not the symptom.>

<optional Summary visual here (see below)>

## Decisions
<only when a non-obvious choice was made: chosen, rejected, and why.
 No relevant choice: delete this section.>

## Evidence
- **Before:** <screenshot / output / failing test run>
  **After:** <screenshot / output / passing test run>

## Merge danger
**Door:** <one-way or two-way>
**Blast radius:** <one word or short phrase>
<optional: ramifications of merging>

## Size
<when the total diff is clearly larger than the lines that count (prose, i18n,
 lockfiles, snapshots), or the PR leans on the exemption: total vs counted, and
 where the rest is. If the total already fits the budget, delete.>

## Scope
- [ ] <part 1 of the plan>
- [ ] <part 2 of the plan>

## Test plan
- [ ] <test command for the touched area>
- [ ] <lint + formatting command>
- [ ] <typecheck command for the touched packages>
- [ ] <manual check, if there is UI or an end-to-end flow>

## References
<ticket/issue: "Closes #123", tracker key, board link.>

## Stack
<only when the work is split: "Layer 2 of 4, depends on #445".
 Reference only PRs that already exist.>
```

## Section rules

- **Context**: why, not what. The need, the request, the decision.
- **What changes**: concrete ("rejects negative quantities in `OrderService.add`"), never "adjustments to the service". Bug fixes state symptom, cause, and why the change hits the cause.
- **Decisions**: only non-obvious ones, with the rejected alternative. If nothing relevant was chosen, omit the section rather than pad it.
- **Evidence**: concrete proof the change works, as before and after. Best: screenshots for visual changes. Next: execution evidence, meaning the exact test that now fails then passes, or console output. "Tests pass" with no detail is weak.
- **Scope**: the checklist you tick as work advances. Ticking is free; rewriting needs the user's approval.
- **Test plan**: commands the reviewer can run, not intentions.
- **References**: link the ticket so traceability survives the person who knew the context leaving.
- **Stack**: one line, backward references only. Never write the number of a PR that does not exist yet.

## Summary: pick the smallest visual

Use a visual only when it makes the key point faster than prose. Place it next
to the text it supports, keep only the calls, files, states or boundaries that
matter, and use one or two, not all. Use the project's domain vocabulary.

| Show | Use |
|------|-----|
| Logic or an algorithm | Pseudocode |
| Runtime control flow | Call tree |
| UI structure | Component tree with the state and module boundaries that matter |
| A broad refactor or file responsibility | Shallow file tree |
| Interaction or data flow between parts | Mermaid `sequenceDiagram` or `flowchart` |
| What changes inside a shape that already exists | A `diff` block of the tree or flow, not of raw code |
| A new function the reader may copy | The whole block |

Example, a flow change as a diff:

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

## Evidence

Before and after, in the strongest form available:

1. A screenshot, when the change is visual and the environment allows it.
2. Execution output: the test that failed before the fix and passes after, shown as the test name and result, or the relevant console output.
3. A reproduction command and its output.

Do not claim evidence you did not produce. If none can be produced, say why and
name the alternative check.

## Merge danger

State whether merging is a **two-way door** (cheap to roll back) or a **one-way
door** (destructive or hard to reverse: data migrations, deleted data, public
API changes, sent notifications). Then state the **blast radius**: who or what is
affected if it is wrong (consumers, layout, mobile, a batch job, billing).
Always fill this for migrations, deploy or CI changes, and shared contracts. For
a small, isolated, reversible change, one line is enough.

For a one-way door, also write what you could **not** verify (for example: no
rehearsal on a copy of production data, nothing checked outside this repo that
reads the dropped columns) and check ordering: the new code must be live before
a migration removes what the old code reads, and a deploy step that migrates must
not run ahead of the code that needs it. Do not claim a check you did not run.

## What never goes in the body

- Gaps, pending work and "next steps" that belong to other PRs. The reviewer judges what is in front of them, and such lists age badly.
- The number of a future PR.
- Pasted AI attribution in the description unless the project's convention puts it there; check recent PRs and the session's own rules. Commit trailers stay in commits.
- A limitation that does not affect this PR as it runs now. A limitation that does (for example, "ships behind a flag that stays off") does belong.

## From a spec to a PR

For large work with no written plan, synthesize one from the conversation first,
without interviewing the user again. Use this shape and publish it where the
project keeps specs or tickets:

1. **Problem statement**, from the user's perspective.
2. **Solution**, from the user's perspective.
3. **User stories**: "As an actor, I want a feature, so that benefit". Be extensive.
4. **Implementation decisions**: modules built or changed, their interfaces, schema and API contracts, architecture choices. No file paths or code snippets that will age quickly.
5. **Testing decisions**: what a good test is (external behavior only), which modules get tested, prior art in the repo. Prefer existing test seams, and the highest seam possible; the ideal is one.
6. **Out of scope.**
7. **Further notes.**

Check with the user that the test seams match their expectations. Then map the
spec onto PRs: user stories and implementation decisions become the **Scope**
checklist and the slicing of the stack, and testing decisions become the **Test
plan**. "Out of scope" stays in the spec or ticket. It does not go into a PR body.

## Titles, trackers and attribution

- Title: the repo's convention (for example `type(scope): short summary`), what the change does, not the ticket number alone.
- Put the tracker key in the title or body before creating, when the project links that way, so linking is automatic.
- Follow the repo's attribution convention for commits and PR bodies, as seen in recent history. Do not invent one, and do not duplicate a trailer a commit already has.
- A changelog entry only if the repo's template asks for one.
