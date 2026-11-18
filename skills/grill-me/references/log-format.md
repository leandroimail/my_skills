# Log format

File: `<cwd>/.grill/<slug>.md`, where `<slug>` is a kebab-case summary of the topic. Create the directory only when there is something to write.

The log is the distilled output, not a transcript: conclusions and the reasoning behind them. **Delete any section that is empty.** Do not leave "TBD".

```markdown
# Grill: <topic>
Date: <ISO date>
Mode: <interview | ideation | both>
Confirmed: <ISO date the user confirmed the shared understanding, or "no">

## Intent
What the user is trying to achieve, in their words, refined.

## Constraints
Non-negotiables.

## Anti-goals
What would make this a failure even if it works.

## Key decisions
- Decision: <what>. Reason: <why>. Rejected: <alternative>. Source: <file or document, when the decision rests on a project fact>.

## Options considered
- <direction>: <what it trades off>. <chosen | dropped: why>.

## My calls (unconfirmed)
- <default the agent chose>. Reason: <why>.

## Terms
- <term>: <meaning agreed>. Avoid: <words that mean something else>.

## Surfaced assumptions
Things the user was assuming, now explicit.

## Prototype verdicts
- Question: <what the prototype was built to answer>. Verdict: <what it showed>.

## Left to the builder
Choices deliberately not made here.

## Open questions
What the user could not answer yet.

## Out of scope
What the user chose not to do.
```

## What goes where

- A choice the user made: `Key decisions`.
- A choice the agent made and the user has not confirmed: `My calls (unconfirmed)`.
- A fact found in the project ("`refund()` is idempotent"): never its own entry. It is the `Source` or the `Reason` of the decision or call it supports.
- Something noticed but not asked for: `Open questions`.

## Lifecycle of a call

1. The agent makes a reversible choice with an obvious default and states it in a message. It goes under `My calls (unconfirmed)`.
2. If the user rejects it, replace it with the user's decision under `Key decisions`.
3. When the user confirms the shared understanding, move every call that was on the table at that moment into `Key decisions` and set `Confirmed` to that date.
4. Anything added after that date stays under `My calls (unconfirmed)` until a new confirmation.

## Resuming from a log

- A decision under `Key decisions` in a confirmed log stands. Do not ask it again.
- A decision that the code does not implement yet is pending work, not a conflict.
- Reopen a decision only when new evidence removes its stated reason. Show the evidence.
- Present `My calls (unconfirmed)` again.
