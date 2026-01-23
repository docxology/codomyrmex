"""
Model Runner - Flexible model execution for Codomyrmex

Provides advanced model execution capabilities with various parameters,
streaming support, and integration options.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Callable, Optional

import aiohttp

from codomyrmex.logging_monitoring import get_logger

from .ollama_manager import ModelExecutionResult, OllamaManager


@dataclass
class ExecutionOptions:
    """
    Configuration options for model execution.
    
    All parameters are modular and can be set independently.
    Defaults are optimized for general-purpose text generation.
    
    Parameters:
        temperature (float): Controls randomness (0.0-2.0). Lower = more deterministic.
            Default: 0.7
        top_p (float): Nucleus sampling threshold (0.0-1.0). Controls diversity.
            Default: 0.9
        top_k (int): Top-k sampling. Number of highest probability tokens to consider.
            Default: 40
        repeat_penalty (float): Penalty for repeating tokens (1.0 = no penalty).
            Default: 1.1
        max_tokens (int): Maximum number of tokens to generate.
            Default: 2048
        timeout (int): Execution timeout in seconds.
            Default: 300
        stream (bool): Whether to stream the response (not yet fully implemented).
            Default: False
        format (Optional[str]): Output format, e.g., "json" for structured output.
            Default: None (text)
        system_prompt (Optional[str]): System prompt for the model.
            Default: None
        context_window (Optional[int]): Context window size (if supported by model).
            Default: None
    """
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    max_tokens: int = 2048
    timeout: int = 300
    stream: bool = False
    format: Optional[str] = None  # "json" for structured output
    system_prompt: Optional[str] = None
    context_window: Optional[int] = None


@dataclass
class StreamingChunk:
    """A chunk of streaming response."""
    content: str
    done: bool = False
    token_count: Optional[int] = None


class ModelRunner:
    """
    Advanced model execution engine for Codomyrmex.

    Provides flexible execution with streaming, custom parameters,
    and integration with Codomyrmex ecosystem.
    """

    def __init__(self, ollama_manager: OllamaManager):
        """
        Initialize the model runner.

        Args:
            ollama_manager: Instance of OllamaManager
        """
        self.ollama_manager = ollama_manager
        self.logger = get_logger(__name__)

    def run_with_options(
        self,
        model_name: str,
        prompt: str,
        options: Optional[ExecutionOptions] = None,
        save_output: bool = True,
        output_dir: Optional[str] = None
    ) -> ModelExecutionResult:
        """
        Run a model with custom execution options.

        Args:
            model_name: Name of the model to run
            prompt: Input prompt
            options: Execution options
            save_output: Whether to save output
            output_dir: Output directory

        Returns:
            ModelExecutionResult
        """
        if options is None:
            options = ExecutionOptions()

        # Convert options to Ollama format
        ollama_options = {
            'temperature': options.temperature,
            'top_p': options.top_p,
            'top_k': options.top_k,
            'repeat_penalty': options.repeat_penalty,
        }

        if options.max_tokens:
            ollama_options['num_predict'] = options.max_tokens

        if options.format:
            ollama_options['format'] = options.format

        # Handle context window - use 'num_ctx' for Ollama API
        if options.context_window:
            ollama_options['num_ctx'] = options.context_window

        # Handle system prompt - use 'system' key for HTTP API
        if options.system_prompt:
            ollama_options['system'] = options.system_prompt
            full_prompt = prompt  # Keep prompt separate when using system prompt
        else:
            full_prompt = prompt

        return self.ollama_manager.run_model(
            model_name,
            full_prompt,
            options=ollama_options,
            save_output=save_output,
            output_dir=output_dir
        )

    def run_streaming(
        self,
        model_name: str,
        prompt: str,
        options: Optional[ExecutionOptions] = None,
        chunk_callback: Optional[Callable[[StreamingChunk], None]] = None
    ) -> ModelExecutionResult:
        """
        Run a model with streaming output.

        Args:
            model_name: Name of the model to run
            prompt: Input prompt
            options: Execution options
            chunk_callback: Callback function for each streaming chunk

        Returns:
            ModelExecutionResult with collected response
        """
        if options is None:
            options = ExecutionOptions()
        options.stream = True

        # For now, implement streaming as a series of regular calls
        # In a full implementation, this would use Ollama's streaming API
        self.logger.info(f"Starting streaming execution for {model_name}")

        # Run the model and collect chunks
        result = self.run_with_options(model_name, prompt, options)

        if result.success and chunk_callback:
            # Simulate streaming by calling callback with response
            chunk = StreamingChunk(
                content=result.response,
                done=True
            )
            chunk_callback(chunk)

        return result

    def run_batch(
        self,
        model_name: str,
        prompts: list[str],
        options: Optional[ExecutionOptions] = None,
        max_concurrent: int = 3
    ) -> list[ModelExecutionResult]:
        """
        Run multiple prompts in batch with concurrency control.

        Args:
            model_name: Name of the model to run
            prompts: List of prompts to execute
            options: Execution options
            max_concurrent: Maximum concurrent executions

        Returns:
            List of ModelExecutionResult objects
        """
        self.logger.info(f"Running batch of {len(prompts)} prompts with {model_name}")

        async def run_batch_async():
            semaphore = asyncio.Semaphore(max_concurrent)
            results = []

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
                    final_results.append(ModelExecutionResult(
                        model_name=model_name,
                        prompt=prompts[i],
                        response="",
                        execution_time=0,
                        success=False,
                        error_message=str(result)
                    ))
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
        options: Optional[ExecutionOptions] = None
    ) -> ModelExecutionResult:
        """
        Run a conversational model execution.

        Args:
            model_name: Name of the model to run
            messages: List of message dictionaries with 'role' and 'content'
            options: Execution options

        Returns:
            ModelExecutionResult
        """
        # Convert conversation format to prompt
        conversation_prompt = self._format_conversation(messages)

        return self.run_with_options(model_name, conversation_prompt, options)

    def _format_conversation(self, messages: list[dict[str, str]]) -> str:
        """Format conversation messages into a single prompt."""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'system':
                formatted.append(f"System: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")
            else:  # user or default
                formatted.append(f"User: {content}")

        return '\n\n'.join(formatted)

    def run_with_context(
        self,
        model_name: str,
        prompt: str,
        context_docs: list[str],
        options: Optional[ExecutionOptions] = None
    ) -> ModelExecutionResult:
        """
        Run a model with additional context documents.

        Args:
            model_name: Name of the model to run
            prompt: Main prompt
            context_docs: List of context documents
            options: Execution options

        Returns:
            ModelExecutionResult
        """
        # Combine context with prompt
        if options is None:
            options = ExecutionOptions()

        # Add context to system prompt
        context_text = '\n\n'.join([f"Context {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])

        if options.system_prompt:
            options.system_prompt += f"\n\nAdditional Context:\n{context_text}"
        else:
            options.system_prompt = f"Use the following context to inform your response:\n{context_text}"

        return self.run_with_options(model_name, prompt, options)

    def benchmark_model(
        self,
        model_name: str,
        test_prompts: list[str],
        options: Optional[ExecutionOptions] = None
    ) -> dict[str, Any]:
        """
        Benchmark a model with multiple test prompts.

        Args:
            model_name: Name of the model to benchmark
            test_prompts: List of test prompts
            options: Execution options

        Returns:
            Benchmark results dictionary
        """
        self.logger.info(f"Benchmarking model {model_name} with {len(test_prompts)} prompts")

        results = []
        total_start_time = time.time()

        for i, prompt in enumerate(test_prompts):
            self.logger.info(f"Running benchmark prompt {i+1}/{len(test_prompts)}")

            result = self.run_with_options(model_name, prompt, options)

            benchmark_data = {
                'prompt_index': i,
                'prompt_length': len(prompt),
                'execution_time': result.execution_time,
                'success': result.success,
                'response_length': len(result.response) if result.success else 0,
                'tokens_per_second': len(result.response) / result.execution_time if result.success and result.execution_time > 0 else 0
            }

            results.append(benchmark_data)

        total_time = time.time() - total_start_time

        # Calculate statistics
        successful_runs = [r for r in results if r['success']]
        failed_runs = [r for r in results if not r['success']]

        benchmark_summary = {
            'model_name': model_name,
            'total_prompts': len(test_prompts),
            'successful_runs': len(successful_runs),
            'failed_runs': len(failed_runs),
            'total_time': total_time,
            'avg_execution_time': sum(r['execution_time'] for r in successful_runs) / len(successful_runs) if successful_runs else 0,
            'avg_tokens_per_second': sum(r['tokens_per_second'] for r in successful_runs) / len(successful_runs) if successful_runs else 0,
            'detailed_results': results
        }

        self.logger.info(f"Benchmark completed: {len(successful_runs)}/{len(test_prompts)} successful")
        return benchmark_summary

    def create_model_comparison(
        self,
        model_names: list[str],
        test_prompt: str,
        options: Optional[ExecutionOptions] = None
    ) -> dict[str, Any]:
        """
        Compare multiple models on the same prompt.

        Args:
            model_names: List of model names to compare
            test_prompt: Test prompt to use
            options: Execution options

        Returns:
            Comparison results dictionary
        """
        self.logger.info(f"Comparing {len(model_names)} models on the same prompt")

        comparison_results = {}

        for model_name in model_names:
            if not self.ollama_manager.is_model_available(model_name):
                self.logger.warning(f"Model {model_name} not available, skipping")
                continue

            result = self.run_with_options(model_name, test_prompt, options)

            comparison_results[model_name] = {
                'success': result.success,
                'execution_time': result.execution_time,
                'response_length': len(result.response) if result.success else 0,
                'tokens_per_second': len(result.response) / result.execution_time if result.success and result.execution_time > 0 else 0,
                'response_preview': result.response[:200] + "..." if result.success and len(result.response) > 200 else result.response,
                'error': result.error_message if not result.success else None
            }

        return {
            'test_prompt': test_prompt,
            'models_compared': len(comparison_results),
            'results': comparison_results,
            'summary': self._create_comparison_summary(comparison_results)
        }

    def _create_comparison_summary(self, results: dict[str, dict]) -> dict[str, Any]:
        """Create summary statistics for model comparison."""
        successful_results = {name: data for name, data in results.items() if data['success']}

        if not successful_results:
            return {'error': 'No successful model executions'}

        execution_times = [data['execution_time'] for data in successful_results.values()]
        tokens_per_sec = [data['tokens_per_second'] for data in successful_results.values()]

        return {
            'fastest_model': min(successful_results.items(), key=lambda x: x[1]['execution_time'])[0],
            'slowest_model': max(successful_results.items(), key=lambda x: x[1]['execution_time'])[0],
            'most_efficient': max(successful_results.items(), key=lambda x: x[1]['tokens_per_second'])[0],
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'avg_tokens_per_second': sum(tokens_per_sec) / len(tokens_per_sec),
            'success_rate': len(successful_results) / len(results)
        }

    # =========================================================================
    # ASYNC VARIANTS FOR I/O-BOUND OPERATIONS
    # =========================================================================

    async def async_run_model(
        self,
        model_name: str,
        prompt: str,
        options: Optional[ExecutionOptions] = None,
        timeout: int = 300
    ) -> ModelExecutionResult:
        """
        Run a model asynchronously with custom execution options.

        Uses aiohttp for non-blocking HTTP requests to the Ollama API.

        Args:
            model_name: Name of the model to run
            prompt: Input prompt
            options: Execution options
            timeout: Request timeout in seconds (default 300)

        Returns:
            ModelExecutionResult with execution details
        """
        if options is None:
            options = ExecutionOptions()

        self.logger.info(f"[ASYNC] Running model {model_name} with prompt length: {len(prompt)}")

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
            }
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
                    f"{self.ollama_manager.base_url}/api/generate",
                    json=payload
                ) as response:
                    execution_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "").strip()
                        tokens_used = data.get("eval_count")

                        self.logger.info(
                            f"[ASYNC] Model {model_name} completed in {execution_time:.2f}s"
                        )

                        return ModelExecutionResult(
                            model_name=model_name,
                            prompt=prompt,
                            response=response_text,
                            execution_time=execution_time,
                            tokens_used=tokens_used,
                            success=True,
                            error_message=None,
                            metadata={"api_method": "async_http"}
                        )
                    else:
                        error_text = await response.text()
                        error_msg = f"HTTP {response.status}: {error_text}"
                        self.logger.error(f"[ASYNC] Model {model_name} failed: {error_msg}")

                        return ModelExecutionResult(
                            model_name=model_name,
                            prompt=prompt,
                            response="",
                            execution_time=execution_time,
                            success=False,
                            error_message=error_msg
                        )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message="Model execution timed out"
            )
        except aiohttp.ClientError as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Execution error: {str(e)}"
            )

    async def async_generate(
        self,
        model_name: str,
        prompt: str,
        options: Optional[ExecutionOptions] = None,
        timeout: int = 300
    ) -> ModelExecutionResult:
        """
        Generate text asynchronously using the specified model.

        This is an alias for async_run_model with a more intuitive name
        for text generation tasks.

        Args:
            model_name: Name of the model to use
            prompt: Input prompt for generation
            options: Execution options (temperature, top_p, etc.)
            timeout: Request timeout in seconds

        Returns:
            ModelExecutionResult with generated text
        """
        return await self.async_run_model(model_name, prompt, options, timeout)

    async def async_chat(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        options: Optional[ExecutionOptions] = None,
        timeout: int = 300
    ) -> ModelExecutionResult:
        """
        Run a chat conversation asynchronously.

        Uses Ollama's chat API endpoint for multi-turn conversations.

        Args:
            model_name: Name of the model to use
            messages: List of message dicts with 'role' and 'content' keys
                     Roles can be: 'system', 'user', 'assistant'
            options: Execution options
            timeout: Request timeout in seconds

        Returns:
            ModelExecutionResult with assistant's response
        """
        if options is None:
            options = ExecutionOptions()

        self.logger.info(
            f"[ASYNC] Running chat with {model_name}, {len(messages)} messages"
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
            }
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
                    f"{self.ollama_manager.base_url}/api/chat",
                    json=payload
                ) as response:
                    execution_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        message = data.get("message", {})
                        response_text = message.get("content", "").strip()
                        tokens_used = data.get("eval_count")

                        self.logger.info(
                            f"[ASYNC] Chat with {model_name} completed in {execution_time:.2f}s"
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
                                "role": message.get("role", "assistant")
                            }
                        )
                    else:
                        error_text = await response.text()
                        error_msg = f"HTTP {response.status}: {error_text}"
                        self.logger.error(f"[ASYNC] Chat with {model_name} failed: {error_msg}")

                        return ModelExecutionResult(
                            model_name=model_name,
                            prompt=json.dumps(messages),
                            response="",
                            execution_time=execution_time,
                            success=False,
                            error_message=error_msg
                        )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=json.dumps(messages),
                response="",
                execution_time=execution_time,
                success=False,
                error_message="Chat execution timed out"
            )
        except aiohttp.ClientError as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=json.dumps(messages),
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=json.dumps(messages),
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Execution error: {str(e)}"
            )

    async def async_generate_stream(
        self,
        model_name: str,
        prompt: str,
        options: Optional[ExecutionOptions] = None,
        timeout: int = 300
    ) -> AsyncIterator[StreamingChunk]:
        """
        Generate text asynchronously with streaming output.

        Yields chunks as they are generated by the model.

        Args:
            model_name: Name of the model to use
            prompt: Input prompt for generation
            options: Execution options
            timeout: Request timeout in seconds

        Yields:
            StreamingChunk objects with partial content
        """
        if options is None:
            options = ExecutionOptions()

        self.logger.info(f"[ASYNC] Starting streaming generation with {model_name}")

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
            }
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
                    f"{self.ollama_manager.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield StreamingChunk(
                            content="",
                            done=True,
                            token_count=0
                        )
                        self.logger.error(f"[ASYNC] Stream failed: HTTP {response.status}")
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
                                    token_count=eval_count
                                )

                                if is_done:
                                    self.logger.info(
                                        f"[ASYNC] Streaming generation completed"
                                    )
                                    return

                            except json.JSONDecodeError:
                                continue

        except asyncio.TimeoutError:
            self.logger.error("[ASYNC] Streaming generation timed out")
            yield StreamingChunk(content="", done=True, token_count=0)
        except aiohttp.ClientError as e:
            self.logger.error(f"[ASYNC] Streaming network error: {e}")
            yield StreamingChunk(content="", done=True, token_count=0)
        except Exception as e:
            self.logger.error(f"[ASYNC] Streaming error: {e}")
            yield StreamingChunk(content="", done=True, token_count=0)

    async def async_run_batch(
        self,
        model_name: str,
        prompts: list[str],
        options: Optional[ExecutionOptions] = None,
        max_concurrent: int = 3
    ) -> list[ModelExecutionResult]:
        """
        Run multiple prompts in batch asynchronously with concurrency control.

        Args:
            model_name: Name of the model to run
            prompts: List of prompts to execute
            options: Execution options
            max_concurrent: Maximum concurrent executions

        Returns:
            List of ModelExecutionResult objects
        """
        self.logger.info(
            f"[ASYNC] Running batch of {len(prompts)} prompts with {model_name}"
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
                final_results.append(ModelExecutionResult(
                    model_name=model_name,
                    prompt=prompts[i],
                    response="",
                    execution_time=0,
                    success=False,
                    error_message=str(result)
                ))
            else:
                final_results.append(result)

        self.logger.info(
            f"[ASYNC] Batch completed: {sum(1 for r in final_results if r.success)}/{len(final_results)} successful"
        )

        return final_results
