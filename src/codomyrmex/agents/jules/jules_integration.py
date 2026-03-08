"""Jules integration adapters for Codomyrmex modules.

Provides :class:`JulesIntegrationAdapter` which bridges the Jules CLI agent
to codomyrmex module interfaces (``ai_code_editing``, ``llm``, ``coding``).
"""

from __future__ import annotations

from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter, AgentRequest


class JulesIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Jules with Codomyrmex modules."""

    def _validate_response(self, response: Any, context: str) -> None:
        """Log and raise if the response indicates failure.

        Args:
            response: Agent response object.
            context: Human-readable label for log messages.
        """
        if not response.is_success():
            self.logger.error(
                "Jules %s failed", context,
                extra={
                    "agent": "jules",
                    "context": context,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Jules {context} failed: {response.error}")

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs: Any
    ) -> str:
        """Adapt Jules for the AI code editing module.

        Args:
            prompt: Code generation prompt.
            language: Programming language (default ``"python"``).
            **kwargs: Additional context parameters forwarded to Jules.

        Returns:
            Generated code as a string.

        Raises:
            RuntimeError: If Jules code generation fails.
        """
        full_prompt = f"Generate {language} code: {prompt}"

        request = AgentRequest(
            prompt=full_prompt,
            context={"language": language, **kwargs},
        )

        response = self.agent.execute(request)
        self._validate_response(response, "code generation")

        self.logger.debug(
            "Jules code generation succeeded",
            extra={
                "agent": "jules",
                "language": language,
                "content_length": len(response.content),
                "execution_time": response.execution_time,
            },
        )

        return response.content

    def adapt_for_llm(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Adapt Jules for the LLM module.

        Converts a ``messages`` list (OpenAI-style) into a single Jules prompt
        and returns a completion dict mirroring the LLM module response schema.

        Args:
            messages: Conversation messages with ``role`` and ``content`` keys.
            model: Unused — Jules does not accept an external model override.
            **kwargs: Additional context parameters.

        Returns:
            dict with keys: ``content``, ``model``, ``usage``, ``metadata``.
        """
        prompt = "\n".join(
            f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages
        )

        request = AgentRequest(prompt=prompt, context=kwargs)
        response = self.agent.execute(request)

        return {
            "content": response.content,
            "model": "jules",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.content.split()),
            },
            "metadata": response.metadata,
        }

    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs: Any
    ) -> dict[str, Any]:
        """Adapt Jules for the code execution sandbox.

        Uses Jules to analyse/validate code rather than execute it directly.

        Args:
            code: Source code to analyse.
            language: Programming language (default ``"python"``).
            **kwargs: Additional context parameters.

        Returns:
            dict with keys: ``success``, ``output``, ``error``, ``metadata``.
        """
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
