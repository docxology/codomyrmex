#!/usr/bin/env python3
"""
Feature Store Demo Script

Demonstrates functionality of the feature_store module.
"""

import sys
import math
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.feature_store import (
    FeatureDefinition,
    FeatureGroup,
    FeatureType,
    ValueType,
    FeatureService,
    FeatureTransform,
    InMemoryFeatureStore,
    FeatureStoreError,
)

def main() -> int:
    print("--- Codomyrmex Feature Store Orchestrator ---")
    
    # 1. Initialize Service and Store
    store = InMemoryFeatureStore()
    
    # Define a transform: Log transform for income
    transform = FeatureTransform()
    transform.add("income", lambda v: math.log(v + 1))
    
    service = FeatureService(store=store, transform=transform)
    
    # 2. Define Features and Groups
    print("\n[1] Registering features and groups...")
    user_features = FeatureGroup(
        name="user_demographics",
        features=[
            FeatureDefinition(
                name="age",
                feature_type=FeatureType.NUMERIC,
                value_type=ValueType.INT,
                description="User age",
                default_value=0
            ),
            FeatureDefinition(
                name="income",
                feature_type=FeatureType.NUMERIC,
                value_type=ValueType.FLOAT,
                description="Annual income"
            ),
            FeatureDefinition(
                name="is_active",
                feature_type=FeatureType.BOOLEAN,
                value_type=ValueType.BOOL,
                default_value=True
            ),
            FeatureDefinition(
                name="city",
                feature_type=FeatureType.CATEGORICAL,
                value_type=ValueType.STRING,
                default_value="Unknown"
            )
        ],
        entity_type="user"
    )
    
    service.register_group(user_features)
    print(f"Registered group: {user_features.name} with {len(user_features.features)} features.")
    
    # 3. Ingest Data
    print("\n[2] Ingesting batch data...")
    batch_data = [
        {"entity_id": "user_001", "age": 28, "income": 50000.0, "city": "San Francisco"},
        {"entity_id": "user_002", "age": 34, "income": 75000.0, "city": "New York"},
        {"entity_id": "user_003", "age": 45, "income": 120000.0, "is_active": False}
    ]
    
    count = service.ingest_batch(batch_data)
    print(f"Successfully ingested {count} records.")
    
    # 4. Retrieve Features
    print("\n[3] Retrieving feature vectors...")
    for user_id in ["user_001", "user_003", "user_999"]:
        print(f"\nFetching features for {user_id}:")
        vector = service.get_group_features(user_id, "user_demographics")
        
        # income is log-transformed because of the transform we added
        income_val = vector.get('income')
        if income_val is not None:
             print(f"  Age: {vector.get('age')}")
             print(f"  Income (Log): {income_val:.4f} (Original would be {math.exp(income_val)-1:.0f})")
             print(f"  City: {vector.get('city')}")
             print(f"  Active: {vector.get('is_active')}")
        else:
             print(f"  Found partial data or defaults: {vector.features}")

    # 5. Demonstrate Type Validation
    print("\n[4] Demonstrating type validation...")
    try:
        service.ingest({"age": "not_an_int"}, "user_001")
    except FeatureStoreError as e:
        print(f"Caught expected validation error: {e}")

    print("\n--- Demo Complete ---")
    return 0


    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "feature_store" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/feature_store/config.yaml")

if __name__ == "__main__":
    sys.exit(main())
