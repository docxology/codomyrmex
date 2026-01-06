"""OpenAI Codex Integration Module.

This module provides integration with OpenAI's API for advanced code
generation, completion, and editing capabilities using GPT-4 and other
code-capable models.

Reference: https://platform.openai.com/docs/guides/code-generation
"""

import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

# Default configuration
DEFAULT_MODEL = "gpt-4-turbo"
DEFAULT_TEMPERATURE = 0.2  # Lower temperature for more deterministic code
MAX_TOKENS = 4096


@dataclass
class CodexRequest:
    """Request structure for Codex code generation."""
    prompt: str
    language: str
    max_tokens: int = MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    stop_sequences: list[str] = field(default_factory=list)
    context: Optional[str] = None


@dataclass
class CodexResponse:
    """Response structure from Codex."""
    generated_code: str
    model: str
    tokens_used: int
    execution_time: float
    finish_reason: str


class OpenAICodex:
    """OpenAI Codex integration for code generation and completion."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenAI Codex integration.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model to use (defaults to gpt-4-turbo)

        Raises:
            ValueError: If no API key is available
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or DEFAULT_MODEL
        self._client = None

        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set - Codex operations will fail")

    def _get_client(self):
        """Lazily initialize OpenAI client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
        return self._client

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Generate code using OpenAI models.

        Args:
            prompt: Code generation prompt describing what to create
            language: Target programming language
            context: Additional context for code generation
            max_tokens: Maximum tokens for generated code
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional arguments for the API

        Returns:
            Dictionary containing generated code and metadata

        Raises:
            RuntimeError: If code generation fails
        """
        start_time = time.time()

        try:
            client = self._get_client()

            # Build the system prompt for code generation
            system_prompt = self._build_system_prompt(language)

            # Build the user prompt
            user_prompt = self._build_user_prompt(prompt, context)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            execution_time = time.time() - start_time
            generated_code = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            finish_reason = response.choices[0].finish_reason or "unknown"

            # Extract just the code block if wrapped
            generated_code = self._extract_code_block(generated_code, language)

            logger.info(
                f"Generated {language} code using {self.model} "
                f"in {execution_time:.2f}s ({tokens_used} tokens)"
            )

            return {
                "generated_code": generated_code,
                "language": language,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "finish_reason": finish_reason,
                "prompt": prompt,
                "status": "success"
            }

        except ImportError as e:
            logger.error(f"OpenAI import error: {e}")
            raise
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise RuntimeError(f"Code generation failed: {e}")
        except Exception as e:
            logger.error(f"Error generating code: {e}", exc_info=True)
            raise RuntimeError(f"Code generation failed: {e}")

    def complete_code(
        self,
        code_prefix: str,
        language: str = "python",
        max_tokens: int = 1024,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Complete partial code.

        Args:
            code_prefix: The code to complete
            language: Programming language
            max_tokens: Maximum tokens for completion
            temperature: Sampling temperature
            **kwargs: Additional arguments

        Returns:
            Dictionary containing completed code and metadata
        """
        prompt = f"Complete the following {language} code:\n\n{code_prefix}"
        return self.generate_code(
            prompt=prompt,
            language=language,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

    def edit_code(
        self,
        code: str,
        instruction: str,
        language: str = "python",
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Edit existing code based on instructions.

        Args:
            code: The code to edit
            instruction: Edit instruction
            language: Programming language
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional arguments

        Returns:
            Dictionary containing edited code and metadata
        """
        start_time = time.time()

        try:
            client = self._get_client()

            system_prompt = (
                f"You are a code editor. Edit the provided {language} code "
                "according to the given instruction. Return only the edited code, "
                "with no explanations."
            )

            user_prompt = f"Instruction: {instruction}\n\nCode to edit:\n```{language}\n{code}\n```"

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            execution_time = time.time() - start_time
            edited_code = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            # Extract code block
            edited_code = self._extract_code_block(edited_code, language)

            logger.info(
                f"Edited {language} code using {self.model} "
                f"in {execution_time:.2f}s ({tokens_used} tokens)"
            )

            return {
                "original_code": code,
                "edited_code": edited_code,
                "instruction": instruction,
                "language": language,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error editing code: {e}", exc_info=True)
            raise RuntimeError(f"Code editing failed: {e}")

    def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
        **kwargs: Any
    ) -> dict[str, Any]:
        """Generate explanation for code.

        Args:
            code: Code to explain
            language: Programming language
            detail_level: Level of detail ("brief", "medium", "detailed")
            **kwargs: Additional arguments

        Returns:
            Dictionary containing explanation and metadata
        """
        start_time = time.time()

        try:
            client = self._get_client()

            detail_instructions = {
                "brief": "Provide a brief one-paragraph summary.",
                "medium": "Provide a clear explanation with key points.",
                "detailed": "Provide a detailed explanation covering all aspects."
            }

            system_prompt = (
                f"You are a code documentation expert. Explain the following "
                f"{language} code. {detail_instructions.get(detail_level, detail_instructions['medium'])}"
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"```{language}\n{code}\n```"}
                ],
                max_tokens=2048,
                temperature=0.3,
                **kwargs
            )

            execution_time = time.time() - start_time
            explanation = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            logger.info(
                f"Generated code explanation using {self.model} "
                f"in {execution_time:.2f}s ({tokens_used} tokens)"
            )

            return {
                "code": code,
                "explanation": explanation,
                "language": language,
                "detail_level": detail_level,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error explaining code: {e}", exc_info=True)
            raise RuntimeError(f"Code explanation failed: {e}")

    def _build_system_prompt(self, language: str) -> str:
        """Build system prompt for code generation."""
        language_guidelines = {
            "python": "Follow PEP 8, use type hints, include docstrings.",
            "javascript": "Use modern ES6+ syntax, include JSDoc comments.",
            "typescript": "Use proper TypeScript types, include TSDoc comments.",
            "java": "Follow Java conventions, include Javadoc comments.",
            "go": "Follow Go conventions, include godoc comments.",
            "rust": "Follow Rust idioms, include rustdoc comments.",
            "cpp": "Use modern C++ features, include Doxygen comments.",
        }

        guidelines = language_guidelines.get(
            language.lower(),
            "Follow language best practices and include documentation."
        )

        return (
            f"You are an expert {language} programmer. Generate clean, "
            f"production-ready code. {guidelines} Return only the code, "
            "no explanations unless specifically requested."
        )

    def _build_user_prompt(self, prompt: str, context: Optional[str]) -> str:
        """Build user prompt with optional context."""
        if context:
            return f"Context: {context}\n\nTask: {prompt}"
        return prompt

    def _extract_code_block(self, text: str, language: str) -> str:
        """Extract code from markdown code blocks if present."""
        import re

        # Try to match code block with language
        pattern = rf"```(?:{language}|{language.lower()})?\s*\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1).strip()

        # If no code block found, return trimmed text
        return text.strip()

    def is_available(self) -> bool:
        """Check if OpenAI Codex is available and configured."""
        if not self.api_key:
            return False

        try:
            self._get_client()
            return True
        except (ImportError, ValueError):
            return False


# Module-level convenience functions
def generate_code(
    prompt: str,
    language: str = "python",
    **kwargs: Any
) -> dict[str, Any]:
    """Generate code using OpenAI (module-level convenience function).

    Args:
        prompt: Code generation prompt
        language: Target programming language
        **kwargs: Additional arguments

    Returns:
        Generated code and metadata
    """
    codex = OpenAICodex()
    return codex.generate_code(prompt, language, **kwargs)


def complete_code(code_prefix: str, language: str = "python", **kwargs: Any) -> dict[str, Any]:
    """Complete code (module-level convenience function)."""
    codex = OpenAICodex()
    return codex.complete_code(code_prefix, language, **kwargs)


def edit_code(code: str, instruction: str, language: str = "python", **kwargs: Any) -> dict[str, Any]:
    """Edit code (module-level convenience function)."""
    codex = OpenAICodex()
    return codex.edit_code(code, instruction, language, **kwargs)


def explain_code(code: str, language: str = "python", **kwargs: Any) -> dict[str, Any]:
    """Explain code (module-level convenience function)."""
    codex = OpenAICodex()
    return codex.explain_code(code, language, **kwargs)
