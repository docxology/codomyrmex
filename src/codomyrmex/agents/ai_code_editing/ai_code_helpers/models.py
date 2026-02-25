"""AI Code Editing Models."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


# Enums for better type safety
class CodeLanguage(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    R = "r"
    MATLAB = "matlab"
    SHELL = "shell"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    XML = "xml"
    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"

class CodeComplexity(Enum):
    """Code complexity levels."""

    SIMPLE = "simple"
    INTERMEDIATE = "intermediate"
    COMPLEX = "complex"
    EXPERT = "expert"

class CodeStyle(Enum):
    """Code style preferences."""

    CLEAN = "clean"
    VERBOSE = "verbose"
    CONCISE = "concise"
    FUNCTIONAL = "functional"
    OBJECT_ORIENTED = "object_oriented"
    PROCEDURAL = "procedural"

@dataclass
class CodeGenerationRequest:
    """Request structure for code generation."""

    prompt: str
    language: CodeLanguage
    complexity: CodeComplexity = CodeComplexity.INTERMEDIATE
    style: CodeStyle = CodeStyle.CLEAN
    context: str | None = None
    requirements: list[str] | None = None
    examples: list[str] | None = None
    max_length: int | None = None
    temperature: float = 0.7

@dataclass
class CodeRefactoringRequest:
    """Request structure for code refactoring."""

    code: str
    language: CodeLanguage
    refactoring_type: str  # e.g., "optimize", "simplify", "add_error_handling"
    context: str | None = None
    preserve_functionality: bool = True
    add_tests: bool = False
    add_documentation: bool = False

@dataclass
class CodeAnalysisRequest:
    """Request structure for code analysis."""

    code: str
    language: CodeLanguage
    analysis_type: str  # e.g., "quality", "security", "performance", "maintainability"
    context: str | None = None
    include_suggestions: bool = True

@dataclass
class CodeGenerationResult:
    """Result structure for code generation."""

    generated_code: str
    language: CodeLanguage
    metadata: dict[str, Any]
    execution_time: float
    tokens_used: int | None = None
    confidence_score: float | None = None

