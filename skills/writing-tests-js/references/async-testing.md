# Async Testing Reference

Patterns for testing asynchronous TypeScript/JavaScript code (Jest syntax;
swap `jest.*` → `vi.*` for Vitest).

## Table of Contents

- [Async Test Basics](#async-test-basics)
- [Rejection Assertions](#rejection-assertions)
- [Fake Timers](#fake-timers)
- [Testing Retry and Backoff Logic](#testing-retry-and-backoff-logic)
- [Testing Concurrency](#testing-concurrency)
- [React: waitFor and findBy](#react-waitfor-and-findby)
- [NestJS: Async Providers and supertest](#nestjs-async-providers-and-supertest)
- [Common Async Pitfalls](#common-async-pitfalls)

## Async Test Basics

Always `await` inside the test — an unawaited promise makes the test pass
before the assertion runs:

```typescript
it('fetches a page of records', async () => {
  const page = await fetchRecords({ page: 1 });
  expect(page.records).toHaveLength(2);
});
```

Resolution assertions in one step:

```typescript
await expect(fetchRecords({ page: 1 })).resolves.toMatchObject({ status: 'ok' });
```

## Rejection Assertions

```typescript
// Exact error class + message
await expect(fetchRecords({ page: -1 })).rejects.toThrow(RangeError);
await expect(fetchRecords({ page: -1 })).rejects.toThrow('page must be positive');

// Inspecting a domain error's fields
await expect(service.approve(0)).rejects.toMatchObject({
  code: 'RECORD_NOT_FOUND',
  status: 404,
});
```

Never wrap in try/catch with assertions in the catch — if nothing throws, the
test silently passes. If you must, add `expect.assertions(n)`:

```typescript
it('rejects invalid ids', async () => {
  expect.assertions(1);
  try {
    await service.approve(0);
  } catch (err) {
    expect(err).toBeInstanceOf(EntityNotFoundException);
  }
});
```

## Fake Timers

Control time-dependent code (debounce, polling, TTL):

```typescript
describe('debounced search', () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  it('fires once after the debounce window', async () => {
    const spy = jest.fn();
    const search = debounce(spy, 300);

    search('a');
    search('ab');
    await jest.advanceTimersByTimeAsync(300);

    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('ab');
  });
});
```

- Use the `*Async` variants (`advanceTimersByTimeAsync`, `runAllTimersAsync`)
  when the timer callbacks contain awaits — they flush microtasks too.
- Fix the clock for date-dependent logic: `jest.setSystemTime(new Date('2026-01-15T12:00:00Z'))`.
- Restore real timers in `afterEach` — leaked fake timers break MSW and Testing Library waits.

## Testing Retry and Backoff Logic

Combine side-effect chains with fake timers so the test doesn't actually wait:

```typescript
it('retries with exponential backoff and succeeds', async () => {
  jest.useFakeTimers();
  const call = jest
    .fn()
    .mockRejectedValueOnce(new Error('ETIMEDOUT'))
    .mockResolvedValueOnce('ok');

  const promise = withRetry(call, { retries: 2, baseDelayMs: 1000 });
  await jest.runAllTimersAsync();

  await expect(promise).resolves.toBe('ok');
  expect(call).toHaveBeenCalledTimes(2);
});
```

Note: create the promise first, then advance timers, then await it —
awaiting first would deadlock under fake timers.

## Testing Concurrency

```typescript
it('fetches all pages in parallel', async () => {
  const fetchPage = jest.fn().mockResolvedValue(buildRecordPage());

  await fetchAllPages(fetchPage, { pages: 3 });

  expect(fetchPage).toHaveBeenCalledTimes(3);
});

it('propagates the first failure from Promise.all', async () => {
  const fetchPage = jest
    .fn()
    .mockResolvedValueOnce(buildRecordPage())
    .mockRejectedValueOnce(new Error('boom'));

  await expect(fetchAllPages(fetchPage, { pages: 2 })).rejects.toThrow('boom');
});
```

For `Promise.allSettled` flows, assert both fulfilled and rejected outcomes are
handled (partial-failure behavior is where bugs hide).

## React: waitFor and findBy

Async UI assertions poll — never sleep:

```tsx
// findBy* = getBy* + waitFor in one call
expect(await screen.findByRole('alert')).toHaveTextContent(/required/i);

// waitFor for non-query assertions
await waitFor(() => expect(result.current.isSuccess).toBe(true));

// state updates outside React handlers need act()
act(() => result.current.mutate(buildRecord()));
```

Rules:
- One logical assertion inside `waitFor` — it retries the whole callback
- Don't mix `waitFor` with fake timers unless the runner is configured for it
  (Testing Library's `asyncWrapper`/`advanceTimers` options)
- `await user.click(...)` — all `user-event` calls are async

## NestJS: Async Providers and supertest

Service unit tests — mock async dependencies with `mockResolvedValue`:

```typescript
it('wraps the Oracle function result', async () => {
  oracleFn.execute.mockResolvedValue([{ HAS_ACCESS: 'S' }]);
  await expect(service.hasAccess('T1234')).resolves.toBe(true);
});
```

E2E — supertest returns promises; await them:

```typescript
it('GET /api/health/ping responds 200', async () => {
  await request(app.getHttpServer())
    .get('/api/health/ping')
    .expect(200)
    .expect((res) => {
      expect(res.body).toHaveProperty('pong', true);
    });
});
```

## Common Async Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Missing `await` on the assertion | Test passes, then logs an unhandled rejection | `await expect(...).rejects/resolves` |
| `setTimeout` sleep in test | Slow and still flaky | fake timers or `waitFor` |
| Fake timers leak between tests | Later tests hang | `jest.useRealTimers()` in `afterEach` |
| Awaiting before advancing fake timers | Deadlock | create promise → advance → await |
| Unclosed server/app/handles | Jest warns "did not exit" | `afterAll(() => app.close())`, `--detectOpenHandles` |
| Multiple assertions in one `waitFor` | Slow retries, unclear failures | one condition per `waitFor` |
| Firing events without `act`/user-event | "not wrapped in act" warnings, stale UI | `userEvent.setup()` + await |
