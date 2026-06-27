## 2024-05-14 - Accessible Icon-Only Buttons
**Learning:** Found several icon-only buttons (`✕`, `&#x2715;`, `&#8592;`, `&#8594;`, `🎙️`/`⬛`) in `src/codomyrmex/agents/pai/pm/spa/index.html` (the PAI PM SPA dashboard) missing descriptive labels for screen readers. This is a common pattern when buttons are dynamically injected via JS template strings.
**Action:** Always ensure strings defining icon-only buttons injected into the DOM contain appropriate `aria-label` attributes to maintain accessibility without cluttering the visual UI.
