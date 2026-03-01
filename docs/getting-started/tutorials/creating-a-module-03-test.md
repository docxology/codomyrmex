## 🧪 Step 4: Write Comprehensive Tests

### **Update test_template.py**
Rename and update the test file:

```bash
mv tests/test_template.py tests/test_text_analysis.py
```

Edit `tests/test_text_analysis.py`:

```python
"""
Comprehensive tests for the text_analysis module.

This module tests all functionality including error conditions,
edge cases, and integration with other Codomyrmex modules.
"""

import pytest
import tempfile
import os

from codomyrmex.text_analysis.text_analyzer import (
    TextAnalyzer,
    TextAnalysisResult,
    analyze_text,
    analyze_file
)


class TestTextAnalyzer:
    """Test suite for TextAnalyzer class"""

    def setup_method(self):
        """Setup for each test method"""
        self.analyzer = TextAnalyzer(enable_sentiment=True)
        self.sample_text = (
            "This is a sample text for testing. "
            "It contains multiple sentences and words. "
            "The text should provide good test coverage."
        )

    def test_analyzer_initialization(self):
        """Test TextAnalyzer initialization"""
        analyzer = TextAnalyzer(enable_sentiment=False)
        assert analyzer.enable_sentiment is False

        analyzer = TextAnalyzer(enable_sentiment=True)
        assert analyzer.enable_sentiment is True

    def test_analyze_text_basic_metrics(self):
        """Test basic text analysis metrics"""
        result = self.analyzer.analyze_text(self.sample_text)

        assert isinstance(result, TextAnalysisResult)
        assert result.word_count == 16  # Count words in sample text
        assert result.character_count == len(self.sample_text)
        assert result.character_count_no_spaces < result.character_count
        assert result.sentence_count == 3
        assert result.paragraph_count == 1
        assert result.average_words_per_sentence > 0
        assert 0 <= result.readability_score <= 100

    def test_analyze_text_with_sentiment(self):
        """Test sentiment analysis functionality"""
        positive_text = "This is amazing and wonderful! I love it!"
        result = self.analyzer.analyze_text(positive_text)

        assert result.sentiment == "positive"
        assert result.sentiment_score > 0

    def test_analyze_text_negative_sentiment(self):
        """Test negative sentiment detection"""
        negative_text = "This is terrible and awful! I hate it!"
        result = self.analyzer.analyze_text(negative_text)

        assert result.sentiment == "negative"
        assert result.sentiment_score < 0

    def test_analyze_text_neutral_sentiment(self):
        """Test neutral sentiment detection"""
        neutral_text = "The weather today is cloudy."
        result = self.analyzer.analyze_text(neutral_text)

        assert result.sentiment == "neutral"
        assert result.sentiment_score == 0.0

    def test_analyze_text_without_sentiment(self):
        """Test analysis with sentiment disabled"""
        analyzer = TextAnalyzer(enable_sentiment=False)
        result = analyzer.analyze_text(self.sample_text)

        assert result.sentiment is None
        assert result.sentiment_score is None

    def test_analyze_empty_text(self):
        """Test analysis of empty text"""
        with pytest.raises(ValueError):
            self.analyzer.analyze_text("")

        with pytest.raises(ValueError):
            self.analyzer.analyze_text("   ")  # Only whitespace

        with pytest.raises(ValueError):
            self.analyzer.analyze_text(None)

    def test_analyze_file_success(self):
        """Test successful file analysis"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_text)
            temp_path = f.name

        try:
            result = self.analyzer.analyze_file(temp_path)
            assert isinstance(result, TextAnalysisResult)
            assert result.word_count > 0
        finally:
            os.unlink(temp_path)

    def test_analyze_file_not_found(self):
        """Test file analysis with non-existent file"""
        with pytest.raises(FileNotFoundError):
            self.analyzer.analyze_file("/path/that/does/not/exist.txt")

    def test_analyze_file_read_error(self):
        """Test file analysis with read permission issues"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_text)
            temp_path = f.name

        try:
            # Change permissions to make file unreadable
            os.chmod(temp_path, 0o000)

            with pytest.raises(IOError):
                self.analyzer.analyze_file(temp_path)
        finally:
            # Restore permissions and clean up
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)

    def test_word_counting_accuracy(self):
        """Test word counting accuracy with various text formats"""
        test_cases = [
            ("Hello world", 2),
            ("Hello, world!", 2),
            ("One two three four five", 5),
            ("Hyphenated-words count as two", 5),
            ("123 numbers count too", 4),
        ]

        for text, expected_words in test_cases:
            result = self.analyzer.analyze_text(text)
            assert result.word_count == expected_words, f"Failed for: {text}"

    def test_sentence_counting_accuracy(self):
        """Test sentence counting with various punctuation"""
        test_cases = [
            ("Hello.", 1),
            ("Hello! How are you?", 2),
            ("First. Second! Third?", 3),
            ("No punctuation", 1),
            ("Multiple... dots... should... work.", 4),
        ]

        for text, expected_sentences in test_cases:
            result = self.analyzer.analyze_text(text)
            assert result.sentence_count == expected_sentences, f"Failed for: {text}"

    def test_paragraph_counting_accuracy(self):
        """Test paragraph counting with various formatting"""
        single_paragraph = "This is one paragraph."
        two_paragraphs = "First paragraph.

Second paragraph."
        three_paragraphs = "First.

Second.

Third."

        assert self.analyzer.analyze_text(single_paragraph).paragraph_count == 1
        assert self.analyzer.analyze_text(two_paragraphs).paragraph_count == 2
        assert self.analyzer.analyze_text(three_paragraphs).paragraph_count == 3

    def test_readability_score_bounds(self):
        """Test readability score stays within bounds"""
        # Very simple text should have high readability
        simple_text = "Cat. Dog. Run. Jump."
        simple_result = self.analyzer.analyze_text(simple_text)
        assert simple_result.readability_score >= 0

        # Complex text should have lower readability
        complex_text = (
            "The implementation of sophisticated algorithmic approaches "
            "necessitates comprehensive understanding of computational complexity."
        )
        complex_result = self.analyzer.analyze_text(complex_text)
        assert complex_result.readability_score <= 100
        assert simple_result.readability_score >= complex_result.readability_score


class TestConvenienceFunctions:
    """Test suite for module-level convenience functions"""

    def test_analyze_text_function(self):
        """Test the analyze_text convenience function"""
        text = "Test text for analysis."
        result = analyze_text(text)

        assert isinstance(result, TextAnalysisResult)
        assert result.word_count == 4

    def test_analyze_text_function_no_sentiment(self):
        """Test analyze_text with sentiment disabled"""
        text = "Test text for analysis."
        result = analyze_text(text, enable_sentiment=False)

        assert result.sentiment is None
        assert result.sentiment_score is None

    def test_analyze_file_function(self):
        """Test the analyze_file convenience function"""
        text_content = "Test file content for analysis."

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(text_content)
            temp_path = f.name

        try:
            result = analyze_file(temp_path)
            assert isinstance(result, TextAnalysisResult)
            assert result.word_count == 5
        finally:
            os.unlink(temp_path)


class TestIntegrationWithCodomyrmex:
    """Test integration with other Codomyrmex modules"""

    @pytest.mark.skipif(
        not hasattr(__import__('codomyrmex', fromlist=['logging_monitoring']), 'logging_monitoring'),
        reason="logging_monitoring module not available"
    )
    def test_logging_integration(self):
        """Test integration with Codomyrmex logging system"""
        analyzer = TextAnalyzer()
        result = analyzer.analyze_text("Test logging integration.")

        # Verify analysis completes successfully with real logging
        assert result is not None
        assert result.word_count == 3

    def test_error_logging(self):
        """Test that errors are properly raised"""
        analyzer = TextAnalyzer()

        with pytest.raises(ValueError):
            analyzer.analyze_text("")  # This should raise ValueError


class TestEdgeCases:
    """Test edge cases and unusual inputs"""

    def test_very_long_text(self):
        """Test analysis of very long text"""
        # Create a long text (10,000 words)
        long_text = "word " * 10000

        analyzer = TextAnalyzer()
        result = analyzer.analyze_text(long_text)

        assert result.word_count == 10000
        assert result.character_count > 0

    def test_unicode_text(self):
        """Test analysis of text with Unicode characters"""
        unicode_text = "Hello 世界! This contains émojis 🌟 and àccénts."

        analyzer = TextAnalyzer()
        result = analyzer.analyze_text(unicode_text)

        assert result.word_count > 0
        assert result.character_count > 0

    def test_only_punctuation(self):
        """Test text with only punctuation"""
        punct_text = "!@#$%^&*(),.?;:"

        analyzer = TextAnalyzer()
        result = analyzer.analyze_text(punct_text)

        assert result.word_count == 0
        assert result.character_count > 0

    def test_single_character(self):
        """Test analysis of single character"""
        analyzer = TextAnalyzer()
        result = analyzer.analyze_text("a")

        assert result.word_count == 1
        assert result.character_count == 1
        assert result.sentence_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
```

## ⚙️ Step 5: Update Module Configuration

### **Update __init__.py**
Edit `__init__.py` to expose the module API:

```python
"""
Text Analysis Module for Codomyrmex

This module provides comprehensive text analysis capabilities including
word counting, readability metrics, and sentiment analysis.
"""

from .text_analyzer import (
    TextAnalyzer,
    TextAnalysisResult,
    analyze_text,
    analyze_file
)

__version__ = "0.1.0"
__author__ = "Codomyrmex Contributors"

# Public API
__all__ = [
    "TextAnalyzer",
    "TextAnalysisResult",
    "analyze_text",
    "analyze_file"
]
```

### **Update `pyproject.toml`**
Edit `pyproject.toml`:

```txt
# Optional dependencies for enhanced sentiment analysis
textblob>=0.17.1

# Core dependencies are handled by parent Codomyrmex installation
```

### **Update CHANGELOG.md**
```markdown
# Changelog

All notable changes to the Text Analysis module will be documented in this file.

## [0.1.0] - 2024-01-XX

### Added
- Initial implementation of TextAnalyzer class
- Basic text metrics (word count, character count, sentence count)
- Readability score calculation (Flesch Reading Ease)
- Basic sentiment analysis capabilities
- File analysis functionality
- Full integration with Codomyrmex logging system
- Comprehensive test suite
- API documentation and usage examples

### Features
- Thread-safe text analysis operations
- Memory-efficient processing for large texts
- Configurable sentiment analysis
- Error handling following Codomyrmex conventions
```
