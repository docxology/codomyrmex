"""AI Code Analysis Helpers."""

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

@monitor_performance("ai_code_analysis")
def analyze_code_quality(
    code: str,
    language: str,
    analysis_type: str = "comprehensive",
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: str | None = None,
    context: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Analyze code quality using an LLM.

    Args:
        code: The code to analyze
        language: Programming language of the code
        analysis_type: Type of analysis ("comprehensive", "security", "performance", "maintainability")
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for analysis
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing analysis results and suggestions

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If analysis fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt based on analysis type
        analysis_prompts = {
            "comprehensive": f"Analyze the following {language} code for overall quality, including readability, maintainability, performance, and best practices:",
            "security": f"Analyze the following {language} code for security vulnerabilities and potential issues:",
            "performance": f"Analyze the following {language} code for performance issues and optimization opportunities:",
            "maintainability": f"Analyze the following {language} code for maintainability, readability, and code organization:",
        }

        prompt = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])
        prompt += f"\n\n{code}"

        if context:
            prompt += f"\n\nAdditional context: {context}"

        prompt += "\n\nProvide specific suggestions for improvement with code examples where appropriate."

        # Generate analysis based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            analysis = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            analysis = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            analysis = response.text
            tokens_used = None

        elif provider == "ollama":
            # Use Ollama integration
            result = client.run_model(
                model_name=model,
                prompt=prompt,
                save_output=False
            )
            analysis = result.response
            tokens_used = result.tokens_used

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "code": code,
            "analysis": analysis,
            "analysis_type": analysis_type,
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
            f"Analyzed {language} code using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except (ValueError, ImportError, AttributeError) as e:
        logger.error(f"Error analyzing code: {e}")
        raise RuntimeError(f"Code analysis failed: {e}") from None
    except Exception as e:
        # Final fallback for unexpected API errors or network issues
        logger.error(f"Unexpected error analyzing code: {e}", exc_info=True)
        raise RuntimeError(f"Code analysis failed: {e}") from None

@monitor_performance("ai_code_comparison")
def compare_code_versions(
    code1: str,
    code2: str,
    language: str,
    provider: str = DEFAULT_LLM_PROVIDER,
    model_name: str | None = None,
    context: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Compare two versions of code and provide analysis.

    Args:
        code1: First version of code
        code2: Second version of code
        language: Programming language of the code
        provider: LLM provider to use
        model_name: Specific model to use (optional)
        context: Additional context for comparison
        **kwargs: Additional parameters for the LLM

    Returns:
        Dictionary containing comparison analysis

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If comparison fails
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not code1 or not code1.strip():
            raise ValueError("First code version cannot be empty")

        if not code2 or not code2.strip():
            raise ValueError("Second code version cannot be empty")

        # Get LLM client
        client, model = get_llm_client(provider, model_name)

        # Prepare the prompt
        prompt = f"""Compare the following two versions of {language} code and provide a detailed analysis:

VERSION 1:
{code1}

VERSION 2:
{code2}

Please analyze:
1. Functional differences
2. Performance implications
3. Code quality improvements/regressions
4. Maintainability changes
5. Best practices adherence
6. Overall recommendation

{context if context else ""}"""

        # Generate comparison based on provider
        if provider == "openai":
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            comparison = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

        elif provider == "anthropic":
            response = client.messages.create(
                model=model, messages=[{"role": "user", "content": prompt}], **kwargs
            )
            comparison = response.content[0].text
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                else None
            )

        elif provider == "google":
            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            comparison = response.text
            tokens_used = None

        elif provider == "ollama":
            # Use Ollama integration
            result = client.run_model(
                model_name=model,
                prompt=prompt,
                save_output=False
            )
            comparison = result.response
            tokens_used = result.tokens_used

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        execution_time = time.time() - start_time

        # Return result
        result = {
            "code1": code1,
            "code2": code2,
            "comparison": comparison,
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
            f"Compared {language} code versions using {provider}/{model} in {execution_time:.2f}s"
        )
        return result

    except (ValueError, ImportError, AttributeError) as e:
        logger.error(f"Error comparing code versions: {e}")
        raise RuntimeError(f"Code comparison failed: {e}") from None
    except Exception as e:
        # Final fallback for unexpected API errors or network issues
        logger.error(f"Unexpected error comparing code versions: {e}", exc_info=True)
        raise RuntimeError(f"Code comparison failed: {e}") from None

