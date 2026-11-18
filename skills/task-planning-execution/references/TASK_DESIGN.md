# Task Design Guide

How to decompose a solution into effective, atomic tasks. This guide draws from
GSD's wave-based execution model, spec-kit's user-story-based decomposition,
and OpenSpec's lightweight tasking.

## Table of Contents

- [Decomposition Strategies](#decomposition-strategies)
- [Task Granularity](#task-granularity)
- [Dependency Management](#dependency-management)
- [Verification Design](#verification-design)
- [Complexity Estimation](#complexity-estimation)

## Decomposition Strategies

### Vertical Slice Decomposition (Preferred)

Decompose by feature slice, not by architectural layer. Each slice delivers
end-to-end functionality for one concern.

**Good** (vertical slices):

```
Task 1: RSI strategy — indicator calc + signal generation + backtest
Task 2: MACD strategy — indicator calc + signal generation + backtest
Task 3: Risk management module — position sizing + stop-loss logic
```

**Avoid** (horizontal layers):

```
Task 1: Create all strategy classes
Task 2: Create all indicator calculations
Task 3: Create all backtest runners
```

Why: Vertical slices are independently verifiable, produce working increments,
and allow parallel execution because they rarely touch the same files.

### Layer-Based Decomposition (Fallback)

Use when tasks are tightly coupled and vertical slicing would cause excessive
duplication. Follow this order:

```
1. Data models / schemas
2. Core logic / services
3. API / interface layer
4. Integration / wiring
5. Tests
6. Documentation
```

### Hybrid Decomposition

For large features, start with vertical slices for independent sub-features,
then use layer-based decomposition within each slice:

```
Feature: Strategy System Overhaul
├── Slice: RSI Strategy
│   ├── 1.1 RSI indicator calculation
│   ├── 1.2 RSI signal generation
│   └── 1.3 RSI backtest validation
├── Slice: Risk Management
│   ├── 2.1 Position sizing module
│   └── 2.2 Stop-loss / take-profit logic
└── Slice: Execution
    ├── 3.1 Order execution service
    └── 3.2 Live trading integration
```

## Task Granularity

### Right-Sized Tasks

A task is the right size when it:

- Can be described in 2-5 bullet points of actions.
- Touches 1-5 files.
- Has a single, clear verification criterion.
- Can be completed without context overflow.
- Has a self-contained `task_plan.md` and `task_design.md` in its folder.

### Too Large (Split)

Signs a task is too large:

- More than 5 files to modify.
- Multiple independent verification criteria.
- Description exceeds 10 bullet points.
- Contains "and" connecting unrelated actions.

### Too Small (Merge)

Signs tasks should be merged:

- Single one-line code change.
- Cannot be verified independently.
- Always executed together with another task.

## Dependency Management

### Declaring Dependencies

Use the `Depends on` field in each task to reference prerequisite tasks:

```markdown
### Task 2.1: Create risk management module
- **Depends on**: Task 1.1 (Strategy base class), Task 1.3 (Signal types)
```

### Dependency Rules

1. **No circular dependencies.** If A → B → A exists, merge into one task.
2. **Minimize cross-phase dependencies.** Each phase should deliver a
   standalone increment when possible.
3. **Mark parallel-safe tasks.** Tasks with no mutual dependencies and no
   shared file writes can be marked `[P]`.

### Wave Grouping

Tasks naturally group into execution waves based on dependencies:

```
Wave 1 (parallel):   Task 1.1 [P]  |  Task 1.2 [P]
Wave 2 (parallel):   Task 2.1 [P]  |  Task 2.2 [P]
Wave 3 (sequential): Task 3.1 (depends on 2.1 + 2.2)
```

Independent tasks in the same wave can be executed in any order or in parallel.

## Task Folder Contents

Each task folder (`tasks/X.Y_task-name/`) must contain:

### task_plan.md

Self-contained execution plan. Use the `task_plan.md` template from the
Document Templates entry in SKILL.md.

### task_design.md

Task-specific design context. Extract from global `design.md`:

- **Only relevant decisions**: Do not copy the entire global design.
- **Files involved**: List with their current state and role.
- **Constraints**: Patterns, conventions, and constraints that apply.
- **Approach**: How this task implements its part of the global solution.

The goal is for an agent to execute the task by reading **only** the
task folder, without needing to parse the global `design.md` or `tasks.md`.

## Verification Design

Every task must have verification criteria that answer: "How do I know this
task is done correctly?"

### Types of Verification

| Type | When to Use | Example |
|------|-------------|---------|
| **Build check** | Code must compile/transpile | "Project builds without errors" |
| **Test execution** | Automated tests exist | "All tests pass: `npm test` (JS/TS) / `uv run pytest` (Python)" |
| **Manual inspection** | UI or output check | "Login page renders correctly" |
| **Linting** | Code style compliance | "No lint errors: `npx eslint .` (JS/TS) / `ruff check src/` (Python)" |
| **Formatting** | Code style format | "Formatted: `npx prettier --check .` (JS/TS) / `ruff format src/` (Python)" |

> Command examples are stack-specific — always use the target project's own
> runner/linter (check `package.json` scripts or `pyproject.toml`).
| **Runtime check** | Feature works end-to-end | "API returns 200 on valid request" |

### Verification Rule

Each task must have at least one verification criterion from the list above.
Prefer automated verification (build/test/lint) over manual inspection.

### Done Criteria

The `Done` field describes the final observable state:

```markdown
- **Done**: RSI strategy generates buy/sell signals from OHLCV data,
  signals pass validation in backtest, and results are logged to
  the configured output.
```

## Complexity Estimation

Use T-shirt sizing for quick estimation:

| Size | Description | Files | Estimated Effort |
|------|-------------|-------|-----------------|
| **S** | Simple, well-understood change | 1-2 | < 5 minutes |
| **M** | Moderate change, some decisions | 2-4 | 5-15 minutes |
| **L** | Complex change, research needed | 4-8 | 15-30 minutes |
| **XL** | Very complex, should be split | 8+ | > 30 minutes — split it |

If a task is `XL`, decompose it further until all tasks are `S`, `M`, or `L`.
