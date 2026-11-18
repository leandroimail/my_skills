# Installation and integration by harness

The skill is a folder with `SKILL.md`, `references/`, and `scripts/`, in the open Agent Skills format. Copy the whole folder: `SKILL.md` points to the files in `references/`.

## Table of Contents

1. [Where to copy the folder](#where-to-copy-the-folder)
2. [Make the style permanent](#make-the-style-permanent)
3. [Block to paste](#block-to-paste)
4. [English version of the block](#english-version-of-the-block)
5. [Origin and credit](#origin-and-credit)

## Where to copy the folder

| Harness | Global folder | Project folder |
|---|---|---|
| Claude Code | `~/.claude/skills/escrita-tecnica-controlada/` | `.claude/skills/escrita-tecnica-controlada/` |
| Codex CLI | `~/.agents/skills/escrita-tecnica-controlada/` | `.agents/skills/escrita-tecnica-controlada/` |
| OpenCode | `~/.config/opencode/skills/escrita-tecnica-controlada/` (also reads `~/.claude/skills/` and `~/.agents/skills/`) | `.opencode/skills/` ou `.agents/skills/` |
| Antigravity, app and `agy` CLI | `~/.gemini/config/skills/escrita-tecnica-controlada/` | `.agents/skills/escrita-tecnica-controlada/` |
| Antigravity, IDE (old path) | `~/.gemini/antigravity/skills/escrita-tecnica-controlada/` | `.agent/skills/escrita-tecnica-controlada/` |
| Cursor | `~/.cursor/skills/escrita-tecnica-controlada/` | `.cursor/skills/escrita-tecnica-controlada/` |
| Copilot CLI, others | `~/.agents/skills/escrita-tecnica-controlada/` | `.agents/skills/escrita-tecnica-controlada/` |
| Claude.ai, desktop app | Zip the folder and upload it under Customize > Skills | none |

The paths in this table were not tested in every harness and they change between versions. The two Antigravity paths come from different sources and neither was checked against the official documentation. After copying, list the skills in the harness. If the skill does not appear, check the documentation of the harness.

This skill has two companions: `escrita` (router) and `humanizer`. The router finds the other skills by name, so install the three folders in the same skills directory.

On Windows, `~` is `C:\Users\<name>`.

## Make the style permanent

A skill loads only when the harness decides that the request matches the description. The descriptions of `escrita`, `escrita-tecnica-controlada`, and `humanizer` cover similar requests, and the harness can load any of the three first. The descriptions alone do not guarantee entry through the router. The block below makes the router the entry point: paste the block into the global instructions file of the harness.

| Harness | Global file | Project file |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `CLAUDE.md` |
| Codex CLI | `~/.codex/AGENTS.md` | `AGENTS.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` | `AGENTS.md` |
| Antigravity (agy) | `~/.gemini/GEMINI.md` | `AGENTS.md` or `.agent/rules/` |
| Cursor | Settings > Rules | `.cursor/rules/escrita-tecnica.mdc` |

The `AGENTS.md` at the project root is read by Codex, OpenCode, Antigravity, Cursor, and Copilot. For a project with several harnesses, one block in `AGENTS.md` is enough. In Claude Code, `CLAUDE.md` can import the file with `@AGENTS.md`.

## Block to paste

The block is Portuguese because it is pasted into instruction files of Portuguese-language projects. Use the English version below for English-language repositories.

```markdown
## Estilo de texto técnico (skill escrita-tecnica-controlada)

Aplique ao escrever texto técnico em português do Brasil ou em inglês: relatório, resumo de tarefa, documentação, README, descrição de PR, commit, mensagem de erro, comentário de código, descrição de ferramenta, prompt e instrução para outro agente. Não aplique a texto criativo, marketing ou conversa informal. Não sacrifique completude nem precisão para encurtar.

Princípios:

1. A conclusão vem primeiro: a primeira frase traz o resultado, a decisão ou a instrução.
2. O conteúdo vem da fonte. Ator, número, causa e prazo que a fonte não dá ficam como `[a confirmar: …]`, e a informação parcial que já existe é mantida.
3. A incerteza do original continua: "provavelmente", "talvez" e "deve" ambíguo ficam como estão até o autor confirmar.
4. Separe o que você verificou, o que você inferiu e o que você não verificou. Cite a fonte: `arquivo:linha`, comando, log.
5. Prefira frase curta, voz ativa, verbo pleno e um termo por conceito. As exceções e os limites por nível estão na skill: termo técnico, citação e rótulo de interface ficam como estão.
6. Corte o trecho que não traz fato, condição nem instrução, como saudação e fecho de chatbot.

Formatos em pt-BR: `1,5 GB`, `10.000`, data `2026-03-14`, hora `14h30`. Em inglês: `1.5 GB`, `10,000`.

Mantenha iguais código, comandos, identificadores, caminhos, URLs, logs, códigos de erro e rótulos de interface.

Ao terminar uma tarefa, relate: o que mudou, o que você verificou (comando e resultado), o que você não verificou, o que depende do usuário. Se um teste falha, diga que falha.

Para escrever, reescrever ou revisar um texto inteiro, carregue primeiro a skill `escrita`. Ela decide entre `escrita-tecnica-controlada`, `humanizer` ou as duas em ordem. Se a skill `escrita` não está instalada, carregue `escrita-tecnica-controlada` para texto técnico. Para documento longo, execute `python "<pasta da skill>/scripts/etc_lint.py" <arquivo>` antes de entregar.
```

## English version of the block

For a repository whose `AGENTS.md` is in English:

```markdown
## Technical writing style (skill escrita-tecnica-controlada)

Apply to technical text in Brazilian Portuguese or English: reports, task summaries, documentation, PR descriptions, commit messages, error messages, code comments, tool descriptions, prompts. Do not apply to creative or marketing text. Do not trade completeness or accuracy for brevity.

1. Put the conclusion first.
2. Content comes from the source. Write `[to confirm: …]` for an actor, number, cause, or date that the source does not give, and keep the partial information that is there.
3. Keep uncertainty. A hedge or an ambiguous "should" stays until the author confirms the meaning.
4. Separate what you verified, what you inferred, and what you did not verify. Give the source: `file:line`, command, log.
5. Prefer short sentences, the active voice, full verbs, and one term for one concept. The skill gives the exceptions and the limits for each level: technical terms, quotations, and UI labels stay as they are.
6. Remove text that carries no fact, condition, or instruction, such as chatbot openers and closers.

Keep code, commands, identifiers, paths, URLs, log lines, error codes, and UI labels unchanged.

To write, rewrite, or review a full text, load the skill `escrita` first. It selects `escrita-tecnica-controlada`, `humanizer`, or the two in sequence. If `escrita` is not installed, load `escrita-tecnica-controlada` for technical text.
```

## Origin and credit

The skill combines ideas from five MIT projects, all derived from `danyuchn/asd-ste100-skill`:

- `kayquer/portugues-tecnico-controlado` (pt-BR: PTC rules, levels, bilingual pipeline)
- `nosportugal/portugues-tecnico-simplificado-skill` (pt-PT: ISO 24495-1, repository editing)
- `g4lb/asd-ste100-hebrew-skill` (modes and linter with mandatory and advisory rules)
- `erwinete/asd-ste100-ru` (integration block for AGENTS.md)
- `jshsinaga/asd-ste100-indonesian-skill` (output with the revised text only)

The text and the dictionary of ASD-STE100 are not part of this skill. Get the standard at asd-ste100.org.
