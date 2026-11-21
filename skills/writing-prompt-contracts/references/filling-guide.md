# Prompt contract filling guide

This guide details each section of the contract templates: [`../assets/contract-template.en.md`](../assets/contract-template.en.md) (English) and [`../assets/contract-template.pt-BR.md`](../assets/contract-template.pt-BR.md) (Brazilian Portuguese). Read the section that raises a doubt, or the variants table when the task is not an API.

The rules come from two sources: the Abyssal Garden prompt (by Noniv) and ViktorKav's video of 2026-11-20, which applied the same format to three tasks and measured the results. The video's prompts are at github.com/viktorkav/uno-com-escada.

## Contents

1. [GOAL](#goal)
2. [PRIORITIES](#priorities)
3. [CONTEXT](#context)
4. [CONSTRAINTS](#constraints)
5. [TARGET](#target)
6. [ENVIRONMENT](#environment)
7. [REQUIREMENTS](#requirements)
8. [INTERFACE](#interface)
9. [VERIFICATION](#verification)
10. [Who writes the gates](#who-writes-the-gates)
11. [Open items and defaults](#open-items-and-defaults)
12. [Domain risks](#domain-risks)
13. [Length and omitted sections](#length-and-omitted-sections)
14. [Reviewer isolation](#reviewer-isolation)
15. [Severity scale](#severity-scale)
16. [IF A GATE DOES NOT PASS](#if-a-gate-does-not-pass)
17. [DONE WHEN](#done-when)
18. [Follow-up contracts](#follow-up-contracts)
19. [Cost](#cost)
20. [Portuguese headings](#portuguese-headings)

## GOAL

Write the result in 1 or 2 sentences. Then write what is enough and what is not needed.

- Test: a colleague reads only this sentence and knows what they will receive.
- Bad: "Build a robust, scalable authorizations API."
- Good: "Build the endpoint that lists a member's authorizations for the service desk screen. It only needs to read. It does not need caching, cursor pagination, or writes."
- Close the details that would stay open. In the video, "an Uno" became "a two-door 1996 Uno Mille EP". In software, "the report" becomes "the monthly billing CSV that finance receives on the 5th".

## PRIORITIES

List 3 to 5 qualities, in order. The order settles conflicts.

- Test: for each pair, there is a decision where the two compete. If they never compete, one of them does not belong in the list.
- Bad: "Quality, performance, and security." Without an order, the list breaks no tie.
- Good: "1. Do not break what exists. 2. Data integrity. 3. p95 within target. 4. Small diff."
- Without an order, the model settles every conflict the same way. In the video, in a batch of prompts with no priorities, the model chose visuals every time, and the page of one of the pieces stuttered on an M4 Max.

## CONTEXT

The Abyssal Garden prompt has no such section, because it started from scratch. In existing code, it is mandatory.

- Say where the files are and which module already does something similar. The agent copies the pattern the contract points to.
- Tell the agent to read the code and the test tooling before changing anything.
- Say what was already ruled out and why. This keeps the agent from repeating the investigation.
- Hand over a hypothesis as a hypothesis: "The hypothesis is X. Confirm or rule out X." A hypothesis written as a fact becomes a premise for the agent.

## CONSTRAINTS

Each constraint closes a shortcut and must be checkable with a yes or no.

- Write the reason for each constraint. The agent applies a rule better when it understands it, including in cases the rule does not mention.
- Include the scope fence: what the agent must not touch.
- List the gate files (fixtures, verification scripts) as files the agent does not change.
- Test: can the constraint be checked with `grep`, with `git diff --stat`, or with a command?
- Bad: "Follow best practices."
- Good: "Do not add a package to `package.json`. Reason: the security pipeline blocks unapproved packages."

## TARGET

Turn "fast", "light", and "scalable" into a number, a unit, and a measurement condition. The Abyssal Garden prompt never says "fast": it says "11 ms average" and "no frame > 16.7 ms".

- Measure the mean and the tail (p95, p99, max). The mean hides the stalls users feel.
- Every number needs a gate that measures it and a report that shows it. In the video, a 30 MB memory target was written in the prompt, nobody was in charge of measuring it, and the result used 129 to 136 MB.
- Bad: "It has to be fast."
- Good: "p95 ≤ 300 ms and max ≤ 1 s, at 50 req/s for 60 s, against the staging database."
- With no number from the user: write `[to confirm: what p95 is acceptable, under what load?]`. You can add a proposal, marked as a proposal.

## ENVIRONMENT

TARGET says where the result has to run. ENVIRONMENT says where the agent works. The video's prompts have this block, and the Abyssal Garden prompt does not.

- List the available tools, with a path when the agent would not find them alone: runtime, Playwright, k6, database client, credential environment variables.
- Set the work folder for scripts, outputs, and evidence. This avoids loose files in the repository and keeps the evidence in one place.
- Write the rules for a shared environment. Example from one of the video's prompts: "close only the browsers you opened yourself, through Playwright, and never kill Chrome processes by name". In software: do not write to staging, do not run load above X, do not stop other teams' containers.

## REQUIREMENTS

Write observable behaviors, one per line. The isolated reviewer checks each line without reading the code.

- Include the edge cases with the expected result.
- When possible, describe a property and leave the implementation to the agent. The original does this with "bounded, but the boundaries can't be visible from the starting area".
- A business rule the user did not confirm stays as `[to confirm: ...]`. Example: "Member with two active plans: one row per member or one row per plan? `[to confirm]`".
- Bad: "Handle errors."
- Good: "Unknown member: HTTP 404 with `code: MEMBER_NOT_FOUND`."

## INTERFACE

Write the exact contract: route, payload, error codes, screen name, keys, flags. An ambiguous interface produces an implementation the reviewer cannot judge.

## VERIFICATION

This section carries the most weight. Each gate needs a command or a tool that runs in the user's environment. If the gate does not run, it is not a gate.

Rules:

- Use the commands that exist in the repository (`package.json`, `Makefile`, CI pipeline). Do not invent scripts.
- Fix the inputs: scenarios, fixtures, seeds. Fixed inputs keep the iterations comparable.
- Every requirement and every INTERFACE element needs at least one scenario that triggers it and checks the effect. The video's circuit prompt adds "an automated test that presses each key and checks the effect" (translated). In software, the equivalent is one test per route, per flag, or per button.
- A structural test is not enough. In the video, a 3D file passed all six automated tests, because the solid was valid, and its shape was wrong. At least one gate compares the observable result with a reference.
- Include evidence of runtime behavior, beyond unit tests: a Playwright trace, a log, a query execution plan.

Variants by task type:

| Task type | Objective gate | What the isolated reviewer receives |
|---|---|---|
| API | Unit and e2e tests with fixed scenarios, latency benchmark | REQUIREMENTS, INTERFACE, the HTTP responses of each scenario, and the expected responses |
| Screen | Playwright tests, screenshots at fixed widths, key dimensions measured from the reference before coding and checked with a pixel tolerance, no horizontal overflow | REQUIREMENTS, the visual reference (design or legacy screen), and the screenshots. Here the Abyssal Garden visual critic applies unchanged. |
| Bug fix | The scenario that reproduces the bug fails before the fix and passes after it | The bug report and the scenario output before and after |
| Refactor | Characterization tests written before the change pass unchanged | The test output before and after, and `git diff --stat` |
| SQL query | Same result as the old query on N fixed cases, execution plan without full scans | The compared results and the execution plan |
| Migration | Output equivalence between the old and the new system on fixed cases | The comparison table |

## Who writes the gates

An agent that writes its own tests also chooses its own exam. In Abyssal Garden, the agent chose the camera poses and the flight path, and the world was laid out around that path. Defects outside the poses got through.

Order of preference:

1. Gates that already exist in the repository or in the pipeline.
2. Gates the user writes before the task.
3. Gates the agent writes as the first deliverable of the contract. The agent writes the scenarios before any code. Then one of two things happens:
   - The user is available: the agent stops and asks for approval. After approval, the scenario files join the list of files the agent does not change.
   - The user is not available: the agent freezes the scenarios instead of waiting. A new isolated reviewer checks the scenarios against REQUIREMENTS only, the agent fixes what the reviewer reports, and then records the scenario files (path and hash) in the report as files it does not change. Only after the freeze does the agent write code. An approval stop in a contract that nobody will answer makes the agent wait for nobody.

Verification scripts become part of the project. In Abyssal Garden, the scripted flight and the benchmark stayed in the code as the `F` and `B` keys. Version these scripts so the next contract can reuse them.

## Open items and defaults

An open item is a question the user did not answer. Mark it where it matters, in one short line, and put the numbered list with context in the reply to the user, not in the contract.

| Kind | When | Marker | What the agent does |
|---|---|---|---|
| Non-blocking | A safe default exists | `[to confirm: <question> Default: <value>]` | Uses the default and lists it in its report |
| Blocking | The answer changes what gets built and is costly to undo: billing, legal, security, data deletion | `[to confirm: <question> BLOCKING]` | Does only the work that the contract allows without the answer, then stops with a "not done" report |

Examples:

- Non-blocking: `Viewport height for 390 px [to confirm: Default: 844 px]`.
- Non-blocking: `Round cap [to confirm: Default: 5 rounds, 2 hours]`.
- Blocking: `Amount billed for a member with two active plans [to confirm: which plan and which amount? BLOCKING]. Without the answer: reproduce the bug, write the scenarios with the expected amount left open, and stop.`

## Domain risks

A generic contract checks structure. The risks below are where real tasks fail, and the reviewer checks only what the contract states. Go through the list, and for each risk that applies, write one requirement, one constraint, or one fixed scenario.

| Risk | What to pin down | Example line |
|---|---|---|
| Dates, time zones, windows | Time zone, window start and end, inclusive or exclusive ends, date format on the wire, driver conversions | "The 30-day window starts at 00:00 America/Fortaleza today and excludes day 31. Dates go out as `YYYY-MM-DD`." |
| Money and amounts | Which amount, rounding, currency, totals that must match | "The scenarios compare `vl_mensalidade` per row, not only the row count." |
| Personal or sensitive data | What may appear in queries, logs, fixtures, screenshots, and evidence (LGPD, GDPR) | "Fixtures and evidence use fictitious members only. Logs carry ids, never names." |
| Authentication and authorization | Which role, what happens without a token, with an expired token, with the wrong role | "Token without the `atendimento` role: HTTP 403, covered by a scenario." |
| Outputs that other systems consume | Column order, field names, formats, encodings that a spreadsheet or another service depends on | "The CSV keeps the current columns in the current order." |
| Concurrency and idempotency | Repeated requests, retries, parallel runs | "Running the job twice for the same month produces the same file." |
| Volume, pagination, limits | Largest realistic input, page size limits, timeouts | "Scenario with 500 authorizations, and `size=101` returns HTTP 400." |
| Encoding and locale | Accents, decimal comma, sorting with accents | "Names with accents keep their accents in the CSV (UTF-8)." |
| Visual fidelity | Measurable checks beyond the critic's opinion | "Key dimensions measured from the PNG match within 2 px. No horizontal scroll at 390 px." |
| Shared environments | Load limits, writes, processes, connections | "No load above 20 req/s on DEV. Close the connections you open." |

## Length and omitted sections

- Do not delete a section silently. When a section does not apply, keep its heading with a one-line reason, for example `TARGET: does not apply. Reason: the change only fixes row selection.`
- Aim for 400 to 800 words and stay under 1,000, not counting code blocks. The linter warns above 1,000. The cap is a ceiling, not a target.
- Budgets per section: GOAL at most 3 sentences, PRIORITIES at most 5 lines, CONTEXT at most 6 bullets, CONSTRAINTS at most 8 bullets, REQUIREMENTS one line per behavior.
- When the contract runs long, cut explanation before you cut conditions. Keep each requirement in REQUIREMENTS, and let an open-item marker carry only the open question and its default.

## Reviewer isolation

The video sums up the rule as "whoever checks cannot be whoever built it". The isolated reviewer depends on the harness being able to start subagents. A new subagent does not know the conversation, but it usually has file tools and can open the code. Isolation also fails another way: in the video's test, the agent sent the critic notes along with the images, such as "the neutral background is on purpose", and the last critic accepted the explanation.

That is why the template's clause:

1. has the builder write only raw outputs to an evidence folder, with no comments or justifications.
2. starts a new subagent every round, without inheriting the conversation, so that a reviewer does not carry what it heard in the previous round.
3. gives the reviewer only REQUIREMENTS, INTERFACE, the reference, the folder's file list, and the severity scale.
4. forbids sending any explanation of what is intentional.
5. tells the reviewer to read no other file.

Give the reviewer a real reference: a design, a legacy screen, expected responses, the output of the old query. Without a reference, the reviewer compares the result with a vague idea. The video shows this with photos of the car: without the photos, the critic compares the result with its own idea of an Uno.

In Claude Code, the subagent is started with the `Agent` tool. Do not use the `fork` type, because a fork inherits the whole conversation context, including the builder's reasoning.

## Severity scale

The stop criterion ("nothing above minor") is stable only if the contract defines the scale. Without a definition, each new reviewer uses its own yardstick.

The video's prompt defines the scale by the effort needed to notice the defect: "severe" is what anyone notices in 1 second, "medium" is noticed by looking carefully, "minor" only shows in a side-by-side comparison. A default scale for software:

- blocker: violates a requirement, the INTERFACE, or a constraint, or exposes data it should not.
- major: a user or a consuming system notices it in normal use.
- minor: only shows in a side-by-side comparison with the reference.

Adapt the examples for each level to the task's domain.

## IF A GATE DOES NOT PASS

The Abyssal Garden prompt has no such section. Without it, a stuck agent tends to weaken the gate to finish.

- Forbid it explicitly: deleting tests, marking them `skip`, raising limits, changing the criterion.
- Set a cap on rounds and on time, and a limit of rounds without progress. In the video, with no cap, neither model closed the criterion: every round, the critic found a new defect. One uncapped run took 7 h 12 min and about US$ 347 at API prices.
- Define progress as a drop in the number of blocker and major defects.
- Ask for a "not done" report when the agent stops without passing. In the video, Opus 5.5 stopped at round 11 and delivered a report saying the task was not done. That is the right behavior.

## DONE WHEN

List the evidence the agent delivers. The video explains what this line does: without it, the model decides when the work is finished, and it usually decides early.

- Ask for a report file with the result of each gate.
- Always include "what was not verified, and why". This item makes the agent declare its gaps.

## Follow-up contracts

When the contract changes something already delivered, the video's follow-up prompt gives the pattern:

- Open by saying what already exists and where the code and the verification tools are. Tell the agent to read both before changing anything.
- Priority 1: "Do not break what exists".
- Repeat the constraints of the previous contract.
- Keep working the hooks that the verification tools use.
- Regression gate: the existing tests keep passing, and the reference outputs stay identical to the current ones.
- In a shared environment, measure performance before and after, under the same conditions, and compare the two. Do not chase an absolute number: the after must not be worse than the before beyond measurement noise.

## Cost

The format trades cost for autonomy. In the video, the same task took 7 minutes and US$ 1.23 as a loose prompt, and 62 minutes and US$ 13 as a contract, with the same model and the same effort. In the YouTuber's own measurement, the contract's result met the performance target (2.2 ms against a target of 8.3 ms average) and still had shape defects that the critic reported and the agent did not fix.

Use a contract when autonomy is worth that cost: a long task, a checkable criterion, nobody available to follow each step. For a short task that someone follows, a direct request costs less.

## Portuguese headings

The pt-BR template already uses these headings and fixed terms. Use the table when you translate a clause or review a pt-BR contract. The linter recognizes both sets of headings.

| English | Portuguese (pt-BR) |
|---|---|
| GOAL (first paragraph, no heading) | OBJETIVO (first paragraph, no heading) |
| PRIORITIES (in this order when they conflict) | PRIORIDADES (nesta ordem quando entrarem em conflito) |
| CONTEXT | CONTEXTO |
| CONSTRAINTS | RESTRIÇÕES |
| TARGET | ALVO |
| ENVIRONMENT | AMBIENTE |
| REQUIREMENTS | REQUISITOS |
| INTERFACE | INTERFACE |
| VERIFICATION | VERIFICAÇÃO |
| IF A GATE DOES NOT PASS | SE UM GATE NÃO PASSAR |
| DONE WHEN | PRONTO QUANDO |
| Reason: | Motivo: |
| Isolated reviewer | Revisor isolado |
| blocker / major / minor | bloqueante / maior / menor |
| "not done" report | relatório "não pronto" |
| `[to confirm: ...]` | `[a confirmar: ...]` |
| Default: | Padrão: |
| BLOCKING | BLOQUEANTE |
| TARGET: does not apply. Reason: ... | ALVO: não se aplica. Motivo: ... |
| Do not break what exists | Não quebrar o que existe |
