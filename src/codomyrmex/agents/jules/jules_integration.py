from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter, AgentInterface
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.core import AgentRequest
from codomyrmex.logging_monitoring import get_logger
























"""Jules integration adapters for Codomyrmex modules."""

"""Core functionality module

This module provides jules_integration functionality including:
- 3 functions: adapt_for_ai_code_editing, adapt_for_llm, adapt_for_code_execution
- 1 classes: JulesIntegrationAdapter

Usage:
    from jules_integration import FunctionName, ClassName
    # Example usage here
"""
class JulesIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Jules with Codomyrmex modules."""

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """
        Adapt Jules for AI code editing module.

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
                "Jules code generation failed",
                extra={
                    "agent": "jules",
                    "language": language,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Code generation failed: {response.error}")

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
        self, messages: list[dict], model: str = None, **kwargs
    ) -> dict:
        """
        Adapt Jules for LLM module.

        Args:
            messages: Conversation messages
            model: Model name (not used for Jules)
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
            "model": "jules",
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
        Adapt Jules for code execution sandbox.

        Args:
            code: Code to execute
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Execution result dictionary
        """

        # Use jules to validate or analyze code
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

