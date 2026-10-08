# Tree-sitter - API Specification

## Introduction

The Tree-sitter module provides code parsing capabilities using Tree-sitter, enabling fast and accurate syntax tree generation for multiple programming languages.

## Endpoints / Functions / Interfaces

### Class: `TreeSitterParser`

- **Description**: Parser for generating syntax trees from source code with py-tree-sitter.
- **Constructor**:
    - `language` (tree_sitter.Language): Grammar to parse with, for example from `LanguageManager.get_language("python")`.
- **Methods**:

#### `parse(source_code: str | bytes) -> tree_sitter.Tree`

- **Description**: Parse source code into a syntax tree. A `str` is encoded as UTF-8.
- **Parameters/Arguments**:
    - `source_code` (str | bytes): Source code to parse.
- **Returns**:
    - `tree_sitter.Tree`: Parsed syntax tree; walk it from `tree.root_node`.

#### `query(tree: tree_sitter.Tree, query_str: str) -> dict[str, list[tree_sitter.Node]]`

- **Description**: Run an S-expression query against a syntax tree.
- **Parameters/Arguments**:
    - `tree` (tree_sitter.Tree): Syntax tree to query.
    - `query_str` (str): Tree-sitter query pattern with `@capture` names.
- **Returns**:
    - `dict[str, list[tree_sitter.Node]]`: Capture name (without `@`) to the captured nodes.

### Class: `LanguageManager`

- **Description**: Class-level registry of tree-sitter grammars. All methods are classmethods; no instance is needed.
- **Methods**:

#### `register_language(lang_name: str, language: Any) -> Any` (classmethod)

- **Description**: Register a grammar shipped as a Python package.
- **Parameters/Arguments**:
    - `lang_name` (str): Name to register the grammar under (e.g., `"python"`).
    - `language`: A `tree_sitter.Language`, or the object returned by a grammar package's `language()` function such as `tree_sitter_python.language()`.
- **Returns**:
    - The registered `tree_sitter.Language`.

#### `load_language(library_path: str, lang_name: str) -> bool` (classmethod)

- **Description**: Load a grammar from a compiled shared library (.so, .dll, .dylib) that exports `tree_sitter_<lang_name>()`.
- **Parameters/Arguments**:
    - `library_path` (str): Path to the shared library.
    - `lang_name` (str): Language name.
- **Returns**:
    - `bool`: True on success; False (with the error logged) on failure.

#### `get_language(lang_name: str) -> Any | None` (classmethod)

- **Description**: Get a registered or loaded grammar.
- **Parameters/Arguments**:
    - `lang_name` (str): Language name.
- **Returns**:
    - The `tree_sitter.Language`, or None when it has not been registered or loaded.

#### `discover_languages(search_path: str) -> None` (classmethod)

- **Description**: Walk a directory and load every `.so`, `.dylib` or `.dll` grammar, inferring the language name from the file name (`tree-sitter-python.so` becomes `python`). A missing directory is ignored.

## Data Models

### Model: `SyntaxTree`

- `root_node` (Node): Root node of the tree.
- `language` (str): Language of the parsed source.
- `source_bytes` (bytes): Original source as bytes.

### Model: `Node`

- `type` (str): Node type (e.g., "function_definition").
- `start_point` (tuple[int, int]): Start position (row, column).
- `end_point` (tuple[int, int]): End position (row, column).
- `start_byte` (int): Start byte offset.
- `end_byte` (int): End byte offset.
- `children` (list[Node]): Child nodes.
- `parent` (Node | None): Parent node.
- `is_named` (bool): Whether node is a named node.

### Model: `QueryMatch`

- `pattern_index` (int): Index of matched pattern.
- `captures` (dict[str, list[Node]]): Named captures.

### Model: `FunctionDef`

- `name` (str): Function name.
- `parameters` (list[str]): Parameter names.
- `start_line` (int): Start line number.
- `end_line` (int): End line number.
- `docstring` (str | None): Function docstring.
- `decorators` (list[str]): Decorator names.

### Model: `ClassDef`

- `name` (str): Class name.
- `bases` (list[str]): Base class names.
- `methods` (list[FunctionDef]): Class methods.
- `start_line` (int): Start line number.
- `end_line` (int): End line number.
- `docstring` (str | None): Class docstring.

## Authentication & Authorization

N/A - This module operates locally.

## Rate Limiting

N/A - Parsing is local and not rate-limited.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
