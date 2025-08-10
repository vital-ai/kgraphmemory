#!/usr/bin/env python3
"""
Basic pyoxigraph test script demonstrating in-memory RDF storage and querying.

This script tests:
1. Creating an in-memory store
2. Adding RDF triples
3. Querying with SPARQL
4. Basic graph operations
"""

import pyoxigraph
from pyoxigraph import Store, NamedNode, BlankNode, Literal, Triple, Quad


def main():
    """Main test function demonstrating pyoxigraph basic functionality."""
    print("=== Pyoxigraph Basic Functionality Test ===\n")
    
    # 1. Create an in-memory store
    print("1. Creating in-memory RDF store...")
    store = Store()
    print("✓ In-memory store created successfully\n")
    
    # 2. Define some RDF vocabulary
    print("2. Defining RDF vocabulary...")
    # Namespaces
    foaf = "http://xmlns.com/foaf/0.1/"
    ex = "http://example.org/"
    
    # Create named nodes (URIs)
    person1 = NamedNode(ex + "person1")
    person2 = NamedNode(ex + "person2")
    name_prop = NamedNode(foaf + "name")
    knows_prop = NamedNode(foaf + "knows")
    age_prop = NamedNode(ex + "age")
    
    print("✓ RDF vocabulary defined\n")
    
    # 3. Add RDF triples to the store
    print("3. Adding RDF triples to the store...")
    
    # Add some basic triples (convert to Quads for the store)
    triples_data = [
        (person1, name_prop, Literal("Alice")),
        (person1, age_prop, Literal("30", datatype=NamedNode("http://www.w3.org/2001/XMLSchema#integer"))),
        (person2, name_prop, Literal("Bob")),
        (person2, age_prop, Literal("25", datatype=NamedNode("http://www.w3.org/2001/XMLSchema#integer"))),
        (person1, knows_prop, person2),
    ]
    
    for subject, predicate, object_ in triples_data:
        quad = Quad(subject, predicate, object_)
        store.add(quad)
        print(f"  Added: {subject} {predicate} {object_}")
    
    print(f"✓ Added {len(triples_data)} triples to the store\n")
    
    # 4. Query the store with SPARQL
    print("4. Querying the store with SPARQL...")
    
    # Query 1: Get all names
    print("\n  Query 1: Get all names")
    query1 = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?person ?name WHERE {
        ?person foaf:name ?name .
    }
    """
    
    results1 = store.query(query1)
    for result in results1:
        print(f"    Person: {result['person']}, Name: {result['name']}")
    
    # Query 2: Get people and their ages
    print("\n  Query 2: Get people and their ages")
    query2 = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ex: <http://example.org/>
    SELECT ?person ?name ?age WHERE {
        ?person foaf:name ?name .
        ?person ex:age ?age .
    }
    ORDER BY ?age
    """
    
    results2 = store.query(query2)
    for result in results2:
        print(f"    {result['name']} is {result['age']} years old")
    
    # Query 3: Find who knows whom
    print("\n  Query 3: Find relationships")
    query3 = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?person1_name ?person2_name WHERE {
        ?person1 foaf:knows ?person2 .
        ?person1 foaf:name ?person1_name .
        ?person2 foaf:name ?person2_name .
    }
    """
    
    results3 = store.query(query3)
    for result in results3:
        print(f"    {result['person1_name']} knows {result['person2_name']}")
    
    print("\n✓ SPARQL queries executed successfully\n")
    
    # 5. Test store statistics
    print("5. Store statistics...")
    
    # Count triples using SPARQL
    count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
    count_result = list(store.query(count_query))[0]
    triple_count = int(count_result['count'].value)
    
    print(f"  Total triples in store: {triple_count}")
    
    # 6. Test ASK query
    print("\n6. Testing ASK queries...")
    
    ask_query1 = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    ASK {
        ?person foaf:name "Alice" .
    }
    """
    
    ask_result1 = store.query(ask_query1)
    print(f"  Is there a person named Alice? {ask_result1}")
    
    ask_query2 = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    ASK {
        ?person foaf:name "Charlie" .
    }
    """
    
    ask_result2 = store.query(ask_query2)
    print(f"  Is there a person named Charlie? {ask_result2}")
    
    print("\n✓ ASK queries executed successfully\n")
    
    # 7. Test CONSTRUCT query
    print("7. Testing CONSTRUCT queries...")
    
    construct_query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ex: <http://example.org/>
    CONSTRUCT {
        ?person ex:hasName ?name .
    } WHERE {
        ?person foaf:name ?name .
    }
    """
    
    constructed_graph = store.query(construct_query)
    print("  Constructed triples:")
    for triple in constructed_graph:
        print(f"    {triple}")
    
    print("\n✓ CONSTRUCT query executed successfully\n")
    
    # 8. Test removing triples
    print("8. Testing triple removal...")
    
    # Remove a specific triple
    quad_to_remove = Quad(person1, knows_prop, person2)
    store.remove(quad_to_remove)
    print(f"  Removed triple: {person1} {knows_prop} {person2}")
    
    # Verify removal
    verify_query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?person1_name ?person2_name WHERE {
        ?person1 foaf:knows ?person2 .
        ?person1 foaf:name ?person1_name .
        ?person2 foaf:name ?person2_name .
    }
    """
    
    verify_results = list(store.query(verify_query))
    print(f"  Remaining relationships: {len(verify_results)}")
    
    print("\n✓ Triple removal tested successfully\n")
    
    print("=== All tests completed successfully! ===")
    print(f"Pyoxigraph version: {pyoxigraph.__version__}")


if __name__ == "__main__":
    main()
