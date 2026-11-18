---
name: documentation
description: >
  Plans, writes, reviews, and validates technical documentation for
  repositories, APIs, architecture, operations, and onboarding using
  Diataxis-aware routing and repo-verified evidence. Use when the user asks to
  document code, revise existing docs, audit documentation quality, create or
  refresh a README, write a tutorial, how-to, reference, explanation,
  runbook, architecture doc, API doc, onboarding guide, or simply says
  "document this". Use whenever documentation is
  written, changed, or judged, even if the user does not name this skill.
license: MIT
compatibility: >
  Works with Markdown-based documentation and local repository access. No
  network access is needed unless the user explicitly provides external
  sources to use.
metadata:
  version: "1.2"
---

# Documentation

## Purpose

Creates, reviews, and improves technical documentation that is accurate,
reader-oriented, and anchored to the repository.

This skill is a router. `SKILL.md` defines the workflow and decision points.
Detailed instructions live in `references/` so the agent can load only the
path needed for the current documentation job.

## When To Use

- A user asks to document a feature, module, command, workflow, or repository.
- A user asks to create, refresh, rewrite, or restructure a `README.md`.
- A user asks for a tutorial, how-to guide, reference doc, or explanation.
- A user asks for API documentation, architecture documentation, or a runbook.
- A user asks for onboarding material for developers, operators, or reviewers.
- A user asks to review, audit, validate, or clean up existing documentation.
- A user says "document this", "write docs for", "review this documentation",
  "audit these docs", or similar phrasing.

## When Not To Use

- Creating or editing an Agent Skill itself. Use `creating-skills`.
- Generating git commit messages. Use `generating-commit-messages`.
- Making code changes with no documentation output requested.
- Pull-request-level code review for code defects. Use `code-review`.

## Inputs

Collect the minimum context required to route and execute the task:

- **Task mode**: create, update, review, audit, or restructure.
- **Document type**: README, tutorial, how-to, reference, explanation, API doc,
  runbook, architecture doc, onboarding guide, or project-wide docs.
- **Audience**: newcomer, contributor, maintainer, operator, reviewer, or
  another explicit reader.
- **Reader goal**: what the reader should be able to do or understand.
- **Scope**: what is in and what is out.
- **Requested outcome**: exact files, sections, review findings, or structural
  changes the user expects.
- **Evidence**: source code, tests, config, CLI help text, examples, schemas,
  diagrams, and existing docs.
- **Constraints**: requested language, file paths, tone, and repository
  conventions.

Infer missing context from the repository when safe. Ask the user only when the
ambiguity would materially change the output.

## Internal Routes

Load the relevant reference for the work type. Always load the review path for
final checking.

- **README work**: See [references/readme.md](references/readme.md)
- **Tutorial work**: See [references/tutorials.md](references/tutorials.md)
- **How-to guide work**: See [references/how-to-guides.md](references/how-to-guides.md)
- **Reference doc work**: See [references/reference-docs.md](references/reference-docs.md)
- **Explanation work**: See [references/explanations.md](references/explanations.md)
- **API documentation work**: See [references/api-docs.md](references/api-docs.md)
- **Runbook work**: See [references/runbooks.md](references/runbooks.md)
- **Architecture documentation work**: See [references/architecture-docs.md](references/architecture-docs.md)
- **Onboarding guide work**: See [references/onboarding-guides.md](references/onboarding-guides.md)
- **Project-wide documentation work**: See [references/project-docs.md](references/project-docs.md)
- **Documentation review and dual validation**: See [references/review-and-validation.md](references/review-and-validation.md)

## Method

### 1. Classify the task before writing anything

Determine both:

- the **task mode**: create, update, review, audit, or restructure
- the **document type**: tutorial, how-to, reference, explanation, README,
  API doc, runbook, architecture doc, onboarding guide, or project-wide docs

Why this matters: documentation quality drops fast when the agent uses the
wrong format. Review work and creation work are not the same task.

### 2. Open the correct internal path

Use this routing rule:

1. Open the reference for the requested document type.
2. Always open [references/review-and-validation.md](references/review-and-validation.md).
3. If the request spans the whole repository, also open
   [references/project-docs.md](references/project-docs.md).

This keeps the base skill small while making each work type explicit and
searchable.

### 3. Gather repository evidence before drafting or judging

Read the smallest set of artifacts that can prove the document's claims:

- implementation files
- tests
- configuration files
- example files
- CLI help text
- schemas and contracts
- existing documentation

Do not invent commands, file paths, defaults, architecture, or examples.
Every important claim should be backed by a local artifact or clearly labeled
as an assumption.

### 4. Build a fact map

Before drafting or reviewing, map the key claims to their evidence:

- claim
- supporting file or artifact
- exact command, path, schema field, or behavior being documented

The fact map can stay implicit for small tasks, but the validation standard
does not change.

### 5. Execute by mode

- **Create or update**: write the document in the format defined by the routed
  reference file.
- **Review or audit**: identify inaccuracies, omissions, contradictions,
  unclear audience targeting, weak examples, and stale operational guidance
  before proposing rewrites.
- **Restructure**: reduce duplication, improve navigation, and split large
  documents into maintainable units without changing verified facts.

### 6. Run dual validation

Validation must happen in two dimensions:

1. **Repository validation**: confirm the facts against code, tests, config,
   and other repository artifacts before drafting conclusions and after edits.
2. **Request validation**: confirm the output matches what the user actually
   asked for, including scope, audience, document type, requested language,
   exclusions, and expected deliverable shape.

Use the detailed validation workflow in
[references/review-and-validation.md](references/review-and-validation.md).

Why this matters: documentation often becomes wrong during editing, even when
the initial understanding was correct.

### 7. Require an independent subagent final review

When the environment supports delegated agents, run an independent subagent
that did not author the documentation or primary review findings.

That subagent must validate both:

- the documentation against repository evidence
- the documentation against the user's requested outcome

The subagent should return concrete findings, missing scope, unsupported
claims, contradictions, and residual risks. Only deliver after resolving or
explicitly reporting those findings.

If delegated agents are unavailable, perform a fresh final pass using the same
checklist while treating the current document as if it were written by someone
else.

### 8. Deliver the right output shape

- For **review-only** requests, return findings first and proposed fixes second.
- For **write/update** requests, deliver the document with concise notes on
  what was verified.
- For **broad repository work**, prefer a navigation hub plus split documents
  instead of one large wall of text.

## Quality Checklist

- [ ] The correct internal reference path was loaded for the document type.
- [ ] `references/review-and-validation.md` was used before delivery.
- [ ] Audience, reader goal, and scope are explicit or safely inferred.
- [ ] The requested outcome is explicit or safely inferred.
- [ ] All important claims are verified against repository evidence or clearly
      marked as assumptions.
- [ ] The output matches what the user asked for, not just what the repository
      supports.
- [ ] The document format matches the job: tutorial teaches, how-to solves,
      reference describes, explanation clarifies.
- [ ] Commands, paths, flags, identifiers, and examples match the project.
- [ ] Review tasks call out stale or contradictory content instead of silently
      rewriting facts.
- [ ] Large documentation changes improve navigation and reduce duplication.
- [ ] An independent subagent review was completed, or the fallback isolated
      final pass was used when subagents were unavailable.
- [ ] The final output passes the second validation pass after edits.

## Outputs

Depending on the request, this skill produces one or more of:

- new or updated Markdown documentation files
- documentation review findings with concrete corrections
- a concise `README.md` hub
- tutorials, how-to guides, reference docs, and explanation docs
- API docs, runbooks, architecture docs, and onboarding guides
- a structured documentation tree for broader repositories
