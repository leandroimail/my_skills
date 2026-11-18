---
name: code-review-js
description: >
  Performs rigorous, domain-specific code reviews for TypeScript/JavaScript,
  React/Next.js, NestJS, and SQL data access. Use when reviewing pull requests,
  auditing query safety, checking API or frontend code, evaluating type
  coverage, evaluating mutation testing coverage (StrykerJS), or identifying
  performance and security issues in TS/JS stacks. Use whenever TS/JS, React,
  NestJS or SQL access changes need a review, even if the user does not name
  this skill ("revisar PR", "code review"). Do NOT use for Python, Java, or
  infrastructure-only changes.
compatibility: >
  Requires Node.js 20+, eslint 9 (flat config), prettier, typescript (tsc),
  npm audit. Optional: eslint-plugin-security, eslint-plugin-sonarjs, knip,
  sqruff, @stryker-mutator/core for mutation testing gate.
allowed-tools: [Read, Grep, Glob, Bash]
metadata:
  tags: [code-review, typescript, javascript, react, nextjs, nestjs, sql, eslint, prettier, tsc, knip, sqruff, jest, stryker]
---

# Code Review — TypeScript · React · NestJS · SQL

## Purpose

Domain-focused review for TypeScript/JavaScript, React/Next.js frontends,
NestJS backends, and SQL data access. Integrates quality, security,
performance, and correctness lenses with fast tooling.

## When To Use

- Reviewing PRs with `.ts`, `.tsx`, `.js`, `.jsx`, `.sql` files
- Auditing NestJS services, controllers, and TypeORM/Prisma data access
- Checking query safety and performance (parameterized binds, N+1)
- Validating type coverage and test quality
- Security audits on API and data access layers

## When Not To Use

- Python, Java, Go, or infra-only changes are out of scope for this skill
- Receiving review feedback → use `receiving-code-review-js`

## Inputs

Collect before starting:

- Scope: file(s) or PR diff
- Context: What does this change do? (feat / bugfix / refactor / migration)
- Stack: Which frameworks? (React / Next.js / NestJS / Express / TypeORM / Prisma / etc.)
- Environment: Node version (20+), DB engine (Oracle / Postgres / MySQL / etc.), monorepo tool (Nx / Turborepo / none)

---

## Method

### Stage 1 — Context Pass (fast)

Run in under 2 minutes to frame the review:

```bash
# Count changed lines and file types
git diff --stat HEAD~1

# Spot hardcoded secrets / credentials (immediate blocker)
grep -rn "password\s*[:=]\s*['\"]" --include="*.ts" --include="*.tsx" src/ apps/ libs/
grep -rn "apiKey\s*[:=]\s*['\"]\|secret\s*[:=]\s*['\"]" --include="*.ts" src/ apps/ libs/
grep -rnE '`(SELECT|INSERT|UPDATE|DELETE)[^`]*\$\{' --include="*.ts" src/ apps/ libs/  # SQL injection via template literal
```

Classify the change before deep review:
- 🔴 **Blocker present** → report immediately, do not continue review
- 🟡 **Needs inspection** → continue with staged review
- 🟢 **Safe to review fully** → proceed

### Stage 2 — Static Analysis Pass (automated)

Run toolchain before manual review. Prioritize fixing tool errors over style
comments. In an Nx monorepo, prefer `nx affected -t lint,test,typecheck` to
scope to changed projects.

```bash
# Lint + format
npx eslint .
npx prettier --check .

# Type checking — the primary correctness gate for TS
npx tsc --noEmit

# Security lint (unsafe regex, eval, child_process injection patterns)
# requires eslint-plugin-security in the flat config
npx eslint . --rule '{"security/detect-eval-with-expression": "error"}' 2>/dev/null || npx eslint .

# Dependency vulnerabilities
npm audit --audit-level=high

# Dead code: unused exports, files, and dependencies
npx knip

# Cyclomatic/cognitive complexity (via ESLint rules — see typescript-checklist)
# eslint rule: complexity (target ≤ 10), sonarjs/cognitive-complexity (target ≤ 15)

# SQL linting for standalone .sql files (built in Rust, fast)
# not on npm — per-OS install: see references/sqruff-install.md
sqruff lint --dialect ansi migrations/ queries/

# Test execution with coverage
npx jest --coverage
# Vitest projects: npx vitest run --coverage
```

Tool failure = **🔴 Blocker** unless agreed to defer.

Optional advisory gates (CRAP and structural duplication) are in
[references/quality-gates.md](references/quality-gates.md). Their absence or
failure is **not** a Blocker: report "metric unavailable" and continue.
To install the tools (Linux, macOS, Windows), see
[Installing the tools](references/quality-gates.md#installing-the-tools).

### Stage 3 — TypeScript Deep Review

Check in this order (stop at first 🔴 and report):

**TypeScript Code Standards (🔴 Blocker if violated):**
- [ ] `strict: true` in tsconfig; new code compiles under `tsc --noEmit`
- [ ] No `console.log` in library/service code → use the project logger
  (NestJS `Logger`, pino, winston); `console` acceptable only in scripts/CLIs
- [ ] No `any` without documented justification — prefer `unknown` + narrowing
- [ ] ES modules and named exports; no `default export` for library code
- See full checklist → [references/typescript-checklist.md](references/typescript-checklist.md#typescript-standards)

**Security (highest priority):**
- [ ] No template-literal SQL: `` `SELECT ... ${var}` `` → must use parameterized binds
- [ ] No `eval()`, `new Function()`, or `child_process.exec()` with interpolated input
- [ ] No secrets hardcoded; use `process.env` via a validated config layer
- [ ] External input validated at the boundary (zod / class-validator) — never trusted raw
- [ ] `npm audit --audit-level=high` passes — no known vulnerable dependencies
- See full checklist → [references/typescript-checklist.md](references/typescript-checklist.md#security)

**Type Safety:**
- [ ] All exported functions have explicit parameter and return types
- [ ] `X | null` / `X | undefined` modeled explicitly — no implicit nullability
- [ ] No non-null assertions (`!`) without a comment proving the invariant
- [ ] External data (API, file, DB row) enters through a schema: zod `.parse()`
  on the frontend, class-validator DTOs in NestJS — no raw `as` casts
- [ ] Type assertions (`as`) justified; prefer type guards and discriminated unions

**Complexity:**
- [ ] Cyclomatic complexity ≤ 10 per function (ESLint `complexity` rule)
- [ ] Cognitive complexity ≤ 15 (eslint-plugin-sonarjs) — refactor or documented exception
- [ ] Functions < 50 lines; components < 300 lines; extract helpers/hooks if longer

**React / Next.js (frontend changes):**
- [ ] Hooks rules pass (`eslint-plugin-react-hooks`); exhaustive deps not silenced
- [ ] Server/client component boundary intentional (`'use client'` only where needed)
- [ ] Server state via a query library (TanStack Query) — not `useEffect` + `useState` fetching
- [ ] Forms validate with a schema resolver (react-hook-form + zod)
- [ ] Accessibility: interactive elements reachable by role/label; errors use `role="alert"`
- See full checklist → [references/react-checklist.md](references/react-checklist.md)

**NestJS (backend changes):**
- [ ] DTOs with class-validator on every mutating endpoint; global `ValidationPipe`
  with `whitelist` + `forbidNonWhitelisted` + `transform`
- [ ] Providers injected via constructor DI — no `new Service()` in business code
- [ ] Guards/interceptors/filters registered intentionally (global vs per-route)
- [ ] No business logic in controllers — delegate to services
- See full checklist → [references/nestjs-checklist.md](references/nestjs-checklist.md)

**Error Handling:**
- [ ] No empty `catch {}` — log with stack or rethrow a domain error
- [ ] New logs follow the project's logging pattern (logger, levels, structured fields, correlation IDs). Log at I/O boundaries and in every error path with the domain identifiers and the original error; never secrets, tokens, personal data or whole payloads (🟡; a secret in a log is 🔴)
- [ ] Promises always awaited or explicitly handled (`no-floating-promises`)
- [ ] Async resources cleaned up (`finally`, `AbortController`, connection release)
- [ ] Domain exceptions extend a base class and map to HTTP status via a filter

**Testing:**
- [ ] Descriptive names: `it('<unit> <scenario> <expected>')` grouped in `describe` blocks
- [ ] Tests co-located per module (e.g. `__tests__/` next to the code) following project convention
- [ ] Shared setup via helpers/factories; `test.each` for equivalence classes
- [ ] Mock external I/O at the boundary (MSW for HTTP, repository mocks for DB); no real network calls
- [ ] No arbitrary `setTimeout` waits in tests — use fake timers or `waitFor`
- [ ] Coverage ≥ 80% on new code (critical paths = 100%)
- [ ] **Mutation testing (StrykerJS):** run on new/changed modules; score ≥ 30% minimum gate
- [ ] Surviving mutants on comparison operators or return values flagged individually
- See full patterns → [references/typescript-checklist.md](references/typescript-checklist.md#testing)
- See mutation testing guide → [references/mutation-testing.md](references/mutation-testing.md)

### Stage 4 — SQL Deep Review

> Tool first: `sqruff lint` must pass for standalone `.sql` files before manual
> review. Not installed? See [references/sqruff-install.md](references/sqruff-install.md)
> (Linux / Windows / macOS).

**Security (🔴 Blocker):**
- [ ] No template-literal / string-concatenated SQL in TS → always parameterized binds
  (`dataSource.query(sql, [params])`, TypeORM `:named` params, Prisma tagged templates)
- [ ] ORM or query builder for dynamic filters; raw SQL only where the ORM cannot express it
- [ ] Identifiers (table/column names) never come from user input — allowlist only

**Correctness:**
- [ ] No accidental Cartesian joins (missing `ON` clause)
- [ ] `NULL` handling: `IS NULL` not `= NULL`; `COALESCE`/`NVL` for defaults
- [ ] Window functions preferred over correlated subqueries
- [ ] CTEs for readability when query has > 2 joins
- [ ] `DISTINCT` usage justified — usually signals a missing join condition
- [ ] Date binds passed as dates or converted explicitly (`TO_DATE(:1, 'YYYY-MM-DD')` in Oracle)

**Performance:**
- [ ] No `SELECT *` in production code — enumerate columns
- [ ] `WHERE` filters leverage indexed columns (check EXPLAIN)
- [ ] Avoid functions on indexed columns in `WHERE`: `WHERE TRUNC(date_col)=...` →
  range predicate `WHERE date_col >= :1 AND date_col < :2`
- [ ] Pagination: keyset/cursor-based preferred over `OFFSET` for large tables
- [ ] ORM N+1: relations loaded eagerly where iterated (`relations`, `leftJoinAndSelect`)
- See full checklist → [references/sql-checklist.md](references/sql-checklist.md)

### Stage 5 — API / Data Layer Review

> Apply when change touches REST endpoints, migrations, or batch data access.

**Contract Safety (🔴 Blocker if broken):**
- [ ] Response shape changes are backward compatible or versioned (`/v1` vs `/v2`)
- [ ] DTO field removals/renames done in two-phase deploy (add new → migrate consumers → drop old)
- [ ] OpenAPI/Swagger annotations match the actual DTOs

**Schema Safety (migrations):**
- [ ] New columns are nullable or have `DEFAULT` (no breaking migration)
- [ ] Column renames done in two-phase deploy
- [ ] `up` and `down` migrations both present and tested

**Resilience:**
- [ ] Retry with exponential backoff for transient failures (HTTP 5xx, DB timeouts)
- [ ] Timeouts set on outbound HTTP and DB calls — no unbounded awaits
- [ ] Rate limiting on public endpoints (e.g. `@nestjs/throttler`)

**Observability:**
- [ ] Request logging with correlation/trace IDs; PII masked in logs
- [ ] Errors logged with stack; row counts / durations logged for batch operations

---

## Severity Rating

| Symbol | Level | Action |
|--------|-------|--------|
| 🔴 | **Critical** | Block merge. Fix before next stage. Security, data loss, broken functionality |
| 🟡 | **Important** | Fix in this PR. Performance, type safety, missing tests |
| 🟢 | **Suggestion** | Optional or follow-up ticket. Style, minor refactors |

Advisory metrics (CRAP, duplication scores) are candidates, not findings. They
start as 🟢. Raise them to 🟡 only after you confirm a concrete problem, and to
🔴 only for a confirmed security, data-loss, or broken-behavior defect.

---

## Feedback Format

Write findings as: `[SEVERITY] File:line — Issue → Suggested fix`

```
🔴 src/services/fatura.service.ts:42 — template-literal SQL injection risk
   const rows = await ds.query(`SELECT * FROM fatura WHERE id = ${userId}`)
   → Use parameterized: ds.query('SELECT * FROM fatura WHERE id = :1', [userId])

🟡 src/hooks/use-orders.ts:87 — data fetching via useEffect + useState
   → Move to TanStack Query: useQuery({ queryKey: orderKeys.list(), queryFn: fetchOrders })

🟢 queries/users.sql:12 — SELECT * in analytics query
   → Enumerate columns for clarity and resilience to schema changes
```

Never write: "Great code!" / "Nice work!" / "You're right!" — only technical
observations and concrete fixes. See `receiving-code-review-js` for the complementary
perspective when you are on the receiving end.

---

## Quality Checklist (final gate)

Before marking review complete:

- [ ] `eslint` + `prettier --check` pass
- [ ] `tsc --noEmit` passes with `strict: true`
- [ ] `npm audit --audit-level=high` — no known vulnerable dependencies
- [ ] `knip` — no unused exports/dependencies introduced
- [ ] ESLint `complexity` / sonarjs — no functions above threshold without justification
- [ ] `sqruff lint` passes for standalone SQL files
- [ ] `jest --coverage` (or `vitest run --coverage`) passes with ≥ 80% on new code
- [ ] `npx stryker run` — mutation score ≥ 30% on new/changed modules
- [ ] No 🔴 Critical findings remain open
- [ ] All SQL queries parameterized
- [ ] No `any` or non-null assertions without justification
- [ ] Project logger used — no `console.log` in library/service code
- [ ] External input validated at the boundary (zod / class-validator)
- [ ] Breaking API/schema changes have a two-phase deploy plan
- [ ] No secrets or hardcoded credentials
- [ ] New tests call the code as its user does and assert the observable result (flag tests with no assertion on the behavior they name, unless "does not raise" is the contract; a "does nothing" test needs a paired positive case)
- [ ] Feedback is specific, actionable, and non-performative

## Outputs

A severity-ranked finding list structured as:

```
## Review Summary
- 🔴 Critical: N
- 🟡 Important: N
- 🟢 Suggestions: N

## Findings
[numbered list following Feedback Format above]

## Merge Decision
BLOCK / APPROVE WITH FIXES / APPROVE
```
