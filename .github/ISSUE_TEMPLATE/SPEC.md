# .github/ISSUE_TEMPLATE — Specification

**Status**: Active | **Last Updated**: February 2026

## Overview

GitHub issue forms using the `yml` format (not legacy Markdown templates). Forms provide
structured input with validation, dropdowns, and checkboxes.

## Template Structure

Each template is a YAML file with:
- `name`: Display name in the "New Issue" picker
- `description`: One-line description shown in the picker
- `title`: Default title prefix (e.g., `[Bug]: `)
- `labels`: Automatically applied labels
- `body`: Array of form fields (markdown, input, textarea, dropdown, checkboxes)

## Required Fields (all templates)

1. **Pre-submission checklist** — confirms user searched for duplicates, read contributing guide
2. **Description** — clear explanation of the issue/request
3. **Codomyrmex version** — version or commit hash
4. **Python version** — runtime environment

## Bug Report Additional Fields

- Steps to reproduce (numbered list)
- Expected behavior
- Actual behavior / error message
- Operating system
- Installation method (uv, pip, source)

## Feature Request Additional Fields

- Problem statement ("I'm trying to...")
- Proposed solution
- Alternatives considered
- Acceptance criteria (definition of done)

## Documentation Issue Additional Fields

- Affected file/section
- Type: incorrect, missing, unclear, outdated
- Suggested improvement
