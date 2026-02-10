"""
Internationalization (i18n) Module

Translation, localization, and message bundle management.
"""

__version__ = "0.1.0"

from .models import Locale
from .translator import MessageBundle, Translator
from .formatters import NumberFormatter, PluralRules
from .date_formatter import DateFormatter

# Convenience
_default_translator: Translator | None = None


def init(default_locale: str = "en") -> Translator:
    global _default_translator
    _default_translator = Translator(Locale.from_string(default_locale))
    return _default_translator


def t(key: str, **kwargs) -> str:
    if _default_translator is None:
        init()
    return _default_translator.t(key, **kwargs)


__all__ = [
    "Locale",
    "MessageBundle",
    "Translator",
    "PluralRules",
    "NumberFormatter",
    "DateFormatter",
    "init",
    "t",
]
