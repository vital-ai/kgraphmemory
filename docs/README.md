# KGraphMemory Documentation

Comprehensive documentation for the KGraphMemory in-memory knowledge graph system designed for AI agents.

## Overview

KGraphMemory is a sophisticated in-memory knowledge graph implementation that enables AI agents to store, manage, and query structured knowledge during interactions with people and task execution. The system combines the power of semantic web technologies with modern vector databases to provide both symbolic reasoning and semantic similarity capabilities.

## Core Components

### KGraphMemory (Manager)
The central management system that:
- Manages multiple knowledge graphs with shared embedding models
- Provides cross-graph search and query capabilities
- Handles resource management and cleanup
- Coordinates operations across multiple KGraph instances

### KGraph (Individual Knowledge Graph)
Each knowledge graph instance provides:
- Dual storage architecture (RDF + Vector)
- CRUD operations for knowledge objects
- Hybrid search capabilities
- Multi-vector support for different semantic aspects

### Storage Backends

#### KGraphRDFDB (Semantic Store)
- **Technology**: pyoxigraph (Rust-based RDF store)
- **Purpose**: SPARQL queries, semantic reasoning, relationship traversal
- **Features**: Named graph support, full SPARQL 1.1 compliance, high performance

#### KGraphVectorDB (Similarity Store)
- **Technology**: Qdrant (vector database)
- **Purpose**: Semantic similarity search, embedding-based retrieval
- **Features**: Multi-vector support, metadata filtering, efficient similarity search

## Ontology Foundation

### Haley AI Knowledge Graph Ontology
The system is built on the `haley-ai-kg-0.1.0.owl` ontology which defines:

- **Core Classes**: KGEntity, KGFrame, KGDocument, KGAgent, KGActor, etc.
- **Edge Relationships**: Type-safe connections with source/destination constraints
- **Vectorization Annotations**: `isVectorized` and `isVectorizedType` properties
- **Semantic Structure**: Comprehensive taxonomy for AI agent knowledge

### VitalSigns Integration
The VitalSigns library provides:
- OWL ontology parsing and validation
- Automatic Python class generation from OWL definitions
- Type-safe object creation and manipulation
- Semantic web standards compliance

## Multi-Vector Architecture

### Vector Types
Each knowledge object can have multiple semantic vectors:
- **type**: Vector representing the object's type/category
- **description**: Vector for descriptive content
- **content**: Vector for main content/body
- **general**: Fallback vector for general representation

### Vector Mappings
Configurable mappings define which properties contribute to each vector type:
```python
{
    "KGEntity": {
        "type": ["hasKGEntityType"],
        "description": ["hasKGEntityDescription"],
        "general": ["hasName", "hasKGEntityDescription"]
    }
}
```

## Key Features for AI Agents

### Context Preservation
- Maintain conversation context across interactions
- Store procedural knowledge for task execution
- Track entity relationships and dependencies

### Semantic Understanding
- Natural language query processing
- Similarity-based knowledge retrieval
- Multi-modal knowledge representation

### Real-time Operations
- Dynamic knowledge updates during agent interactions
- Efficient in-memory operations (<1M records optimized)
- Synchronized dual-store architecture

### Query Capabilities
- **SPARQL Queries**: Complex relationship traversal and reasoning
- **Vector Search**: Semantic similarity and content retrieval
- **Hybrid Search**: Combined SPARQL filtering with vector similarity
- **Cross-Graph Search**: Query across multiple knowledge graphs

## Performance Characteristics

### Optimized for AI Agents
- **Scale**: Designed for <1M records per graph
- **Latency**: In-memory operations for sub-millisecond response
- **Throughput**: Bulk loading support for large datasets
- **Memory**: Efficient storage with configurable limits

### Benchmarks
- **RDF Loading**: 500K+ triples/second (bulk load)
- **SPARQL Queries**: 0.1-0.8 seconds for complex queries
- **Vector Search**: Sub-millisecond similarity search
- **Hybrid Operations**: Combined queries in milliseconds

## Use Cases

### Conversational AI
- Store conversation history and context
- Maintain user preferences and profiles
- Track topic evolution and relationships

### Task-Oriented Agents
- Store procedural knowledge and workflows
- Maintain task dependencies and requirements
- Track progress and intermediate results

### Knowledge Management
- Organize structured information repositories
- Enable semantic search and discovery
- Support knowledge graph construction and maintenance

### Multi-Agent Systems
- Share knowledge across agent instances
- Coordinate collaborative tasks
- Maintain distributed knowledge consistency

## Getting Started

Refer to the main [README](../README.md) for installation and basic usage examples.

For detailed information, see the specific documentation sections:
- [API Reference](api-reference.md) - Complete API documentation
- [Ontology Structure](ontology-structure.md) - Understanding the knowledge model
- [Vector Mappings](vector-mappings.md) - Configuring semantic vectors
- [SPARQL Examples](sparql-examples.md) - Query patterns and examples
- [Integration Patterns](integration-patterns.md) - Common usage patterns
- [Performance Guide](performance-guide.md) - Optimization and tuning