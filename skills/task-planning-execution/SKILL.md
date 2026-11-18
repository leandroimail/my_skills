---
name: task-planning-execution
description: >
  Plans, tracks, and executes code-creation tasks using spec-driven development,
  durable context engineering, and structured state management. Maintains a
  .plan/ directory with numbered folders, design documents, task breakdowns,
  execution logs, and state tracking, with context preservation across sessions,
  human approval gates, and post-execution archival. Use whenever the user asks
  to implement a feature, build a module, refactor code, migrate or rewrite
  something, or do any multi-step coding work ("implemente", "planeje",
  "refatore", "continue de onde parou", "resume the plan"), even if the user
  does not mention planning or this skill. Skip it for one-line fixes.
---

# Task Planning and Execution

## Purpose

Guide the agent through a disciplined, spec-driven workflow for planning and
executing code-creation tasks of any size. Externalizes project state into
durable file artifacts to defeat context rot, enforces human approval gates,
and maintains a complete audit trail.

This skill is optimized for:

- Multi-step coding tasks that benefit from upfront planning.
- Context preservation across long sessions and session restarts.
- Human-in-the-loop approval before execution begins.
- Complete auditability via logs, state tracking, and design documents.

## When To Use

Use this skill when you need to:

- Plan and implement a new feature, module, or system.
- Refactor existing code with a structured approach.
- Execute any multi-step coding task that benefits from decomposition.
- Maintain execution history and decision logs for future reference.
- Resume interrupted work across sessions.

## When Not To Use

Do not use this skill for:

- One-line fixes or trivial changes (use direct editing).
- Pure research or analysis with no code output.
- Questions about how to approach something (answer directly first).
- Tasks the user explicitly wants executed without planning.

## Inputs

Before starting, collect:

- **User request**: The high-level description of what to build or change.
- **Existing context**: Any relevant PRDs, specs, or prior conversations.
- **Scope boundaries**: What is in scope vs. out of scope for this request.

## Method

Follow this workflow exactly. Each phase has a clear gate before proceeding.

> See [WORKFLOW_DETAIL.md](references/WORKFLOW_DETAIL.md) for expanded
> instructions on each phase.

### Phase 0: Initialize Plan Directory

1. Check `.plan/` directory for the last numbered folder (format `XXXX_name`).
2. Create the next sequential folder: `.plan/XXXX_request-name/`.
3. Create the `tasks/` subdirectory inside the plan folder.
4. Timestamp the creation in the log.

**Naming rules:**

- `XXXX` is zero-padded sequential (0000, 0001, 0002...).
- `request-name` is a kebab-case slug derived from the user's request.
- Example: `.plan/0003_add-user-auth/`.

### Phase 1: Understand and Design

Create three foundational documents in the plan folder:

1. **`design.md`** — Understanding and solution design:
   - Summary of the user's request in your own words.
   - Analysis of the current project state relevant to the request.
   - Proposed solution design with rationale.
   - Key decisions and trade-offs considered.
   - Out-of-scope items explicitly noted.

2. **`current_state.md`** — Implementation state tracker (append-only):
   - Initial entry with project baseline.
   - Updated after every significant action.
   - Each entry timestamped.

3. **`implementation_log.md`** — Detailed execution log (append-only):
   - All decisions, discoveries, and actions with timestamps.
   - Errors encountered and how they were resolved.
   - Rationale for non-obvious choices.

> See [DOCUMENT_TEMPLATES.md](references/DOCUMENT_TEMPLATES.md) for the exact
> structure of each document.

### Phase 2: Plan Tasks

Create the task breakdown in two layers:

1. **`tasks.md`** — Master task index with:
   - Sequential numbering (1.1, 1.2, 2.1...).
   - Each task: title, complexity, status, and link to task folder.
   - Dependencies marked explicitly.
   - Parallel-safe tasks marked with `[P]`.

2. **Per-task folders** — For each task, create:
   - Directory: `tasks/X.Y_task-name/`
   - **`task_plan.md`** — Self-contained execution plan: files, actions,
     verification criteria, done criteria, and inline execution log.
   - **`task_design.md`** — Task-specific design context: relevant subset
     of global `design.md`, files involved, constraints, and approach.

**Task design rules:**

- Each task should be atomic and independently verifiable.
- Each task folder must be self-contained for execution without needing
  to parse the global `tasks.md` for task details.
- Tasks should follow dependency order.
- Group by logical phases (e.g., Phase 1: Models, Phase 2: Services).
- Include verification step in every task.

**Task folder naming:** `X.Y_task-name/` where `X.Y` is the task number
and `task-name` is a kebab-case slug (e.g., `1.1_create-user-model/`).

> See [TASK_DESIGN.md](references/TASK_DESIGN.md) for decomposition strategies
> and task template.

### Phase 3: Human Review Gate

**⛔ MANDATORY STOP — Do not proceed without explicit user approval.**

Present to the user for review:

1. The `design.md` — solution understanding and design.
2. The `tasks.md` — complete task breakdown.
3. A summary of total tasks, estimated complexity, and files affected.

Ask explicitly:

> "I've prepared the implementation plan and task breakdown. Please review:
>
> - Design: `.plan/XXXX_name/design.md`
> - Tasks: `.plan/XXXX_name/tasks.md`
>
> Do you approve proceeding with implementation? Any adjustments needed?"

**Wait for explicit approval.** If the user requests changes, update the
documents and re-present for approval.

### Phase 4: Execute Tasks

For each task in order:

1. **Pre-flight check**: Load context from the task's own folder:
   - `task_plan.md` — what to do (self-contained).
   - `task_design.md` — design context for this task.
   - Latest entry from `current_state.md` (global).
   - Relevant entries from `implementation_log.md` (global, if dependent).

2. **Execute**: Implement the task following `task_plan.md`.

3. **Verify and Self-Review**: Run the task's verification criteria from `task_plan.md`. Then, ALWAYS run an inline self-review of your changes before marking the task as completed, by invoking the review skill that matches the stack: the `receiving-code-review` skill for Python, or the `receiving-code-review-js` skill for TypeScript/JavaScript. In a mixed project, review each changed file with the skill for its language; for any other language, use `receiving-code-review` and skip its Python-specific tool steps. Self-review catches defects while the context is still fresh, which is cheaper than finding them after the task is closed.

4. **Update artifacts** (both task-level and global):
   - Append execution log entry to `task_plan.md` (inline log section).
   - Update task status in `task_plan.md`.
   - Mark task as completed in global `tasks.md` with timestamp.
   - Append new state entry to global `current_state.md`.
   - Append execution details to global `implementation_log.md`.

> See [EXECUTION_RULES.md](references/EXECUTION_RULES.md) for context
> management during execution and error handling procedures.

### Phase 5: Completion and Archival

When all tasks are completed:

1. **Final state update**: Write closing entry in `current_state.md`.
2. **Final log entry**: Write completion summary in `implementation_log.md`.
3. **Copy workspace artifacts**: Copy any relevant planning or tracking files
   generated by the IDE or CLI tool to `.plan/XXXX_name/` for archival:
   - Implementation plan files (if generated by the tool)
   - Task tracking files (if generated by the tool)
   - Walkthrough or summary files (if generated by the tool)
4. **Verify copies**: Ensure copied files reflect the latest state.
5. **Summary report**: Present completion summary to the user.

## Context Management Strategy

These rules prevent context rot during long executions.

> See [CONTEXT_MANAGEMENT.md](references/CONTEXT_MANAGEMENT.md) for detailed
> context engineering patterns.

**Core principles:**

1. **State lives in files, not in chat.** Every decision, action, and outcome
   is written to the plan directory immediately.
2. **Read before act.** Before each task, re-read the relevant plan artifacts.
3. **Append, never overwrite.** State and log files use append-only entries.
4. **Scope context per task.** Load only what the current task needs.
5. **Timestamp everything.** Every entry includes ISO 8601 timestamp.

## Outputs

- A `.plan/XXXX_name/` folder with `design.md`, `tasks.md`, `current_state.md`, `implementation_log.md`, and one `tasks/X.Y_task-name/` folder per task (`task_plan.md`, `task_design.md`).
- The implemented code changes, each task verified and self-reviewed.
- An updated audit trail (state entries, execution logs) and a completion report.
- After completion, archived plan artifacts.

## Quality Checklist

A plan-and-execute cycle is acceptable only if all checks pass:

- [ ] Plan directory follows naming convention `XXXX_kebab-name`.
- [ ] `design.md` captures understanding, project analysis, and solution design.
- [ ] `tasks.md` is a master index with links to task folders.
- [ ] Each task has its own folder under `tasks/` with `task_plan.md` and `task_design.md`.
- [ ] Each `task_plan.md` is self-contained for independent execution.
- [ ] Human approval was obtained before execution.
- [ ] `current_state.md` has timestamped entries for every state change.
- [ ] `implementation_log.md` has entries for every action and decision.
- [ ] All tasks have verification criteria that were checked.
- [ ] Errors are documented with resolution in the log.
- [ ] IDE artifacts were copied at completion.
- [ ] Completion summary was presented to the user.

## Error Handling

When errors occur during execution:

1. Log the error with full details in `implementation_log.md`.
2. Update `current_state.md` with error state.
3. Attempt resolution and document the approach.
4. If resolution fails, **stop and consult the user** with:
   - What was attempted.
   - What failed and why.
   - Proposed alternatives.

## Session Recovery

If a session is interrupted or restarted:

1. Read `current_state.md` to restore position.
2. Read `implementation_log.md` for recent activity.
3. Read `tasks.md` to identify next incomplete task.
4. Navigate to the task's folder (`tasks/X.Y_task-name/`).
5. Read `task_plan.md` to load the task's self-contained context.
6. Resume from the last incomplete task.
7. Log the session recovery in `implementation_log.md`.

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| Skipping human approval | User loses oversight, wrong direction | Always gate on Phase 3 |
| Monolithic tasks | Too large to verify or debug | Decompose to atomic units |
| State in chat only | Lost on session restart | Write to plan files immediately |
| Overwriting state files | History is lost | Append-only with timestamps |
| Ignoring verification | Errors compound silently | Verify after every task |
| No error documentation | Same mistakes repeat | Log everything in detail |
| Skipping context reload | Stale context causes drift | Read artifacts before each task |

## Reference Documentation

- **Workflow Details**: [WORKFLOW_DETAIL.md](references/WORKFLOW_DETAIL.md)
- **Document Templates**: [DOCUMENT_TEMPLATES.md](references/DOCUMENT_TEMPLATES.md)
- **Task Design Guide**: [TASK_DESIGN.md](references/TASK_DESIGN.md)
- **Execution Rules**: [EXECUTION_RULES.md](references/EXECUTION_RULES.md)
- **Context Management**: [CONTEXT_MANAGEMENT.md](references/CONTEXT_MANAGEMENT.md)

## Inspirations and External References

- [GSD (Get Shit Done)](https://github.com/gsd-build/get-shit-done) — Context engineering and wave-based execution
- [GitHub Spec Kit](https://github.com/github/spec-kit) — Spec-driven development workflow
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — Lightweight artifact-guided workflow
- [Addy Osmani: How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/) — Spec-writing best practices
- [Martin Fowler: Understanding SDD](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) — SDD tool comparison
