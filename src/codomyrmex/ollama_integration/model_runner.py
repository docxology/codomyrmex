"""
Model Runner - Flexible model execution for Codomyrmex

Provides advanced model execution capabilities with various parameters,
streaming support, and integration options.
"""

import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict

from codomyrmex.logging_monitoring import get_logger
from .ollama_manager import OllamaManager, ModelExecutionResult


@dataclass
class ExecutionOptions:
    """Configuration options for model execution."""
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

        if options.system_prompt:
            # Combine system prompt with user prompt
            full_prompt = f"System: {options.system_prompt}\n\nUser: {prompt}"
        else:
            full_prompt = prompt

        return self.ollama_manager.run_model(
            model_name,
            full_prompt,
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
        prompts: List[str],
        options: Optional[ExecutionOptions] = None,
        max_concurrent: int = 3
    ) -> List[ModelExecutionResult]:
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
        messages: List[Dict[str, str]],
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

    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
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
        context_docs: List[str],
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
        test_prompts: List[str],
        options: Optional[ExecutionOptions] = None
    ) -> Dict[str, Any]:
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
        model_names: List[str],
        test_prompt: str,
        options: Optional[ExecutionOptions] = None
    ) -> Dict[str, Any]:
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

    def _create_comparison_summary(self, results: Dict[str, Dict]) -> Dict[str, Any]:
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
