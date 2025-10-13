# Code Review Module

Comprehensive static analysis and code review capabilities for Codomyrmex, featuring advanced pyscn integration for high-performance code quality assessment.

## Overview

The Code Review module provides advanced static analysis capabilities including:

- **Pyscn Integration**: CFG-based dead code detection, APTED clone detection, and cyclomatic complexity analysis
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, and more
- **Performance Optimization**: 100,000+ lines/sec analysis with parallel processing
- **Rich Reporting**: HTML reports, JSON/CSV exports, and detailed analysis summaries
- **CI/CD Integration**: GitHub Actions, pre-commit hooks, and automated quality gates

## Features

### 🔍 Advanced Static Analysis
- **Dead Code Detection**: Find unreachable code using Control Flow Graph (CFG) analysis
- **Clone Detection**: Identify refactoring opportunities with APTED + LSH algorithms
- **Complexity Analysis**: Spot functions that need breaking down with McCabe metrics
- **Coupling Metrics**: Track architecture quality and module dependencies (CBO)
- **Security Scanning**: Identify vulnerabilities and insecure patterns

### 📊 Performance & Scalability
- **High Speed**: 100,000+ lines/sec analysis performance
- **Parallel Processing**: Configurable worker pools for large codebases
- **LSH Acceleration**: Automatic Locality-Sensitive Hashing for projects >500 files
- **Memory Efficient**: Streaming analysis with <10x memory overhead

### 🔧 Integration & Automation
- **CI/CD Ready**: GitHub Actions, pre-commit hooks, and automated quality gates
- **Multiple Output Formats**: HTML, JSON, CSV, SARIF, and text reports
- **Configurable Quality Gates**: Customizable thresholds and rules
- **Model Context Protocol**: MCP integration for AI-powered assistance

## Installation

### Prerequisites
- Python 3.10+
- uv (recommended) or pip

### Install pyscn
```bash
# Install with pipx (recommended)
pipx install pyscn

# Or with uv
uv tool install pyscn
```

### Install Dependencies
```bash
# From project root
uv sync

# Or install specific dependencies
uv add pyscn python-dotenv
```

## Quick Start

### Basic Usage
```python
from codomyrmex.code_review import CodeReviewer

# Initialize reviewer
reviewer = CodeReviewer()

# Analyze a single file
results = reviewer.analyze_file("my_module.py")
print(f"Found {len(results)} issues")

# Analyze entire project
summary = reviewer.analyze_project()
print(f"Analyzed {summary.files_analyzed} files in {summary.analysis_time:.2f}s")
```

### Command Line Usage
```bash
# Analyze single file
codomyrmex code-review analyze file.py

# Analyze project with specific analyses
codomyrmex code-review analyze . --analyses complexity,security

# Generate HTML report
codomyrmex code-review report --format html

# Check quality gates
codomyrmex code-review check --max-complexity 10
```

## Configuration

### Basic Configuration
Create a `.pyscn.toml` file in your project root:

```toml
# .pyscn.toml
[complexity]
max_complexity = 15

[dead_code]
min_severity = "warning"

[output]
directory = "reports"
```

### Advanced Configuration
```toml
# .pyscn.toml or pyproject.toml [tool.pyscn] section
[dead_code]
enabled = true
min_severity = "warning"
show_context = true
context_lines = 3

[clones]
min_lines = 10
min_nodes = 20
similarity_threshold = 0.7
max_results = 1000

# LSH acceleration for large projects
[clones.lsh]
enabled = "auto"
auto_threshold = 500
bands = 32
rows = 4
hashes = 128

[complexity]
enabled = true
low_threshold = 9
medium_threshold = 19
max_complexity = 0

[cbo]
enabled = true
low_threshold = 5
medium_threshold = 10

[output]
format = "html"
directory = "reports"
show_details = true

[analysis]
recursive = true
include_patterns = ["src/**/*.py", "lib/**/*.py"]
exclude_patterns = [
    "test_*.py",
    "*_test.py",
    "**/migrations/**"
]
```

## Pyscn Integration

### Core Analysis Methods

#### Complexity Analysis
```python
from codomyrmex.code_review import PyscnAnalyzer

analyzer = PyscnAnalyzer()
complexity_results = analyzer.analyze_complexity("my_module.py")

for result in complexity_results:
    print(f"{result.function_name}: complexity {result.complexity} ({result.risk_level})")
    if result.suggestion:
        print(f"  Suggestion: {result.suggestion}")
```

#### Dead Code Detection
```python
dead_code_results = analyzer.detect_dead_code("my_module.py")

for result in dead_code_results:
    print(f"Line {result.line_number}: {result.reason}")
    print(f"  Code: {result.code_snippet}")
```

#### Clone Detection
```python
files_to_analyze = ["src/module1.py", "src/module2.py", "lib/utils.py"]
clone_results = analyzer.find_clones(files_to_analyze, threshold=0.8)

for clone in clone_results:
    print(f"Clone found between {clone.file1} and {clone.file2}")
    print(f"  Similarity: {clone.similarity:.2%}")
    print(f"  Type: {clone.clone_type}")
```

#### Coupling Analysis
```python
coupling_results = analyzer.analyze_coupling("my_module.py")

for result in coupling_results:
    print(f"Class {result.class_name} has {result.coupling_score} dependencies")
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
        run: pyscn check .

      - name: Generate report
        run: pyscn analyze --format html .
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pyscn
        name: pyscn check
        entry: pipx run pyscn check .
        language: system
        pass_filenames: false
        types: [python]
```

## Output Formats

### HTML Reports
Rich web-based reports with interactive visualizations:

```bash
pyscn analyze --format html .
# Generates reports/index.html
```

### JSON Reports
Machine-readable format for CI/CD integration:

```bash
pyscn analyze --format json . > analysis-results.json
```

### Quality Gates
```bash
# Check if code meets quality standards
pyscn check --max-complexity 15 .

# Custom thresholds
pyscn check --max-complexity 10 --max-clones 5 .
```

## Performance Tuning

### For Large Projects
```toml
[clones.lsh]
enabled = "auto"
auto_threshold = 500  # Enable LSH for projects >500 files
bands = 32
rows = 4
hashes = 128
```

### Memory Optimization
```toml
[analysis]
batch_size = 100  # Process files in batches
max_memory_mb = 1024
```

## Troubleshooting

### Common Issues

1. **Pyscn not found**: Install with `pipx install pyscn`
2. **Permission errors**: Use `pipx` instead of `pip` for global installation
3. **Memory issues**: Reduce batch size in configuration
4. **Slow analysis**: Enable LSH acceleration for large projects

### Debug Mode
```bash
PYSCN_DEBUG=1 pyscn analyze .
```

## Contributing

### Development Setup
```bash
# Clone and setup
git clone https://github.com/your-org/codomyrmex.git
cd codomyrmex
uv sync

# Install pyscn for development
pipx install pyscn

# Run tests
uv run pytest src/codomyrmex/code_review/tests/
```

### Adding New Analyzers
1. Implement the analyzer interface
2. Add configuration options
3. Create comprehensive tests
4. Update documentation

## License

MIT License - see LICENSE file for details.

