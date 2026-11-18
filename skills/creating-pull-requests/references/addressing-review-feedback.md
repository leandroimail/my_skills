# Addressing Review Feedback on a PR

Open this when reviewers left comments on a PR you own. The loop is plan first:
decide every item with the user, then act. The technical judgment of each
comment (verify before implementing, ask before assuming, no blind agreement)
is the `receiving-code-review` skill; this file is the PR mechanics around it.

## Table of Contents

- [Rules while planning](#rules-while-planning)
- [1. Gather the feedback](#1-gather-the-feedback)
- [2. Present each item](#2-present-each-item)
- [3. Build the resolution plan](#3-build-the-resolution-plan)
- [4. Carry out the approved plan](#4-carry-out-the-approved-plan)

---

## Rules while planning

Until the user approves the plan, do **not** edit files, commit, push, resolve
threads, or post anything to the host. Read-only commands (`gh`, `git log`,
`git diff`, viewing files) are fine.

The PR may live on github.com or another host (for example GitHub Enterprise
Server). Take the host from the PR's `url` and pass `--hostname <host>` to every
`gh api` call, because `gh api` defaults to github.com.

## 1. Gather the feedback

- Resolve the PR: the number or URL the user gave, otherwise the PR for the current branch (`gh pr view --json number,url,headRefName,headRefOid,baseRefName`). If none, ask.
- Fetch **all** review threads (paginate) with, per thread: resolved and outdated flags, path, line, and every comment's id, url, author, body and diff hunk. Also fetch top-level review bodies and general conversation comments, since feedback hides there too.
- Skip resolved threads and threads where you (the author) had the last word, unless they still look unaddressed. Mention outdated threads, and check whether the feedback still applies to current code.
- Fetch the PR head (`git fetch origin refs/pull/<n>/head`) and check the SHA against `headRefOid`. Read code from that SHA, not from a local branch that may be behind. Say so if the local branch is behind.
- **Order the items so the review reads coherently**, not just by position in the diff. First read everything and spot patterns ("same as above", the same nit in several places). Put the comment that explains a pattern first, then every comment that refers back to it right after. Order the rest by file and line, ties by creation time.
- Tell the user up front how many items there are, with a one-line index in presentation order (`N. @reviewer path:line, gist`), marking follow-ons ("same pattern as #2") and noting skipped threads.

## 2. Present each item

One item per turn. The user cannot see your tool output or reasoning, only your
message text, so write the full item **before** asking for a decision. Do not
paraphrase the comment or skip the diff to save space.

````markdown
### Item N of M: @reviewer, `path:line` (comment link)
Thread: link, status: open | outdated

**Feedback**
> full text of the first comment, verbatim (keep code blocks and suggestions)
> **@replier:** each reply, in order

**Diff context** (the review's hunk, about 10 lines around the commented line)

**Current code**: path, lines A-B, with line numbers, read from the PR head

**Evidence / related context**
- `other/file:123`: why it matters
- Related comment: who, where, how it interacts with this one

**Assessment**: is the reviewer right? What is the trade-off?

**Recommendation**: **Act** (exact files and a short sketch) or **Reply** (draft reply, short and friendly)
````

Rules for the block:

- Always include the comment's URL. Quote the feedback verbatim from the fetched body, not from memory.
- Every claim in Assessment is backed by something in Evidence (a `path:line` and snippet, a commit, a doc link, a related comment).
- Then ask for the decision, with the question self-contained enough to identify the comment. Offer: act as proposed (recommended), reply with reasoning, act differently, skip or defer. For a follow-on item, say which earlier item it follows and what was decided, and offer "same as item K" first.
- If the user picks a free-form option, work it through before moving on. If they ask to see an item again, reprint the full block rather than summarizing.
- Keep a running record of each item and decision (comment id, url, path, line, decision, planned change, reply text) so nothing is lost.

## 3. Build the resolution plan

When every item is decided, write one plan listing, per item: the comment link,
the decision, the code change (if acting), the **exact reply text** to post, and
whether the thread will be **resolved**. Show it and wait for approval.

Default resolution:

| Decision | Reply | Resolve the thread |
|----------|-------|--------------------|
| Act | Yes, pointing at the commit | Yes |
| Reply with reasoning | Yes | No, leave it open for the reviewer |
| Skip / defer | No | No |

Top-level review or conversation feedback has no thread to resolve.

## 4. Carry out the approved plan

- **Before any edit**, check out the PR head cleanly (`gh pr checkout <n>`, which also sets the push destination for fork PRs), and confirm `HEAD` matches the verified head SHA and the tree is clean. If not, stop and tell the user.
- Make small, focused commits. Where sensible, one commit per feedback item, so a reply can point at a specific commit. Each commit passes the commit gate from `SKILL.md`, step 3.
- **Push before you reply.** A reply that mentions a commit SHA must be posted only after that commit is on the host, or the SHA will not render as a link. In order:
  1. Commit, then push.
  2. Re-read the PR's `headRefOid` and confirm each referenced commit is reachable from it (`git fetch origin refs/pull/<n>/head`, then `git merge-base --is-ancestor <sha> FETCH_HEAD`). If not, stop and fix that first.
  3. Only then post replies, using the full 40-character SHA or a commit URL.
- Reply **inside the existing thread** (`gh api repos/{owner}/{repo}/pulls/{n}/comments/{comment_id}/replies -f body=...`), not as a new top-level comment. For top-level feedback, post one PR comment that quotes what it answers.
- Post the reply text the user approved. Changing only the SHAs is fine.
- Resolve only threads the plan marks for resolution, and only after their reply is posted. Never resolve a thread you left open on purpose.
- **Re-request review last.** After commits are pushed, replies posted and threads resolved, re-request review from every human reviewer whose feedback was addressed in this pass (not yourself, not bots).
- If the pass changed code, validate the new candidate in order: tests, then lint and typecheck, then formatting once. Do not repeat validation for metadata-only changes.
- Finish with a short summary: links to each reply posted, each commit pushed, which threads were resolved, and who was re-requested.

In a stack, a fix goes in the layer where the code lives, followed by a cascade
rebase upward (the "Changing a lower layer" procedure for stacks is
covered in the stacked PRs reference listed in SKILL.md).
