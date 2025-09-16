"""
Core implementation of AI code editing functionality.

This module contains functions for generating and refactoring code using LLMs.
"""

import os
import sys
import json
import time
import random
from typing import Dict, Any, Optional, Tuple, Union

# Add project root to Python path to allow sibling module imports if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import logger setup
try:
    from logging_monitoring import setup_logging, get_logger
except ImportError:
    # Fallback if logging module isn't available
    import logging
    def get_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

# Get module logger
logger = get_logger(__name__)

# Import performance monitoring
try:
    from performance import monitor_performance, performance_context
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False
    # Create no-op decorators
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class performance_context:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

# Import environment setup utilities if available
try:
    from environment_setup.env_checker import check_and_setup_env_vars
except ImportError:
    logger.warning("Could not import from environment_setup.env_checker. Environment variables may need to be set manually.")
    check_and_setup_env_vars = None

# Default LLM configurations
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_LLM_MODEL = {
    "openai": "gpt-3.5-turbo",
    "anthropic": "claude-instant-1",
    "google": "gemini-pro"
}

# Retry configuration for API calls
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds

# LLM client initialization
@monitor_performance("llm_client_initialization")
def get_llm_client(provider: str, model_name: Optional[str] = None) -> Tuple[Any, str]:
    """
    Initialize and return an LLM client based on the specified provider.
    
    Args:
        provider: The LLM provider to use (e.g., "openai", "anthropic")
        model_name: Optional specific model to use
        
    Returns:
        Tuple of (client, model_name)
        
    Raises:
        ImportError: If the required client library is not installed
        ValueError: If the provider is not supported or configuration is invalid
    """
    provider = provider.lower()
    
    if provider == "openai":
        try:
            from openai import OpenAI
            # Check for API key
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            client = OpenAI(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["openai"]
            return client, model
            
        except ImportError:
            raise ImportError("OpenAI Python package not installed. Install with: pip install openai")
    
    elif provider == "anthropic":
        try:
            from anthropic import Anthropic
            # Check for API key
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
            client = Anthropic(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["anthropic"]
            return client, model
            
        except ImportError:
            raise ImportError("Anthropic Python package not installed. Install with: pip install anthropic")
    
    elif provider == "google":
        try:
            import google.generativeai as genai
            # Check for API key
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            
            genai.configure(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["google"]
            return genai, model
            
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai")
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: openai, anthropic, google")

@monitor_performance("ai_code_generation")
def generate_code_snippet(
    prompt: str,
    language: str,
    context_code: Optional[str] = None,
    llm_provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate code snippet based on natural language prompt and optional context code.
    
    Args:
        prompt: Natural language description of the code to be generated
        language: Target programming language for the generated code
        context_code: Optional existing code snippet or broader context to guide generation
        llm_provider: LLM provider to use (e.g., "openai", "anthropic")
        model_name: Specific model to use (provider-dependent)
        
    Returns:
        Dictionary containing generation status and results
    """
    logger.info(f"Generating code snippet in {language}")
    
    try:
        # Validate inputs
        if not prompt or not language:
            return {
                "status": "failure",
                "generated_code": None,
                "error_message": "Required parameters 'prompt' or 'language' missing"
            }
        
        # Get LLM client
        try:
            client, model = get_llm_client(llm_provider, model_name)
        except (ImportError, ValueError) as e:
            return {
                "status": "failure",
                "generated_code": None,
                "error_message": f"LLM client initialization failed: {str(e)}"
            }
        
        # Construct prompt
        system_message = f"You are an expert {language} programmer. Generate clean, efficient, and well-documented code based on the user's requirements."
        
        if context_code:
            full_prompt = f"Generate {language} code for the following task:\n\n{prompt}\n\nUse the following context as a guide:\n```{language}\n{context_code}\n```\n\nRespond with ONLY the code and nothing else."
        else:
            full_prompt = f"Generate {language} code for the following task:\n\n{prompt}\n\nRespond with ONLY the code and nothing else."
        
        # Handle different providers with retry logic
        generated_code = None
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                if llm_provider == "openai":
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.2,  # Lower temperature for more deterministic code generation
                    )
                    generated_code = response.choices[0].message.content.strip()
                    
                elif llm_provider == "anthropic":
                    response = client.messages.create(
                        model=model,
                        system=system_message,
                        messages=[{"role": "user", "content": full_prompt}],
                        max_tokens=2000,
                        temperature=0.2,
                    )
                    generated_code = response.content[0].text.strip()
                
                elif llm_provider == "google":
                    # Configure generation parameters
                    generation_config = {
                        "temperature": 0.2,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2000,
                    }
                    
                    # Create the model
                    model_instance = client.GenerativeModel(model, generation_config=generation_config)
                    
                    # Create the prompt
                    google_prompt = f"{system_message}\n\n{full_prompt}"
                    
                    # Generate content
                    response = model_instance.generate_content(google_prompt)
                    generated_code = response.text.strip()
                
                else:
                    return {
                        "status": "failure",
                        "generated_code": None, 
                        "error_message": f"Unsupported LLM provider: {llm_provider}"
                    }
                
                # If we get here, the request was successful
                break
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff with jitter
                    delay = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed")
        
        # Check if we got a successful response
        if generated_code is None:
            return {
                "status": "failure",
                "generated_code": None,
                "error_message": f"Failed to generate code after {MAX_RETRIES} attempts. Last error: {str(last_error)}"
            }
        
        # Clean up the response to extract just code
        if "```" in generated_code:
            # Extract code from markdown code blocks if present
            code_blocks = []
            lines = generated_code.split("\n")
            in_code_block = False
            current_block = []
            
            for line in lines:
                if line.startswith("```"):
                    if in_code_block:
                        code_blocks.append("\n".join(current_block))
                        current_block = []
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    current_block.append(line)
            
            if code_blocks:
                generated_code = code_blocks[0]  # Take the first code block
        
        return {
            "status": "success",
            "generated_code": generated_code,
            "error_message": None
        }
    
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        return {
            "status": "failure",
            "generated_code": None,
            "error_message": f"Code generation failed: {str(e)}"
        }

@monitor_performance("ai_code_refactoring")
def refactor_code_snippet(
    code_snippet: str,
    refactoring_instruction: str,
    language: str,
    llm_provider: str = DEFAULT_LLM_PROVIDER,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Refactor code snippet based on provided instruction.
    
    Args:
        code_snippet: Existing code to be refactored
        refactoring_instruction: Natural language instruction for refactoring
        language: Programming language of the code snippet
        llm_provider: LLM provider to use (e.g., "openai", "anthropic")
        model_name: Specific model to use (provider-dependent)
        
    Returns:
        Dictionary containing refactoring status and results
    """
    logger.info(f"Refactoring {language} code snippet")
    
    try:
        # Validate inputs
        if not code_snippet or not refactoring_instruction or not language:
            return {
                "status": "failure",
                "refactored_code": None,
                "explanation": None,
                "error_message": "Required parameters missing"
            }
        
        # Get LLM client
        try:
            client, model = get_llm_client(llm_provider, model_name)
        except (ImportError, ValueError) as e:
            return {
                "status": "failure",
                "refactored_code": None,
                "explanation": None,
                "error_message": f"LLM client initialization failed: {str(e)}"
            }
        
        # Construct prompt
        system_message = f"You are an expert {language} programmer specializing in code refactoring. Given a code snippet and refactoring instruction, improve the code while preserving its functionality."
        
        full_prompt = f"Refactor the following {language} code according to this instruction: {refactoring_instruction}\n\n```{language}\n{code_snippet}\n```\n\nRespond with the refactored code followed by a brief explanation of changes made. If no changes are needed, explain why."
        
        # Handle different providers with retry logic
        full_response = None
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                if llm_provider == "openai":
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.2,
                    )
                    full_response = response.choices[0].message.content.strip()
                    
                elif llm_provider == "anthropic":
                    response = client.messages.create(
                        model=model,
                        system=system_message,
                        messages=[{"role": "user", "content": full_prompt}],
                        max_tokens=2000,
                        temperature=0.2,
                    )
                    full_response = response.content[0].text.strip()
                
                elif llm_provider == "google":
                    # Configure generation parameters
                    generation_config = {
                        "temperature": 0.2,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2000,
                    }
                    
                    # Create the model
                    model_instance = client.GenerativeModel(model, generation_config=generation_config)
                    
                    # Create the prompt
                    google_prompt = f"{system_message}\n\n{full_prompt}"
                    
                    # Generate content
                    response = model_instance.generate_content(google_prompt)
                    full_response = response.text.strip()
                
                else:
                    return {
                        "status": "failure",
                        "refactored_code": None,
                        "explanation": None,
                        "error_message": f"Unsupported LLM provider: {llm_provider}"
                    }
                
                # If we get here, the request was successful
                break
                
            except Exception as e:
                last_error = e
                logger.warning(f"Refactoring attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff with jitter
                    delay = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {MAX_RETRIES} refactoring attempts failed")
        
        # Check if we got a successful response
        if full_response is None:
            return {
                "status": "failure",
                "refactored_code": None,
                "explanation": None,
                "error_message": f"Failed to refactor code after {MAX_RETRIES} attempts. Last error: {str(last_error)}"
            }
        
        # Parse the response to extract refactored code and explanation
        refactored_code = ""
        explanation = ""
        
        # Check for markdown code blocks
        if "```" in full_response:
            # Extract code from first markdown code block
            parts = full_response.split("```")
            if len(parts) >= 3:  # At least one complete code block
                # The code block content should be in the second part (index 1), skipping the language identifier
                code_lines = parts[1].split("\n")
                if len(code_lines) > 0 and not code_lines[0].strip().startswith(language):
                    refactored_code = parts[1]
                else:
                    refactored_code = "\n".join(code_lines[1:])
                
                # Explanation is likely after the code block
                explanation = parts[2].strip()
            else:
                # Fallback if parsing fails
                refactored_code = full_response
        else:
            # No code blocks, use the entire response as code (less likely)
            refactored_code = full_response
        
        # Determine status
        if refactored_code.strip() == code_snippet.strip():
            status = "no_change_needed"
        else:
            status = "success"
        
        return {
            "status": status,
            "refactored_code": refactored_code,
            "explanation": explanation,
            "error_message": None
        }
    
    except Exception as e:
        logger.error(f"Error refactoring code: {str(e)}")
        return {
            "status": "failure",
            "refactored_code": None,
            "explanation": None,
            "error_message": f"Code refactoring failed: {str(e)}"
        }

# Test functions if this module is run directly
if __name__ == "__main__":
    # Set up logging for standalone testing
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Example code generation
    result = generate_code_snippet(
        prompt="Create a function to find the maximum value in a list of numbers",
        language="python",
    )
    print("\nGENERATED CODE:")
    print(json.dumps(result, indent=2))
    
    # Example refactoring
    if result["status"] == "success":
        refactor_result = refactor_code_snippet(
            code_snippet=result["generated_code"],
            refactoring_instruction="Add type hints and improve error handling",
            language="python",
        )
        print("\nREFACTORED CODE:")
        print(json.dumps(refactor_result, indent=2)) 