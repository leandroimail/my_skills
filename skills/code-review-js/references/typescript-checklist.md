# TypeScript Review Checklist

## Table of Contents
- [TypeScript Standards](#typescript-standards)
- [Security](#security)
- [npm audit](#npm-audit)
- [Type Safety (tsc)](#type-safety-tsc)
- [Complexity (ESLint)](#complexity-eslint)
- [Dead Code (knip)](#dead-code-knip)
- [Async / Promises](#async--promises)
- [Error Handling](#error-handling)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Performance](#performance)
- [Design Principles (conditional)](#design-principles-conditional)

---

## TypeScript Standards

```
🔴 BLOCKER — all items below are mandatory for TS projects
```

### Strict Compiler

- [ ] `tsconfig.json` has `"strict": true` (implies `strictNullChecks`, `noImplicitAny`)
- [ ] New code passes `npx tsc --noEmit` with zero errors
- [ ] `noUncheckedIndexedAccess` recommended for new projects

### Import Order

1. Node built-ins (`node:path`, `node:fs`)
2. Third-party packages
3. Workspace aliases (`@myorg/*`)
4. Relative imports

Each group separated by **one blank line**. Enforce with `eslint-plugin-import`
(`import/order`) or the project's ESLint preset.

### Console Output — project logger only

- [ ] **Never** `console.log` in library or service code
- [ ] NestJS: `new Logger(ClassName.name)` from `@nestjs/common`
- [ ] Node services: pino or winston with structured fields
- [ ] `console` acceptable only in one-off scripts and CLI entry points
- [ ] New logs follow the project's logging pattern (logger, levels, structured fields, correlation IDs). Log at I/O boundaries and in every error path with the domain identifiers and the original exception; never secrets, tokens, personal data or whole payloads (🟡; a secret in a log is 🔴)

```typescript
// ✅ Correct (NestJS)
private readonly logger = new Logger(FaturaService.name);
this.logger.log(`Processed ${count} invoices in ${elapsed}ms`);

// ❌ Wrong
console.log('done');
```

### Exports and Modules

- [ ] Named exports for library code — no `export default` (breaks refactoring and grep)
- [ ] Barrel files (`index.ts`) only re-export the public surface, no logic
- [ ] No circular imports — restructure via dependency injection or extracting shared types

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes / Types / Interfaces / Enums | `PascalCase` | `FaturaService`, `CreateUserDto` |
| Functions / Variables | `camelCase` | `projectPath`, `runChecks()` |
| Constants | `UPPER_CASE` | `DEFAULT_PAGE_SIZE` |
| Private class members | `camelCase` (with `private`/`#`) | `private isInitialized` |
| React components / hooks | `PascalCase` / `useCamelCase` | `UserCard`, `useOrders` |
| Files | project convention (kebab-case common) | `fatura.service.ts`, `UserCard.tsx` |

---

## Security

```
🔴 BLOCKER — any single item here = merge blocked
```

- [ ] No template-literal SQL: `` `SELECT ... ${var}` `` → parameterized binds
- [ ] No `eval()` or `new Function()` on user-controlled input
- [ ] No `child_process.exec(interpolatedString)` — use `execFile` with an args array
- [ ] Secrets via `process.env` behind a validated config module — never hardcoded
- [ ] No `JSON.parse` of untrusted data straight into typed code — validate with zod/class-validator
- [ ] Path handling with `node:path` (`path.resolve`, prefix check) before file access (traversal risk)
- [ ] No `Math.random()` for tokens/ids with security meaning — `crypto.randomUUID()` / `crypto.randomBytes()`
- [ ] Regex on user input checked for catastrophic backtracking (ReDoS) — `eslint-plugin-security` `detect-unsafe-regex`
- [ ] Prototype pollution: no deep-merge of untrusted objects without key filtering (`__proto__`, `constructor`)
- [ ] `npm audit --audit-level=high` passes — see [npm audit](#npm-audit)

**Injection patterns to flag:**
```typescript
// 🔴 BLOCK: template literal
const rows = await dataSource.query(`SELECT * FROM orders WHERE user_id = ${userId}`);

// 🔴 BLOCK: string concatenation
const sql = "SELECT * FROM orders WHERE status = '" + status + "'";

// ✅ SAFE: positional binds (Oracle style)
const rows = await dataSource.query(
  'SELECT * FROM orders WHERE user_id = :1 AND status = :2',
  [userId, status],
);

// ✅ SAFE: query builder
const order = await repo
  .createQueryBuilder('o')
  .where('o.userId = :userId', { userId })
  .andWhere('o.status = :status', { status })
  .getOne();
```

---

## npm audit

Run: `npm audit --audit-level=high` (fails on high/critical advisories).

- [ ] Output is clean — no high/critical vulnerabilities
- [ ] If vulnerabilities found: `npm audit fix`, upgrade, or document risk with team approval
- [ ] Run in CI as a mandatory gate
- [ ] Lockfile committed and in sync (`npm ci` works)

```bash
npm audit --audit-level=high

# JSON report
npm audit --json > npm-audit-report.json
```

---

## Type Safety (tsc)

Run: `npx tsc --noEmit`

- [ ] All exported functions have explicit parameter and return types
- [ ] `X | null` / `X | undefined` modeled explicitly; handled with narrowing, not `!`
- [ ] No bare `any` — use `unknown` and narrow; document unavoidable `any` inline
- [ ] Non-null assertions (`!`) require a comment proving the invariant
- [ ] Type assertions (`as X`) justified — prefer type guards (`is X`) and discriminated unions
- [ ] `interface` or `type` for dicts with known shape — no `Record<string, any>`
- [ ] `readonly` on arrays/fields not meant to mutate
- [ ] Enums: prefer union of string literals (`type Status = 'open' | 'closed'`) over `enum`

**Boundary validation patterns:**
```typescript
// Good: external data always enters through a schema (frontend)
const userSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().int().positive(),
});
const user = userSchema.parse(await res.json());

// Good: NestJS DTO (backend)
export class CreateUserDto {
  @IsString() @MaxLength(100)
  name!: string;

  @IsEmail()
  email!: string;
}

// Bad: blind cast from the wire
const user = (await res.json()) as User;
```

---

## Complexity (ESLint)

Enable in the flat config:

```javascript
// eslint.config.mjs
import sonarjs from 'eslint-plugin-sonarjs';

export default [
  {
    plugins: { sonarjs },
    rules: {
      complexity: ['warn', 10],
      'sonarjs/cognitive-complexity': ['warn', 15],
      'max-depth': ['warn', 4],
      'max-lines-per-function': ['warn', { max: 50, skipBlankLines: true }],
    },
  },
];
```

| Metric | Threshold | Action |
|--------|-----------|--------|
| Cyclomatic ≤ 10 | OK | ✅ |
| Cyclomatic 11–15 | Complex | 🟡 Refactor or justify |
| Cyclomatic > 15 | Very complex | 🔴 Must refactor |
| Cognitive > 15 | Hard to follow | 🟡 Refactor or justify |

- [ ] No function above cyclomatic 15 (hard blocker)
- [ ] Prefer early returns to reduce nesting (flattens complexity)
- [ ] Extract predicates and branches into named functions

---

## Dead Code (knip)

Run: `npx knip`

- [ ] No unused exports introduced by the PR
- [ ] No unused dependencies added to `package.json`
- [ ] Unused files flagged by knip either removed or justified (entry points configured)
- [ ] Generated directories excluded in the knip config (`coverage/`,
  `reports/`, `dist/`) — otherwise coverage/mutation report artifacts show up
  as "unused files" and bury real findings

---

## Async / Promises

- [ ] No floating promises — `await`, `.catch()`, or `void` with a comment
  (`@typescript-eslint/no-floating-promises`)
- [ ] `Promise.all` for independent awaits — no sequential `await` chains for parallel work
- [ ] `Promise.allSettled` when partial failure is acceptable and handled
- [ ] No `async` executor in `new Promise(async ...)` (swallows rejections)
- [ ] `AbortController` / timeout on outbound HTTP calls
- [ ] No `await` inside loops for independent items — collect promises, then `Promise.all`

```typescript
// Bad: sequential — 3× latency
const a = await fetchA();
const b = await fetchB();
const c = await fetchC();

// Good: parallel
const [a, b, c] = await Promise.all([fetchA(), fetchB(), fetchC()]);
```

---

## Error Handling

- [ ] No empty `catch {}` — always log with stack or rethrow
- [ ] Catch narrows the error: `if (err instanceof DomainError)` — `err` is `unknown` in TS
- [ ] Log the error object (stack), not just `err.message`
- [ ] External calls (HTTP, DB, file I/O) wrapped with retry/backoff or an error boundary
- [ ] Custom errors extend a domain base class, not raw `Error`
- [ ] NestJS: domain exceptions map to HTTP status via an exception filter — controllers don't `try/catch` for shaping responses

```typescript
// Bad
try {
  result = await process(data);
} catch {}

// Good
try {
  result = await process(data);
} catch (err) {
  this.logger.error(`Processing failed for record ${recordId}`, err instanceof Error ? err.stack : String(err));
  throw err;
}
```

---

## Code Quality

- [ ] `eslint` and `prettier --check` pass without new suppressions
- [ ] No magic numbers — named constants or config values
- [ ] Functions < 50 lines; React components < 300 lines; extract helpers/hooks if longer
- [ ] No commented-out code in PR (use git for history)
- [ ] `// TODO: TICKET-123` format if deferring — not naked TODOs
- [ ] `eslint-disable` comments carry the specific rule and a reason
- [ ] Monorepo: module boundaries respected (`@nx/enforce-module-boundaries` passes);
  no deep relative imports across libs — use workspace aliases

---

## Testing

Naming convention: `describe('<unit>')` + `it('<scenario> <expected>')`

```typescript
// Good
describe('validateProjectName', () => {
  it('accepts a simple valid name', () => {
    expect(validateProjectName('myproject')).toBeNull();
  });

  it('rejects an empty name with a message', () => {
    expect(validateProjectName('')).toBe('Project name cannot be empty');
  });
});

// Bad (flat, undescriptive)
test('test1', () => {
  expect(validateProjectName('myproject')).toBeNull();
});
```

**Avoid test redundancy:**
- Generic/base behaviour tested **once** — shared behaviour of a base class or
  factory is not re-tested in every consumer suite
- Specific implementations test only their **unique** behaviour

- [ ] `describe` blocks group related tests per unit/feature
- [ ] Shared setup via `beforeEach` and factory helpers — no copy-paste setup blocks
- [ ] `test.each` (Jest) / `it.each` for equivalence classes:

```typescript
it.each([
  [{ uv: false, git: true }, ['uv']],
  [{ uv: true, git: false }, ['git']],
  [{ uv: false, git: false }, ['uv', 'git']],
])('detects missing prerequisites for %j', (prereqs, missing) => {
  const result = checkPrerequisites(prereqs);
  missing.forEach((tool) => expect(result).toContain(tool));
});
```

- [ ] No real `setTimeout` waits — `jest.useFakeTimers()` / `vi.useFakeTimers()` or `waitFor`
- [ ] Tests are deterministic: seed random data, fix dates (`jest.setSystemTime`)
- [ ] HTTP mocked at the network boundary (MSW) — not by mocking the fetch wrapper
- [ ] Coverage ≥ 80% for new code; 100% for critical paths (auth, billing, data access)
- [ ] Run via `npx jest` (or `npx vitest run`); Nx monorepo: `nx affected -t test`

---

## Performance

- [ ] No O(n²) lookups — build a `Map`/`Set` instead of `array.find` inside a loop
- [ ] Streams / pagination for large payloads — no loading full tables into memory
- [ ] Hot-path objects not re-created per call (regex literals, formatters, schemas hoisted)
- [ ] Node event loop not blocked: no sync fs/crypto/zlib in request handlers
  (`fs.readFileSync`, `pbkdf2Sync`) — use async variants or worker threads
- [ ] Memoize pure expensive computations (`useMemo` in React, module-level cache in Node)
- [ ] Profile before optimizing (`node --cpu-prof`, Chrome DevTools) — no premature work
- [ ] Bundle-sensitive frontend code avoids importing whole libraries for one function

---

## Design Principles (conditional)

Apply only when the change touches the situation described. Each is a review question, not a blanket rule.

- **Parse once at the boundary.** External data (HTTP bodies, files, env, DB rows) is parsed with a schema (zod, class-validator) into a typed value where it enters; inner code trusts the typed result. Re-validating deep inside is noise; skipping validation at the edge is a defect.
- **Business logic in pure functions.** If a function needs I/O to be tested, ask whether the decision can be separated from the I/O.
- **Re-run after a partial failure.** For jobs that write more than one thing, ask what state a crash halfway leaves, and whether running again ends in the same state.
- **Do not share mutable state you do not need.** If two actors do not need the same mutable object, give each its own copy or make the data immutable. If they do share it, ask who owns it and what guards concurrent writes (single owner, queue, lock), and whether the invariants hold under the concurrency model the code already uses.
