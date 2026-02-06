# i18n - MCP Tool Specification

## General Considerations for i18n Tools

- **Dependencies**: No external dependencies. Pure Python with standard library only.
- **Initialization**: A `Translator` instance is maintained across tool calls within a session. Message bundles must be loaded before translation.
- **Error Handling**: Tools return `{"error": "description"}` on failure. Translation tools return the raw key as fallback when no match is found.
- **Locale Codes**: Accept both hyphen (`en-US`) and underscore (`en_US`) formats.

---

## Tool: `i18n_translate`

### 1. Tool Purpose and Description

Translates a message key to the specified locale, applying variable interpolation. Falls back through locale hierarchy (exact match, language-only, default locale, raw key).

### 2. Invocation Name

`i18n_translate`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `key` | `string` | Yes | Message key to translate | `"greeting.hello"` |
| `locale` | `string` | No | Target locale code. Default: current locale | `"es_MX"` |
| `variables` | `object` | No | Interpolation values for `{placeholder}` tokens | `{"name": "World"}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `translation` | `string` | Translated and interpolated message | `"Hola, World"` |
| `locale` | `string` | Locale that provided the match | `"es"` |
| `fallback` | `boolean` | True if default locale or raw key was used | `false` |

### 5. Error Handling

- `NO_BUNDLES_LOADED`: No message bundles have been registered.

### 6. Idempotency

- **Idempotent**: Yes. Same key, locale, and variables always produce the same result.

### 7. Usage Examples

```json
{
  "tool_name": "i18n_translate",
  "arguments": {
    "key": "welcome.message",
    "locale": "fr",
    "variables": {"user": "Alice", "count": "3"}
  }
}
```

### 8. Security Considerations

- **Input Validation**: Keys and variables are treated as plain strings. No code execution.
- **Data Handling**: No file system access during translation. Bundles are pre-loaded.

---

## Tool: `i18n_add_messages`

### 1. Tool Purpose and Description

Registers a message bundle for a locale. Accepts a flat key-value mapping of message keys to translated strings. Overwrites any existing bundle for that locale.

### 2. Invocation Name

`i18n_add_messages`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `locale` | `string` | Yes | Locale code for the bundle | `"de"` |
| `messages` | `object` | Yes | Flat mapping of key to translated string | `{"greeting": "Hallo", "farewell": "Tschuess"}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `locale` | `string` | Registered locale code | `"de"` |
| `message_count` | `integer` | Number of messages in the bundle | `2` |
| `status` | `string` | Operation result | `"success"` |

### 5. Error Handling

- `INVALID_LOCALE`: Locale code could not be parsed.
- `INVALID_MESSAGES`: Messages parameter is not a valid object.

### 6. Idempotency

- **Idempotent**: Yes. Repeated calls with the same data produce the same state.

### 7. Usage Examples

```json
{
  "tool_name": "i18n_add_messages",
  "arguments": {
    "locale": "ja",
    "messages": {
      "greeting": "こんにちは",
      "farewell": "さようなら",
      "thanks": "ありがとう"
    }
  }
}
```

### 8. Security Considerations

- **Input Validation**: Message values are stored as-is. No template execution.
- **Data Handling**: Bundles are held in memory only. No persistent storage.

---

## Tool: `i18n_list_locales`

### 1. Tool Purpose and Description

Lists all locales that have registered message bundles, along with the number of messages in each bundle.

### 2. Invocation Name

`i18n_list_locales`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| _(none)_ | | | This tool takes no parameters | |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `locales` | `array[object]` | List of `{code, language, region, message_count}` | See below |
| `default_locale` | `string` | Current default locale code | `"en"` |
| `total` | `integer` | Total number of registered locales | `3` |

### 5. Error Handling

- No error conditions. Returns empty array if no bundles are loaded.

### 6. Idempotency

- **Idempotent**: Yes. Read-only operation.

### 7. Usage Examples

```json
{
  "tool_name": "i18n_list_locales",
  "arguments": {}
}
```

### 8. Security Considerations

- **Data Handling**: Read-only. No sensitive data exposed.

---

## Navigation Links

- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Human Documentation**: [README.md](README.md)
- **Parent Directory**: [codomyrmex](../README.md)
