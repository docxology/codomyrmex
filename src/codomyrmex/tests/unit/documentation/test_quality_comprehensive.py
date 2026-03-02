"""Unit tests for documentation quality and consistency checks.

Strict zero-mock policy. All tests use real filesystem.
"""

import pytest
from codomyrmex.documentation.quality.consistency_checker import DocumentationConsistencyChecker
from codomyrmex.documentation.quality.quality_assessment import DocumentationQualityAnalyzer

@pytest.fixture
def tmp_docs(tmp_path):
    """Create a temporary documentation structure."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    # Valid README
    readme = docs_dir / "README.md"
    readme.write_text("""# Test Module

## Overview
This is a test module.

## Purpose
The purpose is testing.

## Navigation
- [Link](./OTHER.md)
""")

    # Valid OTHER
    other = docs_dir / "OTHER.md"
    other.write_text("# Other File\n\n## Overview\nContent.")

    # Invalid file (missing sections, broken link)
    invalid = docs_dir / "INVALID.md"
    invalid.write_text("# Invalid File\n\n[Broken](./NONEXISTENT.md)")
    
    # RASP file with missing sections
    spec = docs_dir / "SPEC.md"
    spec.write_text("# Specification\n\nMissing mandatory sections.")
    
    return docs_dir

class TestConsistencyChecker:
    def test_check_file_valid(self, tmp_docs):
        checker = DocumentationConsistencyChecker()
        issues = checker.check_file(str(tmp_docs / "README.md"))
        # Should have no issues if mandatory sections are present and links work
        assert not any(i.issue_type == "missing_section" for i in issues)
        assert not any(i.issue_type == "broken_link" for i in issues)

    def test_check_file_broken_link(self, tmp_docs):
        checker = DocumentationConsistencyChecker()
        issues = checker.check_file(str(tmp_docs / "INVALID.md"))
        assert any(i.issue_type == "broken_link" for i in issues)

    def test_check_file_missing_section(self, tmp_docs):
        checker = DocumentationConsistencyChecker()
        issues = checker.check_file(str(tmp_docs / "SPEC.md"))
        assert any(i.issue_type == "missing_section" for i in issues)

    def test_check_directory(self, tmp_docs):
        checker = DocumentationConsistencyChecker()
        report = checker.check_directory(str(tmp_docs))
        assert report.files_checked == 4
        assert len(report.issues) > 0
        assert report.passed is False

class TestQualityAnalyzer:
    def test_analyze_file_high_quality(self, tmp_docs):
        analyzer = DocumentationQualityAnalyzer()
        # Create a high quality file
        high_quality = tmp_docs / "HIGH_QUALITY.md"
        high_quality.write_text("""# High Quality Module

## Overview
Substantial overview content that is long enough to pass thresholds.

## Purpose
This module serves a very specific and well-documented purpose.

## Installation
```bash
pip install codomyrmex
```

## Usage
How to use this module.

## API
Detailed API information.

## Examples
Here are some examples of usage.

## Navigation
[Home](../../README.md)

### Technical Details
This class uses a decorator and returns a generator. It handles exceptions properly and provides an interface for asynchronous operations.
Version: v1.0.0
""")
        
        analysis = analyzer.analyze_file(high_quality)
        assert analysis["overall_score"] > 80
        assert analysis["completeness"] == 100.0
        assert analysis["technical_accuracy"] > 70.0

    def test_analyze_file_low_quality(self, tmp_docs):
        analyzer = DocumentationQualityAnalyzer()
        low_quality = tmp_docs / "LOW_QUALITY.md"
        low_quality.write_text("# Low\n\nToo short.")
        
        analysis = analyzer.analyze_file(low_quality)
        # Score might be exactly 40 if some default conditions are met
        assert analysis["overall_score"] <= 40
