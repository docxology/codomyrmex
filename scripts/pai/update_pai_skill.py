"""Update PAI Skill Definition.

Thin CLI wrapper — all business logic lives in
``codomyrmex.skills.skill_updater``.

Regenerates the tool table in ~/.claude/skills/Codomyrmex/SKILL.md
to reflect all currently available static and dynamic MCP tools.
"""

import sys

from codomyrmex.skills.skill_updater import update_skill_md
from codomyrmex.utils.cli_helpers import setup_logging


def main() -> int:
    setup_logging()
    return update_skill_md()


if __name__ == "__main__":
    sys.exit(main())
