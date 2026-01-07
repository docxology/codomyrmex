"""Claude integration adapters for Codomyrmex modules."""

from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter


class ClaudeIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Claude with Codomyrmex modules."""

    def adapt_for_ai_code_editing(
        self, prompt: str, language: str = "python", **kwargs
    ) -> str:
        """
        Adapt Claude for AI code editing module.

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
            self.logger.error(
                "Claude code generation failed",
                extra={
                    "agent": "claude",
                    "language": language,
                    "error": response.error,
                    "execution_time": response.execution_time,
                },
            )
            raise RuntimeError(f"Code generation failed: {response.error}")

        self.logger.debug(
            "Claude code generation succeeded",
            extra={
                "agent": "claude",
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
        Adapt Claude for LLM module.

        Args:
            messages: Conversation messages
            model: Model name (optional, uses Claude default)
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
            "model": model or "claude",
            "usage": {
                "prompt_tokens": response.metadata.get("usage", {}).get(
                    "input_tokens", 0
                ),
                "completion_tokens": response.metadata.get("usage", {}).get(
                    "output_tokens", 0
                ),
            },
            "metadata": response.metadata,
        }

    def adapt_for_code_execution(
        self, code: str, language: str = "python", **kwargs
    ) -> dict[str, Any]:
        """
        Adapt Claude for code execution sandbox.

        Args:
            code: Code to execute
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Execution result dictionary
        """
        from codomyrmex.agents.core import AgentRequest

        # Use Claude to analyze or validate code
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

