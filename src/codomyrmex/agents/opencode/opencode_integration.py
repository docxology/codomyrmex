from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.logging_monitoring import get_logger
























"""OpenCode integration adapters for Codomyrmex modules."""

"""Core functionality module

This module provides opencode_integration functionality including:
- 3 functions: adapt_for_ai_code_editing, adapt_for_llm, adapt_for_code_execution
- 1 classes: OpenCodeIntegrationAdapter

Usage:
    from opencode_integration import FunctionName, ClassName
    # Example usage here
"""
class OpenCodeIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for OpenCode with Codomyrmex modules."""

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """
        Adapt OpenCode for AI code editing module.

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
                "OpenCode code generation failed",
                extra={
                    "agent": "opencode",
                    "language": language,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Code generation failed: {response.error}")

        self.logger.debug(
            "OpenCode code generation succeeded",
            extra={
                "agent": "opencode",
                "language": language,
                "content_length": len(response.content),
                "execution_time": response.execution_time,
            },
        )

        return response.content

    def adapt_for_llm(
        self, messages: list[dict], model: str = None, **kwargs
    ) -> dict:
        """
        Adapt OpenCode for LLM module.

        Args:
            messages: Conversation messages
            model: Model name (not used for OpenCode)
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
            "model": "opencode",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.content.split()),
            },
            "metadata": response.metadata,
        }

    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs
    ) -> dict[str, Any]:
        """
        Adapt OpenCode for code execution sandbox.

        Args:
            code: Code to execute
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Execution result dictionary
        """

        # Use OpenCode to analyze or validate code
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

