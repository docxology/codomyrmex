"""Code Analysis Module.

Provides advanced static analysis capabilities through pyscn integration,
including complexity analysis, dead code detection, clone detection, and
coupling metrics. Serves as the analysis engine for the code review system.

Example:
    >>> from codomyrmex.coding.review.analyzer import PyscnAnalyzer
    >>> analyzer = PyscnAnalyzer()
    >>> complexity_results = analyzer.analyze_complexity("my_module.py")
    >>> for func in complexity_results:
    ...     print(f"{func['name']}: complexity={func['complexity']}")
"""

import glob
import json
import os
import subprocess
import tempfile
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from .models import (
    ToolNotFoundError,
)

logger = get_logger(__name__)

# Try to import performance monitoring
try:
    from codomyrmex.performance import monitor_performance
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback).

        A no-op fallback decorator used when the performance module
        is not available. Simply returns the decorated function unchanged.

        Args:
            *args: Ignored positional arguments.
            **kwargs: Ignored keyword arguments.

        Returns:
            A decorator function that returns the original function.
        """
        def decorator(func):
            """Inner decorator that returns the function unchanged."""
            return func
        return decorator


class PyscnAnalyzer:
    """Specialized analyzer using pyscn for advanced static analysis.

    Provides high-performance code analysis through the pyscn tool,
    including cyclomatic complexity measurement, dead code detection,
    code clone identification, and coupling analysis.

    Attributes:
        config: Configuration dictionary for pyscn options.

    Example:
        >>> analyzer = PyscnAnalyzer({"threshold": 10})
        >>> dead_code = analyzer.detect_dead_code("src/module.py")
        >>> clones = analyzer.find_clones(["file1.py", "file2.py"])
    """

    def __init__(self, config: dict[str, Any] = None):
        """Initialize pyscn analyzer with configuration.

        Args:
            config: Optional dictionary of pyscn configuration options.
                Supported options depend on pyscn version.

        Raises:
            ToolNotFoundError: If pyscn is not installed or not working.
        """
        self.config = config or {}
        self._check_pyscn_availability()

    def _check_pyscn_availability(self) -> None:
        """Check if pyscn is available and working.

        Verifies that the pyscn command-line tool is installed and
        responds to version queries.

        Raises:
            ToolNotFoundError: If pyscn is not found or not functioning.
        """
        try:
            # Try to run pyscn --version
            result = subprocess.run(
                ["pyscn", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ToolNotFoundError("pyscn not available or not working")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise ToolNotFoundError(
                "pyscn not found. Install with: pipx install pyscn"
            )

    @monitor_performance("pyscn_analyze_complexity")
    def analyze_complexity(self, file_path: str) -> list[dict[str, Any]]:
        """Analyze cyclomatic complexity using pyscn.

        Calculates cyclomatic complexity for all functions in the specified
        file using pyscn's analysis engine.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            A list of dictionaries, each containing:
            - name: Function name
            - complexity: Cyclomatic complexity score
            - line_number: Starting line of the function
            - file_path: Path to the file
            - risk_level: Risk classification based on complexity

        Example:
            >>> results = analyzer.analyze_complexity("my_module.py")
            >>> for func in results:
            ...     if func["complexity"] > 10:
            ...         print(f"Complex function: {func['name']}")
        """
        try:
            # Pyscn writes JSON to a file, we need to read it from there
            # Get the most recent .pyscn/reports file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file) as f:
                        data = json.load(f)

                    # Pyscn returns data under "complexity" key in the main object
                    complexity_data = data.get("complexity", {})
                    if "Functions" in complexity_data:
                        # Extract functions from the Functions array
                        functions = []
                        for func_data in complexity_data["Functions"]:
                            # Extract complexity from Metrics
                            complexity = func_data.get("Metrics", {}).get("Complexity", 0)
                            functions.append({
                                "name": func_data.get("Name", ""),
                                "complexity": complexity,
                                "line_number": func_data.get("StartLine", 0),
                                "file_path": func_data.get("FilePath", ""),
                                "risk_level": func_data.get("RiskLevel", "")
                            })
                        return functions
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn complexity analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_detect_dead_code")
    def detect_dead_code(self, file_path: str) -> list[dict[str, Any]]:
        """Detect dead code using control flow graph (CFG) analysis.

        Identifies unreachable code, unused variables, and other dead code
        patterns using pyscn's CFG-based analysis.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            A list of findings, each containing location information,
            description, and severity of the dead code detected.

        Example:
            >>> dead_code = analyzer.detect_dead_code("module.py")
            >>> for finding in dead_code:
            ...     print(f"Dead code at line {finding.get('location', {}).get('start_line')}")
        """
        try:
            # Pyscn writes JSON to a file, we need to read it from there
            # Get the most recent .pyscn/reports file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file) as f:
                        data = json.load(f)

                    # Pyscn returns data under "dead_code" key
                    dead_code_data = data.get("dead_code", {})
                    if "files" in dead_code_data:
                        # Extract findings from all files
                        findings = []
                        for file_data in dead_code_data["files"]:
                            for function_data in file_data.get("functions", []):
                                findings.extend(function_data.get("findings", []))
                        return findings
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn dead code analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_find_clones")
    def find_clones(self, files: list[str], threshold: float = 0.8) -> list[dict[str, Any]]:
        """Find code clones using APTED with LSH acceleration.

        Detects duplicate or similar code patterns across the specified files
        using tree-edit distance algorithms accelerated by locality-sensitive
        hashing.

        Args:
            files: List of file paths to analyze for clones.
            threshold: Similarity threshold (0.0-1.0) for clone detection.
                Higher values require more similarity. Defaults to 0.8.

        Returns:
            A list of clone groups, each containing information about
            similar code fragments and their locations.

        Example:
            >>> clones = analyzer.find_clones(["a.py", "b.py"], threshold=0.9)
            >>> for group in clones:
            ...     print(f"Clone group with {len(group.get('fragments', []))} instances")
        """
        try:
            # For single file analysis, pyscn doesn't need a file list
            if len(files) == 1:
                cmd = [
                    "pyscn", "analyze", "--select", "clones",
                    "--json", f"--clone-threshold={threshold}",
                    files[0]
                ]
            else:
                # For multiple files, create temporary file list
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    for file_path in files:
                        f.write(file_path + '\n')
                    file_list_path = f.name

                cmd = [
                    "pyscn", "analyze", "--select", "clones",
                    "--json", f"--clone-threshold={threshold}",
                    f"@{file_list_path}"
                ]

                subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                # Clean up temporary file
                os.unlink(file_list_path)

            # Read from the generated JSON file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file) as f:
                        data = json.load(f)

                    # Pyscn returns clone data under "clones" key
                    clones_data = data.get("clones", {})
                    if "groups" in clones_data:
                        return clones_data["groups"]
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn clone detection: {e}")
            return []

    @monitor_performance("pyscn_analyze_coupling")
    def analyze_coupling(self, file_path: str) -> list[dict[str, Any]]:
        """Analyze Coupling Between Objects (CBO) metrics.

        Measures the coupling between classes/modules to identify
        highly coupled components that may be difficult to maintain.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            A list of coupling data for classes in the file, including
            CBO scores and dependency information.

        Example:
            >>> coupling = analyzer.analyze_coupling("service.py")
            >>> for cls in coupling:
            ...     if cls.get("cbo", 0) > 10:
            ...         print(f"High coupling: {cls.get('name')}")
        """
        try:
            cmd = ["pyscn", "analyze", "--select", "cbo", "--json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.stdout:
                data = json.loads(result.stdout)
                # Pyscn returns CBO data under "cbo" key
                cbo_data = data.get("cbo", {})
                if "files" in cbo_data:
                    # Extract coupling data from all files
                    coupling_data = []
                    for file_data in cbo_data["files"]:
                        coupling_data.extend(file_data.get("classes", []))
                    return coupling_data
                return []
            return []

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running pyscn coupling analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_generate_report")
    def generate_report(self, output_dir: str = "reports") -> str:
        """Generate a comprehensive pyscn HTML report.

        Creates a detailed HTML report containing all analysis results
        including complexity, dead code, clones, and coupling metrics.

        Args:
            output_dir: Directory to write the report to.
                Defaults to "reports".

        Returns:
            Absolute path to the generated HTML report file,
            or empty string if generation failed.

        Example:
            >>> report_path = analyzer.generate_report("./analysis_reports")
            >>> print(f"Report available at: {report_path}")
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Change to the directory we want to analyze
            old_cwd = os.getcwd()
            os.chdir(output_dir)

            try:
                # Generate comprehensive report
                cmd = ["pyscn", "analyze", "--format", "html", ".."]
                subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                report_path = "index.html"
                if os.path.exists(report_path):
                    return os.path.abspath(report_path)
                else:
                    logger.warning("Pyscn report generation completed but no HTML file found")
                    return ""
            finally:
                os.chdir(old_cwd)

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error generating pyscn report: {e}")
            return ""

