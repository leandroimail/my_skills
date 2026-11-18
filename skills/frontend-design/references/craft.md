# Craft: typography, color, layout

Working measures for executing a direction once it is chosen. Accessibility minimums are covered by the quality floor in [SKILL.md](../SKILL.md); the numbers here are starting points to tune by eye, not rules to quote.

## Contents

- Typography
- Color
- Layout and spacing
- Browser surfaces
- If the chosen direction is minimal

## Typography

- **Body size.** 16px (1rem) or more for running text. Respect the user's font-size setting by sizing in rem.
- **Measure.** Running prose reads best at about 65–75 characters per line; 45–75 is workable. This applies to prose, not to UI labels or tables.
- **Leading follows measure.** Longer lines need more line height; short lines and large display type need less. Body text usually sits near 1.5–1.6, display type near 1.1.
- **Tracking.** Large display type tolerates slightly negative letter-spacing; small uppercase labels need it opened up. Tune per typeface, since a value that suits one face cramps another.
- **Light on dark.** Light text on a dark ground looks heavier and tighter than the reverse. Compensate with a little more line height, a little more tracking, or one step of weight.
- **Wrapping.** `text-wrap: balance` for headings and other short centered text, `text-wrap: pretty` for body copy. Both are progressive enhancements; the layout must hold without them.
- **Paragraph rhythm.** Separate paragraphs with space or with a first-line indent, not both.
- **Numbers.** `font-variant-numeric: tabular-nums` wherever figures are compared in a column or change in place.
- **Small marks.** Use a real ellipsis character, curly quotes, and a non-breaking space between a number and its unit.
- **Loading.** Load only the weights you use, pick a fallback with similar metrics so the swap does not shift the layout, and never hide text while a font loads.
- **Roles before sizes.** Name the typographic roles (display, heading, body, label, data) and the contrast between them first, then assign sizes. Three or four sizes with clear jumps read as hierarchy; many near-identical sizes read as noise.

## Color

- **Roles, not swatches.** Turn the palette into roles: canvas, raised surface, primary and secondary text, action, focus, border, and the state colors (success, warning, error, info). Every color in the build should answer "which role is this?"
- **Build ramps in OKLCH.** Stepping lightness in `oklch()` gives even perceived steps. Reduce chroma toward the light and dark ends, where saturated color turns garish or muddy.
- **Avoid pure black for body text** on a light ground unless the direction calls for that harshness; a very dark tint of the palette's hue sits better.
- **Tint the secondary text.** On a colored surface, secondary text carries the hue of the background or the foreground. Neutral grey on color looks dead and often fails contrast. Measure the result.
- **Accent discipline.** Decide how many accent colors the design has and keep to it. An accent that appears everywhere stops being one.
- **State color needs a second cue.** Pair it with text, an icon, or a shape, so the meaning survives color blindness and greyscale. A reliable pattern for badges is a light tint of a hue behind a dark shade of the same hue.
- **Dark mode is composed, not inverted.** Elevation is expressed by lighter surfaces instead of shadows, saturated colors usually need less chroma, and each text and surface pair is rechecked for contrast. Set `color-scheme` on the root so native controls follow, and match `<meta name="theme-color">` to the page background.
- **Prefer explicit colors to stacked transparency.** Layers of alpha overlays make contrast unpredictable.
- **Choose light or dark from the scene of use**: who is looking, where, in what light, for how long. Do not choose it from the product category.

## Layout and spacing

- **Proximity first.** Things that belong together sit closer than things that do not. Add a border or a container only when spacing alone cannot show the grouping.
- **A spacing scale.** Pick one and hold it. A 4px base is a common starting point because it keeps the intermediate steps a pure 8px scale lacks. Use `gap` for the rhythm between siblings.
- **Rhythm is contrast.** Uniform spacing everywhere reads as flat. Tight intervals inside groups and generous ones between them create hierarchy.
- **Headings bind downward.** Give a heading more room above than beneath, so it attaches to the text it introduces.
- **Squint test.** Blur the screen or step back: the primary element, the secondary ones, and the groups should still be visible. If everything has equal weight, nothing leads.
- **Fit the container.** Use container queries for components placed in different contexts, a `max-width` so content does not stretch on very wide screens, and `min-width: 0` on flex and grid children that must shrink.
- **Order.** DOM order matches visual order, so keyboard focus and screen readers follow the same path the eye does.
- **Shadows.** An elevation shadow has an offset and a soft blur and reads as light from one direction. A colored halo with zero offset is decoration; use it only if the direction asks for glow.
- **Overlays.** A menu or tooltip inside an `overflow: hidden` ancestor gets clipped. Use `<dialog>`, the popover API, or fixed positioning.

## Browser surfaces

On Persuade and Experience surfaces, the details the browser draws by default are a cheap way to make a page feel finished: text selection color, caret color, underline offset and thickness, and the focus ring, all taken from the palette. Keep contrast intact and do not break forced-colors mode. On Operate surfaces leave scrollbars and native controls native.

## If the chosen direction is minimal

This section is execution guidance for a brief that calls for restraint. It is never the default direction. Check your plan against the three default looks in `SKILL.md` before using it, because the quiet off-white editorial page is one of them.

- Precision replaces ornament, so inconsistencies show. All borders share one thickness, radii come from a short scale (for example one value for controls and one for containers), and section spacing is generous and regular.
- Shadows are nearly absent. Separate surfaces with a hairline or a small step in tone.
- Color is scarce: neutrals carry the page, and the few colored elements carry meaning.
- Type does the work that decoration would have done, which makes size contrast, weight, and spacing the whole design. Spend the time there.
- Minimal still needs a signature. A page with nothing memorable is unfinished, however restrained it looks.
