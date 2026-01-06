"""Jules integration adapters for Codomyrmex modules."""

from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter, AgentInterface
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


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
        from codomyrmex.agents.core import AgentRequest

        # Build prompt with language context
        full_prompt = f"Generate {language} code: {prompt}"

        request = AgentRequest(
            prompt=full_prompt,
            context={"language": language, **kwargs},
        )

        response = self.agent.execute(request)

        if not response.is_success():
            logger.error(f"Jules code generation failed: {response.error}")
            raise RuntimeError(f"Code generation failed: {response.error}")

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
        from codomyrmex.agents.core import AgentRequest

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
        from codomyrmex.agents.core import AgentRequest

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

