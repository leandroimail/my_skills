# Workflow Detail

Expanded instructions for each phase of the task planning and execution
workflow. Read this file when executing the skill for the first time or when
you need clarification on a specific phase.

## Table of Contents

- [Phase 0: Initialize Plan Directory](#phase-0-initialize-plan-directory)
- [Phase 1: Understand and Design](#phase-1-understand-and-design)
- [Phase 2: Plan Tasks](#phase-2-plan-tasks)
- [Phase 3: Human Review Gate](#phase-3-human-review-gate)
- [Phase 4: Execute Tasks](#phase-4-execute-tasks)
- [Phase 5: Completion and Archival](#phase-5-completion-and-archival)

## Phase 0: Initialize Plan Directory

### Sequence Number Discovery

1. List all directories inside `.plan/` (create `.plan/` if it does not exist).
2. Extract the numeric prefix from each directory name.
3. Determine the next sequential number.
4. If no directories exist, start at `0000`.

### Directory Naming

```
.plan/XXXX_request-name/
```

Rules:

- `XXXX`: Zero-padded 4-digit sequence number.
- `request-name`: Kebab-case slug derived from the user's request.
  - Remove articles (a, an, the).
  - Truncate to 50 characters maximum.
  - Use only lowercase letters, numbers, and hyphens.

Examples:

```
.plan/0000_initial-project-setup/
.plan/0001_add-user-authentication/
.plan/0002_refactor-payment-module/
.plan/0003_fix-dashboard-performance/
```

### Initial Files

Create these immediately upon initialization:

1. `design.md`
2. `tasks.md`
3. `current_state.md`
4. `implementation_log.md`
5. `tasks/` (empty subdirectory for per-task folders)

## Phase 1: Understand and Design

This phase is about deep understanding before any code is written. Inspired by
GSD's "discuss" phase and spec-kit's "specify" + "clarify" steps.

### Step 1.1: Analyze the Request

- Restate the user's request in your own words.
- Identify ambiguities, implicit assumptions, and gray areas.
- If ambiguities exist, ask the user for clarification before proceeding.

### Step 1.2: Analyze the Project

- Examine the existing codebase relevant to the request.
- Identify files, patterns, conventions, and constraints.
- Note any architectural decisions that affect the implementation.
- Document the current state of the relevant parts of the codebase.

### Step 1.3: Design the Solution

- Propose a solution design with clear rationale.
- Document trade-offs and alternatives considered.
- Specify what is in scope and what is explicitly out of scope.
- If the solution is complex, use diagrams or structured breakdowns.

### Step 1.4: Write design.md

Combine all findings into `design.md` following the `design.md` template
(see the Document Templates entry in SKILL.md).

### Step 1.5: Initialize State and Log

- Write the first entry in `current_state.md` documenting the project baseline.
- Write the first entry in `implementation_log.md` documenting the analysis
  phase and its findings.

## Phase 2: Plan Tasks

This phase decomposes the solution into atomic, verifiable tasks. Inspired by
GSD's XML task plans and spec-kit's task breakdown.

### Decomposition Strategy

Use the following hierarchy:

```
Solution
├── Phase 1: [Logical Group Name]
│   ├── tasks/1.1_task-name/   ← task_plan.md + task_design.md
│   ├── tasks/1.2_task-name/
│   └── tasks/1.3_task-name/
├── Phase 2: [Logical Group Name]
│   ├── tasks/2.1_task-name/
│   └── tasks/2.2_task-name/
└── Phase 3: [Logical Group Name]
    └── tasks/3.1_task-name/
```

### Task Atomicity Criteria

A task is atomic if:

- It can be verified independently.
- It touches a focused set of files (ideally ≤ 5).
- It takes less than ~30 minutes of focused work.
- Its success or failure is objectively measurable.

### Per-Task Folder Creation

For each task in the decomposition:

1. Create directory: `tasks/X.Y_task-name/`
2. Create `task_plan.md` — self-contained execution plan with:
   - Files, actions, verification criteria, done criteria.
   - Empty execution log section (populated during Phase 4).
3. Create `task_design.md` — task-specific design context with:
   - Relevant design decisions extracted from global `design.md`.
   - Files involved and their current state.
   - Constraints, patterns, and approach for this task.

### Dependency Management

- List dependencies between tasks explicitly.
- Tasks without dependencies on prior tasks can be marked `[P]` (parallel-safe).
- Never create circular dependencies.
- Respect the natural order: config/variables → strategies → trading → backtest → models → main.

### Writing tasks.md

The global `tasks.md` is a **master index** with summary table rows
and links to each task folder. Task details live in `task_plan.md`.

Follow the `tasks.md` template and the task design guidance listed in
SKILL.md's Reference Documentation.

## Phase 3: Human Review Gate

This is the most critical phase. **Never skip it.**

### Presentation Format

Present to the user:

1. **Summary**: One paragraph describing what will be built.
2. **Design highlights**: Key decisions from `design.md`.
3. **Task overview**: Count of tasks, estimated complexity, files affected.
4. **Links**: Paths to `design.md` and `tasks.md` for detailed review.
5. **Explicit question**: Ask for approval or change requests.

### Handling Change Requests

If the user requests changes:

1. Acknowledge the feedback.
2. Update the relevant documents.
3. Log the change and rationale in `implementation_log.md`.
4. Re-present the updated plan for approval.
5. Do not proceed until explicit approval is given.

### Approval Formats

Accept approval in any of these forms:

- "Yes", "Approved", "Go ahead", "Looks good", "LGTM"
- "Proceed with changes" (after adjustments)
- An explicit thumbs-up or approval indicator

## Phase 4: Execute Tasks

### Pre-Flight Checklist (Before Each Task)

Before executing any task, load context from the **task's own folder**:

- [ ] The task's `task_plan.md` (self-contained execution plan).
- [ ] The task's `task_design.md` (task-specific design context).
- [ ] The latest `current_state.md` entry (global position).
- [ ] The `design.md` key decisions (global, if needed beyond task_design.md).

If any of these are stale or unavailable, re-read them from disk.

### Execution Loop

For each task:

```
1. READ  → Load task_plan.md and task_design.md from task folder.
2. PLAN  → Mentally outline the implementation approach.
3. ACT   → Implement the task.
4. CHECK → Run verification criteria from task_plan.md.
5. LOG   → Update task-level and global tracking artifacts.
```

### Post-Task Updates

After each task, update **both** task-level and global files:

**Task-level** (in `tasks/X.Y_task-name/`):

1. Append execution log entry to `task_plan.md` (Execution Log section).
2. Update status in `task_plan.md` to `✅ Done` with timestamp.

**Global** (in plan root):

1. Mark the task as `[DONE ✅ YYYY-MM-DDTHH:MM:SS]` in `tasks.md`.
2. Append state entry in `current_state.md`.
3. Append log entry in `implementation_log.md` with:
   - What was done.
   - Files changed.
   - Verification results.
   - Any issues encountered and resolutions.
   - Decisions made during implementation.

## Phase 5: Completion and Archival

### Final State Update

Write a closing entry in `current_state.md`:

```markdown
## [YYYY-MM-DDTHH:MM:SS] — IMPLEMENTATION COMPLETE

All tasks completed. Final state:
- Total tasks: X
- Completed: X
- Failed: 0
- Files changed: [list]
- Key decisions: [summary]
```

### IDE/CLI Artifact Archival

Copy any planning or tracking artifacts generated by the IDE or CLI tool
to the plan directory for archival. Adapt the list below to the tool in use:

| Source (if exists) | Destination |
|---------------------|-------------|
| `implementation_plan.md` | `.plan/XXXX_name/implementation_plan.md` |
| `task.md` | `.plan/XXXX_name/task.md` |
| `.plan/walkthrough.md` | `.plan/XXXX_name/walkthrough.md` |

Before copying:

1. Verify the source files exist.
2. Ensure they reflect the latest state.
3. If they don't exist, log the absence and continue.

### Completion Report

Present to the user:

```markdown
## Implementation Complete ✅

**Plan**: `.plan/XXXX_name/`
**Tasks**: X completed, 0 failed
**Duration**: [start] → [end]

### Changes Made
- [Summary of key changes]

### Files Modified
- [List of files]

### Key Decisions
- [Important choices made during implementation]

### Archived Artifacts
- [List of copied IDE artifacts]
```
