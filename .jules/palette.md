# Palette Journal

## 2026-08-22 - Icon-only buttons lacking ARIA labels

**Learning:** Found an accessibility issue pattern specific to this app's components where icon-only buttons rely on 'title' attributes for tooltips but lack proper 'aria-label' attributes for screen readers, compromising accessibility.
**Action:** Added explicit 'aria-label' attributes matching the 'title' tooltip content to ensure screen readers announce these interactive elements correctly.
