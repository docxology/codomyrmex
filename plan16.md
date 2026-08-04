The CI fails again! This time `Validate Documentation` fails:
`Missing README.md in tests`

Wait, `tests` is not a module! "Checking module: tests", "Missing README.md in tests".
This is also a pre-existing issue.

Wait, why did my PR trigger `Validate Documentation`?
Oh, I see:
```bash
if git diff --name-only origin/main...HEAD | grep -E "(README\.md|docs/|CHANGELOG\.md|API_SPECIFICATION\.md|MCP_TOOL_SPECIFICATION\.md|USAGE_EXAMPLES\.md|documentation/)" > /dev/null; then
    echo "docs=true" >> $GITHUB_OUTPUT
else
    echo "docs=false" >> $GITHUB_OUTPUT
fi
```
But wait! If I didn't change any of those files, it shouldn't trigger!
Oh, it checks `origin/main...HEAD`. If `origin/main` doesn't exist, it might trigger.
Either way, the failure is:
`src/codomyrmex/documentation/` script checking `../*/` and failing on `tests`.

This is ALSO an out-of-scope pre-existing issue in an unmodified file!
My memory says:
"When investigating GitHub CI check suite failures, if the errors stem from pre-existing issues in unmodified files (such as widespread `ruff format` violations, `markdownlint` errors in other directories, or missing environment dependencies like `eSpeak`), do not apply repository-wide fixes or formatting to turn the CI green. Use `message_user` to report the out-of-scope failures and proceed with submission."

I should just `message_user` with `continue_working: false` again.
