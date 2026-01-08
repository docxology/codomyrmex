from typing import Any


from codomyrmex.agents.core import AgentIntegrationAdapter
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.logging_monitoring import get_logger






























"""Codex integration adapters for Codomyrmex modules."""




"""Core functionality module

This module provides codex_integration functionality including:
- 3 functions: adapt_for_ai_code_editing, adapt_for_llm, adapt_for_code_execution
- 1 classes: CodexIntegrationAdapter

Usage:
    # Example usage here
"""
class CodexIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Codex with Codomyrmex modules."""

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """
        Adapt Codex for AI code editing module.

        Args:
            prompt: Code generation prompt
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Generated code
        """

        # Build prompt with language context
        full_prompt = f"Generate {language} code: {prompt}"

        request = AgentRequest(
            prompt=full_prompt,
            context={"language": language, **kwargs},
        )

        response = self.agent.execute(request)

        if not response.is_success():
            self.logger.error(
                "Codex code generation failed",
                extra={
                    "agent": "codex",
                    "language": language,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Code generation failed: {response.error}")

        self.logger.debug(
            "Codex code generation succeeded",
            extra={
                "agent": "codex",
                "language": language,
                "content_length": len(response.content),
                "execution_time": response.execution_time,
                "tokens_used": response.tokens_used,
            },
        )

        return response.content

    def adapt_for_llm(
        self, messages: list[dict], model: str = None, **kwargs
    ) -> dict:
        """
        Adapt Codex for LLM module.

        Args:
            messages: Conversation messages
            model: Model name (optional, uses Codex default)
            **kwargs: Additional parameters

        Returns:
            Completion result dictionary
        """

        # Convert messages to prompt
        prompt = "\n".join(
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages
        )

        request = AgentRequest(prompt=prompt, context=kwargs)

        response = self.agent.execute(request)

        return {
            "content": response.content,
            "model": model or "codex",
            "usage": {
                "prompt_tokens": response.metadata.get("usage", {}).get(
                    "prompt_tokens", 0
                ),
                "completion_tokens": response.metadata.get("usage", {}).get(
                    "completion_tokens", 0
                ),
            },
            "metadata": response.metadata,
        }

    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs
    ) -> dict[str, Any]:
        """
        Adapt Codex for code execution sandbox.

        Args:
            code: Code to execute
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Execution result dictionary
        """

        # Use Codex to analyze or validate code
        prompt = f"Analyze this {language} code:\n\n{code}"

        request = AgentRequest(
            prompt=prompt,
            context={"language": language, "code": code, **kwargs},
        )

        response = self.agent.execute(request)

        return {
            "success": response.is_success(),
            "output": response.content,
            "error": response.error,
            "metadata": response.metadata,
        }

