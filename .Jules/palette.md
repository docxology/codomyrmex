## 2024-05-18 - Nav Rail Expand Accessibility
**Learning:** The navigation rail expand/collapse button in the dashboard lacked context for screen readers when toggling child views.
**Action:** Always add dynamic \`aria-label\` (indicating Expand/Collapse action based on state) and \`aria-expanded\` attributes to icon-only toggle buttons in navigation components.
