# API Reference

## KGraphMemory Class

The main manager class for handling multiple knowledge graphs.

### Constructor

```python
KGraphMemory(embedding_model, default_vector_mappings=None)
```

**Parameters:**
- `embedding_model`: SentenceTransformer or compatible embedding model
- `default_vector_mappings`: Optional dict of default vector property mappings

### Methods

#### create_kgraph(graph_id, graph_uri, custom_vector_mappings=None)
Creates a new knowledge graph instance.

**Parameters:**
- `graph_id`: Unique string identifier for the graph
- `graph_uri`: URI for the named graph in RDF store
- `custom_vector_mappings`: Optional custom mappings for this graph

**Returns:** KGraph instance

#### get_kgraph(graph_id)
Retrieves an existing knowledge graph by ID.

**Returns:** KGraph instance or None

#### remove_kgraph(graph_id)
Removes and cleans up a knowledge graph.

#### list_kgraphs()
Returns list of all graph IDs.

#### has_kgraph(graph_id)
Checks if a graph exists.

**Returns:** Boolean

#### search_across_kgraphs(query, vector_id="general", limit=10)
Searches across all knowledge graphs.

**Parameters:**
- `query`: Search query string
- `vector_id`: Vector type to search ("general", "type", "description", "content")
- `limit`: Maximum number of results

**Returns:** List of search results with graph_id and scores

#### sparql_query_across_kgraphs(sparql_query)
Executes SPARQL query across all graphs.

**Returns:** Combined query results

#### clear_all()
Removes all knowledge graphs and cleans up resources.

## KGraph Class

Individual knowledge graph with dual RDF/Vector storage.

### Constructor

```python
KGraph(graph_id, embedding_model, graph_uri, vector_mappings=None)
```

### Core Operations

#### add_object(graph_object)
Adds a knowledge object to both RDF and vector stores.

**Parameters:**
- `graph_object`: VITAL_Node or VITAL_Edge instance

#### get_object(uri)
Retrieves object by URI from RDF store.

**Returns:** Graph object or None

#### update_object(graph_object)
Updates existing object in both stores.

#### delete_object(uri)
Removes object from both stores.

#### object_exists(uri)
Checks if object exists.

**Returns:** Boolean

### Query Operations

#### sparql_query(query)
Executes SPARQL query on RDF store.

**Parameters:**
- `query`: SPARQL query string

**Returns:** Query results

#### vector_search(query, vector_id="general", limit=10, filters=None)
Performs vector similarity search.

**Parameters:**
- `query`: Search query string
- `vector_id`: Vector type to search
- `limit`: Maximum results
- `filters`: Optional metadata filters

**Returns:** List of results with URIs and scores

#### vector_search_by_type(query, vector_id, limit=10)
Searches specific vector type.

#### hybrid_search(query, sparql_filter=None, vector_filters=None, limit=10)
Combines SPARQL filtering with vector search.

**Parameters:**
- `query`: Search query
- `sparql_filter`: Optional SPARQL WHERE clause
- `vector_filters`: Optional vector metadata filters
- `limit`: Maximum results

**Returns:** Ranked results combining both approaches

### Vector Operations

#### get_object_vectors(uri)
Gets all vectors for an object.

**Returns:** Dict mapping vector_id to vector data

#### get_available_vector_types_for_object(graph_object)
Gets available vector types for object type.

**Returns:** List of vector_id strings

### Statistics

#### get_statistics()
Returns graph statistics including triple count, vector count, etc.

## KGraphRDFDB Class

RDF triple store interface using pyoxigraph.

### Methods

#### add_triple(subject, predicate, object, graph_uri=None)
Adds RDF triple to store.

#### get_triples(subject=None, predicate=None, object=None)
Retrieves matching triples.

#### sparql_select(query)
Executes SPARQL SELECT query.

#### sparql_construct(query)
Executes SPARQL CONSTRUCT query.

#### sparql_ask(query)
Executes SPARQL ASK query.

#### bulk_load_file(file_path, format="turtle")
Bulk loads RDF file.

## KGraphVectorDB Class

Vector database interface using Qdrant.

### Methods

#### add_vector(vector_id, vector, metadata=None)
Adds vector with metadata.

#### search_vectors(query_vector, limit=10, filters=None)
Searches for similar vectors.

#### get_vector(vector_id)
Retrieves vector by ID.

#### delete_vector(vector_id)
Removes vector.

#### batch_add_vectors(vectors_data)
Adds multiple vectors efficiently.

## Utility Functions

### URI Generation

```python
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator

uri = URIGenerator.generate_uri()
```

### Vector Mapping Configuration

```python
vector_mappings = {
    "KGEntity": {
        "type": ["hasKGEntityType"],
        "description": ["hasKGEntityDescription"],
        "general": ["hasName", "hasKGEntityDescription"]
    },
    "KGDocument": {
        "content": ["hasKGDocumentContent"],
        "description": ["hasKGDocumentDescription"],
        "general": ["hasName", "hasKGDocumentContent"]
    }
}
```

## Error Handling

### Common Exceptions

- `ValueError`: Invalid parameters or configuration
- `KeyError`: Missing graph IDs or vector types
- `RuntimeError`: Storage backend errors
- `TypeError`: Invalid object types

### Best Practices

1. Always check if graphs exist before operations
2. Handle embedding model failures gracefully
3. Use try-catch for SPARQL query errors
4. Monitor memory usage for large datasets
5. Clean up resources with clear_all() when done
