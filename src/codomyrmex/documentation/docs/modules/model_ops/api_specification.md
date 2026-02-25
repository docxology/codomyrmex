# Model Operations - API Specification

## Introduction

The Model Operations module provides tools for managing machine learning model lifecycles, including dataset preparation, fine-tuning jobs, and model evaluation.

## Endpoints / Functions / Interfaces

### Class: `Dataset`

- **Description**: Represents a dataset for training or evaluation.
- **Constructor**:
    - `name` (str): Dataset name.
    - `data` (list | pd.DataFrame, optional): Initial data.
    - `path` (str, optional): Path to data file.
- **Methods**:

#### `load(path: str) -> Dataset`

- **Description**: Load dataset from a file.
- **Parameters/Arguments**:
    - `path` (str): Path to data file (JSON, CSV, JSONL).
- **Returns**:
    - `Dataset`: Loaded dataset.

#### `save(path: str) -> None`

- **Description**: Save dataset to a file.
- **Parameters/Arguments**:
    - `path` (str): Output file path.

#### `split(train_ratio: float = 0.8) -> tuple[Dataset, Dataset]`

- **Description**: Split dataset into train and validation sets.
- **Parameters/Arguments**:
    - `train_ratio` (float): Ratio for training set. Default: 0.8.
- **Returns**:
    - `tuple[Dataset, Dataset]`: Train and validation datasets.

#### `sample(n: int) -> Dataset`

- **Description**: Sample n rows from the dataset.
- **Parameters/Arguments**:
    - `n` (int): Number of samples.
- **Returns**:
    - `Dataset`: Sampled dataset.

### Class: `DatasetSanitizer`

- **Description**: Sanitizes datasets for training.
- **Methods**:

#### `sanitize(dataset: Dataset) -> Dataset`

- **Description**: Remove problematic entries from dataset.
- **Parameters/Arguments**:
    - `dataset` (Dataset): Dataset to sanitize.
- **Returns**:
    - `Dataset`: Sanitized dataset.

#### `validate(dataset: Dataset) -> ValidationResult`

- **Description**: Validate dataset format and content.
- **Parameters/Arguments**:
    - `dataset` (Dataset): Dataset to validate.
- **Returns**:
    - `ValidationResult`: Validation results.

### Class: `FineTuningJob`

- **Description**: Manages a fine-tuning job.
- **Constructor**:
    - `model` (str): Base model to fine-tune.
    - `dataset` (Dataset): Training dataset.
    - `hyperparameters` (dict, optional): Training hyperparameters.
- **Methods**:

#### `start() -> str`

- **Description**: Start the fine-tuning job.
- **Returns**:
    - `str`: Job ID.

#### `get_status() -> JobStatus`

- **Description**: Get current job status.
- **Returns**:
    - `JobStatus`: Current status.

#### `cancel() -> bool`

- **Description**: Cancel the running job.
- **Returns**:
    - `bool`: True if cancellation was successful.

#### `get_metrics() -> dict`

- **Description**: Get training metrics.
- **Returns**:
    - `dict`: Training metrics (loss, accuracy, etc.).

#### `get_model() -> str`

- **Description**: Get the fine-tuned model identifier.
- **Returns**:
    - `str`: Model identifier.

### Class: `Evaluator`

- **Description**: Evaluates model performance.
- **Constructor**:
    - `metrics` (list[str], optional): Metrics to compute. Default: ["accuracy"].
- **Methods**:

#### `evaluate(model: str, dataset: Dataset) -> EvaluationResult`

- **Description**: Evaluate a model on a dataset.
- **Parameters/Arguments**:
    - `model` (str): Model identifier.
    - `dataset` (Dataset): Evaluation dataset.
- **Returns**:
    - `EvaluationResult`: Evaluation results.

#### `compare(models: list[str], dataset: Dataset) -> ComparisonResult`

- **Description**: Compare multiple models on a dataset.
- **Parameters/Arguments**:
    - `models` (list[str]): Model identifiers.
    - `dataset` (Dataset): Evaluation dataset.
- **Returns**:
    - `ComparisonResult`: Comparison results.

## Data Models

### Model: `ValidationResult`
- `valid` (bool): Whether dataset is valid.
- `errors` (list[str]): List of errors.
- `warnings` (list[str]): List of warnings.
- `stats` (dict): Dataset statistics.

### Model: `JobStatus`
- `job_id` (str): Job identifier.
- `status` (str): Status (pending, running, completed, failed, cancelled).
- `progress` (float): Progress percentage (0-100).
- `created_at` (datetime): Creation timestamp.
- `updated_at` (datetime): Last update timestamp.
- `error` (str | None): Error message if failed.

### Model: `EvaluationResult`
- `model` (str): Model identifier.
- `metrics` (dict): Computed metrics.
- `samples_evaluated` (int): Number of samples.
- `duration` (float): Evaluation duration in seconds.

### Model: `ComparisonResult`
- `models` (list[str]): Compared models.
- `results` (dict[str, EvaluationResult]): Results per model.
- `best_model` (str): Best performing model.
- `ranking` (list[str]): Models ranked by performance.

## Authentication & Authorization

Fine-tuning and evaluation may require API keys for model providers. Configure credentials via environment variables.

## Rate Limiting

Fine-tuning jobs may be subject to rate limits from underlying model providers.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
