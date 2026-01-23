# Codomyrmex Agents - src/codomyrmex/fpf/io

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Input/Output module for FPF (First Principles Framework) specifications. Provides fetching from GitHub, local file loading, JSON export for context engineering, and section-level extraction and management. This module handles all data transfer and serialization needs for FPF processing.

## Active Components

- `fetcher.py` - GitHub fetcher with caching (FPFFetcher)
- `exporter.py` - JSON and context export (FPFExporter)
- `section_manager.py` - Section extraction and management (SectionManager)
- `section_exporter.py` - Section-specific export utilities
- `section_importer.py` - Section import utilities

## Key Classes

### FPFFetcher (fetcher.py)
Fetcher for FPF specification from GitHub:
- `fetch_latest()`: Download FPF-Spec.md from GitHub
  - Default: `ailev/FPF` repository, `main` branch
  - Constructs raw.githubusercontent.com URL
  - 30-second timeout for requests
- `check_for_updates()`: Compare local file hash with remote
  - SHA256 hash comparison
  - Returns True if local differs from remote
- `get_version_info()`: Get commit information from GitHub API
  - Returns sha, date, message from latest commit
- `cache_spec()`: Save specification to local cache
  - Cache directory: `~/.codomyrmex/fpf_cache/`
  - Filename includes version or content hash

### FPFExporter (exporter.py)
Exporter for FPF specifications to structured formats:
- `export_json()`: Export complete specification to JSON
  - Includes version, patterns, concepts, relationships, TOC
  - Creates parent directories automatically
- `export_patterns_json()`: Export pattern list only
- `export_concepts_json()`: Export concept list only
- `export_for_context()`: Export optimized for prompt engineering
  - Truncates sections to 500 chars, definitions to 200 chars
  - Applies filters: part, status, pattern_ids
  - Returns summary counts with truncated content

Internal conversion methods:
- `_pattern_to_dict()`: Convert Pattern to dictionary
- `_concept_to_dict()`: Convert Concept to dictionary
- `_relationship_to_dict()`: Convert Relationship to dictionary

### SectionManager (section_manager.py)
Manager for FPF section extraction and management:
- `extract_part()`: Extract all content for a specific part (A, B, C...)
  - Returns patterns, concepts, relationships for that part
  - Includes metadata with counts
- `extract_pattern_group()`: Extract group of patterns by ID
  - Optionally includes dependent patterns
  - Follows relationship graph for dependencies
- `extract_concept_cluster()`: Extract concept group with related patterns
  - Optionally includes patterns that reference concepts
- `extract_relationship_subset()`: Extract relationships by type
  - Optionally includes related patterns
- `list_parts()`: Get all part identifiers in specification
- `list_pattern_groups()`: List patterns grouped by part or flat
- `get_section_statistics()`: Statistics for each part
  - Pattern count, concept count, relationship count per part

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- FPFFetcher requires network access for GitHub fetching
- Cache directory is created automatically if needed
- FPFExporter creates parent directories for output files
- JSON exports use UTF-8 encoding with 2-space indentation
- Context exports truncate content to manage token limits
- SectionManager filters use set operations for efficient matching
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Core Module**: `../core/` - FPFParser, FPFExtractor, models for data structures
- **Analysis Module**: `../analysis/` - FPFAnalyzer, FPFIndexer, TermAnalyzer
- **Visualization Module**: `../visualization/` - FPFVisualizer, GraphGenerator
- **CEREBRUM Integration**: `../../cerebrum/fpf/` - Uses FPFClient which wraps fetcher/exporter
- **Parent Directory**: [fpf](../README.md) - FPF package documentation
- **Project Root**: ../../../../README.md - Main project documentation
