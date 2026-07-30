# qmd Documentation Search

Use this skill when searching repository Markdown, notes, or documentation.

## Safety boundary

`qmd` is optional and is not installed by Codomyrmex. Do not install it, download
embedding or reranking models, create an index, or modify a user's qmd
collections without explicit authorization. These operations may consume
substantial disk space and network bandwidth.

## Search procedure

1. From the repository root, check whether qmd is available:

   ```bash
   command -v qmd
   ```

2. If it is available, inspect configured collections before querying:

   ```bash
   qmd collection list
   ```

3. Query only an existing collection whose scope matches the request. Start with
   lexical search; use hybrid or semantic search only when the installed qmd
   version supports it and the broader retrieval is useful.

4. If qmd is absent or no suitable collection exists, use the repository-native
   fallback:

   ```bash
   rg --files -g '*.md'
   rg -n -i 'search terms' -g '*.md' .
   ```

5. Open only the relevant files and verify claims against current source,
   generated receipts, or authoritative documentation before editing.

## Output expectations

- Report the search scope and whether qmd or `rg` supplied the results.
- Treat search results as discovery evidence, not proof that a document is
  current.
- Preserve the dirty worktree and the documentation hand-pass freeze.
