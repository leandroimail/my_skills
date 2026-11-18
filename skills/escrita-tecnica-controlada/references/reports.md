# Technical reports

A technical report exists so that someone can decide or act. It answers, in this order: what you concluded, how much the reader can trust it, and what the reader needs to do.

The templates are in Portuguese because the reports they produce are Portuguese; the instructions are in English. Template placeholders in square brackets say what to write.

## Table of Contents

1. [Base structure](#1-base-structure)
2. [Content rules](#2-content-rules)
3. [Length](#3-length)
4. [Template: incident report (postmortem)](#4-template-incident-report-postmortem)
5. [Template: investigation or diagnosis](#5-template-investigation-or-diagnosis)
6. [Template: technical analysis with recommendation](#6-template-technical-analysis-with-recommendation)
7. [Template: project status](#7-template-project-status)
8. [Template: agent task report](#8-template-agent-task-report)
9. [Tables, figures, and evidence](#9-tables-figures-and-evidence)
10. [Final check](#10-final-check)

## 1. Base structure

Use this order when the type of report has no template of its own. Cut a section that would be empty.

```markdown
# [Título: o objeto e o resultado. Ex.: "Falha de login em 2026-03-14: certificado expirado"]

## Resumo
[2 a 5 frases. Conclusão, impacto com número, ação pedida ao leitor. Quem ler só isto consegue decidir.]

## Contexto
[O que o leitor precisa saber para entender o resto. Escopo: o que entrou e o que ficou de fora.]

## O que foi verificado
[Fatos, cada um com a fonte: arquivo:linha, comando, log, medição, data.]

## Análise
[Inferências. Cada uma aponta os fatos em que se apoia. Hipóteses descartadas e o motivo.]

## Recomendações
[Lista numerada. Cada item: ação, responsável, prazo. Sem dado: `[a confirmar: …]`.]

## Limitações e pendências
[O que não foi verificado e por quê. Riscos que restam. Perguntas em aberto.]

## Anexos
[Saída bruta de comando, tabela longa, consulta SQL, glossário.]
```

## 2. Content rules

- **The summary stands alone.** It does not say "este relatório apresenta". It says the result.
- **A section title informs.** "Causa: timeout de 5 s no gateway" informs more than "Análise".
- **Fact and inference in separate sections**, or marked in the sentence. The reader needs to tell "medi" (I measured) from "deduzi" (I deduced).
- **Every cause statement carries the evidence and the degree of certainty.** Use three degrees and keep the terms. `confirmado` (confirmed): the investigation showed the mechanism, or a controlled intervention isolated the cause (the defect goes away when only that cause is removed and comes back when it is restored). `provável` (probable): the evidence points to the cause, without isolating it. `hipótese` (hypothesis): compatible with the facts, with no direct evidence. Measuring the symptom shows that the problem exists and leaves the cause open.
- **Every number has a unit, a period, and a source.** "Erro em 3,2 % das requisições entre 14h00 e 14h30 (painel `api-gateway`, 2026-03-14)."
- **A negative result goes in.** "Procurei X em Y e não encontrei" is information. Say where you looked.
- **A recommendation is an action.** "Aumente o timeout para 15 s em `config/http.yaml`" is an action. "Rever a estratégia de timeout" is not.
- **No blame on a person.** Describe the action and the system: "o deploy ocorreu sem a migração", not "fulano esqueceu a migração".
- **Verb tense.** What happened: pretérito perfeito. How the system behaves: present. What to do: imperative.
- **Do not narrate your process**, unless the method affects the confidence in the result. In that case, a short method section is enough.

## 3. Length

Write the length that the decision needs. A diagnosis of one bug fits in 10 lines. Do not fill a whole template for a small subject: use only Resumo, Evidência, and Próximo passo. Detail that only part of the readers want goes in an appendix.

## 4. Template: incident report (postmortem)

```markdown
# Incidente [ID]: [o que falhou] em [data ISO]

## Resumo
[O que falhou, por quanto tempo, quem foi afetado e quanto, causa em uma frase com o grau de certeza, estado atual.]

## Impacto
- Duração: [início] a [fim], [fuso] ([N] min)
- Usuários ou sistemas afetados: [número e fonte]
- Efeito: [o que deixou de funcionar]
- Perda de dados: [sim, quanto / não / a confirmar]

## Linha do tempo
| Hora ([fuso]) | Evento | Fonte |
|---|---|---|
| 14h02 | O alerta `HighErrorRate` disparou | Alertmanager |

## Causa
[Causa raiz e grau: confirmado / provável / hipótese. Evidência. Fatores que contribuíram.]

## Detecção e resposta
[Como o time detectou. Tempo até detectar e até mitigar. O que funcionou e o que atrasou.]

## Correção aplicada
[O que mudou, onde, quando. Comando ou PR.]

## Ações
| # | Ação | Responsável | Prazo | Tipo |
|---|---|---|---|---|
| 1 | [verbo + objeto] | [nome ou `[a confirmar]`] | [data] | prevenir / detectar / mitigar |

## Pendências
[O que ainda não se sabe.]
```

The timeline is the only place where chronological order rules. Each row has one event and one source. The passive is acceptable when the author of the action is unknown.

## 5. Template: investigation or diagnosis

```markdown
# [Sintoma investigado]

## Conclusão
[Causa, grau de certeza e próximo passo.]

## Sintoma
[O que acontece, onde, desde quando, com que frequência. Como reproduzir.]

## Evidência
1. [Fato + fonte]
2. [Fato + fonte]

## Hipóteses
| Hipótese | Situação | Evidência |
|---|---|---|
| Cache desatualizado | descartada | O erro ocorre com `CACHE=off` |
| Timeout do gateway | provável | 38 de 40 erros têm `ETIMEDOUT` |

## Próximo passo
[Uma ação. Como saber se ela resolveu.]

## Não verificado
[Lista.]
```

## 6. Template: technical analysis with recommendation

```markdown
# [Decisão a tomar]

## Recomendação
[A opção recomendada e o motivo principal, em até 3 frases. O que o leitor precisa aprovar.]

## Critérios
[Lista dos critérios e do peso de cada um. Quem definiu.]

## Opções
| Critério | Opção A | Opção B | Opção C |
|---|---|---|---|
| Custo mensal | R$ 1.200 | R$ 3.400 | R$ 0 |

## Análise
[Um parágrafo por opção: o que ela resolve, o que ela não resolve, o risco.]

## Riscos da recomendação
[Risco, probabilidade, o que fazer se ocorrer.]

## Premissas e lacunas
[O que foi suposto. O que mudaria a recomendação.]
```

Use the same criteria, in the same order, for all options. A cell with no data receives `[a confirmar]`, not an adjective.

## 7. Template: project status

```markdown
# Status: [projeto], [data ISO]

**Situação:** [no prazo / em risco / atrasado] — [motivo em uma frase]

## Concluído desde [data do último status]
- [Entrega verificável]

## Em andamento
- [Item]: [% ou etapa], previsão [data]

## Bloqueios
- [Bloqueio]: [quem pode remover], [o que você precisa dessa pessoa]

## Próximos passos até [data]
- [Ação] ([responsável])

## Decisões pedidas
- [Pergunta que o leitor precisa responder, com as opções]
```

"Concluído" (done) lists a deliverable that someone can check, not an activity. "Trabalhamos na API" is an activity. "O endpoint `POST /pedidos` está em homologação" is a deliverable.

## 8. Template: agent task report

For the summary that an agent (Claude Code, Codex, Antigravity, OpenCode) delivers at the end of a task.

```markdown
[Resultado em 1 ou 2 frases: o que está feito e se funciona.]

**Alterado**
- `caminho/arquivo.ext`: [o que mudou e por quê]

**Verificado**
- [Comando executado] → [resultado, com números]

**Não verificado**
- [O que ficou sem teste e o motivo]

**Pendente para você**
- [Decisão ou ação que depende do usuário]
```

- If a test fails, say that it fails and paste the error line.
- If you skipped a step, say which one.
- Do not say "tudo certo" without saying what you checked.
- Cut the empty section. A small task fits in two sentences, with no headings.

## 9. Tables, figures, and evidence

- A table to compare items by the same attributes. Prose to explain a cause relation.
- Each numeric column carries the unit in the header.
- Code block for command, output, log, and configuration. Copy the output as it came. If you cut it, mark `[…]`.
- Code reference in the format `caminho/arquivo.ext:linha`.
- A chart only when the shape of the curve is the argument. The chart title states the conclusion.

## 10. Final check

1. Can a reader who reads only the summary decide?
2. Does each cause statement have evidence and a degree of certainty?
3. Does each number have a unit, a period, and a source?
4. Is what was not verified written down?
5. Does each recommendation have an action, an owner, and a deadline, or an `[a confirmar]` marker?
6. Are the terms the same from start to end?
7. Can any passage go without losing a fact? Cut it.
