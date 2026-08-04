## 2024-07-28 - Added ARIA attributes to expandable/collapsible nav buttons
**Learning:** Collapsible sections like sidebars, nav groups, and nested menus are completely inaccessible to screen readers without proper aria-expanded states and clear aria-labels that describe both the action and the target.
**Action:** Always pair visual collapse/expand indicators with `aria-expanded` attributes and descriptive `aria-label`s on the triggering button.
