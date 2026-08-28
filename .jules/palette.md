## 2026-08-28 - Accessible custom inline forms
**Learning:** Custom interactive elements (like color pickers or custom toggle switches) built with standard `<button>` tags require explicit ARIA attributes (`aria-label`, `role='switch'`, `aria-checked`, `aria-pressed`) to be correctly interpreted by screen readers. Visual indicators are insufficient.
**Action:** When building non-standard interactive UI controls, ensure equivalent programmatic semantic meaning is provided via appropriate ARIA roles and states.
