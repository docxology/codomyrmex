"""Translation engine and message bundles."""

import json
import re
from pathlib import Path
from typing import Any

from .models import Locale


class MessageBundle:
    """A collection of translated messages."""

    def __init__(self, locale: Locale):
        """Execute   Init   operations natively."""
        self.locale = locale
        self._messages: dict[str, str] = {}

    def add(self, key: str, message: str) -> None:
        """Execute Add operations natively."""
        self._messages[key] = message

    def get(self, key: str, default: str | None = None) -> str | None:
        """Execute Get operations natively."""
        return self._messages.get(key, default)

    def has(self, key: str) -> bool:
        """Execute Has operations natively."""
        return key in self._messages

    def keys(self) -> list[str]:
        """Execute Keys operations natively."""
        return list(self._messages.keys())

    def to_dict(self) -> dict[str, str]:
        """Execute To Dict operations natively."""
        return self._messages.copy()

    @classmethod
    def from_dict(cls, locale: Locale, data: dict[str, str]) -> "MessageBundle":
        """Execute From Dict operations natively."""
        bundle = cls(locale)
        bundle._messages = data
        return bundle

    @classmethod
    def from_json_file(cls, locale: Locale, path: str) -> "MessageBundle":
        """Execute From Json File operations natively."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(locale, data)


class Translator:
    """Multi-locale translator."""

    def __init__(self, default_locale: Locale | None = None):
        """Execute   Init   operations natively."""
        self.default_locale = default_locale or Locale("en")
        self._bundles: dict[str, MessageBundle] = {}
        self._current_locale = self.default_locale
        self._interpolation_pattern = re.compile(r'\{(\w+)\}')

    def add_bundle(self, bundle: MessageBundle) -> None:
        """Execute Add Bundle operations natively."""
        self._bundles[bundle.locale.code] = bundle

    def set_locale(self, locale: Locale) -> None:
        """Execute Set Locale operations natively."""
        self._current_locale = locale

    def get_locale(self) -> Locale:
        """Execute Get Locale operations natively."""
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
        """Execute  Interpolate operations natively."""
        def replacer(match):
            """Execute Replacer operations natively."""
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
