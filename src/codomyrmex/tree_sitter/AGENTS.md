# tree_sitter - Technical Documentation

## Operating Contract

- Use `tree-sitter` for all parsing operations.
- Maintain a registry of supported languages and their compiled libraries.
- Ensure thread-safety for parser instances where possible.
- Provide clear error messages for grammar loading failures.

## Directory Structure

- `__init__.py`: Module entry point and exports.
- `parser.py`: Core `TreeSitterParser` implementation.
- `languages.py`: Language grammar management and loading logic.
- `utils.py`: AST traversal and utility functions.

## Implementation Details

### Parser Lifecycle

1. Request a language grammar from `LanguageManager`.
2. Initialize `tree_sitter.Parser`.
3. Set the parser's language.
4. Execute `parser.parse(source_code)`.

### Grammar Compilation

If a pre-compiled library is not found, the module should provide instructions or a helper to clone the grammar repository and build it using `Language.build_library`.

## Testing Strategy

- Unit tests for parser initialization.
- Mocked grammar loading to verify parser calls.
- Integration tests with real grammars (if available in the environment).
