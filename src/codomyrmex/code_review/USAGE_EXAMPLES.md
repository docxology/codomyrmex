# Code Review Module - Usage Examples

This document provides practical examples of using the Code Review module for various static analysis tasks.

## Basic Usage

### Analyzing a Single File

```python
from codomyrmex.code_review import CodeReviewer, AnalysisType

# Create reviewer instance
reviewer = CodeReviewer()

# Analyze a single Python file
results = reviewer.analyze_file("my_module.py")
print(f"Found {len(results)} issues")

# Filter by severity
warnings = [r for r in results if r.severity == "warning"]
errors = [r for r in results if r.severity == "error"]
print(f"Warnings: {len(warnings)}, Errors: {len(errors)}")
```

### Project-Wide Analysis

```python
from codomyrmex.code_review import analyze_project

# Analyze entire project
summary = analyze_project("/path/to/project")

print(f"Analyzed {summary.files_analyzed} files")
print(f"Found {summary.total_issues} total issues")
print(f"Analysis took {summary.analysis_time:.2f} seconds")

# Check issues by category
for category, count in summary.by_category.items():
    print(f"{category}: {count} issues")
```

### Quality Gate Checking

```python
from codomyrmex.code_review import check_quality_gates

# Define quality thresholds
thresholds = {
    "max_complexity": 15,
    "max_issues_per_file": 50,
    "max_clone_similarity": 0.8
}

# Check if project meets quality standards
result = check_quality_gates("/path/to/project", thresholds)

if result.passed:
    print("✅ All quality gates passed!")
else:
    print("❌ Quality gates failed:")
    for failure in result.failures:
        print(f"  - {failure['gate']}: {failure['message']}")
```

## Pyscn Integration Examples

### Advanced Complexity Analysis

```python
from codomyrmex.code_review import PyscnAnalyzer

analyzer = PyscnAnalyzer()

# Analyze function complexity
complexity_results = analyzer.analyze_complexity("my_module.py")

for func in complexity_results:
    print(f"Function: {func['name']}")
    print(f"Complexity: {func['complexity']}")
    print(f"Risk Level: {func.get('risk_level', 'unknown')}")

    if func['complexity'] > 15:
        print("⚠️  High complexity - consider refactoring")
```

### Dead Code Detection

```python
# Detect unreachable code
dead_code = analyzer.detect_dead_code("my_module.py")

for issue in dead_code:
    print(f"Line {issue['line']}: {issue['message']}")
    print(f"Context: {issue.get('context', 'N/A')}")
```

### Code Clone Detection

```python
# Find duplicate code across files
files_to_check = [
    "src/module1.py",
    "src/module2.py",
    "lib/utils.py"
]

clones = analyzer.find_clones(files_to_check, threshold=0.8)

for clone in clones:
    print(f"Clone between {clone['file1']} and {clone['file2']}")
    print(f"Similarity: {clone['similarity']:.2%}")
    print(f"Lines: {clone['line_range1']} ↔ {clone['line_range2']}")
```

### Comprehensive Pyscn Report

```python
# Generate HTML report with all analyses
report_path = analyzer.generate_report("reports")
print(f"Report generated at: {report_path}")

# Open report in browser
import webbrowser
webbrowser.open(f"file://{report_path}")
```

## Command Line Usage

### Single File Analysis

```bash
# Analyze single file with default settings
python -m codomyrmex.code_review.analyze_file my_module.py

# Analyze with specific analysis types
python -m codomyrmex.code_review.analyze_file my_module.py --analyses complexity,security

# Generate JSON output
python -m codomyrmex.code_review.analyze_file my_module.py --format json > results.json
```

### Project Analysis

```bash
# Analyze entire project
python -m codomyrmex.code_review.analyze_project /path/to/project

# Analyze with custom configuration
python -m codomyrmex.code_review.analyze_project /path/to/project --config .pyscn.toml

# Exclude certain directories
python -m codomyrmex.code_review.analyze_project /path/to/project --exclude node_modules,tests
```

### Report Generation

```bash
# Generate HTML report
python -m codomyrmex.code_review.generate_report /path/to/project --format html --output report.html

# Generate comprehensive pyscn report
python -m codomyrmex.code_review.generate_report /path/to/project --format html --pyscn

# Generate all report formats
python -m codomyrmex.code_review.generate_report /path/to/project --format all
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/code-review.yml
name: Code Review
on: [push, pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pipx install pyscn

      - name: Run code review
        run: |
          python -c "
          from codomyrmex.code_review import check_quality_gates
          result = check_quality_gates('.', {'max_complexity': 15})
          if not result.passed:
              print('Quality gates failed!')
              exit(1)
          "

      - name: Generate report
        run: |
          python -c "
          from codomyrmex.code_review import generate_report
          generate_report('.', 'code-review-report.html')
          "
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: code-review
        name: Code Review
        entry: python -m codomyrmex.code_review.analyze_file
        language: system
        files: \.py$
        pass_filenames: true
```

## Custom Configuration

### TOML Configuration

```toml
# .pyscn.toml
[complexity]
max_complexity = 15
low_threshold = 9
medium_threshold = 19

[dead_code]
min_severity = "warning"
show_context = true

[clones]
min_lines = 10
similarity_threshold = 0.8
lsh_enabled = "auto"

[output]
format = "html"
directory = "reports"

[analysis]
recursive = true
include_patterns = ["src/**/*.py"]
exclude_patterns = ["tests/**", "__pycache__/**"]
```

### Python Configuration

```python
from codomyrmex.code_review import CodeReviewer

# Custom configuration
config = {
    "analysis_types": ["complexity", "security"],
    "max_complexity": 10,
    "output_format": "json",
    "pyscn": {
        "enabled": True,
        "lsh_threshold": 1000
    }
}

reviewer = CodeReviewer(config_path="custom_config.toml")
```

## Error Handling

### Handling Analysis Errors

```python
from codomyrmex.code_review import CodeReviewError, PyscnError

try:
    results = reviewer.analyze_file("problematic_file.py")
except PyscnError as e:
    print(f"Pyscn analysis failed: {e}")
except CodeReviewError as e:
    print(f"Code review error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Tool Availability Checking

```python
from codomyrmex.code_review import CodeReviewer

reviewer = CodeReviewer()
tools = reviewer.tools_available

if tools["pyscn"]:
    print("✅ Pyscn is available")
else:
    print("❌ Pyscn not found - install with: pipx install pyscn")

if tools["pylint"]:
    print("✅ Pylint is available")
else:
    print("❌ Pylint not found - install with: pip install pylint")
```

## Performance Optimization

### For Large Projects

```python
# Enable parallel processing
config = {
    "parallel_processing": True,
    "max_workers": 8,
    "pyscn": {
        "lsh_enabled": "auto",
        "lsh_threshold": 500
    }
}

reviewer = CodeReviewer()
reviewer.config.update(config)
```

### Memory Management

```python
# Process files in batches for large projects
def analyze_large_project(project_path, batch_size=100):
    reviewer = CodeReviewer(project_path)

    # Get all Python files
    import os
    python_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    # Process in batches
    for i in range(0, len(python_files), batch_size):
        batch = python_files[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}...")

        for file_path in batch:
            reviewer.analyze_file(file_path)

    return reviewer
```

## Advanced Examples

### Custom Analysis Pipeline

```python
from codomyrmex.code_review import CodeReviewer, AnalysisResult, SeverityLevel

class CustomReviewer(CodeReviewer):
    def analyze_file(self, file_path, analysis_types=None):
        # Run standard analysis
        results = super().analyze_file(file_path, analysis_types)

        # Add custom rules
        custom_results = self._apply_custom_rules(file_path)
        results.extend(custom_results)

        return results

    def _apply_custom_rules(self, file_path):
        """Apply organization-specific rules."""
        results = []

        with open(file_path, 'r') as f:
            content = f.read()

        # Check for forbidden imports
        forbidden_imports = ['import os', 'from os import']
        for i, line in enumerate(content.split('
'), 1):
            for forbidden in forbidden_imports:
                if forbidden in line:
                    results.append(AnalysisResult(
                        file_path=file_path,
                        line_number=i,
                        column_number=0,
                        severity=SeverityLevel.ERROR,
                        message=f"Forbidden import: {forbidden}",
                        rule_id="CUSTOM_FORBIDDEN_IMPORT",
                        category="style"
                    ))

        return results
```

### Integration with IDE

```python
# VS Code extension helper
def analyze_current_file():
    """Analyze the currently open file in VS Code."""
    # This would integrate with VS Code API
    current_file = get_current_editor_file()

    reviewer = CodeReviewer()
    results = reviewer.analyze_file(current_file)

    # Display results in problems panel
    show_problems(results)

    return results
```

This comprehensive set of examples demonstrates the flexibility and power of the Code Review module for various use cases and integration scenarios.

