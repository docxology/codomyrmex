# i18n - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The i18n module provides internationalization support including message translation with interpolation, locale management, pluralization rules, and locale-aware number formatting.

## Data Classes

### `Locale`

Represents a language/region locale.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `language` | `str` | required | ISO 639-1 language code (e.g., `"en"`, `"es"`) |
| `region` | `str` | `""` | ISO 3166-1 region code (e.g., `"US"`, `"MX"`) |

#### Property: `code -> str`

Returns the full locale code. Example: `"en_US"` or `"en"` if no region.

#### `Locale.from_string(code) -> Locale` (classmethod)

- **Description**: Parse a locale string. Accepts both `"en-US"` and `"en_US"` formats.
- **Parameters**:
    - `code` (str): Locale string.
- **Returns**: `Locale` instance.

## Classes

### `MessageBundle`

A collection of translated messages for a single locale.

#### `MessageBundle.__init__(locale)`

- **Parameters**:
    - `locale` (Locale): The locale this bundle serves.

#### `MessageBundle.add(key, message) -> None`

- **Description**: Add or overwrite a message by key.

#### `MessageBundle.get(key, default=None) -> str | None`

- **Description**: Retrieve a message by key with optional default.

#### `MessageBundle.has(key) -> bool`

- **Description**: Check if a key exists in the bundle.

#### `MessageBundle.keys() -> list[str]`

- **Description**: Return all message keys.

#### `MessageBundle.to_dict() -> dict[str, str]`

- **Description**: Export bundle as a dictionary copy.

#### `MessageBundle.from_dict(locale, data) -> MessageBundle` (classmethod)

- **Description**: Create a bundle from a locale and dict of key-message pairs.

#### `MessageBundle.from_json_file(locale, path) -> MessageBundle` (classmethod)

- **Description**: Load messages from a JSON file. File must be a flat `{"key": "message"}` mapping.
- **Raises**: `FileNotFoundError`, `json.JSONDecodeError`.

### `Translator`

Multi-locale translator with interpolation and fallback resolution.

#### `Translator.__init__(default_locale=None)`

- **Parameters**:
    - `default_locale` (Locale | None): Fallback locale. Defaults to `Locale("en")`.

#### `Translator.add_bundle(bundle) -> None`

- **Description**: Register a `MessageBundle`.

#### `Translator.set_locale(locale) -> None`

- **Description**: Set the current active locale.

#### `Translator.get_locale() -> Locale`

- **Description**: Return the current active locale.

#### `Translator.t(key, locale=None, **kwargs) -> str`

- **Description**: Translate a key with interpolation. Resolution order: (1) exact locale match, (2) language-only fallback, (3) default locale, (4) raw key.
- **Parameters**:
    - `key` (str): Message key.
    - `locale` (Locale | None): Override locale for this call.
    - `**kwargs`: Interpolation values for `{placeholder}` tokens.
- **Returns**: `str` - Translated and interpolated message, or the raw key if not found.

#### `Translator.load_directory(path) -> int`

- **Description**: Load all `*.json` files from a directory as message bundles. File stems are parsed as locale codes.
- **Returns**: `int` - Number of bundles loaded.

### `PluralRules`

Locale-aware pluralization. Supports `en`, `es`, `ru`, and `ar` out of the box.

#### `PluralRules.get_rule(locale) -> Callable[[int], str]` (classmethod)

- **Description**: Get the plural category function for a locale. Falls back to English rules.
- **Returns**: A function that maps a count to a category string (`"one"`, `"other"`, `"few"`, `"zero"`, `"two"`).

#### `PluralRules.pluralize(locale, count, forms) -> str` (classmethod)

- **Description**: Select the correct plural form for a count.
- **Parameters**:
    - `locale` (Locale): Target locale.
    - `count` (int): The number to pluralize.
    - `forms` (dict[str, str]): Mapping of plural category to message string.
- **Returns**: `str` - Selected form. Falls back to `"other"` key.

### `NumberFormatter`

Locale-aware number formatting. Supports `en`, `de`, and `fr` decimal/thousands conventions.

#### `NumberFormatter.format(locale, number, decimals=2) -> str` (classmethod)

- **Description**: Format a number with locale-appropriate separators.
- **Parameters**:
    - `locale` (Locale): Target locale.
    - `number` (float): Number to format.
    - `decimals` (int): Decimal places. Use `0` for integers.
- **Returns**: `str` - Formatted number string.

## Convenience Functions

### `init(default_locale="en") -> Translator`

Initialize the global default translator. Returns the `Translator` instance.

### `t(key, **kwargs) -> str`

Translate using the global translator. Auto-initializes with `"en"` if not yet configured.

## Error Handling

`Translator.t()` never raises exceptions -- it returns the raw key as a last-resort fallback. `MessageBundle.from_json_file` raises standard I/O and JSON exceptions. `NumberFormatter.format` falls back to English formatting for unknown locales.

## Configuration

No configuration files required. Bundles are loaded programmatically or from JSON files via `load_directory()`.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
