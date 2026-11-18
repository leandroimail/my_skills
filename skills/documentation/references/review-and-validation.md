# Review And Validation Path

Use this path for every documentation task. It is mandatory for review work and
required as the final gate for creation or update work.

## Review Modes

- **Review only**: inspect documentation and return findings.
- **Review plus fix**: inspect first, then correct the issues.
- **Validation only**: confirm a document matches the repository without large rewrites.

## Dual Validation Workflow

### Pass 1: Repository Validation

Before drafting conclusions, verify the source of truth:

- code paths and module names
- commands and CLI flags
- configuration keys and defaults
- schemas, request and response fields
- behavior proven by tests or examples
- existing docs that must stay consistent

Reject or flag any claim that cannot be tied to a real repository artifact.

### Pass 2: Request Validation

Before approving the result, confirm it matches what the user actually asked
for:

- requested document type
- requested scope and exclusions
- target audience
- requested language and tone
- requested files, sections, or deliverable shape

Flag any technically correct content that still misses the user's ask.

### Pass 3: Output Validation

After writing or editing, verify the document itself:

- commands still match the implementation
- paths and filenames exist
- defaults and examples stayed correct after rewriting
- links point to real files or sections
- diagrams still reflect verified relationships
- no contradictions were introduced across documents

## Independent Subagent Validation

Use an independent subagent for the final validation whenever delegated agents
are available. The subagent must not be the author of the documentation or the
primary reviewer.

That subagent must verify both:

- the produced or revised documentation against repository evidence
- the result against the user's requested scope, audience, constraints, and
  deliverable shape

Ask the subagent to report:

- unsupported or invented claims
- missed requested scope
- technically correct but user-misaligned content
- contradictions, stale guidance, or broken examples
- residual risks that remain after edits

If delegated agents are unavailable, run the same checklist as a fresh final
pass while treating the document as if it were written by someone else.

## Review Checklist

- stale claims or outdated setup steps
- commands that no longer work
- wrong defaults, flags, or config keys
- examples that do not match the code or schema
- broken links or missing target files
- duplicated content that diverges across files
- missing prerequisites, rollback steps, or verification steps
- audience mismatch or scope drift
- diagrams with invented or unverified relationships

## Output Format For Review Work

Present findings first. For each finding, state:

- what is wrong
- where it appears
- what repository artifact contradicts or supports it
- how to correct it

If no findings remain, say so explicitly and note any residual validation gaps.
