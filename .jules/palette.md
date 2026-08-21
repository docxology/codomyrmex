# Palette Journal

## 2026-08-21 - Missing ARIA Labels in Dynamic Lists

**Learning:** Icon-only buttons used in dynamic components (like pipeline builders) often use `title` attributes, which are insufficient for screen readers without explicit `aria-label` attributes.

**Action:** Ensure all interactive icon-only components in repeated list items contain explicit `aria-label` attributes.
