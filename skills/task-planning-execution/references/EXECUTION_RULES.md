# Execution Rules

Rules and procedures for executing tasks, handling errors, and managing context
during the execution phase. Read this when entering Phase 4 of the workflow.

## Table of Contents

- [Pre-Execution Validation](#pre-execution-validation)
- [Execution Loop](#execution-loop)
- [Context Loading Per Task](#context-loading-per-task)
- [Error Handling Procedures](#error-handling-procedures)
- [Blocking Errors vs. Non-Blocking Errors](#blocking-errors-vs-non-blocking-errors)
- [Task Modification During Execution](#task-modification-during-execution)
- [Progress Reporting](#progress-reporting)

## Pre-Execution Validation

Before starting execution of any task, validate:

1. **Approval gate passed**: Human approval was received (check
   `current_state.md` for approval entry).
2. **Tasks are current**: The `tasks.md` file reflects the approved plan,
   including any change requests.
3. **Dependencies met**: All prerequisite tasks are marked as done.
4. **State is consistent**: `current_state.md` and `implementation_log.md`
   are up-to-date.

If any validation fails, resolve the issue before proceeding.

## Execution Loop

For each task, follow this explicit loop:

### 1. READ — Load Context

```
Load from task folder (tasks/X.Y_task-name/):
├── task_plan.md → self-contained plan for this task
├── task_design.md → task-specific design context

Load from plan root (if needed):
├── current_state.md → confirm current position
└── design.md → global decisions (only if beyond task_design.md)
```

### 2. PLAN — Outline Approach

Before touching any file:

- Identify all files that will be modified or created.
- Confirm the approach aligns with `design.md`.
- If the task requires a decision not covered in `design.md`, document the
  decision in `implementation_log.md` before proceeding.

### 3. ACT — Implement

Execute the task actions as specified. Rules:

- Follow the project's existing conventions and patterns.
- Do not introduce dependencies not specified in the design.
- Do not modify files outside the task's declared scope.
- If the implementation reveals a flaw in the plan, stop and document it.

### 4. CHECK — Verify

Run the task's verification criteria:

- Execute any test commands specified.
- Check build/compilation status.
- Verify the done criteria are met.
- If verification fails, enter error handling.

### 5. LOG — Update Artifacts

Update **both** task-level and global tracking files:

**Task-level** (in `tasks/X.Y_task-name/`):

- `task_plan.md`: Append execution log entry, update status.

**Global** (in plan root):

- `tasks.md`: Mark task as done with timestamp.
- `current_state.md`: Append new state entry.
- `implementation_log.md`: Append detailed execution log.

**Critical**: Do this immediately after each task, not in batch.
If the session crashes, the progress is preserved.

## Context Loading Per Task

### Minimal Context Loading

Load only what the current task needs. Do not load the entire project history
into context for every task.

| Always Load | Load If Relevant | Do Not Load |
|-------------|-----------------|-------------|
| `task_plan.md` from task folder | Previous task's log entry (if dependent) | Completed tasks' full logs |
| `task_design.md` from task folder | Global `design.md` (if task_design.md insufficient) | Unrelated phase artifacts |
| Latest `current_state.md` entry | Error resolution history | Historical design alternatives |

### Context Refresh Triggers

Reload artifacts from disk when:

- Starting a new task.
- Recovering from an error.
- Resuming after a session break.
- The task depends on a recently completed task.

### Anti-Pattern: Context Accumulation

Do **not** carry implementation details from prior tasks in memory.
The log files persist this information. Re-read from files when needed.
This is the core principle that prevents context rot.

## Error Handling Procedures

### Error Classification

| Category | Description | Action |
|----------|-------------|--------|
| **Build error** | Code does not compile/transpile | Fix immediately, log, re-verify |
| **Test failure** | Tests do not pass | Analyze, fix, log, re-verify |
| **Design conflict** | Task reveals design flaw | Stop, document, consult user |
| **Dependency error** | External dependency issue | Document workaround, log |
| **Scope creep** | Task requires unplanned changes | Stop, document, consult user |

### Error Handling Steps

1. **Capture**: Log the full error message and stack trace in
   `implementation_log.md`.
2. **Analyze**: Determine root cause and category.
3. **Decide**:
   - If fixable within task scope → fix, log resolution, re-verify.
   - If requires design change → stop, update docs, consult user.
   - If blocking → mark task as blocked, move to next if possible.
4. **Document**: Every error and its resolution goes in the log,
   regardless of how trivial.

## Blocking Errors vs. Non-Blocking Errors

### Non-Blocking (Self-Resolvable)

Errors that can be resolved without changing the plan:

- Typos in code.
- Missing imports.
- Test failures caused by the current task's code.
- Minor refactoring needed for the current task.

**Action**: Fix, document, continue.

### Blocking (Requires Human Input)

Errors that indicate a plan problem:

- The design assumption was wrong.
- A dependency does not work as expected.
- The task scope is significantly larger than estimated.
- The approach needs a fundamentally different strategy.

**Action**: Stop, document fully, present to the user with:

```markdown
## ⚠️ Blocking Issue in Task X.Y

**Task**: [title]
**Issue**: [description]
**Root Cause**: [analysis]
**Impact**: [what cannot proceed]
**Options**:
1. [Option A — description, trade-offs]
2. [Option B — description, trade-offs]
3. [Option C — skip for now, revisit later]

Which approach would you like to take?
```

## Task Modification During Execution

Sometimes execution reveals that tasks need adjustment.

### Minor Adjustments (Agent Decides)

- Changing the order of actions within a task.
- Adding an import or utility function implied by the task.
- Adjusting file paths due to project conventions.

**Action**: Proceed, document the adjustment in the log.

### Moderate Adjustments (Log and Proceed)

- Splitting a task that turned out to be larger than expected.
- Adding a small preparatory task that was missed.
- Adjusting verification criteria based on actual implementation.

**Action**: Update `tasks.md`, log the change with rationale, proceed.

### Major Adjustments (Require Human Approval)

- Adding entirely new tasks not in the original plan.
- Changing the design approach.
- Removing planned tasks.
- Altering scope (in or out).

**Action**: Stop, present changes, get approval before proceeding.

## Progress Reporting

### After Each Phase

When completing a group of related tasks (a logical phase), present a brief
progress report:

```markdown
## Phase N Complete: [Phase Name]

**Tasks completed**: X/Y
**Status**: ✅ All passed | ⚠️ Issues (see below)

### Completed
- Task N.1: [title] ✅
- Task N.2: [title] ✅

### Issues (if any)
- Task N.3: [description of issue and resolution]

### Next Phase
- Phase N+1: [name] — [N tasks]
```

### On Completion

Provide the full completion report as described for Phase 5 (completion and
archival) in the workflow details listed in SKILL.md.
