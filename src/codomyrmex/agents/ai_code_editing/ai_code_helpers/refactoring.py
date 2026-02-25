"""AI Code Refactoring Helpers."""

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

logger = get_logger(__name__)

@monitor_performance("ai_code_refactoring")
def refactor_code_snippet(
    code: str,
    refactoring_type: str,
    language: str,
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: str | None = None,
    context: str | None = None,
    preserve_functionality: bool = True,
    **kwargs,
) -> dict[str, Any]:
    """
    Refactor existing code using an LLM.

    Args:
        code: The code to refactor
        refactoring_type: Type of refactoring (e.g., "optimize", "simplify", "add_error_handling")
        language: Programming language of the code
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for refactoring
        preserve_functionality: Whether to preserve original functionality
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing refactored code and metadata

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If refactoring fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        if not refactoring_type:
            raise ValueError("Refactoring type must be specified")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt
        functionality_note = (
            "Preserve the original functionality exactly."
            if preserve_functionality
            else "You may modify functionality if it improves the code."
        )

        prompt = f"""Refactor the following {language} code to {refactoring_type}:

{code}

{functionality_note}"""

        if context:
            prompt += f"\n\nAdditional context: {context}"

        # Generate refactored code based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            refactored_code = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            refactored_code = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            refactored_code = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, "usage_metadata") else None

        elif provider == "ollama":
            # Use Ollama integration
            result = client.run_model(
                model_name=model,
                prompt=prompt,
                save_output=False
            )
            refactored_code = result.response
            tokens_used = result.tokens_used

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "original_code": code,
            "refactored_code": refactored_code,
            "refactoring_type": refactoring_type,
            "language": language,
            "provider": provider,
            "model": model,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "metadata": {
                "context": context,
                "preserve_functionality": preserve_functionality,
            },
        }

        logger.info(
            f"Refactored {language} code using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except (ValueError, ImportError, AttributeError) as e:
        logger.error(f"Error refactoring code: {e}")
        raise RuntimeError(f"Code refactoring failed: {e}") from None
    except Exception as e:
        # Final fallback for unexpected API errors or network issues
        logger.error(f"Unexpected error refactoring code: {e}", exc_info=True)
        raise RuntimeError(f"Code refactoring failed: {e}") from None

