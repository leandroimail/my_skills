---
name: writing-tests-js
description: >
  Designs, structures, and implements Jest/Vitest test suites for
  TypeScript/JavaScript projects (React, Next.js, NestJS, Node). Handles test
  data factories, MSW network mocks, NestJS TestingModule and repository mocks,
  React Testing Library setup, and async testing. Use when creating tests,
  writing unit or integration tests, setting up test infrastructure, designing
  factories and fixtures, organizing mocks, or configuring test setup files.
  Also handles mutation testing with StrykerJS: running Stryker, improving weak
  tests, killing surviving mutants. Use whenever the user mentions testing,
  test coverage, Jest, Vitest, Testing Library, MSW, supertest, mutation
  testing, or test quality, even if not explicit.
compatibility: >
  Requires Node.js 20+, Jest >=29 (examples use Jest 30 syntax) or Vitest >=3
  (equivalence notes provided). Optional: @testing-library/react,
  @testing-library/user-event, msw, supertest, @nestjs/testing, fast-check,
  @stryker-mutator/core. Run tests via `npx jest` / `npx vitest run`
  (or `nx affected -t test` in Nx monorepos).
metadata:
  author: generic
  version: "2.1"
---

# Writing TypeScript/JavaScript Tests

## Purpose

Enforces a production-grade testing workflow for TypeScript/JavaScript
projects. Tests follow strict placement conventions with data factories,
network-boundary mocks (MSW), and framework-aware harnesses (Testing Library
for React, TestingModule for NestJS). The patterns below are domain-neutral:
substitute the generic placeholders (records, the pricing service, the REST
API client) with your project's actual modules.

**Runner note:** Examples use **Jest** syntax. Vitest is API-compatible for
almost everything shown — see the [equivalence table](#jest--vitest-equivalence)
and swap `jest.*` for `vi.*`.

## When To Use

- Creating or extending test suites for any module
- Setting up test infrastructure for new libs/apps in a monorepo
- Designing factories for API payloads, entities, or DTOs
- Organizing mocks for external APIs (MSW), repositories, or framework modules
- Configuring setup files (`test-setup.ts`) and coverage thresholds
- Testing React components and hooks (Testing Library)
- Testing NestJS services, controllers, and e2e endpoints (TestingModule, supertest)
- Testing async client code against external APIs
- Running mutation testing with StrykerJS and improving test quality
- Killing surviving mutants by strengthening assertions or adding boundary tests

## When Not To Use

- Non-JS/TS projects
- Performance/load testing (use k6 or Artillery)
- Cross-browser E2E suites (use Playwright directly — though component-level
  interaction tests belong here)
- Static analysis or linting (use eslint, tsc)

## Inputs

Before writing tests, collect from the user or infer from context:

1. **Source module** — which lib/app module is being tested
2. **Test scope** — unit, integration, e2e, or combination
3. **Data dependencies** — external APIs, DB repositories, config, framework context (Router, QueryClient)
4. **Coverage target** — default ≥70% overall, 100% for critical/business-logic modules
5. **Runner** — Jest or Vitest (check existing config before adding either)

## Directory Structure (Mandatory)

Tests are **co-located with the module they test**, grouped in a `__tests__/`
directory beside the source, with mocks and factories in a sibling `mocks/`
directory. This keeps each feature lib self-contained.

```
libs/my-feature/src/lib/
├── components/
│   └── RecordForm.tsx
├── hooks/
│   ├── query-keys.ts              # Hierarchical query keys (single source)
│   └── use-records.ts
├── services/
│   └── record.service.ts
├── mocks/                         # Factories + MSW handlers live here
│   ├── index.ts                   # Barrel: exports factories + handlers
│   ├── factories.ts               # buildX(overrides) data factories
│   ├── fixtures.ts                # Static payload constants
│   └── handlers.ts                # MSW request handlers
└── __tests__/                     # All tests for this lib
    ├── test-utils.tsx             # createWrapper() and shared harness helpers
    ├── RecordForm.test.tsx        # Component tests
    ├── use-records.test.ts        # Hook tests
    └── record.service.test.ts     # Service/unit tests
```

For a NestJS app, the same principle per module (spec naming follows the
project convention — `*.spec.ts` is the Nest default):

```
apps/api/src/modules/records/
├── dtos/
├── entities/
├── records.controller.ts
├── records.service.ts
└── __tests__/
    └── records.service.spec.ts
apps/api/test/
└── records.e2e-spec.ts            # supertest e2e against the HTTP server
```

**Why co-located?** When `use-records.test.ts` fails, you know the issue is in
this lib. Nx/Turborepo can then run only affected projects
(`nx affected -t test`).

## Method

### Before Step 1: Settle the Seams

A seam is the public boundary where a test observes behavior without reaching
inside: the subject, its entry point, the outputs the test may observe, and the
dependencies it may replace. Settle the seams before you create any test
infrastructure.

- A seam the user named in the request ("add a regression test for
  `normalizeRecords`") or approved in an earlier plan is settled. Do not ask again.
- When the choice is open and the user can answer, list the proposed seams with
  one line each on what it catches and what it misses, and ask once.
- When the user cannot be asked (an unattended run), choose the seams yourself
  and state them, with the same one-line notes, in the final report.

### Step 1: Create the Directory Skeleton

Create `__tests__/` and `mocks/` inside the target lib/module. Match the
project's existing naming convention (`*.test.ts` vs `*.spec.ts`) — check
before inventing one.

### Step 2: Write Data Factories in `mocks/factories.ts`

Factories build fully-typed objects with sensible defaults and partial
overrides. Every factory **must**:

1. Return a complete, valid object of the declared type
2. Accept `overrides: Partial<T> = {}` spread last
3. Be deterministic (fixed dates/ids — no `Math.random()` without a seed)

```typescript
// libs/my-feature/src/lib/mocks/factories.ts
import type { RecordDto, RecordPage } from '../types';

export function buildRecord(overrides: Partial<RecordDto> = {}): RecordDto {
  return {
    id: 1,
    timestamp: '2026-01-01T00:00:00Z',
    value: 42.5,
    category: 'A',
    ...overrides,
  };
}

export function buildRecordPage(overrides: Partial<RecordPage> = {}): RecordPage {
  return {
    status: 'ok',
    page: 1,
    records: [buildRecord(), buildRecord({ id: 2, category: 'B' })],
    ...overrides,
  };
}
```

> **For detailed factory and fixture patterns** (entity factories, seeded
> lists, temp files, config): See [fixture-patterns.md](references/fixture-patterns.md)

### Step 3: Mock the Network Boundary with MSW in `mocks/handlers.ts`

Mock HTTP at the network boundary — not by mocking your api-client module.
Handlers are centralized per lib and reused by tests and (optionally) by a
browser mock mode.

```typescript
// libs/my-feature/src/lib/mocks/handlers.ts
import { http, HttpResponse, delay } from 'msw';
import { buildRecordPage } from './factories';

const BASE = '/api/records';

export const recordHandlers = [
  http.get(`${BASE}`, async () => {
    await delay(50);
    return HttpResponse.json(buildRecordPage());
  }),
  http.post(`${BASE}`, async ({ request }) => {
    const body = (await request.json()) as { value: number };
    if (body.value < 0) {
      return HttpResponse.json({ code: '001', message: 'invalid' }, { status: 422 });
    }
    return HttpResponse.json(buildRecordPage(), { status: 201 });
  }),
];
```

In tests, boot a server per file and override per test:

```typescript
import { setupServer } from 'msw/node';
import { recordHandlers } from '../mocks/handlers';

const server = setupServer(...recordHandlers);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// per-test override
server.use(http.get('/api/records', () => HttpResponse.json(buildRecordPage({ records: [] }))));
```

> **For mock patterns** (repository mocks, QueryBuilder chains, module mocks,
> spies): See [mock-patterns.md](references/mock-patterns.md)

### Step 4: Build the Test Harness in `__tests__/test-utils.tsx`

Shared harness helpers live once per lib — provider wrappers, render helpers,
store resets. Example for a React lib using TanStack Query:

```tsx
// libs/my-feature/src/lib/__tests__/test-utils.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';

export function createWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}
```

The runner-level setup file (`test-setup.ts`, registered via `setupFiles`)
holds only environment shims and matcher registration:

```typescript
// test-setup.ts
import '@testing-library/jest-dom';

// JSDOM lacks these browser APIs
class ResizeObserverStub { observe() {} unobserve() {} disconnect() {} }
globalThis.ResizeObserver ??= ResizeObserverStub as never;
window.matchMedia ??= ((q: string) =>
  ({ matches: false, media: q, addEventListener() {}, removeEventListener() {} })) as never;
```

### Step 5: Write Tests Following AAA + TDD

Every test follows the **Arrange → Act → Assert** pattern inside a
**TDD cycle** (Red → Green → Refactor).

In the Red step, run the test and confirm it fails for the expected reason (the
assertion about the behavior, not an import error or a typo) before you write
the code. If an honest test is impractical, state the alternative verification
instead of writing a weak test.

A test for behavior that already exists (a characterization test, or one that
kills a surviving mutant in Step 8) has no Green step: it passes at once. Prove
that it is sensitive by breaking the code temporarily, or by checking that the
mutant dies.

Avoid these three anti-patterns:

- **Implementation-coupled**: the test replaces a collaborator that sits inside
  the seam, calls non-public methods, or reads state that is not an output of the seam.
  For a UI test that means the database or the store; for a repository or
  store test that state is the output, and asserting on it is correct.
  Test doubles belong at the system boundaries: network, database, clock,
  filesystem, environment. Assert on a call to a double only when that outgoing
  call is the behavior under test. The tell: the test breaks on a refactor that
  did not change behavior.
- **Tautological**: the expected value is produced by copying the production
  algorithm into the test, so both share the same bug; or the test asserts on
  what a mock was configured to return without running the real subject. Derive
  expected values independently: a known-good literal, a worked example, the
  spec. Properties taken from the spec (idempotence, round-trip, invariants)
  are valid.
- **Horizontal slicing**: when building new or changed behavior, writing all
  tests first and then all the implementation. Work in vertical slices instead:
  one behavior (a parametrized set counts as one), Red, minimal Green, Refactor,
  repeat, so each test responds to what the previous cycle taught you.

```tsx
// libs/my-feature/src/lib/__tests__/RecordForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RecordForm } from '../components/RecordForm';

describe('<RecordForm />', () => {
  it('submits a valid payload and shows the success state', async () => {
    // Arrange
    const user = userEvent.setup();
    render(<RecordForm />);
    // Act
    await user.type(screen.getByLabelText(/value/i), '42.5');
    await user.click(screen.getByRole('button', { name: /save/i }));
    // Assert
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent(/saved/i));
  });

  it('announces validation errors with role=alert', async () => {
    const user = userEvent.setup();
    render(<RecordForm />);
    await user.click(screen.getByRole('button', { name: /save/i }));
    const alerts = await screen.findAllByRole('alert');
    expect(alerts[0]).toHaveTextContent(/required/i);
  });
});
```

Use `test.each` for equivalence classes:

```typescript
describe('normalizeRecords', () => {
  it.each([
    ['time', 'timestamp'],
    ['date', 'timestamp'],
    ['created_at', 'created_at'],
  ])('renames column %s to %s', (input, expected) => {
    const result = normalizeRecords([{ [input]: '2026-01-01' }]);
    expect(result[0]).toHaveProperty(expected);
  });
});
```

### Step 6: Configure the Runner and Coverage

**Jest (per app/lib in a monorepo, extending a shared preset):**

```javascript
// apps/api/jest.config.js
module.exports = {
  ...require('../../jest.preset'),
  displayName: 'api',
  rootDir: 'src',
  testRegex: '.*\\.spec\\.ts$',
  collectCoverageFrom: ['**/*.ts', '!**/index.ts', '!main.ts', '!**/mocks/**'],
  coverageThreshold: {
    global: { statements: 80, branches: 70, functions: 80, lines: 80 },
  },
};
```

**Vitest (per lib):**

```typescript
// vite.config.mts — test block
test: {
  name: 'my-feature',
  environment: 'jsdom',
  setupFiles: ['src/test-setup.ts'],
  include: ['src/**/*.{test,spec}.{ts,tsx}'],
  coverage: {
    provider: 'v8',
    include: ['src/lib/**/*.{ts,tsx}'],
    exclude: ['src/lib/**/__tests__/**', 'src/lib/mocks/**', 'src/lib/**/index.ts',
              'src/lib/**/*.stories.tsx'],
    thresholds: { statements: 80, branches: 80, functions: 80, lines: 70 },
  },
},
```

Always exclude `__tests__/`, `mocks/`, barrels (`index.ts`), stories, and
route wrappers covered by E2E from coverage.

### Step 7: Verify and Iterate

Run the validation checklist below. Fix any failures. Re-run until all pass.

```bash
npx jest --coverage
# Vitest: npx vitest run --coverage
# Nx monorepo: nx affected -t test
```

### Step 8: Run Mutation Testing with StrykerJS

After achieving ≥80% line coverage, validate that tests actually enforce
behavior — not just execution. Start with the highest-priority modules
(business services, pricing/validation logic).

```bash
# Install if not already present
npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner

# Run mutation testing on a specific module
npx stryker run --mutate "src/lib/services/record.service.ts"

# Inspect surviving mutants in the HTML report
# open reports/mutation/mutation.html with your browser: xdg-open (Linux), open (macOS), start (Windows)

# Incremental re-runs while strengthening tests
npx stryker run --incremental
```

Work in this order: cover uncovered lines first, then kill survivors. For each
surviving mutant: identify the missing assertion (boundary, exact value, or
inverse case), add it to the test, and re-run. If the mutant is equivalent,
justify it with the exact behavior. A survivor can also point to dead code:
report it, and remove it only when the removal is in scope. Target 80%+ mutation
score on critical modules with 100% coverage targets.

> **Full guide**: [mutation-testing.md](references/mutation-testing.md) — covers
> configuration, mutation types, TypeScript examples, and workflow.

## Jest ↔ Vitest Equivalence

| Jest | Vitest | Notes |
|------|--------|-------|
| `jest.fn()` | `vi.fn()` | identical API |
| `jest.mock('./mod')` | `vi.mock('./mod')` | Vitest hoists too; factory arg supported |
| `jest.spyOn(obj, 'm')` | `vi.spyOn(obj, 'm')` | identical |
| `jest.useFakeTimers()` | `vi.useFakeTimers()` | identical |
| `jest.setSystemTime(d)` | `vi.setSystemTime(d)` | identical |
| `jest.resetAllMocks()` | `vi.resetAllMocks()` | identical |
| `jest.requireActual` | `vi.importActual` | async in Vitest |
| `jest.config.js` | `test` block in `vite.config.mts` | |
| `@stryker-mutator/jest-runner` | `@stryker-mutator/vitest-runner` | |

`describe/it/expect`, Testing Library, and MSW usage are identical in both.

## Quality Checklist

- [ ] Tests co-located per lib/module in `__tests__/` (or the project's convention)
- [ ] All factories live in `mocks/factories.ts` with `Partial<T>` overrides, typed against real contracts
- [ ] HTTP mocked with MSW at the network boundary; `onUnhandledRequest: 'error'` in tests
- [ ] Every MSW server has `listen`/`resetHandlers`/`close` lifecycle hooks
- [ ] Shared harness (provider wrappers, store resets) in `test-utils.tsx` — not copy-pasted
- [ ] Setup file contains ONLY environment shims and matcher registration
- [ ] Tests follow AAA pattern (Arrange → Act → Assert)
- [ ] Each test verifies exactly one behavior
- [ ] `test.each` cases are labeled/readable
- [ ] Coverage is ≥70% overall, 100% for critical/business-logic modules
- [ ] Mutation score ≥80% for critical modules (after 100% line coverage)
- [ ] No truthiness-only assertions (`toBeDefined`, `length > 0`) for exact-value logic
- [ ] Boundary conditions tested for every comparison operator (at, above, and below threshold)
- [ ] Seams were settled before any test was written, and the final report states them
- [ ] Test doubles sit only at system boundaries; a call to a double is asserted only when that call is the behavior under test
- [ ] Every test runs the real subject, and no expected value copies the production algorithm
- [ ] Each new test fails when the behavior it describes is removed (break the code temporarily, or check surviving mutants); strengthen tests that still pass
- [ ] Functions this task changes that are complex and poorly covered get tests or are split (optional diagnostic: CRAP, see the `code-review-js` skill, which has the install steps)
- [ ] Test names describe `<unit> <scenario> <expected>`
- [ ] No shared mutable state between tests (stores reset in `afterEach`; fresh mocks per test)
- [ ] External API calls are mocked (no real network calls in tests)
- [ ] Async assertions use `waitFor`/`findBy*` — no arbitrary sleeps

## Outputs

This skill produces:

1. **Directory structure** — `__tests__/` and `mocks/` per lib/module
2. **Factory files** — typed `buildX(overrides)` factories in `mocks/factories.ts`
3. **MSW handlers** — centralized per lib in `mocks/handlers.ts`
4. **Test harness** — `test-utils.tsx` wrappers and `test-setup.ts` shims
5. **Test files** — AAA-structured tests with `test.each` and Testing Library queries
6. **Runner config** — jest.config / vitest `test` block with coverage thresholds
7. **Stryker config** — `stryker.config.json` (when Step 8 is executed)
8. **Mutation report** — HTML report at `reports/mutation/mutation.html` identifying surviving mutants (when Step 8 is executed)

## Reference Documentation

- **Fixture Patterns**: [fixture-patterns.md](references/fixture-patterns.md)
- **Mock Patterns**: [mock-patterns.md](references/mock-patterns.md)
- **Async Testing**: [async-testing.md](references/async-testing.md)
- **Advanced Techniques**: [advanced-techniques.md](references/advanced-techniques.md)
- **Mutation Testing**: [mutation-testing.md](references/mutation-testing.md)
