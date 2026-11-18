# Quality floor

Check the build against this before handing off. Items marked **(WCAG)** are conformance minimums at level AA and are not negotiable for style reasons. The rest are practices that prevent defects people see. Everything is written for plain HTML and CSS; translate to your framework.

## Contents

- Contrast and color
- Focus and keyboard
- Semantics
- Forms
- States
- Extreme content
- Responsive, zoom, and touch
- Motion
- Images and media
- Navigation and state
- Dark mode
- Language and formats

## Contrast and color

- **(WCAG 1.4.3)** Text has at least 4.5:1 contrast against its background. This includes placeholder text, secondary text, and button labels.
- **(WCAG 1.4.3)** Only large text may drop to 3:1. Large means at least 24 CSS px, or at least 18.66 CSS px in bold.
- **(WCAG 1.4.11)** The visual parts needed to identify a control or its state (an input's border, a checkbox's box, a focus ring, a meaningful icon) have at least 3:1 against adjacent colors. Disabled controls are exempt.
- **(WCAG 1.4.1)** Color is never the only signal for a state, a required field, or a link inside text.
- Measure the pairs; do not judge contrast by eye, especially for text over images or gradients.

## Focus and keyboard

- **(WCAG 2.4.7)** Every interactive element shows a visible focus indicator. Never write `outline: none` without a replacement.
- Style focus with `:focus-visible`, so it appears for keyboard use and not on every click. Use `:focus-within` for composite controls.
- **(WCAG 2.4.11)** A focused element is not completely hidden by a sticky header, footer, or overlay.
- **(WCAG 2.1.1)** Everything that works with a pointer works with the keyboard, in an order that matches the visual order.
- A dialog traps focus while open and returns it to the trigger when closed. Use `<dialog>` to get this for free.

## Semantics

- A `<button>` performs an action and an `<a href>` navigates. A clickable `<div>` is neither.
- Reach for native elements before ARIA.
- An icon-only button has an accessible name (`aria-label`); a decorative icon has `aria-hidden="true"`.
- Every `<img>` has `alt`: a description when it carries information, empty when it is decoration.
- Headings descend in order without skipping levels, with one `<h1>` per page. A long page offers a skip link to the main content.
- **(WCAG 4.1.3)** A status that appears without a page change (a toast, an inline validation result, "saved") is announced to assistive technology without moving focus.

## Forms

- Every field has a visible `<label>` connected to it. A placeholder is not a label.
- Use the right `type` and `inputmode` (`email`, `tel`, `url`, numeric) so mobile keyboards match, and meaningful `autocomplete` and `name` values so browsers can fill them.
- Never block paste.
- Show errors next to the field they concern, say how to fix them, and move focus to the first error on submit.
- Keep the submit button enabled until the request starts, then show progress on it. A button disabled for unexplained reasons is a dead end.
- Warn before navigating away from unsaved changes.
- Clicking a checkbox's or radio's label toggles it, with no dead gap between the two.

## States

Design each of these for every view and component that can reach it:

- **Loading:** a skeleton shaped like the final layout, so nothing jumps when content arrives. Reserve spinners for short waits inside a control.
- **Empty:** composed, with a way forward (see the writing section of `SKILL.md` for the kinds of empty).
- **Error:** specific, inline where possible, with a recovery action. Consider offline, timeout, and no-permission as well as server failure.
- **Success:** confirmed in the place the person is looking.
- **Disabled:** visibly different, and explained when the reason is not obvious.
- **Hover, active, focus:** each more prominent than rest, and distinguishable from each other.

## Extreme content

- Try each text slot with very short, typical, and very long content, and each list with zero, one, and a great many items. Try large numbers and long unbroken strings.
- Let text wrap (`overflow-wrap: anywhere` for long strings) before truncating it.
- Truncate only what the person can reach in full elsewhere. Never truncate an error, an instruction, or the label of an essential action.

## Responsive, zoom, and touch

- **(WCAG 1.4.10)** Content reflows at 320 CSS px wide with no loss of information or function and no two-dimensional scrolling. This is also what a 1280px window looks like at 400% zoom. Data tables, maps, and diagrams that need two dimensions are excepted.
- **(WCAG 1.4.4)** Never set `user-scalable=no` or `maximum-scale=1`. Check the layout with text enlarged to 200% as a separate test from narrow width.
- **(WCAG 2.5.8)** Pointer targets are at least 24 by 24 CSS px, with exceptions for inline links and targets with enough spacing. Aim for about 44px on touch surfaces; that is the comfortable size and the AAA criterion.
- A gesture such as drag, swipe, or pinch has a single-tap or keyboard alternative.
- Full-bleed layouts respect notches and home indicators with `env(safe-area-inset-*)`.
- Check the breakpoints the content needs, not only the ones a framework ships with.

## Motion

The floor: content is visible without JavaScript-driven reveals; `prefers-reduced-motion` removes non-essential movement and keeps state feedback; motion that starts on its own, lasts more than five seconds, and sits beside other content can be paused, stopped, or hidden **(WCAG 2.2.2)**.

## Images and media

- Give `<img>` explicit `width` and `height` (or an `aspect-ratio`) so the layout does not shift when it loads.
- Lazy-load images below the fold with `loading="lazy"`, and prioritize the one that dominates the first screen.
- Check the crop and focal point at narrow widths; use `object-fit` and `object-position` deliberately.
- Make sure the layout still holds, with a sensible background and readable overlaid text, when an image fails to load.
- Prefer a muted, looping `<video playsinline>` to an animated GIF, and give it a still fallback.
- Icons come from one family, at one stroke weight and optical size, aligned to the text they sit beside.

## Navigation and state

- The URL reflects what the person would expect to share or return to: filters, tabs, pagination, an open item.
- Links are real links, so opening in a new tab works.
- A destructive action asks for confirmation or offers undo.

## Dark mode

- Set `color-scheme` so native controls, scrollbars, and form fields match.
- Give native `<select>` an explicit `background-color` and `color`; some platforms otherwise render it unreadable on dark themes.
- Recheck every text and surface pair for contrast; do not assume the light theme's ratios carry over.

## Language and formats

- Format dates, times, numbers, and currency with `Intl.DateTimeFormat` and `Intl.NumberFormat` for the user's locale instead of hard-coding a format.
- Write complete messages; do not assemble sentences from fragments, because word order changes between languages.
- Leave room for translated text to run about a third longer than English.
- Use logical properties (`margin-inline-start`, `padding-inline`) so the layout can mirror for right-to-left scripts.
- Set the `lang` attribute on the document.
