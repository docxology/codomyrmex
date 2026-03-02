"""Locale-aware formatting utilities."""

from collections.abc import Callable

from .models import Locale


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
        """pluralize ."""
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
        """Format the value for output."""
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
