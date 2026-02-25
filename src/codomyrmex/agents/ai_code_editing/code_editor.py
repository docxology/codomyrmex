"""Code Editor Agent Implementation."""
from collections.abc import Iterator
from typing import Any

from codomyrmex.agents.ai_code_editing import ai_code_helpers
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.exceptions import AgentError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class CodeEditor(BaseAgent):
    """
    Agent specialized in code editing, generation, and analysis.
    Wraps functionality from ai_code_helpers.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Code Editor.
        """
        super().__init__(
            name="code_editor",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
            ],
            config=config,
        )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute code editing request.
        For now, this is a simplified wrapper that assumes the prompt is a generation request.
        """
        try:
            # Extract language from context, metadata or default to python
            language = request.context.get("language") or request.metadata.get("language", "python")

            # Simple dispatch based on prompt content keywords (naive routing)
            if "refactor" in request.prompt.lower():
                # Naively assume the context has 'code'
                code = request.context.get("code", "") if request.context else ""
                result_dict = ai_code_helpers.refactor_code_snippet(code, request.prompt, language=language)
                result = result_dict.get("refactored_code", str(result_dict))
            else:
                context_str = str(request.context) if request.context else None
                result_dict = ai_code_helpers.generate_code_snippet(request.prompt, language=language, context=context_str)
                result = result_dict.get("generated_code", str(result_dict))

            return AgentResponse(content=result, request_id=request.id)
        except Exception as e:
            raise AgentError(f"CodeEditor failed: {str(e)}") from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream not supported for this wrapper yet."""
        yield "Streaming not supported by CodeEditor wrapper yet."

    def setup(self) -> None:
        """Setup Code Editor."""
        # Could check if optional deps (anthropic, openai) are installed
        pass

    def test_connection(self) -> bool:
        """Test if underlying helpers working."""
        # Simple check if modules imported
        return True

    # First-class methods
    def generate_code(self, prompt: str, context: str | None = None) -> str:
        """Directly generate code."""
        return ai_code_helpers.generate_code_snippet(prompt, context)

    def refactor(self, code: str, instruction: str) -> str:
        """Directly refactor code."""
        return ai_code_helpers.refactor_code_snippet(code, instruction)

    def analyze_code(self, code: str) -> dict[str, Any]:
        """
        Analyze code for quality metrics and potential issues.

        Args:
            code: Code to analyze

        Returns:
            Analysis results including lines, complexity hints, and suggestions
        """
        lines = code.strip().split('\n')

        # Basic static analysis
        analysis = {
            "total_lines": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": sum(1 for line in lines if line.strip().startswith('#')),
            "has_docstring": '"""' in code or "'''" in code,
            "imports": [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))],
            "functions": [],
            "classes": [],
        }

        # Find function and class definitions
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('def '):
                name = stripped.split('(')[0].replace('def ', '')
                analysis["functions"].append({"name": name, "line": i + 1})
            elif stripped.startswith('class '):
                name = stripped.split('(')[0].split(':')[0].replace('class ', '')
                analysis["classes"].append({"name": name, "line": i + 1})

        logger.debug(f"Analyzed code: {analysis['total_lines']} lines, {len(analysis['functions'])} functions")
        return analysis

    def explain_code(self, code: str, detail_level: str = "summary") -> str:
        """
        Generate explanation for code.

        Args:
            code: Code to explain
            detail_level: Level of detail ("summary", "detailed")

        Returns:
            Human-readable explanation
        """
        analysis = self.analyze_code(code)

        explanation = []
        explanation.append(f"This code has {analysis['total_lines']} lines.")

        if analysis['classes']:
            class_names = [c['name'] for c in analysis['classes']]
            explanation.append(f"It defines {len(class_names)} class(es): {', '.join(class_names)}.")

        if analysis['functions']:
            func_names = [f['name'] for f in analysis['functions']]
            explanation.append(f"It defines {len(func_names)} function(s): {', '.join(func_names)}.")

        if analysis['imports']:
            explanation.append(f"It imports from {len(analysis['imports'])} module(s).")

        if detail_level == "detailed":
            if analysis['has_docstring']:
                explanation.append("The code includes documentation strings.")
            if analysis['comment_lines'] > 0:
                explanation.append(f"There are {analysis['comment_lines']} comment lines.")

        return " ".join(explanation)
