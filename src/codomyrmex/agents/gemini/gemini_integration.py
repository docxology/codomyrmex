from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.logging_monitoring import get_logger
























"""Gemini integration adapters for Codomyrmex modules."""

"""Core functionality module

This module provides gemini_integration functionality including:
- 3 functions: adapt_for_ai_code_editing, adapt_for_llm, adapt_for_code_execution
- 1 classes: GeminiIntegrationAdapter

Usage:
    from gemini_integration import FunctionName, ClassName
    # Example usage here
"""
class GeminiIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Gemini with Codomyrmex modules."""

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """
        Adapt Gemini for AI code editing module.

        Args:
            prompt: Code generation prompt
            language: Programming language
            **kwargs: Additional parameters (files, directories, etc.)

        Returns:
            Generated code
        """

        # Build prompt with language context
        full_prompt = f"Generate {language} code: {prompt}"

        # Include files/directories from kwargs if provided
        context = {"language": language}
        if "files" in kwargs:
            context["files"] = kwargs["files"]
        if "directories" in kwargs:
            context["directories"] = kwargs["directories"]
        
        # Forward multimodal data if present
        if "images" in kwargs:
            context["images"] = kwargs["images"]

        request = AgentRequest(
            prompt=full_prompt,
            context=context,
        )

        response = self.agent.execute(request)

        if not response.is_success():
            self.logger.error(
                "Gemini code generation failed",
                extra={
                    "agent": "gemini",
                    "language": language,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Code generation failed: {response.error}")

        self.logger.debug(
            "Gemini code generation succeeded",
            extra={
                "agent": "gemini",
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
        Adapt Gemini for LLM module.

        Args:
            messages: Conversation messages
            model: Model name (optional, can use /model command)
            **kwargs: Additional parameters

        Returns:
            Completion result dictionary
        """

        # Convert messages to prompt (naive implementation for now, 
        # ideally we should map to history or structured content if supported)
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Model: {content}")
            elif role == "system":
                prompt_parts.append(f"System: {content}")

        prompt = "\n".join(prompt_parts)

        # Context setup
        context = kwargs.copy()
        if model:
            context["model"] = model

        request = AgentRequest(prompt=prompt, context=context)

        response = self.agent.execute(request)

        # Token usage from metadata if available
        usage = response.metadata.get("usage", {})
        prompt_tokens = usage.get("prompt_token_count", 0)
        completion_tokens = usage.get("candidates_token_count", 0)
        total_tokens = usage.get("total_token_count", 0)

        return {
            "content": response.content,
            "model": model or response.metadata.get("model", "gemini"),
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "metadata": response.metadata,
        }

    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs
    ) -> dict[str, Any]:
        """
        Adapt Gemini for code execution sandbox.
        """

        # Use gemini to analyze or validate code
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
