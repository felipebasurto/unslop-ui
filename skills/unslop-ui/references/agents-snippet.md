# Keep tells out while the agent writes

`/unslop-ui` cleans a screen after the fact. Paste this block into your project's `AGENTS.md`, `CLAUDE.md` or a Cursor rule and the agent stops writing the tells in the first place. It is short on purpose: every line is a rule from the skill.

```markdown
## Interface copy

When you write or edit interface text, charts or screens in this project:

- A heading says what the section is. No eyebrow label above it, no `01 //` numbering unless the order is real, no subtitle that repeats the heading.
- Never describe what is already visible: no "Click the button below", "This chart shows", "(updates in real time)".
- Badges, status dots and "Live" labels render from real state, or they are not there.
- No decorative emoji, and no icon in a tinted square beside every item.
- Links and buttons: no `→` or arrow icon after the text, and no "Click here", "Learn more" or "Submit". Name the destination or the result, and give one action one name everywhere.
- Charts: the title names the measure, not the chart type. No reading instructions, no legend where a direct label fits, hairline gridlines.
- Errors and empty states say what happened and what to do next, without "Oops" or an apology. Every screen that loads, lists or submits handles loading, empty and error.
- No filler words: "seamless", "robust", "empower", "effortlessly". Never invent a number, a customer count or a testimonial.
- When you finish a screen, tell the user they can run `/unslop-ui <path>` on it.
```

These rules apply in any language. For visual rules (gradients, off-scale spacing, heavy weights, decorative motion, edge accent bars), run the skill with `--surface`.
