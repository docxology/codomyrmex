# Feature Store

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview
This directory contains the real, functional implementations and components for the `Feature Store` module within the Codomyrmex ecosystem. It provides a robust, typed, and versioned store for ML features.

## Principles
- **Functional Integrity**: All methods and classes within this directory are designed to be fully operational and production-ready.
- **Zero-Mock Policy**: Code herein adheres to the strict Zero-Mock testing policy, ensuring all tests run against real logic.
- **Type Safety**: Features are strictly typed using `FeatureType` and `ValueType`.
- **Concurrency**: The `InMemoryFeatureStore` is thread-safe.

## Components
- `models.py`: Data models for features, values, vectors, and groups.
- `store.py`: Storage backend interfaces and implementations.
- `service.py`: High-level feature service with transforms and batching.
- `exceptions.py`: Module-specific exception classes.
