## 2024-07-14 - Missing ARIA Labels on Icon Buttons
**Learning:** The application has a recurring accessibility pattern where icon-only buttons (such as those in the header and theme selector) lack `aria-label` attributes, making them inaccessible to screen readers despite having `title` attributes or tooltip equivalents.
**Action:** Always verify that icon-only `<Button>` components explicitly include an `aria-label` during development or code review.
