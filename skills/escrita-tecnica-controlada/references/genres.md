# Short technical genres

How an agent or a person writes each type of everyday technical text. The ten rules apply to all of them. This file shows what changes in each one. The templates and examples are in Portuguese because the text they produce is Portuguese; the instructions are in English.

In the "Antes e Depois" (before and after) examples, every datum that appears only in the "Depois" (limit, size, code, parameter, behavior) came from the code or from the system specification. Without that source, use `[a confirmar: …]`.

## Table of Contents

1. [Technical answer in a conversation](#1-technical-answer-in-a-conversation)
2. [Commit message](#2-commit-message)
3. [PR description](#3-pr-description)
4. [Error and log message](#4-error-and-log-message)
5. [Code comment and docstring](#5-code-comment-and-docstring)
6. [Tool and skill description](#6-tool-and-skill-description)
7. [System prompt and instruction for another agent](#7-system-prompt-and-instruction-for-another-agent)
8. [Procedure and runbook](#8-procedure-and-runbook)
9. [README and documentation](#9-readme-and-documentation)
10. [ADR (decision record)](#10-adr-decision-record)

## 1. Technical answer in a conversation

Level `leve` or `descritivo`.

- The first sentence answers the question. The explanation comes after.
- A yes-or-no question starts with "Sim" or "Não".
- Do not repeat the question, do not praise the question, and do not close with an offer of help.
- Say what you verified and what you assumed.
- If the user has to choose, give the recommendation and the reason, not only the list of options.

| Antes | Depois |
|---|---|
| "Ótima pergunta! Existem várias formas de resolver isso. Vamos analisar cada uma…" | "Use `git revert`. Ele cria um commit novo e preserva o histórico. `git reset --hard` só serve se ninguém baixou o branch." |

## 2. Commit message

- Title: up to 72 characters, no final period. State the effect, not the file. Follow the convention of the repository (for example, Conventional Commits), and the language and verb form of the history. With no history, use the imperative.
- Body: the reason for the change and what it does not cover. The diff already shows the "how".
- No "pequenos ajustes", "melhorias", "correções diversas".

```text
fix(auth): rejeite token com `exp` ausente

O validador aceitava token sem o campo `exp` e o tratava como
sem validade. Agora o validador retorna 401.

Não cobre tokens emitidos antes de 2026-01-10, que usam `expires`.
```

## 3. PR description

Level `descritivo`. The template headings are Portuguese because the PR text is Portuguese.

```markdown
## O que muda
[1 a 3 frases: comportamento antes e depois.]

## Por quê
[O problema, com link para o item de trabalho.]

## Como testar
1. [Passo no imperativo]
2. [Resultado esperado]

## Riscos e o que ficou de fora
[O que pode quebrar. O que este PR não resolve.]
```

- Say what you tested and what you did not test.
- A contract change, a migration, or a new environment variable appears at the top.

## 4. Error and log message

Level `estrito`.

An error message for the user answers three questions: what failed, why (if the system knows), and what to do.

| Antes | Depois |
|---|---|
| "Ops! Algo deu errado." | "O arquivo não foi enviado. O tamanho máximo é 10 MB e o arquivo tem 14 MB. Reduza o arquivo e envie de novo." |
| "Erro ao processar." | "A consulta ao banco excedeu 30 s. Tente de novo. Se o erro continuar, informe o código `DB-TIMEOUT-07`." |

- Neutral tone. Do not blame the user, no exclamation mark, no joke.
- Include the received value and the expected value.
- Do not state a cause that the system does not know: "O servidor não respondeu" is a fact. "O servidor está fora do ar" is an assumption.
- Log: one line, one event, finite verb, identifiers as fields (`pedido_id=812`). The same sentence for the same event, to allow search.
- Before changing the text of an existing message, look for tests and alerts that depend on it.

## 5. Code comment and docstring

- The comment explains the reason. The code already shows what it does.
- Describe the current behavior, not the history ("antes era X, mudei para Y" belongs in the commit).
- Docstring: present tense, third person. The first line says what the function returns or does. Then parameters, return value, exceptions, and side effects.
- If the comment and the code diverge, show the divergence to the user and ask which one is right. Do not change the prose silently.
- Follow the language already used in the comments of the repository.

```python
def calcular_carencia(data_adesao: date, plano: Plano) -> int:
    """Retorna os dias de carência que faltam para o beneficiário.

    Retorna 0 se a carência já terminou. Lança `PlanoInativoError`
    se `plano.ativo` é False.
    """
```

## 6. Tool and skill description

Level `estrito`, reader `agente`. The model decides to use the tool from the description alone.

- First sentence: what the tool does, in the present tense, third person.
- Then: when to use it, when not to use it, what it returns, side effects.
- Each parameter: type, unit, format, default value, example.
- State the limits: maximum size, pagination, what happens on error.

| Antes | Depois |
|---|---|
| "Busca dados do cliente." | "Retorna o cadastro de um beneficiário a partir do CPF. Use para consultar nome, plano e situação. Não retorna histórico de atendimento. Retorna `null` se o CPF não existe. Parâmetro `cpf`: 11 dígitos, sem pontuação." |

## 7. System prompt and instruction for another agent

Level `estrito`, reader `agente`. The receiving agent knows only what is in the text.

Include, in this order:

1. **Goal**: the expected result and what it is for.
2. **Context**: what is already known, what was already ruled out, where the files are. Absolute path in an instruction for the current session. Path relative to a defined root in a reusable prompt.
3. **Scope**: what to do and what not to do.
4. **Completion criterion**: how the agent knows it is done.
5. **Response format**: what to return and in which form.
6. **On failure**: what to do if it cannot finish.

- Explain the reason for each restriction. The agent applies a rule better when it understands it.
- No anaphora between sentences. Repeat the name of the file, the function, the service.
- Do not hand over your hypothesis as a fact. Say "a hipótese é X, confirme ou descarte".

## 8. Procedure and runbook

Level `estrito`.

- Before the steps: goal, prerequisites, estimated time, risk, and how to undo.
- Numbered list. One step, one action, in the imperative.
- The condition opens the step: "Se o comando retornar `0`, vá para o passo 5."
- Safety warning before the dangerous step, not after.
- After each step that changes state, give the expected result and how to check it.
- Command in a code block, ready to copy. A value that the reader replaces is marked: `<nome-do-servico>`.

```markdown
3. **Atenção:** o passo 4 apaga os dados da fila. Confirme que o backup do passo 2 terminou.
4. Execute:
   ```bash
   rabbitmqctl purge_queue <nome-da-fila>
   ```
   Resultado esperado: `Purging queue '<nome-da-fila>' ...` seguido do número de mensagens removidas.
```

## 9. README and documentation

Level `descritivo`.

- The first sentence says what the project does and for whom.
- Order: what it is, how to install, how to use (with an example that works), configuration, how to contribute.
- One type of content per page: tutorial, task guide, reference, or explanation.
- A runnable example is worth more than a paragraph.
- Describe the current behavior. Do not promise what does not exist yet without marking it as planned.

## 10. ADR (decision record)

Level `descritivo`.

```markdown
# ADR-NNN: [decisão, no presente: "Usa PostgreSQL para o cadastro"]

- Situação: proposta / aceita / substituída por ADR-MMM
- Data: [ISO]

## Contexto
[O problema e as restrições. Fatos, com fonte.]

## Decisão
[O que foi decidido, em voz ativa: "O time usa…".]

## Alternativas consideradas
[Cada uma com o motivo da rejeição.]

## Consequências
[O que fica mais fácil. O que fica mais difícil. O que precisa ser revisto e quando.]
```
