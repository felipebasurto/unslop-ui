# Surface values

Fix targets for U17 to U20. When the project already has a token system (Tailwind theme, CSS variables, a design-system package), use its values and only fix where the code bypasses them. These numbers are the fallback, not a house style.

## Contents
- Spacing
- Color
- Type
- Radius and depth
- Motion

## Spacing

Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64.

| Where | Value |
|---|---|
| Inside a control | 4 to 12 |
| Between rows in a list | 2 to 8 |
| Between groups (a label and its list, two cards) | 12 to 24 |
| Between sections | 32 to 64 |
| Card padding | 16 to 24, one value for sibling cards |
| Row height | 32 compact, 36 default, 44 touch |

Space inside a group is smaller than space between groups. An off-scale value moves to the nearest step (`mt-[13px]` becomes `mt-3`). A 2px nudge inside a small control, or an odd value that exactly centers something, can stay.

## Color

No hex ramp is prescribed. Keep the project's palette and fix how it is used.

- Surfaces, borders and text come from one neutral family. Three text roles: primary, secondary, muted. Five near-identical tints of one hue become three.
- One accent, on the primary action, the selection or the one number that matters.
- Borders are hairlines: the text color at 6 to 10% opacity.
- Text contrast is at least 4.5:1 on its surface, including text on the accent and muted text.
- Semantic colors (green good, red error) carry meaning only, and sit inside the palette instead of glowing.
- Gradients are allowed only as a tone shift inside one neutral. A gradient from one hue to another, gradient text, colored glows and blurred color blobs go.

## Type

| Use | Size | Weight |
|---|---|---|
| Meta, counts | 12 | 400 |
| Captions, secondary | 13 to 14 | 400 |
| Body, navigation | 14 to 15 | 400 to 500 |
| KPI figure | 28 to 32 | 500, `tabular-nums` |
| Page title | 24 to 32 | 500 to 600 |

Weights 400 to 600. Hierarchy comes from size and color, not from 800 or 900. Letter spacing is 0 under 16px. Negative tracking is for display text only. Numbers use one format on the screen.

## Radius and depth

| Element | Radius |
|---|---|
| Tag, keycap | 4 to 6 |
| Input, button, row | 8 to 10 |
| Card | 12 to 16 |
| Panel | 16 to 20 |

Nested radius: inner = outer minus the padding between them, never below 4.

Depth: a surface step plus a hairline. Where a shadow earns its place, keep it neutral and small: `0 1px 2px rgb(0 0 0 / 0.05)`, or `0 8px 24px rgb(0 0 0 / 0.06)` for something floating.

## Motion

| Use | Duration |
|---|---|
| Hover, press, toggle | 120 to 180ms |
| Menu, popover, tooltip | 160 to 220ms |
| Entrance, layout change | 300 to 400ms |

One easing curve for the screen: `cubic-bezier(0.22, 1, 0.36, 1)` or the framework's ease-out. Transition named properties (`transition-colors`, `transition-[opacity,transform]`), never `all`. Never animate width, height, top, left or margins. A press scales to 0.97 to 0.98. A card does not scale on hover. Keep motion that explains something (a menu rising a few pixels, a number tweening) and drop loops and bounces.
