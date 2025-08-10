# KGraphMemory

An in-memory knowledge graph system designed for AI agents to store, manage, and query structured knowledge during interactions with people and task execution.

## Overview

KGraphMemory provides a high-performance, in-memory knowledge graph implementation that combines RDF triple stores with vector databases to enable AI agents to:

- Store and retrieve structured knowledge using semantic web standards
- Perform vector-based similarity search for semantic understanding
- Maintain context and relationships across agent interactions
- Execute complex SPARQL queries on knowledge representations
- Support multi-vector embeddings for different semantic aspects

## Key Features

### Dual Storage Architecture
- **RDF Store**: Uses pyoxigraph for fast SPARQL queries and semantic reasoning
- **Vector Store**: Uses Qdrant for similarity search and semantic retrieval
- **Synchronized Operations**: Automatic synchronization between stores

### Ontology-Driven Design
- Built on the Haley AI Knowledge Graph ontology (`haley-ai-kg-0.1.0.owl`)
- Uses VitalSigns library for OWL parsing and Python class generation
- Type-safe edge relationships with source/destination constraints
- Support for vectorization annotations (`isVectorized`, `isVectorizedType`)

### Multi-Vector Support
- Multiple semantic vectors per object (type, description, content, general)
- Configurable vector mappings for different object types
- Precise semantic search across different vector types

### Agent-Centric Features
- **KGraphMemory**: Manages multiple knowledge graphs with shared embedding models
- **Cross-graph operations**: Search and query across multiple knowledge graphs
- **Real-time updates**: Dynamic knowledge updates during agent interactions
- **Efficient querying**: Hybrid search combining SPARQL and vector similarity

## Architecture

```
KGraphMemory (Manager)
├── KGraph (Individual Knowledge Graph)
│   ├── KGraphRDFDB (pyoxigraph)
│   ├── KGraphVectorDB (Qdrant)
│   └── Vector Mappings
├── Shared Embedding Model
└── Cross-Graph Operations
```

## Use Cases

- **Conversational AI**: Maintain context and knowledge across chat interactions
- **Task Execution**: Store and retrieve procedural knowledge for agent tasks
- **Knowledge Management**: Organize and query structured information
- **Semantic Search**: Find relevant information using natural language queries
- **Relationship Modeling**: Represent complex entity relationships and dependencies

## Getting Started

```python
from kgraphmemory import KGraphMemory
from sentence_transformers import SentenceTransformer

# Initialize with embedding model
embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
memory = KGraphMemory(embedding_model)

# Create a knowledge graph
graph = memory.create_kgraph("agent_kb", "http://example.org/agent")

# Add knowledge objects
graph.add_object(entity)

# Search across graphs
results = memory.search_across_kgraphs("find information about...")
```

## Documentation

See the [docs](docs/) directory for detailed documentation on:
- API Reference
- Ontology Structure
- Vector Mapping Configuration
- SPARQL Query Examples
- Integration Patterns
