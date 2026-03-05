"""Synthetic data generation for ML training datasets."""

import random
import string
from dataclasses import dataclass


@dataclass
class DataSchema:
    """Schema for generating synthetic data."""

    fields: (
        dict  # {field_name: {"type": "str|int|float|bool|choice", "options": [...]}}
    )
    n_samples: int = 100


class TemplateGenerator:
    """Template-based text generation with variable substitution."""

    def __init__(self, templates: list[str], variables: dict[str, list]):
        self.templates = templates
        self.variables = variables

    def generate(self, n: int = 10, seed: int | None = None) -> list[str]:
        """Generate n samples by filling templates with random variables."""
        if seed is not None:
            random.seed(seed)

        samples = []
        for _ in range(n):
            template = random.choice(self.templates)
            for var_name, options in self.variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in template:
                    template = template.replace(placeholder, random.choice(options))
            samples.append(template)
        return samples


class SyntheticDataGenerator:
    """
    Generate synthetic datasets for ML training.

    Supports:
    - Structured data (tabular) with type-aware field generation
    - Text templates with variable substitution
    - Classification datasets with configurable label balance
    """

    ADJECTIVES = ["quick", "slow", "bright", "dark", "happy", "sad", "large", "small"]
    NOUNS = ["cat", "dog", "car", "house", "tree", "book", "phone", "computer"]
    VERBS = ["runs", "jumps", "sleeps", "reads", "writes", "plays", "builds", "finds"]

    def generate_structured(
        self, schema: DataSchema, seed: int | None = None
    ) -> list[dict]:
        """Generate n_samples structured records matching the schema."""
        if seed is not None:
            random.seed(seed)

        records = []
        for _ in range(schema.n_samples):
            record = {}
            for field_name, spec in schema.fields.items():
                field_type = spec.get("type", "str")

                if field_type == "str":
                    length = spec.get("length", 8)
                    record[field_name] = "".join(
                        random.choices(string.ascii_lowercase, k=length)
                    )

                elif field_type == "int":
                    lo = spec.get("min", 0)
                    hi = spec.get("max", 100)
                    record[field_name] = random.randint(lo, hi)

                elif field_type == "float":
                    lo = spec.get("min", 0.0)
                    hi = spec.get("max", 1.0)
                    record[field_name] = random.uniform(lo, hi)

                elif field_type == "bool":
                    record[field_name] = random.choice([True, False])

                elif field_type == "choice":
                    options = spec.get("options", ["a", "b", "c"])
                    record[field_name] = random.choice(options)

                elif field_type == "text":
                    n_words = spec.get("n_words", 5)
                    words = (
                        [random.choice(self.ADJECTIVES)]
                        + [random.choice(self.NOUNS)]
                        + [random.choice(self.VERBS)]
                        + [
                            random.choice(self.ADJECTIVES)
                            for _ in range(max(0, n_words - 3))
                        ]
                    )[:n_words]
                    record[field_name] = " ".join(words)

            records.append(record)
        return records

    def generate_classification(
        self,
        n_samples: int,
        n_classes: int = 2,
        n_features: int = 10,
        class_balance: str = "balanced",
        seed: int | None = None,
    ) -> tuple[list[list[float]], list[int]]:
        """
        Generate a synthetic classification dataset.

        Each class has a random centroid; samples are noisy points around centroids.

        Args:
            n_samples: Total samples
            n_classes: Number of classes
            n_features: Feature vector dimension
            class_balance: "balanced" or "imbalanced"
            seed: Random seed

        Returns:
            (features, labels): Both lists
        """
        import numpy as np

        if seed is not None:
            np.random.seed(seed)

        centroids = np.random.randn(n_classes, n_features) * 2.0

        if class_balance == "balanced":
            samples_per_class = [n_samples // n_classes] * n_classes
            samples_per_class[-1] += n_samples - sum(samples_per_class)
        else:
            weights = np.exp(-np.arange(n_classes))
            weights /= weights.sum()
            samples_per_class = [max(1, int(w * n_samples)) for w in weights]
            samples_per_class[-1] = max(1, n_samples - sum(samples_per_class[:-1]))

        features, labels = [], []
        for cls_idx, n_cls in enumerate(samples_per_class):
            noise = np.random.randn(n_cls, n_features) * 0.5
            cls_features = centroids[cls_idx] + noise
            features.extend(cls_features.tolist())
            labels.extend([cls_idx] * n_cls)

        return features, labels

    def generate_preference_pairs(
        self,
        n_pairs: int = 100,
        templates: list[str] | None = None,
        seed: int | None = None,
    ) -> list[dict]:
        """Generate preference pairs for RLHF/DPO training."""
        if seed is not None:
            random.seed(seed)

        if templates is None:
            templates = [
                "The answer to {question} is {answer}",
                "I believe {answer} is correct for {question}",
                "{answer}",
            ]

        questions = [
            f"What is {random.choice(self.ADJECTIVES)} about {random.choice(self.NOUNS)}?"
            for _ in range(n_pairs)
        ]

        pairs = []
        for q in questions:
            winner = random.choice(self.NOUNS) + " " + random.choice(self.VERBS)
            loser = random.choice(self.ADJECTIVES)
            pairs.append(
                {
                    "prompt": q,
                    "chosen": winner,
                    "rejected": loser,
                    "quality_score_chosen": random.uniform(0.7, 1.0),
                    "quality_score_rejected": random.uniform(0.0, 0.4),
                }
            )
        return pairs
