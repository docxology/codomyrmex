"""Language detection module for the Codomyrmex platform."""

import langdetect


def detect_language(text: str) -> str:
    """Detect the language of the provided text.

    Args:
        text: The text to analyze.

    Returns:
        The detected ISO 639-1 language code (e.g. 'en', 'fr').
    """
    if not text or not text.strip():
        return "unknown"
    try:
        return langdetect.detect(text)
    except langdetect.lang_detect_exception.LangDetectException:
        return "unknown"


def detect_languages_with_probabilities(text: str) -> list[dict[str, float]]:
    """Detect multiple languages with probabilities for the provided text.

    Args:
        text: The text to analyze.

    Returns:
        A list of dictionaries, each with 'lang' and 'prob' keys.
    """
    if not text or not text.strip():
        return []
    try:
        results = langdetect.detect_langs(text)
        return [{"lang": r.lang, "prob": r.prob} for r in results]
    except langdetect.lang_detect_exception.LangDetectException:
        return []
