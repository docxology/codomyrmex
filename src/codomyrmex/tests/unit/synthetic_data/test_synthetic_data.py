"""Tests for the synthetic_data module."""

import pytest

try:
    from codomyrmex.synthetic_data import SyntheticDataGenerator, DataSchema, TemplateGenerator
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if not HAS_MODULE:
    pytest.skip("synthetic_data module not available", allow_module_level=True)


@pytest.mark.unit
class TestDataSchema:
    """Test suite for DataSchema."""

    def test_create_schema(self):
        """DataSchema stores fields and n_samples."""
        schema = DataSchema(
            fields={"name": {"type": "str"}, "age": {"type": "int"}},
            n_samples=50,
        )
        assert schema.n_samples == 50
        assert "name" in schema.fields
        assert "age" in schema.fields

    def test_default_n_samples(self):
        """Default n_samples is 100."""
        schema = DataSchema(fields={"x": {"type": "int"}})
        assert schema.n_samples == 100


@pytest.mark.unit
class TestTemplateGenerator:
    """Test suite for TemplateGenerator."""

    def test_generate_fills_templates(self):
        """Templates are filled with random variable choices."""
        gen = TemplateGenerator(
            templates=["Hello {name}, you are {age}."],
            variables={"name": ["Alice", "Bob"], "age": ["25", "30"]},
        )
        results = gen.generate(n=5, seed=42)
        assert len(results) == 5
        for r in results:
            assert "Hello " in r
            assert "{name}" not in r
            assert "{age}" not in r

    def test_deterministic_with_seed(self):
        """Same seed produces identical output."""
        gen = TemplateGenerator(
            templates=["{x} and {y}"],
            variables={"x": ["a", "b", "c"], "y": ["1", "2", "3"]},
        )
        r1 = gen.generate(n=10, seed=123)
        r2 = gen.generate(n=10, seed=123)
        assert r1 == r2

    def test_multiple_templates(self):
        """Generator samples from multiple templates."""
        gen = TemplateGenerator(
            templates=["Template A: {x}", "Template B: {x}"],
            variables={"x": ["val"]},
        )
        results = gen.generate(n=20, seed=42)
        assert any("Template A" in r for r in results)
        assert any("Template B" in r for r in results)


@pytest.mark.unit
class TestSyntheticDataGeneratorStructured:
    """Test suite for structured data generation."""

    def test_generate_str_field(self):
        """String fields produce lowercase alphabetic strings."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(fields={"name": {"type": "str", "length": 5}}, n_samples=10)
        records = gen.generate_structured(schema, seed=42)
        assert len(records) == 10
        for r in records:
            assert len(r["name"]) == 5
            assert r["name"].isalpha()

    def test_generate_int_field(self):
        """Integer fields respect min/max bounds."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(
            fields={"age": {"type": "int", "min": 18, "max": 65}},
            n_samples=50,
        )
        records = gen.generate_structured(schema, seed=42)
        for r in records:
            assert 18 <= r["age"] <= 65

    def test_generate_float_field(self):
        """Float fields respect min/max bounds."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(
            fields={"score": {"type": "float", "min": 0.0, "max": 1.0}},
            n_samples=50,
        )
        records = gen.generate_structured(schema, seed=42)
        for r in records:
            assert 0.0 <= r["score"] <= 1.0

    def test_generate_bool_field(self):
        """Boolean fields produce True/False values."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(
            fields={"active": {"type": "bool"}},
            n_samples=50,
        )
        records = gen.generate_structured(schema, seed=42)
        values = {r["active"] for r in records}
        assert values.issubset({True, False})

    def test_generate_choice_field(self):
        """Choice fields only pick from given options."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(
            fields={"color": {"type": "choice", "options": ["red", "green", "blue"]}},
            n_samples=50,
        )
        records = gen.generate_structured(schema, seed=42)
        for r in records:
            assert r["color"] in ["red", "green", "blue"]

    def test_generate_text_field(self):
        """Text fields produce multi-word strings."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(
            fields={"description": {"type": "text", "n_words": 4}},
            n_samples=10,
        )
        records = gen.generate_structured(schema, seed=42)
        for r in records:
            words = r["description"].split()
            assert len(words) == 4

    def test_deterministic_with_seed(self):
        """Same seed produces identical structured output."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(fields={"x": {"type": "int"}}, n_samples=20)
        r1 = gen.generate_structured(schema, seed=99)
        r2 = gen.generate_structured(schema, seed=99)
        assert r1 == r2

    def test_multiple_fields(self):
        """Schemas with multiple fields produce complete records."""
        gen = SyntheticDataGenerator()
        schema = DataSchema(
            fields={
                "name": {"type": "str", "length": 6},
                "age": {"type": "int", "min": 0, "max": 100},
                "active": {"type": "bool"},
            },
            n_samples=10,
        )
        records = gen.generate_structured(schema, seed=42)
        assert len(records) == 10
        for r in records:
            assert "name" in r
            assert "age" in r
            assert "active" in r


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestSyntheticDataGeneratorClassification:
    """Test suite for classification data generation."""

    def test_balanced_classification(self):
        """Balanced classification produces roughly equal class sizes."""
        gen = SyntheticDataGenerator()
        features, labels = gen.generate_classification(
            n_samples=100, n_classes=4, n_features=5, seed=42,
        )
        assert len(features) == len(labels)
        assert len(features) == 100

        from collections import Counter
        counts = Counter(labels)
        assert len(counts) == 4
        assert all(c == 25 for c in counts.values())

    def test_imbalanced_classification(self):
        """Imbalanced classification produces different class sizes."""
        gen = SyntheticDataGenerator()
        features, labels = gen.generate_classification(
            n_samples=100, n_classes=3, class_balance="imbalanced", seed=42,
        )
        from collections import Counter
        counts = Counter(labels)
        sizes = sorted(counts.values(), reverse=True)
        # First class should have more samples than last
        assert sizes[0] > sizes[-1]

    def test_feature_dimensionality(self):
        """Each feature vector has n_features dimensions."""
        gen = SyntheticDataGenerator()
        features, labels = gen.generate_classification(
            n_samples=50, n_features=7, seed=42,
        )
        for f in features:
            assert len(f) == 7

    def test_deterministic_with_seed(self):
        """Same seed produces identical classification data."""
        gen = SyntheticDataGenerator()
        f1, l1 = gen.generate_classification(n_samples=30, seed=123)
        f2, l2 = gen.generate_classification(n_samples=30, seed=123)
        assert f1 == f2
        assert l1 == l2

    def test_binary_classification(self):
        """Default 2-class produces labels in {0, 1}."""
        gen = SyntheticDataGenerator()
        features, labels = gen.generate_classification(n_samples=50, seed=42)
        assert set(labels).issubset({0, 1})


@pytest.mark.unit
class TestSyntheticDataGeneratorPreference:
    """Test suite for preference pair generation."""

    def test_generate_preference_pairs(self):
        """Preference pairs have required fields."""
        gen = SyntheticDataGenerator()
        pairs = gen.generate_preference_pairs(n_pairs=10, seed=42)
        assert len(pairs) == 10
        for p in pairs:
            assert "prompt" in p
            assert "chosen" in p
            assert "rejected" in p
            assert "quality_score_chosen" in p
            assert "quality_score_rejected" in p

    def test_quality_score_ranges(self):
        """Chosen scores > 0.7, rejected scores < 0.4."""
        gen = SyntheticDataGenerator()
        pairs = gen.generate_preference_pairs(n_pairs=50, seed=42)
        for p in pairs:
            assert 0.7 <= p["quality_score_chosen"] <= 1.0
            assert 0.0 <= p["quality_score_rejected"] <= 0.4

    def test_deterministic_with_seed(self):
        """Same seed produces identical pairs."""
        gen = SyntheticDataGenerator()
        p1 = gen.generate_preference_pairs(n_pairs=20, seed=77)
        p2 = gen.generate_preference_pairs(n_pairs=20, seed=77)
        assert p1 == p2


@pytest.mark.unit
class TestSyntheticDataMCPTools:
    """Test MCP tool wrappers for synthetic_data."""

    def test_synth_generate_structured(self):
        """MCP tool returns structured records."""
        from codomyrmex.synthetic_data.mcp_tools import synth_generate_structured
        result = synth_generate_structured(
            fields={"x": {"type": "int", "min": 0, "max": 10}},
            n_samples=5,
            seed=42,
        )
        assert result["status"] == "success"
        assert result["n_samples"] == 5

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
    def test_synth_generate_classification(self):
        """MCP tool returns classification data summary."""
        from codomyrmex.synthetic_data.mcp_tools import synth_generate_classification
        result = synth_generate_classification(
            n_samples=30, n_classes=3, seed=42,
        )
        assert result["status"] == "success"
        assert result["n_samples"] == 30

    def test_synth_generate_preference_pairs(self):
        """MCP tool returns preference pairs."""
        from codomyrmex.synthetic_data.mcp_tools import synth_generate_preference_pairs
        result = synth_generate_preference_pairs(n_pairs=5, seed=42)
        assert result["status"] == "success"
        assert result["n_pairs"] == 5
