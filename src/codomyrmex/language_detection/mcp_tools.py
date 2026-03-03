"""MCP tools for the language detection module."""
from typing import Dict, Any, List
from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.language_detection import detect_language, detect_languages_with_probabilities

@mcp_tool(category="language_detection")
def language_detection_detect(text: str) -> Dict[str, Any]:
    """Detect the language of the provided text.

    Args:
        text: The string content whose language is to be detected.

    Returns:
        A dictionary containing status and the detected ISO 639-1 language code.
    """
    try:
        lang = detect_language(text)
        return {
            "status": "success",
            "language": lang
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp_tool(category="language_detection")
def language_detection_detect_probs(text: str) -> Dict[str, Any]:
    """Detect multiple languages with probabilities for the provided text.

    Args:
        text: The string content whose languages are to be detected.

    Returns:
        A dictionary containing status and a list of detected languages with their probabilities.
    """
    try:
        results = detect_languages_with_probabilities(text)
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
