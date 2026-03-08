# Languages Module

The `languages` module provides a consolidated interface for AI agents and automation scripts to interact with various programming languages on the host system.

## Purpose

To enable the system to easily:

1. **Check** if a language toolchain is installed (e.g., `python3`, `node`, `rustc`, `go`).
2. **Install** (provide instructions for) missing toolchains.
3. **Use** standard patterns to run basic scripts or commands in those languages.

## Supported Languages

* `csharp` (`dotnet`)
* `elixir`
* `go`
* `java`
* `javascript` (`node`)
* `php`
* `python`
* `r`
* `ruby`
* `rust`
* `swift`
* `typescript`
* `bash`

## Usage (MCP)

This module registers tools like:

* `check_language_installed(language)`
* `get_language_install_instructions(language)`
* `run_language_script(language, script_content)`
