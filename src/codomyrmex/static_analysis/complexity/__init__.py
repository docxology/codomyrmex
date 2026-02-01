"""
Static Analysis Complexity Module

Code complexity analysis and metrics.
"""

__version__ = "0.1.0"

import re
import ast
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path


class ComplexityLevel(Enum):
    """Complexity severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ComplexityMetric:
    """A complexity metric result."""
    name: str
    value: float
    level: ComplexityLevel
    threshold_low: float = 5.0
    threshold_medium: float = 10.0
    threshold_high: float = 20.0
    
    @classmethod
    def from_value(
        cls,
        name: str,
        value: float,
        thresholds: Optional[Dict[str, float]] = None,
    ) -> "ComplexityMetric":
        """Create from value with auto-level."""
        t = thresholds or {"low": 5, "medium": 10, "high": 20}
        
        if value <= t["low"]:
            level = ComplexityLevel.LOW
        elif value <= t["medium"]:
            level = ComplexityLevel.MEDIUM
        elif value <= t["high"]:
            level = ComplexityLevel.HIGH
        else:
            level = ComplexityLevel.VERY_HIGH
        
        return cls(name=name, value=value, level=level)


@dataclass
class FunctionMetrics:
    """Metrics for a single function."""
    name: str
    file_path: str
    line_number: int
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    parameter_count: int = 0
    nesting_depth: int = 0
    
    @property
    def overall_complexity(self) -> ComplexityLevel:
        """Get overall complexity level."""
        if self.cyclomatic_complexity > 15 or self.cognitive_complexity > 15:
            return ComplexityLevel.VERY_HIGH
        elif self.cyclomatic_complexity > 10 or self.cognitive_complexity > 10:
            return ComplexityLevel.HIGH
        elif self.cyclomatic_complexity > 5 or self.cognitive_complexity > 5:
            return ComplexityLevel.MEDIUM
        return ComplexityLevel.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "file": self.file_path,
            "line": self.line_number,
            "cyclomatic": self.cyclomatic_complexity,
            "cognitive": self.cognitive_complexity,
            "loc": self.lines_of_code,
            "level": self.overall_complexity.value,
        }


@dataclass
class FileMetrics:
    """Metrics for a file."""
    file_path: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    function_count: int = 0
    class_count: int = 0
    functions: List[FunctionMetrics] = field(default_factory=list)
    
    @property
    def average_complexity(self) -> float:
        """Get average cyclomatic complexity."""
        if not self.functions:
            return 0.0
        return sum(f.cyclomatic_complexity for f in self.functions) / len(self.functions)
    
    @property
    def max_complexity(self) -> int:
        """Get maximum cyclomatic complexity."""
        if not self.functions:
            return 0
        return max(f.cyclomatic_complexity for f in self.functions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": self.file_path,
            "lines": self.total_lines,
            "code_lines": self.code_lines,
            "functions": self.function_count,
            "avg_complexity": self.average_complexity,
            "max_complexity": self.max_complexity,
        }


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """AST visitor for calculating cyclomatic complexity."""
    
    def __init__(self):
        self.complexity = 1  # Base complexity
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Assert(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_comprehension(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        # Add for each 'and' or 'or'
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


def calculate_cyclomatic_complexity(code: str) -> int:
    """Calculate cyclomatic complexity of code."""
    try:
        tree = ast.parse(code)
        visitor = CyclomaticComplexityVisitor()
        visitor.visit(tree)
        return visitor.complexity
    except SyntaxError:
        return 0


def calculate_cognitive_complexity(code: str) -> int:
    """Calculate cognitive complexity of code."""
    complexity = 0
    nesting = 0
    
    # Simple heuristic based on nesting and control structures
    lines = code.split('\n')
    for line in lines:
        stripped = line.strip()
        
        # Count nesting by indentation
        if line and not line.isspace():
            indent = len(line) - len(line.lstrip())
            current_nesting = indent // 4
            
            # Add for control structures with nesting bonus
            if any(stripped.startswith(kw) for kw in ['if ', 'elif ', 'for ', 'while ', 'except', 'with ']):
                complexity += 1 + current_nesting
    
    return complexity


def count_lines(code: str) -> Dict[str, int]:
    """Count different types of lines."""
    total = 0
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    
    in_docstring = False
    
    for line in code.split('\n'):
        total += 1
        stripped = line.strip()
        
        if not stripped:
            blank_lines += 1
        elif stripped.startswith('#'):
            comment_lines += 1
        elif '"""' in stripped or "'''" in stripped:
            comment_lines += 1
            in_docstring = not in_docstring
        elif in_docstring:
            comment_lines += 1
        else:
            code_lines += 1
    
    return {
        "total": total,
        "code": code_lines,
        "comments": comment_lines,
        "blank": blank_lines,
    }


class ComplexityAnalyzer:
    """
    Analyzes code complexity.
    
    Usage:
        analyzer = ComplexityAnalyzer()
        
        # Analyze a file
        metrics = analyzer.analyze_file("module.py")
        print(f"Average complexity: {metrics.average_complexity:.1f}")
        
        # Analyze code string
        func_metrics = analyzer.analyze_function(code, "my_function")
    """
    
    def __init__(
        self,
        complexity_threshold: int = 10,
        loc_threshold: int = 50,
    ):
        self.complexity_threshold = complexity_threshold
        self.loc_threshold = loc_threshold
    
    def analyze_function(
        self,
        code: str,
        name: str = "function",
        file_path: str = "",
        line_number: int = 1,
    ) -> FunctionMetrics:
        """Analyze a function's complexity."""
        cyclomatic = calculate_cyclomatic_complexity(code)
        cognitive = calculate_cognitive_complexity(code)
        lines = count_lines(code)
        
        # Count parameters (simple heuristic)
        param_count = 0
        match = re.search(r'def\s+\w+\s*\((.*?)\)', code, re.DOTALL)
        if match:
            params = match.group(1)
            if params.strip():
                param_count = len([p for p in params.split(',') if p.strip()])
        
        # Calculate max nesting
        max_nesting = 0
        current_nesting = 0
        for line in code.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                current_nesting = indent // 4
                max_nesting = max(max_nesting, current_nesting)
        
        return FunctionMetrics(
            name=name,
            file_path=file_path,
            line_number=line_number,
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=lines["code"],
            parameter_count=param_count,
            nesting_depth=max_nesting,
        )
    
    def analyze_file(self, file_path: str) -> FileMetrics:
        """Analyze a file's complexity."""
        path = Path(file_path)
        if not path.exists():
            return FileMetrics(file_path=file_path)
        
        content = path.read_text(encoding='utf-8', errors='ignore')
        lines = count_lines(content)
        
        metrics = FileMetrics(
            file_path=file_path,
            total_lines=lines["total"],
            code_lines=lines["code"],
            comment_lines=lines["comments"],
            blank_lines=lines["blank"],
        )
        
        # Parse and analyze functions
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics.function_count += 1
                    
                    # Get function source
                    func_lines = content.split('\n')[node.lineno - 1:node.end_lineno]
                    func_code = '\n'.join(func_lines)
                    
                    func_metrics = self.analyze_function(
                        func_code,
                        name=node.name,
                        file_path=file_path,
                        line_number=node.lineno,
                    )
                    metrics.functions.append(func_metrics)
                
                elif isinstance(node, ast.ClassDef):
                    metrics.class_count += 1
        
        except SyntaxError:
            pass
        
        return metrics
    
    def get_high_complexity_functions(
        self,
        metrics: FileMetrics,
    ) -> List[FunctionMetrics]:
        """Get functions exceeding complexity threshold."""
        return [
            f for f in metrics.functions
            if f.cyclomatic_complexity > self.complexity_threshold
        ]


__all__ = [
    # Enums
    "ComplexityLevel",
    # Data classes
    "ComplexityMetric",
    "FunctionMetrics",
    "FileMetrics",
    # Functions
    "calculate_cyclomatic_complexity",
    "calculate_cognitive_complexity",
    "count_lines",
    # Core
    "ComplexityAnalyzer",
]
