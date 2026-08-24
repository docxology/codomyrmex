## 2024-08-24 - Navigation Accordion Accessibility
**Learning:** Custom accordion implementations using `<button>` or `<Button>` without `aria-expanded` and `aria-label` make it impossible for screen reader users to understand the state and purpose of expandable navigation groups.
**Action:** Always ensure expandable UI elements include descriptive `aria-label` attributes and dynamically bound `aria-expanded={boolean}` states to communicate interaction outcomes clearly to assistive technologies.
