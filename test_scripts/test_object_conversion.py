#!/usr/bin/env python3
"""
Test script for GraphObject <-> RDF conversion functionality.
Tests the object conversion methods in KGraphRDFDB and KGraph.
"""

import sys
import os
import warnings

# Suppress protobuf warnings
warnings.filterwarnings("ignore", message=".*protobuf.*")

# Add the parent directory to the path so we can import kgraphmemory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vital_ai_vitalsigns.vitalsigns import VitalSigns
from vital_ai_vitalsigns.embedding.embedding_model import EmbeddingModel
from ai_haley_kg_domain.model.KGEntity import KGEntity
from kgraphmemory.kgraph_memory import KGraphMemory


def test_rdf_object_conversion():
    """Test RDF <-> GraphObject conversion functionality."""
    
    print("=== Object Conversion Test Script ===\n")
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create embedding model
    try:
        embedding_model = EmbeddingModel()
    except Exception as e:
        print(f"Warning: EmbeddingModel initialization issue: {e}")
        embedding_model = EmbeddingModel()
    
    # Create KGraphMemory and KGraph
    print("1. Creating KGraphMemory and KGraph...")
    memory = KGraphMemory(embedding_model)
    graph = memory.create_kgraph("test_conversion", "http://example.com/graphs/test_conversion")
    
    # Create test entities
    print("\n2. Creating test KGEntity objects...")
    entities = []
    
    # Entity 1: Apple Inc.
    apple = KGEntity()
    apple.URI = "http://example.com/entities/apple"
    apple.name = "Apple Inc."
    apple.kGEntityTypeDescription = "technology corporation"
    apple.kGraphDescription = "Technology company that designs, develops, and sells consumer electronics, computer software, and online services"
    entities.append(apple)
    
    # Entity 2: Microsoft Corporation
    microsoft = KGEntity()
    microsoft.URI = "http://example.com/entities/microsoft"
    microsoft.name = "Microsoft Corporation"
    microsoft.kGEntityTypeDescription = "technology corporation"
    microsoft.kGraphDescription = "American multinational technology corporation that produces computer software, consumer electronics, and personal computers"
    entities.append(microsoft)
    
    print(f"   Created {len(entities)} test entities")
    
    # Test 1: Add objects to graph (GraphObject -> RDF conversion)
    print("\n3. Testing GraphObject -> RDF conversion...")
    for entity in entities:
        success = graph.add_object(entity)
        print(f"   Added {entity.name}: {success}")
    
    # Check RDF storage
    stats = graph.get_stats()
    print(f"   RDF triples stored: {stats['rdf_triple_count']}")
    print(f"   Vector records stored: {stats['vector_record_count']}")
    
    # Test 2: Direct RDF database object retrieval
    print("\n4. Testing RDF database object conversion...")
    for entity in entities:
        uri = str(entity.URI)
        print(f"   Testing conversion for: {uri}")
        
        # Test direct RDF database conversion
        converted_object = graph.rdf_store.get_graph_object(uri, graph.graph_uri)
        
        if converted_object:
            print(f"   ✅ Successfully converted: {converted_object.name}")
            print(f"      Type: {converted_object.get_class_uri()}")
            print(f"      URI: {converted_object.URI}")
            desc = getattr(converted_object, 'kGraphDescription', 'N/A')
            desc_str = str(desc)[:50] + "..." if len(str(desc)) > 50 else str(desc)
            print(f"      Description: {desc_str}")
        else:
            print(f"   ❌ Failed to convert object for URI: {uri}")
    
    # Test 3: KGraph object retrieval (delegated to RDF database)
    print("\n5. Testing KGraph object retrieval...")
    for entity in entities:
        uri = str(entity.URI)
        print(f"   Retrieving via KGraph: {uri}")
        
        retrieved_object = graph.get_object(uri)
        
        if retrieved_object:
            print(f"   ✅ Successfully retrieved: {retrieved_object.name}")
            print(f"      Type: {retrieved_object.get_class_uri()}")
            print(f"      Original URI: {entity.URI}")
            print(f"      Retrieved URI: {retrieved_object.URI}")
            
            # Compare properties
            original_dict = entity.to_dict()
            retrieved_dict = retrieved_object.to_dict()
            
            print(f"      Property comparison:")
            print(f"         Original properties: {len(original_dict)}")
            print(f"         Retrieved properties: {len(retrieved_dict)}")
            
            # Check key properties
            key_props = ['URI', 'type', 'http://vital.ai/ontology/vital-core#hasName']
            for prop in key_props:
                if prop in original_dict and prop in retrieved_dict:
                    # Convert both to strings for comparison
                    orig_val = str(original_dict[prop]).strip('"').strip("'")
                    retr_val = str(retrieved_dict[prop]).strip('"').strip("'")
                    match = orig_val == retr_val
                    print(f"         {prop}: {'✅' if match else '❌'} ({orig_val} vs {retr_val})")
        else:
            print(f"   ❌ Failed to retrieve object for URI: {uri}")
    
    # Test 4: Bulk object retrieval
    print("\n6. Testing bulk object retrieval...")
    all_uris = [str(entity.URI) for entity in entities]
    retrieved_objects = graph.get_object_list(all_uris)
    
    print(f"   Requested {len(all_uris)} objects")
    print(f"   Retrieved {len(retrieved_objects)} objects")
    
    for obj in retrieved_objects:
        print(f"   ✅ Retrieved: {obj.name} ({obj.URI})")
    
    # Test 5: Round-trip conversion test
    print("\n7. Testing round-trip conversion...")
    for entity in entities:
        uri = str(entity.URI)
        print(f"   Round-trip test for: {entity.name}")
        
        # Original -> RDF -> GraphObject
        retrieved = graph.get_object(uri)
        
        if retrieved:
            # Compare key properties with proper string normalization
            original_name = getattr(entity, 'name', None)
            retrieved_name = getattr(retrieved, 'name', None)
            
            original_desc = getattr(entity, 'kGraphDescription', None)
            retrieved_desc = getattr(retrieved, 'kGraphDescription', None)
            
            # Normalize strings by removing quotes and converting to string
            def normalize_value(val):
                if val is None:
                    return None
                return str(val).strip('"').strip("'")
            
            norm_orig_name = normalize_value(original_name)
            norm_retr_name = normalize_value(retrieved_name)
            norm_orig_desc = normalize_value(original_desc)
            norm_retr_desc = normalize_value(retrieved_desc)
            
            name_match = norm_orig_name == norm_retr_name
            desc_match = norm_orig_desc == norm_retr_desc
            uri_match = str(entity.URI) == str(retrieved.URI)
            
            print(f"      Name: {'✅' if name_match else '❌'} ({norm_orig_name} -> {norm_retr_name})")
            print(f"      Description: {'✅' if desc_match else '❌'}")
            print(f"      URI: {'✅' if uri_match else '❌'}")
            
            if name_match and desc_match and uri_match:
                print(f"   ✅ Round-trip successful for {entity.name}")
            else:
                print(f"   ❌ Round-trip failed for {entity.name}")
        else:
            print(f"   ❌ Could not retrieve object for round-trip test")
    
    # Test 6: RDF triples inspection and debugging
    print("\n8. Inspecting RDF triples and debugging conversion...")
    for entity in entities:
        uri = str(entity.URI)
        triples = graph.rdf_store.get_triples(subject=uri, graph=graph.graph_uri)
        print(f"   {entity.name}: {len(triples)} triples")
        
        # Show ALL triples for debugging
        for i, (s, p, o, g) in enumerate(triples):
            predicate_short = p.split('#')[-1] if '#' in p else p.split('/')[-1]
            object_short = o[:50] + "..." if len(str(o)) > 50 else o
            print(f"      {i+1}. {predicate_short}: {object_short}")
        
        # Test VitalSigns conversion directly using the same logic as the working method
        print(f"   Testing VitalSigns conversion for {entity.name}:")
        try:
            from rdflib import URIRef, Literal, BNode
            
            def triple_generator():
                for subject, predicate, obj, graph_name in triples:
                    print(f"      Triple: ({subject}, {predicate}, {obj})")
                    
                    # Apply the same conversion logic as in KGraphRDFDB.get_graph_object
                    # Clean all URI strings by removing angle brackets
                    clean_subject = subject.strip('<>')
                    clean_predicate = predicate.strip('<>')
                    clean_obj = obj.strip('<>')
                    
                    # Convert subject to proper RDFLib object
                    if clean_subject.startswith('_:'):
                        rdf_subject = BNode(clean_subject[2:])
                    else:
                        rdf_subject = URIRef(clean_subject)
                    
                    # Convert predicate to URIRef
                    rdf_predicate = URIRef(clean_predicate)
                    
                    # Convert object to proper RDFLib object
                    if clean_obj.startswith('_:'):
                        rdf_object = BNode(clean_obj[2:])
                    elif clean_obj.startswith('http://') or clean_obj.startswith('https://'):
                        rdf_object = URIRef(clean_obj)
                    else:
                        # Literal value - strip quotes if present
                        clean_literal = clean_obj.strip('"').strip("'")
                        rdf_object = Literal(clean_literal)
                    
                    yield (rdf_subject, rdf_predicate, rdf_object)
            
            vs = VitalSigns()
            converted = vs.from_triples(triple_generator())
            
            if converted:
                print(f"   ✅ VitalSigns conversion successful: {type(converted)}")
                print(f"      URI: {getattr(converted, 'URI', 'N/A')}")
                print(f"      Name: {getattr(converted, 'name', 'N/A')}")
            else:
                print(f"   ❌ VitalSigns conversion returned None")
                
        except Exception as e:
            print(f"   ❌ VitalSigns conversion failed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== Object Conversion Test Complete ===")
    print(f"Summary:")
    print(f"  - Created {len(entities)} test entities")
    print(f"  - Stored {stats['rdf_triple_count']} RDF triples")
    print(f"  - Tested RDF database conversion")
    print(f"  - Tested KGraph object retrieval")
    print(f"  - Tested bulk retrieval")
    print(f"  - Tested round-trip conversion")
    print(f"  - All RDF-specific code contained in KGraphRDFDB")


if __name__ == "__main__":
    test_rdf_object_conversion()
