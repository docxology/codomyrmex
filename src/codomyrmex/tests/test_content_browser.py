"""Property-based tests for content browser operations.

# Feature: local-web-viewer
# Tests Properties 17–18 from the design document.

Uses Hypothesis to verify that the content tree API matches the
filesystem and that file content is returned correctly.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from codomyrmex.website.education_provider import EducationDataProvider

# ── Strategies ─────────────────────────────────────────────────────

SAFE_NAMES = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_",
                           max_codepoint=127),
    min_size=1,
    max_size=20,
).map(str.strip).filter(lambda s: len(s) > 0 and not s.startswith("."))

FILE_CONTENT = st.text(min_size=0, max_size=200).filter(lambda s: "\r" not in s)


# ── Property 17: Content tree matches filesystem ──────────────────
# Feature: local-web-viewer, Property 17: Content tree matches filesystem
# Validates: Requirements 8.1


@given(
    file_names=st.lists(SAFE_NAMES, min_size=1, max_size=5, unique=True),
    dir_names=st.lists(SAFE_NAMES, min_size=0, max_size=3, unique=True),
)
@settings(max_examples=100)
def test_property17_content_tree_matches_filesystem(
    file_names: list[str], dir_names: list[str]
) -> None:
    """Content tree entries SHALL match actual files and directories on disk."""
    dir_names = [d for d in dir_names if d not in file_names]

    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir)

        for name in file_names:
            (content_dir / f"{name}.txt").write_text(f"content of {name}")
        for name in dir_names:
            (content_dir / name).mkdir(exist_ok=True)

        provider = EducationDataProvider(content_root=content_dir)
        result = provider.list_output_files("")

        entry_names = {e["name"] for e in result["entries"]}
        expected_files = {f"{name}.txt" for name in file_names}
        expected_dirs = set(dir_names)

        assert expected_files.issubset(entry_names)
        assert expected_dirs.issubset(entry_names)

        for entry in result["entries"]:
            if entry["name"] in expected_files:
                assert entry["type"] == "file"
            elif entry["name"] in expected_dirs:
                assert entry["type"] == "directory"


# ── Property 18: Content file returns correct contents ─────────────
# Feature: local-web-viewer, Property 18: Content file returns correct contents
# Validates: Requirements 8.3


@given(file_name=SAFE_NAMES, content=FILE_CONTENT)
@settings(max_examples=100)
def test_property18_content_file_returns_correct_contents(
    file_name: str, content: str
) -> None:
    """For text files, the content API SHALL return the exact file contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir)
        filepath = f"{file_name}.txt"
        (content_dir / filepath).write_text(content, encoding="utf-8")

        provider = EducationDataProvider(content_root=content_dir)
        result = provider.get_file_content(filepath)

        assert result["type"] == "text"
        assert result["content"] == content
        assert result["path"] == filepath
