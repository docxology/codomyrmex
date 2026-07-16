## 2026-07-16 - Hover-only visibility
**Learning:** Interactive elements in this app (like the remove attachment button) sometimes use hover-only visibility (e.g., opacity-0 group-hover:opacity-100), which hides them from keyboard users.
**Action:** Always add focus-visible fallback classes (e.g., focus:opacity-100) and aria-labels for hidden interactive elements.
