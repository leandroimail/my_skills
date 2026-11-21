# api-rede-credenciada

API NestJS da rede credenciada. Lê dados do Oracle (DEV e HML compartilhados com outros times).

- Autenticação: JWT validado pelo `JwtAuthGuard`; papéis no claim `roles`.
- Acesso ao banco: cada módulo tem um `*.repository.ts` que usa `OracleService.query(sql, binds)`.
- Testes: `npm test` (unitários) e `npm run test:e2e` (sobe o app com banco DEV).
- Mudanças de schema seguem o fluxo de DBA (fora deste repositório).
