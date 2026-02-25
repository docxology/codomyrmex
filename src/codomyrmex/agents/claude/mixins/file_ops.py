"""FileOpsMixin functionality."""

import os
from typing import Any

from codomyrmex.agents.core import (
    AgentRequest,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class FileOpsMixin:
    """FileOpsMixin class."""

    def edit_file(
        self,
        file_path: str,
        instructions: str,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Apply AI-guided edits to a file.

        Uses Claude to understand the file content and apply edits
        based on natural language instructions.

        Args:
            file_path: Absolute path to the file to edit
            instructions: Natural language description of edits to make
            language: Programming language (auto-detected if None)

        Returns:
            Dictionary containing:
                - success: Whether editing succeeded
                - original_content: Original file content
                - modified_content: Modified file content
                - diff: Unified diff of changes
                - explanation: Description of changes made
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.edit_file(
            ...     "/path/to/file.py",
            ...     "Add type hints to all function parameters"
            ... )
            >>> print(result["diff"])
        """

        # Read the file
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "original_content": "",
                "modified_content": "",
            }

        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "original_content": "",
                "modified_content": "",
            }

        # Auto-detect language from extension
        if language is None:
            ext = os.path.splitext(file_path)[1].lower()
            lang_map = {
                ".py": "python", ".js": "javascript", ".ts": "typescript",
                ".java": "java", ".cpp": "cpp", ".c": "c", ".go": "go",
                ".rs": "rust", ".rb": "ruby", ".php": "php", ".swift": "swift",
                ".kt": "kotlin", ".scala": "scala", ".cs": "csharp",
            }
            language = lang_map.get(ext, "text")

        # Build the prompt
        system_prompt = f"""You are an expert {language} developer performing code edits.
Apply the requested changes to the provided code.
Return ONLY the complete modified code, no explanations.
Preserve all existing functionality unless explicitly asked to change it."""

        prompt = f"""Edit this {language} file according to the instructions.

Instructions: {instructions}

Current file content:
```{language}
{original_content}
```

Return the complete modified file content:"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "original_content": original_content,
                "modified_content": "",
            }

        # Extract code from response
        modified_content = self._extract_code_block(response.content, language)

        # Generate diff
        diff = self._generate_unified_diff(original_content, modified_content, file_path)

        return {
            "success": True,
            "original_content": original_content,
            "modified_content": modified_content,
            "diff": diff,
            "explanation": f"Applied edits: {instructions}",
            "language": language,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def create_file(
        self,
        file_path: str,
        description: str,
        language: str = "python",
    ) -> dict[str, Any]:
        """Generate a new file from a description.

        Uses Claude to create file content based on a natural language
        description of what the file should contain.

        Args:
            file_path: Path where file should be created
            description: Description of what the file should contain
            language: Programming language

        Returns:
            Dictionary containing:
                - success: Whether creation succeeded
                - content: Generated file content
                - file_path: Path to created file
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.create_file(
            ...     "/path/to/utils.py",
            ...     "Utility functions for string manipulation"
            ... )
        """

        system_prompt = f"""You are an expert {language} developer.
Generate clean, well-documented, production-ready code.
Follow {language} best practices and include appropriate error handling.
Return ONLY the code, no explanations or markdown wrappers."""

        prompt = f"""Create a {language} file with the following content:

Description: {description}
Filename: {os.path.basename(file_path)}

Generate the complete file content:"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "content": "",
                "file_path": file_path,
            }

        content = self._extract_code_block(response.content, language)

        return {
            "success": True,
            "content": content,
            "file_path": file_path,
            "language": language,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def _extract_code_block(self, response: str, language: str) -> str:
        """Extract code from markdown-formatted response."""
        import re

        # Try language-specific block
        pattern = rf"```{language}\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try generic code block
        pattern = r"```\n?(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return response.strip()

