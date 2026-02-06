"""Tests for i18n module."""

import pytest

try:
    from codomyrmex.i18n import (
        Locale,
        MessageBundle,
        NumberFormatter,
        PluralRules,
        Translator,
        init,
        t,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("i18n module not available", allow_module_level=True)


@pytest.mark.unit
class TestLocale:
    def test_create_locale(self):
        locale = Locale(language="en")
        assert locale.language == "en"
        assert locale.region == ""

    def test_locale_with_region(self):
        locale = Locale(language="en", region="US")
        assert locale.region == "US"

    def test_from_string(self):
        locale = Locale.from_string("en-US")
        assert locale.language == "en"

    def test_from_string_language_only(self):
        locale = Locale.from_string("fr")
        assert locale.language == "fr"


@pytest.mark.unit
class TestMessageBundle:
    def test_create_bundle(self):
        locale = Locale(language="en")
        bundle = MessageBundle(locale=locale)
        assert bundle is not None


@pytest.mark.unit
class TestTranslator:
    def test_create_translator(self):
        translator = Translator()
        assert translator is not None

    def test_create_with_default_locale(self):
        locale = Locale(language="fr")
        translator = Translator(default_locale=locale)
        assert translator is not None


@pytest.mark.unit
class TestPluralRules:
    def test_class_exists(self):
        assert PluralRules is not None


@pytest.mark.unit
class TestNumberFormatter:
    def test_class_exists(self):
        assert NumberFormatter is not None


@pytest.mark.unit
class TestInit:
    def test_init_returns_translator(self):
        translator = init()
        assert isinstance(translator, Translator)

    def test_init_with_locale(self):
        translator = init(default_locale="fr")
        assert translator is not None


@pytest.mark.unit
class TestTranslateFunction:
    def test_t_returns_string(self):
        init()
        result = t("hello")
        assert isinstance(result, str)
