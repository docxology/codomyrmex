# Agentic Guidelines

Agents interacting with the `languages` module can utilize it to safely probe the current environment's capabilities before generating or attempting to execute code.

## Protocol for Agents

1. **Check Presence:** Always use `check_language_installed('language')` before attempting to execute a script or build command.
2. **Provide Guidance:** If a language is missing, use `get_language_install_instructions('language')` and politely inform the user, offering to run the commands for them if permitted.
3. **Execute Cautiously:** When using `run_language_script`, remember that code runs directly on the user's host machine. Ensure the generated script is safe and non-destructive.
