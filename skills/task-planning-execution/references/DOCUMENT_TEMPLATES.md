# Document Templates

Templates for all plan directory documents. Use these exact structures when
creating files in the `.plan/XXXX_name/` directory.

## Table of Contents

- [design.md Template](#designmd-template)
- [tasks.md Template](#tasksmd-template)
- [task_plan.md Template](#task_planmd-template)
- [task_design.md Template](#task_designmd-template)
- [current_state.md Template](#current_statemd-template)
- [implementation_log.md Template](#implementation_logmd-template)

## design.md Template

```markdown
# Design: [Request Name]

**Created**: YYYY-MM-DDTHH:MM:SS
**Plan**: .plan/XXXX_request-name/
**Status**: Draft | Approved | In Progress | Complete

## 1. Request Understanding

### Original Request
> [User's exact request or a faithful summary]

### Restated Understanding
[Your interpretation of what the user wants, in your own words.
Highlight any implicit requirements you've identified.]

### Clarifications
[Questions asked and answers received. If none were needed, state so.]

## 2. Project Analysis

### Relevant Codebase Areas
| Area | Path | Purpose | Current State |
|------|------|---------|---------------|
| ... | ... | ... | ... |

### Architecture and Patterns
[Existing patterns, conventions, and architectural decisions
that constrain or guide this implementation.]

### Dependencies and Constraints
[External dependencies, version constraints, performance
requirements, or compatibility concerns.]

## 3. Solution Design

### Approach
[High-level description of the proposed solution.]

### Key Decisions
| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| ... | ... | ... | ... |

### Component Design
[Detailed breakdown of components, modules, or layers
involved in the solution.]

### Data Flow
[How data moves through the system for this feature.
Use a diagram if helpful.]

## 4. Scope

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1 — reason]
- [Item 2 — reason]

### Future Considerations
[Items to revisit in future iterations.]

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ... | Low/Med/High | Low/Med/High | ... |
```

## tasks.md Template

The `tasks.md` serves as a **master index** — a summary view with links
to self-contained task folders. Task details live in each task's own folder.

```markdown
# Tasks: [Request Name]

**Created**: YYYY-MM-DDTHH:MM:SS
**Plan**: .plan/XXXX_request-name/
**Total Tasks**: N
**Status**: Pending Review | Approved | In Progress | Complete

## Summary

| Phase | Tasks | Complexity | Status |
|-------|-------|-----------|--------|
| Phase 1: [Name] | N | S/M/L | ⬜ Pending |
| Phase 2: [Name] | N | S/M/L | ⬜ Pending |
| Total | N | | |

---

## Phase 1: [Phase Name]

| Task | Title | Complexity | Depends On | Parallel | Status | Folder |
|------|-------|-----------|------------|----------|--------|--------|
| 1.1 | [Task Title] | S | None | [P] | ⬜ Pending | [tasks/1.1_task-name/](tasks/1.1_task-name/) |
| 1.2 | [Task Title] | M | 1.1 | N/A | ⬜ Pending | [tasks/1.2_task-name/](tasks/1.2_task-name/) |

---

## Phase 2: [Phase Name]

| Task | Title | Complexity | Depends On | Parallel | Status | Folder |
|------|-------|-----------|------------|----------|--------|--------|
| 2.1 | [Task Title] | M | 1.2 | N/A | ⬜ Pending | [tasks/2.1_task-name/](tasks/2.1_task-name/) |

---

## Completion Log

| Task | Completed At | Notes |
|------|-------------|-------|
| | | |
```

## task_plan.md Template

Self-contained execution plan for a single task. This file contains
everything the agent needs to execute the task independently.

```markdown
# Task X.Y: [Task Title]

**Plan**: .plan/XXXX_name/tasks/X.Y_task-name/
**Status**: ⬜ Pending | 🔄 In Progress | ✅ Done | ❌ Failed
**Created**: YYYY-MM-DDTHH:MM:SS

## Specification

- **Files**: `path/to/file1.ts`, `path/to/file2.ts`
- **Depends on**: [Task X.Z or "None"]
- **Complexity**: S/M/L
- **Parallel**: [P] or N/A

## Actions

1. [Specific action 1]
2. [Specific action 2]
3. [Specific action 3]

## Verification

- [Criterion 1: e.g. "Project builds without errors"]
- [Criterion 2: e.g. "All tests pass" — use the project's runner: `npm test` (JS/TS), `uv run pytest` (Python)]

## Done Criteria

[What "done" looks like for this specific task]

## Execution Log

> Append entries here during execution. This section is append-only.

### [YYYY-MM-DDTHH:MM:SS] — Started

- Approach: [brief description of approach taken]

### [YYYY-MM-DDTHH:MM:SS] — Completed

- Files changed: [list]
- Verification: Passed / Failed [details]
- Notes: [any observations or decisions made]
```

## task_design.md Template

Task-specific design context. Contains only the relevant subset of
the global `design.md` needed for this task's execution.

```markdown
# Design Context: Task X.Y — [Task Title]

**Global Design**: ../../design.md
**Task Plan**: ./task_plan.md

## Relevant Design Decisions

[Extract from global design.md only the decisions that affect this task.
Do not copy the entire design — only the relevant subset.]

| Decision | Choice | Why It Matters Here |
|----------|--------|--------------------|
| ... | ... | ... |

## Files Involved

| File | Role | Current State |
|------|------|---------------|
| `path/to/file.ts` | [What this file does] | [Current state relevant to task] |

## Constraints and Patterns

[Project conventions, architectural constraints, and patterns
that this specific task must follow. Extract from global design.]

## Approach

[How this specific task implements its portion of the global design.
Include any task-specific decisions not covered in the global design.]
```

## current_state.md Template

```markdown
# Current State: [Request Name]

**Plan**: .plan/XXXX_request-name/

> This file is append-only. Each entry represents a state snapshot.
> Never delete or modify previous entries.

---

## [YYYY-MM-DDTHH:MM:SS] — Initialization

**Phase**: Planning
**Status**: Plan directory created
**Context**:
- Project baseline: [brief description]
- Request received for: [brief description]
**Next**: Analyze request and create design document

---

## [YYYY-MM-DDTHH:MM:SS] — Design Complete

**Phase**: Planning
**Status**: Design document created, ready for task decomposition
**Context**:
- Solution approach defined: [brief]
- Key decisions: [brief]
**Next**: Create task breakdown

---

## [YYYY-MM-DDTHH:MM:SS] — Tasks Planned

**Phase**: Planning
**Status**: Task breakdown complete, awaiting human approval
**Context**:
- Total tasks: N
- Phases: N
**Next**: Present for human review

---

## [YYYY-MM-DDTHH:MM:SS] — Approved

**Phase**: Execution
**Status**: Human approval received, beginning execution
**Context**:
- Approved by user at [time]
- Any adjustments: [none / brief description]
**Next**: Execute Task 1.1

---

## [YYYY-MM-DDTHH:MM:SS] — Task X.Y Complete

**Phase**: Execution
**Status**: Task X.Y "[title]" completed
**Context**:
- Files changed: [list]
- Verification: Passed / Failed [details]
**Next**: Execute Task X.Z

---

## [YYYY-MM-DDTHH:MM:SS] — IMPLEMENTATION COMPLETE

**Phase**: Completion
**Status**: All tasks complete
**Context**:
- Total tasks: X completed, 0 failed
- Key outcomes: [brief]
- Artifacts archived: [list]
**Next**: None — implementation complete
```

## implementation_log.md Template

```markdown
# Implementation Log: [Request Name]

**Plan**: .plan/XXXX_request-name/

> This file is append-only. Each entry documents an action, decision,
> or event during the implementation lifecycle.

---

### [YYYY-MM-DDTHH:MM:SS] — Plan Initialized

**Action**: Created plan directory `.plan/XXXX_request-name/`
**Details**:
- Sequence number derived from existing plans
- Request: "[user's request summary]"

---

### [YYYY-MM-DDTHH:MM:SS] — Analysis Phase

**Action**: Analyzed codebase and user request
**Details**:
- Examined: [files/modules examined]
- Findings: [key findings]
- Ambiguities identified: [list or "none"]

---

### [YYYY-MM-DDTHH:MM:SS] — Design Decision

**Action**: Made design decision
**Decision**: [what was decided]
**Rationale**: [why this choice]
**Alternatives**: [what else was considered]

---

### [YYYY-MM-DDTHH:MM:SS] — Task X.Y Execution

**Action**: Executed Task X.Y "[title]"
**Details**:
- Files modified: [list]
- Changes: [summary of changes]
- Verification: [result]
- Issues: [any issues or "none"]
- Resolution: [if issues, how they were resolved]

---

### [YYYY-MM-DDTHH:MM:SS] — Error Encountered

**Action**: Error during Task X.Y
**Error**: [description]
**Root Cause**: [analysis]
**Resolution**: [what was done to fix it]
**Impact**: [impact on timeline or approach]

---

### [YYYY-MM-DDTHH:MM:SS] — Session Recovery

**Action**: Session restarted, restoring context
**Details**:
- Last completed task: X.Y
- Next task: X.Z
- State verified from: current_state.md
- Context restored from: implementation_log.md

---

### [YYYY-MM-DDTHH:MM:SS] — Implementation Complete

**Action**: All tasks completed
**Summary**:
- Total tasks: X
- Duration: [start] → [end]
- Files changed: [count]
- Errors encountered: [count]
- Key decisions: [summary]
**IDE Artifacts Archived**: [list of files copied]
```
