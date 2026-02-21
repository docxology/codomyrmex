"""Project analyzer using codomyrmex static analysis capabilities.

Demonstrates integration with:
- codomyrmex.static_analysis for code quality analysis
- codomyrmex.pattern_matching for code pattern recognition
- codomyrmex.validation for input validation

Example:
    >>> from pathlib import Path
    >>> from src.analyzer import ProjectAnalyzer
    >>>
    >>> analyzer = ProjectAnalyzer()
    >>> results = analyzer.analyze(Path("src"))
    >>> print(f"Files: {results['summary']['total_files']}")
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Real codomyrmex imports - no fallback for mega-seed project
from codomyrmex.logging_monitoring import get_logger

HAS_CODOMYRMEX_LOGGING = True  # Exported for integration tests

logger = get_logger(__name__)


@dataclass
class AnalysisResult:
    """Results from analyzing a single file.

    Attributes:
        file_path: Path to the analyzed file.
        metrics: Dictionary of calculated metrics (lines, functions, classes).
        issues: List of identified issues/warnings.
        patterns: List of detected code patterns.

    Example:
        >>> result = AnalysisResult(file_path=Path("example.py"))
        >>> result.metrics = {"lines_of_code": 100, "functions": 5}
        >>> result.patterns = ["dataclasses", "type_hints"]
        >>> print(result.to_dict())
    """

    file_path: Path
    metrics: dict[str, Any] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return len(self.issues) > 0

    @property
    def is_complex(self) -> bool:
        """Check if file has high complexity."""
        complexity = self.metrics.get("complexity", 0)
        return complexity > 10

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            "file": str(self.file_path),
            "metrics": self.metrics,
            "issues": self.issues,
            "patterns": self.patterns,
            "has_issues": self.has_issues,
        }


class ProjectAnalyzer:
    """Analyzer for project code quality and patterns.

    Uses codomyrmex.static_analysis for linting and complexity analysis,
    and codomyrmex.pattern_matching for identifying code patterns.

    Attributes:
        config_path: Optional path to configuration file.
        include_patterns: File patterns to include in analysis.
        exclude_patterns: File patterns to exclude from analysis.
        max_complexity: Maximum acceptable complexity score.

    Example:
        >>> analyzer = ProjectAnalyzer()
        >>> results = analyzer.analyze(Path("."))
        >>> for file_result in results["files"]:
        ...     print(f"{file_result['file']}: {file_result['metrics']['lines_of_code']} lines")
    """

    def __init__(self, config_path: Path | None = None):
        """Initialize the analyzer.

        Args:
            config_path: Optional path to YAML configuration file.
        """
        self.config_path = config_path
        self.include_patterns: list[str] = ["*.py"]
        self.exclude_patterns: list[str] = [
            "**/test_*",
            "**/__pycache__/**",
            "**/venv/**",
            "**/.git/**",
        ]
        self.max_complexity: int = 10
        self.patterns_to_detect: list[str] = [
            "async_functions",
            "dataclasses",
            "type_hints",
            "decorators",
            "context_managers",
        ]

        self._load_config()

    def _load_config(self) -> None:
        """Load analyzer configuration from file."""
        if self.config_path and self.config_path.exists():
            logger.info(f"Loading config from {self.config_path}")
            try:
                import yaml

                with open(self.config_path) as f:
                    config = yaml.safe_load(f)

                analysis_config = config.get("analysis", {})
                self.include_patterns = analysis_config.get(
                    "include_patterns", self.include_patterns
                )
                self.exclude_patterns = analysis_config.get(
                    "exclude_patterns", self.exclude_patterns
                )
                self.max_complexity = analysis_config.get(
                    "max_complexity", self.max_complexity
                )
                self.patterns_to_detect = analysis_config.get(
                    "patterns_to_detect", self.patterns_to_detect
                )
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")

    def analyze(self, target_path: Path) -> dict[str, Any]:
        """Analyze target path for code quality.

        Scans the target path (file or directory) and performs:
        - Metric calculation (lines, functions, classes)
        - Pattern detection (async, dataclasses, type hints)
        - Issue identification

        Args:
            target_path: Path to file or directory to analyze.

        Returns:
            Dictionary containing:
            - target: str - Target path analyzed
            - files: List[dict] - Per-file analysis results
            - summary: dict - Aggregate statistics

        Raises:
            ValueError: If target path does not exist.

        Example:
            >>> results = analyzer.analyze(Path("src"))
            >>> print(results["summary"]["total_files"])
        """
        # Validate target path
        if not target_path.exists():
            error_msg = f"Target path does not exist: {target_path}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "target": str(target_path),
                "files": [],
                "summary": {},
            }

        logger.info(f"Analyzing: {target_path}")
        results: list[dict[str, Any]] = []

        if target_path.is_file():
            # Analyze single file
            if self._should_include(target_path) and not self._should_exclude(
                target_path
            ):
                result = self._analyze_file(target_path)
                results.append(result.to_dict())
        else:
            # Analyze directory recursively
            for pattern in self.include_patterns:
                # Handle glob patterns properly
                glob_pattern = pattern.lstrip("*").lstrip(".")  # *.py -> py
                for py_file in target_path.rglob(f"*.{glob_pattern}"):
                    if py_file.is_file() and not self._should_exclude(py_file):
                        result = self._analyze_file(py_file)
                        results.append(result.to_dict())

        summary = self._generate_summary(results)

        return {
            "target": str(target_path),
            "files": results,
            "summary": summary,
        }

    def _analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a single file using codomyrmex modules.

        Args:
            file_path: Path to file to analyze.

        Returns:
            AnalysisResult with metrics, patterns, and issues.
        """
        logger.debug(f"Analyzing file: {file_path}")

        result = AnalysisResult(file_path=file_path)

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            result.issues.append(
                {
                    "type": "read_error",
                    "severity": "error",
                    "message": str(e),
                    "line": 0,
                }
            )
            return result

        lines = content.split("\n")

        # 1. Integration with codomyrmex.static_analysis
        from codomyrmex.coding.static_analysis.static_analyzer import StaticAnalyzer, AnalysisType
        analyzer = StaticAnalyzer()
        try:
            static_results = analyzer.analyze_file(str(file_path), [AnalysisType.QUALITY, AnalysisType.COMPLEXITY])
            for res in static_results:
                result.issues.append({
                    "type": res.category or "quality",
                    "severity": res.severity.value if hasattr(res.severity, "value") else str(res.severity),
                    "message": res.message,
                    "line": res.line_number
                })
        except Exception as e:
            logger.warning(f"StaticAnalyzer failed for {file_path}: {e}")

        # Metrics calculation
        try:
            metrics = analyzer.calculate_metrics(str(file_path))
            complexity = metrics.cyclomatic_complexity
            loc = metrics.lines_of_code
        except Exception as e:
            complexity = 0
            loc = len(lines)

        # Fallback for metrics not natively provided by CodeMetrics
        result.metrics = {
            "lines_of_code": loc,
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith("#")]),
            "functions": len(re.findall(r"^\s*def\s+\w+", content, re.MULTILINE)),
            "async_functions": len(re.findall(r"^\s*async\s+def\s+\w+", content, re.MULTILINE)),
            "classes": len(re.findall(r"^\s*class\s+\w+", content, re.MULTILINE)),
            "imports": len(re.findall(r"^(?:import|from)\s+", content, re.MULTILINE)),
            "complexity": complexity,
        }

        # 2. Integration with codomyrmex.pattern_matching
        from codomyrmex.coding.pattern_matching.code_patterns import PatternDetector
        try:
            detector = PatternDetector()
            matches = detector.detect_patterns(content)
            # Use a dict to preserve order while removing duplicates
            unique_patterns = {match["pattern"]: None for match in matches}
            
            # Additional regex-based generic pattern detection (from old implementation)
            # to preserve original test_project feature completeness checks
            pattern_checks = {
                "async_functions": r"async\s+def\s+\w+",
                "dataclasses": r"@dataclass",
                "type_hints": r"def\s+\w+\([^)]*:\s*\w+",
                "decorators": r"@\w+",
                "context_managers": r"with\s+\w+",
            }
            for pattern_name, regex in pattern_checks.items():
                if re.search(regex, content):
                    unique_patterns[pattern_name] = None
                    
            result.patterns = list(unique_patterns.keys())
        except Exception as e:
            logger.warning(f"Pattern matching failed for {file_path}: {e}")

        return result

    def _should_include(self, path: Path) -> bool:
        """Check if path matches include patterns."""
        path_str = str(path)
        for pattern in self.include_patterns:
            # Simple glob matching
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
        return False

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from analysis."""
        path_str = str(path)
        filename = path.name

        for pattern in self.exclude_patterns:
            # Handle different pattern types
            if pattern.startswith("**/"):
                # Directory patterns like **/__pycache__/**
                check = pattern.replace("**", "").replace("*", "").strip("/")
                if check and f"/{check}/" in path_str:
                    return True
            elif pattern.startswith("*"):
                # Filename patterns like **/test_* - check filename only
                check = pattern.replace("**", "").replace("*", "").strip("/")
                if check and filename.startswith(check.lstrip("_")):
                    return True
            else:
                # Direct match
                if pattern in path_str:
                    return True
        return False

    def _generate_summary(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate summary statistics from file results.

        Args:
            results: List of file analysis result dictionaries.

        Returns:
            Summary dictionary with aggregate statistics.
        """
        total_lines = sum(r.get("metrics", {}).get("lines_of_code", 0) for r in results)
        total_functions = sum(r.get("metrics", {}).get("functions", 0) for r in results)
        total_classes = sum(r.get("metrics", {}).get("classes", 0) for r in results)
        total_issues = sum(len(r.get("issues", [])) for r in results)

        # Count pattern frequency
        all_patterns: dict[str, int] = {}
        for r in results:
            for pattern in r.get("patterns", []):
                all_patterns[pattern] = all_patterns.get(pattern, 0) + 1

        return {
            "total_files": len(results),
            "total_lines": total_lines,
            "total_non_empty_lines": sum(
                r.get("metrics", {}).get("non_empty_lines", 0) for r in results
            ),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_issues": total_issues,
            "average_lines_per_file": total_lines / len(results) if results else 0,
            "patterns_found": all_patterns,
            "files_with_issues": len([r for r in results if r.get("issues")]),
        }
