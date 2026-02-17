"""Claude integration adapters for Codomyrmex modules.

Provides adapters that bridge the ClaudeClient with other Codomyrmex modules,
enabling seamless integration for code editing, LLM operations, and code execution.
"""

from collections.abc import Iterator
from typing import Any

from codomyrmex.agents.core import AgentIntegrationAdapter, AgentRequest
from codomyrmex.logging_monitoring import get_logger


class ClaudeIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Claude with Codomyrmex modules.

    This adapter provides specialized methods for integrating the Claude
    agent with various Codomyrmex modules including:
    - AI Code Editing (code generation, refactoring)
    - LLM module (general language model operations)
    - Code Execution sandbox (code analysis)

    Example:
        ```python
        from codomyrmex.agents.claude import ClaudeClient, ClaudeIntegrationAdapter

        client = ClaudeClient()
        adapter = ClaudeIntegrationAdapter(client)

        # Generate code
        code = adapter.adapt_for_ai_code_editing(
            prompt="Create a function that calculates fibonacci",
            language="python",
            style="functional"
        )
        ```
    """

    def __init__(self, agent):
        """Initialize the Claude integration adapter.

        Args:
            agent: A ClaudeClient instance to use for API calls
        """
        super().__init__(agent)
        self.logger = get_logger(self.__class__.__name__)

    def adapt_for_ai_code_editing(
        self,
        prompt: str,
        language: str = "python",
        style: str | None = None,
        context_code: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any
    ) -> str:
        """Adapt Claude for AI code editing module.

        Generates code using Claude with optimized prompts for code generation.
        Includes context-aware prompting and language-specific optimizations.

        Args:
            prompt: Code generation prompt describing what code to create
            language: Programming language for the generated code
            style: Optional coding style hints (e.g., "functional", "oop", "minimal")
            context_code: Optional existing code for context
            max_tokens: Optional override for max output tokens
            temperature: Optional override for sampling temperature
            **kwargs: Additional context parameters

        Returns:
            Generated code as a string

        Raises:
            RuntimeError: If code generation fails
        """
        # Build optimized prompt for code generation
        system_prompt = self._build_code_generation_system_prompt(language, style)

        full_prompt = prompt
        if context_code:
            full_prompt = f"Existing code context:\n```{language}\n{context_code}\n```\n\n{prompt}"

        # Build context with system prompt
        context = {
            "system": system_prompt,
            "language": language,
            "task": "code_generation",
            **kwargs
        }

        request = AgentRequest(
            prompt=full_prompt,
            context=context,
        )

        # Override agent parameters if specified
        original_max_tokens = None
        original_temperature = None

        if max_tokens is not None and hasattr(self.agent, 'max_tokens'):
            original_max_tokens = self.agent.max_tokens
            self.agent.max_tokens = max_tokens

        if temperature is not None and hasattr(self.agent, 'temperature'):
            original_temperature = self.agent.temperature
            self.agent.temperature = temperature

        try:
            response = self.agent.execute(request)
        finally:
            # Restore original parameters
            if original_max_tokens is not None:
                self.agent.max_tokens = original_max_tokens
            if original_temperature is not None:
                self.agent.temperature = original_temperature

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
                "cost_usd": response.metadata.get("cost_usd"),
            },
        )

        # Extract code from response if it's wrapped in markdown
        return self._extract_code_from_response(response.content, language)

    def adapt_for_ai_code_editing_stream(
        self,
        prompt: str,
        language: str = "python",
        **kwargs: Any
    ) -> Iterator[str]:
        """Stream code generation for AI code editing module.

        Args:
            prompt: Code generation prompt
            language: Programming language
            **kwargs: Additional parameters

        Yields:
            Chunks of generated code
        """
        system_prompt = self._build_code_generation_system_prompt(language)

        context = {
            "system": system_prompt,
            "language": language,
            **kwargs
        }

        request = AgentRequest(
            prompt=f"Generate {language} code: {prompt}",
            context=context,
        )

        yield from self.agent.stream(request)

    def adapt_for_llm(
        self,
        messages: list[dict],
        model: str | None = None,
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Adapt Claude for LLM module.

        Provides a standardized interface for the LLM module to use Claude
        as a backend provider.

        Args:
            messages: Conversation messages in OpenAI-compatible format
            model: Model name (optional, uses Claude default)
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Completion result dictionary with:
            - content: The response text
            - model: Model used
            - usage: Token usage statistics
            - metadata: Additional response metadata
        """
        # Extract system message from messages if present
        conversation_messages = []
        extracted_system = system_prompt

        for msg in messages:
            if msg.get("role") == "system":
                if not extracted_system:
                    extracted_system = msg.get("content", "")
            else:
                conversation_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Build context with conversation history
        context: dict[str, Any] = {**kwargs}
        if extracted_system:
            context["system"] = extracted_system
        if len(conversation_messages) > 1:
            context["messages"] = conversation_messages[:-1]

        # Get the last user message as the prompt
        last_message = conversation_messages[-1] if conversation_messages else {"content": ""}
        prompt = last_message.get("content", "")

        request = AgentRequest(prompt=prompt, context=context)
        response = self.agent.execute(request)

        return {
            "content": response.content,
            "model": model or getattr(self.agent, 'model', 'claude'),
            "usage": {
                "prompt_tokens": response.metadata.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": response.metadata.get("usage", {}).get("output_tokens", 0),
                "total_tokens": response.tokens_used or 0,
            },
            "metadata": {
                **response.metadata,
                "execution_time": response.execution_time,
                "success": response.is_success(),
                "error": response.error,
            },
        }

    def adapt_for_code_execution(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "general",
        **kwargs: Any
    ) -> dict[str, Any]:
        """Adapt Claude for code execution sandbox.

        Uses Claude to analyze code for potential issues before or after execution.
        This is useful for security analysis, bug detection, and code review.

        Args:
            code: Code to analyze
            language: Programming language
            analysis_type: Type of analysis ("general", "security", "bugs", "performance")
            **kwargs: Additional parameters

        Returns:
            Analysis result dictionary with:
            - success: Whether analysis completed
            - output: Analysis results
            - issues: List of identified issues
            - recommendations: List of recommendations
            - error: Error message if failed
        """
        # Build analysis-specific prompt
        analysis_prompts = {
            "general": "Analyze this code for correctness, style, and potential improvements.",
            "security": "Perform a security analysis of this code. Identify potential vulnerabilities, injection risks, and security best practices violations.",
            "bugs": "Analyze this code for bugs, edge cases, and potential runtime errors.",
            "performance": "Analyze this code for performance issues, inefficiencies, and optimization opportunities.",
        }

        analysis_instruction = analysis_prompts.get(analysis_type, analysis_prompts["general"])

        prompt = f"""{analysis_instruction}

```{language}
{code}
```

Provide your analysis in a structured format with:
1. Summary of findings
2. Specific issues identified (if any)
3. Recommendations for improvement"""

        context = {
            "system": f"You are an expert {language} code analyst. Provide thorough, actionable analysis.",
            "language": language,
            "analysis_type": analysis_type,
            **kwargs
        }

        request = AgentRequest(prompt=prompt, context=context)
        response = self.agent.execute(request)

        result = {
            "success": response.is_success(),
            "output": response.content,
            "language": language,
            "analysis_type": analysis_type,
            "metadata": response.metadata,
        }

        if response.error:
            result["error"] = response.error

        # Parse structured output if available
        if response.is_success():
            parsed = self._parse_analysis_output(response.content)
            result.update(parsed)

        return result

    def adapt_for_code_refactoring(
        self,
        code: str,
        instruction: str,
        language: str = "python",
        **kwargs: Any
    ) -> dict[str, Any]:
        """Adapt Claude for code refactoring operations.

        Args:
            code: Code to refactor
            instruction: Refactoring instruction
            language: Programming language
            **kwargs: Additional parameters

        Returns:
            Refactoring result dictionary
        """
        prompt = f"""Refactor this {language} code according to the following instruction:

Instruction: {instruction}

Original code:
```{language}
{code}
```

Provide:
1. The refactored code
2. A brief explanation of the changes made"""

        context = {
            "system": f"You are an expert {language} developer. Provide clean, well-structured refactored code.",
            "language": language,
            "task": "refactoring",
            **kwargs
        }

        request = AgentRequest(prompt=prompt, context=context)
        response = self.agent.execute(request)

        result = {
            "success": response.is_success(),
            "refactored_code": self._extract_code_from_response(response.content, language),
            "explanation": response.content,
            "original_code": code,
            "instruction": instruction,
            "metadata": response.metadata,
        }

        if response.error:
            result["error"] = response.error

        return result

    def _build_code_generation_system_prompt(
        self,
        language: str,
        style: str | None = None
    ) -> str:
        """Build optimized system prompt for code generation.

        Args:
            language: Target programming language
            style: Optional coding style

        Returns:
            System prompt string
        """
        base_prompt = f"""You are an expert {language} developer. Generate clean, efficient, and well-documented code.

Guidelines:
- Follow {language} best practices and idioms
- Include appropriate error handling
- Add concise but helpful comments where needed
- Ensure code is production-ready and maintainable
- Do not include unnecessary boilerplate"""

        if style:
            style_hints = {
                "functional": "- Prefer functional programming patterns (pure functions, immutability)",
                "oop": "- Use object-oriented design patterns where appropriate",
                "minimal": "- Keep the code as minimal and concise as possible",
                "verbose": "- Include detailed documentation and explicit type hints",
            }
            if style in style_hints:
                base_prompt += f"\n{style_hints[style]}"

        return base_prompt

    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from markdown-formatted response.

        Args:
            response: Full response text
            language: Expected language for code block

        Returns:
            Extracted code or original response if no code block found
        """
        import re

        # Try to find code block with specific language
        pattern = rf"```{language}\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try generic code block
        pattern = r"```\n?(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Return original if no code block
        return response.strip()

    def _parse_analysis_output(self, output: str) -> dict[str, Any]:
        """Parse structured analysis output.

        Args:
            output: Raw analysis output

        Returns:
            Parsed analysis components
        """
        result: dict[str, Any] = {
            "issues": [],
            "recommendations": [],
        }

        lines = output.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            lower_line = line.lower()

            if "issue" in lower_line or "problem" in lower_line or "bug" in lower_line:
                current_section = "issues"
            elif "recommend" in lower_line or "suggestion" in lower_line:
                current_section = "recommendations"
            elif line.startswith(('-', '*', '•')) and current_section:
                item = line.lstrip('-*• ').strip()
                if item and current_section in result:
                    result[current_section].append(item)

        return result
