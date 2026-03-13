"""Synchronous execution mixin for Ollama Model Runner.

Extracted from model_runner.py.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from .model_runner import ExecutionOptions, StreamingChunk
from .ollama_manager import ModelExecutionResult


class OllamaExecutionMixin:
    """Mixin for synchronous model execution operations."""

    # Note: Requires self.ollama_manager and self.logger

    def run_with_options(
        self,
        model_name: str,
        prompt: str,
        options: ExecutionOptions | None = None,
        save_output: bool = True,
        output_dir: str | None = None,
    ) -> ModelExecutionResult:
        """Run a model with custom execution options."""
        from .model_runner import ExecutionOptions

        if options is None:
            options = ExecutionOptions()

        # Convert options to Ollama format
        ollama_options = {
            "temperature": options.temperature,
            "top_p": options.top_p,
            "top_k": options.top_k,
            "repeat_penalty": options.repeat_penalty,
        }

        if options.max_tokens:
            ollama_options["num_predict"] = options.max_tokens

        if options.format:
            ollama_options["format"] = options.format

        # Handle context window - use 'num_ctx' for Ollama API
        if options.context_window:
            ollama_options["num_ctx"] = options.context_window

        # Handle system prompt - use 'system' key for HTTP API
        if options.system_prompt:
            ollama_options["system"] = options.system_prompt
            full_prompt = prompt  # Keep prompt separate when using system prompt
        else:
            full_prompt = prompt

        return self.ollama_manager.run_model(
            model_name,
            full_prompt,
            options=ollama_options,
            save_output=save_output,
            output_dir=output_dir,
        )

    def run_streaming(
        self,
        model_name: str,
        prompt: str,
        options: ExecutionOptions | None = None,
        chunk_callback: Callable[[StreamingChunk], None] | None = None,
    ) -> ModelExecutionResult:
        """Run a model with streaming output."""
        from .model_runner import ExecutionOptions, StreamingChunk

        if options is None:
            options = ExecutionOptions()
        options.stream = True

        self.logger.info("Starting streaming execution for %s", model_name)

        # Run the model and collect chunks
        result = self.run_with_options(model_name, prompt, options)

        if result.success and chunk_callback:
            # Simulate streaming by calling callback with response
            chunk = StreamingChunk(content=result.response, done=True)
            chunk_callback(chunk)

        return result

    def run_batch(
        self,
        model_name: str,
        prompts: list[str],
        options: ExecutionOptions | None = None,
        max_concurrent: int = 3,
    ) -> list[ModelExecutionResult]:
        """Run multiple prompts in batch with concurrency control."""
        self.logger.info("Running batch of %s prompts with %s", len(prompts), model_name)

        async def run_batch_async() -> list[ModelExecutionResult]:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def run_single(prompt: str) -> ModelExecutionResult:
                async with semaphore:
                    return await self.ollama_manager.run_model_async(
                        model_name, prompt, options.__dict__ if options else None
                    )

            # Create tasks for all prompts
            tasks = [run_single(prompt) for prompt in prompts]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(
                        ModelExecutionResult(
                            model_name=model_name,
                            prompt=prompts[i],
                            response="",
                            execution_time=0,
                            success=False,
                            error_message=str(result),
                        )
                    )
                else:
                    final_results.append(result)

            return final_results

        # Run the async batch
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(run_batch_async())
        finally:
            loop.close()

    def run_conversation(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        options: ExecutionOptions | None = None,
    ) -> ModelExecutionResult:
        """Run a conversational model execution."""
        # Convert conversation format to prompt
        conversation_prompt = self._format_conversation(messages)

        return self.run_with_options(model_name, conversation_prompt, options)

    def _format_conversation(self, messages: list[dict[str, str]]) -> str:
        """Format conversation messages into a single prompt."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
            else:  # user or default
                formatted.append(f"User: {content}")

        return "\n\n".join(formatted)

    def run_with_context(
        self,
        model_name: str,
        prompt: str,
        context_docs: list[str],
        options: ExecutionOptions | None = None,
    ) -> ModelExecutionResult:
        """Run a model with additional context documents."""
        from .model_runner import ExecutionOptions

        # Combine context with prompt
        if options is None:
            options = ExecutionOptions()

        # Add context to system prompt
        context_text = "\n\n".join(
            [f"Context {i + 1}:\n{doc}" for i, doc in enumerate(context_docs)]
        )

        if options.system_prompt:
            options.system_prompt += f"\n\nAdditional Context:\n{context_text}"
        else:
            options.system_prompt = (
                f"Use the following context to inform your response:\n{context_text}"
            )

        return self.run_with_options(model_name, prompt, options)
