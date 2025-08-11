#!/usr/bin/env python3
"""
Test script for KGEntity functionality with KGraphBridge architecture.
Demonstrates creating entities, storing them via bridges, and performing SPARQL and vector queries.
"""

import sys
import warnings
import os
from typing import List, Dict, Any
from datetime import datetime

# Add the parent directory to the path to import kgraphmemory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vital_ai_vitalsigns.embedding.embedding_model import EmbeddingModel
from vital_ai_vitalsigns.vitalsigns import VitalSigns

# Import existing KGEntity class
from ai_haley_kg_domain.model.KGEntity import KGEntity

# Import our KGraph components with new bridge architecture
from kgraphmemory.kgraph_memory import KGraphMemory
from kgraphmemory.kgraph_bridge import KGraphBridge


def create_test_entities() -> List[KGEntity]:
    """Create a diverse set of test entities for similarity testing."""
    
    entities = []
    
    # Technology Companies
    apple = KGEntity()
    apple.URI = "http://example.com/entities/apple"
    apple.name = "Apple Inc."
    apple.kGraphDescription = "Technology company that designs, develops, and sells consumer electronics, computer software, and online services"
    apple.kGEntityTypeDescription = "technology corporation"
    entities.append(apple)
    
    google = KGEntity()
    google.URI = "http://example.com/entities/google"
    google.name = "Google LLC"
    google.kGraphDescription = "Multinational technology company specializing in Internet-related services and products"
    google.kGEntityTypeDescription = "technology corporation"
    entities.append(google)
    
    microsoft = KGEntity()
    microsoft.URI = "http://example.com/entities/microsoft"
    microsoft.name = "Microsoft Corporation"
    microsoft.kGraphDescription = "American multinational technology corporation that produces computer software, consumer electronics, and personal computers"
    microsoft.kGEntityTypeDescription = "technology corporation"
    entities.append(microsoft)
    
    # People
    jobs = KGEntity()
    jobs.URI = "http://example.com/entities/steve_jobs"
    jobs.name = "Steve Jobs"
    jobs.kGraphDescription = "American business magnate, industrial designer, investor, and media proprietor who was the co-founder and CEO of Apple Inc."
    jobs.kGEntityTypeDescription = "person"
    entities.append(jobs)
    
    gates = KGEntity()
    gates.URI = "http://example.com/entities/bill_gates"
    gates.name = "Bill Gates"
    gates.kGraphDescription = "American business magnate, software developer, investor, and philanthropist who co-founded Microsoft Corporation"
    gates.kGEntityTypeDescription = "person"
    entities.append(gates)
    
    # Locations
    cupertino = KGEntity()
    cupertino.URI = "http://example.com/entities/cupertino"
    cupertino.name = "Cupertino"
    cupertino.kGraphDescription = "City in Santa Clara County, California, known as the headquarters location of Apple Inc."
    cupertino.kGEntityTypeDescription = "city"
    entities.append(cupertino)
    
    seattle = KGEntity()
    seattle.URI = "http://example.com/entities/seattle"
    seattle.name = "Seattle"
    seattle.kGraphDescription = "Seaport city in Washington state, home to major technology companies including Microsoft and Amazon"
    seattle.kGEntityTypeDescription = "city"
    entities.append(seattle)
    
    # Products
    iphone = KGEntity()
    iphone.URI = "http://example.com/entities/iphone"
    iphone.name = "iPhone"
    iphone.kGraphDescription = "Line of smartphones designed and marketed by Apple Inc. that use Apple's iOS mobile operating system"
    iphone.kGEntityTypeDescription = "consumer product"
    entities.append(iphone)
    
    windows = KGEntity()
    windows.URI = "http://example.com/entities/windows"
    windows.name = "Microsoft Windows"
    windows.kGraphDescription = "Group of several proprietary graphical operating system families developed and marketed by Microsoft"
    windows.kGEntityTypeDescription = "software product"
    entities.append(windows)
    
    # AI/ML Related
    chatgpt = KGEntity()
    chatgpt.URI = "http://example.com/entities/chatgpt"
    chatgpt.name = "ChatGPT"
    chatgpt.kGraphDescription = "Artificial intelligence chatbot developed by OpenAI that uses natural language processing to engage in conversational dialogue"
    chatgpt.kGEntityTypeDescription = "artificial intelligence system"
    entities.append(chatgpt)
    
    return entities


def print_results(results: List[Dict[str, Any]], title: str, limit: int = 10):
    """Print formatted search results."""
    print(f"\n=== {title} ===")
    print(f"Total Results: {len(results)}")
    print("-" * 60)
    
    for i, result in enumerate(results[:limit]):
        score = result.get('score', 'N/A')
        if isinstance(score, (int, float)):
            print(f"{i+1}. Score: {score:.4f}")
        else:
            print(f"{i+1}. Score: {score}")
        
        # Extract URI from different possible locations
        uri = result.get('uri')  # For SPARQL results
        if not uri:
            uri = result.get('subject')  # Alternative for SPARQL results
        if not uri:
            uri = result.get('?subject')  # SPARQL results with ? prefix
        if not uri and 'metadata' in result:
            uri = result['metadata'].get('uri')  # For vector search results
        
        print(f"   URI: {uri if uri else 'N/A'}")
        
        if 'vector_id' in result:
            print(f"   Vector ID: {result['vector_id']}")
        elif 'metadata' in result and 'vector_id' in result['metadata']:
            print(f"   Vector ID: {result['metadata']['vector_id']}")
        # Print some metadata
        for key, value in result.items():
            if key not in ['uri', 'score', 'vector_id', 'subject'] and value:
                print(f"   {key}: {value}")
        print()


def main():
    """Main test function demonstrating KGraphBridge functionality."""
    
    print("=== KGEntity and KGraphBridge Test Script ===\n")
    
    # Initialize VitalSigns (required for VITAL objects)
    vs = VitalSigns()
    
    # Create actual embedding model (same as working test)
    try:
        embedding_model = EmbeddingModel()
    except Exception as e:
        print(f"Warning: EmbeddingModel initialization issue: {e}")
        print("Continuing with default initialization...")
        embedding_model = EmbeddingModel()
    
    # Create KGraphMemory
    print("1. Creating KGraphMemory...")
    memory = KGraphMemory(embedding_model)
    
    # Create a KGraphBridge (updated architecture)
    print("2. Creating KGraphBridge...")
    bridge = memory.create_kgraph_bridge(
        graph_id="test_entities",
        graph_uri="http://example.com/graphs/test_entities"
    )
    
    # Create and store test entities using bridge
    print("3. Creating and storing test entities via bridge...")
    entities = create_test_entities()
    
    # Store entities using the bridge's entity management
    for entity in entities:
        success = bridge.add_object(entity)
        print(f"   Added entity: {entity.name} ({entity.kGEntityTypeDescription}) - Success: {success}")
    
    # Get statistics
    print(f"\n4. Bridge Statistics:")
    stats = bridge.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test SPARQL queries via bridge
    print(f"\n5. Testing SPARQL Queries via Bridge:")
    
    # Get the graph URI for named graph queries
    graph_uri = bridge.get_graph_uri()
    
    # First, let's see what's actually in the RDF store (query named graph)
    debug_query = f"""
    SELECT ?subject ?predicate ?object WHERE {{
        GRAPH <{graph_uri}> {{
            ?subject ?predicate ?object .
        }}
    }} LIMIT 10
    """
    
    debug_results = bridge.sparql_query(debug_query)
    print_results(debug_results, "First 10 RDF triples (debug)")
    
    # Query for all type triples to see what class URIs are used
    type_query = f"""
    SELECT ?subject ?type WHERE {{
        GRAPH <{graph_uri}> {{
            ?subject <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
        }}
    }}
    """
    
    type_results = bridge.sparql_query(type_query)
    print_results(type_results, "All type triples")
    
    # Query for all entities (updated based on what we find)
    sparql_query1 = f"""
    SELECT ?subject ?predicate ?object WHERE {{
        GRAPH <{graph_uri}> {{
            ?subject ?predicate ?object .
            ?subject <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
            FILTER(CONTAINS(STR(?type), "KGEntity"))
        }}
    }} LIMIT 10
    """
    
    sparql_results1 = bridge.sparql_query(sparql_query1)
    print_results(sparql_results1, "All KGEntity triples")
    
    # Query for technology corporations (should work now with fixed RDF storage)
    sparql_query2 = f"""
    SELECT ?subject ?name WHERE {{
        GRAPH <{graph_uri}> {{
            ?subject <http://vital.ai/ontology/haley-ai-kg#hasKGEntityTypeDescription> "technology corporation" .
            ?subject <http://vital.ai/ontology/vital-core#hasName> ?name .
        }}
    }}
    """
    
    # Alternative query in case the property URIs are different
    sparql_query2_alt = f"""
    SELECT ?subject ?predicate ?object WHERE {{
        GRAPH <{graph_uri}> {{
            ?subject ?predicate ?object .
            FILTER(CONTAINS(STR(?object), "technology corporation"))
        }}
    }} LIMIT 5
    """
    
    sparql_results2 = bridge.sparql_query(sparql_query2)
    print_results(sparql_results2, "Technology corporations")
    
    # Always run the alternative query to debug
    sparql_results2_alt = bridge.sparql_query(sparql_query2_alt)
    print_results(sparql_results2_alt, "Technology corporations (alternative query - debug)")
    
    # Test Vector Searches via Bridge
    print(f"\n6. Testing Vector Searches via Bridge:")
    
    # Search by entity type
    print("\n--- Searching by Entity Type ---")
    type_results1 = bridge.vector_search_by_type("technology company", "entity_type", limit=5)
    print_results(type_results1, "Entity Type Search: 'technology company'")
    
    type_results2 = bridge.vector_search_by_type("person", "entity_type", limit=5)
    print_results(type_results2, "Entity Type Search: 'person'")
    
    # Search by entity value
    print("\n--- Searching by Entity Value ---")
    value_results1 = bridge.vector_search_by_type("Apple computer company", "entity_value", limit=5)
    print_results(value_results1, "Entity Value Search: 'Apple computer company'")
    
    value_results2 = bridge.vector_search_by_type("artificial intelligence", "entity_value", limit=5)
    print_results(value_results2, "Entity Value Search: 'artificial intelligence'")
    
    # General vector search (across all vectors)
    print("\n--- General Vector Search ---")
    general_results = bridge.vector_search("Microsoft software", limit=5)
    print_results(general_results, "General Vector Search: 'Microsoft software'")
    
    # Test cross-graph search via memory
    print(f"\n7. Testing Cross-Graph Search via Memory:")
    cross_results = memory.search_across_kgraphs("technology", limit_per_graph=3)
    
    for graph_id, results in cross_results.items():
        print_results(results, f"Cross-Graph Search in '{graph_id}': 'technology'", limit=3)
    
    # Memory statistics
    print(f"\n8. Memory Statistics:")
    memory_stats = memory.get_memory_stats()
    for key, value in memory_stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n=== Test Complete ===")
    print(f"Successfully demonstrated:")
    print(f"  - KGEntity creation and property setting")
    print(f"  - KGraphMemory and KGraphBridge integration")
    print(f"  - Multi-vector storage (entity_type and entity_value)")
    print(f"  - SPARQL queries on RDF store via bridge")
    print(f"  - Vector similarity searches by type via bridge")
    print(f"  - Cross-graph search capabilities")
    print(f"  - Search result containers with similarity scores")


if __name__ == "__main__":
    main()
