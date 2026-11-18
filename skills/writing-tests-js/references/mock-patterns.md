# Mock Patterns Reference

Patterns for organizing and using mocks in TypeScript/JavaScript test suites
(Jest syntax; swap `jest.*` → `vi.*` for Vitest, `jest.requireActual` →
`await vi.importActual`).

## Table of Contents

- [Mock Organization by Type](#mock-organization-by-type)
- [Network Mocks with MSW](#network-mocks-with-msw)
- [Data Factories](#data-factories)
- [Module Mocks](#module-mocks)
- [Repository and QueryBuilder Mocks (NestJS/TypeORM)](#repository-and-querybuilder-mocks-nestjstypeorm)
- [Side-Effect Chains](#side-effect-chains)
- [Spies over Stubs](#spies-over-stubs)
- [Async Mocks](#async-mocks)
- [Store Mocks and Resets](#store-mocks-and-resets)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Mock Organization by Type

```
libs/my-feature/src/lib/mocks/
├── index.ts          # Barrel: exports factories + handlers
├── factories.ts      # buildX(overrides) typed data factories
├── fixtures.ts       # Static payload constants (error envelopes, configs)
└── handlers.ts       # MSW request handlers (consume the factories)
```

**Why by type?** Multiple test files need the same mock data. Centralizing
prevents duplicated definitions and keeps mocks in sync with the real
contracts (DTO types). Handlers double as a browser mock mode when the app
boots MSW behind an env flag.

## Network Mocks with MSW

Mock at the network boundary. Tests exercise the real api client, real
serialization, real error handling.

```typescript
// mocks/handlers.ts
import { http, HttpResponse, delay } from 'msw';
import { buildRecordPage, buildApiErrorEnvelope } from './factories';

const BASE = '/api/records';

// Sentinel values let tests trigger error paths through the same handlers
export const TRIGGER = { failCategory: 'FAIL' } as const;

export const recordHandlers = [
  http.get(BASE, async () => {
    await delay(50);
    return HttpResponse.json(buildRecordPage());
  }),
  http.post(BASE, async ({ request }) => {
    const body = (await request.json()) as { category: string };
    if (body.category === TRIGGER.failCategory) {
      return HttpResponse.json(buildApiErrorEnvelope('001'), { status: 422 });
    }
    return HttpResponse.json(buildRecordPage(), { status: 201 });
  }),
];
```

Test lifecycle — strict by default, override per test:

```typescript
import { setupServer } from 'msw/node';

const server = setupServer(...recordHandlers);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it('renders the empty state when the API returns no records', async () => {
  server.use(http.get('/api/records', () => HttpResponse.json(buildRecordPage({ records: [] }))));
  render(<RecordList />, { wrapper: createWrapper().wrapper });
  expect(await screen.findByText(/no records/i)).toBeInTheDocument();
});
```

Capturing the request body for assertions:

```typescript
let receivedBody: unknown = null;
server.use(
  http.post('/api/records', async ({ request }) => {
    receivedBody = await request.json();
    return HttpResponse.json(buildRecordPage(), { status: 201 });
  }),
);
// ...act...
await waitFor(() => expect(receivedBody).toEqual({ value: 42.5, category: 'A' }));
```

## Data Factories

Typed factories with `Partial<T>` overrides (see fixture-patterns.md for the
full treatment):

```typescript
export function buildApiErrorEnvelope(code: string, overrides: Partial<ApiError> = {}): ApiError {
  return { success: false, message: 'Erro de negócio', errors: [{ code }], data: null, ...overrides };
}
```

Usage in tests:

```typescript
it('labels the record page with its category counts', () => {
  const page = buildRecordPage({ records: buildRecordList(4, { category: 'B' }) });
  expect(summarize(page)).toEqual({ A: 0, B: 4 });
});
```

## Module Mocks

Mock framework modules the environment can't provide — navigation, toasts,
native bindings. Keep them minimal and per-file:

```typescript
// Next.js navigation
const push = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push, replace: jest.fn(), prefetch: jest.fn() }),
  usePathname: () => '/records',
}));

// Toast library
jest.mock('sonner', () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));
```

Partial module mock — keep the real implementation, replace one export:

```typescript
jest.mock('../services/record.service', () => ({
  ...jest.requireActual('../services/record.service'),
  exportToPdf: jest.fn().mockResolvedValue('/tmp/out.pdf'),
}));
```

**Prefer MSW over module mocks for anything HTTP** — module-mocking your api
client skips serialization and error paths, which is where bugs live.

## Repository and QueryBuilder Mocks (NestJS/TypeORM)

Repositories injected by token, mocked as plain objects:

```typescript
const repo = {
  findOne: jest.fn(),
  find: jest.fn(),
  save: jest.fn(),
  createQueryBuilder: jest.fn(),
};

await Test.createTestingModule({
  providers: [
    RecordService,
    { provide: getRepositoryToken(TbRecord), useValue: repo },
  ],
}).compile();
```

QueryBuilder is a fluent chain — mock with `mockReturnThis()`:

```typescript
const qb = {
  where: jest.fn().mockReturnThis(),
  andWhere: jest.fn().mockReturnThis(),
  orderBy: jest.fn().mockReturnThis(),
  getOne: jest.fn().mockResolvedValue(buildTbRecord()),
  getMany: jest.fn().mockResolvedValue([buildTbRecord()]),
};
repo.createQueryBuilder.mockReturnValue(qb as never);

// With the repository mocked, the query is the only place a filter shows, so
// assert it here. An integration test against a real database that asserts
// the returned rows is the stronger check, and it survives query refactors.
expect(qb.andWhere).toHaveBeenCalledWith('r.flAtivo = :ativo', { ativo: 'S' });
```

Raw SQL services — route `DataSource.query` by SQL content when a service
issues multiple statements:

```typescript
const dataSource = {
  query: jest.fn().mockImplementation((sql: string) => {
    if (sql.includes('FN_CHECK_ACESSO')) return Promise.resolve([{ HAS_ACCESS: 'S' }]);
    if (sql.includes('NEXTVAL')) return Promise.resolve([{ NEXT_VAL: 42 }]);
    return Promise.resolve([]);
  }),
};
```

## Side-Effect Chains

Simulate transient failures followed by success:

```typescript
it('retries on timeout and succeeds on the third attempt', async () => {
  const fetchPage = jest
    .fn()
    .mockRejectedValueOnce(new Error('ETIMEDOUT'))
    .mockRejectedValueOnce(new Error('ETIMEDOUT'))
    .mockResolvedValueOnce(buildRecordPage());

  const result = await fetchWithRetry(fetchPage, { retries: 3 });

  expect(result.records.length).toBeGreaterThan(0);
  expect(fetchPage).toHaveBeenCalledTimes(3);
});
```

With MSW, use a counter in the handler:

```typescript
let calls = 0;
server.use(
  http.get('/api/records', () => {
    calls += 1;
    if (calls < 3) return HttpResponse.error();
    return HttpResponse.json(buildRecordPage());
  }),
);
```

## Spies over Stubs

When the real implementation should run but you need observability, spy. Spy
on a call only when that call is the behavior under test (here, the hook's
contract is that a successful mutation invalidates the record list). When the
effect is visible to the user, assert on the refreshed data instead.

```typescript
const { wrapper, client } = createWrapper();
const invalidateSpy = jest.spyOn(client, 'invalidateQueries');

const { result } = renderHook(() => useRegisterRecord(), { wrapper });
act(() => result.current.mutate(buildRecord()));

await waitFor(() => expect(result.current.isSuccess).toBe(true));
expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: recordKeys.all });
```

Restore spies that replace behavior:

```typescript
afterEach(() => jest.restoreAllMocks());
```

## Async Mocks

`mockResolvedValue` / `mockRejectedValue` for promise-returning functions:

```typescript
const client = { fetchRecords: jest.fn().mockResolvedValue(buildRecordPage()) };

it('maps API records into domain rows', async () => {
  const rows = await loadRows(client);
  expect(rows).toHaveLength(2);
  expect(client.fetchRecords).toHaveBeenCalledWith({ page: 1 });
});
```

Type mocked interfaces so misuse fails compilation:

```typescript
const client: jest.Mocked<RecordClient> = {
  fetchRecords: jest.fn(),
  createRecord: jest.fn(),
};
client.fetchRecords.mockResolvedValue(buildRecordPage()); // typed!
```

`jest.Mocked<T>` is the closest analogue to autospec — the mock's surface is
checked against the real interface by the compiler.

## Store Mocks and Resets

Zustand-style stores: prefer the real store + reset over mocking it away.

```typescript
afterEach(() => {
  useRecordStore.setState(useRecordStore.getInitialState(), true);
});

it('advances the wizard after a successful submit', async () => {
  useRecordStore.setState({ step: 'form', cdPessoa: 1001 });
  // ... interact ...
  // The seam here is the store. In a UI test, assert the confirmation screen.
  expect(useRecordStore.getState().step).toBe('confirmation');
});
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Mocks defined inside each test file | Duplication, inconsistency | Define in `mocks/`, import |
| Mocking your own api-client module | Skips serialization/error paths | MSW at the network boundary |
| Over-mocking (mock everything) | Tests pass but code is broken | Mock only network, DB, and framework boundaries |
| Untyped `jest.fn()` grab-bags | Silent API drift | `jest.Mocked<Interface>` |
| Shared mutable mock state across tests | Order-dependent flakiness | Fresh mocks in `beforeEach`; `resetHandlers` |
| Mocking pure functions/data transforms | Fragile, tests the mock | Use real functions with factory data |
| Hardcoded temp paths | Parallel-run collisions | `mkdtemp` fixtures |
| Mock never checked | Mock silently ignored | Assert `toHaveBeenCalledWith(...)` when the outgoing call is the behavior under test; otherwise assert on the result it feeds |
| Asserting on the mock's own return value | Tests the mock, not the code | Run the real subject; mock only its boundary |
