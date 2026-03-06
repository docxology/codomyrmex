# Cache -- Agent Integration Guide

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The Cache module provides agents with key-value caching for intermediate results, enabling faster repeated operations and cross-phase data sharing.

## Available MCP Tools

### cache_get

Get a value from the named in-memory cache.

**Parameters:**
- `key` (str, required) -- The cache key to look up
- `cache_name` (str, default: "default") -- Name of the cache instance

**Returns:** The cached value, or None if the key is missing or expired.

### cache_set

Store a value in the named in-memory cache with optional TTL.

**Parameters:**
- `key` (str, required) -- The cache key
- `value` (object, required) -- The value to store (must be serializable)
- `ttl` (int | None, default: None) -- Time-to-live in seconds; None means no expiry
- `cache_name` (str, default: "default") -- Name of the cache instance

**Returns:** True on success.

### cache_delete

Delete a key from the named in-memory cache.

**Parameters:**
- `key` (str, required) -- The cache key to delete
- `cache_name` (str, default: "default") -- Name of the cache instance

**Returns:** True if deleted, False if the key did not exist.

### cache_stats

Get hit/miss/eviction statistics for the named cache.

**Parameters:**
- `cache_name` (str, default: "default") -- Name of the cache instance

**Returns:** Dictionary with hits, misses, hit_rate, size, writes, deletes.

## Agent Interaction Patterns

### Cross-Phase Caching
Store intermediate results in the OBSERVE phase for reuse in BUILD and VERIFY phases. Use descriptive keys like `"module_analysis:{module_name}"`.

### Performance Optimization
Before performing expensive operations (code analysis, API calls), check the cache first with `cache_get`. Store results with appropriate TTL values.

## Trust Level

All four MCP tools are classified as **Safe** -- they operate on in-process data and do not perform file system or network operations.

## Navigation

- **Source**: [src/codomyrmex/cache/](../../../../src/codomyrmex/cache/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
