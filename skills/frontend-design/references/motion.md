# Motion

Read this before writing any animation beyond a hover or press state. Durations and curves are starting points to tune for the direction; the accessibility items are requirements.

## Contents

- Decide whether to animate
- Timing
- Easing
- Patterns that hold up
- Performance
- Reduced motion and resilience
- Ambitious effects

## Decide whether to animate

Name the purpose in one word before building: *feedback* (the press registered), *continuity* (where this came from and went), *state change* (something is now different), *explanation* (how this works), or *delight*. If no word fits, leave the animation out.

Then weigh frequency. This heuristic comes from native app practice and transfers well to web apps:

| How often the person triggers it | What it can carry |
|---|---|
| Constantly (tab switch, scroll, typing) | Nothing beyond what the platform does |
| Dozens of times a day (press, row select, toggle) | Under about 150ms, barely noticeable |
| Occasionally (dialog, sheet, toast) | A standard, unhurried transition |
| Rarely or once (first run, completion, a hero) | Room for delight |

When unsure, removing the animation is usually the stronger choice. One orchestrated moment lands harder than the same entrance repeated on every section.

## Timing

| Kind | Starting range |
|---|---|
| Immediate feedback | 100–150ms |
| Routine state change | 150–300ms |
| Overlay, layout shift, view transition | 300–500ms |
| A focal, authored entrance | 500–800ms |

Exits run faster than entrances: the person has already decided, so do not make them wait. On Operate surfaces stay in the lower half of these ranges and skip page-load choreography.

## Easing

Use a deceleration curve for things entering or responding: fast at the start, settling at the end. `cubic-bezier(0.16, 1, 0.3, 1)` is a strong version of this and `cubic-bezier(0.2, 0, 0, 1)` a gentler one; pick or tune one that suits the character of the design, then reuse it so the motion feels like one system. Bounce and elastic curves are a statement, so use them when the direction is playful and not out of habit. Linear easing suits only continuous motion such as a progress bar or a spinner.

## Patterns that hold up

- **Enter from nearby.** Start from about `scale(0.95)` with a fade, or a short translate. Starting from `scale(0)` or from far away draws attention to the animation instead of the content.
- **Press feedback.** A small scale down (around 0.97) on `:active` reads as a physical response.
- **Origin.** Menus and popovers grow from the control that opened them; set `transform-origin` accordingly.
- **Hover.** Keep the hovered element itself still and move a child inside it. If the hit area moves away from the pointer, the hover flickers at the edge.
- **Stagger.** Offset list items by a small step and cap the total delay, so the last item does not arrive late.
- **Interruptible.** A transition can be reversed midway without snapping; prefer CSS transitions or animation APIs that handle this over fixed timelines.

## Performance

- Animate `transform` and `opacity`. Animating `width`, `height`, `top`, `left`, or `margin` forces layout on every frame; use transforms, grid tricks, or a FLIP technique for size changes.
- Never write `transition: all`. List the properties, so an unrelated change does not animate by accident.
- Apply `will-change` only while the animation runs, then remove it.
- Trigger scroll reveals with `IntersectionObserver`, not a scroll event listener.

## Reduced motion and resilience

- **Content is visible by default.** Do not hide elements in CSS and rely on JavaScript to reveal them. If the script fails, the page must not be blank.
- **Honor `prefers-reduced-motion`.** Remove non-essential movement: translation, scaling, parallax, and ambient loops. Keep the feedback that tells people something happened, as an instant change or a short opacity fade. Shortening a large movement does not make it comfortable; removing it does. Avoid the global hack that forces every duration to near zero, since it breaks animations that carry state.
- **Automatic motion needs a control.** Anything that starts on its own, lasts more than five seconds, and sits beside other content needs a way to pause, stop, or hide it (WCAG 2.2.2). Content that updates automatically needs the same control regardless of duration.
- **No flashing** more than three times a second.

## Ambitious effects

For WebGL, scroll-driven scenes, view transitions, and similar:

1. Choose the result first, then the technique.
2. Build the baseline that works without the effect, then layer the effect on.
3. Test on a real mid-range device. If the frame rate drops noticeably and stays low, simplify.
4. Clean up observers, listeners, and animation loops when the element leaves the page.

Ask four questions before keeping it: does it serve the product, is the page worse without it, does the page work without it, and is it smooth where people will actually see it?
