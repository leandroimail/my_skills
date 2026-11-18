---
name: generating-commit-messages
description: >
  Generates git commit messages using Conventional Commits format according to
  standards. Use whenever the user asks to write, generate, or format a commit
  message from git diffs or descriptions, or says "commit this", "mensagem de
  commit", or "commitar", even if they do not name this skill.
compatibility: Requires git.
---

# Generating Commit Messages

## Purpose

Enforces standard Conventional Commits formatting for all code changes. Ensures consistency, correct classification (feat, fix, chore, etc.), and English descriptions.

## When To Use

- The user asks you to write a commit message.
- The user provides a `git diff` and wants a commit message.
- The user gives a rough description of changes to be committed.

## When Not To Use

- Pull request titles or descriptions (use the `creating-pull-requests` skill).
- Changelogs or release notes.

## Inputs

- A `git diff` (staged or not), a list of changed files, or a rough description of the changes.
- Optionally: issue references for the footer and project scope names.

## Requirements

1. Generate the commit message in English, so history stays readable for every contributor and tooling.
2. Think step-by-step and write each thought step in English, so the reasoning and the final message use the same vocabulary.
3. Transform the input prompt into thoughts in English before generating the final message, so the message does not carry over the input language.
4. Always include a scope: it lets readers filter history by area and keeps changelogs navigable.

## Method

1. Read the diff or description; list what changed and why.
2. Group the changes by affinity (see Grouping Strategy).
3. For each group, pick the type from the accepted table and a lowercase scope.
4. Write the short message, then the long message (context, motivation, what was done).
5. Run the Quality Checklist before presenting.

## Format

Follow strict **Conventional Commits** format:

```text
<type>(<scope>): <short description in English>

[optional body - detailed description]

[optional footer - issue references]
```

## Commit Types Accepted

| Type | Description |
|------|-------------|
| `feat` | New functionality |
| `fix` | Bug fix |
| `revert` | Revert previous commit |
| `docs` | Documentation only |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Add or fix tests |
| `ci` | CI/CD changes |
| `chore` | Maintenance tasks |
| `style` | Code formatting (does not affect logic) |

## Commit Examples

```text
feat(auth): implement OAuth 2.0 login flow
```

```text
fix(api): correct CPF validation in customer registration
```

```text
refactor(database): optimize PostgreSQL queries with composite indexes
```

```text
perf(sqs): implement batch processing to reduce latency
```

```text
test(payment): add integration tests for payment flow
```

```text
docs(readme): update local setup instructions
```

```text
chore(deps): update Spring Boot to version 3.2.1
```

```text
ci(github-actions): add dependency cache for Maven
```

## Grouping Strategy

When generating commits for multiple artifacts, **group by affinity** — files or changes that relate to the same feature, fix, or purpose should be grouped together. This includes:

- Scripts, planning documents, configurations, and documentation can be unified in the same affinity group when they serve a common purpose.
- Aim for coherent, meaningful groups rather than one commit per file.

## Message Structure

For each group, generate:

1. **Short message**: Concise summary in English (follows Conventional Commits format).
2. **Long message**: Detailed description that explains:
   - **Context**: Background and situation that led to the change.
   - **Motivation**: Why the change was needed or what problem it solves.
   - **What was done**: Concrete actions taken and their outcome.

## Quality Checklist

- [ ] Uses one of the accepted commit types.
- [ ] Description is in English.
- [ ] Follows the specific `<type>(<scope>): <description>` structure.
- [ ] Scope is present and lowercase.
- [ ] No trailing periods in the short description.
- [ ] Short description starts with a lowercase letter.
- [ ] Changes are grouped by affinity when multiple artifacts are involved.
- [ ] Long message includes context, motivation, and what was done.

## Outputs

For each group of changes: a short message in `<type>(<scope>): <description>` format, followed by a long message with context, motivation, and what was done. Optional footer with issue references.
