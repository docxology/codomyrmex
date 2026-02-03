from pathlib import Path
from ..utils import get_logger

logger = get_logger(__name__)

def handle_ai_generate(prompt: str, language: str, provider: str) -> bool:
    """Handle AI code generation command."""
    try:
        from codomyrmex.agents.ai_code_editing import generate_code_snippet

        result = generate_code_snippet(
            prompt=prompt, language=language, provider=provider
        )

        if result["status"] == "success":
            print("Generated code:")
            print("-" * 40)
            print(result["generated_code"])
            print("-" * 40)
            return True
        else:
            print(f"❌ Code generation failed: {result['error_message']}")
            return False

    except ImportError:
        logger.warning("AI code editing module not available")
        print("❌ AI code editing module not available")
        return False
    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error(f"Error generating code: {e}", exc_info=True)
        print(f"❌ Error generating code: {str(e)}")
        return False


def handle_ai_refactor(file_path: str, instruction: str) -> bool:
    """Handle AI code refactoring command."""
    try:
        from codomyrmex.agents.ai_code_editing import refactor_code_snippet

        # Read the file
        try:
            with open(file_path) as f:
                code = f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return False

        # Determine language from file extension
        language = Path(file_path).suffix.lstrip(".")
        if language == "py":
            language = "python"
        elif language == "js":
            language = "javascript"

        result = refactor_code_snippet(
            code_snippet=code, refactoring_instruction=instruction, language=language
        )

        if result["status"] in ["success", "no_change_needed"]:
            print("Refactored code:")
            print("-" * 40)
            print(result["refactored_code"])
            print("-" * 40)
            if result.get("explanation"):
                print(f"Explanation: {result['explanation']}")
            return True
        else:
            print(f"❌ Refactoring failed: {result['error_message']}")
            return False

    except ImportError:
        logger.warning("AI code editing module not available")
        print("❌ AI code editing module not available")
        return False
    except (ValueError, TypeError, AttributeError, RuntimeError, OSError) as e:
        logger.error(f"Error refactoring code: {e}", exc_info=True)
        print(f"❌ Error refactoring code: {str(e)}")
        return False
