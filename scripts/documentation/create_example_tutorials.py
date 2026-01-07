#!/usr/bin/env python3
"""
Thin wrapper for create_example_tutorials.py.
Logic migrated to codomyrmex.documentation.scripts.create_example_tutorials.
"""

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Ensure src is in python path
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root / "src") not in sys.path:
        sys.path.insert(0, str(project_root / "src"))

    try:
        from codomyrmex.documentation.scripts import create_example_tutorials
        if hasattr(create_example_tutorials, 'main'):
            sys.exit(create_example_tutorials.main())
        else:
            # If no main, just running the module might have been the original behavior
            # But importing it effectively runs top-level code if not guarded.
            # Most scripts here likely have "if __name__ == '__main__': main()"
            # But if we import it, the name is not main.
            # So we might need to explicitly run main().
            pass
    except ImportError as e:
        print(f"Error importing module: {e}")
        sys.exit(1)
    except AttributeError:
        print(f"Module create_example_tutorials does not have a main function or failed to execute.")
        sys.exit(1)
