## 2024-09-05 - Consistent use of `aria-label` for icon-only buttons
**Learning:** Found several icon-only close buttons lacking `aria-label`s in `runtime-setup-modal.tsx`, making them inaccessible to screen readers.
**Action:** Always verify that buttons containing only an icon `<svg>` have an `aria-label` that describes their function.
