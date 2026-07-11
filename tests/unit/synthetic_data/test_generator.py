"""Tests for synthetic_data.generator — DataSchema, TemplateGenerator,
SyntheticDataGenerator.

Zero-mock policy: real class instantiation + stdlib only.
Skip guard: generate_classification uses numpy — skipped if absent.
"""

import pytest

from codomyrmex.synthetic_data.generator import (
    DataSchema,
    SyntheticDataGenerator,
    TemplateGenerator,
)

numpy = pytest.importorskip  # importorskip called inline below where needed


# ──────────────────────────── DataSchema ───────────────────────────────────


class TestDataSchema:
    def test_basic_construction(self):
        schema = DataSchema(fields={"name": {"type": "str"}})
        assert schema.fields == {"name": {"type": "str"}}

    def test_default_n_samples(self):
        schema = DataSchema(fields={})
        assert schema.n_samples == 100

    def test_custom_n_samples(self):
        schema = DataSchema(fields={}, n_samples=50)
        assert schema.n_samples == 50

    def test_multiple_fields(self):
        schema = DataSchema(
            fields={
                "age": {"type": "int", "min": 0, "max": 120},
                "score": {"type": "float"},
                "label": {"type": "choice", "options": ["a", "b"]},
            }
        )
        assert len(schema.fields) == 3


# ──────────────────────────── TemplateGenerator ────────────────────────────


class TestTemplateGenerator:
    def _gen(self):
        return TemplateGenerator(
            templates=["Hello {name}!", "Goodbye {name}."],
            variables={"name": ["Alice", "Bob", "Carol"]},
        )

    def test_instantiation(self):
        gen = self._gen()
        assert gen is not None

    def test_templates_stored(self):
        gen = self._gen()
        assert len(gen.templates) == 2

    def test_variables_stored(self):
        gen = self._gen()
        assert "name" in gen.variables

    def test_generate_returns_list(self):
        gen = self._gen()
        result = gen.generate(n=5)
        assert isinstance(result, list)

    def test_generate_correct_length(self):
        gen = self._gen()
        result = gen.generate(n=7)
        assert len(result) == 7

    def test_seed_reproducibility(self):
        gen = self._gen()
        r1 = gen.generate(n=5, seed=42)
        r2 = gen.generate(n=5, seed=42)
        assert r1 == r2

    def test_different_seed_different_output(self):
        gen = self._gen()
        r1 = gen.generate(n=10, seed=1)
        r2 = gen.generate(n=10, seed=2)
        assert r1 != r2

    def test_placeholder_substituted(self):
        gen = self._gen()
        results = gen.generate(n=20, seed=42)
        for text in results:
            assert "{name}" not in text

    def test_substituted_value_from_options(self):
        gen = self._gen()
        results = gen.generate(n=20, seed=0)
        names = {"Alice", "Bob", "Carol"}
        for text in results:
            # text should contain one of the names
            assert any(name in text for name in names)

    def test_zero_n_returns_empty(self):
        gen = self._gen()
        assert gen.generate(n=0) == []

    def test_no_variables_templates_returned_as_is(self):
        gen = TemplateGenerator(templates=["static text"], variables={})
        results = gen.generate(n=3, seed=0)
        assert all(r == "static text" for r in results)


# ──────────────────────────── SyntheticDataGenerator ──────────────────────


class TestSyntheticDataGeneratorClassVars:
    def test_adjectives_is_list(self):
        assert isinstance(SyntheticDataGenerator.ADJECTIVES, list)

    def test_nouns_is_list(self):
        assert isinstance(SyntheticDataGenerator.NOUNS, list)

    def test_verbs_is_list(self):
        assert isinstance(SyntheticDataGenerator.VERBS, list)

    def test_adjectives_not_empty(self):
        assert len(SyntheticDataGenerator.ADJECTIVES) > 0

    def test_nouns_not_empty(self):
        assert len(SyntheticDataGenerator.NOUNS) > 0

    def test_verbs_not_empty(self):
        assert len(SyntheticDataGenerator.VERBS) > 0

    def test_adjectives_all_strings(self):
        assert all(isinstance(a, str) for a in SyntheticDataGenerator.ADJECTIVES)

    def test_nouns_all_strings(self):
        assert all(isinstance(n, str) for n in SyntheticDataGenerator.NOUNS)

    def test_verbs_all_strings(self):
        assert all(isinstance(v, str) for v in SyntheticDataGenerator.VERBS)


class TestGenerateStructured:
    def _gen(self):
        return SyntheticDataGenerator()

    def test_returns_list(self):
        schema = DataSchema(fields={"x": {"type": "str"}}, n_samples=5)
        result = self._gen().generate_structured(schema)
        assert isinstance(result, list)

    def test_correct_number_of_records(self):
        schema = DataSchema(fields={"x": {"type": "int"}}, n_samples=10)
        result = self._gen().generate_structured(schema)
        assert len(result) == 10

    def test_each_record_has_expected_keys(self):
        schema = DataSchema(
            fields={"name": {"type": "str"}, "age": {"type": "int"}}, n_samples=5
        )
        for record in self._gen().generate_structured(schema):
            assert "name" in record
            assert "age" in record

    def test_str_field_is_string(self):
        schema = DataSchema(fields={"s": {"type": "str"}}, n_samples=5)
        for record in self._gen().generate_structured(schema):
            assert isinstance(record["s"], str)

    def test_str_field_default_length_8(self):
        schema = DataSchema(fields={"s": {"type": "str"}}, n_samples=10)
        for record in self._gen().generate_structured(schema):
            assert len(record["s"]) == 8

    def test_str_field_custom_length(self):
        schema = DataSchema(fields={"s": {"type": "str", "length": 4}}, n_samples=5)
        for record in self._gen().generate_structured(schema):
            assert len(record["s"]) == 4

    def test_int_field_is_int(self):
        schema = DataSchema(fields={"n": {"type": "int"}}, n_samples=10)
        for record in self._gen().generate_structured(schema):
            assert isinstance(record["n"], int)

    def test_int_field_within_range(self):
        schema = DataSchema(
            fields={"n": {"type": "int", "min": 5, "max": 10}}, n_samples=20
        )
        for record in self._gen().generate_structured(schema):
            assert 5 <= record["n"] <= 10

    def test_float_field_is_float(self):
        schema = DataSchema(fields={"f": {"type": "float"}}, n_samples=5)
        for record in self._gen().generate_structured(schema):
            assert isinstance(record["f"], float)

    def test_float_field_within_default_range(self):
        schema = DataSchema(fields={"f": {"type": "float"}}, n_samples=20)
        for record in self._gen().generate_structured(schema):
            assert 0.0 <= record["f"] <= 1.0

    def test_bool_field_is_bool(self):
        schema = DataSchema(fields={"b": {"type": "bool"}}, n_samples=20)
        for record in self._gen().generate_structured(schema):
            assert isinstance(record["b"], bool)

    def test_choice_field_from_options(self):
        options = ["red", "green", "blue"]
        schema = DataSchema(
            fields={"color": {"type": "choice", "options": options}}, n_samples=20
        )
        for record in self._gen().generate_structured(schema):
            assert record["color"] in options

    def test_choice_default_options(self):
        schema = DataSchema(fields={"x": {"type": "choice"}}, n_samples=10)
        defaults = ["a", "b", "c"]
        for record in self._gen().generate_structured(schema):
            assert record["x"] in defaults

    def test_text_field_is_string(self):
        schema = DataSchema(fields={"t": {"type": "text"}}, n_samples=5)
        for record in self._gen().generate_structured(schema):
            assert isinstance(record["t"], str)

    def test_text_field_has_words(self):
        schema = DataSchema(fields={"t": {"type": "text", "n_words": 3}}, n_samples=10)
        for record in self._gen().generate_structured(schema):
            assert len(record["t"].split()) >= 1  # at least 1 word

    def test_seed_reproducibility(self):
        schema = DataSchema(fields={"x": {"type": "int"}}, n_samples=5)
        gen = self._gen()
        r1 = gen.generate_structured(schema, seed=42)
        r2 = gen.generate_structured(schema, seed=42)
        assert r1 == r2

    def test_zero_samples_returns_empty(self):
        schema = DataSchema(fields={"x": {"type": "str"}}, n_samples=0)
        result = self._gen().generate_structured(schema)
        assert result == []

    def test_empty_fields_each_record_empty_dict(self):
        schema = DataSchema(fields={}, n_samples=3)
        result = self._gen().generate_structured(schema)
        assert all(r == {} for r in result)


class TestGeneratePreferencePairs:
    def _gen(self):
        return SyntheticDataGenerator()

    def test_returns_list(self):
        result = self._gen().generate_preference_pairs(n_pairs=5)
        assert isinstance(result, list)

    def test_correct_count(self):
        result = self._gen().generate_preference_pairs(n_pairs=10)
        assert len(result) == 10

    def test_each_pair_has_required_keys(self):
        for pair in self._gen().generate_preference_pairs(n_pairs=5):
            assert "prompt" in pair
            assert "chosen" in pair
            assert "rejected" in pair
            assert "quality_score_chosen" in pair
            assert "quality_score_rejected" in pair

    def test_quality_score_chosen_in_range(self):
        for pair in self._gen().generate_preference_pairs(n_pairs=20, seed=0):
            assert 0.7 <= pair["quality_score_chosen"] <= 1.0

    def test_quality_score_rejected_in_range(self):
        for pair in self._gen().generate_preference_pairs(n_pairs=20, seed=0):
            assert 0.0 <= pair["quality_score_rejected"] <= 0.4

    def test_seed_reproducibility(self):
        gen = self._gen()
        r1 = gen.generate_preference_pairs(n_pairs=5, seed=99)
        r2 = gen.generate_preference_pairs(n_pairs=5, seed=99)
        assert r1 == r2

    def test_prompt_is_string(self):
        for pair in self._gen().generate_preference_pairs(n_pairs=5):
            assert isinstance(pair["prompt"], str)

    def test_zero_pairs_returns_empty(self):
        result = self._gen().generate_preference_pairs(n_pairs=0)
        assert result == []

    def test_custom_templates_accepted(self):
        gen = self._gen()
        templates = ["Answer: {answer}"]
        result = gen.generate_preference_pairs(n_pairs=5, templates=templates)
        assert isinstance(result, list)
        assert len(result) == 5


# ──────────────────────────── generate_classification (numpy) ─────────────


class TestGenerateClassification:
    @pytest.fixture(autouse=True)
    def require_numpy(self):
        pytest.importorskip("numpy")

    def _gen(self):
        return SyntheticDataGenerator()

    def test_returns_tuple_of_two(self):
        features, labels = self._gen().generate_classification(n_samples=20)
        assert isinstance(features, list)
        assert isinstance(labels, list)

    def test_feature_count_matches_n_samples_balanced(self):
        features, labels = self._gen().generate_classification(
            n_samples=20, n_classes=2, class_balance="balanced"
        )
        assert len(features) == 20
        assert len(labels) == 20

    def test_feature_vectors_have_correct_dimension(self):
        features, _ = self._gen().generate_classification(n_samples=10, n_features=5)
        for fv in features:
            assert len(fv) == 5

    def test_labels_are_ints(self):
        _, labels = self._gen().generate_classification(n_samples=10, n_classes=3)
        for lbl in labels:
            assert isinstance(lbl, int)

    def test_labels_in_valid_range(self):
        n_classes = 4
        _, labels = self._gen().generate_classification(
            n_samples=40, n_classes=n_classes
        )
        for lbl in labels:
            assert 0 <= lbl < n_classes

    def test_seed_reproducibility(self):
        gen = self._gen()
        f1, l1 = gen.generate_classification(n_samples=10, seed=42)
        f2, l2 = gen.generate_classification(n_samples=10, seed=42)
        assert f1 == f2
        assert l1 == l2

    def test_imbalanced_produces_correct_total(self):
        features, labels = self._gen().generate_classification(
            n_samples=20, n_classes=3, class_balance="imbalanced"
        )
        assert len(labels) == 20
        assert len(features) == 20

    def test_all_classes_represented_balanced(self):
        _, labels = self._gen().generate_classification(
            n_samples=60, n_classes=3, class_balance="balanced", seed=0
        )
        assert set(labels) == {0, 1, 2}
