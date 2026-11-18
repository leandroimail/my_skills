# Context Management

Strategies for preserving context, preventing context rot, and managing memory
across long sessions and session restarts. These patterns are derived from GSD's
durable context engineering, Addy Osmani's hierarchical summarization, and
Anthropic's effective context engineering guidelines.

## Table of Contents

- [Core Problem: Context Rot](#core-problem-context-rot)
- [Durable Context Engineering](#durable-context-engineering)
- [Hierarchical Context Strategy](#hierarchical-context-strategy)
- [Session Management](#session-management)
- [Context Budget Per Task](#context-budget-per-task)
- [State Recovery Protocol](#state-recovery-protocol)

## Core Problem: Context Rot

Context rot is the quality degradation that occurs as an AI agent fills its
context window with accumulated discussion, partial decisions, outdated intent,
and debugging noise. Early in a session, the agent has clear focus; by task 15+,
the agent may forget requirements, make inconsistent decisions, or repeat
mistakes.

**Symptoms of context rot:**

- Agent becomes "more concise" (truncating detail).
- Agent forgets earlier requirements or decisions.
- Code quality decreases on later tasks.
- Agent makes contradictory decisions.
- Agent asks about things already discussed.

**Root cause:** The context window is finite. As it fills with chat history,
the useful signal gets buried under noise.

## Durable Context Engineering

The solution is to externalize state into files and reload only what's needed.

### Principle 1: State Lives in Files

Every important piece of information must be persisted to the plan directory:

| Information Type | File | Why |
|-----------------|------|-----|
| What to build (global) | `design.md` | Architectural reference |
| Task index | `tasks.md` | Master index with links to task folders |
| Task execution plan | `tasks/X.Y/task_plan.md` | Self-contained task instructions |
| Task design context | `tasks/X.Y/task_design.md` | Task-specific design subset |
| Where we are | `current_state.md` | Position tracking |
| What happened | `implementation_log.md` | Decision and action history |

**Rule:** If a decision or action is not written to a file, it does not exist
for future tasks.

### Principle 2: Append, Never Overwrite

State and log files are append-only:

- New entries go at the bottom with timestamps.
- Previous entries are never modified or deleted.
- This creates a complete audit trail.
- On restart, the latest entry tells you the current state.

### Principle 3: Scope Context Per Task

Load only the context relevant to the current task:

```
Per-task context budget:
├── MUST READ:  task_plan.md (from task folder)
├── MUST READ:  task_design.md (from task folder)
├── MUST READ:  Latest state entry from current_state.md
├── MAY READ:   Global design.md (if beyond task_design.md)
└── DO NOT READ: Other tasks' folders, entire log history
```

### Principle 4: Timestamp Everything

Every file entry includes an ISO 8601 timestamp (`YYYY-MM-DDTHH:MM:SS`).
This enables:

- Chronological ordering on restart.
- Duration tracking for performance analysis.
- Conflict resolution between entries.

### Principle 5: Fresh Context Per Major Unit

Inspired by GSD's wave execution: each major unit of work (task) should
operate with a "fresh" context loaded from file artifacts, not from
accumulated chat history.

In practice, this means:

- Re-read plan files from disk at the start of each task.
- Do not rely on in-memory state from prior tasks.
- Treat each task as if it were the first task in the session.

## Hierarchical Context Strategy

For complex projects, use a layered approach to context:

```
Level 1: Always Loaded (from task folder)
├── task_plan.md (self-contained execution plan)
├── task_design.md (task-specific design context)
└── Current state (from current_state.md, latest entry)

Level 2: Plan-Relevant (loaded if task_design.md insufficient)
├── Global design.md decisions
├── Dependency task results (from dependent task's task_plan.md)
└── Relevant code files

Level 3: On-Demand (loaded only when needed)
├── Full implementation_log.md history
├── Other tasks' folders
└── Prior plan directories
```

This mirrors the progressive disclosure pattern: lightweight overview always
present, details loaded only when the task requires them.

## Session Management

### Starting a New Session

When a new session begins for an active plan:

1. Read `current_state.md` — latest entry tells you where you are.
2. Read `tasks.md` — find the next incomplete task.
3. Read `implementation_log.md` — last 2-3 entries for recent context.
4. Resume from the next incomplete task.
5. Log the session start in `implementation_log.md`.

### Pausing Mid-Session

When the user pauses or the session may end:

1. Ensure all current progress is logged.
2. Write a state entry with:
   - Current task in progress (if any).
   - What has been completed in the current task.
   - What remains to be done.
3. This entry becomes the recovery point.

### Handoff Between Sessions

The plan directory serves as the complete handoff:

```
A new agent instance can resume work by reading:
1. current_state.md → "Where am I?"
2. tasks.md → "What task is next?" (master index)
3. tasks/X.Y_task-name/task_plan.md → "What do I need to do?"
4. tasks/X.Y_task-name/task_design.md → "What context do I need?"
```

No chat history is needed. All state is in the files.

## Context Budget Per Task

### Token Budget Guidance

Keep the context loaded per task lean:

| Content | Estimated Tokens | Priority |
|---------|-----------------|----------|
| `task_plan.md` (from task folder) | ~300 | Critical |
| `task_design.md` (from task folder) | ~400 | Critical |
| Latest state entry | ~100 | Critical |
| Total per-task budget | ~800 | Target |

This leaves the vast majority of the context window available for the actual
code implementation work.

### What NOT to Load

- Full text of completed tasks.
- Historical log entries unrelated to the current task.
- Design alternatives that were rejected.
- Error histories from resolved issues.
- Chat transcript excerpts.

## State Recovery Protocol

When recovering from a crash, interruption, or new session:

### Step 1: Assess Current Position

```
Read: current_state.md
Extract: Latest entry → current phase, status, next task
```

### Step 2: Verify Consistency

```
Read: tasks.md
Check: Are completed tasks marked as done?
Check: Does the next task from state match the next unmarked task?
```

### Step 3: Load Recent Context

```
Read: implementation_log.md (last 3 entries)
Extract: Recent decisions, any pending issues
```

### Step 4: Verify File System

```
Check: Do the files mentioned in completed tasks actually exist?
Check: Do they contain the expected changes?
```

### Step 5: Resume or Reconcile

If everything is consistent:

- Log the recovery in `implementation_log.md`.
- Resume from the next incomplete task.

If inconsistency found:

- Log the discrepancy.
- Investigate the actual file system state.
- Update `current_state.md` to reflect reality.
- Proceed from the corrected state.
