# Advanced Testing Techniques

Advanced patterns for TypeScript/JavaScript suites (Jest syntax; swap
`jest.*` → `vi.*` for Vitest).

## Table of Contents

- [Parameterized Tests (test.each)](#parameterized-tests-testeach)
- [Property-Based Testing (fast-check)](#property-based-testing-fast-check)
- [Snapshot Testing — Sparingly](#snapshot-testing--sparingly)
- [Frozen Time and Deterministic Randomness](#frozen-time-and-deterministic-randomness)
- [Custom Matchers](#custom-matchers)
- [Contract and Parity Testing](#contract-and-parity-testing)
- [Testing Error Boundaries and Fallbacks](#testing-error-boundaries-and-fallbacks)
- [Selective Execution and Suite Hygiene](#selective-execution-and-suite-hygiene)

## Parameterized Tests (test.each)

Table form with named fields keeps cases self-documenting:

```typescript
it.each`
  value    | threshold | expected
  ${71}    | ${70}     | ${'HIGH'}
  ${70}    | ${70}     | ${'NORMAL'}
  ${30}    | ${30}     | ${'NORMAL'}
  ${29}    | ${30}     | ${'LOW'}
`('classifies value=$value with threshold=$threshold as $expected', ({ value, threshold, expected }) => {
  expect(classifyValue(value, { high: threshold, low: 30 })).toBe(expected);
});
```

Array form for compact equivalence classes:

```typescript
it.each([
  ['11', '987654321', true],
  ['1', '987654321', false],   // DDD too short
  ['11', '12345', false],      // number too short
])('validates ddd=%s number=%s → %s', (ddd, num, ok) => {
  expect(phoneSchema.safeParse({ ddd, num }).success).toBe(ok);
});
```

Include boundary rows (at, just above, just below every threshold) — these are
exactly the cases mutation testing punishes you for skipping.

## Property-Based Testing (fast-check)

`fast-check` is the JS equivalent of Python's hypothesis. Use it for
invariants over hand-picked examples:

```typescript
import fc from 'fast-check';

it('normalizeRecords is idempotent', () => {
  fc.assert(
    fc.property(
      fc.array(fc.record({ time: fc.date().map((d) => d.toISOString()), value: fc.float() })),
      (rows) => {
        const once = normalizeRecords(rows);
        expect(normalizeRecords(once)).toEqual(once);
      },
    ),
  );
});

it('parse/serialize round-trips', () => {
  fc.assert(
    fc.property(recordArbitrary(), (record) => {
      expect(parseRecord(serializeRecord(record))).toEqual(record);
    }),
  );
});
```

Good targets: parsers/serializers, normalization, sorting/pagination math,
money/rounding logic. Keep a `seed` in CI output so failures reproduce, and
add each shrunk counterexample as a permanent `it.each` row.

## Snapshot Testing — Sparingly

Snapshots verify structure you don't want to hand-assert — but they rot into
"approve everything" noise if overused.

```typescript
// ✅ Good: small, stable, reviewed serialized output
expect(buildSwaggerDoc(module).paths['/records']).toMatchSnapshot();

// ✅ Better: inline snapshot for small values — visible in the diff
expect(formatCurrency(1234.5)).toMatchInlineSnapshot(`"R$ 1.234,50"`);

// ❌ Bad: full-page component snapshot — fails on every style change
expect(render(<RecordPage />).container).toMatchSnapshot();
```

Rules:
- Snapshot only deterministic, semantically meaningful output
- Prefer `toMatchInlineSnapshot` for anything under ~10 lines
- A snapshot update in a PR is a **behavior change** — review it as such

## Frozen Time and Deterministic Randomness

```typescript
beforeEach(() => {
  jest.useFakeTimers();
  jest.setSystemTime(new Date('2026-01-15T12:00:00Z'));
});
afterEach(() => jest.useRealTimers());

it('stamps the record with the current business date', () => {
  expect(createRecord(buildRecord()).businessDate).toBe('2026-01-15');
});
```

Randomness: inject the generator, don't patch globals —

```typescript
// Production signature accepts an rng with a default
export function shuffle<T>(items: T[], rng: () => number = Math.random): T[] { ... }

// Test passes a seeded/deterministic rng
const seq = [0.1, 0.9, 0.5];
let i = 0;
expect(shuffle(items, () => seq[i++ % seq.length])).toEqual([...]);
```

## Custom Matchers

Encapsulate domain assertions used across many tests:

```typescript
// test-setup.ts
expect.extend({
  toBeValidCpf(received: string) {
    const pass = isValidCpf(received);
    return {
      pass,
      message: () => `expected ${received} ${pass ? 'not ' : ''}to be a valid CPF`,
    };
  },
});

// usage
expect(payload.cpf).toBeValidCpf();
```

Declare the matcher type once (`declare module 'expect' { interface Matchers<R> { toBeValidCpf(): R } }`)
so misuse fails compilation.

## Contract and Parity Testing

When two implementations must agree (legacy vs modern rewrite, v1 vs v2
route), build a harness that runs both against the same inputs and asserts
equality per business rule:

```typescript
describe('records parity: legacy vs modern', () => {
  let legacy: LegacyRecordService;
  let modern: ModernRecordService;

  beforeEach(async () => {
    ({ legacy, modern } = await createParityHarness()); // two TestingModules, mocked I/O
  });

  it.each([
    ['BR-REC-001: active filter', { flAtivo: 'S' }],
    ['BR-REC-002: date range', { from: '2026-01-01', to: '2026-01-31' }],
  ])('%s produces identical results', async (_rule, filters) => {
    const [legacyResult, modernResult] = await Promise.all([
      legacy.list(filters),
      modern.list(filters),
    ]);
    expect(modernResult).toEqual(legacyResult);
  });
});
```

Practices:
- Route mocked `DataSource.query` by SQL content so one harness serves many rules
- Give every business rule an ID (`BR-XXX-NNN`) and one `it.each` row
- Intentional divergences (bug-for-bug decisions) get their own test asserting
  the *documented* difference — never a skipped test

Schema contracts: validate handler/fixture payloads with the production zod
schema so mocks can't drift from reality:

```typescript
it('mock factories satisfy the API schema', () => {
  expect(() => recordPageSchema.parse(buildRecordPage())).not.toThrow();
});
```

## Testing Error Boundaries and Fallbacks

```tsx
it('renders the fallback when the widget throws', () => {
  const Boom = () => { throw new Error('boom'); };
  const spy = jest.spyOn(console, 'error').mockImplementation(() => {}); // silence React noise

  render(
    <ErrorBoundary fallback={<p role="alert">something broke</p>}>
      <Boom />
    </ErrorBoundary>,
  );

  expect(screen.getByRole('alert')).toHaveTextContent(/something broke/i);
  spy.mockRestore();
});
```

Backend equivalent: assert the global exception filter maps each domain error
to its envelope/status through a real HTTP call (supertest), not by calling
the filter directly.

## Selective Execution and Suite Hygiene

```bash
npx jest path/to/file.test.ts          # one file
npx jest -t "boundary"                 # by test name
npx jest --changedSince=main           # affected by your diff
nx affected -t test                    # monorepo: affected projects only
npx jest --detectOpenHandles           # find leaked servers/timers
```

- `it.only` / `it.skip` never reach main — lint with `no-focused-tests` (eslint-plugin-jest)
- Quarantine flaky tests with a ticket, don't retry-loop them
- Keep unit suites under ~30s per project; push slow paths to integration/E2E tiers
