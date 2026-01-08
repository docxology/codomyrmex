from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter, AgentInterface
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.logging_monitoring import get_logger
























"""Every Code integration adapters for Codomyrmex modules."""

"""Core functionality module

This module provides every_code_integration functionality including:
- 3 functions: adapt_for_ai_code_editing, adapt_for_llm, adapt_for_code_execution
- 1 classes: EveryCodeIntegrationAdapter

Usage:
    from every_code_integration import FunctionName, ClassName
    # Example usage here
"""
class EveryCodeIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Every Code with Codomyrmex modules."""

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """
        Adapt Every Code for AI code editing module.

        Args:
            prompt: Code generation prompt
            language: Programming language
            **kwargs: Additional parameters (files, directories, etc.)

        Returns:
            Generated code
        """

        # Use /code command for code generation
        full_prompt = f"/code Generate {language} code: {prompt}"

        # Include files/directories from kwargs if provided
        context = {"language": language}
        if "files" in kwargs:
            context["files"] = kwargs["files"]
        if "directories" in kwargs:
            context["directories"] = kwargs["directories"]

        request = AgentRequest(
            prompt=full_prompt,
            context=context,
        )

        response = self.agent.execute(request)

        if not response.is_success():
            self.logger.error(
                "Every Code code generation failed",
                extra={
                    "agent": "every_code",
                    "language": language,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Code generation failed: {response.error}")

        self.logger.debug(
            "Every Code code generation succeeded",
            extra={
                "agent": "every_code",
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
        Adapt Every Code for LLM module.

        Args:
            messages: Conversation messages
            model: Model name (optional)
            **kwargs: Additional parameters

        Returns:
            Completion result dictionary
        """

        # Convert messages to prompt
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                prompt_parts.append(content)
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            elif role == "system":
                prompt_parts.append(f"System: {content}")

        prompt = "\n".join(prompt_parts)

        # If model is specified, include in context or use --model flag
        context = kwargs.copy()
        if model:
            context["model"] = model
            # Prepend model override to prompt
            prompt = f"--model {model} {prompt}"

        request = AgentRequest(prompt=prompt, context=context)

        response = self.agent.execute(request)

        # Estimate token usage (rough approximation)
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response.content.split()) if response.content else 0

        return {
            "content": response.content,
            "model": model or "gpt-5.1",
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "metadata": response.metadata,
        }

    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs
    ) -> dict[str, Any]:
        """
        Adapt Every Code for code execution sandbox.

        Args:
            code: Code to analyze
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Analysis result dictionary
        """

        # Use Every Code to analyze or validate code
        prompt = f"Analyze this {language} code:\n\n```{language}\n{code}\n```"

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

