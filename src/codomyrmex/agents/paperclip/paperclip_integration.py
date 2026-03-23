"""Paperclip integration adapters for Codomyrmex modules."""

from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter, AgentRequest


class PaperclipIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Paperclip with Codomyrmex modules."""

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs: Any
    ) -> str:
        """Adapt Paperclip for AI code editing module.

        Args:
            prompt: Code generation prompt.
            language: Programming language.
            **kwargs: Additional parameters.

        Returns:
            Generated code string.
        """
        full_prompt = f"Generate {language} code: {prompt}"

        request = AgentRequest(
            prompt=full_prompt,
            context={"language": language, **kwargs},
        )

        response = self.agent.execute(request)

        if not response.is_success():
            self.logger.error(
                "Paperclip code generation failed",
                extra={
                    "agent": "paperclip",
                    "language": language,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Code generation failed: {response.error}")

        self.logger.debug(
            "Paperclip code generation succeeded",
            extra={
                "agent": "paperclip",
                "language": language,
                "content_length": len(response.content),
                "execution_time": response.execution_time,
            },
        )

        return response.content

    def adapt_for_llm(
        self, messages: list[dict], model: str | None = None, **kwargs: Any
    ) -> dict:
        """Adapt Paperclip for LLM module.

        Args:
            messages: Conversation messages.
            model: Model name (not directly used for Paperclip).
            **kwargs: Additional parameters.

        Returns:
            Completion result dictionary.
        """
        prompt = "\n".join(
            f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages
        )

        request = AgentRequest(prompt=prompt, context=kwargs)
        response = self.agent.execute(request)

        return {
            "content": response.content,
            "model": "paperclip",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.content.split()),
            },
            "metadata": response.metadata,
        }

    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs: Any
    ) -> dict[str, Any]:
        """Adapt Paperclip for code execution sandbox.

        Args:
            code: Code to execute.
            language: Programming language.
            **kwargs: Additional parameters.

        Returns:
            Execution result dictionary.
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
