# Palette UX Learnings

## 2024-03-24 - Accessibility on Icon-only Buttons

**Learning:** Found a pattern in ChatInput component where icon-only buttons relied purely on the `title` attribute, which is not fully reliable for screen reader accessibility.
**Action:** Always ensure icon-only buttons use `aria-label` attributes alongside `title` attributes for robust accessibility.
