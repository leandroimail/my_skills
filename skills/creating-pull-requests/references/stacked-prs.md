# Slicing Work into Stacked PRs

Open this before creating the branch when the plan may not fit one PR, and
whenever you must change a layer that already has an open PR below or above it.

## Table of Contents

- [Size budget](#size-budget)
- [Slicing in canonical order](#slicing-in-canonical-order)
- [What a stack is](#what-a-stack-is)
- [Native path: gh stack](#native-path-gh-stack)
- [Manual path](#manual-path)
- [Numbers and cross references](#numbers-and-cross-references)
- [Changing a lower layer](#changing-a-lower-layer)
- [Merge order](#merge-order)
- [Other platforms](#other-platforms)
- [Measuring size](#measuring-size)

---

## Size budget

About **600 lines of diff** (additions plus deletions) that need line-by-line
review, with up to 25% tolerance (about 750) when cutting exactly there would
break cohesion. What counts and what does not is the table in `SKILL.md`, PR
rule 1. If the repo states its own budget, use that.

Review capacity drops sharply with diff size: past a few hundred lines the
reviewer stops finding defects and approves out of fatigue. That is why slicing
comes before branching; discovering it later means redoing the whole queue.

**Documentation is the exception.** Do not slice prose: a text cut into four
dependent layers costs the reviewer more attention, not less. Different
subjects become independent PRs against the trunk, not a stack. The doc part of
a mixed PR rides with the code it documents, in that layer.

## Slicing in canonical order

Each layer needs three things:

1. **It makes sense read alone**: a title and summary describing one whole change, not "part 2 of the thing". The reviewer can approve it without reading the others.
2. **It leaves the trunk consistent if merged alone**: build green, tests passing, no "breaks here, fixed in the next layer". If the upper layers are abandoned, the lower one must not have made things worse.
3. **It prepares the ground for the next layer.**

The order that usually emerges:

```
contract / types / migration -> domain implementation -> exposure (endpoint, UI) -> cleanup of old callers
```

A refactor comes **before** the feature that relies on it, in its own layer,
never in the same PR.

A slicing test: write each layer's title before writing code. If one only makes
sense as "the rest of the previous one", the cut is in the wrong place.

## What a stack is

The first PR targets the trunk (`develop`/`main`). Each next PR targets the
**branch of the PR below it**, not the trunk. Effects:

- Each PR's diff shows only its own layer. If layer 2 targeted the trunk, its diff would repeat layer 1 and the reviewer would pay twice.
- You are not blocked waiting for review: open layer 2 on top of unmerged layer 1 and keep working.
- Layers can be reviewed in parallel by different people.
- The dependency is recorded in the system, not only in body text.

## Native path: gh stack

GitHub has native support for stacked PRs through the `gh stack` extension. The
source workflow reports it as a public preview (July 2026) and subject to
change, so verify what the installed version supports before promising a
structure to the user:

```bash
gh extension list | grep -i stack   # installed?
gh stack --help                     # does it exist and answer?
gh extension install github/gh-stack
```

Prefer it when available: it produces the "stack map" in the UI. If you resume a
stack from another session, run `gh stack sync --prune` first (updates the
trunk, rebases the stack, reports diverged layers).

```bash
gh stack init                 # create the stack (use --base <branch> if the trunk is not the repo default)
git add -A && git commit -m "feat(x): ..."
gh stack add <branch-layer-2>
git add -A && git commit -m "feat(x): ..."
gh stack push
gh stack submit               # creates/updates the PRs with the right bases
gh stack view
```

| Command | Purpose |
|---------|---------|
| `gh stack up` / `down` / `top` / `bottom` / `trunk` | move between layers |
| `gh stack checkout <PR \| branch \| URL>` | jump to a layer |
| `gh stack rebase --upstack` | re-cascade from the current layer upward after editing below |
| `gh stack rebase --downstack` | rebase from the stack base to the current layer |
| `gh stack rebase --continue` / `--abort` | resume or cancel after a conflict |
| `gh stack sync --prune` | pull the trunk, rebase, push, clean merged branches |
| `gh stack modify` | reorder, split, merge or remove layers (interactive) |
| `gh stack merge --squash` | merge one or more layers |

Constraints worth knowing: all branches must be in the same repository (no stacks
across forks); merging is bottom to top; the UI's "Rebase stack" runs server-side
and does not sign commits, so rebase from the CLI where signing is required;
`gh stack modify` needs a clean tree and linear history. If a command is missing
in the installed version, confirm with `--help` and fall back to the manual path.

**Draft plus approved text.** If `gh stack submit` does not expose draft or body
control, create each PR with `gh pr create --draft --base <lower-layer-branch>`
and link them afterwards with `gh stack link`.

## Manual path

Works on any version of the host and is the fallback.

```bash
# layer 1
git fetch origin <trunk>
git checkout -b feat/part-1 origin/<trunk>
# ... commits ...
git push -u origin feat/part-1
gh pr create --draft --base <trunk> --head feat/part-1 ...

# layer 2: branch from layer 1 and target layer 1
git fetch origin feat/part-1:feat/part-1   # sync layer 1 first; it may have received pushes
git checkout -b feat/part-2 feat/part-1
# ... commits ...
git push -u origin feat/part-2
gh pr create --draft --base feat/part-1 --head feat/part-2 ...
```

For any layer N, sync layer N-1 with the remote before branching the next.

Maintenance, where the pain lives:

- **Changed layer 1?** Rebase the upper layers with `git rebase --update-refs` (Git 2.38+), which repositions every branch pointing into the rebased range at once. To make it the default: `git config --global rebase.updateRefs true`.
- **After a rebase, run the commit gate on each affected layer** (lint, formatting, typecheck). A rebase resolves text conflicts, not type conflicts: if the lower layer changed a contract, the upper one can have clean history and code that does not compile.
- Push with `git push --force-with-lease`, never bare `--force`, so you cannot erase someone else's commits.
- **When layer 1 merges**, the host usually retargets open PRs that had it as base. Confirm that happened and rebase layer 2 onto the updated trunk before asking for review.

## Numbers and cross references

**Never write the number of a PR that does not exist yet.** Others open PRs in
the meantime; "followed by #446" becomes a broken link or someone else's PR.

- At creation, only backward references: `Layer 2 of 4, depends on #445.`
- The position (`2 of 4`) is safe while the plan has 4 layers; update the bodies if slicing changes.
- A forward link only after the next PR exists, by editing the earlier body. Optional.

With the native stack the UI already shows the whole stack, so the one human
line is enough. That line is the **only** mention of other layers in a body.

## Changing a lower layer

It will happen: review on layer 1 asks for a change while layer 2 is open. The
fix goes **in the layer where the code lives**, never "I'll fix it up here
because I'm here":

```bash
gh stack down                 # or: git checkout feat/part-1
# ... fix, commit ...
gh stack rebase --upstack
gh stack push
```

Manually: rebase the upper branches with `git rebase --update-refs` and push
with `--force-with-lease`. Fixing in the wrong layer breaks the premise of the
stack: the layer 1 reviewer approves code that is not what reaches the trunk.

## Merge order

Bottom to top, always. Merging from the middle orphans the layers below. After
each merge, `gh stack sync --prune` (or a manual rebase) brings the remaining
stack onto the updated trunk. If a middle layer is rejected, remove it with
`gh stack modify` or a manual rebase instead of leaving the queue blocked.

## Other platforms

The principle "each part targets the previous one" is the same everywhere; what
changes is what the platform records. Confirm what exists in the repo:

- **GitLab**: merge request dependencies are native, in addition to base-branch chaining.
- **Gerrit**: relation chains are the native model.
- **Bitbucket, Azure DevOps**: no dependency field; base-branch chaining plus a reference in the body.

## Measuring size

Measure while working, not at the end. Two numbers: the total diff (what the
host lists) and what counts toward the budget.

```bash
# total
git diff --shortstat <base-branch-of-this-PR>...HEAD

# what counts: without prose, bulk data, snapshots and lockfiles
git diff --shortstat <base-branch-of-this-PR>...HEAD -- . \
  ':(exclude)*.md' ':(exclude)*.txt' ':(exclude)*.adoc' \
  ':(exclude)docs/*' ':(exclude)*i18n/*' ':(exclude)*locales/*' \
  ':(exclude)*__snapshots__/*' ':(exclude)*.snap' \
  ':(exclude)*.lock' ':(exclude)*-lock.json' ':(exclude)*-lock.yaml'
```

The exclusion list is a starting point: adjust it to the repo (the docs folder
may be `documentacao/`, fixtures may live in `test/data/`). It deliberately does
**not** exclude `.yml` or `.json` in general: CI workflows and deploy manifests
are code in another syntax.

When the two numbers diverge a lot, find where the weight is, and confirm the
exclusion did not eat something that should count:

```bash
git diff --numstat <base-branch-of-this-PR>...HEAD | sort -rn | head -20
```

Near 500 **counted** lines with scope left, close this layer and open the next.
When the numbers differ a lot, the body says so (`## Size`), because the
reviewer decides whether to open the PR by looking at the total.

If you conclude that splitting would truly break cohesion (a signature change
that compiles only with 40 callers updated together), **stop and ask** before
continuing. Present: counted lines and total; why it cannot be split; the split
you considered and rejected. Before asking, recompute: if the volume came from
docs, translations, snapshots or generated code, the PR may already fit.
