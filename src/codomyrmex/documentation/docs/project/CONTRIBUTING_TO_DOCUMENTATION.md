---
sidebar_label: 'Contributing to Documentation'
---

# Contributing to Documentation

Thank you for your interest in contributing to the Codomyrmex project documentation! High-quality documentation is crucial for making the project accessible, understandable, and easy to use for everyone.

This guide provides conventions and best practices for writing and structuring documentation content. For instructions on how to set up the Docusaurus environment locally, build the site, or the overall contribution workflow (Git, PRs), please refer to the [main project `CONTRIBUTING.md`](../../../../../../docs/project/contributing.md) and the [`documentation` module's `README.md`](../../../README.md).

## Guiding Principles

-   **Clarity**: Write in clear, concise language. Avoid jargon where possible, or explain it if necessary.
-   **Accuracy**: Ensure all information is up-to-date and technically correct. Test code examples and steps in tutorials.
-   **Completeness**: Cover the necessary topics thoroughly, but avoid unnecessary detail.
-   **Consistency**: Follow the established style, tone, and terminology across all documentation.
-   **User-Focus**: Write for the target audience. Consider what they need to know and how they will use the information. (e.g., are you writing for end-users, developers, or contributors?)

## Documentation Structure

The overall documentation is structured as follows (see `documentation/README.md` for more on the Docusaurus file structure):

-   **Introduction (`docs/intro.md`)**: The main landing page.
-   **Project-Level Information (`docs/project/`)**:
    -   Overall project architecture, goals, and vision.
    -   General contribution guidelines (like this document).
    -   Code of Conduct, License.
-   **Module-Specific Documentation (`docs/modules/<module-name>/`)**: Each module has its own section containing:
    -   `README.md` (Overview)
    -   `API_SPECIFICATION.md`
    -   `MCP_TOOL_SPECIFICATION.md`
    -   `docs/technical_overview.md`
    -   `docs/tutorials/*.md`
    -   `USAGE_EXAMPLES.md`
    -   `SECURITY.md`
    -   `CHANGELOG.md`
-   **Project-Wide Tutorials (`docs/tutorials/`)**: Tutorials that span multiple modules or cover general project concepts.
-   **Development Guides (`docs/development/`)**: Information for developers contributing to Codomyrmex itself (e.g., advanced setup, coding standards, testing, documentation pipeline).

## Style and Tone

-   **Tone**: Professional, helpful, and informative.
-   **Voice**: Use active voice where possible.
-   **Language**: Use clear and straightforward American English.
-   **Pronouns**: Use "you" to address the reader. Use "we" when referring to the Codomyrmex project or team.
-   **Abbreviations and Acronyms**: Spell out acronyms on first use, followed by the acronym in parentheses. For example, "Model Context Protocol (MCP)". Thereafter, the acronym can be used.

## Markdown and MDX Usage

All documentation is written in Markdown (`.md`) or MDX (`.mdx`). MDX allows embedding React components within Markdown.

### Headings

-   Use ATX-style headings (`#`, `##`, `###`, etc.).
-   Start with a single H1 (`#`) for the page title (Docusaurus often handles this via frontmatter `title` or filename). Subsequent sections should use H2 (`##`), H3 (`###`), and so on.
-   Do not skip heading levels (e.g., H2 followed directly by H4).
-   Write headings in sentence case (capitalize the first word and any proper nouns).

### Text Formatting

-   **Bold**: Use `**bold**` for strong emphasis or to highlight UI elements, filenames, or key terms.
-   *Italic*: Use `*italic*` or `_italic_` for emphasis, new terms, or placeholders.
-   `Code`: Use backticks (`` `code` ``) for inline code, commands, file paths, variable names, function names, and MCP tool names.
    - For file paths: `path/to/your/file.md`
    - For commands: `npm run start`
    - For module names: `ai_code_editing`
    - For function names: `create_line_plot()`
    - For MCP tool names: `execute_code`

### Lists

-   **Unordered Lists**: Use hyphens (`-`) or asterisks (`*`).
    ```markdown
    - Item 1
    - Item 2
      - Sub-item 2.1
      - Sub-item 2.2
    ```
-   **Ordered Lists**: Use numbers followed by a period.
    ```markdown
    1. First step
    2. Second step
       1. Sub-step 2.1
    3. Third step
    ```

### Code Blocks

-   Use triple backticks (```` ``` ````) to create fenced code blocks.
-   Specify the language for syntax highlighting:
    ````markdown
    ```python
    def hello_world():
        print("Hello, Codomyrmex!")
    ```

    ```json
    {
      "tool_name": "example_tool",
      "arguments": {
        "param1": "value1"
      }
    }
    ```

    ```bash
    npm install docusaurus
    ```
    ````
-   For longer commands or outputs, use code blocks. For short inline commands, use single backticks.

### Links

-   **Internal Links**: Use relative paths to link to other documentation pages or assets.
    -   Linking to another page in the same directory: `[Link Text](./other-page.md)`
    -   Linking to a page in a subdirectory: `[Link Text](./subdirectory/page.md)`
    -   Linking to a page in a parent directory: `[Link Text](../parent-page.md)`
    -   Linking to a specific heading: `[Link Text](./other-page.md#heading-id)` (Docusaurus auto-generates heading IDs).
-   **External Links**: Use the full URL.
    `[Docusaurus Website](https://docusaurus.io/)`
-   **Asset Links**: To link to static assets (like images in `static/img/`), use a path relative to the `static` directory, prefixed with a `/`.
    `![Alt Text](/img/codomyrmex_logo.png)`

### Images

-   Store images in the `documentation/static/img/` directory, possibly in subfolders for organization.
-   Use descriptive alt text for accessibility: `![Diagram showing data flow through the module](/img/data_flow_diagram.png)`
-   Optimize images for the web to reduce file sizes.

### Tables

-   Use Markdown tables for structured data.
    ```markdown
    | Header 1 | Header 2 | Header 3 |
    | :------- | :------: | -------: |
    | Left     | Center   | Right    |
    | Cell     | Cell     | Cell     |
    ```

### Admonitions (Docusaurus Feature)

Use admonitions to highlight important information. Docusaurus provides several types:

```markdown
:::note
This is a note. Useful for tips or additional information.
:::

:::tip
This is a tip. Suggests helpful advice or best practices.
:::

:::info
This is an informational message.
:::

:::caution
This is a caution. Warns about potential pitfalls or risks.
:::

:::danger
This is a danger warning. Indicates critical information or actions that could have negative consequences.
:::
```

## Writing Guidelines

### Tutorials

-   **Goal-Oriented**: Clearly state the learning objectives at the beginning.
-   **Prerequisites**: List any necessary knowledge, tools, or setup.
-   **Step-by-Step Instructions**: Break down complex tasks into manageable, numbered steps.
-   **Code Examples**: Provide clear, concise, and runnable code examples. Explain each part of the code.
-   **Expected Outcome**: Describe what the user should see or achieve after completing the tutorial.
-   **Troubleshooting**: Include a section for common problems and their solutions.
-   **Next Steps**: Suggest further learning or related topics.

### API and MCP Tool Specifications

-   **Consistency**: Follow the established format for `API_SPECIFICATION.md` and `MCP_TOOL_SPECIFICATION.md` files across modules.
-   **Parameters/Arguments**: Clearly define each parameter, its type, whether it's required, its purpose, and provide an example value.
-   **Return Values/Output Schema**: Describe the structure and meaning of the output.
-   **Error Handling**: Explain how errors are reported.
-   **Idempotency**: State whether the tool or function is idempotent.
-   **Usage Examples**: Provide clear JSON examples for MCP tools or Python snippets for API functions.
-   **Security Considerations**: Detail any security aspects relevant to the API or tool.

### Technical Overviews

-   **Introduction and Purpose**: Briefly explain what the module does and the problems it solves.
-   **Architecture**: Describe key components, data flow, core logic, and external dependencies. Include Mermaid diagrams where helpful.
-   **Design Decisions**: Explain the rationale behind significant design choices.
-   **Data Models**: Describe important data structures used by the module.
-   **Configuration**: Detail any configuration options.
-   **Scalability and Performance**: Discuss relevant aspects.
-   **Security Aspects**: Summarize or link to key security points from `SECURITY.md`.
-   **Future Development**: Outline potential future enhancements.

### READMEs (Module-Level)

-   Provide a concise overview of the module's purpose and functionality.
-   Include basic setup and usage instructions relevant to that module.
-   Link to more detailed documentation within the module (API specs, technical overview, tutorials).

## Updating Existing Documentation

-   When making changes to code that affect functionality, API signatures, or user workflows, **always update the corresponding documentation**.
-   Review existing documentation periodically for accuracy and completeness.
-   If you find outdated or incorrect information, please fix it or report an issue.

## Final Checklist Before Submitting

-   [ ] Have you followed the style and tone guidelines?
-   [ ] Is the information accurate and up-to-date?
-   [ ] Are code examples correct and runnable?
-   [ ] Are all links working (internal and external)?
-   [ ] Is the Markdown/MDX syntax correct and rendering as expected? (Test locally!)
-   [ ] Have you used appropriate alt text for images?
-   [ ] If adding new files, have you updated `sidebars.js` if necessary to include them in navigation?
-   [ ] Have you followed the project's general contribution workflow (Git, PRs)?

Thank you for helping to improve the Codomyrmex documentation! 