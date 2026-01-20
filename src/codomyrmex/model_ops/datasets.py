"""Dataset management utilities."""

import json
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class Dataset:
    """Represents a collection of training/eval data."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    @classmethod
    def from_file(cls, file_path: str):
        """Load dataset from a JSONL file."""
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        return cls(data)

    def to_jsonl(self, file_path: str):
        """Save dataset to a JSONL file."""
        with open(file_path, 'w') as f:
            for item in self.data:
                f.write(json.dumps(item) + '\n')
        logger.info(f"Dataset saved to {file_path}")

    def validate(self) -> bool:
        """Basic validation for LLM datasets."""
        for i, item in enumerate(self.data):
            if "messages" not in item and "prompt" not in item:
                logger.error(f"Invalid format at index {i}: missing 'messages' or 'prompt'")
                return False
        return True

class DatasetSanitizer:
    """Utilities for sanitizing datasets (removing PII, etc.)."""
    
    @staticmethod
    def strip_keys(dataset: Dataset, keys_to_remove: List[str]) -> Dataset:
        """Remove specific keys from all items in the dataset."""
        new_data = []
        for item in dataset.data:
            new_item = {k: v for k, v in item.items() if k not in keys_to_remove}
            new_data.append(new_item)
        return Dataset(new_data)

    @staticmethod
    def filter_by_length(dataset: Dataset, min_len: int = 0, max_len: int = 100000) -> Dataset:
        """Filter items by content length."""
        new_data = []
        for item in dataset.data:
            content = str(item.get("prompt", "")) or str(item.get("messages", ""))
            if min_len <= len(content) <= max_len:
                new_data.append(item)
        return Dataset(new_data)
