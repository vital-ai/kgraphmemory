#!/usr/bin/env python3
"""
Test script to understand what VitalSigns expects for successful conversion.
"""

import sys
import os

# Add the parent directory to the path so we can import kgraphmemory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vital_ai_vitalsigns.vitalsigns import VitalSigns
from ai_haley_kg_domain.model.KGEntity import KGEntity

def test_vitalsigns_conversion():
    """Test VitalSigns conversion with known working data."""
    
    print("=== VitalSigns Conversion Test ===\n")
    
    # Test 1: Create a KGEntity and convert to triples, then back
    print("1. Testing round-trip conversion...")
    
    entity = KGEntity()
    entity.URI = "http://example.com/entities/test"
    entity.name = "Test Entity"
    entity.kGEntityTypeDescription = "test type"
    entity.kGraphDescription = "Test description"
    
    print(f"   Original entity: {entity.name} ({entity.URI})")
    
    # Convert to triples using VitalSigns
    vs = VitalSigns()
    
    try:
        # Get triples from the entity
        triples = vs.to_triples(entity)
        print(f"   Generated {len(list(triples))} triples")
        
        # Convert back to triples generator for testing
        triples = vs.to_triples(entity)
        
        print("   Generated triples:")
        triple_list = []
        for i, (s, p, o) in enumerate(triples):
            print(f"     {i+1}. ({s}, {p}, {o})")
            triple_list.append((s, p, o))
        
        # Try to convert back
        def triple_generator():
            for triple in triple_list:
                yield triple
        
        converted = vs.from_triples(triple_generator())
        
        if converted:
            print(f"   ✅ Round-trip successful: {converted.name} ({converted.URI})")
        else:
            print(f"   ❌ Round-trip failed: got None")
            
    except Exception as e:
        print(f"   ❌ Round-trip failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try loading from the working test data
    print(f"\n2. Testing with working test data...")
    
    try:
        # Load some triples from the working test data
        working_triples = [
            ("http://vital.ai/haley.ai/chat-saas/KGEntity/test", "http://vital.ai/ontology/vital-core#hasName", "test entity"),
            ("http://vital.ai/haley.ai/chat-saas/KGEntity/test", "http://vital.ai/ontology/vital-core#vitaltype", "http://vital.ai/ontology/haley-ai-kg#KGEntity"),
            ("http://vital.ai/haley.ai/chat-saas/KGEntity/test", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://vital.ai/ontology/haley-ai-kg#KGEntity"),
            ("http://vital.ai/haley.ai/chat-saas/KGEntity/test", "http://vital.ai/ontology/vital-core#vital__hasOntologyIRI", "http://vital.ai/ontology/haley-ai-kg"),
            ("http://vital.ai/haley.ai/chat-saas/KGEntity/test", "http://vital.ai/ontology/vital-core#vital__hasVersionIRI", "0.1.0"),
        ]
        
        def working_triple_generator():
            for triple in working_triples:
                yield triple
        
        converted = vs.from_triples(working_triple_generator())
        
        if converted:
            print(f"   ✅ Working data conversion successful: {type(converted)}")
            print(f"      URI: {getattr(converted, 'URI', 'N/A')}")
            print(f"      Name: {getattr(converted, 'name', 'N/A')}")
        else:
            print(f"   ❌ Working data conversion returned None")
            
    except Exception as e:
        print(f"   ❌ Working data conversion failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_vitalsigns_conversion()
