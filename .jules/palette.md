## 2026-07-12 - Added ARIA attributes to icon-only toggle buttons in React Components
**Learning:** Found an accessibility issue pattern specific to this app's components, where collapsible parent navigation items used an icon-only `<button>` element without any `aria-label` or `aria-expanded` attributes, which screen readers need to properly announce the button's purpose and state.
**Action:** Always ensure icon-only interactive elements explicitly provide an `aria-label` (e.g., `aria-label="Toggle "`) and reflect their current state (e.g., `aria-expanded={isExpanded}`) for accessibility.
