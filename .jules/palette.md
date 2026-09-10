# Palette Journal

## 2024-05-14 - Missing ARIA labels in dynamic SVGs

**Learning:** Icon-only buttons used for expanding/collapsing sidebars or closing panels often miss ARIA labels, creating accessibility issues for screen readers. This pattern is prevalent when inline SVGs are used instead of textual components.
**Action:** Audit icon-only interactive elements regularly to ensure `aria-label` is applied, particularly in dynamic or collapsible UI elements.
