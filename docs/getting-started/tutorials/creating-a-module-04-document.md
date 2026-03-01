
## 🧪 Step 6: Test Your Module

### **Run the Tests**
```bash
# Navigate to project root
cd ../../../

# Run tests for your module
pytest src/codomyrmex/text_analysis/tests/ -v

# Run with coverage
pytest src/codomyrmex/text_analysis/tests/ --cov=src/codomyrmex/text_analysis --cov-report=term

# Add to main test suite
pytest src/codomyrmex/tests/unit/test_text_analysis.py -v
```

### **Manual Testing**
Create a test script to verify functionality:

```python
# test_my_module.py
import sys
sys.path.insert(0, 'src')

from codomyrmex.text_analysis import analyze_text, TextAnalyzer

# Test basic functionality
text = """
This is a sample text for testing our new text analysis module.
It contains multiple sentences and should provide interesting metrics.
The readability should be reasonable for this type of content.
"""

print("=== Testing Text Analysis Module ===")

# Test convenience function
result = analyze_text(text.strip())
print(f"Words: {result.word_count}")
print(f"Characters: {result.character_count}")
print(f"Sentences: {result.sentence_count}")
print(f"Readability: {result.readability_score:.1f}")
print(f"Sentiment: {result.sentiment} ({result.sentiment_score:.2f})")

# Test class-based approach
analyzer = TextAnalyzer(enable_sentiment=False)
result2 = analyzer.analyze_text(text.strip())
print(f"
Without sentiment: {result2.sentiment}")

print("
✅ Module working correctly!")
```

## 🔧 Step 7: Integration Testing

### **Add to System Discovery**
Your module should automatically be discovered by the system. Test this:

```bash
# Run system discovery
python -c "
import sys; sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery
discovery = SystemDiscovery()
modules = discovery.discover_modules()
print('text_analysis' in modules)
print(modules.get('text_analysis', 'Not found'))
"
```

### **Test with Other Modules**
Create integration examples:

```python
# integration_test.py
import sys
sys.path.insert(0, 'src')

from codomyrmex.text_analysis import analyze_text
from codomyrmex.data_visualization import create_bar_chart

# Analyze multiple texts
texts = [
    "This is a simple text.",
    "This text is more complex with sophisticated vocabulary and longer sentences.",
    "Short. Quick. Fast."
]

readability_scores = []
for i, text in enumerate(texts):
    result = analyze_text(text)
    readability_scores.append(result.readability_score)
    print(f"Text {i+1} readability: {result.readability_score:.1f}")

# Create visualization
create_bar_chart(
    categories=[f"Text {i+1}" for i in range(len(texts))],
    values=readability_scores,
    title="Text Readability Comparison",
    y_label="Readability Score",
    output_path="text_readability.png",
    show_plot=False
)

print("✅ Integration test completed! Check text_readability.png")
```

## 📚 Step 8: Documentation and Examples

### **Create Usage Examples**
Update `USAGE_EXAMPLES.md`:

```markdown
# Text Analysis Usage Examples

## Basic Text Analysis

```python
from codomyrmex.text_analysis import analyze_text

text = """
Artificial intelligence is transforming how we work and live.
It offers tremendous opportunities for innovation and efficiency.
However, we must consider the ethical implications carefully.
"""

result = analyze_text(text)
print(f"Readability Score: {result.readability_score:.1f}")
print(f"Sentiment: {result.sentiment}")
```

## File Processing

```python
from codomyrmex.text_analysis import analyze_file

# Analyze a document
result = analyze_file("my_document.txt")
print(f"Document has {result.word_count} words")
print(f"Average words per sentence: {result.average_words_per_sentence:.1f}")
```

## Integration with Data Visualization

```python
from codomyrmex.text_analysis import analyze_file
from codomyrmex.data_visualization import create_line_plot
import os

# Analyze all text files in a directory
files = [f for f in os.listdir('.') if f.endswith('.txt')]
readability_scores = []

for file in files:
    result = analyze_file(file)
    readability_scores.append(result.readability_score)

# Plot readability trend
create_line_plot(
    x_data=list(range(len(files))),
    y_data=readability_scores,
    title="Document Readability Analysis",
    x_label="Document Index",
    y_label="Readability Score",
    output_path="readability_trend.png"
)
```

## Batch Processing Example

```python
from codomyrmex.text_analysis import TextAnalyzer
from pathlib import Path
import json

analyzer = TextAnalyzer(enable_sentiment=True)
results = {}

# Process all markdown files in a project
for md_file in Path("docs/").rglob("*.md"):
    try:
        result = analyzer.analyze_file(str(md_file))
        results[str(md_file)] = {
            'words': result.word_count,
            'readability': result.readability_score,
            'sentiment': result.sentiment
        }
    except Exception as e:
        print(f"Error processing {md_file}: {e}")

# Save results
with open('text_analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Analyzed {len(results)} files")
```
```

## 🚀 Step 9: Final Integration

### **Add to Main Test Suite**
Create `src/codomyrmex/tests/unit/test_text_analysis.py`:

```python
"""Integration tests for text_analysis module with main test suite"""

import pytest
from codomyrmex.text_analysis import analyze_text, TextAnalyzer


class TestTextAnalysisIntegration:
    """Integration tests for text analysis module"""

    def test_module_import(self):
        """Test that module imports correctly"""
        from codomyrmex.text_analysis import TextAnalyzer, analyze_text
        assert TextAnalyzer is not None
        assert analyze_text is not None

    def test_basic_functionality(self):
        """Test basic module functionality"""
        result = analyze_text("This is a test sentence.")
        assert result.word_count == 5
        assert result.sentence_count == 1

    def test_logging_integration(self):
        """Test integration with Codomyrmex logging"""
        # This test ensures the module uses Codomyrmex logging
        analyzer = TextAnalyzer()
        result = analyzer.analyze_text("Test logging integration.")
        assert result is not None
```

### **Update Project Documentation**
Add your module to the main documentation in `docs/modules/overview.md` (add to the appropriate table).

### **Run Full Test Suite**
```bash
# Run all tests to ensure no regressions
pytest src/codomyrmex/tests/ -v

# Run your module specifically
pytest src/codomyrmex/tests/unit/test_text_analysis.py -v

# Check system discovery
python -c "
import sys; sys.path.insert(0, 'src')
from codomyrmex.system_discovery import SystemDiscovery
discovery = SystemDiscovery()
discovery.run_full_discovery()
"
```

## ✅ Step 10: Verification and Documentation

### **Final Checklist**

- [ ] Module structure follows Codomyrmex conventions
- [ ] Core functionality implemented and working
- [ ] Comprehensive test suite with >90% coverage
- [ ] Integration with Codomyrmex logging system
- [ ] API documentation complete and accurate
- [ ] Usage examples work correctly
- [ ] Integration with other modules tested
- [ ] Error handling follows project conventions
- [ ] Security considerations documented
- [ ] Performance tested with reasonable limits

### **Create Pull Request**
If contributing back to Codomyrmex:

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add text_analysis module with comprehensive text analysis capabilities"
   ```

2. **Push and create PR**:
   ```bash
   git push origin feature/text-analysis-module
   ```

3. **Include in PR description**:
   - Overview of module functionality
   - Testing approach and coverage
   - Integration points with existing modules
   - Performance characteristics
   - Future enhancement possibilities

## 🎉 Congratulations!

You've successfully created a complete Codomyrmex module! Your `text_analysis` module now provides:

- ✅ Comprehensive text analysis capabilities
- ✅ Full integration with the Codomyrmex ecosystem
- ✅ Professional documentation and examples
- ✅ Robust test coverage
- ✅ Integration with other modules
- ✅ Following all Codomyrmex conventions

## 🚀 Next Steps

### **Enhance Your Module**
- Add support for more languages
- Implement advanced sentiment analysis with ML models
- Add text classification capabilities
- Create visualization templates for common analyses
- Add export formats (CSV, JSON, XML)

### **Share with Community**
- Submit a pull request to the main Codomyrmex repository
- Create blog posts about your module
- Present at community meetups
- Help others create their own modules

### **Integrate with Other Modules**
- Create workflows combining text analysis with AI code editing
- Build documentation analysis tools
- Add text analysis to build pipelines
- Create automated content quality checks

---

This tutorial showed you the complete process of creating a professional-grade Codomyrmex module. The patterns and practices you've learned can be applied to create any type of module for the Codomyrmex ecosystem!

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Repository Root](../../README.md)
