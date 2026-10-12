# Documentation theme override

`main.html` extends Material's base template. It retains the upstream header
and adds its localized search label to the search dialog before delivery.
The generated dialog must have a non-empty accessible name after theme updates.

Contrast overrides live in [the stylesheet](../../../docs/theme-accessibility.css).
Verify the generated pages with `make docs-check` and the Lighthouse workflow.
