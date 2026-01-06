# Code Review Example

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Complete | **Last Updated**: December 2025

## Overview

This example demonstrates automated code review and quality assessment using the Codomyrmex `code_review` module. It showcases comprehensive static analysis capabilities including code quality scoring, complexity analysis, security scanning, and actionable feedback generation.

## What This Example Demonstrates

### Core Features
- **Automated Code Analysis**: Intelligent review of code files and projects
- **Quality Assessment**: Multi-dimensional code quality scoring
- **Security Review**: Vulnerability detection and security recommendations
- **Performance Analysis**: Identification of performance bottlenecks
- **Complexity Measurement**: Code complexity evaluation and reduction suggestions
- **Style Consistency**: Automated style guide enforcement
- **Documentation Review**: Assessment of code documentation completeness

### Key Capabilities
- File-level and project-level analysis
- Quality gate checking with configurable thresholds
- Comprehensive reporting with actionable recommendations
- Integration with multiple programming languages
- Configurable analysis depth and types

## Tested Methods

This example references the following tested methods from `testing/unit/test_code_review.py`:

- `CodeReviewer.review_file()` - Verified in `TestCodeReview::test_code_reviewer_class_import`
- `CodeReviewer.analyze_code_quality()` - Verified in `TestCodeReview::test_code_review_all_exports`
- `analyze_file()` - Verified in `TestCodeReview::test_code_review_all_exports`
- `analyze_project()` - Verified in `TestCodeReview::test_code_review_all_exports`
- `check_quality_gates()` - Verified in `TestCodeReview::test_code_review_all_exports`
- `generate_report()` - Verified in `TestCodeReview::test_code_review_all_exports`

## Running the Example

### Quick Start

```bash
# Navigate to the example directory
cd examples/code_review

# Run with default YAML configuration
python example_basic.py

# Run with JSON configuration
python example_basic.py --config config.json

# Run with custom configuration
python example_basic.py --config my_custom_config.yaml
```

### Expected Output

The example will:
1. Create a sample code file with various quality issues
2. Perform comprehensive analysis using multiple analysis types
3. Check quality gates against configurable thresholds
4. Generate detailed reports with actionable feedback
5. Save results to `output/code_review_results.json`

### Sample Output Structure

```json
{
  "sample_code_file": "sample_code/sample_review.py",
  "file_analysis_results": 15,
  "project_analysis_files": 1,
  "project_analysis_issues": 8,
  "quality_gates_passed": 3,
  "quality_gates_failed": 2,
  "report_generated": true,
  "reviewer_quality_score": 65.5,
  "reviewer_issues_found": 12,
  "file_review_score": 72.0,
  "file_review_comments": 6,
  "analysis_types_used": ["quality", "complexity", "style", "security", "performance"],
  "supported_languages": ["python", "javascript", "typescript", "java", "cpp", "csharp", "go", "rust", "php", "ruby"],
  "quality_gate_thresholds": {
    "max_complexity": 10,
    "max_line_length": 100,
    "min_test_coverage": 80
  }
}
```

## Configuration Options

### Quality Gates

Configure automated quality thresholds:

```yaml
quality_gates:
  max_complexity: 10          # Maximum cyclomatic complexity
  max_line_length: 100        # Maximum line length
  min_test_coverage: 80       # Minimum test coverage percentage
  max_duplication: 5          # Maximum code duplication percentage
  security_violations: 0      # Maximum security violations (0 = strict)
  critical_issues: 0          # Maximum critical issues
```

### Analysis Configuration

Customize analysis settings:

```yaml
analysis:
  types:                      # Analysis types to perform
    - quality
    - complexity
    - style
    - security
    - performance
  language: python            # Programming language
  depth: medium              # Analysis depth (shallow/medium/deep)
  include_patterns:           # File patterns to include
    - "*.py"
    - "*.js"
  exclude_patterns:           # File patterns to exclude
    - "*test*"
    - "*__pycache__*"
```

### Review Settings

Configure review behavior:

```yaml
review:
  generate_comments: true     # Generate review comments
  severity_thresholds:        # Issue severity thresholds
    info: 10
    warning: 5
    error: 2
    critical: 0
  categories:                 # Review categories to include
    - style
    - complexity
    - security
    - performance
```

## Analysis Types

### Quality Analysis
- Code style and formatting consistency
- Naming conventions and readability
- Documentation completeness
- Code organization and structure

### Complexity Analysis
- Cyclomatic complexity measurement
- Function length and parameter count
- Nested control structures
- Cognitive complexity assessment

### Security Analysis
- Common security vulnerabilities
- Input validation issues
- Authentication and authorization problems
- Data exposure risks

### Performance Analysis
- Inefficient algorithms identification
- Memory usage patterns
- I/O operation optimization opportunities
- Resource leak detection

### Style Analysis
- PEP 8 compliance (for Python)
- Consistent indentation and spacing
- Import organization
- Comment quality and placement

## Quality Gates

The example demonstrates quality gate checking with configurable thresholds:

| Gate | Description | Default Threshold |
|------|-------------|-------------------|
| Complexity | Maximum cyclomatic complexity | 10 |
| Line Length | Maximum characters per line | 100 |
| Test Coverage | Minimum test coverage percentage | 80% |
| Duplication | Maximum code duplication | 5% |
| Security | Maximum security violations | 0 |
| Critical Issues | Maximum critical severity issues | 0 |

## Integration Examples

### CI/CD Integration

```python
from codomyrmex.code_review import CodeReviewer, check_quality_gates

# In CI/CD pipeline
reviewer = CodeReviewer()
results = reviewer.analyze_project("/path/to/codebase")

gates = check_quality_gates(results, {
    "max_complexity": 10,
    "security_violations": 0
})

if not gates["passed"]:
    print("Quality gates failed - blocking deployment")
    exit(1)
```

### Pre-commit Hooks

```python
from codomyrmex.code_review import analyze_file

# Pre-commit hook
def check_code_quality(file_path):
    results = analyze_file(file_path, language="python")
    if results and any(r.severity == "error" for r in results):
        print(f"Quality issues found in {file_path}")
        return False
    return True
```

## Output Files

The example generates several output files:

- `output/code_review_results.json` - Complete analysis results
- `output/sample_code/reviewed_code.py` - Sample code that was analyzed
- `logs/example_basic.log` - Execution logs

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **Analysis Failures**: Check file permissions and readability
3. **Configuration Errors**: Validate YAML/JSON syntax
4. **Memory Issues**: Reduce analysis depth for large codebases

### Performance Considerations

- Use `depth: shallow` for large codebases
- Exclude test files and generated code
- Run analysis incrementally on changed files only

## Related Examples

- **[Static Analysis](../static_analysis/)** - Code quality analysis
- **[Security Audit](../security_audit/)** - Security vulnerability scanning
- **[Git Operations](../git_operations/)** - Version control integration
- **[Multi-Module Workflows](../multi_module/)** - Integrated workflows

## Module Documentation

- **[Code Review Module](../../src/codomyrmex/code_review/)** - Complete module documentation
- **[API Specification](../../src/codomyrmex/code_review/API_SPECIFICATION.md)** - Detailed API reference
- **[Usage Examples](../../src/codomyrmex/code_review/USAGE_EXAMPLES.md)** - Additional usage patterns

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)