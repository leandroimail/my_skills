# NestJS Review Checklist

Patterns verified against a production Nx + NestJS 11 codebase (TypeORM +
Oracle, Passport JWT, Swagger, global filters/interceptors in a shared
"chassis" lib). Substitute infrastructure names for your project's
equivalents — the checks stay the same.

## Table of Contents
- [DTOs and Validation](#dtos-and-validation)
- [Dependency Injection](#dependency-injection)
- [Controllers and Services](#controllers-and-services)
- [Data Access (TypeORM / Raw SQL)](#data-access-typeorm--raw-sql)
- [Guards, Auth, and Rate Limiting](#guards-auth-and-rate-limiting)
- [Exception Handling](#exception-handling)
- [Logging and Observability](#logging-and-observability)
- [Configuration](#configuration)
- [Testing NestJS Code](#testing-nestjs-code)

---

## DTOs and Validation

```
🔴 BLOCKER — unvalidated input on a mutating endpoint = merge blocked
```

- [ ] Global `ValidationPipe` configured with `whitelist: true`,
  `forbidNonWhitelistedProperties`/`forbidNonWhitelisted: true`, `transform: true`
- [ ] Every request body/query enters through a DTO class with class-validator
  decorators — no `@Body() body: any`
- [ ] Optional fields: `@IsOptional()` + type decorator; enum-like fields via `@IsIn([...])`
- [ ] String lengths bounded (`@MaxLength`) on fields persisted to the DB
- [ ] Update DTOs derive from create DTOs: `PartialType(CreateXDto)`
- [ ] Swagger annotations (`@ApiProperty` / `@ApiPropertyOptional`) match the actual
  validators — docs and behavior don't drift

```typescript
export class CreateAjusteFaturaDto {
  @ApiPropertyOptional()
  @IsOptional()
  @IsNumber()
  cdEmpresa?: number;

  @ApiPropertyOptional()
  @IsOptional()
  @IsDateString()
  dtVencimento?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsIn(['S', 'N'])
  @MaxLength(1)
  flAtivo?: string;
}
```

---

## Dependency Injection

- [ ] Providers injected via constructor — no `new SomeService()` inside business code
- [ ] Injection tokens for swappable implementations: `Symbol` token + provider
  `{ provide: TOKEN, useClass: Impl }`, consumed with `@Inject(TOKEN)` against an interface
- [ ] Typed config injected via `@nestjs/config` `registerAs` + `config.KEY` —
  no scattered `process.env` reads in services
- [ ] `forRoot`/`forFeature` module patterns for shared infra libs
- [ ] Request-scoped providers justified (they disable singleton caching and cascade)

---

## Controllers and Services

- [ ] Controllers are thin: route + DTO + delegation. No business logic, no SQL
- [ ] Services own business logic; repositories/data services own persistence
- [ ] One module per feature; shared infra in a dedicated lib, imported explicitly
- [ ] Route naming RESTful and versioned when contracts differ (`/v1` legacy vs `/v2` modern)
- [ ] Endpoints documented (`@ApiTags`, `@ApiOperation`) if the project uses Swagger
- [ ] Response envelope consistent (e.g. `{ success, message, data, errors }` via a
  global interceptor) — controllers don't hand-build envelopes

---

## Data Access (TypeORM / Raw SQL)

```
🔴 BLOCKER — string-built SQL = merge blocked
```

- [ ] Repository/QueryBuilder for standard CRUD; raw SQL only where the ORM cannot
  express the query (analytics, PL/SQL, hints)
- [ ] Raw SQL always uses binds — positional (`:1, :2` with a params array in Oracle)
  or named (`:param` with QueryBuilder) — never `${}` interpolation of values
- [ ] Identifiers (table, sequence, procedure names) interpolated only from
  code-owned constants/allowlists — never from user input
- [ ] Date binds explicit: pass `Date` objects or convert in SQL
  (`TO_DATE(:1, 'YYYY-MM-DD')` in Oracle) — no locale-dependent string comparison
- [ ] Stored procedure/function calls build placeholders programmatically:

```typescript
// Positional binds generated from the params array — safe and uniform
const placeholders = params.map((_, i) => `:${i + 1}`).join(', ');
await this.dataSource.query(`BEGIN ${procedureName}(${placeholders}); END;`, params);
```

- [ ] N+1 avoided: `relations: [...]` or `leftJoinAndSelect` where the result is iterated
- [ ] Transactions (`dataSource.transaction`) around multi-statement writes
- [ ] Bulk writes batched — no per-row `save()` loops for > 1k rows
- [ ] Entity definitions match the real schema (nullable, lengths, precision);
  migrations reviewed for two-phase safety (see sql-checklist)
- [ ] Connections/query runners released in `finally`

---

## Guards, Auth, and Rate Limiting

- [ ] Auth guard registered globally (`APP_GUARD`) with an explicit `@Public()`
  escape hatch via `Reflector` — endpoints are private by default
- [ ] Multi-issuer JWT (e.g. `AuthGuard(['keycloak-jwt', 'forms-jwt'])`) ordered
  most-common first; strategies extract via `ExtractJwt.fromAuthHeaderAsBearerToken()`
- [ ] Secrets/JWKS endpoints come from config — never inline
- [ ] Rate limiting on public surfaces: `ThrottlerModule` with tiered limits
  (e.g. 10/s short, 60/min medium) and `ThrottlerGuard` global
- [ ] Authorization (roles/screen-access) is separate from authentication and
  opt-in where legacy tokens lack claims
- [ ] Guard order intentional: authentication → throttling → authorization
- [ ] `helmet()` and CORS with explicit origins in bootstrap — wildcard origins
  only in local dev

---

## Exception Handling

- [ ] One global catch-all filter (`@Catch()` + `APP_FILTER`) normalizes every
  error into the response envelope; handles class-validator's `message: string[]`
- [ ] Domain exceptions extend a base (`BusinessException` → 422,
  `EntityNotFoundException` → 404) — services throw domain errors, not `HttpException`
  with hand-built payloads
- [ ] No `try/catch` in controllers for response shaping — that's the filter's job
- [ ] Stack traces logged server-side, never returned to clients in production

---

## Logging and Observability

- [ ] `new Logger(ClassName.name)` from `@nestjs/common` — no `console.*`
- [ ] Request logging via a global interceptor: method, url, status, elapsed ms,
  user, trace id
- [ ] PII masked in logs (dedicated interceptor or serializer)
- [ ] APM/tracing initialized first in `main.ts` (before other imports) when used;
  external calls (DB, HTTP) wrapped so they appear as spans
- [ ] Batch jobs log row counts at source and sink (detect silent data loss)

---

## Configuration

- [ ] `@nestjs/config` with `registerAs` namespaces; schema-validated at boot
  (fail fast on missing vars)
- [ ] No `process.env.X` sprinkled through services — inject typed config
- [ ] Separate config per environment; secrets from the environment/vault, never committed
- [ ] Feature flags and per-app toggles documented

---

## Testing NestJS Code

- [ ] Unit tests use `Test.createTestingModule` with mocked providers —
  repositories via `getRepositoryToken(Entity)` + `useValue`:

```typescript
const module: TestingModule = await Test.createTestingModule({
  providers: [
    SessionService,
    { provide: getRepositoryToken(TbOperador), useValue: { findOne: jest.fn() } },
    { provide: databasesConfig.KEY, useValue: [{ name: 'DEFAULT' }] },
  ],
}).compile();
service = module.get(SessionService);
```

- [ ] QueryBuilder mocked as a fluent chain: `{ where: jest.fn().mockReturnThis(), ..., getOne: jest.fn().mockResolvedValue(x) }`
- [ ] E2E via supertest against `app.getHttpServer()`, with the same global pipes
  as production bootstrap
- [ ] Migration/parity work (legacy vs modern implementations) covered by
  comparison tests asserting `expect(legacyResult).toEqual(modernResult)` per
  business rule, with intentional divergences documented by rule ID
- [ ] No real DB/Oracle connections in unit tests — mock `DataSource.query`
- [ ] Coverage thresholds enforced in jest config (e.g. 80% statements/functions/lines)
