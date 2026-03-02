1. **Create `src/codomyrmex/web_scraping/mcp_tools.py`:**
   - Add three MCP tools to the module:
     - `scraping_fetch_page(url: str) -> dict`: fetches and parses a web page.
     - `scraping_extract_links(url: str, base_url: str = "") -> dict`: extracts all links from a page.
     - `scraping_get_text(url: str) -> dict`: extracts clean text content from a URL.
   - Use the `@mcp_tool` decorator. Note: The prompt instructed to import from `codomyrmex.model_context_protocol.tool_decorator`, but standard usage and actual file existence points to `codomyrmex.model_context_protocol.decorators`. I will import from `codomyrmex.model_context_protocol.tool_decorator` and create a compatibility alias or just create `src/codomyrmex/model_context_protocol/tool_decorator.py` to alias to decorators if it's strictly required by tests, or simply use what exists. Wait! I will just import `mcp_tool` from `codomyrmex.model_context_protocol.tool_decorator` and provide that file if it's missing, OR just assume the user meant `codomyrmex.model_context_protocol.tool_decorator` and I need to create it since they explicitly asked for it? Let's read the memory: "MCP tools across the project should use the `@mcp_tool` decorator imported specifically from `codomyrmex.model_context_protocol.tool_decorator`". So I must ensure `tool_decorator.py` exists or I must use it. Let's create `tool_decorator.py` that imports `mcp_tool` from `decorators.py`!
2. **Implement web scraping logic:**
   - Use standard libraries like `urllib` or `requests` (if installed) and `re` or `html.parser` for zero-dependency parsing, or `beautifulsoup4` if available. Let's use `urllib.request` and `html.parser` to avoid adding dependencies unless requested.
3. **Create `src/codomyrmex/tests/unit/web_scraping/test_mcp_tools.py`:**
   - Write zero-mock unit tests for the three MCP tools.
   - Use the filesystem or `http.server` module for a real, local web server, or perhaps rely on local files using `file://` URLs for strictly zero-mock tests without relying on the internet. Wait, zero mock means we should use real objects, a real local http server is perfect for this.
4. **Pre commit step:**
   - Run the pre commit instructions.
5. **Submit:**
   - Commit and submit.
