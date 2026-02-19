"""
Shared test fixtures for Obsidian vault tests.

Provides temporary vault directories with sample notes for testing.
"""

import json

import pytest
from pathlib import Path


SAMPLE_NOTE_WITH_FRONTMATTER = """---
title: My Test Note
tags:
  - testing
  - obsidian
created: 2024-01-15
status: draft
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

## Callouts

> [!note] Important Info
> This is a note callout with important information.
> It spans multiple lines.

> [!warning]- Collapsible Warning
> This is collapsed by default.

> [!tip]+ Expandable Tip
> This starts expanded.
"""

SAMPLE_NOTE_SIMPLE = """# Simple Note

Just a simple note with a link to [[My Test Note]] and a #simple-tag.
"""

SAMPLE_NOTE_NO_FRONTMATTER = """# No Frontmatter

This note has no YAML frontmatter at all.

It links to [[Another Note]] though.
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
    ],
}


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary vault with sample notes."""
    vault_dir = tmp_path / "test-vault"
    vault_dir.mkdir()

    # Create .obsidian dir (simulates real vault)
    obsidian_dir = vault_dir / ".obsidian"
    obsidian_dir.mkdir()
    (obsidian_dir / "app.json").write_text('{"vimMode": false}')

    # Create notes
    (vault_dir / "My Test Note.md").write_text(SAMPLE_NOTE_WITH_FRONTMATTER)
    (vault_dir / "Simple Note.md").write_text(SAMPLE_NOTE_SIMPLE)
    (vault_dir / "No Frontmatter.md").write_text(SAMPLE_NOTE_NO_FRONTMATTER)

    # Create subfolder with note
    subfolder = vault_dir / "subfolder"
    subfolder.mkdir()
    (subfolder / "Nested Note.md").write_text(
        "---\ntags:\n  - nested\n---\n# Nested\nA note in a subfolder.\n"
    )

    return vault_dir


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
