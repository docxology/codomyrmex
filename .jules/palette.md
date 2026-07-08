## 2024-05-18 - Icon-Only Button Accessibility in Mission Control
**Learning:** Terminal toolbar components and other icon-only interactive elements in `mission_control/app` lacked `aria-label` and `title` attributes, making them inaccessible to screen readers and lacking tooltip context.
**Action:** Always verify that every `<Button size="icon-sm">` containing only an `<svg>` includes both `aria-label` and `title` attributes for full accessibility.
