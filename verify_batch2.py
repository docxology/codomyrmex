
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

import codomyrmex.agents as agents
import codomyrmex.skills as skills
import codomyrmex.tools as tools
from codomyrmex.agents.git_agent import GitAgent

print("Verifying Agent Ecosystem...")

try:
    # 1. verify GitAgent instantiation
    print("Checking GitAgent...")
    agent = GitAgent()
    print("✅ GitAgent instantiated")
except Exception as e:
    print(f"❌ GitAgent failed: {e}")
    sys.exit(1)

try:
    # 2. Verify SkillsManager
    print("Checking SkillsManager...")
    sm = skills.get_skills_manager(auto_sync=False)
    print("✅ SkillsManager instantiated")
except Exception as e:
    print(f"❌ SkillsManager failed: {e}")
    sys.exit(1)

try:
    # 3. Verify Check Dependencies tool
    print("Checking DependencyAnalyzer...")
    analyzer = tools.DependencyAnalyzer(str(src_dir))
    print("✅ DependencyAnalyzer instantiated")
except Exception as e:
    print(f"❌ DependencyAnalyzer failed: {e}")
    sys.exit(1)

print("\nBatch 2 Verification Passed!")
