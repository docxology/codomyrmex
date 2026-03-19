#!/usr/bin/env python3
from codomyrmex.agents.hermes.hermes_client import HermesClient


def main():
    client = HermesClient()
    print("=== Hermes Health Check ===")

    # Check status
    try:
        status = client.get_hermes_status()
        print(f"CLI Available: {status['cli_available']}")
        print(f"Ollama Available: {status['ollama_available']}")
        print(f"Active Backend: {status['active_backend']}")
        print(f"Active Model (Ollama): {status['ollama_model']}")
    except Exception as e:
        print(f"Error checking status: {e}")

    # Check Rotation
    try:
        models = client._router.get_rotation_models()
        print(f"\nRotation Config: {len(models)} models found at {client._router._rotation_path}")
        for m in models:
            print(f"  - {m['model']} (priority {m['priority']})")
    except Exception as e:
        print(f"Error checking rotation: {e}")

    # Check DB
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore
        with SQLiteSessionStore(client._session_db_path) as store:
            stats = store.get_stats()
            print(f"\nSession Database: {client._session_db_path}")
            print(f"  - Sessions: {stats['session_count']}")
            print(f"  - DB Size: {stats['db_size_bytes'] / 1024:.1f} KB")
            print(f"  - Newest: {stats['newest_session_at']}")
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    main()
