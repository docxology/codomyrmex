#!/bin/bash

# Fix E402 by moving the import above the sys.path.insert, which is actually fine because we want to ignore E402 on this line.
# Or just ignore it. I will add # noqa: E402
for file in scripts/validation/rules/rules_demo.py scripts/validation/sanitizers/sanitizers_demo.py scripts/validation/schemas/schemas_demo.py; do
    sed -i 's/from codomyrmex.utils.cli_helpers import (/from codomyrmex.utils.cli_helpers import (  # noqa: E402/' "$file"
done
