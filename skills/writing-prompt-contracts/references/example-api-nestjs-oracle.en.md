<!--
Illustrative example of the filled template. Paths, tables, routes, and scripts are fictitious: replace them with the ones in your repository.
This example shows that the template can be filled. Nobody has executed it on a real task.
Before using it, confirm that every command in VERIFICATION runs in your environment.
A pt-BR contract uses the headings in the "Portuguese headings" table of filling-guide.md.
-->

Build in `apps/api` the endpoint that lists a member's authorizations, for the portal's service desk screen. The endpoint only needs to read. It does not need caching, writes, or cursor pagination.

PRIORITIES (in this order when they conflict)
1. Do not break what exists: the current `apps/api` tests keep passing and no existing endpoint changes its contract.
2. Correct data: the response has the same records as the reference query.
3. Security: only an authenticated operator with the `atendimento` role has access.
4. Performance on target.
5. Small diff.

CONTEXT
- Repository: `<monorepo-root>`. Read the code and the test tooling before changing anything, starting with `apps/api/src/beneficiarios/` and `apps/api/test/beneficiarios.e2e-spec.ts`.
- Pattern to follow: the `beneficiarios` module. The `beneficiarios` module already uses the Oracle repository, the JWT guard, and DTOs with `class-validator`.
- Reference query: `docs/sql/autorizacoes-por-beneficiario.sql`. The business team validated this query.
- Open hypothesis: the index on `<AUTHORIZATIONS_TABLE>(ID_BENEFICIARIO, DT_SOLICITACAO)` covers the query. Confirm or rule out the hypothesis with the execution plan in DEV.
- Open items: for each `[to confirm: ... Default: ...]`, use the default and list it in the report. For the `BLOCKING` item, do everything except the cancelled-status rule and stop with a "not done" report.

CONSTRAINTS
- Access Oracle read-only, in DEV only. Reason: staging and production are shared.
- Do not change the schema, views, or database packages. Reason: database changes go through a different approval flow.
- Do not change files outside `apps/api/src/autorizacoes/`, `apps/api/src/app.module.ts`, and `apps/api/test/`.
- Do not change `apps/api/test/fixtures/autorizacoes.json` or `apps/api/perf/autorizacoes.k6.js`. Reason: these files are the gates, and the team wrote both before the task.
- Do not add a package to `package.json`. Reason: the pipeline blocks unapproved packages.
- Use bind variables in every query. Reason: prevent SQL injection and reuse the execution plan.

TARGET
- Node 20, NestJS 10, Oracle 19c in DEV.
- p95 ≤ 300 ms and max ≤ 1 s, at 20 req/s for 60 s, for a member with up to 500 authorizations [to confirm: is 20 req/s the real peak? Default: 20 req/s]. The performance gate measures these numbers.

ENVIRONMENT
- Available tools: Node 20, k6, and read access to Oracle DEV through the `ORACLE_DEV_URL` variable.
- Write scripts, outputs, and evidence to `.work/autorizacoes/`. Do not include that folder in the PR.
- The DEV database is shared with other teams. Do not run load above 20 req/s and do not leave connections open after the tests.

REQUIREMENTS
- The endpoint returns the authorizations of the last 12 months, newest first. The window starts at 00:00 America/Fortaleza today minus 12 months, and dates go out as `YYYY-MM-DD`.
- Cancelled authorizations [to confirm: should the service desk see them? BLOCKING].
- Each item has the authorization number, request date, status, procedure, and provider.
- The endpoint paginates with `page` and `size`. Without `size`, the page size is 20. The maximum `size` is 100.
- `size` above 100: HTTP 400 with `code: PARAMETRO_INVALIDO`.
- Member with no authorizations: HTTP 200 with empty `items`.
- Unknown member: HTTP 404 with `code: BENEFICIARIO_NAO_ENCONTRADO`.
- Request without a token or with an expired token: HTTP 401. Token without the `atendimento` role: HTTP 403.
- The response never contains data from another member.

INTERFACE
```
GET /beneficiarios/{id}/autorizacoes?page=1&size=20

200 {
  "items": [{
    "numero": "string",
    "dataSolicitacao": "YYYY-MM-DD",
    "situacao": "string",
    "procedimento": { "codigo": "string", "descricao": "string" },
    "prestador": { "codigo": "string", "nome": "string" }
  }],
  "page": 1, "size": 20, "total": 0
}

4xx { "code": "string", "message": "string" }
```

VERIFICATION
- Tests: `npm run test -w apps/api` and `npm run test:e2e -w apps/api` exit with code 0.
- Fixed scenarios, already written in `apps/api/test/fixtures/autorizacoes.json`:
  1. member with no authorizations
  2. member with 1 authorization
  3. member with 500 authorizations
  4. member with one authorization from 13 months ago, outside the window
  5. unknown member
  6. token without the `atendimento` role
  7. request without a token
  8. `size=101`
- Regression: the `apps/api` tests that exist today keep passing without changes.
- Equivalence: for scenarios 1 to 4, the endpoint response has the same records as the reference query in DEV.
- Execution plan: the `EXPLAIN PLAN` of the new query has no `TABLE ACCESS FULL` on `<AUTHORIZATIONS_TABLE>`.
- Performance: `k6 run apps/api/perf/autorizacoes.k6.js` against DEV. Report mean, p95, p99, and max.
- Isolated reviewer:
  - Write to `.work/autorizacoes/evidence/` only the HTTP responses of the 8 scenarios, with status and body, and the output of the reference query. Do not put your comments or justifications in that folder.
  - Every round, start a new subagent that does not inherit this conversation. Give it ONLY: REQUIREMENTS, INTERFACE, the file list of `.work/autorizacoes/evidence/`, and the scale below. Send no explanation of what is intentional. Tell the reviewer to read no other file.
  - Reason: whoever reads the builder's code, reasoning, or justifications tends to accept what the builder intended.
  - The reviewer compares the responses with REQUIREMENTS, INTERFACE, and the reference query, and returns concrete defects, ordered by severity:
    - blocker: violates a requirement, the INTERFACE, or a constraint, or shows another member's data
    - major: the service desk screen would show something wrong in normal use, such as a wrong order, date, or status
    - minor: a difference in the `message` text or in formatting that does not change the meaning
  - Iterate until the reviewer reports nothing above "minor".

IF A GATE DOES NOT PASS
- Do not weaken the gate. Do not delete a test, do not mark it `skip`, do not raise a limit, do not change the criterion.
- If the execution plan shows a full scan, do not create an index. Deliver the plan and the ruled-out hypothesis.
- Limit: at most 5 reviewer rounds and 2 hours of work. Stop earlier if 2 consecutive rounds do not reduce the blocker and major defects.
- When you stop without passing, deliver a "not done" report: the failing gate, the evidence, the remaining defects, and the hypotheses.

DONE WHEN all gates pass. Deliver:
- the draft PR with the diff
- `.work/autorizacoes/report.md` with the result of each gate and the test command output
- the equivalence table for scenarios 1 to 4
- the execution plan
- the performance report
- the final review of the isolated reviewer
- what was not verified, and why
