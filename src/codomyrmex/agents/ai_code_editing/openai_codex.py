import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, NoReturn

from openai import OpenAI

from codomyrmex.logging_monitoring import get_logger

"""OpenAI Codex Integration Module.

This module provides integration with OpenAI's API for advanced code
generation, completion, and editing capabilities using GPT-4 and other
code-capable models.

Reference: https://platform.openai.com/docs/guides/code-generation
"""


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
    context: str | None = None


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

    def __init__(self, api_key: str | None = None, model: str | None = None):
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
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                ) from None
        return self._client

    def _call_api(
        self,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
        **kwargs: Any,
    ):
        """Send a chat completion request and return the raw response."""
        client = self._get_client()
        return client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

    def _parse_response(
        self, response, start_time: float
    ) -> tuple[str, int, float, str]:
        """Extract (content, tokens_used, execution_time, finish_reason) from a response."""
        execution_time = time.time() - start_time
        content = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else 0
        finish_reason = response.choices[0].finish_reason or "unknown"
        return content, tokens_used, execution_time, finish_reason

    @staticmethod
    def _reraise(label: str, e: Exception) -> NoReturn:
        """Log and re-raise a caught exception as RuntimeError."""
        logger.error("Error in %s: %s", label, e, exc_info=e)
        raise RuntimeError(f"{label} failed: {e}") from e

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: str | None = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate code using OpenAI models. Returns dict with generated_code and metadata."""
        start_time = time.time()
        try:
            messages = [
                {"role": "system", "content": self._build_system_prompt(language)},
                {"role": "user", "content": self._build_user_prompt(prompt, context)},
            ]
            response = self._call_api(messages, max_tokens, temperature, **kwargs)
            generated_code, tokens_used, execution_time, finish_reason = (
                self._parse_response(response, start_time)
            )
            generated_code = self._extract_code_block(generated_code, language)
            logger.info(
                "Generated %s code using %s in %.2fs (%s tokens)",
                language,
                self.model,
                execution_time,
                tokens_used,
            )
            return {
                "generated_code": generated_code,
                "language": language,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "finish_reason": finish_reason,
                "prompt": prompt,
                "status": "success",
            }
        except ImportError as e:
            logger.error("OpenAI import error: %s", e)
            raise
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self._reraise("code generation", e)

    def complete_code(
        self,
        code_prefix: str,
        language: str = "python",
        max_tokens: int = 1024,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any,
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
            **kwargs,
        )

    def _build_edit_messages(
        self, code: str, instruction: str, language: str
    ) -> list[dict[str, str]]:
        """Build chat messages for an edit_code request."""
        system_prompt = (
            f"You are a code editor. Edit the provided {language} code "
            "according to the given instruction. Return only the edited code, "
            "with no explanations."
        )
        user_prompt = (
            f"Instruction: {instruction}\n\nCode to edit:\n```{language}\n{code}\n```"
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _build_explain_messages(
        self, code: str, language: str, detail_level: str
    ) -> list[dict[str, str]]:
        """Build chat messages for an explain_code request."""
        detail_instructions = {
            "brief": "Provide a brief one-paragraph summary.",
            "medium": "Provide a clear explanation with key points.",
            "detailed": "Provide a detailed explanation covering all aspects.",
        }
        detail = detail_instructions.get(detail_level, detail_instructions["medium"])
        system_prompt = (
            f"You are a code documentation expert. Explain the following "
            f"{language} code. {detail}"
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"```{language}\n{code}\n```"},
        ]

    def edit_code(
        self,
        code: str,
        instruction: str,
        language: str = "python",
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Edit existing code based on instructions. Returns dict with edited_code and metadata."""
        start_time = time.time()
        try:
            messages = self._build_edit_messages(code, instruction, language)
            response = self._call_api(messages, max_tokens, temperature, **kwargs)
            edited_code, tokens_used, execution_time, _ = self._parse_response(
                response, start_time
            )
            edited_code = self._extract_code_block(edited_code, language)
            logger.info(
                "Edited %s code using %s in %.2fs (%s tokens)",
                language,
                self.model,
                execution_time,
                tokens_used,
            )
            return {
                "original_code": code,
                "edited_code": edited_code,
                "instruction": instruction,
                "language": language,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "status": "success",
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self._reraise("code editing", e)

    def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate explanation for code. Returns dict with explanation and metadata."""
        start_time = time.time()
        try:
            messages = self._build_explain_messages(code, language, detail_level)
            response = self._call_api(messages, 2048, 0.3, **kwargs)
            explanation, tokens_used, execution_time, _ = self._parse_response(
                response, start_time
            )
            logger.info(
                "Generated code explanation using %s in %.2fs (%s tokens)",
                self.model,
                execution_time,
                tokens_used,
            )
            return {
                "code": code,
                "explanation": explanation,
                "language": language,
                "detail_level": detail_level,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "status": "success",
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self._reraise("code explanation", e)

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
            "Follow language best practices and include documentation.",
        )

        return (
            f"You are an expert {language} programmer. Generate clean, "
            f"production-ready code. {guidelines} Return only the code, "
            "no explanations unless specifically requested."
        )

    def _build_user_prompt(self, prompt: str, context: str | None) -> str:
        """Build user prompt with optional context."""
        if context:
            return f"Context: {context}\n\nTask: {prompt}"
        return prompt

    def _extract_code_block(self, text: str, language: str) -> str:
        """Extract code from markdown code blocks if present."""

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
        except (ImportError, ValueError) as e:
            logger.warning("OpenAI Codex unavailable: %s", e)
            return False


# Module-level convenience functions
def generate_code(
    prompt: str, language: str = "python", **kwargs: Any
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


def complete_code(
    code_prefix: str, language: str = "python", **kwargs: Any
) -> dict[str, Any]:
    """Complete code (module-level convenience function)."""
    codex = OpenAICodex()
    return codex.complete_code(code_prefix, language, **kwargs)


def edit_code(
    code: str, instruction: str, language: str = "python", **kwargs: Any
) -> dict[str, Any]:
    """Edit code (module-level convenience function)."""
    codex = OpenAICodex()
    return codex.edit_code(code, instruction, language, **kwargs)


def explain_code(code: str, language: str = "python", **kwargs: Any) -> dict[str, Any]:
    """Explain code (module-level convenience function)."""
    codex = OpenAICodex()
    return codex.explain_code(code, language, **kwargs)
