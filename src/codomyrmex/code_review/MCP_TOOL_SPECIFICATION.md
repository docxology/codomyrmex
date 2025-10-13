# Code Review Module - Model Context Protocol Tool Specification

## Overview
This document defines the Model Context Protocol (MCP) tools exposed by the Code Review module for AI-powered code analysis and improvement assistance.

## Tool Categories

### 🔍 Analysis Tools
Tools for analyzing code quality, security, and performance.

### 📋 Code Review Tools
Tools for performing comprehensive code reviews.

### 🔧 Improvement Tools
Tools for suggesting and applying code improvements.

## Tool Definitions

### analyze_code
**Description**: Perform comprehensive static analysis on code files or projects.

**Parameters**:
- `target` (string, required): Path to file or directory to analyze
- `analyses` (array of strings, optional): Types of analysis to perform
  - `"complexity"`: Cyclomatic complexity analysis
  - `"dead_code"`: Dead code detection
  - `"clones"`: Code clone detection
  - `"security"`: Security vulnerability scanning
  - `"quality"`: Code quality assessment
  - `"performance"`: Performance analysis
  - `"pyscn"`: Advanced pyscn analysis (includes complexity, dead_code, clones)
- `output_format` (string, optional): Output format (`"json"`, `"html"`, `"text"`)
- `config_file` (string, optional): Path to configuration file

**Returns**: Analysis results object containing findings, metrics, and suggestions.

**Example**:
```javascript
{
  "results": [
    {
      "file_path": "src/main.py",
      "line_number": 42,
      "severity": "warning",
      "message": "High cyclomatic complexity: 15",
      "rule_id": "PYSCN_COMPLEXITY",
      "category": "complexity",
      "suggestion": "Consider breaking down this function into smaller, more focused functions"
    }
  ],
  "summary": {
    "total_issues": 8,
    "files_analyzed": 12,
    "analysis_time": 2.3
  }
}
```

### find_dead_code
**Description**: Detect unreachable code using Control Flow Graph (CFG) analysis.

**Parameters**:
- `file_path` (string, required): Path to file to analyze
- `min_confidence` (number, optional): Minimum confidence threshold (0-100)

**Returns**: List of dead code findings with line numbers and explanations.

### detect_clones
**Description**: Find code clones using APTED algorithm with LSH acceleration.

**Parameters**:
- `files` (array of strings, required): List of files to analyze
- `min_similarity` (number, optional): Minimum similarity threshold (0.0-1.0)
- `min_lines` (number, optional): Minimum lines for clone detection

**Returns**: List of clone pairs with similarity scores and locations.

### analyze_complexity
**Description**: Analyze cyclomatic complexity of functions and methods.

**Parameters**:
- `file_path` (string, required): Path to file to analyze
- `max_complexity` (number, optional): Maximum acceptable complexity
- `risk_thresholds` (object, optional): Custom risk level thresholds

**Returns**: Complexity analysis results with risk assessments.

### check_quality_gates
**Description**: Verify code meets quality standards and thresholds.

**Parameters**:
- `target` (string, required): Path to check
- `gates` (object, optional): Quality gate configuration
  - `max_complexity` (number): Maximum cyclomatic complexity
  - `max_clone_similarity` (number): Maximum clone similarity
  - `min_test_coverage` (number): Minimum test coverage percentage
  - `max_security_issues` (number): Maximum security issues

**Returns**: Quality gate check results with pass/fail status.

### generate_report
**Description**: Generate comprehensive analysis report in various formats.

**Parameters**:
- `target` (string, required): Analysis target
- `format` (string, optional): Report format (`"html"`, `"json"`, `"markdown"`)
- `output_path` (string, optional): Output file path
- `include_sections` (array of strings, optional): Sections to include

**Returns**: Report generation status and file path if applicable.

### analyze_complexity_patterns
**Description**: Analyze complexity patterns and provide detailed reduction suggestions.

**Parameters**:
- `target` (string, required): Target file or directory to analyze
- `threshold` (number, optional): Complexity threshold for flagging issues (default: 15)

**Returns**: List of complexity reduction suggestions with specific refactoring recommendations.

### analyze_dead_code_patterns
**Description**: Analyze dead code patterns and provide enhanced findings with actionable suggestions.

**Parameters**:
- `target` (string, required): Target file or directory to analyze
- `include_suggestions` (boolean, optional): Include detailed fix suggestions (default: true)

**Returns**: List of dead code findings with specific removal recommendations.

### analyze_architecture_compliance
**Description**: Analyze architecture compliance and identify layering violations and structural issues.

**Parameters**:
- `target` (string, required): Target project to analyze
- `check_naming` (boolean, optional): Check naming convention compliance (default: true)
- `check_layering` (boolean, optional): Check architectural layering (default: true)

**Returns**: List of architecture violations with severity levels and fix suggestions.

### generate_refactoring_plan
**Description**: Generate a comprehensive refactoring plan based on all analysis results.

**Parameters**:
- `target` (string, required): Target project to analyze
- `include_performance` (boolean, optional): Include performance optimization suggestions (default: true)
- `include_architecture` (boolean, optional): Include architectural improvements (default: true)

**Returns**: Comprehensive refactoring plan with priority actions, quick wins, and long-term improvements.

### generate_quality_dashboard
**Description**: Generate a comprehensive quality dashboard with scores, metrics, and recommendations.

**Parameters**:
- `target` (string, required): Target project to analyze
- `include_trends` (boolean, optional): Include trend analysis if historical data available (default: false)
- `detailed_metrics` (boolean, optional): Include detailed metrics breakdown (default: true)

**Returns**: Quality dashboard with overall score, category scores, top issues, and actionable recommendations.

### optimize_performance
**Description**: Generate performance optimization suggestions based on code analysis.

**Parameters**:
- `target` (string, required): Target project to analyze
- `focus_areas` (array of strings, optional): Specific areas to focus on (`"memory"`, `"cpu"`, `"io"`, `"caching"`)

**Returns**: Performance optimization suggestions categorized by type with implementation guidance.

### suggest_improvements
**Description**: Generate AI-powered improvement suggestions for code issues.

**Parameters**:
- `findings` (array of objects, required): List of analysis findings
- `improvement_types` (array of strings, optional): Types of improvements to suggest
  - `"refactoring"`: Code refactoring suggestions
  - `"security"`: Security improvements
  - `"performance"`: Performance optimizations
  - `"readability"`: Code readability improvements

**Returns**: List of improvement suggestions with code examples.

### apply_fixes
**Description**: Apply automatic fixes for identified issues where possible.

**Parameters**:
- `findings` (array of objects, required): List of fixable findings
- `dry_run` (boolean, optional): Preview changes without applying
- `backup` (boolean, optional): Create backup before applying fixes

**Returns**: Fix application results with success/failure status.

### configure_analyzer
**Description**: Update code review configuration and settings.

**Parameters**:
- `config_updates` (object, required): Configuration changes to apply
  - `analysis_types` (array): Enabled analysis types
  - `thresholds` (object): Custom thresholds
  - `output_settings` (object): Output configuration
  - `performance_settings` (object): Performance tuning

**Returns**: Updated configuration status.

### get_analysis_summary
**Description**: Get summary statistics for previous analysis runs.

**Parameters**:
- `since` (string, optional): Start date for summary (ISO format)
- `target` (string, optional): Specific target to summarize

**Returns**: Analysis summary with trends and statistics.

## MCP Server Integration

### Server Configuration
```python
# MCP server setup for code review tools
@mcp.server()
class CodeReviewMCPServer:
    def __init__(self):
        self.analyzer = CodeReviewer()
        self.cache = AnalysisCache()

    @mcp.tool()
    def analyze_code(self, **kwargs):
        # Implementation using CodeReviewer
        pass

    @mcp.tool()
    def find_dead_code(self, **kwargs):
        # Implementation using PyscnAnalyzer
        pass

    # ... other tools
```

### Error Handling
All tools implement comprehensive error handling:

```python
class MCPToolError(Exception):
    """Base exception for MCP tool errors."""

    def __init__(self, message: str, tool_name: str, error_code: str):
        self.message = message
        self.tool_name = tool_name
        self.error_code = error_code
        super().__init__(message)
```

### Caching Strategy
- Analysis results cached for 1 hour by default
- Cache key includes file hash and analysis parameters
- Configurable cache TTL per tool
- Cache invalidation on file changes

## Performance Considerations

### Async Support
All analysis tools support async execution for better performance:

```python
@mcp.tool()
async def analyze_code_async(self, target: str, **kwargs):
    """Async version of analyze_code for large projects."""
    # Implementation with asyncio
    pass
```

### Streaming Results
For large analyses, tools support streaming responses:

```python
@mcp.tool()
def analyze_code_streaming(self, target: str, **kwargs):
    """Stream analysis results for real-time updates."""
    # Implementation with streaming response
    pass
```

## Security Considerations

### Input Validation
- All file paths validated and sanitized
- Analysis scope limited to project boundaries
- Resource limits enforced to prevent abuse
- Sensitive data filtering in outputs

### Sandboxing
- External tool execution in sandboxed environments
- Memory and CPU limits for analysis operations
- Network isolation for security tools

## Monitoring and Observability

### Metrics Collection
```python
@dataclass
class ToolMetrics:
    tool_name: str
    execution_time: float
    files_processed: int
    issues_found: int
    cache_hits: int
    errors: int
```

### Logging
Structured logging for all tool operations:
- Tool execution start/completion
- Error conditions with context
- Performance metrics
- Cache operations

## Tool Discovery

### Capabilities Advertisement
```python
@mcp.capabilities()
def get_capabilities(self):
    return {
        "analysis_tools": [
            "analyze_code",
            "find_dead_code",
            "detect_clones",
            "analyze_complexity"
        ],
        "review_tools": [
            "check_quality_gates",
            "suggest_improvements",
            "apply_fixes"
        ],
        "utility_tools": [
            "generate_report",
            "configure_analyzer",
            "get_analysis_summary"
        ]
    }
```

## Examples

### Basic Code Analysis
```python
// MCP client request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "analyze_code",
    "arguments": {
      "target": "src/main.py",
      "analyses": ["complexity", "dead_code"]
    }
  }
}
```

### Clone Detection
```python
// MCP client request for clone detection
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "detect_clones",
    "arguments": {
      "files": ["src/module1.py", "src/module2.py"],
      "min_similarity": 0.8,
      "min_lines": 5
    }
  }
}
```

### Quality Gate Check
```python
// MCP client request for quality assessment
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "check_quality_gates",
    "arguments": {
      "target": ".",
      "gates": {
        "max_complexity": 10,
        "max_clone_similarity": 0.7
      }
    }
  }
}
```

This MCP tool specification enables AI assistants to perform comprehensive code analysis, review, and improvement tasks through a standardized interface.

