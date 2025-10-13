# Code Review Module - API Specification

## Overview
The Code Review module provides comprehensive static analysis capabilities for code quality assessment, security scanning, and performance analysis across multiple programming languages.

## Core Classes

### CodeReviewer
Main class for performing code reviews and static analysis.

```python
class CodeReviewer:
    def __init__(self, project_root: str = None, config_path: str = None):
        """Initialize the code reviewer with optional configuration."""

    def analyze_file(self, file_path: str, analysis_types: List[str] = None) -> List[AnalysisResult]:
        """Analyze a single file for various issues."""

    def analyze_project(self, target_paths: List[str] = None, analysis_types: List[str] = None) -> AnalysisSummary:
        """Analyze an entire project or multiple files."""

    def check_quality_gates(self, thresholds: Dict[str, int] = None) -> QualityGateResult:
        """Check if code meets quality standards."""

    def generate_report(self, output_path: str, format: str = "html") -> bool:
        """Generate comprehensive analysis report."""
```

## Enums and Data Classes

### AnalysisType
```python
class AnalysisType(Enum):
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    PYSCN = "pyscn"  # Advanced pyscn analysis
```

### SeverityLevel
```python
class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

### AnalysisResult
```python
@dataclass
class AnalysisResult:
    file_path: str
    line_number: int
    column_number: int
    severity: SeverityLevel
    message: str
    rule_id: str
    category: str
    suggestion: Optional[str] = None
    context: Optional[str] = None
    fix_available: bool = False
    confidence: float = 1.0
```

### AnalysisSummary
```python
@dataclass
class AnalysisSummary:
    total_issues: int
    by_severity: Dict[SeverityLevel, int]
    by_category: Dict[str, int]
    by_rule: Dict[str, int]
    files_analyzed: int = 0
    analysis_time: float = 0.0
    language: Optional[str] = None
    pyscn_metrics: Optional[Dict[str, Any]] = None
```

## Pyscn Integration

### PyscnAnalyzer
Specialized class for pyscn-based analysis.

```python
class PyscnAnalyzer:
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize pyscn analyzer with configuration."""

    def analyze_complexity(self, file_path: str) -> List[ComplexityResult]:
        """Analyze cyclomatic complexity using pyscn."""

    def detect_dead_code(self, file_path: str) -> List[DeadCodeResult]:
        """Detect dead code using CFG analysis."""

    def find_clones(self, files: List[str], threshold: float = 0.8) -> List[CloneResult]:
        """Find code clones using APTED with LSH acceleration."""

    def analyze_coupling(self, file_path: str) -> List[CouplingResult]:
        """Analyze Coupling Between Objects (CBO) metrics."""

    def generate_report(self, output_dir: str = "reports") -> str:
        """Generate comprehensive pyscn HTML report."""
```

### PyscnResult Classes
```python
@dataclass
class ComplexityResult:
    function_name: str
    complexity: int
    line_number: int
    risk_level: str
    suggestion: str

@dataclass
class DeadCodeResult:
    line_number: int
    code_snippet: str
    reason: str
    severity: str

@dataclass
class CloneResult:
    file1: str
    file2: str
    similarity: float
    line_range1: Tuple[int, int]
    line_range2: Tuple[int, int]
    clone_type: str  # "type1", "type2", "type3", "type4"
```

## Configuration

### Configuration Schema
```python
class CodeReviewConfig:
    # Analysis settings
    enabled_analyses: List[AnalysisType]
    max_complexity: int = 15
    min_clone_similarity: float = 0.8

    # Pyscn settings
    pyscn_config: Dict[str, Any] = None

    # Output settings
    output_format: str = "html"
    output_directory: str = "reports"

    # Performance settings
    parallel_processing: bool = True
    max_workers: int = 4

    # Quality gates
    quality_gates: Dict[str, int] = None
```

## Error Handling

### Custom Exceptions
```python
class CodeReviewError(CodomyrmexError):
    """Base exception for code review operations."""

class PyscnError(CodeReviewError):
    """Error in pyscn analysis."""

class ToolNotFoundError(CodeReviewError):
    """Required analysis tool not found."""

class ConfigurationError(CodeReviewError):
    """Invalid configuration provided."""
```

## Integration Points

### CLI Integration
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

### Model Context Protocol
```python
# MCP tool registration
@mcp.tool()
def analyze_code(file_path: str, analyses: List[str] = None) -> Dict[str, Any]:
    """Analyze code file using configured analyzers."""
    reviewer = CodeReviewer()
    results = reviewer.analyze_file(file_path, analyses)
    return {"results": [result.to_dict() for result in results]}
```

## Performance Characteristics

- **Analysis Speed**: >100,000 lines/second for pyscn analysis
- **Memory Usage**: <10x file size with streaming
- **Parallel Processing**: Configurable worker pools
- **LSH Acceleration**: Automatic for projects >500 files
- **Incremental Analysis**: Cache support for unchanged files (planned)

## Supported Languages

- Python (comprehensive pyscn support)
- JavaScript/TypeScript
- Java
- Go
- Rust
- C/C++
- C#
- PHP
- Ruby

## Output Formats

- **HTML**: Rich web-based reports with interactive visualizations
- **JSON**: Machine-readable format for CI/CD integration
- **CSV**: Tabular format for spreadsheet analysis
- **SARIF**: Industry-standard security format
- **Text**: Human-readable console output

