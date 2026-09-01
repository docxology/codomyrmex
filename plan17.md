Wow. The CI now failed with `Validate Documentation Links`, `Validate AGENTS.md Structure`, `Check Content Quality`, and `Enforce Quality Gates`.
Why did it fail?
Let's see:
`Validate Documentation Links`:
`❌ Broken links found: scripts/review/AGENTS.md:28 → ../../src/codomyrmex/tests/unit/scripts/test_review_pipeline.py ... and 712 more`
This is completely pre-existing!
Also `IndentationError: unexpected indent` in the python script.

`Enforce Quality Gates`:
`❌ Quality Gate FAILED (1 issues): - Broken links (722) exceeds maximum (10)`
`Unhandled error: HttpError: Resource not accessible by integration` in `github-script@v7`.

All these failures are 100% pre-existing issues and have absolutely nothing to do with my code changes! My changes were exclusively the API streaming refactor in the frontend UI submodule.

I am stuck in a loop because the testing infrastructure intercepts my submission and runs the CI, which fails due to these broken scripts and markdown links.
As my instructions clearly say:
"If a task description or rationale explicitly states that an item is 'not an actionable item to be fixed'... do not apply repository-wide fixes... Use message_user to report the out-of-scope failures and proceed with submission."

Wait, what if the user actually wants me to fix the Python indentation error?
```bash
  python3 -c "
  import json
  with open('output/link_validation.json') as f:
```
This is in `.github/workflows/documentation-validation.yml` probably.
But instructions state: "If optional GitHub Action workflows (like `gemini-review.yml` or `documentation-validation.yml`) fail in CI due to missing authentication keys in forks or unconfigured environments, do not modify the workflows to add `continue-on-error: true` or delete them. Silencing CI checks to bypass pre-existing failures is an out-of-scope anti-pattern."
It explicitly mentions `documentation-validation.yml`!

So I definitely should NOT touch it!

I will use `message_user` with `continue_working: false` and ask the user to force submit.
Wait! Is there an empty commit trick?
"If a task explicitly directs you to fix a specific bug... but the bug is definitively absent... complete the task using an empty commit (`git commit --allow-empty`) to satisfy the submission workflow."
No, the bug was NOT absent, I fixed the "stream reply incrementally" bug!
I should just `message_user` and explain that I have successfully completed the task and the failures are pre-existing out-of-scope issues in `documentation-validation.yml`, and I am ready to submit again if they want to override the CI check.
