#!/usr/bin/env python3
"""
Debug script to examine what KGEntity.to_dict() actually returns.
"""

import sys
import os

# Add the parent directory to the path so we can import kgraphmemory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_haley_kg_domain.model.KGEntity import KGEntity
import json

def debug_kgentity_dict():
    """Debug what KGEntity.to_dict() returns."""
    
    print("=== KGEntity to_dict() Debug ===\n")
    
    # Create a test KGEntity
    entity = KGEntity()
    entity.URI = "http://example.com/entities/test"
    entity.name = "Test Entity"
    entity.kGEntityTypeDescription = "test type"
    entity.kGraphDescription = "Test description"
    
    print("1. Created KGEntity:")
    print(f"   URI: {entity.URI}")
    print(f"   Name: {entity.name}")
    print(f"   Type Description: {entity.kGEntityTypeDescription}")
    print(f"   Description: {entity.kGraphDescription}")
    
    print("\n2. KGEntity.to_dict() output:")
    entity_dict = entity.to_dict()
    
    for key, value in entity_dict.items():
        print(f"   '{key}': {repr(value)}")
    
    print(f"\n3. Total properties in to_dict(): {len(entity_dict)}")
    
    print("\n4. JSON representation:")
    try:
        json_str = entity.to_json()
        json_data = json.loads(json_str)
        print("   JSON keys:")
        for key in json_data.keys():
            print(f"     '{key}': {repr(json_data[key])}")
    except Exception as e:
        print(f"   Error getting JSON: {e}")
    
    print("\n5. Class URI:")
    print(f"   get_class_uri(): {entity.get_class_uri()}")


if __name__ == "__main__":
    debug_kgentity_dict()
