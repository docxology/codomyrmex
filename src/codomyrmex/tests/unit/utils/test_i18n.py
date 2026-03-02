"""
Unit tests for utils.i18n — Zero-Mock compliant.

Covers: Locale (code/from_string/__str__), MessageBundle
(add/get/has/keys/to_dict/from_dict), Translator (add_bundle/set_locale/
get_locale/t/fallback/_interpolate), PluralRules (get_rule/pluralize),
NumberFormatter (format), DateFormatter (format_date/format_time/
format_datetime/relative_time).
"""

from datetime import date, datetime, timedelta

import pytest

from codomyrmex.utils.i18n import DateFormatter, NumberFormatter, PluralRules
from codomyrmex.utils.i18n.models import Locale
from codomyrmex.utils.i18n.translator import MessageBundle, Translator

# ── Locale ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLocale:
    def test_code_no_region(self):
        loc = Locale(language="en")
        assert loc.code == "en"

    def test_code_with_region(self):
        loc = Locale(language="en", region="US")
        assert loc.code == "en_US"

    def test_str_no_region(self):
        loc = Locale(language="fr")
        assert str(loc) == "fr"

    def test_str_with_region(self):
        loc = Locale(language="pt", region="BR")
        assert str(loc) == "pt_BR"

    def test_from_string_language_only(self):
        loc = Locale.from_string("en")
        assert loc.language == "en"
        assert loc.region == ""

    def test_from_string_underscore(self):
        loc = Locale.from_string("en_US")
        assert loc.language == "en"
        assert loc.region == "US"

    def test_from_string_hyphen(self):
        loc = Locale.from_string("fr-FR")
        assert loc.language == "fr"
        assert loc.region == "FR"

    def test_from_string_lowercases_language(self):
        loc = Locale.from_string("EN_US")
        assert loc.language == "en"

    def test_from_string_uppercases_region(self):
        loc = Locale.from_string("en_us")
        assert loc.region == "US"

    def test_from_string_three_part(self):
        # e.g. zh_hans_cn — take first two
        loc = Locale.from_string("zh_hans")
        assert loc.language == "zh"
        assert loc.region == "HANS"

    def test_region_empty_string_default(self):
        loc = Locale(language="de")
        assert loc.region == ""


# ── MessageBundle ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestMessageBundle:
    def _bundle(self):
        return MessageBundle(Locale("en"))

    def test_add_and_get(self):
        b = self._bundle()
        b.add("greeting", "Hello")
        assert b.get("greeting") == "Hello"

    def test_get_missing_returns_none(self):
        b = self._bundle()
        assert b.get("missing") is None

    def test_get_missing_returns_default(self):
        b = self._bundle()
        assert b.get("missing", "fallback") == "fallback"

    def test_has_true(self):
        b = self._bundle()
        b.add("key", "val")
        assert b.has("key") is True

    def test_has_false(self):
        b = self._bundle()
        assert b.has("nope") is False

    def test_keys_empty(self):
        b = self._bundle()
        assert b.keys() == []

    def test_keys_populated(self):
        b = self._bundle()
        b.add("a", "1")
        b.add("b", "2")
        keys = b.keys()
        assert "a" in keys
        assert "b" in keys
        assert len(keys) == 2

    def test_to_dict_copy(self):
        b = self._bundle()
        b.add("x", "y")
        d = b.to_dict()
        d["extra"] = "nope"
        assert "extra" not in b._messages

    def test_from_dict(self):
        locale = Locale("es")
        b = MessageBundle.from_dict(locale, {"hello": "Hola"})
        assert b.get("hello") == "Hola"
        assert b.locale.language == "es"

    def test_locale_stored(self):
        loc = Locale("de", "DE")
        b = MessageBundle(loc)
        assert b.locale.code == "de_DE"


# ── Translator ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTranslator:
    def _make_translator_with_en(self):
        t = Translator(Locale("en"))
        bundle = MessageBundle.from_dict(Locale("en"), {
            "greeting": "Hello",
            "farewell": "Goodbye",
            "item_count": "You have {count} items",
        })
        t.add_bundle(bundle)
        return t

    def test_translate_known_key(self):
        t = self._make_translator_with_en()
        assert t.t("greeting") == "Hello"

    def test_translate_missing_key_returns_key(self):
        t = self._make_translator_with_en()
        assert t.t("no_such_key") == "no_such_key"

    def test_translate_with_interpolation(self):
        t = self._make_translator_with_en()
        result = t.t("item_count", count=5)
        assert result == "You have 5 items"

    def test_set_locale_changes_current(self):
        t = self._make_translator_with_en()
        new_locale = Locale("fr")
        t.set_locale(new_locale)
        assert t.get_locale().language == "fr"

    def test_get_locale_default(self):
        t = Translator(Locale("en"))
        assert t.get_locale().language == "en"

    def test_fallback_to_language_code(self):
        t = Translator(Locale("en"))
        # Add bundle for "en" (no region)
        en_bundle = MessageBundle.from_dict(Locale("en"), {"key": "value"})
        t.add_bundle(en_bundle)
        # Set locale to "en_US" — exact match fails, falls back to "en"
        t.set_locale(Locale("en", "US"))
        assert t.t("key") == "value"

    def test_fallback_to_default_locale(self):
        t = Translator(Locale("en"))
        en_bundle = MessageBundle.from_dict(Locale("en"), {"hello": "Hi"})
        t.add_bundle(en_bundle)
        # Switch to French (no French bundle)
        t.set_locale(Locale("fr"))
        # Falls back to default locale (English)
        assert t.t("hello") == "Hi"

    def test_interpolation_unknown_placeholder_preserved(self):
        t = Translator(Locale("en"))
        bundle = MessageBundle.from_dict(Locale("en"), {"msg": "Hello {name}!"})
        t.add_bundle(bundle)
        result = t.t("msg")  # no name kwarg
        # Unresolved placeholder remains as-is
        assert "{name}" in result

    def test_interpolation_multiple_values(self):
        t = Translator(Locale("en"))
        bundle = MessageBundle.from_dict(Locale("en"), {"msg": "{a} and {b}"})
        t.add_bundle(bundle)
        assert t.t("msg", a="X", b="Y") == "X and Y"

    def test_add_bundle_multiple_locales(self):
        t = Translator(Locale("en"))
        en = MessageBundle.from_dict(Locale("en"), {"hi": "Hello"})
        es = MessageBundle.from_dict(Locale("es"), {"hi": "Hola"})
        t.add_bundle(en)
        t.add_bundle(es)
        t.set_locale(Locale("es"))
        assert t.t("hi") == "Hola"


# ── PluralRules ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPluralRules:
    def test_english_one(self):
        en = Locale("en")
        rule = PluralRules.get_rule(en)
        assert rule(1) == "one"

    def test_english_other(self):
        en = Locale("en")
        rule = PluralRules.get_rule(en)
        assert rule(0) == "other"
        assert rule(2) == "other"
        assert rule(100) == "other"

    def test_russian_one(self):
        ru = Locale("ru")
        rule = PluralRules.get_rule(ru)
        assert rule(1) == "one"
        assert rule(21) == "one"

    def test_russian_few(self):
        ru = Locale("ru")
        rule = PluralRules.get_rule(ru)
        assert rule(2) == "few"
        assert rule(3) == "few"
        assert rule(4) == "few"
        assert rule(22) == "few"

    def test_russian_other(self):
        ru = Locale("ru")
        rule = PluralRules.get_rule(ru)
        assert rule(5) == "other"
        assert rule(11) == "other"
        assert rule(15) == "other"

    def test_arabic_zero(self):
        ar = Locale("ar")
        rule = PluralRules.get_rule(ar)
        assert rule(0) == "zero"

    def test_arabic_one(self):
        ar = Locale("ar")
        rule = PluralRules.get_rule(ar)
        assert rule(1) == "one"

    def test_arabic_two(self):
        ar = Locale("ar")
        rule = PluralRules.get_rule(ar)
        assert rule(2) == "two"

    def test_arabic_other(self):
        ar = Locale("ar")
        rule = PluralRules.get_rule(ar)
        assert rule(5) == "other"

    def test_unknown_locale_falls_back_to_english(self):
        unknown = Locale("xx")
        rule = PluralRules.get_rule(unknown)
        assert rule(1) == "one"
        assert rule(2) == "other"

    def test_pluralize_en_singular(self):
        en = Locale("en")
        result = PluralRules.pluralize(en, 1, {"one": "cat", "other": "cats"})
        assert result == "cat"

    def test_pluralize_en_plural(self):
        en = Locale("en")
        result = PluralRules.pluralize(en, 5, {"one": "cat", "other": "cats"})
        assert result == "cats"

    def test_pluralize_falls_back_to_other(self):
        en = Locale("en")
        # Only "other" form provided
        result = PluralRules.pluralize(en, 1, {"other": "things"})
        # "one" not in forms, falls back to "other"
        assert result == "things"


# ── NumberFormatter ────────────────────────────────────────────────────


@pytest.mark.unit
class TestNumberFormatter:
    def test_english_no_decimals(self):
        en = Locale("en")
        assert NumberFormatter.format(en, 1234, decimals=0) == "1,234"

    def test_english_with_decimals(self):
        en = Locale("en")
        result = NumberFormatter.format(en, 1234.56, decimals=2)
        assert result == "1,234.56"

    def test_german_decimal_comma(self):
        de = Locale("de")
        result = NumberFormatter.format(de, 1234.5, decimals=1)
        assert "," in result  # decimal separator is comma

    def test_german_thousands_dot(self):
        de = Locale("de")
        result = NumberFormatter.format(de, 1234567.0, decimals=0)
        assert "." in result  # thousands separator is dot

    def test_french_thousands_space(self):
        fr = Locale("fr")
        result = NumberFormatter.format(fr, 1234567.0, decimals=0)
        assert " " in result  # thousands separator is space

    def test_unknown_locale_uses_english(self):
        unk = Locale("xx")
        result = NumberFormatter.format(unk, 1000.0, decimals=0)
        assert result == "1,000"

    def test_small_number_no_thousands(self):
        en = Locale("en")
        result = NumberFormatter.format(en, 999, decimals=0)
        assert result == "999"
        assert "," not in result

    def test_zero_decimals_rounds(self):
        en = Locale("en")
        result = NumberFormatter.format(en, 2.9, decimals=0)
        assert result == "3"

    def test_negative_number(self):
        en = Locale("en")
        result = NumberFormatter.format(en, -1234.5, decimals=1)
        assert "-" in result


# ── DateFormatter ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestDateFormatter:
    def test_format_date_en(self):
        en = Locale("en")
        d = date(2024, 3, 15)
        result = DateFormatter.format_date(en, d)
        assert result == "03/15/2024"

    def test_format_date_de(self):
        de = Locale("de")
        d = date(2024, 3, 15)
        result = DateFormatter.format_date(de, d)
        assert result == "15.03.2024"

    def test_format_date_fr(self):
        fr = Locale("fr")
        d = date(2024, 3, 15)
        result = DateFormatter.format_date(fr, d)
        assert result == "15/03/2024"

    def test_format_date_ja(self):
        ja = Locale("ja")
        d = date(2024, 3, 15)
        result = DateFormatter.format_date(ja, d)
        assert result == "2024/03/15"

    def test_format_date_unknown_uses_en(self):
        unk = Locale("xx")
        d = date(2024, 1, 5)
        result = DateFormatter.format_date(unk, d)
        # Falls back to en format MM/DD/YYYY
        assert result == "01/05/2024"

    def test_format_time_en_am(self):
        en = Locale("en")
        dt = datetime(2024, 3, 15, 9, 30, 0)
        result = DateFormatter.format_time(en, dt)
        assert "9:30" in result
        assert "AM" in result

    def test_format_time_de_24h(self):
        de = Locale("de")
        dt = datetime(2024, 3, 15, 14, 30, 0)
        result = DateFormatter.format_time(de, dt)
        assert result == "14:30"

    def test_format_datetime_en(self):
        en = Locale("en")
        dt = datetime(2024, 3, 15, 9, 30, 0)
        result = DateFormatter.format_datetime(en, dt)
        assert "03/15/2024" in result

    def test_relative_time_just_now(self):
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(seconds=30)
        assert DateFormatter.relative_time(past, now=now) == "just now"

    def test_relative_time_one_minute(self):
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(seconds=90)
        result = DateFormatter.relative_time(past, now=now)
        assert "1 minute ago" == result

    def test_relative_time_plural_minutes(self):
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(minutes=5)
        assert DateFormatter.relative_time(past, now=now) == "5 minutes ago"

    def test_relative_time_one_hour(self):
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=1)
        assert DateFormatter.relative_time(past, now=now) == "1 hour ago"

    def test_relative_time_plural_hours(self):
        now = datetime(2024, 1, 1, 12, 0, 0)
        past = now - timedelta(hours=3)
        assert DateFormatter.relative_time(past, now=now) == "3 hours ago"

    def test_relative_time_yesterday(self):
        now = datetime(2024, 1, 2, 12, 0, 0)
        past = now - timedelta(hours=24)
        assert DateFormatter.relative_time(past, now=now) == "yesterday"

    def test_relative_time_days_ago(self):
        now = datetime(2024, 1, 10, 12, 0, 0)
        past = now - timedelta(days=5)
        assert DateFormatter.relative_time(past, now=now) == "5 days ago"

    def test_relative_time_uses_now_when_not_provided(self):
        # Passing a recent time — should return "just now" or similar without error
        past = datetime.now() - timedelta(seconds=10)
        result = DateFormatter.relative_time(past)
        assert isinstance(result, str)
        assert len(result) > 0
