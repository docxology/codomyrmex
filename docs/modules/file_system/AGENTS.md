# File System -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a unified interface for filesystem operations including file CRUD, directory management, searching, and metadata retrieval. Abstracts platform-specific filesystem details behind a consistent API.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `file_system_read` | Read a file and return its contents with metadata | Standard | file_system |
| `file_system_list_directory` | List entries in a directory with optional recursion | Standard | file_system |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| OBSERVE | Infrastructure Agent | Read and list filesystem contents for analysis |
| EXECUTE | Engineer Agent | Perform file operations as part of build workflows |


## Agent Instructions

1. file_system_read returns content and size metadata for the specified path
2. Set recursive=True on file_system_list_directory to traverse subdirectories


## Navigation

- [Source README](../../src/codomyrmex/file_system/README.md) | [SPEC.md](SPEC.md)
