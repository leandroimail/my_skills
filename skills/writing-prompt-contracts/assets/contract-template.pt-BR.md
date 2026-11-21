<OBJETIVO em 1 ou 2 frases: o que construir ou mudar, e para quem.> <O que basta: "Só precisa ...". O que não precisa: ...>

PRIORIDADES (nesta ordem quando entrarem em conflito)
1. <ex.: Não quebrar o que existe: os testes atuais continuam passando>
2. <ex.: Integridade dos dados>
3. <ex.: Performance no alvo>
4. <ex.: Diff pequeno>

CONTEXTO
- Repositório: <caminho>. Leia o código e as ferramentas de teste antes de mexer. Comece por: <arquivos>.
- Padrão a seguir: <arquivo ou módulo que já faz algo parecido>.
- Já se sabe: <fatos>. Já foi descartado: <hipótese e motivo>.
- Hipótese ainda aberta: <X>. Confirme ou descarte <X> antes de construir sobre ela.
- Pendências: para cada `[a confirmar: ... Padrão: ...]`, use o padrão e liste o item no relatório. Para um item `BLOQUEANTE`, faça só <trabalho permitido sem a resposta> e pare com um relatório "não pronto".

RESTRIÇÕES
- <restrição verificável>. Motivo: <por quê>.
- Não altere: <módulos, schema, contratos públicos, configuração de deploy>.
- Não altere os arquivos dos gates: <fixtures, cenários, scripts de verificação>.
- Não adicione dependência nova sem listar o motivo no relatório final.

ALVO
- Ambiente-alvo: <runtime, banco, navegador, com versão>.
- Orçamento: <métrica com número, unidade e condição de medição. Ex.: p95 ≤ 300 ms com 50 req/s durante 60 s>. Cada número desta seção tem um gate em VERIFICAÇÃO que mede o número e o reporta.

AMBIENTE
- Ferramentas disponíveis: <ex.: Node 20, Playwright, k6, leitura no banco DEV pela variável `<NOME>`>.
- Grave scripts, saídas e evidências em `<pasta-de-trabalho>/`.
- Ambiente compartilhado: <o que o agente não faz. Ex.: encerre só os processos que você abriu, não escreva em HML>.

REQUISITOS
- <comportamento observável>
- <regra de negócio>
- <caso de borda e o resultado esperado>
- <propriedade, sem implementação. Ex.: "nenhuma consulta faz full scan em <tabela>">

INTERFACE
<rotas, payloads, códigos de erro, telas, comandos, flags>

VERIFICAÇÃO
- Testes: `<comando>` termina com código 0. Cenários fixos: <lista ou arquivo>. Cada requisito e cada elemento da INTERFACE tem pelo menos um cenário que aciona o elemento e confere o efeito.
- Regressão: <os testes que já existem continuam passando. Saídas que precisam sair iguais às de antes>.
- Performance: `<comando>`. Reporte média, p95, p99 e máximo. <Em ambiente compartilhado: meça antes e depois da mudança, nas mesmas condições. O depois não pode ser pior que o antes além do ruído da medição.>
- Revisor isolado:
  - Grave em `<pasta-de-evidencias>/` só as saídas brutas: <respostas dos cenários, screenshots, logs>. Não grave nessa pasta comentário nem justificativa sua.
  - A cada rodada, crie um subagente novo, sem herdar esta conversa. Entregue a ele SOMENTE: REQUISITOS, INTERFACE, a referência `<gabarito: design, tela legada, respostas esperadas>`, a lista de arquivos de `<pasta-de-evidencias>/` e a escala abaixo. Não envie nenhuma explicação sobre o que é de propósito. Instrua o revisor a não ler nenhum outro arquivo.
  - Motivo: quem lê o código, o raciocínio ou a justificativa de quem construiu tende a aceitar o que o construtor pretendia.
  - O revisor compara as saídas com a referência e devolve defeitos concretos, em ordem de gravidade:
    - bloqueante: <viola um requisito, a INTERFACE ou uma restrição>
    - maior: <um usuário nota no uso normal>
    - menor: <só aparece na comparação lado a lado com a referência>
  - Itere até o revisor não reportar nada acima de "menor".

SE UM GATE NÃO PASSAR
- Não enfraqueça o gate. Não apague teste, não marque `skip`, não aumente limite, não mude o critério.
- Limite: no máximo <R> rodadas do revisor e <T> horas de trabalho. Pare antes se <N> rodadas seguidas não reduzirem os defeitos bloqueantes e maiores.
- Ao parar sem passar, entregue um relatório "não pronto": o gate que falha, a evidência, os defeitos que restam e as hipóteses.

PRONTO QUANDO todos os gates passam. Entregue:
- <diff ou PR>
- `<pasta-de-trabalho>/relatorio.md` com o resultado de cada gate e a saída dos comandos
- o relatório de performance
- a revisão final do revisor isolado
- os scripts de verificação, versionados para os próximos contratos
- o que ficou sem verificar, e o motivo
