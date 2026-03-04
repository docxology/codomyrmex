"""Property-based tests for RuleLoader._parse_sections using Hypothesis (zero-mock)."""
from __future__ import annotations
import re
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from codomyrmex.agentic_memory.rules.loader import RuleLoader
from codomyrmex.agentic_memory.rules.models import RuleSection
pytestmark = pytest.mark.unit
_HEADING_RE = re.compile(r"^#{1,3}\s+(\d+)\.\s+(.+)$", re.MULTILINE)
_NO_HASH = st.characters(blacklist_characters="#")


def _build_raw(bodies: list[str], numbers: list[int] | None = None) -> str:
    """Build a .cursorrules string with numbered headings and no-hash body text."""
    nums = numbers if numbers is not None else list(range(len(bodies)))
    lines: list[str] = []
    for idx, body in zip(nums, bodies):
        lines.append(f"## {idx}. Section {idx}")
        lines.append(body.replace("\n#", "\n-"))
    return "\n".join(lines)


class TestParseSectionsLength:
    """_parse_sections always returns at least one section for any input."""

    @given(st.text())
    def test_any_text_yields_nonempty_result(self, raw: str) -> None:
        assert len(RuleLoader._parse_sections(raw)) >= 1

    @given(st.text(min_size=1, max_size=5000))
    def test_large_text_yields_nonempty_result(self, raw: str) -> None:
        assert len(RuleLoader._parse_sections(raw)) >= 1


class TestParseSectionsFallback:
    """No heading pattern in raw text triggers the single-section fallback."""

    @given(st.text(alphabet=_NO_HASH))
    def test_no_hash_gives_number_zero_section(self, raw: str) -> None:
        sections = RuleLoader._parse_sections(raw)
        assert sections[0].number == 0

    @given(st.text(alphabet=_NO_HASH))
    def test_no_hash_gives_title_content(self, raw: str) -> None:
        sections = RuleLoader._parse_sections(raw)
        assert sections[0].title == "Content"

    @given(st.text(alphabet=_NO_HASH))
    def test_no_hash_content_equals_stripped_raw(self, raw: str) -> None:
        sections = RuleLoader._parse_sections(raw)
        assert sections[0].content == raw.strip()

    @given(st.text())
    def test_no_heading_match_gives_single_section(self, raw: str) -> None:
        assume(not _HEADING_RE.search(raw))
        assert len(RuleLoader._parse_sections(raw)) == 1


class TestParseSectionsCounting:
    """Section count matches number of headings found in the raw string."""

    @given(st.lists(st.text(alphabet=_NO_HASH, max_size=80), min_size=1, max_size=6))
    @settings(max_examples=80)
    def test_count_matches_heading_count(self, bodies: list[str]) -> None:
        assert len(RuleLoader._parse_sections(_build_raw(bodies))) == len(bodies)

    @given(st.integers(min_value=1, max_value=8))
    def test_n_headings_give_n_sections(self, n: int) -> None:
        raw = "\n".join(f"## {i}. Title\nBody {i}." for i in range(n))
        assert len(RuleLoader._parse_sections(raw)) == n


class TestParseSectionsOrdering:
    """Section numbers follow heading input order; _parse_sections never sorts."""

    @given(st.lists(st.integers(0, 50), min_size=2, max_size=6, unique=True).map(sorted))
    def test_ascending_numbers_preserved(self, numbers: list[int]) -> None:
        raw = _build_raw([f"B{n}" for n in numbers], numbers)
        result = [s.number for s in RuleLoader._parse_sections(raw)]
        assert result == numbers

    @given(st.permutations(list(range(4))))
    def test_permuted_numbers_preserved_not_sorted(self, perm: list[int]) -> None:
        raw = _build_raw([f"B{n}" for n in perm], perm)
        result = [s.number for s in RuleLoader._parse_sections(raw)]
        assert result == perm


class TestParseSectionsQuality:
    """All section content is stripped; all titles are non-empty strings."""

    @given(st.text())
    def test_content_has_no_surrounding_whitespace(self, raw: str) -> None:
        for section in RuleLoader._parse_sections(raw):
            assert section.content == section.content.strip()

    @given(st.text())
    def test_titles_are_nonempty_strings(self, raw: str) -> None:
        for section in RuleLoader._parse_sections(raw):
            assert isinstance(section.title, str) and len(section.title) >= 1

    @given(st.text(alphabet=st.characters(blacklist_characters="\n\r#"), min_size=1, max_size=60))
    def test_heading_title_captured_after_strip(self, title: str) -> None:
        safe = title.strip()
        assume(len(safe) >= 1)
        result = RuleLoader._parse_sections(f"## 0. {safe}\nBody.")
        assert result[0].title == safe


class TestParseSectionsRegressions:
    """Targeted regression cases for specific edge and boundary conditions."""

    def test_empty_string_gives_empty_content(self) -> None:
        sections = RuleLoader._parse_sections("")
        assert sections[0].content == ""

    def test_single_heading_number_and_title(self) -> None:
        sections = RuleLoader._parse_sections("## 0. Preamble\nZero-mock policy.")
        assert sections[0].number == 0
        assert sections[0].title == "Preamble"

    def test_two_headings_split_body_correctly(self) -> None:
        raw = "## 1. Imports\nUse explicit imports.\n\n## 2. Style\nUse black."
        s = RuleLoader._parse_sections(raw)
        assert len(s) == 2 and s[0].number == 1 and s[1].number == 2

    def test_level_3_heading_recognised(self) -> None:
        s = RuleLoader._parse_sections("### 5. Deep Section\nContent.")
        assert s[0].number == 5 and s[0].title == "Deep Section"

    def test_whitespace_only_input_empty_content(self) -> None:
        s = RuleLoader._parse_sections("   \n   ")
        assert s[0].content == ""

    def test_results_are_rule_section_instances(self) -> None:
        s = RuleLoader._parse_sections("## 0. Check\nBody.")
        assert all(isinstance(x, RuleSection) for x in s)
