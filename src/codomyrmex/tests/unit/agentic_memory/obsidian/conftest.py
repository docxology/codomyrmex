"""
Shared test fixtures for Obsidian vault tests.

Provides temporary vault directories with rich sample notes covering
all parser features: frontmatter, wikilinks, embeds, tags, callouts,
code blocks, math, Dataview fields, daily notes, and canvas files.
"""

import json
import shutil

import pytest

from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault

SAMPLE_NOTE_WITH_FRONTMATTER = """---
title: My Test Note
tags:
  - testing
  - obsidian
created: 2024-01-15
status: draft
aliases:
  - Test Note
  - TN
---

# My Test Note

This is a test note with various Obsidian features.

## Links

Here is a link to [[Another Note]] and one with an alias [[Target|Display Text]].
Also linking to a heading [[Some Note#Section One]] and a block [[Other#^block-id]].

## Embeds

![[image.png]]
![[diagram.png|400]]
![[photo.jpg|800x600]]

## Tags

This note has #inline-tag and #parent/child tags.

## Code

```python
def hello():
    print("Hello, Obsidian!")
```

```javascript
console.log("test");
```

## Math

The quadratic formula is $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$ for solving polynomials.

Inline math: $E = mc^2$ is famous.

## Dataview Fields

Due:: 2024-02-15
Priority:: High
Category:: Research

## Callouts

> [!note] Important Info
> This is a note callout with important information.
> It spans multiple lines.

> [!warning]- Collapsible Warning
> This is collapsed by default.

> [!tip]+ Expandable Tip
> This starts expanded.

## Tasks

- [ ] Todo item
- [x] Done item
- [/] In progress
"""

SAMPLE_NOTE_SIMPLE = """# Simple Note

Just a simple note with a link to [[My Test Note]] and a #simple-tag.
"""

SAMPLE_NOTE_NO_FRONTMATTER = """# No Frontmatter

This note has no YAML frontmatter at all.

It links to [[Another Note]] though.
"""

SAMPLE_NOTE_DAILY = """---
tags:
  - daily
created: 2024-01-15
---

# 2024-01-15

## Tasks

- [ ] Morning standup
- [x] Review PRs
- [ ] Write documentation
"""

SAMPLE_NOTE_WITH_MANY_LINKS = """---
title: Hub Note
tags:
  - hub
---

# Hub Note

This note links to many others:
- [[My Test Note]]
- [[Simple Note]]
- [[No Frontmatter]]
- [[Nested Note]]
"""

SAMPLE_CANVAS = {
    "nodes": [
        {
            "id": "node-1",
            "type": "text",
            "x": 0,
            "y": 0,
            "width": 250,
            "height": 140,
            "text": "Hello World",
        },
        {
            "id": "node-2",
            "type": "file",
            "x": 300,
            "y": 0,
            "width": 250,
            "height": 140,
            "file": "notes/test.md",
        },
        {
            "id": "node-3",
            "type": "link",
            "x": 0,
            "y": 200,
            "width": 250,
            "height": 140,
            "url": "https://example.com",
        },
        {
            "id": "node-4",
            "type": "text",
            "x": 300,
            "y": 200,
            "width": 250,
            "height": 140,
            "text": "Colored node",
            "color": "#ff5555",
        },
    ],
    "edges": [
        {
            "id": "edge-1",
            "fromNode": "node-1",
            "toNode": "node-2",
            "fromSide": "right",
            "toSide": "left",
            "label": "references",
        },
        {
            "id": "edge-2",
            "fromNode": "node-3",
            "toNode": "node-4",
        },
    ],
}


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary vault with rich sample notes."""
    vault_dir = tmp_path / "test-vault"
    vault_dir.mkdir()

    # Create .obsidian dir (simulates real vault)
    obsidian_dir = vault_dir / ".obsidian"
    obsidian_dir.mkdir()
    (obsidian_dir / "app.json").write_text('{"vimMode": false}')
    (obsidian_dir / "daily-notes.json").write_text(
        '{"folder": "daily", "format": "YYYY-MM-DD"}'
    )

    # Create notes
    (vault_dir / "My Test Note.md").write_text(SAMPLE_NOTE_WITH_FRONTMATTER)
    (vault_dir / "Simple Note.md").write_text(SAMPLE_NOTE_SIMPLE)
    (vault_dir / "No Frontmatter.md").write_text(SAMPLE_NOTE_NO_FRONTMATTER)
    (vault_dir / "Hub Note.md").write_text(SAMPLE_NOTE_WITH_MANY_LINKS)

    # Create subfolder with note
    subfolder = vault_dir / "subfolder"
    subfolder.mkdir()
    (subfolder / "Nested Note.md").write_text(
        "---\ntags:\n  - nested\n---\n# Nested\nA note in a subfolder.\n"
    )

    # Create daily notes folder
    daily_dir = vault_dir / "daily"
    daily_dir.mkdir()
    (daily_dir / "2024-01-15.md").write_text(SAMPLE_NOTE_DAILY)

    # Create templates folder
    templates_dir = vault_dir / "Templates"
    templates_dir.mkdir()
    (templates_dir / "Daily.md").write_text(
        "---\ntags:\n  - daily\n---\n\n# {{date}}\n\n## Tasks\n\n- [ ] \n"
    )

    return vault_dir


@pytest.fixture
def vault_instance(tmp_vault):
    """Return a loaded ObsidianVault instance."""
    return ObsidianVault(tmp_vault)


@pytest.fixture
def tmp_canvas_file(tmp_path):
    """Create a temporary canvas file."""
    canvas_file = tmp_path / "test.canvas"
    canvas_file.write_text(json.dumps(SAMPLE_CANVAS, indent=2))
    return canvas_file


@pytest.fixture
def sample_frontmatter_note():
    """Return sample note content with frontmatter."""
    return SAMPLE_NOTE_WITH_FRONTMATTER


@pytest.fixture
def sample_simple_note():
    """Return simple note content."""
    return SAMPLE_NOTE_SIMPLE


@pytest.fixture
def unavailable_cli():
    """Return an ObsidianCLI pointing to a nonexistent binary."""
    from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI
    return ObsidianCLI(binary="__nonexistent_cli_binary__")


@pytest.fixture
def cli_available():
    """Return True if the Obsidian CLI is on PATH."""
    return shutil.which("obsidian") is not None
