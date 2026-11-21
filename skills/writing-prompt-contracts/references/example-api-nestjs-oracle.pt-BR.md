<!--
Exemplo ilustrativo do template preenchido. Caminhos, tabelas, rotas e scripts são fictícios: substitua pelos do seu repositório.
Este exemplo mostra que o template é preenchível. Ninguém executou este exemplo numa tarefa real.
Antes de usar, confirme que cada comando da seção VERIFICAÇÃO roda no seu ambiente.
-->

Crie em `apps/api` o endpoint que lista as autorizações de um beneficiário, para a tela de atendimento do portal. O endpoint só precisa ler. Não precisa de cache, de escrita nem de paginação por cursor.

PRIORIDADES (nesta ordem quando entrarem em conflito)
1. Não quebrar o que existe: os testes atuais de `apps/api` continuam passando e nenhum endpoint existente muda de contrato.
2. Dados corretos: a resposta tem os mesmos registros que a consulta de referência.
3. Segurança: só operador autenticado com o papel `atendimento` acessa.
4. Performance no alvo.
5. Diff pequeno.

CONTEXTO
- Repositório: `<raiz-do-monorepo>`. Leia o código e as ferramentas de teste antes de mexer. Comece por `apps/api/src/beneficiarios/` e `apps/api/test/beneficiarios.e2e-spec.ts`.
- Padrão a seguir: o módulo `beneficiarios`. O módulo `beneficiarios` já usa o repository Oracle, o guard de JWT e DTOs com `class-validator`.
- Consulta de referência: `docs/sql/autorizacoes-por-beneficiario.sql`. O time de negócio validou esta consulta.
- Hipótese aberta: o índice em `<TABELA_AUTORIZACOES>(ID_BENEFICIARIO, DT_SOLICITACAO)` cobre a consulta. Confirme ou descarte a hipótese com o plano de execução em DEV.
- Pendências: para cada `[a confirmar: ... Padrão: ...]`, use o padrão e liste o item no relatório. Para o item `BLOQUEANTE`, faça tudo menos a regra das autorizações canceladas e pare com um relatório "não pronto".

RESTRIÇÕES
- Acesse o Oracle só para leitura, só em DEV. Motivo: HML e PROD são compartilhados.
- Não altere schema, views nem packages do banco. Motivo: mudança de banco tem outro fluxo de aprovação.
- Não altere arquivos fora de `apps/api/src/autorizacoes/`, `apps/api/src/app.module.ts` e `apps/api/test/`.
- Não altere `apps/api/test/fixtures/autorizacoes.json` nem `apps/api/perf/autorizacoes.k6.js`. Motivo: esses arquivos são os gates, e o time escreveu os dois antes da tarefa.
- Não adicione pacote ao `package.json`. Motivo: o pipeline bloqueia pacote sem aprovação.
- Use bind variables em toda consulta. Motivo: evitar SQL injection e reaproveitar o plano de execução.

ALVO
- Node 20, NestJS 10, Oracle 19c em DEV.
- p95 ≤ 300 ms e máximo ≤ 1 s, com 20 req/s durante 60 s, para beneficiário com até 500 autorizações [a confirmar: 20 req/s é o pico real? Padrão: 20 req/s]. O gate de performance mede estes números.

AMBIENTE
- Ferramentas disponíveis: Node 20, k6 e leitura no Oracle DEV pela variável `ORACLE_DEV_URL`.
- Grave scripts, saídas e evidências em `.trabalho/autorizacoes/`. Não inclua essa pasta no PR.
- O banco DEV é compartilhado com outros times. Não rode carga acima de 20 req/s e não deixe conexões abertas depois dos testes.

REQUISITOS
- O endpoint retorna as autorizações dos últimos 12 meses, da mais recente para a mais antiga. A janela começa às 00h00 de hoje menos 12 meses em America/Fortaleza, e as datas saem como `YYYY-MM-DD`.
- Autorizações canceladas [a confirmar: o atendimento deve ver essas autorizações? BLOQUEANTE].
- Cada item tem número da autorização, data da solicitação, situação, procedimento e prestador.
- O endpoint pagina por `page` e `size`. Sem `size`, o tamanho é 20. O `size` máximo é 100.
- `size` acima de 100: HTTP 400 com `code: PARAMETRO_INVALIDO`.
- Beneficiário sem autorizações: HTTP 200 com `items` vazio.
- Beneficiário inexistente: HTTP 404 com `code: BENEFICIARIO_NAO_ENCONTRADO`.
- Requisição sem token ou com token expirado: HTTP 401. Token sem o papel `atendimento`: HTTP 403.
- A resposta nunca contém dado de outro beneficiário.

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

VERIFICAÇÃO
- Testes: `npm run test -w apps/api` e `npm run test:e2e -w apps/api` terminam com código 0.
- Cenários fixos, já escritos em `apps/api/test/fixtures/autorizacoes.json`:
  1. beneficiário sem autorizações
  2. beneficiário com 1 autorização
  3. beneficiário com 500 autorizações
  4. beneficiário com uma autorização de 13 meses atrás, fora da janela
  5. beneficiário inexistente
  6. token sem o papel `atendimento`
  7. requisição sem token
  8. `size=101`
- Regressão: os testes de `apps/api` que existem hoje continuam passando sem alteração.
- Equivalência: para os cenários 1 a 4, a resposta do endpoint tem os mesmos registros que a consulta de referência em DEV.
- Plano de execução: o `EXPLAIN PLAN` da consulta nova não tem `TABLE ACCESS FULL` em `<TABELA_AUTORIZACOES>`.
- Performance: `k6 run apps/api/perf/autorizacoes.k6.js` contra DEV. Reporte média, p95, p99 e máximo.
- Revisor isolado:
  - Grave em `.trabalho/autorizacoes/evidencias/` só as respostas HTTP dos 8 cenários, com status e corpo, e o resultado da consulta de referência. Não grave nessa pasta comentário nem justificativa sua.
  - A cada rodada, crie um subagente novo, sem herdar esta conversa. Entregue a ele SOMENTE: REQUISITOS, INTERFACE, a lista de arquivos de `.trabalho/autorizacoes/evidencias/` e a escala abaixo. Não envie nenhuma explicação sobre o que é de propósito. Instrua o revisor a não ler nenhum outro arquivo.
  - Motivo: quem lê o código, o raciocínio ou a justificativa de quem construiu tende a aceitar o que o construtor pretendia.
  - O revisor compara as respostas com REQUISITOS, INTERFACE e a consulta de referência e devolve defeitos concretos, em ordem de gravidade:
    - bloqueante: viola um requisito, a INTERFACE ou uma restrição, ou mostra dado de outro beneficiário
    - maior: a tela de atendimento mostraria algo errado no uso normal, como ordem, data ou situação incorreta
    - menor: diferença de texto em `message` ou de formatação que não muda o significado
  - Itere até o revisor não reportar nada acima de "menor".

SE UM GATE NÃO PASSAR
- Não enfraqueça o gate. Não apague teste, não marque `skip`, não aumente limite, não mude o critério.
- Se o plano de execução mostrar full scan, não crie índice. Entregue o plano e a hipótese descartada.
- Limite: no máximo 5 rodadas do revisor e 2 horas de trabalho. Pare antes se 2 rodadas seguidas não reduzirem os defeitos bloqueantes e maiores.
- Ao parar sem passar, entregue um relatório "não pronto": o gate que falha, a evidência, os defeitos que restam e as hipóteses.

PRONTO QUANDO todos os gates passam. Entregue:
- o PR em rascunho com o diff
- `.trabalho/autorizacoes/relatorio.md` com o resultado de cada gate e a saída dos comandos de teste
- a tabela de equivalência dos cenários 1 a 4
- o plano de execução
- o relatório de performance
- a revisão final do revisor isolado
- o que ficou sem verificar, e o motivo
