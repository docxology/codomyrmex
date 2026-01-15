from typing import Optional
from pathlib import Path
import json
import yaml
import traceback
from ..utils import get_logger

logger = get_logger(__name__)

def handle_skills_sync(force: bool) -> bool:
    """Handle skills sync command."""
    try:
        from codomyrmex.skills import get_skills_manager
        manager = get_skills_manager()
        success = manager.sync_upstream(force=force)

        if success:
            print("✅ Skills synced successfully")
        else:
            print("❌ Failed to sync skills")
        return success
    except Exception as e:
        print(f"❌ Error syncing skills: {str(e)}")
        traceback.print_exc()
        return False


def handle_skills_list(category: Optional[str]) -> bool:
    """Handle skills list command."""
    try:
        from codomyrmex.skills import get_skills_manager
        manager = get_skills_manager()
        manager.initialize()

        skills = manager.list_skills(category=category)

        if not skills:
            print("No skills found" + (f" in category '{category}'" if category else ""))
            return True

        print(f"Found {len(skills)} skill(s):\n")
        for skill in skills:
            cat = skill["category"]
            name = skill["name"]
            source = skill.get("metadata", {}).get("source", "unknown")
            print(f"  {cat}/{name} ({source})")

        return True
    except Exception as e:
        print(f"❌ Error listing skills: {str(e)}")
        traceback.print_exc()
        return False


def handle_skills_get(category: str, name: str, output: Optional[str]) -> bool:
    """Handle skills get command."""
    try:
        from codomyrmex.skills import get_skills_manager
        manager = get_skills_manager()
        manager.initialize()

        skill = manager.get_skill(category, name)

        if not skill:
            print(f"❌ Skill not found: {category}/{name}")
            return False

        if output:
            output_path = Path(output)
            if output_path.suffix in [".yaml", ".yml"]:
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(skill, f, default_flow_style=False, sort_keys=False)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(skill, f, indent=2, ensure_ascii=False)
            print(f"✅ Skill saved to {output}")
        else:
            print(json.dumps(skill, indent=2, default=str, ensure_ascii=False))

        return True
    except Exception as e:
        print(f"❌ Error getting skill: {str(e)}")
        traceback.print_exc()
        return False


def handle_skills_search(query: str) -> bool:
    """Handle skills search command."""
    try:
        from codomyrmex.skills import get_skills_manager
        manager = get_skills_manager()
        manager.initialize()

        results = manager.search_skills(query)

        if not results:
            print(f"No skills found matching '{query}'")
            return True

        print(f"Found {len(results)} matching skill(s):\n")
        for result in results:
            cat = result["category"]
            name = result["name"]
            source = result.get("metadata", {}).get("source", "unknown")
            print(f"  {cat}/{name} ({source})")

        return True
    except Exception as e:
        print(f"❌ Error searching skills: {str(e)}")
        traceback.print_exc()
        return False
