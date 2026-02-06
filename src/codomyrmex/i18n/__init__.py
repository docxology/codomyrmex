"""
Internationalization (i18n) Module

Translation, localization, and message bundle management.
"""

__version__ = "0.1.0"

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections.abc import Callable


@dataclass
class Locale:
    """A locale specification."""
    language: str  # ISO 639-1 (e.g., "en", "es")
    region: str = ""  # ISO 3166-1 (e.g., "US", "MX")

    @property
    def code(self) -> str:
        if self.region:
            return f"{self.language}_{self.region}"
        return self.language

    @classmethod
    def from_string(cls, code: str) -> "Locale":
        parts = code.replace("-", "_").split("_")
        language = parts[0].lower()
        region = parts[1].upper() if len(parts) > 1 else ""
        return cls(language=language, region=region)

    def __str__(self) -> str:
        return self.code


class MessageBundle:
    """A collection of translated messages."""

    def __init__(self, locale: Locale):
        self.locale = locale
        self._messages: dict[str, str] = {}

    def add(self, key: str, message: str) -> None:
        self._messages[key] = message

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._messages.get(key, default)

    def has(self, key: str) -> bool:
        return key in self._messages

    def keys(self) -> list[str]:
        return list(self._messages.keys())

    def to_dict(self) -> dict[str, str]:
        return self._messages.copy()

    @classmethod
    def from_dict(cls, locale: Locale, data: dict[str, str]) -> "MessageBundle":
        bundle = cls(locale)
        bundle._messages = data
        return bundle

    @classmethod
    def from_json_file(cls, locale: Locale, path: str) -> "MessageBundle":
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(locale, data)


class Translator:
    """Multi-locale translator."""

    def __init__(self, default_locale: Locale | None = None):
        self.default_locale = default_locale or Locale("en")
        self._bundles: dict[str, MessageBundle] = {}
        self._current_locale = self.default_locale
        self._interpolation_pattern = re.compile(r'\{(\w+)\}')

    def add_bundle(self, bundle: MessageBundle) -> None:
        self._bundles[bundle.locale.code] = bundle

    def set_locale(self, locale: Locale) -> None:
        self._current_locale = locale

    def get_locale(self) -> Locale:
        return self._current_locale

    def t(
        self,
        key: str,
        locale: Locale | None = None,
        **kwargs,
    ) -> str:
        """
        Translate a key.

        Args:
            key: Message key
            locale: Override locale
            **kwargs: Interpolation values

        Returns:
            Translated and interpolated message
        """
        loc = locale or self._current_locale

        # Try exact locale
        bundle = self._bundles.get(loc.code)
        if bundle and bundle.has(key):
            return self._interpolate(bundle.get(key), kwargs)

        # Try language only
        bundle = self._bundles.get(loc.language)
        if bundle and bundle.has(key):
            return self._interpolate(bundle.get(key), kwargs)

        # Fall back to default
        bundle = self._bundles.get(self.default_locale.code)
        if bundle and bundle.has(key):
            return self._interpolate(bundle.get(key), kwargs)

        # Return key as fallback
        return key

    def _interpolate(self, message: str, values: dict[str, Any]) -> str:
        def replacer(match):
            key = match.group(1)
            return str(values.get(key, match.group(0)))
        return self._interpolation_pattern.sub(replacer, message)

    def load_directory(self, path: str) -> int:
        """Load all JSON bundles from directory."""
        count = 0
        dir_path = Path(path)
        for file in dir_path.glob("*.json"):
            locale_code = file.stem
            locale = Locale.from_string(locale_code)
            bundle = MessageBundle.from_json_file(locale, str(file))
            self.add_bundle(bundle)
            count += 1
        return count


class PluralRules:
    """Pluralization rules for different locales."""

    RULES = {
        "en": lambda n: "one" if n == 1 else "other",
        "es": lambda n: "one" if n == 1 else "other",
        "ru": lambda n: "one" if n % 10 == 1 and n % 100 != 11 else (
            "few" if 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20) else "other"
        ),
        "ar": lambda n: "zero" if n == 0 else (
            "one" if n == 1 else ("two" if n == 2 else "other")
        ),
    }

    @classmethod
    def get_rule(cls, locale: Locale) -> Callable[[int], str]:
        return cls.RULES.get(locale.language, cls.RULES["en"])

    @classmethod
    def pluralize(cls, locale: Locale, count: int, forms: dict[str, str]) -> str:
        rule = cls.get_rule(locale)
        category = rule(count)
        return forms.get(category, forms.get("other", ""))


class NumberFormatter:
    """Format numbers for different locales."""

    FORMATS = {
        "en": {"decimal": ".", "thousands": ","},
        "de": {"decimal": ",", "thousands": "."},
        "fr": {"decimal": ",", "thousands": " "},
    }

    @classmethod
    def format(
        cls,
        locale: Locale,
        number: float,
        decimals: int = 2,
    ) -> str:
        fmt = cls.FORMATS.get(locale.language, cls.FORMATS["en"])

        if decimals == 0:
            int_part = str(int(round(number)))
            dec_part = ""
        else:
            parts = f"{number:.{decimals}f}".split(".")
            int_part = parts[0]
            dec_part = fmt["decimal"] + parts[1]

        # Add thousands separators
        result = ""
        for i, digit in enumerate(reversed(int_part)):
            if i > 0 and i % 3 == 0:
                result = fmt["thousands"] + result
            result = digit + result

        return result + dec_part


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
    "init",
    "t",
]
