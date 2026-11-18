# The ten rules in detail (pt-BR)

Each rule gives the reason, the test to apply, and examples. The text is in English; the examples are Portuguese because Portuguese is the object of the rules. Examples marked "Antes" (before) contain errors on purpose.

Every datum that appears only in the "Depois" (after) of an example came from a source that the example does not show: a log, a measurement, or the author's answer. Without that source, keep the original expression and add `[a confirmar: …]`. The marker adds a question and keeps the partial information in the sentence.

## Table of Contents

1. [The conclusion comes first](#1-the-conclusion-comes-first)
2. [The actor appears](#2-the-actor-appears)
3. [One idea per sentence, one verb form](#3-one-idea-per-sentence-one-verb-form)
4. [Modality and uncertainty](#4-modality-and-uncertainty)
5. [Fact, inference, and gap](#5-fact-inference-and-gap)
6. [Numbers and names instead of adjectives](#6-numbers-and-names-instead-of-adjectives)
7. [Full verb and simple word](#7-full-verb-and-simple-word)
8. [One term per concept](#8-one-term-per-concept)
9. [Flat syntax](#9-flat-syntax)
10. [No noise](#10-no-noise)
11. [The `leitor: agente` (agent reader) flag](#11-the-leitor-agente-agent-reader-flag)
12. [Level matrix](#12-level-matrix)

---

## 1. The conclusion comes first

**Reason.** A technical reader decides from the start of the text whether to keep reading. An agent can receive the text truncated. In both cases, what is at the end may not be read.

**Test.** Delete everything after the first sentence of each section. Does the reader still know the result or the action?

- Order from known to new and from the common case to the exception.
- A heading describes the content ("Causa da falha"), not the role in the document ("Análise").
- Supporting detail goes at the end or in an appendix.
- Do not narrate the investigation in chronological order, unless the genre is a timeline.

| Antes | Depois |
|---|---|
| "Primeiro olhei os logs, depois o código, e por fim percebi que o timeout estava baixo." | "A causa provável das falhas é o timeout de 5 s em `config/http.yaml`. Evidência: 38 de 40 erros no log têm `ETIMEDOUT`. A lentidão do serviço externo ainda não foi descartada." |

## 2. The actor appears

**Reason.** Portuguese third person serves for "ele", "ela", "você", "o sistema", and "o usuário". Without a subject, the reader picks one.

- Explicit subject in every finite clause. The exception is the imperative addressed to the reader.
- In a coordination with the same subject, do not repeat it. If the subject changes, split into two sentences.
- **`-se` test**: if the sentence accepts "é/são + participle" without changing the meaning, the `-se` is a passive marker. In `estrito`, replace it. In `descritivo`, accept it when there is no relevant actor. A true pronominal verb ("conectar-se", "referir-se") passes.
- Avoid a third-person pronoun that points to another sentence ("ele", "o", "lhe", "o mesmo", "este último"). Repeat the noun.
- Avoid mesoclisis ("far-se-á").
- **The actor comes from the source.** Name the actor only when the text or the context identifies it. Use the imperative for the action that the source assigns to the reader, such as a step of a procedure that the reader executes. An event or a state stays an event or a state: "o serviço foi reiniciado" does not become an order and does not get an author. With no known actor, use `[a confirmar: quem faz X?]`.
- The passive is acceptable in `descritivo` when the actor is unknown or irrelevant ("O servidor foi desligado às 02h10" in a timeline with no known author).

| Antes | Depois |
|---|---|
| "Envia o e-mail e atualiza o status." | Se a fonte diz que é o serviço: "O serviço envia o e-mail e atualiza o status." Se não diz: "`[a confirmar: quem?]` envia o e-mail e atualiza o status." |
| "A configuração usa o certificado padrão. Ele expira em 90 dias." | "A configuração usa o certificado padrão. O certificado padrão expira em 90 dias." |
| "Segue anexo o relatório." | "O relatório está anexado." |

## 3. One idea per sentence, one verb form

- **Instruction**: imperative in the "você" form ("Clique", "Execute", "Confirme"). No "deve-se", no "por favor", no "poderia", no infinitive as an order.
- **Behavior description**: present indicative, third person ("O endpoint retorna 404").
- **Report of what happened**: pretérito perfeito ("O deploy falhou às 14h02").
- A list uses one form only. A list that mixes "Abrir o painel" with "Clique em Salvar" is a common error in runbooks.
- **Gerund**: it stays in the periphrasis with "estar" that marks an action in progress ("O job está processando a fila", "O backup está sendo validado"). Replacing it with "está validado" would change progress into completion. The gerund goes away when it links two clauses and in "gerundismo" ("vamos estar enviando o boleto" becomes "vamos enviar o boleto"). Check first: "amanhã, às 14h, o serviço vai estar processando a fila" marks an action in progress at a moment in time and stays.
- **Non-restrictive relative clause** (between commas): in `estrito`, make it a separate sentence. The comma changes the scope without the reader noticing. "Reinicie os pods que falharam" restricts. "Reinicie os pods, que falharam" states that all of them failed.
- "Onde" only for a physical place. In the other cases, "em que".

| Antes | Depois |
|---|---|
| "Execute o script, gerando o relatório." | Finalidade: "Execute o script para gerar o relatório." Consequência: "Execute o script. O script gera o relatório." |
| "1. Abrir o painel. 2. Clique em Salvar." | "1. Abra o painel. 2. Clique em Salvar." |

## 4. Modality and uncertainty

| Word | Only allowed meaning | Replaces |
|---|---|---|
| `deve` | obligation | deverá, há de, é necessário que |
| `pode` | permission | none |
| `consegue` | technical capability | "pode" used as capability |
| no modal | probability: use "talvez", "provavelmente", or a number | deveria, poderia, deve ser que |

- **Do not inflate certainty.** Choose "funciona" if the evidence supports it and "talvez funcione" if it does not. If the source text does not decide, keep the doubt or use a marker.
- **Cut only the redundant hedge.** "Talvez possa possivelmente ocorrer" says the same doubt three times and becomes "talvez ocorra". Before cutting, check that the word only repeats the doubt: "eventualmente" can mark frequency, and then it stays. Hedges of different types all stay: the source of the evidence, the degree of certainty, the condition of validity, and the exception. "Segundo a simulação, provavelmente funciona apenas sem carga" has three pieces of information and none is redundant.
- **Ambiguous "deve" in the original**: keep the sentence and add `[a confirmar: estimativa ou obrigação?]`. The answer comes from the author.
- **Negation with a quantifier**: "Todos os arquivos não foram enviados" has two readings. Write "Nenhum arquivo foi enviado" or "Parte dos arquivos não foi enviada" according to the source. If the source does not decide, keep the sentence and add `[a confirmar: nenhum ou parte?]`.
- `e/ou` does not exist. Choose "e" or "ou". If it is truly inclusive: "A, B ou os dois".

## 5. Fact, inference, and gap

**Reason.** The reader of a report decides based on it. The decision changes if a statement was measured, deduced, or assumed.

- **Observed fact**: give the source. Use `arquivo:linha`, the command executed, the log excerpt, the run ID, or the date of the measurement.
- **Inference**: mark it with "portanto", "isso indica", "a hipótese é". Say which facts it comes from.
- **Gap**: say what was not verified and why. "Não testei em produção, porque não tenho acesso."
- A test or command result is reported as it came out. If 3 of 40 tests fail, the text says "3 de 40 falham", not "a maioria passa".
- "Estudos mostram", "é sabido que", and "especialistas apontam" need the source or go away.
- A reference without a trace ("conforme alinhado") becomes a checkable reference ("conforme a decisão de 2026-03-14, registrada no PR 412").

| Antes | Depois |
|---|---|
| "A migração funcionou e está tudo ok." | "A migração terminou sem erro (`migrate.log`, 1.204 linhas, nenhuma com `ERROR`). Conferi a contagem de 3 das 12 tabelas. Não conferi as outras 9." |
| "O bug é causado pelo cache." | "A hipótese é que o cache causa o bug: o erro some com `CACHE=off` em 5 de 5 execuções. Não identifiquei a linha responsável." |

## 6. Numbers and names instead of adjectives

- A vague quantifier ("vários", "alguns", "muitos", "a maioria") becomes the number from the source. Without the number, the quantifier stays and gets the marker: "a maioria dos testes `[a confirmar: quantos de quantos?]`".
- A vague deadline ("em breve", "logo", "recentemente") becomes a date or a duration.
- An evaluation adjective ("rápido", "lento", "grande", "estável") becomes the measure with unit and the condition of the measurement.
- A comparison gives both sides: "caiu de 4,2 s para 0,3 s", not "ficou 14x mais rápido" alone.
- Give the direction: "afeta" gives no information. "Aumenta", "reduz", "impede" do.

## 7. Full verb and simple word

- **Light verb**: fazer, realizar, efetuar, proceder a, executar, promover + nominalization. Use the verb: "realizar a validação" becomes "validar".
- "Executar" with a concrete object stays: "execute o script".
- A nominalization that is a domain term stays: "a validação de entrada rejeita CPF inválido".
- Between two words with the same meaning, use the shorter and more common one: "usar", "ter", "pedir", "para".
- One word, one grammatical class within the document.
- An established anglicism stays ("commit", "deploy" as a noun, "backup", "endpoint"). A deformed verb goes away ("deployar", "startar", "setar").

## 8. One term per concept

- The first occurrence defines. The following ones repeat.
- In a long document or in a project, keep a glossary:

| Termo PT | Termo EN | Artigo | Definição em 1 linha | Não usar |
|---|---|---|---|---|
| beneficiário | member | o beneficiário | Pessoa coberta pelo plano | cliente, usuário, paciente |

- Acronym: expanded at the first occurrence, except common ones (CPF, PDF, URL). Fixed gender ("a API", "a URL", "o endpoint"). Plural without apostrophe ("APIs").
- Brazilian variant: arquivo, usuário, tela, equipe, celular, cadastro, aplicativo, gerenciar, planilha, contato, registro.

## 9. Flat syntax

- **The condition and the safety warning open the sentence.** "Se o disco estiver acima de 90%, pare a ingestão." A reader who executes while reading needs the condition before the action.
- **Nothing between verb and object.** A circumstance goes to the start (condition, trigger) or to the end (means, place).
- **Chain of "de/em/para"**: up to 2 nodes in `estrito`, 3 in `descritivo`. A lexicalized term counts as one node ("banco de dados", "chave de API", "tempo de resposta").
- **Adjective after the noun.** The position changes the meaning: "simples teste" (just a test) and "teste simples" (not complex). For the preposed meaning, use another word: "apenas um teste".
- **Modifier in a coordination.** "Os relatórios e planilhas antigos" does not say whether "antigos" applies to both. If the source confirms that it applies to both, write "os relatórios antigos e as planilhas antigas". If it applies only to the spreadsheets, write "as planilhas antigas e os relatórios". Without confirmation, use `[a confirmar: …]`.
- **No semicolon.** Use a full stop.
- **No dash or parentheses to nest a second idea** in the sentence. Make it another sentence.
- **No telegraphic ellipsis.** "Serviço reiniciado, erro persiste" becomes "O serviço foi reiniciado. O erro persiste." If the source says who restarted it, name the actor: "A plantonista reiniciou o serviço."
- **Vertical list** for 3 or more steps, conditions, or items. Numbered if the order matters.
- **Paragraph**: one subject, the subject in the first sentence, up to 6 sentences.

| Antes | Depois |
|---|---|
| "Envie, após validar o token, o pacote ao servidor." | "Valide o token. Envie o pacote ao servidor." |
| "a validação do cadastro do cliente do contrato" | "Valide o cadastro. Esse cadastro pertence ao cliente do contrato." |

## 10. No noise

**Test.** Delete the passage. If no fact, condition, or instruction was lost, the passage was noise.

Categories (the catalog is in the lexicon file listed in SKILL.md):

- Chatbot artifact: greeting, praise of the question, offer of help at the end.
- Metatext: "vale ressaltar", "é importante notar", "neste documento vamos abordar".
- A summary that repeats the short section the reader just read.
- Emphasis without evidence: "sem dúvida", "certamente", "claramente".
- Inflation: "robusto", "crucial", "de ponta", "revolucionário".
- Avoidance of the verb "ser": "atua como", "funciona como", "se configura como".
- Contrast with a negation that nobody stated: "não é só um cache, é uma plataforma".

What stays: a connector that marks a real logical relation, a technical term with its own meaning ("estimador robusto"), first person and social tone in `leve`.

---

## 11. The `leitor: agente` (agent reader) flag

It applies on top of `estrito`. The agent does not have the context of the writer and can receive only an excerpt.

1. Instruction in the imperative. Tool description in the present, third person.
2. No anaphora crosses sentences. Repeat the whole noun phrase.
3. Status is subject + finite verb. "Arquivo enviado" does not say whether it is an event or a state. Write "O agente enviou o arquivo" or "O arquivo está no estado ENVIADO".
4. Give the completion criterion: how the agent knows it is done.
5. Say what to do on failure and what not to do.
6. Give exact names, values, and paths, not descriptions of them. In an instruction for the current session, use the absolute path. In a reusable prompt or document, use a path relative to a root that the text defines, because the absolute path of your machine does not exist on the machine of the next reader.

## 12. Level matrix

| Aspect | `estrito` | `descritivo` | `leve` |
|---|---|---|---|
| Explicit subject | mandatory | mandatory | mandatory |
| Passive `-se` | forbidden | ok without relevant actor | free |
| Passive voice | forbidden | ok without relevant actor | free |
| Propositions per sentence | 1 | 2 if coordinated | free |
| Non-restrictive relative clause | forbidden | 1 per sentence | free |
| Light verb | forbidden | avoid | free |
| Lexicon avoid→use (long word, bureaucratese, slang) | mandatory | mandatory | recommended |
| Chain of "de" | ≤ 2 | ≤ 3 | free |
| Words per sentence | ≤ 25 | ≤ 30 | ≤ 35 |
| Frozen term | mandatory | mandatory | product and process names |
| Vertical list for ≥ 3 items | mandatory | recommended | free |
| Condition opens the sentence | mandatory | mandatory | mandatory |
| First person | avoid | ok to report what you did | ok |
| Uncertainty preserved | mandatory | mandatory | mandatory |
| Fact separated from inference | mandatory | mandatory | mandatory |
