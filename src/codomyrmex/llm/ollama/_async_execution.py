"""Asynchronous execution mixin for Ollama Model Runner.

Extracted from model_runner.py.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from .model_runner import ExecutionOptions, StreamingChunk
from .ollama_manager import ModelExecutionResult


class OllamaAsyncExecutionMixin:
    """Mixin for asynchronous model execution operations."""

    # Note: Requires self.ollama_manager and self.logger

    async def async_run_model(
        self,
        model_name: str,
        prompt: str,
        options: ExecutionOptions | None = None,
        timeout: int = 300,
    ) -> ModelExecutionResult:
        """Run a model asynchronously with custom execution options."""
        from .model_runner import ExecutionOptions

        if options is None:
            options = ExecutionOptions()

        self.logger.info(
            "[ASYNC] Running model %s with prompt length: %s", model_name, len(prompt)
        )

        start_time = time.time()

        # Build Ollama API payload
        payload: dict[str, Any] = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "repeat_penalty": options.repeat_penalty,
            },
        }

        if options.max_tokens:
            payload["options"]["num_predict"] = options.max_tokens

        if options.format:
            payload["format"] = options.format

        if options.context_window:
            payload["options"]["num_ctx"] = options.context_window

        if options.system_prompt:
            payload["system"] = options.system_prompt

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.post(
                    f"{self.ollama_manager.base_url}/api/generate", json=payload
                ) as response:
                    execution_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "").strip()
                        tokens_used = data.get("eval_count")

                        self.logger.info(
                            "[ASYNC] Model %s completed in %.2fs",
                            model_name,
                            execution_time,
                        )

                        return ModelExecutionResult(
                            model_name=model_name,
                            prompt=prompt,
                            response=response_text,
                            execution_time=execution_time,
                            tokens_used=tokens_used,
                            success=True,
                            error_message=None,
                            metadata={"api_method": "async_http"},
                        )
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.logger.error(
                        "[ASYNC] Model %s failed: %s", model_name, error_msg
                    )

                    return ModelExecutionResult(
                        model_name=model_name,
                        prompt=prompt,
                        response="",
                        execution_time=execution_time,
                        success=False,
                        error_message=error_msg,
                    )

        except TimeoutError:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message="Model execution timed out",
            )
        except aiohttp.ClientError as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Network error: {e!s}",
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Execution error: {e!s}",
            )

    async def async_generate(
        self,
        model_name: str,
        prompt: str,
        options: ExecutionOptions | None = None,
        timeout: int = 300,
    ) -> ModelExecutionResult:
        """Generate text asynchronously using the specified model."""
        return await self.async_run_model(model_name, prompt, options, timeout)

    async def async_chat(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        options: ExecutionOptions | None = None,
        timeout: int = 300,
    ) -> ModelExecutionResult:
        """Run a chat conversation asynchronously."""
        from .model_runner import ExecutionOptions

        if options is None:
            options = ExecutionOptions()

        self.logger.info(
            "[ASYNC] Running chat with %s, %s messages", model_name, len(messages)
        )

        start_time = time.time()

        # Build Ollama chat API payload
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "repeat_penalty": options.repeat_penalty,
            },
        }

        if options.max_tokens:
            payload["options"]["num_predict"] = options.max_tokens

        if options.format:
            payload["format"] = options.format

        if options.context_window:
            payload["options"]["num_ctx"] = options.context_window

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.post(
                    f"{self.ollama_manager.base_url}/api/chat", json=payload
                ) as response:
                    execution_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        message = data.get("message", {})
                        response_text = message.get("content", "").strip()
                        tokens_used = data.get("eval_count")

                        self.logger.info(
                            "[ASYNC] Chat with %s completed in %.2fs",
                            model_name,
                            execution_time,
                        )

                        # Format the prompt as the conversation for logging
                        prompt_repr = json.dumps(messages, indent=2)

                        return ModelExecutionResult(
                            model_name=model_name,
                            prompt=prompt_repr,
                            response=response_text,
                            execution_time=execution_time,
                            tokens_used=tokens_used,
                            success=True,
                            error_message=None,
                            metadata={
                                "api_method": "async_chat",
                                "message_count": len(messages),
                                "role": message.get("role", "assistant"),
                            },
                        )
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.logger.error(
                        "[ASYNC] Chat with %s failed: %s", model_name, error_msg
                    )

                    return ModelExecutionResult(
                        model_name=model_name,
                        prompt=json.dumps(messages),
                        response="",
                        execution_time=execution_time,
                        success=False,
                        error_message=error_msg,
                    )

        except TimeoutError:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=json.dumps(messages),
                response="",
                execution_time=execution_time,
                success=False,
                error_message="Chat execution timed out",
            )
        except aiohttp.ClientError as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=json.dumps(messages),
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Network error: {e!s}",
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=json.dumps(messages),
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Execution error: {e!s}",
            )

    async def async_generate_stream(
        self,
        model_name: str,
        prompt: str,
        options: ExecutionOptions | None = None,
        timeout: int = 300,
    ) -> AsyncIterator[StreamingChunk]:
        """Generate text asynchronously with streaming output."""
        from .model_runner import ExecutionOptions, StreamingChunk

        if options is None:
            options = ExecutionOptions()

        self.logger.info("[ASYNC] Starting streaming generation with %s", model_name)

        # Build Ollama API payload with streaming enabled
        payload: dict[str, Any] = {
            "model": model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": options.temperature,
                "top_p": options.top_p,
                "top_k": options.top_k,
                "repeat_penalty": options.repeat_penalty,
            },
        }

        if options.max_tokens:
            payload["options"]["num_predict"] = options.max_tokens

        if options.format:
            payload["format"] = options.format

        if options.context_window:
            payload["options"]["num_ctx"] = options.context_window

        if options.system_prompt:
            payload["system"] = options.system_prompt

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.post(
                    f"{self.ollama_manager.base_url}/api/generate", json=payload
                ) as response:
                    if response.status != 200:
                        await response.text()
                        yield StreamingChunk(content="", done=True, token_count=0)
                        self.logger.error(
                            "[ASYNC] Stream failed: HTTP %s", response.status
                        )
                        return

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode("utf-8"))
                                chunk_content = data.get("response", "")
                                is_done = data.get("done", False)
                                eval_count = data.get("eval_count")

                                yield StreamingChunk(
                                    content=chunk_content,
                                    done=is_done,
                                    token_count=eval_count,
                                )

                                if is_done:
                                    self.logger.info(
                                        "[ASYNC] Streaming generation completed"
                                    )
                                    return

                            except json.JSONDecodeError:
                                continue

        except TimeoutError:
            self.logger.error("[ASYNC] Streaming generation timed out")
            yield StreamingChunk(content="", done=True, token_count=0)
        except aiohttp.ClientError as e:
            self.logger.error("[ASYNC] Streaming network error: %s", e)
            yield StreamingChunk(content="", done=True, token_count=0)
        except Exception as e:
            self.logger.error("[ASYNC] Streaming error: %s", e)
            yield StreamingChunk(content="", done=True, token_count=0)

    async def async_run_batch(
        self,
        model_name: str,
        prompts: list[str],
        options: ExecutionOptions | None = None,
        max_concurrent: int = 3,
    ) -> list[ModelExecutionResult]:
        """Run multiple prompts in batch asynchronously with concurrency control."""
        self.logger.info(
            "[ASYNC] Running batch of %s prompts with %s", len(prompts), model_name
        )

        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_single(prompt: str) -> ModelExecutionResult:
            async with semaphore:
                return await self.async_run_model(model_name, prompt, options)

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

        self.logger.info(
            "[ASYNC] Batch completed: %s/%s successful",
            sum(1 for r in final_results if r.success),
            len(final_results),
        )

        return final_results
