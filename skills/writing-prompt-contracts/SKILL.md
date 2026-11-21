---
name: writing-prompt-contracts
description: >
  Interviews the user and writes a prompt contract ("prompt-contrato"): a short,
  verifiable spec that an AI coding agent executes on its own. The contract states
  the goal and what is out of scope, priorities ordered for trade-offs, repository
  context, constraints with reasons, numeric targets, observable requirements, the
  interface, verification gates with runnable commands and an isolated reviewer,
  a rule for gates that fail, and the evidence to deliver. Use whenever the user
  wants to write, fill, improve or review a prompt, brief or spec that an agent
  will implement (feature, endpoint, bug fix, refactor, migration, screen), or says
  "prompt-contrato", "contrato de prompt", "escreve o prompt pro agente",
  "especifica a tarefa pro Claude", "preenche o template", "prompt estilo Abyssal
  Garden", even if they do not name this skill. Writes the contract only and does
  not implement the task.
compatibility: >
  The bundled linter needs Python 3.8 or later (standard library only, no network).
  Everything else is plain Markdown and works in any agent that reads skills.
---

# Writing Prompt Contracts

## Purpose

A prompt contract turns "build X, and make it good" into a task that an agent can verify by itself. The pattern comes from the Abyssal Garden prompt: 314 words that produced the first version of a full WebGPU world, with later prompts adding the menu, sound, and collision. That prompt had no role-play and no motivational adjectives. It worked because every line was a goal, a constraint, a number, a checkable requirement, or a verification step, and because the verification had an isolated critic, fixed inputs, a stop criterion, and a list of evidence to deliver.

That prompt was greenfield. Existing codebases also need three things it did not have: context on where to look, a fence around what must not change, and a rule for when a gate does not pass (without it, a stuck agent tends to weaken the gate to finish).

A later test of the same format (ViktorKav's video of 2026-11-20, prompts at github.com/viktorkav/uno-com-escada) found more gaps, and the template closes them:

- The builder sent the critic notes such as "the neutral background is on purpose", and the last critic accepted them. The reviewer must get the outputs and nothing else, and must be a new subagent every round.
- Without a defined severity scale, "nothing above minor" depends on each reviewer's own judgment.
- Without a real reference (design, legacy screen, expected responses), the reviewer compares the result with a vague idea.
- A target with nobody measuring it is ignored: a written 30 MB memory target ended at 129 to 136 MB.
- Structural tests can pass on a wrong result. A gate has to compare the observable result with the reference, and every interface element needs a test that triggers it and checks the effect.
- With no cap on rounds, neither model closed the criterion (one run took 7 h and about US$ 347 at API prices). A good stop is a report that says "not done".
- The agent needs an environment block: available tools, a work folder, and rules for a shared machine.
- The format costs more: the same task took 62 minutes and US$ 13 as a contract, against 7 minutes and US$ 1.23 as a loose prompt. It buys autonomy, not savings.

This skill interviews the user, fills the contract, checks it, and saves it. It does not execute the contract.

## When To Use

- The user is about to hand a multi-step coding task to an agent and wants the prompt for it.
- The user has a rough request ("the agent needs to build endpoint X") and wants it turned into a contract.
- The user has a draft prompt and wants it reviewed or rewritten against the contract checklist (review mode, at the end of Method).

## When Not To Use

- The requirement is still in discovery (who uses it, what problem it solves). Interview for the requirement first, for example with a requirements-interview skill such as `grill-me`, then come back.
- The change is one line. Writing the contract costs more than it saves.
- No outcome can be checked by a command or a tool. Say so: without a runnable gate, the contract's iteration loop has no stop condition. Offer a plain brief instead.
- The user wants an existing contract executed. The contract itself is the instruction. Follow it.
- The user wants a system prompt for a chatbot or product feature. That is a different genre.

## Inputs

- The task, in the user's words.
- The repository path, if the task touches existing code.
- What already exists to verify the work: test scripts, e2e suites, lint, benchmarks, CI pipeline.
- What only the user knows: priorities, numeric targets, what must not change, business rules.

## Method

### Step 1: Check the fit

Read the request and decide whether a contract pays off (see When Not To Use). If the request is vague about the problem itself, say that and suggest a requirements interview first. A contract built on a guessed requirement makes the agent optimize the wrong thing very efficiently.

### Step 2: Read before asking

If there is a repository, read it before asking anything:

- README, AGENTS.md or CLAUDE.md, and contributing notes, for conventions.
- `package.json`, `pyproject.toml`, `Makefile`, or the build file, for the scripts that really exist (`test`, `test:e2e`, `lint`, `bench`).
- The CI pipeline file, for the gates the team already trusts.
- The module closest to the target, to point at as the pattern to follow.
- Runtime and database versions (`.nvmrc`, `engines`, `requires-python`, docker-compose).

Every question the repository answers is one the user does not have to, and a command copied from the repository is a command that runs. Record what you found with its path so the contract can cite it.

### Step 3: Interview for the gaps

Ask only what the repository could not answer. Ask in rounds of at most four questions, the ones that change the contract most first. Typical gaps:

1. The goal in one or two sentences, what is enough, and what is not needed.
2. The priority order when qualities conflict. Propose an order and ask for confirmation, because confirming is cheaper than composing.
3. The fence: modules, schema, public contracts, or deploy configuration the agent must not touch.
4. Numeric targets, with the measurement condition (load, data size, environment).
5. Business rules, edge cases, and the expected error behavior.
6. Which gates exist, and who writes the missing ones (see "Who writes the gates" in [references/filling-guide.md](references/filling-guide.md)).
7. The reference the reviewer compares against: design, legacy screen, expected responses, the output of the old query.
8. The environment the agent works in: tools available, how it reaches each system (credentials, test data such as a known record id), and what is shared with other people.
9. The budget: maximum reviewer rounds, maximum hours, and how many rounds without progress before the agent stops and reports.

When the user does not know an answer, or says they cannot answer now, do not invent it. Mark the open item at the place in the contract where it matters, and list it in the reply. Open items are of two kinds:

- Non-blocking: a safe default exists. Write `[to confirm: <question> Default: <value>]` (pt-BR: `[a confirmar: <pergunta> Padrão: <valor>]`). The contract tells the agent to use the default and to list it in its report. Most open items are of this kind: limits, viewport sizes, page sizes, round caps, naming.
- Blocking: the answer changes what gets built in a way that is costly to undo, such as a billing rule, a legal or security rule, or a data deletion. Write `[to confirm: <question> BLOCKING]` (pt-BR: `BLOQUEANTE`). The contract says what the agent may do without the answer (read, reproduce, write scenarios, diagnose) and where it stops with a "not done" report.

An invented number or rule becomes a gate that the agent will optimize for, and nobody notices it was a guess. A default is different, because it is visible, labeled, and reported.

When the user says they will not be available while the agent runs, do not put an approval stop in the middle of the contract. The agent would wait for nobody. Use the scenario freeze from "Who writes the gates" in [references/filling-guide.md](references/filling-guide.md) instead.

### Step 4: List the domain risks

Before you fill the template, list the risks of this domain that a generic contract would miss. Turn each risk that applies into a requirement, a constraint, or a fixed scenario, in one line. Do not write an essay about it. The isolated reviewer checks only what the contract states, so a risk that is not written down is a risk that nobody checks.

Go through the "Domain risks" checklist in [references/filling-guide.md](references/filling-guide.md): dates, time zones, and windows; money, rounding, and amounts; personal or sensitive data in queries, logs, fixtures, and evidence; authentication and authorization; outputs that other systems consume; concurrency and idempotency; volume, pagination, and limits; encoding and locale; shared environments. Also close vague nouns: "the report" becomes "the monthly billing CSV that finance receives on the 5th".

### Step 5: Fill the template

Write the contract in the user's language, because the user reviews it and the agent receives it as the user's own instruction. Copy the matching template and fill every section:

- English: [assets/contract-template.en.md](assets/contract-template.en.md)
- Brazilian Portuguese: [assets/contract-template.pt-BR.md](assets/contract-template.pt-BR.md)

For another language, translate the English template and keep its structure. The rules below use the English section names. The "Portuguese headings" table in [references/filling-guide.md](references/filling-guide.md) maps them to pt-BR. The rules, in short:

- GOAL: one or two sentences, plus what is enough and what is not needed.
- PRIORITIES: three to five items, ordered. Each pair must be able to conflict. Otherwise one of them does not belong.
- CONTEXT: files to read first, the pattern file, known facts, ruled-out hypotheses with the reason, and open hypotheses phrased as "confirm or rule out".
- CONSTRAINTS: each one checkable in the artifact and followed by `Reason:`. The agent applies a rule better when it knows why. Include the fence, and list gate files (fixtures, benchmark scripts) as files the agent must not modify.
- TARGET: versions, and each target as number + unit + measurement condition. Measure the mean and the tail (p95, p99, max), because the mean hides the stalls users feel. Every number here needs a gate that measures it and reports it.
- ENVIRONMENT: where the agent works, which is different from where the result runs. Tools and their paths, credential variables, the work folder for scripts and evidence, and rules for shared resources (close only the processes you opened, no writes to shared environments).
- REQUIREMENTS: observable behaviors, one per line, including edge cases and error codes. Prefer a property ("no query does a full scan") to an implementation.
- INTERFACE: the exact contract: routes, payloads, error format, screens, commands.
- VERIFICATION: gates with commands that exist, fixed scenarios that trigger every requirement and every interface element and check the effect, a regression gate, at least one gate that compares the observable result with the reference, the isolated-reviewer clause from the template with a severity scale adapted to the domain, and performance reported as mean, p95, p99, and max.
- IF A GATE DOES NOT PASS: keep the template text and set R (max rounds), T (max hours), and N (rounds without progress).
- DONE WHEN: a report file with the result of each gate, the evidence list, the verification scripts kept for the next contract, and what was not verified and why.

For a follow-up contract on something already delivered, open with what exists and where its verification tools are, make "do not break what exists" priority 1, repeat the previous constraints, and in a shared environment measure performance before and after under the same conditions instead of chasing an absolute number.

Do not delete a section silently. When a section does not apply, keep its heading and write one line with the reason, for example `TARGET: no performance requirement. The change only fixes row selection.` The agent and the reviewer then know that the omission was a decision.

Keep the contract short. Aim for 400 to 800 words and stay under 1,000, not counting code blocks such as the INTERFACE payloads. The linter warns above 1,000. These budgets keep it there:

- GOAL: at most 3 sentences.
- PRIORITIES: at most 5 lines.
- CONTEXT: at most 6 bullets, one line each.
- CONSTRAINTS: at most 8 bullets.
- REQUIREMENTS: one line per behavior. Group the edge cases of one rule on one line.
- VERIFICATION: name each scenario with a short phrase. Keep the reviewer clause as the template has it, without a second explanation.
- Open items: a short marker inline. The numbered list with context goes in the reply, not in the contract.

When the contract still runs long, cut explanation before you cut conditions. A gate needs its conditions, and it does not need prose about them. The 1,000-word cap is a ceiling, not a target. Squeezing a contract to just under it tends to bury requirements inside open-item markers. Write each requirement in REQUIREMENTS, and let the marker carry only the open question and its default. Cut role-play ("you are an expert"), motivational adjectives ("amazing", "robust"), and step-by-step implementation: the contract says what to deliver and how to check it, and leaves the construction to the agent.

The isolated reviewer is the part that is easiest to get wrong, and it leaks in three ways. A fresh subagent has no conversation history, but it usually can still open the repository. The builder can pass its own justifications along with the outputs. A reviewer reused across rounds carries what it heard before. The clause therefore has the builder write only raw outputs to one evidence folder, with no comments. It starts a new subagent every round that does not inherit the conversation (in Claude Code, never the `fork` type). It passes only REQUIREMENTS, INTERFACE, the reference, the file list, and the severity scale, sends no explanation of what is intentional, and tells the reviewer to read nothing else. Keep that clause intact.

For details, bad and good examples per section, and verification variants by task type (API, screen, bug fix, refactor, SQL, migration), read [references/filling-guide.md](references/filling-guide.md). For a fully filled contract, read [references/example-api-nestjs-oracle.en.md](references/example-api-nestjs-oracle.en.md) or its pt-BR version [references/example-api-nestjs-oracle.pt-BR.md](references/example-api-nestjs-oracle.pt-BR.md).

### Step 6: Check the contract

Run the bundled linter on the contract. It works for English and pt-BR and detects the language:

```bash
python scripts/lint_contract.py <repo>/.prompts/<slug>.md
```

Use `python3` where `python` is not Python 3. Fix every ERROR. Read every WARN and fix it, or keep it when the contract has a reason (for example, a section that does not apply). The linter checks structure, not content, so go through the Quality Checklist below as well. Then:

- For each gate command, confirm that it exists and that it runs as written in this environment: the script is defined in the build file, the binary is installed, and the command needs no missing setup (for example, `make` is absent, or `pytest` needs `PYTHONPATH=src`). Write the command that works. Do not run long suites without asking the user.
- Turn each leftover template placeholder (`<...>`) into content or into `[to confirm: ...]`. The linter lists them.
- Write the contract as an instruction for an agent: imperative mood, one idea per sentence, explicit subject, numbers with units, no semicolons. The receiving agent cannot ask what a sentence meant.

### Step 7: Save and hand off

Save the contract to `<repo>/.prompts/<slug>.md`, where `<slug>` is a short kebab-case name taken from the goal. Outside a repository, ask where to save it. If the user cannot answer, use `.prompts/` in the current directory. If the file already exists, ask before overwriting it.

Reply with:

- the path of the contract
- the `[to confirm: ...]` items, as a numbered list with blocking items first and the default of each non-blocking item, so the user can answer them in one message
- how to run it, for example: `Execute the contract in @.prompts/<slug>.md` (in pt-BR: `Execute o contrato em @.prompts/<slug>.md`).

Do not start implementing the task. The user decides when to send the contract, and the open items may change it.

### Review mode

When the user brings an existing prompt, check it against the Quality Checklist. Report the gaps in order of impact (missing verification and missing fence first), then offer the rewritten version in the template format.

## Quality Checklist

- [ ] The goal fits in two sentences and says what is not needed.
- [ ] The priorities are ordered, and each pair can conflict.
- [ ] Each constraint is checkable and has a reason.
- [ ] The fence says what the agent must not touch, including the gate files.
- [ ] Every performance adjective became a number with unit and measurement condition, or a `[to confirm]` item, and every number has a gate that measures it.
- [ ] ENVIRONMENT lists the tools, the work folder, and the rules for shared resources.
- [ ] Each requirement is an observable behavior, and each requirement and interface element is triggered by at least one fixed scenario that checks the effect.
- [ ] Each gate has a command that exists in the user's environment, and at least one gate compares the result with a reference.
- [ ] The isolated reviewer is new every round and gets only the spec, the reference, the evidence file list, and the severity scale, with no builder justification, and is told to read nothing else.
- [ ] The severity scale is defined in the contract.
- [ ] The failing-gate rule forbids weakening the gate, caps rounds and hours, and asks for a "not done" report.
- [ ] The done-when list includes a report per gate, the evidence, and what was not verified.
- [ ] Nothing the user did not say is stated as fact. Open items are marked `[to confirm: ...]`.
- [ ] Each open item is non-blocking with a default, or blocking with a defined stopping point. There is no mid-run approval stop when the user will not be available.
- [ ] Each domain risk that applies became a requirement, a constraint, or a scenario.
- [ ] Each section that does not apply keeps its heading with a one-line reason.
- [ ] The contract has at most 1,000 words outside code blocks.
- [ ] No role-play, motivational adjectives, or implementation steps.

## Outputs

- The contract file at `<repo>/.prompts/<slug>.md` (or the location the user chose).
- A short reply with the path, the numbered `[to confirm]` list, and the command to execute the contract.

## Reference files

| File | Content | When to read |
|---|---|---|
| [assets/contract-template.en.md](assets/contract-template.en.md) | The English skeleton to copy and fill | Step 5, for an English contract |
| [assets/contract-template.pt-BR.md](assets/contract-template.pt-BR.md) | The pt-BR skeleton to copy and fill | Step 5, for a Portuguese contract |
| [references/filling-guide.md](references/filling-guide.md) | Section-by-section guidance with bad and good examples, verification variants by task type, who writes the gates, open items and defaults, the domain-risk checklist, reviewer isolation, severity scale, follow-up contracts, cost, and the Portuguese headings table | Steps 3 to 5: open items, domain risks, a section that raises a doubt, a task type that is not an API, or a pt-BR contract |
| [references/example-api-nestjs-oracle.en.md](references/example-api-nestjs-oracle.en.md) | A fully filled English contract for a NestJS endpoint reading Oracle | Step 5, to calibrate length and level of detail |
| [references/example-api-nestjs-oracle.pt-BR.md](references/example-api-nestjs-oracle.pt-BR.md) | The same contract in pt-BR | Step 5, for a Portuguese contract |
| [scripts/lint_contract.py](scripts/lint_contract.py) | Contract linter for English and pt-BR (standard library only; `--json`, `--selftest`) | Step 6, every time |
