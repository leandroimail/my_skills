# Surfaces and existing identity

How much expression a design can carry depends on what the surface is for and on what the product already looks like. This file expands the "Read the situation first" section of `SKILL.md`.

## Contents

- What the surface is for
- Working inside an existing identity
- Two sanity checks

## What the surface is for

Most products mix surfaces: a marketing site, the app behind the login, and the docs. Calibrate each one separately, and keep the same tokens across them so they read as one product.

### Persuade: landing page, marketing, portfolio, campaign

The visitor has not committed yet, so the page has to make a case. This is where the full skill applies: a hero that works as a thesis, a characterful display face, one orchestrated moment of motion, a visible risk.

### Operate: app screen, admin, dashboard shell, form, internal tool

The person is here to finish a task, often many times a day. They must recognize navigation, controls, and current state before they notice style.

- Keep standard affordances standard. Tables, dialogs, selects, tabs, and scrollbars behave the way the platform taught people to expect. Restyle them within the palette; do not reinvent how they work.
- Identity lives in the type, the color roles, the density, and one considered detail (how a status reads, how a row selects, how the empty state is drawn), not in layout tricks.
- One typeface family is often enough. Keep display faces away from labels, buttons, and data.
- Use a contained type scale: a ratio of about 1.125 to 1.2 between steps, in fixed rem sizes, since fluid type makes dense screens jitter between widths.
- Group with space first. Reach for a border or a card only when proximity alone fails, and avoid a card inside a card.
- Motion is brief and functional: roughly 150–250ms for state changes, no page-load choreography, nothing that delays the first interaction.
- Density is a design decision. Choose it for the person's working conditions (how much they compare, how long they stay), then hold it everywhere.

What "risk" means here: one deliberate choice a stock component kit would not have made, executed precisely. It does not mean novel navigation.

### Read: documentation, articles, long-form

- The reading column stays calm: about 60–75 characters per line, body text at 16px or more, generous line height, monospace only for code.
- Identity belongs to the frame: masthead, navigation rail, section openers, figures, and code blocks.
- Headings, anchors, and a visible "where am I" matter more than any decorative move.

### Experience: immersive, playful, or showcase piece

- The effect is the content, so choose the result you want before choosing a technique.
- The baseline still works without the effect: content is reachable with reduced motion, on touch, and on a slow device.
- One effect done well beats several competing ones.

## Working inside an existing identity

Look for evidence before deciding: design tokens or CSS variables, a component library, a style guide, neighboring screens. Then pick the case.

| Case | Signals | What to do |
|---|---|---|
| Preserve | Tokens, components, and consistent neighboring screens exist | Inherit all of it. Contribute precision, hierarchy, and the states nobody designed. Differ only where the task needs it, and say why |
| Extend | Some confirmed traits (a logo, a color, a typeface) and gaps everywhere else | Keep the confirmed traits fixed and fill the gaps in the same spirit. Name what you added |
| Replace | A redesign was asked for explicitly | Treat the old look as evidence of what to move away from. Commit to the new direction; a blend of old and new satisfies nobody |
| Create | No identity to inherit | Apply the full skill |

When refining rather than redesigning:

- Keep behavior, factual copy, and everything outside the requested scope as they are. Ask before changing claims, numbers, or legal text.
- If the system has a flaw that blocks the task (a missing token, a component that cannot express a needed state), classify it before fixing: a missing token, a one-off implementation, or a local defect. Fix it at that level instead of adding a parallel style.
- Do not polish one corner to a standard the rest of the screen does not meet. Raise the whole view or flag the gap.

## Two sanity checks

1. Cover the logo. Does it still read as a usable product of its kind, and is the main task obvious?
2. Swap in another product's name. If the design would serve it unchanged, the design is not yet about this one. On a Preserve task, this check applies to the product as a whole, not to your addition.
