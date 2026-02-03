"""Tests for FPF parser."""

import pytest
from pathlib import Path

from codomyrmex.fpf import FPFParser, FPFSpec, Pattern


@pytest.mark.unit
def test_parser_initialization():
    """Test parser initialization."""
    parser = FPFParser()
    assert parser is not None


@pytest.mark.unit
def test_extract_table_of_contents():
    """Test table of contents extraction."""
    parser = FPFParser()
    content = """
# Table of Content

**Part A - Kernel Architecture Cluster**

| § | ID & Title | Status |
| :--- | :--- | :--- |
| A.1 | **Test Pattern** | Stable |
"""
    toc = parser.extract_table_of_contents(content)
    assert "parts" in toc
    assert "A" in toc["parts"]


@pytest.mark.unit
def test_extract_patterns():
    """Test pattern extraction."""
    parser = FPFParser()
    content = """
## A.1 - Test Pattern Title

### Problem
This is a test problem.

### Solution
This is a test solution.
"""
    patterns = parser.extract_patterns(content)
    assert len(patterns) > 0
    assert patterns[0].id == "A.1"
    assert patterns[0].title == "Test Pattern Title"


@pytest.mark.unit
def test_extract_sections():
    """Test section extraction."""
    parser = FPFParser()
    content = """
## A.1 - Test Pattern

### Problem
This is the problem section.

### Solution
This is the solution section.
"""
    sections = parser.extract_sections(content)
    assert "problem" in sections or "header" in sections


@pytest.mark.unit
def test_parse_spec():
    """Test full specification parsing."""
    parser = FPFParser()
    content = """
# First Principles Framework (FPF)

## A.1 - Test Pattern

### Problem
Test problem.

### Solution
Test solution.
"""
    spec = parser.parse_spec(content)
    assert spec is not None
    assert len(spec.patterns) > 0


@pytest.mark.unit
def test_parse_spec_with_empty_content():
    """Test parsing empty content."""
    parser = FPFParser()
    spec = parser.parse_spec("")
    assert spec is not None
    assert len(spec.patterns) == 0


@pytest.mark.unit
def test_parse_spec_with_multiple_patterns():
    """Test parsing multiple patterns."""
    parser = FPFParser()
    content = """
## A.1 - First Pattern
Content 1

## A.2 - Second Pattern
Content 2
"""
    spec = parser.parse_spec(content)
    assert len(spec.patterns) == 2
    assert spec.patterns[0].id == "A.1"
    assert spec.patterns[1].id == "A.2"


@pytest.mark.unit
def test_extract_patterns_with_dependencies():
    """Test pattern extraction with dependencies."""
    parser = FPFParser()
    content = """
## A.1 - Test Pattern
**Builds on:** A.0, B.1. **Prerequisite for:** A.2.
"""
    patterns = parser.extract_patterns(content)
    assert len(patterns) > 0
    pattern = patterns[0]
    assert "builds_on" in pattern.dependencies or len(pattern.dependencies) > 0


@pytest.mark.unit
def test_extract_patterns_with_keywords():
    """Test pattern extraction with keywords."""
    parser = FPFParser()
    content = """
## A.1 - Test Pattern
*Keywords:* holon, system, entity. *Queries:* "What is a holon?"
"""
    patterns = parser.extract_patterns(content)
    assert len(patterns) > 0
    # Keywords should be extracted during metadata extraction


@pytest.mark.unit
def test_extract_sections_empty():
    """Test section extraction from empty content."""
    parser = FPFParser()
    sections = parser.extract_sections("")
    assert isinstance(sections, dict)


@pytest.mark.unit
def test_extract_table_of_contents_empty():
    """Test TOC extraction from empty content."""
    parser = FPFParser()
    toc = parser.extract_table_of_contents("")
    assert isinstance(toc, dict)


@pytest.mark.unit
def test_extract_table_of_contents_multiple_parts():
    """Test TOC extraction with multiple parts."""
    parser = FPFParser()
    content = """
# Table of Content

**Part A - Kernel**
| A.1 | Pattern | Stable |

**Part B - Reasoning**
| B.1 | Pattern | Stable |
"""
    toc = parser.extract_table_of_contents(content)
    assert "A" in toc.get("parts", {})
    assert "B" in toc.get("parts", {})

