## 2026-07-26 - ARIA Labels for Icon Buttons
**Learning:** Icon-only buttons lacking accessible names are a common pattern in the codebase, significantly hindering screen reader usage.
**Action:** Always verify that 'size="icon"' or 'size="icon-*"' Button components have a descriptive 'aria-label' or 'title' (if appropriate for screen readers, though aria-label is preferred for icons).
