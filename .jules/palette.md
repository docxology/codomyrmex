# 2024-05-18 - Missing ARIA Labels on Icon-only Buttons

**Learning:** There was a widespread pattern in this codebase of using icon-only buttons (like `x` or `&times;`) without `aria-label` attributes, making them inaccessible to screen readers. We discovered 8 components with missing labels.

**Action:** Always add descriptive `aria-label` attributes to `<Button>` elements that contain only an icon or symbol instead of text.
