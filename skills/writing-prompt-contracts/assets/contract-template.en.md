<GOAL in 1 or 2 sentences: what to build or change, and for whom.> <What is enough: "It only needs to ...". What is not needed: ...>

PRIORITIES (in this order when they conflict)
1. <e.g.: Do not break what exists: the current tests keep passing>
2. <e.g.: Data integrity>
3. <e.g.: Performance on target>
4. <e.g.: Small diff>

CONTEXT
- Repository: <path>. Read the code and the test tooling before changing anything, starting with: <files>.
- Pattern to follow: <file or module that already does something similar>.
- Known: <facts>. Already ruled out: <hypothesis and reason>.
- Open hypothesis: <X>. Confirm or rule out <X> before building on it.
- Open items: for each `[to confirm: ... Default: ...]`, use the default and list it in the report. For a `BLOCKING` item, do only <work allowed without the answer> and stop with a "not done" report.

CONSTRAINTS
- <checkable constraint>. Reason: <why>.
- Do not change: <modules, schema, public contracts, deploy configuration>.
- Do not change the gate files: <fixtures, scenarios, verification scripts>.
- Do not add a new dependency without stating the reason in the final report.

TARGET
- Target environment: <runtime, database, browser, with versions>.
- Budget: <metric with number, unit, and measurement condition. E.g.: p95 ≤ 300 ms at 50 req/s for 60 s>. Every number in this section has a gate in VERIFICATION that measures it and reports it.

ENVIRONMENT
- Available tools: <e.g.: Node 20, Playwright, k6, read access to the DEV database through the `<NAME>` variable>.
- Write scripts, outputs, and evidence to `<work-folder>/`.
- Shared environment: <what the agent must not do. E.g.: close only the processes you opened, do not write to staging>.

REQUIREMENTS
- <observable behavior>
- <business rule>
- <edge case and the expected result>
- <property, not implementation. E.g.: "no query does a full scan on <table>">

INTERFACE
<routes, payloads, error codes, screens, commands, flags>

VERIFICATION
- Tests: `<command>` exits with code 0. Fixed scenarios: <list or file>. Every requirement and every INTERFACE element has at least one scenario that triggers it and checks the effect.
- Regression: <the existing tests keep passing. Outputs that must stay identical to the current ones>.
- Performance: `<command>`. Report mean, p95, p99, and max. <In a shared environment: measure before and after the change, under the same conditions. The after must not be worse than the before beyond measurement noise.>
- Isolated reviewer:
  - Write only raw outputs to `<evidence-folder>/`: <scenario responses, screenshots, logs>. Do not put your comments or justifications in that folder.
  - Every round, start a new subagent that does not inherit this conversation. Give it ONLY: REQUIREMENTS, INTERFACE, the reference `<benchmark: design, legacy screen, expected responses>`, the file list of `<evidence-folder>/`, and the scale below. Send no explanation of what is intentional. Tell the reviewer to read no other file.
  - Reason: whoever reads the builder's code, reasoning, or justifications tends to accept what the builder intended.
  - The reviewer compares the outputs with the reference and returns concrete defects, ordered by severity:
    - blocker: <violates a requirement, the INTERFACE, or a constraint>
    - major: <a user notices it in normal use>
    - minor: <only shows in a side-by-side comparison with the reference>
  - Iterate until the reviewer reports nothing above "minor".

IF A GATE DOES NOT PASS
- Do not weaken the gate. Do not delete a test, do not mark it `skip`, do not raise a limit, do not change the criterion.
- Limit: at most <R> reviewer rounds and <T> hours of work. Stop earlier if <N> consecutive rounds do not reduce the blocker and major defects.
- When you stop without passing, deliver a "not done" report: the failing gate, the evidence, the remaining defects, and the hypotheses.

DONE WHEN all gates pass. Deliver:
- <diff or PR>
- `<work-folder>/report.md` with the result of each gate and the command output
- the performance report
- the final review of the isolated reviewer
- the verification scripts, versioned for the next contracts
- what was not verified, and why
