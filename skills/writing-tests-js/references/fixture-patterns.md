# Fixture Patterns Reference

Detailed patterns for test data and resource lifecycle management in
TypeScript/JavaScript test suites (Jest syntax; swap `jest.*` → `vi.*` for
Vitest).

## Table of Contents

- [Design Principles](#design-principles)
- [Data Factories](#data-factories)
- [Entity Factories (NestJS / TypeORM)](#entity-factories-nestjs--typeorm)
- [Temp File and Directory Fixtures](#temp-file-and-directory-fixtures)
- [Config Fixtures](#config-fixtures)
- [Provider Wrapper Fixtures (React)](#provider-wrapper-fixtures-react)
- [TestingModule Fixtures (NestJS)](#testingmodule-fixtures-nestjs)
- [Fixture Composition](#fixture-composition)
- [Scope Decision Guide](#scope-decision-guide)
- [Seeding via Factories](#seeding-via-factories)

## Design Principles

Every fixture/harness **must** follow this lifecycle contract:

```
1. SETUP    → provision the resource (beforeAll / beforeEach / factory call)
2. PROVIDE  → hand the ready resource to the test (return value / closure)
3. TEARDOWN → clean up (afterEach / afterAll: close servers, rm temp dirs, reset stores)
```

**Why explicit teardown?** Leaked servers, timers, and temp files make suites
flaky and order-dependent. Jest reports open handles
(`--detectOpenHandles`) — treat those as failures.

## Data Factories

The core pattern: a typed function with complete defaults and `Partial<T>`
overrides spread last. Deterministic by default.

```typescript
// mocks/factories.ts
import type { RecordDto } from '../types';

export function buildRecord(overrides: Partial<RecordDto> = {}): RecordDto {
  return {
    id: 1,
    timestamp: '2026-01-01T00:00:00Z',
    value: 42.5,
    category: 'A',
    ...overrides,
  };
}

// Lists: index-parameterized builder
export function buildRecordList(n = 10, overrides: Partial<RecordDto> = {}): RecordDto[] {
  return Array.from({ length: n }, (_, i) =>
    buildRecord({ id: i + 1, category: i % 2 === 0 ? 'A' : 'B', ...overrides }),
  );
}
```

For synthetic numeric series (deterministic pseudo-noise without `Math.random`):

```typescript
export function buildValueSeries(n = 100, base = 100, amplitude = 0.5): number[] {
  return Array.from({ length: n }, (_, i) => base + Math.sin(i / 3) * amplitude + i * 0.1);
}
```

## Entity Factories (NestJS / TypeORM)

Entities need every column the code touches — mirror the real schema:

```typescript
// apps/api/src/modules/records/__tests__/factories.ts
import { TbRecord } from '../entities/tb-record.entity';

export function buildTbRecord(overrides: Partial<TbRecord> = {}): TbRecord {
  return Object.assign(new TbRecord(), {
    id: 1,
    dsName: 'Record A',
    flAtivo: 'S',
    dtCriacao: new Date('2026-01-01T00:00:00Z'),
    ...overrides,
  });
}
```

`Object.assign(new Entity(), {...})` keeps the prototype (getters, methods)
while allowing plain-object defaults.

## Temp File and Directory Fixtures

```typescript
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

describe('csv importer', () => {
  let dataDir: string;

  beforeEach(async () => {
    dataDir = await mkdtemp(join(tmpdir(), 'myproject-test-'));
  });

  afterEach(async () => {
    await rm(dataDir, { recursive: true, force: true });
  });

  it('imports a well-formed csv', async () => {
    const path = join(dataDir, 'records.csv');
    await writeFile(path, 'id,value\n1,42.5\n2,43.0\n');
    const result = await importCsv(path);
    expect(result).toHaveLength(2);
  });
});
```

Rules:
- Always `mkdtemp` — never fixed paths like `/tmp/test.csv` (collisions in parallel runs)
- Teardown with `force: true` so failed tests still clean up
- Per-test (`beforeEach`) for mutable dirs; per-file (`beforeAll`) only for read-only data

## Config Fixtures

Prefer in-memory config injection over env-var mutation. When env mutation is
unavoidable, restore in teardown:

```typescript
describe('loadConfig', () => {
  const OLD_ENV = process.env;

  beforeEach(() => {
    process.env = { ...OLD_ENV };
  });

  afterAll(() => {
    process.env = OLD_ENV;
  });

  it('reads mode from the environment', () => {
    process.env.MYPROJECT_MODE = 'fast';
    expect(loadConfig().mode).toBe('fast');
  });
});
```

NestJS: inject typed config via its token instead of touching `process.env`:

```typescript
{ provide: databasesConfig.KEY, useValue: [{ name: 'DEFAULT', host: 'localhost' }] }
```

## Provider Wrapper Fixtures (React)

Framework context (QueryClient, Router, Theme) is provided by a `createWrapper`
helper — one per lib, in `__tests__/test-utils.tsx`:

```tsx
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

Usage — the returned `client` doubles as an observability handle, for tests
where cache invalidation is itself the behavior under test:

```typescript
const { wrapper, client } = createWrapper();
const invalidateSpy = jest.spyOn(client, 'invalidateQueries');
const { result } = renderHook(() => useRegisterRecord(), { wrapper });
act(() => result.current.mutate(buildRecord()));
await waitFor(() => expect(result.current.isSuccess).toBe(true));
expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: recordKeys.all });
```

Zustand (or similar) stores must be reset between tests:

```typescript
afterEach(() => {
  useRecordStore.getState().reset(); // or useRecordStore.setState(initialState, true)
});
```

## TestingModule Fixtures (NestJS)

Compile a module per suite with mocked providers:

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';

describe('RecordService', () => {
  let service: RecordService;
  let repo: { findOne: jest.Mock; save: jest.Mock };

  beforeEach(async () => {
    repo = { findOne: jest.fn(), save: jest.fn() };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        RecordService,
        { provide: getRepositoryToken(TbRecord), useValue: repo },
        { provide: OracleFunctionService, useValue: { execute: jest.fn() } },
      ],
    }).compile();

    service = module.get(RecordService);
  });

  it('returns the record when found', async () => {
    repo.findOne.mockResolvedValue(buildTbRecord());
    await expect(service.findById(1)).resolves.toMatchObject({ id: 1 });
  });
});
```

For e2e, boot the full app once per file and close it:

```typescript
let app: INestApplication;

beforeAll(async () => {
  const moduleFixture = await Test.createTestingModule({ imports: [AppModule] }).compile();
  app = moduleFixture.createNestApplication();
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));
  await app.init();
});

afterAll(async () => {
  await app.close();
});
```

Mirror the production bootstrap (prefix, pipes) or e2e results lie.

## Fixture Composition

Compose small helpers into scenario-level harnesses:

```typescript
// __tests__/test-utils.tsx
export function renderRecordForm(overrides: Partial<RecordDto> = {}) {
  const { wrapper, client } = createWrapper();
  const record = buildRecord(overrides);
  const utils = render(<RecordForm initial={record} />, { wrapper });
  return { ...utils, client, record };
}
```

```typescript
// NestJS: harness returning module + mocks together
export async function createRecordHarness() {
  const repo = { findOne: jest.fn(), save: jest.fn() };
  const module = await Test.createTestingModule({
    providers: [RecordService, { provide: getRepositoryToken(TbRecord), useValue: repo }],
  }).compile();
  return { service: module.get(RecordService), repo };
}
```

## Scope Decision Guide

| Hook | Lifecycle | Use For |
|------|-----------|---------|
| factory call in test | per statement | payloads, DTOs, entities |
| `beforeEach` | each test | mutable state, mock resets, temp dirs |
| `beforeAll` (file) | each file | MSW server, NestJS e2e app, expensive read-only setup |
| setup file (`setupFiles`) | whole run | environment shims, matchers |

**Rule of thumb:** Use the narrowest scope that avoids unnecessary re-creation.
Mutable resources are per-test; servers and compiled apps are per-file with
explicit `afterAll` teardown.

## Seeding via Factories

When a scenario needs pre-existing state (files on disk, handler datasets),
build a seeding helper that composes factories with the resource:

```typescript
// Seed a temp dir with batch files
export async function seedBatchDir(dir: string, nBatches = 5): Promise<string[]> {
  const paths: string[] = [];
  for (let i = 0; i < nBatches; i++) {
    const records = buildRecordList(20 * (i + 1));
    const path = join(dir, `batch_2026010${i + 1}.json`);
    await writeFile(path, JSON.stringify(records));
    paths.push(path);
  }
  return paths;
}

// Seed MSW with a stateful dataset for a multi-step flow
export function seedRecordHandlers(initial: RecordDto[] = buildRecordList(3)) {
  const db = [...initial];
  return [
    http.get('/api/records', () => HttpResponse.json({ records: db })),
    http.post('/api/records', async ({ request }) => {
      const body = (await request.json()) as RecordDto;
      db.push(body);
      return HttpResponse.json(body, { status: 201 });
    }),
  ];
}
```

**Key pattern:** factories flow into resources (files, handlers, repositories)
through small composition helpers — tests declare scenarios, not plumbing.
