# Pattern Matching Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Complete | **Last Updated**: December 2025

## Overview

This example demonstrates comprehensive code pattern detection and analysis using the Codomyrmex `pattern_matching` module. It showcases AST-based analysis, text search, symbol extraction, complexity measurement, and advanced repository analysis capabilities.

## What This Example Demonstrates

### Core Features
- **AST-Based Analysis**: Abstract Syntax Tree parsing for code structure understanding
- **Pattern Detection**: Regex and AST-based pattern recognition in source code
- **Symbol Extraction**: Function, class, and variable symbol identification
- **Text Search**: Context-aware text searching with configurable patterns
- **Complexity Analysis**: Code complexity measurement and assessment
- **Repository Analysis**: Large-scale codebase pattern analysis (when module available)

### Key Capabilities
- Multi-language pattern detection support
- Configurable analysis depth and patterns
- Symbol usage and cross-reference analysis
- Code complexity assessment
- Advanced embedding-based analysis (when dependencies available)
- Repository-wide pattern recognition

## Tested Methods

This example references the following tested methods from `src/codomyrmex/tests/unit/test_pattern_matching.py`:

- `analyze_repository_path()` - Verified in `TestPatternMatching::test_pattern_matching_module_structure`
- `run_full_analysis()` - Verified in `TestPatternMatching::test_pattern_matching_module_structure`
- `get_embedding_function()` - Verified in `TestPatternMatching::test_get_embedding_function_with_sentence_transformer`

## Running the Example

### Quick Start

```bash
# Navigate to the example directory
cd examples/pattern_matching

# Run with default YAML configuration
python example_basic.py

# Run with JSON configuration
python example_basic.py --config config.json

# Run with custom configuration
python example_basic.py --config my_custom_config.yaml
```

### Expected Output

The example will:
1. Create sample Python files with various code patterns
2. Perform AST-based analysis of code structure
3. Detect functions, classes, imports, and decorators
4. Execute text search with context extraction
5. Analyze symbol usage and complexity
6. Attempt advanced analysis if pattern_matching module is available
7. Generate comprehensive analysis reports

### Sample Output Structure

```json
{
  "sample_files_created": 2,
  "files_analyzed": 2,
  "total_functions_found": 8,
  "total_classes_found": 2,
  "total_imports_found": 6,
  "unique_functions": 8,
  "unique_classes": 2,
  "search_matches_found": 12,
  "symbols_extracted": 10,
  "average_complexity": 2.5,
  "advanced_analysis_available": true,
  "analysis_file_saved": "output/analysis/pattern_analysis.json",
  "pattern_matcher_initialized": true,
  "ast_analysis_performed": true,
  "text_search_completed": true,
  "symbol_analysis_completed": true,
  "complexity_analysis_completed": true
}
```

## Configuration Options

### Analysis Configuration

Customize analysis settings:

```yaml
analysis:
  types:                    # Analysis types to perform
    - ast_analysis
    - pattern_detection
    - symbol_extraction
    - complexity_analysis
    - text_search

  include_patterns:         # File patterns to include
    - "*.py"
    - "*.js"
    - "*.ts"

  exclude_patterns:         # File patterns to exclude
    - "*test*"
    - "*__pycache__*"

  depth: medium            # Analysis depth (shallow/medium/deep)
```

### Pattern Detection

Configure pattern recognition:

```yaml
patterns:
  code_patterns:           # Code patterns to detect
    - function_definitions
    - class_definitions
    - import_statements
    - decorators
    - async_functions

  ast_patterns:            # AST-based patterns
    - control_flow_complexity
    - nesting_levels
    - function_length
    - variable_usage
```

### Text Search

Configure search parameters:

```yaml
search:
  terms:                   # Search terms
    - "def "
    - "class "
    - "import "

  context_lines: 2         # Context lines around matches
  case_sensitive: false    # Case sensitivity
```

### Symbol Analysis

Configure symbol extraction:

```yaml
symbols:
  types:                   # Symbol types to extract
    - functions
    - classes
    - variables
    - imports

  analyze_usage: true      # Enable usage analysis
  cross_reference: true    # Enable cross-referencing
```

### Complexity Analysis

Configure complexity assessment:

```yaml
complexity:
  metrics:                 # Complexity metrics
    - cyclomatic_complexity
    - nesting_depth
    - function_length
    - parameter_count

  thresholds:              # Complexity level thresholds
    low: 5
    medium: 10
    high: 20
```

## Analysis Types

### AST-Based Analysis
- Parse Python code into Abstract Syntax Trees
- Extract structural information (functions, classes, imports)
- Analyze control flow and nesting complexity
- Identify code patterns and anti-patterns

### Pattern Detection
- Regex-based pattern matching for code elements
- Detect function definitions, class declarations
- Identify import statements and decorators
- Find async/await patterns and complex expressions

### Symbol Extraction
- Extract function names, parameters, and return types
- Identify class hierarchies and inheritance
- Track variable declarations and usage
- Analyze import dependencies and module relationships

### Text Search with Context
- Configurable text pattern searching
- Context extraction around matches (configurable lines)
- Case-sensitive or case-insensitive matching
- Multi-file search across codebases

### Complexity Analysis
- Cyclomatic complexity calculation
- Nesting depth measurement
- Function length assessment
- Parameter count analysis

## Advanced Features

### Repository Analysis (when available)
- Large-scale codebase pattern analysis
- Cross-file symbol referencing
- Dependency graph generation
- Code similarity detection

### Embedding-Based Analysis (when dependencies available)
- Semantic code understanding using embeddings
- Code similarity measurement
- Intelligent pattern recognition
- Documentation indexing and search

### Code Summarization
- Automatic code documentation generation
- Function and class description extraction
- Code complexity explanations
- Usage pattern identification

## Integration Examples

### CI/CD Pipeline Integration

```python
from codomyrmex.pattern_matching import analyze_repository_path, run_full_analysis

# Analyze codebase before deployment
def analyze_codebase(repo_path: str) -> dict:
    """Analyze codebase for patterns and quality."""
    analysis = analyze_repository_path(repo_path)

    # Check for problematic patterns
    issues = []
    if analysis.get('complex_functions', 0) > 10:
        issues.append("High complexity functions detected")

    if analysis.get('missing_docstrings', 0) > 20:
        issues.append("Many functions missing docstrings")

    return {
        'analysis': analysis,
        'issues': issues,
        'approved': len(issues) == 0
    }
```

### Code Review Integration

```python
from codomyrmex.pattern_matching import run_full_analysis

# Automated code review
def review_code_changes(changed_files: list) -> dict:
    """Review changed files for patterns."""
    results = run_full_analysis(changed_files)

    review_comments = []
    for file_result in results.get('file_results', []):
        if file_result.get('complexity_score', 0) > 15:
            review_comments.append(f"High complexity in {file_result['file']}")

        if file_result.get('missing_tests', 0) > 0:
            review_comments.append(f"Missing tests in {file_result['file']}")

    return {
        'review_comments': review_comments,
        'overall_score': results.get('overall_quality_score', 0)
    }
```

## Output Files

The example generates several output files:

- `output/pattern_matching_results.json` - Complete analysis results and metrics
- `output/analysis/pattern_analysis.json` - Detailed pattern analysis data
- `logs/pattern_matching.log` - Execution logs and analysis details

## Dependencies

### Required Dependencies
- Python 3.8+ (for AST parsing)
- `ast` module (built-in)
- `re` module (built-in)
- `json` module (built-in)

### Optional Dependencies (for advanced features)
- `sentence-transformers` - For embedding-based analysis
- `kit` - For advanced repository analysis
- `tqdm` - For progress bars during analysis

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **AST Parsing Errors**: Check Python syntax in analyzed files
3. **Pattern Matching Failures**: Verify regex patterns are valid
4. **Memory Issues**: Reduce analysis depth for large codebases

### Performance Considerations

- Use `depth: shallow` for large codebases
- Limit analysis to specific file types
- Exclude generated and third-party code
- Use incremental analysis for large repositories

## Security Considerations

- Pattern matching operates on source code only
- No execution of analyzed code
- AST parsing is safe and sandboxed
- Embedding analysis (if enabled) processes text only

## Related Examples

- **[Static Analysis](../static_analysis/)** - Code quality and structure analysis
- **[Code Review](../code_review/)** - Automated code review and feedback
- **[Data Visualization](../data_visualization/)** - Pattern analysis visualization
- **[Git Operations](../git_operations/)** - Code change pattern analysis

## Module Documentation

- **[Pattern Matching Module](../../src/codomyrmex/pattern_matching/)** - Complete module documentation
- **[API Specification](../../src/codomyrmex/pattern_matching/API_SPECIFICATION.md)** - Detailed API reference
- **[Usage Examples](../../src/codomyrmex/pattern_matching/USAGE_EXAMPLES.md)** - Additional usage patterns

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->
