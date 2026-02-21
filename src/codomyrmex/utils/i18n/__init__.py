"""
Internationalization (i18n) Module

Translation, localization, and message bundle management.
"""

__version__ = "0.1.0"

from .models import Locale
from .translator import MessageBundle, Translator
from .formatters import NumberFormatter, PluralRules
from .date_formatter import DateFormatter

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Convenience
_default_translator: Translator | None = None


def init(default_locale: str = "en") -> Translator:
    global _default_translator
    _default_translator = Translator(Locale.from_string(default_locale))
    return _default_translator


def t(key: str, **kwargs) -> str:
    global _default_translator
    if _default_translator is None:
        init()
    return _default_translator.t(key, **kwargs)


def cli_commands():
    """Return CLI commands for the i18n module."""

    def _locales():
        """List supported locales."""
        print("i18n Supported Locales")
        print(f"  Default: en")
        print(f"  Available formatters: NumberFormatter, DateFormatter")
        print(f"  Plural rules engine: PluralRules")

    def _translate(text: str = "", target: str = ""):
        """Translate text with --text and --target args."""
        if not text or not target:
            print("Usage: i18n translate --text <text> --target <locale>")
            return
        try:
            locale = Locale.from_string(target)
            translator = Translator(locale)
            result = translator.t(text)
            print(f"  Source: {text}")
            print(f"  Target locale: {target}")
            print(f"  Result: {result}")
        except Exception as e:
            print(f"Translation error: {e}")

    return {
        "locales": _locales,
        "translate": _translate,
    }


__all__ = [
    "Locale",
    "MessageBundle",
    "Translator",
    "PluralRules",
    "NumberFormatter",
    "DateFormatter",
    "init",
    "t",
    "cli_commands",
]
