"""Tests for i18n module."""

import pytest
from datetime import datetime, date, timedelta

try:
    from codomyrmex.i18n import (
        Locale,
        MessageBundle,
        NumberFormatter,
        PluralRules,
        Translator,
        DateFormatter,
        init,
        t,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("i18n module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Locale
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLocale:
    # --- original 4 tests ---
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

    # --- new behavioral tests ---
    def test_code_language_only(self):
        """Locale.code with language only returns 'en'."""
        locale = Locale(language="en")
        assert locale.code == "en"

    def test_code_with_region(self):
        """Locale.code with region returns 'en_US'."""
        locale = Locale(language="en", region="US")
        assert locale.code == "en_US"

    def test_from_string_dash_separator(self):
        """from_string parses 'en-US' correctly."""
        locale = Locale.from_string("en-US")
        assert locale.language == "en"
        assert locale.region == "US"
        assert locale.code == "en_US"

    def test_from_string_underscore_separator(self):
        """from_string parses 'en_US' correctly."""
        locale = Locale.from_string("en_US")
        assert locale.language == "en"
        assert locale.region == "US"
        assert locale.code == "en_US"

    def test_from_string_normalizes_case(self):
        """from_string lowercases language and uppercases region."""
        locale = Locale.from_string("EN-us")
        assert locale.language == "en"
        assert locale.region == "US"

    def test_str_returns_code(self):
        """__str__ returns code."""
        locale = Locale(language="en", region="US")
        assert str(locale) == "en_US"

    def test_str_language_only(self):
        """__str__ with language only returns language code."""
        locale = Locale(language="fr")
        assert str(locale) == "fr"


# ---------------------------------------------------------------------------
# MessageBundle
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMessageBundle:
    # --- original 1 test ---
    def test_create_bundle(self):
        locale = Locale(language="en")
        bundle = MessageBundle(locale=locale)
        assert bundle is not None

    # --- new behavioral tests ---
    def test_add_and_get(self):
        """add() stores a message, get() retrieves it."""
        bundle = MessageBundle(Locale("en"))
        bundle.add("greeting", "Hello")
        assert bundle.get("greeting") == "Hello"

    def test_get_missing_returns_none(self):
        """get() returns None for missing key when no default."""
        bundle = MessageBundle(Locale("en"))
        assert bundle.get("missing") is None

    def test_get_missing_returns_default(self):
        """get() returns explicit default for missing key."""
        bundle = MessageBundle(Locale("en"))
        assert bundle.get("missing", "fallback") == "fallback"

    def test_has_true(self):
        """has() returns True for existing key."""
        bundle = MessageBundle(Locale("en"))
        bundle.add("key", "val")
        assert bundle.has("key") is True

    def test_has_false(self):
        """has() returns False for missing key."""
        bundle = MessageBundle(Locale("en"))
        assert bundle.has("nope") is False

    def test_keys(self):
        """keys() returns list of all message keys."""
        bundle = MessageBundle(Locale("en"))
        bundle.add("a", "1")
        bundle.add("b", "2")
        assert sorted(bundle.keys()) == ["a", "b"]

    def test_to_dict(self):
        """to_dict() returns copy of all messages."""
        bundle = MessageBundle(Locale("en"))
        bundle.add("x", "y")
        d = bundle.to_dict()
        assert d == {"x": "y"}
        # Verify it is a copy
        d["x"] = "changed"
        assert bundle.get("x") == "y"

    def test_from_dict(self):
        """from_dict() creates populated bundle."""
        locale = Locale("es")
        data = {"hello": "hola", "bye": "adios"}
        bundle = MessageBundle.from_dict(locale, data)
        assert bundle.locale.language == "es"
        assert bundle.get("hello") == "hola"
        assert bundle.get("bye") == "adios"
        assert len(bundle.keys()) == 2


# ---------------------------------------------------------------------------
# Translator
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTranslator:
    # --- original 2 tests ---
    def test_create_translator(self):
        translator = Translator()
        assert translator is not None

    def test_create_with_default_locale(self):
        locale = Locale(language="fr")
        translator = Translator(default_locale=locale)
        assert translator is not None

    # --- new behavioral tests ---
    def test_t_returns_translation(self):
        """t() returns translated message for current locale."""
        tr = Translator(Locale("en"))
        bundle = MessageBundle.from_dict(Locale("en"), {"hi": "Hello"})
        tr.add_bundle(bundle)
        assert tr.t("hi") == "Hello"

    def test_t_fallback_to_default_locale(self):
        """t() falls back to default locale when current locale has no translation."""
        tr = Translator(Locale("en"))
        en = MessageBundle.from_dict(Locale("en"), {"msg": "English"})
        tr.add_bundle(en)
        tr.set_locale(Locale("fr"))
        assert tr.t("msg") == "English"

    def test_t_returns_key_when_not_found(self):
        """t() returns the key itself when no translation exists anywhere."""
        tr = Translator(Locale("en"))
        assert tr.t("nonexistent.key") == "nonexistent.key"

    def test_t_interpolation(self):
        """t() replaces {name} placeholders with kwargs."""
        tr = Translator(Locale("en"))
        bundle = MessageBundle.from_dict(Locale("en"), {"greet": "Hello, {name}!"})
        tr.add_bundle(bundle)
        assert tr.t("greet", name="World") == "Hello, World!"

    def test_t_interpolation_multiple_vars(self):
        """t() replaces multiple placeholders."""
        tr = Translator(Locale("en"))
        bundle = MessageBundle.from_dict(
            Locale("en"),
            {"msg": "{count} items for {user}"},
        )
        tr.add_bundle(bundle)
        assert tr.t("msg", count="5", user="Alice") == "5 items for Alice"

    def test_t_interpolation_missing_var_preserved(self):
        """t() preserves {placeholder} when no matching kwarg."""
        tr = Translator(Locale("en"))
        bundle = MessageBundle.from_dict(Locale("en"), {"msg": "Hi {name}"})
        tr.add_bundle(bundle)
        assert tr.t("msg") == "Hi {name}"

    def test_set_locale_changes_language(self):
        """set_locale() changes the current locale used by t()."""
        tr = Translator(Locale("en"))
        en = MessageBundle.from_dict(Locale("en"), {"hello": "Hello"})
        es = MessageBundle.from_dict(Locale("es"), {"hello": "Hola"})
        tr.add_bundle(en)
        tr.add_bundle(es)
        assert tr.t("hello") == "Hello"
        tr.set_locale(Locale("es"))
        assert tr.t("hello") == "Hola"

    def test_get_locale(self):
        """get_locale() returns the current locale."""
        tr = Translator(Locale("en"))
        assert tr.get_locale().language == "en"
        tr.set_locale(Locale("de"))
        assert tr.get_locale().language == "de"

    def test_t_with_locale_override(self):
        """t() accepts a locale parameter that overrides current locale."""
        tr = Translator(Locale("en"))
        en = MessageBundle.from_dict(Locale("en"), {"hello": "Hello"})
        es = MessageBundle.from_dict(Locale("es"), {"hello": "Hola"})
        tr.add_bundle(en)
        tr.add_bundle(es)
        # Current locale is en, but override with es
        assert tr.t("hello", locale=Locale("es")) == "Hola"

    def test_t_language_fallback_from_regional(self):
        """t() falls back from regional locale (en_US) to language-only (en) bundle."""
        tr = Translator(Locale("en"))
        en = MessageBundle.from_dict(Locale("en"), {"msg": "English base"})
        tr.add_bundle(en)
        tr.set_locale(Locale.from_string("en-US"))
        assert tr.t("msg") == "English base"


# ---------------------------------------------------------------------------
# PluralRules
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPluralRules:
    # --- original 1 test ---
    def test_class_exists(self):
        assert PluralRules is not None

    # --- new behavioral tests ---
    def test_english_one(self):
        """English: count=1 selects 'one'."""
        forms = {"one": "1 apple", "other": "{n} apples"}
        result = PluralRules.pluralize(Locale("en"), 1, forms)
        assert result == "1 apple"

    def test_english_other(self):
        """English: count=5 selects 'other'."""
        forms = {"one": "1 apple", "other": "many apples"}
        result = PluralRules.pluralize(Locale("en"), 5, forms)
        assert result == "many apples"

    def test_english_zero_is_other(self):
        """English: count=0 selects 'other'."""
        forms = {"one": "1 item", "other": "no items"}
        assert PluralRules.pluralize(Locale("en"), 0, forms) == "no items"

    def test_russian_one(self):
        """Russian: 1 = 'one'."""
        forms = {"one": "one-form", "few": "few-form", "other": "other-form"}
        assert PluralRules.pluralize(Locale("ru"), 1, forms) == "one-form"

    def test_russian_few(self):
        """Russian: 2-4 = 'few'."""
        forms = {"one": "one-form", "few": "few-form", "other": "other-form"}
        assert PluralRules.pluralize(Locale("ru"), 2, forms) == "few-form"
        assert PluralRules.pluralize(Locale("ru"), 3, forms) == "few-form"
        assert PluralRules.pluralize(Locale("ru"), 4, forms) == "few-form"

    def test_russian_other(self):
        """Russian: 5-20 = 'other'."""
        forms = {"one": "one-form", "few": "few-form", "other": "other-form"}
        for n in [5, 11, 12, 13, 14, 20]:
            assert PluralRules.pluralize(Locale("ru"), n, forms) == "other-form"

    def test_russian_21_is_one(self):
        """Russian: 21 = 'one' (n%10==1 and n%100!=11)."""
        forms = {"one": "one-form", "few": "few-form", "other": "other-form"}
        assert PluralRules.pluralize(Locale("ru"), 21, forms) == "one-form"

    def test_russian_22_is_few(self):
        """Russian: 22 = 'few'."""
        forms = {"one": "one-form", "few": "few-form", "other": "other-form"}
        assert PluralRules.pluralize(Locale("ru"), 22, forms) == "few-form"

    def test_unknown_locale_uses_english_rule(self):
        """Unknown locale falls back to English plural rules."""
        forms = {"one": "singular", "other": "plural"}
        assert PluralRules.pluralize(Locale("xx"), 1, forms) == "singular"
        assert PluralRules.pluralize(Locale("xx"), 2, forms) == "plural"


# ---------------------------------------------------------------------------
# NumberFormatter
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestNumberFormatter:
    # --- original 1 test ---
    def test_class_exists(self):
        assert NumberFormatter is not None

    # --- new behavioral tests ---
    def test_english_format(self):
        """English: 1234.56 -> '1,234.56'."""
        result = NumberFormatter.format(Locale("en"), 1234.56)
        assert result == "1,234.56"

    def test_german_format(self):
        """German: 1234.56 -> '1.234,56'."""
        result = NumberFormatter.format(Locale("de"), 1234.56)
        assert result == "1.234,56"

    def test_french_format(self):
        """French: 1234.56 -> '1 234,56'."""
        result = NumberFormatter.format(Locale("fr"), 1234.56)
        assert result == "1 234,56"

    def test_zero_decimals(self):
        """decimals=0 returns integer only, no decimal point."""
        result = NumberFormatter.format(Locale("en"), 1234.56, decimals=0)
        assert result == "1,235"

    def test_small_number(self):
        """Number below 1000 has no thousands separator."""
        result = NumberFormatter.format(Locale("en"), 42.5)
        assert result == "42.50"

    def test_large_number(self):
        """Large number gets multiple thousands separators."""
        result = NumberFormatter.format(Locale("en"), 1234567.89)
        assert result == "1,234,567.89"

    def test_unknown_locale_uses_english(self):
        """Unknown locale falls back to English format."""
        result = NumberFormatter.format(Locale("xx"), 1000.5)
        assert result == "1,000.50"


# ---------------------------------------------------------------------------
# DateFormatter
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDateFormatter:
    def test_format_date_english(self):
        """English date: MM/DD/YYYY."""
        d = date(2025, 3, 15)
        assert DateFormatter.format_date(Locale("en"), d) == "03/15/2025"

    def test_format_date_german(self):
        """German date: DD.MM.YYYY."""
        d = date(2025, 3, 15)
        assert DateFormatter.format_date(Locale("de"), d) == "15.03.2025"

    def test_format_date_french(self):
        """French date: DD/MM/YYYY."""
        d = date(2025, 3, 15)
        assert DateFormatter.format_date(Locale("fr"), d) == "15/03/2025"

    def test_format_date_japanese(self):
        """Japanese date: YYYY/MM/DD."""
        d = date(2025, 3, 15)
        assert DateFormatter.format_date(Locale("ja"), d) == "2025/03/15"

    def test_format_date_spanish(self):
        """Spanish date: DD/MM/YYYY."""
        d = date(2025, 3, 15)
        assert DateFormatter.format_date(Locale("es"), d) == "15/03/2025"

    def test_format_date_unknown_locale_uses_english(self):
        """Unknown locale falls back to English date format."""
        d = date(2025, 3, 15)
        assert DateFormatter.format_date(Locale("xx"), d) == "03/15/2025"

    def test_format_time_english(self):
        """English time: 12-hour with AM/PM."""
        dt = datetime(2025, 3, 15, 14, 30)
        result = DateFormatter.format_time(Locale("en"), dt)
        assert result == "02:30 PM"

    def test_format_time_german(self):
        """German time: 24-hour."""
        dt = datetime(2025, 3, 15, 14, 30)
        assert DateFormatter.format_time(Locale("de"), dt) == "14:30"

    def test_format_datetime_english(self):
        """English datetime: MM/DD/YYYY HH:MM AM/PM."""
        dt = datetime(2025, 3, 15, 14, 30)
        result = DateFormatter.format_datetime(Locale("en"), dt)
        assert result == "03/15/2025 02:30 PM"

    def test_format_datetime_german(self):
        """German datetime: DD.MM.YYYY HH:MM."""
        dt = datetime(2025, 3, 15, 14, 30)
        result = DateFormatter.format_datetime(Locale("de"), dt)
        assert result == "15.03.2025 14:30"

    def test_relative_time_just_now(self):
        """Under 60 seconds -> 'just now'."""
        now = datetime(2025, 3, 15, 12, 0, 0)
        dt = datetime(2025, 3, 15, 11, 59, 30)
        assert DateFormatter.relative_time(dt, now) == "just now"

    def test_relative_time_one_minute(self):
        """Exactly 1 minute -> '1 minute ago' (singular)."""
        now = datetime(2025, 3, 15, 12, 1, 0)
        dt = datetime(2025, 3, 15, 12, 0, 0)
        assert DateFormatter.relative_time(dt, now) == "1 minute ago"

    def test_relative_time_multiple_minutes(self):
        """5 minutes -> '5 minutes ago' (plural)."""
        now = datetime(2025, 3, 15, 12, 5, 0)
        dt = datetime(2025, 3, 15, 12, 0, 0)
        assert DateFormatter.relative_time(dt, now) == "5 minutes ago"

    def test_relative_time_one_hour(self):
        """Exactly 1 hour -> '1 hour ago' (singular)."""
        now = datetime(2025, 3, 15, 13, 0, 0)
        dt = datetime(2025, 3, 15, 12, 0, 0)
        assert DateFormatter.relative_time(dt, now) == "1 hour ago"

    def test_relative_time_multiple_hours(self):
        """3 hours -> '3 hours ago' (plural)."""
        now = datetime(2025, 3, 15, 15, 0, 0)
        dt = datetime(2025, 3, 15, 12, 0, 0)
        assert DateFormatter.relative_time(dt, now) == "3 hours ago"

    def test_relative_time_yesterday(self):
        """24-47 hours -> 'yesterday'."""
        now = datetime(2025, 3, 15, 12, 0, 0)
        dt = datetime(2025, 3, 14, 12, 0, 0)
        assert DateFormatter.relative_time(dt, now) == "yesterday"

    def test_relative_time_days_ago(self):
        """3 days -> '3 days ago'."""
        now = datetime(2025, 3, 15, 12, 0, 0)
        dt = datetime(2025, 3, 12, 12, 0, 0)
        assert DateFormatter.relative_time(dt, now) == "3 days ago"


# ---------------------------------------------------------------------------
# Convenience functions: init() and t()
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestInit:
    # --- original 2 tests ---
    def test_init_returns_translator(self):
        translator = init()
        assert isinstance(translator, Translator)

    def test_init_with_locale(self):
        translator = init(default_locale="fr")
        assert translator is not None

    # --- new behavioral tests ---
    def test_init_sets_default_locale(self):
        """init('es') creates translator with Spanish default."""
        translator = init(default_locale="es")
        assert translator.get_locale().language == "es"


@pytest.mark.unit
class TestTranslateFunction:
    # --- original 1 test ---
    def test_t_returns_string(self):
        init()
        result = t("hello")
        assert isinstance(result, str)

    # --- new behavioral tests ---
    def test_global_t_returns_key_when_no_bundle(self):
        """Global t() returns the key when no bundles loaded."""
        init("en")
        assert t("some.missing.key") == "some.missing.key"

    def test_global_translator_works_end_to_end(self):
        """init() + add bundle + t() works as a full workflow."""
        import codomyrmex.i18n as i18n_mod
        tr = init("en")
        bundle = MessageBundle.from_dict(Locale("en"), {"welcome": "Welcome!"})
        tr.add_bundle(bundle)
        # The global _default_translator is the same object
        assert i18n_mod._default_translator is tr
        assert t("welcome") == "Welcome!"


# ---------------------------------------------------------------------------
# MessageBundle.from_json_file() tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMessageBundleFromJsonFile:
    """Tests for MessageBundle.from_json_file()."""

    def test_loads_valid_json_file(self, tmp_path):
        """Loads messages from a valid JSON file."""
        import json
        f = tmp_path / "en.json"
        f.write_text(json.dumps({"hello": "Hello", "bye": "Goodbye"}))
        bundle = MessageBundle.from_json_file(Locale("en"), str(f))
        assert bundle.get("hello") == "Hello"
        assert bundle.get("bye") == "Goodbye"
        assert bundle.locale.language == "en"

    def test_preserves_all_keys(self, tmp_path):
        """All keys from the JSON file are available."""
        import json
        data = {"k1": "v1", "k2": "v2", "k3": "v3"}
        f = tmp_path / "fr.json"
        f.write_text(json.dumps(data))
        bundle = MessageBundle.from_json_file(Locale("fr"), str(f))
        assert sorted(bundle.keys()) == ["k1", "k2", "k3"]

    def test_raises_on_missing_file(self):
        """Raises FileNotFoundError for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            MessageBundle.from_json_file(Locale("en"), "/nonexistent/path.json")

    def test_raises_on_invalid_json(self, tmp_path):
        """Raises JSONDecodeError for malformed JSON."""
        import json
        f = tmp_path / "bad.json"
        f.write_text("not valid json{{{")
        with pytest.raises(json.JSONDecodeError):
            MessageBundle.from_json_file(Locale("en"), str(f))


# ---------------------------------------------------------------------------
# Translator.load_directory() tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTranslatorLoadDirectory:
    """Tests for Translator.load_directory()."""

    def test_loads_all_json_files(self, tmp_path):
        """Loads all .json files from directory."""
        import json
        (tmp_path / "en.json").write_text(json.dumps({"hi": "Hello"}))
        (tmp_path / "es.json").write_text(json.dumps({"hi": "Hola"}))
        tr = Translator(Locale("en"))
        count = tr.load_directory(str(tmp_path))
        assert count == 2
        assert tr.t("hi") == "Hello"
        tr.set_locale(Locale("es"))
        assert tr.t("hi") == "Hola"

    def test_returns_count_of_loaded_bundles(self, tmp_path):
        """Returns the number of bundles loaded."""
        import json
        (tmp_path / "en.json").write_text(json.dumps({"a": "b"}))
        (tmp_path / "fr.json").write_text(json.dumps({"a": "c"}))
        (tmp_path / "de.json").write_text(json.dumps({"a": "d"}))
        tr = Translator(Locale("en"))
        assert tr.load_directory(str(tmp_path)) == 3

    def test_ignores_non_json_files(self, tmp_path):
        """Ignores .txt and other non-.json files."""
        import json
        (tmp_path / "en.json").write_text(json.dumps({"a": "b"}))
        (tmp_path / "readme.txt").write_text("not a bundle")
        (tmp_path / "data.csv").write_text("a,b,c")
        tr = Translator(Locale("en"))
        assert tr.load_directory(str(tmp_path)) == 1

    def test_empty_directory_returns_zero(self, tmp_path):
        """Returns 0 for an empty directory."""
        tr = Translator(Locale("en"))
        assert tr.load_directory(str(tmp_path)) == 0

    def test_file_stems_become_locale_codes(self, tmp_path):
        """File name (stem) is parsed as locale code."""
        import json
        (tmp_path / "en_US.json").write_text(json.dumps({"msg": "US English"}))
        tr = Translator(Locale("en"))
        tr.load_directory(str(tmp_path))
        result = tr.t("msg", locale=Locale.from_string("en-US"))
        assert result == "US English"
