# Pai Pm — Functional Specification

**Module**: `codomyrmex.pai_pm`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Codomyrmex pai_pm module — PAI Project Manager server wrapper.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Source Files

- `client.py`
- `config.py`
- `exceptions.py`
- `mcp_tools.py`
- `server_manager.py`

## 3. Dependencies

See `src/codomyrmex/pai_pm/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k pai_pm -v
```
