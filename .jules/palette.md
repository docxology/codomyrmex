## 2024-08-13 - Added aria-label to sub-menu toggle
**Learning:** Icon-only toggle buttons in dynamic nested menus must have screen-reader explicit context (e.g., "Expand <Item>") rather than generic labels, as they share the immediate DOM area with the parent navigation link.
**Action:** Ensure dynamic tree UI implementations provide item-specific aria-labels on stateful expansion toggles.
