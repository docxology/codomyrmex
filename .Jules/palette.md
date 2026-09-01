## 2024-05-24 - Missing aria-label on icon-only buttons
**Learning:** Many icon-only buttons (`size="icon-xs"`, `size="icon-sm"`) rely solely on `title` attributes or lack accessible text entirely, which are not reliably read by screen readers across all browsers.
**Action:** Always provide an explicit `aria-label` for icon-only buttons to ensure they are accessible to screen reader users.
