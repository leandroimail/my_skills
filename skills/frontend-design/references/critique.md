# Critique

Use this for the final pass on your own build, and when asked to review or polish existing UI. Accessibility and state checks are covered by the quality-floor pass in [SKILL.md](../SKILL.md) and are not repeated here.

## Contents

- Two separate passes
- Reflexes worth examining
- Token trace
- Simplify
- Triage order when polishing
- Reviewing someone else's design

## Two separate passes

Keep the design judgment and the mechanical check apart, because each hides the other's findings.

1. **Design pass.** Look at the rendered result, not the code. Ask: what is the first thing the eye lands on, and is that the right thing? What is this page's thesis, and does the first screen state it? Would this design serve a different product unchanged? What one thing will someone remember?
2. **Mechanical pass.** Go through the token trace below and the quality-floor checklist item by item.

Answer each check with evidence (the selector, the computed value, the screenshot), not with "yes." A check you could not run is reported as not run.

## Reflexes worth examining

These patterns appear in generated design regardless of subject. None is banned. Each is listed with the situation that earns it; if that situation is not yours, replace it.

| Reflex | Earned when |
|---|---|
| A grid of identical icon-title-text cards carrying the whole page | The items really are parallel and equal, and something else on the page provides the hierarchy |
| A card nested inside a card | Almost never; group with spacing or a divider instead |
| Hero built from a big number, a small label, and a row of stats | The number is the story and is real |
| An eyebrow label above every heading | The label adds information the heading does not carry |
| Section numbers (01, 02, 03) | The content is a true sequence |
| Gradient-filled headline text | The gradient is part of the brand, not a finish |
| Blur and glass panels | There is real layered content behind them worth hinting at |
| A thick colored stripe on one side of cards or alerts | The color encodes a category the reader needs, and a second cue backs it up |
| Hard offset shadows | The whole direction is built in that idiom |
| Emoji or Unicode glyphs as icons | The tone is deliberately informal and the set is consistent |
| Monospace for labels and headings | The subject is code, data, or machinery and the face is doing real work |
| Sparklines, progress rings, and stat tiles filled with invented data | There is real data, and the chart answers a question |
| A modal for a task that does not need interruption | The task must be completed or dismissed before anything else makes sense |
| The same fade-and-rise entrance on every section | Rarely; one authored moment does more |
| Light or dark theme chosen by product category | The choice follows where, when, and for how long people use it |

A second-order reflex: avoiding all of the above and landing on the predictable opposite. If the aesthetic can be guessed from the category plus what it is avoiding, it is still a default.

## Token trace

Go through the build and trace each value to the plan:

- Every color maps to a role in the plan (the roles come from the plan). Strays are fixed or justified.
- Every radius, spacing value, and shadow comes from the declared scales.
- Every font family, weight, and size belongs to a named typographic role.
- One user action has one name everywhere it appears: the button, the confirmation, the toast, the menu item.

A matching count proves little, since two wrong colors still count as two. Trace the values themselves.

## Simplify

- Remove anything that says what another element already says: a subtitle restating the title, an intro restating the heading.
- Remove containers that group nothing.
- Keep one primary action per view. Demote or remove duplicates.
- Hide the advanced and the rare behind progressive disclosure, without hiding anything the main task needs.
- Then take one more thing away.

## Triage order when polishing

Fix in this order, because polish on top of a broken flow is wasted:

1. Tasks that are broken, blocked, or misleading, and anything that loses data.
2. Missing states and missing feedback.
3. Flow, hierarchy, and responsive behavior.
4. Visual and motion inconsistency, including drift from the tokens.
5. Code cleanup.

Fix layout and proportion before type, spacing, and color; the later ones depend on the earlier. Bring the whole view to one standard instead of perfecting a corner.

## Reviewing someone else's design

- State what you inspected (which views, which widths, which states) and what you could not.
- Rank findings: **P0** blocks the task or loses data; **P1** materially harms use or is a confirmed accessibility failure; **P2** is friction with a workaround; **P3** is polish.
- Separate what you confirmed from what you suspect.
- Pair each finding with a concrete change.
- "No material findings in the inspected scope" is a valid result. Do not invent problems to fill a list.
