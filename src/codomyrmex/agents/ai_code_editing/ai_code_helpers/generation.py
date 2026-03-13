"""AI Code Generation Helpers."""

import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed

with contextlib.suppress(ImportError):
    from google.genai import types
try:
    from codomyrmex.performance import monitor_performance
except ImportError:

    def monitor_performance(name):
        def decorator(func):
            return func

        return decorator


import time
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .config import DEFAULT_LLM_PROVIDER, get_llm_client
from .models import CodeGenerationRequest, CodeGenerationResult

logger = get_logger(__name__)


@monitor_performance("ai_code_generation")
def generate_code_snippet(
    prompt: str,
    language: str,
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: str | None = None,
    context: str | None = None,
    max_length: int | None = None,
    temperature: float = 0.7,
    **kwargs,
) -> dict[str, Any]:
    """
    Generate a code snippet using an LLM.

    Args:
        prompt: The prompt describing what code to generate
        language: Programming language for the generated code
        provider: LLM provider to use ("openai", "anthropic", "google")
        model_name: Specific model to use (optional)
        context: Additional context for the generation
        max_length: Maximum length of generated code
        temperature: Sampling temperature (0.0 to 1.0)
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing generated code and metadata

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If code generation fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if not language:
            raise ValueError("Language must be specified")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt
        full_prompt = f"Generate {language} code for: {prompt}"
        if context:
            full_prompt += f"\n\nContext: {context}"

        # Add language-specific instructions
        language_instructions = {
            "python": "Follow PEP 8 style guidelines and include proper error handling.",
            "javascript": "Use modern ES6+ syntax and include JSDoc comments.",
            "typescript": "Use TypeScript best practices with proper type annotations.",
            "java": "Follow Java naming conventions and include JavaDoc comments.",
            "cpp": "Use modern C++ features and include proper memory management.",
        }

        if language.lower() in language_instructions:
            full_prompt += f"\n\n{language_instructions[language.lower()]}"

        # Generate code based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=max_length or 1000,
                temperature=temperature,
                **kwargs,
            )
            generated_code = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model,
                max_tokens=max_length or 1000,
                temperature=temperature,
                messages=[{"role": "user", "content": full_prompt}],
                **kwargs,
            )
            generated_code = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_length or 2000,
                    temperature=temperature,
                )
                if types
                else None,
            )
            generated_code = response.text
            tokens_used = (
                response.usage_metadata.total_token_count
                if hasattr(response, "usage_metadata")
                else None
            )

        elif provider == "ollama":
            # Use Ollama integration
            options = {
                "temperature": temperature,
            }
            if max_length:
                options["max_tokens"] = max_length

            result = client.run_model(
                model_name=model, prompt=full_prompt, options=options, save_output=False
            )
            generated_code = result.response
            tokens_used = result.tokens_used

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "generated_code": generated_code,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "prompt": prompt,
                "context": context,
                "temperature": temperature,
                "max_length": max_length,
            },
        }

        logger.info(
            "Generated %s code snippet using %s/%s in %.2fs",
            language,
            provider,
            model,
            execution_time,
        )
        return result

    except (ValueError, ImportError, AttributeError) as e:
        logger.error("Error generating code snippet: %s", e)
        raise RuntimeError(f"Code generation failed: {e}") from None
    except Exception as e:
        # Final fallback for unexpected API errors or network issues
        logger.error("Unexpected error generating code snippet: %s", e, exc_info=True)
        raise RuntimeError(f"Code generation failed: {e}") from None


def _dispatch_document(client, provider: str, model: str, prompt: str, **kwargs):
    """Call the provider API for documentation and return (documentation, tokens_used)."""
    if provider == "openai":
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], **kwargs
        )
        return response.choices[0].message.content, (
            response.usage.total_tokens if response.usage else None
        )
    if provider == "anthropic":
        response = client.messages.create(
            model=model, messages=[{"role": "user", "content": prompt}], **kwargs
        )
        tokens = (
            (response.usage.input_tokens + response.usage.output_tokens)
            if response.usage
            else None
        )
        return response.content[0].text, tokens
    if provider == "google":
        model_instance = client.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text, None
    if provider == "ollama":
        result = client.run_model(model_name=model, prompt=prompt, save_output=False)
        return result.response, result.tokens_used
    raise ValueError(f"Unsupported provider: {provider}")


def _make_error_result(
    language, request_language, e: Exception
) -> "CodeGenerationResult":
    """Return a failed CodeGenerationResult for batch processing."""
    return CodeGenerationResult(
        generated_code="",
        language=request_language,
        metadata={"error": str(e)},
        execution_time=0.0,
    )


def _process_single_request(
    request: CodeGenerationRequest, provider, model_name, **kwargs
) -> CodeGenerationResult:
    """Process one CodeGenerationRequest, returning a result or an error result."""
    try:
        result = generate_code_snippet(
            prompt=request.prompt,
            language=request.language.value,
            provider=provider,
            model_name=model_name,
            context=request.context,
            max_length=request.max_length,
            temperature=request.temperature,
            **kwargs,
        )
        return CodeGenerationResult(
            generated_code=result["generated_code"],
            language=request.language,
            metadata=result["metadata"],
            execution_time=result["execution_time"],
            tokens_used=result.get("tokens_used"),
        )
    except Exception as e:
        logger.error("Error processing request: %s", e)
        return _make_error_result(None, request.language, e)


def _run_parallel_batch(
    requests: list[CodeGenerationRequest],
    max_workers: int,
    provider,
    model_name,
    **kwargs,
) -> list[CodeGenerationResult]:
    """Execute a batch of requests in parallel, preserving original order."""
    logger.info(
        "Processing %s requests in parallel with %s workers", len(requests), max_workers
    )
    results_dict: dict[int, CodeGenerationResult] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(
                _process_single_request, req, provider, model_name, **kwargs
            ): idx
            for idx, req in enumerate(requests)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                results_dict[idx] = future.result()
            except Exception as e:
                logger.error("Parallel execution failed for request %s: %s", idx, e)
                results_dict[idx] = _make_error_result(None, requests[idx].language, e)
    return [results_dict[i] for i in range(len(requests))]


@monitor_performance("ai_code_generation_batch")
def generate_code_batch(
    requests: list[CodeGenerationRequest],
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: str | None = None,
    parallel: bool = False,
    max_workers: int = 4,
    **kwargs,
) -> list[CodeGenerationResult]:
    """Generate multiple code snippets in batch. Returns list of CodeGenerationResult."""
    if not requests:
        raise ValueError("Requests list cannot be empty")
    if parallel and len(requests) > 1:
        return _run_parallel_batch(
            requests, max_workers, provider, model_name, **kwargs
        )
    return [
        _process_single_request(req, provider, model_name, **kwargs) for req in requests
    ]


def _build_doc_prompt(
    language: str, doc_type: str, code: str, context: str | None
) -> str:
    """Build the documentation generation prompt."""
    doc_prompts = {
        "comprehensive": f"Generate comprehensive documentation for the following {language} code, including overview, function descriptions, parameters, return values, and usage examples:",
        "api": f"Generate API documentation for the following {language} code, focusing on public interfaces, method signatures, and parameters:",
        "inline": f"Generate inline documentation (comments) for the following {language} code, following the language's documentation standards:",
        "readme": f"Generate a README-style documentation for the following {language} code, including installation, usage, and examples:",
    }
    prompt = doc_prompts.get(doc_type, doc_prompts["comprehensive"]) + f"\n\n{code}"
    if context:
        prompt += f"\n\nAdditional context: {context}"
    return prompt


@monitor_performance("ai_code_documentation")
def generate_code_documentation(
    code: str,
    language: str,
    doc_type: str = "comprehensive",
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: str | None = None,
    context: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """Generate documentation for code using an LLM. Returns dict with documentation and metadata."""
    if not code or not code.strip():
        raise ValueError("Code cannot be empty")
    start_time = time.time()
    try:
        client, model = get_llm_client(provider, model_name)
        prompt = _build_doc_prompt(language, doc_type, code, context)
        documentation, tokens_used = _dispatch_document(
            client, provider, model, prompt, **kwargs
        )
        execution_time = time.time() - start_time
        logger.info(
            "Generated %s documentation for %s code using %s/%s in %.2fs",
            doc_type,
            language,
            provider,
            model,
            execution_time,
        )
        return {
            "code": code,
            "documentation": documentation,
            "doc_type": doc_type,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {"context": context},
        }
    except (ValueError, ImportError, AttributeError) as e:
        logger.error("Error generating documentation: %s", e)
        raise RuntimeError(f"Documentation generation failed: {e}") from None
    except Exception as e:
        logger.error("Unexpected error generating documentation: %s", e, exc_info=True)
        raise RuntimeError(f"Documentation generation failed: {e}") from None
