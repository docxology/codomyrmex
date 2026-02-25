# Tree-sitter - API Specification

## Introduction

The Tree-sitter module provides code parsing capabilities using Tree-sitter, enabling fast and accurate syntax tree generation for multiple programming languages.

## Endpoints / Functions / Interfaces

### Class: `TreeSitterParser`

- **Description**: Parser for generating syntax trees from source code.
- **Constructor**:
    - `language` (str): Programming language to parse.
    - `language_manager` (LanguageManager, optional): Language manager instance.
- **Methods**:

#### `parse(source: str | bytes) -> SyntaxTree`

- **Description**: Parse source code into a syntax tree.
- **Parameters/Arguments**:
    - `source` (str | bytes): Source code to parse.
- **Returns**:
    - `SyntaxTree`: Parsed syntax tree.

#### `parse_file(path: str) -> SyntaxTree`

- **Description**: Parse source code from a file.
- **Parameters/Arguments**:
    - `path` (str): Path to source file.
- **Returns**:
    - `SyntaxTree`: Parsed syntax tree.

#### `query(tree: SyntaxTree, query_string: str) -> list[QueryMatch]`

- **Description**: Execute a Tree-sitter query on a syntax tree.
- **Parameters/Arguments**:
    - `tree` (SyntaxTree): Syntax tree to query.
    - `query_string` (str): Tree-sitter query pattern.
- **Returns**:
    - `list[QueryMatch]`: List of query matches.

#### `get_node_text(node: Node, source: str | bytes) -> str`

- **Description**: Get the text content of a syntax tree node.
- **Parameters/Arguments**:
    - `node` (Node): Syntax tree node.
    - `source` (str | bytes): Original source code.
- **Returns**:
    - `str`: Node text content.

#### `find_nodes(tree: SyntaxTree, node_type: str) -> list[Node]`

- **Description**: Find all nodes of a specific type.
- **Parameters/Arguments**:
    - `tree` (SyntaxTree): Syntax tree to search.
    - `node_type` (str): Type of nodes to find.
- **Returns**:
    - `list[Node]`: Matching nodes.

#### `get_function_definitions(tree: SyntaxTree, source: str) -> list[FunctionDef]`

- **Description**: Extract function definitions from syntax tree.
- **Parameters/Arguments**:
    - `tree` (SyntaxTree): Syntax tree.
    - `source` (str): Source code.
- **Returns**:
    - `list[FunctionDef]`: List of function definitions.

#### `get_class_definitions(tree: SyntaxTree, source: str) -> list[ClassDef]`

- **Description**: Extract class definitions from syntax tree.
- **Parameters/Arguments**:
    - `tree` (SyntaxTree): Syntax tree.
    - `source` (str): Source code.
- **Returns**:
    - `list[ClassDef]`: List of class definitions.

### Class: `LanguageManager`

- **Description**: Manages Tree-sitter language grammars.
- **Constructor**:
    - `languages_dir` (str, optional): Directory for language grammars.
- **Methods**:

#### `get_language(name: str) -> Language`

- **Description**: Get a language grammar.
- **Parameters/Arguments**:
    - `name` (str): Language name (e.g., "python", "javascript").
- **Returns**:
    - `Language`: Tree-sitter language grammar.

#### `load_language(name: str, path: str) -> Language`

- **Description**: Load a language grammar from a shared library.
- **Parameters/Arguments**:
    - `name` (str): Language name.
    - `path` (str): Path to shared library.
- **Returns**:
    - `Language`: Loaded language grammar.

#### `get_available_languages() -> list[str]`

- **Description**: Get list of available languages.
- **Returns**:
    - `list[str]`: Available language names.

#### `is_language_available(name: str) -> bool`

- **Description**: Check if a language is available.
- **Parameters/Arguments**:
    - `name` (str): Language name.
- **Returns**:
    - `bool`: True if language is available.

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
