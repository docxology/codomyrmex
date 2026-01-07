"""Gemini integration adapters for Codomyrmex modules."""

from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter, AgentInterface


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
        from codomyrmex.agents.core import AgentRequest

        # Build prompt with language context
        full_prompt = f"Generate {language} code: {prompt}"

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
            logger.error(f"Gemini code generation failed: {response.error}")
            raise RuntimeError(f"Code generation failed: {response.error}")

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
        from codomyrmex.agents.core import AgentRequest

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

        # If model is specified, use /model command
        if model:
            prompt = f"/model {model}\n{prompt}"

        request = AgentRequest(prompt=prompt, context=kwargs)

        response = self.agent.execute(request)

        # Estimate token usage (rough approximation)
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response.content.split()) if response.content else 0

        return {
            "content": response.content,
            "model": model or "gemini",
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
        Adapt Gemini for code execution sandbox.

        Args:
            code: Code to analyze
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Analysis result dictionary
        """
        from codomyrmex.agents.core import AgentRequest

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

