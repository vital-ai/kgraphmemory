#!/usr/bin/env python3
"""
Debug script to understand RDF.type comparison issue.
"""

import sys
import os

# Add the parent directory to the path so we can import kgraphmemory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rdflib import RDF
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from ai_haley_kg_domain.model.KGEntity import KGEntity

def debug_rdf_type():
    """Debug RDF.type comparison issue."""
    
    print("=== RDF.type Debug ===\n")
    
    print("1. Checking RDF.type:")
    print(f"   RDF.type: {RDF.type}")
    print(f"   RDF.type type: {type(RDF.type)}")
    print(f"   RDF.type str: '{str(RDF.type)}'")
    
    print("\n2. Testing string comparison:")
    rdf_type_string = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    print(f"   String: '{rdf_type_string}'")
    print(f"   RDF.type == string: {RDF.type == rdf_type_string}")
    print(f"   str(RDF.type) == string: {str(RDF.type) == rdf_type_string}")
    
    print("\n3. Testing VitalSigns to_triples output:")
    entity = KGEntity()
    entity.URI = "http://example.com/entities/test"
    entity.name = "Test Entity"
    
    vs = VitalSigns()
    triples = vs.to_triples(entity)
    
    print("   VitalSigns generated triples:")
    for i, (s, p, o) in enumerate(triples):
        print(f"     {i+1}. Subject: {s} (type: {type(s)})")
        print(f"        Predicate: {p} (type: {type(p)})")
        print(f"        Object: {o} (type: {type(o)})")
        print(f"        Predicate == RDF.type: {p == RDF.type}")
        print(f"        str(Predicate) == str(RDF.type): {str(p) == str(RDF.type)}")
        print()


if __name__ == "__main__":
    debug_rdf_type()
