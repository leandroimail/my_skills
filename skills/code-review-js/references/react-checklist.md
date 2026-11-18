# React / Next.js Review Checklist

Patterns verified against a production Nx + Next.js App Router codebase
(React 19, TanStack Query v5, react-hook-form + zod, Zustand, Tailwind,
Radix-based design system). Substitute library names for your project's
equivalents — the checks stay the same.

## Table of Contents
- [Hooks Rules](#hooks-rules)
- [Server / Client Components (Next.js App Router)](#server--client-components-nextjs-app-router)
- [Data Fetching](#data-fetching)
- [Forms and Validation](#forms-and-validation)
- [State Management](#state-management)
- [Component Design](#component-design)
- [Accessibility](#accessibility)
- [Rendering Performance](#rendering-performance)
- [Testing React Code](#testing-react-code)

---

## Hooks Rules

```
🔴 BLOCKER — hook misuse causes stale state and impossible-to-debug renders
```

- [ ] `eslint-plugin-react-hooks` passes (comes via `eslint-config-next`)
- [ ] No hooks inside conditions, loops, or callbacks
- [ ] `exhaustive-deps` warnings resolved, not silenced — a suppression needs a comment
  explaining why the dependency is intentionally omitted
- [ ] Effects used for synchronization with external systems only — not for
  deriving state (compute during render) or fetching server data (use a query library)
- [ ] Cleanup functions on every effect that subscribes, listens, or sets timers
- [ ] Custom hooks named `useX` and composed from primitives — components stay thin

```tsx
// ❌ Derived state in an effect — extra render + stale window
useEffect(() => { setFullName(`${first} ${last}`); }, [first, last]);

// ✅ Compute during render
const fullName = `${first} ${last}`;
```

---

## Server / Client Components (Next.js App Router)

- [ ] `'use client'` only where interactivity requires it (state, effects, browser APIs) —
  not copy-pasted on every file
- [ ] Server-only secrets (`process.env.X` without `NEXT_PUBLIC_`) never imported
  into client components
- [ ] Route wrappers (`page.tsx`, `layout.tsx`) stay thin — logic lives in feature
  libs/components; wrappers are covered by E2E rather than unit tests
- [ ] Route handlers (`app/api/**/route.ts`) validate input with a schema before use
- [ ] `next/image` for images and `next/link` for internal navigation — no raw
  `<img>`/`<a>` for app routes
- [ ] Metadata via the Metadata API — not manual `<head>` manipulation

---

## Data Fetching

- [ ] Server state via TanStack Query (or equivalent) — **not** `useEffect` +
  `useState` fetch orchestration
- [ ] Query keys are hierarchical and centralized per feature (e.g. a
  `query-keys.ts` exporting `featureKeys.all`, `featureKeys.detail(id)`) —
  mutations invalidate by key, no string duplication
- [ ] API responses validated with a zod schema (`schema.parse(raw)`) before
  entering typed code
- [ ] Mutations handle errors visibly (toast/alert) and invalidate affected
  queries in `onSuccess`
- [ ] Loading and error states rendered — no silent spinners forever
- [ ] No secrets or tokens in query keys or URLs

```typescript
// ✅ Pattern: hierarchical keys + validated fetch
export const orderKeys = {
  all: ['orders'] as const,
  detail: (id: number) => [...orderKeys.all, 'detail', id] as const,
};

export function useOrder(id: number) {
  return useQuery({
    queryKey: orderKeys.detail(id),
    queryFn: async () => orderSchema.parse(await api.get(`/orders/${id}`)),
  });
}
```

---

## Forms and Validation

- [ ] react-hook-form + `zodResolver` (or equivalent schema resolver) — no
  hand-rolled validation state
- [ ] Schema colocated with the form and shared with the submit payload type
  (`z.infer<typeof schema>`)
- [ ] Validation mode intentional (`mode: 'onBlur'` is a good default) —
  aggressive `onChange` validation justified
- [ ] Error messages rendered with `role="alert"` and linked via `aria-describedby`
- [ ] Inputs labeled: `<Label htmlFor>` matching input `id`; `aria-invalid` on error
- [ ] Submit disabled or debounced during pending mutation — no double submits
- [ ] Masked inputs (CPF, phone) keep the unmasked value in the form state

---

## State Management

- [ ] Server cache (query library) vs client state (Zustand/context) vs URL state —
  each piece of data lives in exactly one place; no copying query results into a store
- [ ] Stores are small and feature-scoped; selectors used to avoid whole-store re-renders
- [ ] Store reset on logout/unmount where state must not leak between sessions/tests
- [ ] No context for rapidly-changing values (causes tree-wide re-renders)

---

## Component Design

- [ ] Components < 300 lines; stores < 150 lines — extract subcomponents/hooks beyond that
- [ ] Presentational components take data via props — no data fetching in leaves
- [ ] Design-system primitives used instead of ad-hoc styled elements; `className`
  merged via a `cn()` helper
- [ ] Design tokens (CSS vars) instead of hardcoded colors
- [ ] Lists render with stable `key` — never the array index when items reorder
- [ ] No `dangerouslySetInnerHTML` with unsanitized input (XSS — 🔴 Blocker)
- [ ] Named exports; feature code in libs, apps as thin wrappers (monorepo)

---

## Accessibility

- [ ] Interactive elements are reachable by role and accessible name —
  `getByRole('button', { name: /continuar/i })` works in tests
- [ ] Keyboard navigation: no `div onClick` without `role`, `tabIndex`, and key handlers —
  use `<button>` / `<a>`
- [ ] Form errors announced: `role="alert"` + `aria-describedby`
- [ ] Focus management on route/dialog changes (focus trap in modals — Radix handles this)
- [ ] Color contrast meets WCAG AA; state not conveyed by color alone
- [ ] `eslint-plugin-jsx-a11y` (via Next preset) passes
- [ ] Automated a11y checks in E2E when configured (`@axe-core/playwright` `AxeBuilder`)

---

## Rendering Performance

- [ ] Expensive computations memoized (`useMemo`) with correct deps — but only
  when measured/hot; no cargo-cult memoization of trivial values
- [ ] Callbacks passed to memoized children wrapped in `useCallback`
- [ ] Large lists virtualized (TanStack Virtual or table pagination)
- [ ] No new object/array literals passed as props to memoized components per render
- [ ] Heavy client libs dynamically imported (`next/dynamic`) when below the fold
- [ ] Images sized (`width`/`height` or `fill`) to prevent layout shift

---

## Testing React Code

- [ ] Testing Library queries by role/label — no `getByTestId` where a role query works
  (a11y and tests reinforce each other)
- [ ] `userEvent.setup()` for interactions — not `fireEvent` for user flows
- [ ] HTTP mocked with MSW at the network boundary (`setupServer` +
  `server.use(...)` per-test overrides) — not by mocking the api client module
- [ ] Framework modules mocked explicitly when needed
  (`vi.mock('next/navigation')` / `jest.mock('next/navigation')`)
- [ ] Hooks tested with `renderHook` + a `QueryClientProvider` wrapper helper
  (`retry: false` in tests)
- [ ] Zustand stores reset in `afterEach` — no state leaking between tests
- [ ] Async assertions via `findBy*` / `waitFor` — no arbitrary sleeps
- [ ] Route wrappers (`page.tsx`) excluded from unit coverage and covered by E2E
