# Codomyrmex Agents — serialization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `serialization` module enables agents to persist and transmit complex data structures. It provides the mechanism for state snapshots, inter-agent message encoding, and high-performance data storage.

## Active Components

- `serializer.py` – Core contract for all serialization formats.
- `binary_formats.py` – Efficient binary encoding (Msgpack, Avro, Parquet).
- `serialization_manager.py` – Global registry for format-agnostic data handling.

## Operating Contracts

1. **Format Parsimony**: Select the most efficient format for the medium (e.g., Msgpack for RPC, Parquet for large datasets, JSON for human-readable config).
2. **Schema Resilience**: Ensure serializers handle missing or unknown fields gracefully during deserialization.
3. **Deep Encoding**: Use `SerializationManager` to handle object graphs with circular references.

## Core Interfaces

- `Serializer.serialize(...)` / `Serializer.deserialize(...)`: Standard interface.
- `SerializationManager.encode(...)` / `SerializationManager.decode(...)`: format-aware orchestration.

## Navigation Links

- **🏠 Project Root**: ../../../README.md
- **📦 Module README**: ./README.md
- **📜 Functional Spec**: ./SPEC.md
