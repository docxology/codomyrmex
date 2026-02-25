"""CodeIntelMixin functionality."""

from typing import Any

from codomyrmex.agents.core import (
    AgentRequest,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class CodeIntelMixin:
    """CodeIntelMixin class."""

    def review_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "general",
    ) -> dict[str, Any]:
        """Perform AI-powered code review.

        Uses Claude to analyze code for issues, bugs, security
        vulnerabilities, and improvement opportunities.

        Args:
            code: Code to review
            language: Programming language
            analysis_type: Type of analysis:
                - "general": Overall code review
                - "security": Security-focused analysis
                - "bugs": Bug and error detection
                - "performance": Performance analysis

        Returns:
            Dictionary containing:
                - success: Whether review succeeded
                - output: Full analysis text
                - issues: List of identified issues
                - recommendations: List of suggestions
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.review_code(
            ...     "def add(a, b): return a + b",
            ...     language="python",
            ...     analysis_type="general"
            ... )
        """
        analysis_prompts = {
            "general": "Analyze for correctness, style, and improvements.",
            "security": "Identify security vulnerabilities and risks.",
            "bugs": "Find bugs, edge cases, and potential runtime errors.",
            "performance": "Identify performance issues and optimizations.",
        }

        analysis_instruction = analysis_prompts.get(analysis_type, analysis_prompts["general"])

        system_prompt = f"""You are an expert {language} code analyst.
Provide thorough, actionable code review.
Structure your response with:
1. Summary
2. Issues (as bullet points)
3. Recommendations (as bullet points)"""

        prompt = f"""{analysis_instruction}

```{language}
{code}
```"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "output": "",
                "issues": [],
                "recommendations": [],
            }

        # Parse issues and recommendations
        issues, recommendations = self._parse_review_output(response.content)

        return {
            "success": True,
            "output": response.content,
            "issues": issues,
            "recommendations": recommendations,
            "language": language,
            "analysis_type": analysis_type,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def generate_diff(
        self,
        original: str,
        modified: str,
        filename: str = "file",
    ) -> dict[str, Any]:
        """Generate unified diff between code versions.

        Creates a unified diff format output showing the differences
        between original and modified code.

        Args:
            original: Original code content
            modified: Modified code content
            filename: Filename for diff header

        Returns:
            Dictionary containing:
                - diff: Unified diff string
                - additions: Number of lines added
                - deletions: Number of lines removed
                - has_changes: Whether there are any changes

        Example:
            >>> diff_result = client.generate_diff(
            ...     "def foo():\\n    pass",
            ...     "def foo():\\n    return 42"
            ... )
            >>> print(diff_result["diff"])
        """
        diff = self._generate_unified_diff(original, modified, filename)

        # Count additions and deletions
        additions = 0
        deletions = 0
        for line in diff.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        return {
            "diff": diff,
            "additions": additions,
            "deletions": deletions,
            "has_changes": additions > 0 or deletions > 0,
        }

    def _generate_unified_diff(
        self,
        original: str,
        modified: str,
        filename: str,
    ) -> str:
        """Generate unified diff between two strings."""
        import difflib

        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )

        return "".join(diff)

    def _parse_review_output(self, output: str) -> tuple[list[str], list[str]]:
        """Parse code review output for issues and recommendations."""
        issues: list[str] = []
        recommendations: list[str] = []

        lines = output.split("\n")
        current_section = None

        for line in lines:
            line_stripped = line.strip()
            lower_line = line_stripped.lower()

            if "issue" in lower_line or "problem" in lower_line or "bug" in lower_line:
                current_section = "issues"
            elif "recommend" in lower_line or "suggestion" in lower_line or "improvement" in lower_line:
                current_section = "recommendations"
            elif line_stripped.startswith(("-", "*", "•", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
                item = line_stripped.lstrip("-*•0123456789.) ").strip()
                if item and len(item) > 5:  # Filter out very short items
                    if current_section == "issues":
                        issues.append(item)
                    elif current_section == "recommendations":
                        recommendations.append(item)

        return issues, recommendations

    def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
    ) -> dict[str, Any]:
        """Generate a comprehensive explanation of code.

        Uses Claude to explain what the code does, how it works,
        and any notable patterns or algorithms used.

        Args:
            code: Code to explain
            language: Programming language
            detail_level: Level of detail ("brief", "medium", "detailed")

        Returns:
            Dictionary containing:
                - success: Whether explanation succeeded
                - explanation: Full explanation text
                - summary: One-line summary
                - concepts: Key concepts mentioned
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.explain_code("def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)")
            >>> print(result["summary"])
        """
        detail_prompts = {
            "brief": "Provide a 2-3 sentence explanation.",
            "medium": "Provide a clear explanation covering purpose, logic, and key patterns.",
            "detailed": "Provide an in-depth explanation including purpose, step-by-step logic, patterns, edge cases, and potential improvements.",
        }

        detail_instruction = detail_prompts.get(detail_level, detail_prompts["medium"])

        system_prompt = f"""You are an expert {language} developer and educator.
Explain code clearly for developers of varying skill levels.
Structure your response:
1. Summary (one line)
2. Explanation
3. Key Concepts (bullet points)"""

        prompt = f"""{detail_instruction}

```{language}
{code}
```"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "explanation": "",
                "summary": "",
                "concepts": [],
            }

        # Parse the response
        content = response.content
        summary = ""
        concepts = []

        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "summary" in line.lower() and i + 1 < len(lines):
                summary = lines[i + 1].strip().lstrip("-•* ")
                break
            elif line.strip() and not any(h in line.lower() for h in ["explanation", "concept", "##", "#"]):
                summary = line.strip()
                break

        # Extract concepts
        in_concepts = False
        for line in lines:
            if "concept" in line.lower():
                in_concepts = True
                continue
            if in_concepts and line.strip().startswith(("-", "*", "•")):
                concept = line.strip().lstrip("-*• ").strip()
                if concept:
                    concepts.append(concept)
            elif in_concepts and line.strip() and not line.strip().startswith(("-", "*", "•")):
                if line.startswith("#"):
                    in_concepts = False

        return {
            "success": True,
            "explanation": content,
            "summary": summary[:200] if summary else "See full explanation",
            "concepts": concepts[:10],
            "language": language,
            "detail_level": detail_level,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def suggest_tests(
        self,
        code: str,
        language: str = "python",
        framework: str | None = None,
    ) -> dict[str, Any]:
        """Generate test suggestions for code.

        Uses Claude to analyze code and suggest appropriate tests,
        including edge cases and common testing patterns.

        Args:
            code: Code to generate tests for
            language: Programming language
            framework: Testing framework (e.g., "pytest", "unittest", "jest")

        Returns:
            Dictionary containing:
                - success: Whether generation succeeded
                - tests: Generated test code
                - test_cases: List of test case descriptions
                - coverage_notes: Notes about test coverage
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.suggest_tests("def add(a, b): return a + b")
            >>> print(result["tests"])
        """
        if framework is None:
            framework = "pytest" if language == "python" else "jest" if language in ("javascript", "typescript") else "default"

        system_prompt = f"""You are an expert {language} testing specialist.
Generate comprehensive tests using {framework}.
Include:
1. Basic functionality tests
2. Edge cases
3. Error handling tests

Return:
1. Test code (ready to run)
2. List of test cases with descriptions"""

        prompt = f"""Generate tests for this {language} code using {framework}:

```{language}
{code}
```"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "tests": "",
                "test_cases": [],
                "coverage_notes": "",
            }

        content = response.content
        tests = self._extract_code_block(content, language)

        # Extract test case descriptions
        test_cases = []
        for line in content.split("\n"):
            line_stripped = line.strip()
            if line_stripped.startswith(("-", "*", "•", "1", "2", "3", "4", "5")):
                case = line_stripped.lstrip("-*•0123456789.) ").strip()
                if case and ("test" in case.lower() or "case" in case.lower() or "should" in case.lower()):
                    test_cases.append(case)

        return {
            "success": True,
            "tests": tests,
            "test_cases": test_cases[:15],
            "coverage_notes": f"Generated {len(test_cases)} test cases for {framework}",
            "language": language,
            "framework": framework,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

