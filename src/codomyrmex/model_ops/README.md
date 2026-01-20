# model_ops

Machine Learning and LLM operations management module.

## Overview

This module provides tools for managing the lifecycle of machine learning models, specifically focusing on Large Language Models (LLMs). It covers fine-tuning orchestration, model evaluation, and dataset management.

## Key Features

- **Fine-tuning**: Standardized interface for triggering and monitoring fine-tuning jobs.
- **Evaluation**: Unified `Evaluator` for running benchmarks with metrics like Exact Match (EM).
- **Dataset Management**: `DatasetSanitizer` for stripping keys and filtering data by length.
- **Model Registry**: A central hub for tracking models and their metadata.

## Usage

```python
from codomyrmex.model_ops import FineTuningJob, Dataset

# Prepare dataset
dataset = Dataset.from_file("training_data.jsonl")
dataset.upload("my-bucket/datasets/")

# Start fine-tuning
job = FineTuningJob(base_model="gpt-3.5-turbo", dataset=dataset)
job.run()
print(job.status)
```

## Navigation Links

- [Functional Specification](SPEC.md)
- [Technical Documentation](AGENTS.md)
