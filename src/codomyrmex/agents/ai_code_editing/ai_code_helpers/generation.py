"""AI Code Generation Helpers."""

from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from google.genai import types
except ImportError:
    types = None
try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(name):
        def decorator(func):
            return func
        return decorator


import time
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

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
                ) if types else None
            )
            generated_code = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, "usage_metadata") else None

        elif provider == "ollama":
            # Use Ollama integration
            options = {
                "temperature": temperature,
            }
            if max_length:
                options["max_tokens"] = max_length

            result = client.run_model(
                model_name=model,
                prompt=full_prompt,
                options=options,
                save_output=False
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
            f"Generated {language} code snippet using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except (ValueError, ImportError, AttributeError) as e:
        logger.error(f"Error generating code snippet: {e}")
        raise RuntimeError(f"Code generation failed: {e}") from None
    except Exception as e:
        # Final fallback for unexpected API errors or network issues
        logger.error(f"Unexpected error generating code snippet: {e}", exc_info=True)
        raise RuntimeError(f"Code generation failed: {e}") from None

@monitor_performance("ai_code_generation_batch")
def generate_code_batch(
    requests: list[CodeGenerationRequest],
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: str | None = None,
    parallel: bool = False,
    max_workers: int = 4,
    **kwargs,
) -> list[CodeGenerationResult]:
    """
    Generate multiple code snippets in batch.

    Args:
        requests: List of code generation requests
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        parallel: Whether to process requests in parallel
        max_workers: Maximum number of parallel workers (default: 4)
        **kwargs: Additional parameters for the LLM

    Returns:
        List of code generation results

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If batch generation fails
    """
    if not requests:
        raise ValueError("Requests list cannot be empty")

    def process_request(request: CodeGenerationRequest) -> CodeGenerationResult:
        """Process a single code generation request."""
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

        except (RuntimeError, ValueError, ImportError) as e:
            logger.error(f"Error processing request: {e}")
            return CodeGenerationResult(
                generated_code="",
                language=request.language,
                metadata={"error": str(e)},
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Unexpected error processing request: {e}", exc_info=True)
            return CodeGenerationResult(
                generated_code="",
                language=request.language,
                metadata={"error": str(e)},
                execution_time=0.0,
            )

    if parallel and len(requests) > 1:

        logger.info(f"Processing {len(requests)} requests in parallel with {max_workers} workers")
        results_dict: dict[int, CodeGenerationResult] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks and track their indices
            future_to_index = {
                executor.submit(process_request, req): idx
                for idx, req in enumerate(requests)
            }

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    results_dict[idx] = future.result()
                except Exception as e:
                    logger.error(f"Parallel execution failed for request {idx}: {e}")
                    results_dict[idx] = CodeGenerationResult(
                        generated_code="",
                        language=requests[idx].language,
                        metadata={"error": str(e)},
                        execution_time=0.0,
                    )

        # Return results in original order
        return [results_dict[i] for i in range(len(requests))]

    else:
        # Sequential processing
        return [process_request(request) for request in requests]

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
    """
    Generate documentation for code using an LLM.

    Args:
        code: The code to document
        language: Programming language of the code
        doc_type: Type of documentation ("comprehensive", "api", "inline", "readme")
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for documentation
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing generated documentation

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If documentation generation fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt based on documentation type
        doc_prompts = {
            "comprehensive": f"Generate comprehensive documentation for the following {language} code, including overview, function descriptions, parameters, return values, and usage examples:",
            "api": f"Generate API documentation for the following {language} code, focusing on public interfaces, method signatures, and parameters:",
            "inline": f"Generate inline documentation (comments) for the following {language} code, following the language's documentation standards:",
            "readme": f"Generate a README-style documentation for the following {language} code, including installation, usage, and examples:",
        }

        prompt = doc_prompts.get(doc_type, doc_prompts["comprehensive"])
        prompt += f"\n\n{code}"

        if context:
            prompt += f"\n\nAdditional context: {context}"

        # Generate documentation based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            documentation = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            documentation = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            documentation = response.text
            tokens_used = None

        elif provider == "ollama":
            # Use Ollama integration
            result = client.run_model(
                model_name=model,
                prompt=prompt,
                save_output=False
            )
            documentation = result.response
            tokens_used = result.tokens_used

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "code": code,
            "documentation": documentation,
            "doc_type": doc_type,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "context": context,
            },
        }

        logger.info(
            f"Generated {doc_type} documentation for {language} code using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except (ValueError, ImportError, AttributeError) as e:
        logger.error(f"Error generating documentation: {e}")
        raise RuntimeError(f"Documentation generation failed: {e}") from None
    except Exception as e:
        # Final fallback for unexpected API errors or network issues
        logger.error(f"Unexpected error generating documentation: {e}", exc_info=True)
        raise RuntimeError(f"Documentation generation failed: {e}") from None

