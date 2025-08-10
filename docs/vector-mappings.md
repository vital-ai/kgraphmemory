# Vector Mappings Configuration

## Overview

Vector mappings define how object properties are transformed into semantic vectors for similarity search. KGraphMemory supports multiple vectors per object type, enabling precise semantic search across different aspects of knowledge.

## Vector Types

### Standard Vector Types

#### general
- **Purpose**: Overall semantic representation of the object
- **Usage**: Default vector for general similarity search
- **Content**: Combines name, description, and key identifying properties

#### type
- **Purpose**: Categorical/taxonomic representation
- **Usage**: Search by object type or category
- **Content**: Type classifications, categories, taxonomies

#### description
- **Purpose**: Descriptive content representation
- **Usage**: Search by descriptive characteristics
- **Content**: Descriptions, explanations, characteristics

#### content
- **Purpose**: Main content/body representation
- **Usage**: Search within primary content
- **Content**: Document body, message content, detailed information

## Default Mappings

### Core Entity Types

```python
DEFAULT_VECTOR_MAPPINGS = {
    "KGEntity": {
        "type": ["hasKGEntityType"],
        "description": ["hasKGEntityDescription"],
        "general": ["hasName", "hasKGEntityDescription"]
    },
    
    "KGDocument": {
        "content": ["hasKGDocumentContent"],
        "description": ["hasKGDocumentDescription"],
        "general": ["hasName", "hasKGDocumentContent"]
    },
    
    "KGAgent": {
        "type": ["hasKGAgentType"],
        "description": ["hasKGAgentDescription"],
        "general": ["hasName", "hasKGAgentDescription"]
    },
    
    "KGFrame": {
        "type": ["hasKGFrameType"],
        "description": ["hasKGFrameDescription"],
        "general": ["hasName", "hasKGFrameDescription"]
    },
    
    "KGChatMessage": {
        "content": ["hasKGChatMessageContent"],
        "type": ["hasKGChatMessageType"],
        "general": ["hasKGChatMessageContent"]
    },
    
    "KGAction": {
        "type": ["hasKGActionType"],
        "description": ["hasKGActionDescription"],
        "general": ["hasName", "hasKGActionDescription"]
    }
}
```

### Extended Entity Types

```python
EXTENDED_MAPPINGS = {
    "KGActor": {
        "type": ["hasKGActorType"],
        "description": ["hasKGActorDescription"],
        "general": ["hasName", "hasKGActorDescription"]
    },
    
    "KGMedia": {
        "type": ["hasKGMediaType"],
        "description": ["hasKGMediaDescription"],
        "general": ["hasName", "hasKGMediaDescription"]
    },
    
    "KGCodeDocument": {
        "content": ["hasKGCodeContent"],
        "type": ["hasKGCodeLanguage"],
        "description": ["hasKGCodeDescription"],
        "general": ["hasName", "hasKGCodeContent"]
    },
    
    "KGInteraction": {
        "type": ["hasKGInteractionType"],
        "description": ["hasKGInteractionDescription"],
        "general": ["hasName", "hasKGInteractionDescription"]
    }
}
```

## Custom Mapping Configuration

### Basic Custom Mapping

```python
from kgraphmemory import KGraphMemory

custom_mappings = {
    "KGEntity": {
        "type": ["hasKGEntityType", "hasKGCategory"],
        "description": ["hasKGEntityDescription", "hasKGEntitySummary"],
        "content": ["hasKGEntityDetails"],
        "general": ["hasName", "hasKGEntityDescription"]
    }
}

memory = KGraphMemory(embedding_model, default_vector_mappings=custom_mappings)
```

### Per-Graph Custom Mappings

```python
# Different mappings for different graphs
agent_mappings = {
    "KGEntity": {
        "type": ["hasKGEntityType"],
        "description": ["hasKGEntityDescription"],
        "context": ["hasKGInteractionContext"],  # Custom vector type
        "general": ["hasName", "hasKGEntityDescription"]
    }
}

graph = memory.create_kgraph("agent_kb", "http://example.org/agent", agent_mappings)
```

### Domain-Specific Mappings

```python
# Medical domain example
medical_mappings = {
    "KGEntity": {
        "type": ["hasKGEntityType", "hasMedicalCategory"],
        "symptoms": ["hasSymptoms", "hasClinicalPresentation"],
        "treatment": ["hasTreatment", "hasTherapy"],
        "description": ["hasKGEntityDescription"],
        "general": ["hasName", "hasKGEntityDescription"]
    },
    
    "KGDocument": {
        "content": ["hasKGDocumentContent"],
        "diagnosis": ["hasDiagnosis", "hasFindings"],
        "procedure": ["hasProcedure", "hasIntervention"],
        "general": ["hasName", "hasKGDocumentContent"]
    }
}
```

## Vector Creation Process

### Property Extraction
1. **Object Analysis**: Examine object type and available properties
2. **Mapping Lookup**: Find applicable vector mappings for object type
3. **Property Retrieval**: Extract values for mapped properties
4. **Text Concatenation**: Combine property values into text strings
5. **Vector Generation**: Create embeddings using the embedding model

### Example Process

```python
# Object: KGEntity with properties
entity = KGEntity()
entity.hasName = "Apple Inc."
entity.hasKGEntityType = "http://vital.ai/ontology/haley-ai-kg#CorporationType"
entity.hasKGEntityDescription = "Technology company based in Cupertino"

# Vector creation for "type" vector
type_properties = ["hasKGEntityType"]  # From mapping
type_text = "CorporationType"  # Extracted and processed
type_vector = embedding_model.encode(type_text)

# Vector creation for "general" vector
general_properties = ["hasName", "hasKGEntityDescription"]
general_text = "Apple Inc. Technology company based in Cupertino"
general_vector = embedding_model.encode(general_text)
```

## Advanced Configuration

### Conditional Mappings

```python
def get_dynamic_mappings(object_type, object_instance):
    """Generate mappings based on object characteristics"""
    base_mappings = DEFAULT_VECTOR_MAPPINGS.get(object_type, {})
    
    # Add conditional mappings based on object properties
    if hasattr(object_instance, 'hasKGDocumentType'):
        doc_type = object_instance.hasKGDocumentType
        if 'Technical' in doc_type:
            base_mappings['technical'] = ['hasTechnicalDetails', 'hasSpecifications']
        elif 'Legal' in doc_type:
            base_mappings['legal'] = ['hasLegalTerms', 'hasCompliance']
    
    return base_mappings
```

### Weighted Property Mappings

```python
# Future enhancement: weighted properties
weighted_mappings = {
    "KGEntity": {
        "general": [
            ("hasName", 1.0),  # Full weight
            ("hasKGEntityDescription", 0.8),  # Reduced weight
            ("hasKGEntitySummary", 0.6)  # Lower weight
        ]
    }
}
```

## Vector Search Strategies

### Type-Specific Search

```python
# Search only in type vectors
results = graph.vector_search_by_type("technology company", "type")

# Search only in content vectors
results = graph.vector_search_by_type("machine learning algorithms", "content")
```

### Multi-Vector Search

```python
# Search across multiple vector types
type_results = graph.vector_search_by_type(query, "type", limit=5)
desc_results = graph.vector_search_by_type(query, "description", limit=5)

# Combine and rank results
combined_results = combine_and_rank([type_results, desc_results])
```

### Fallback Strategy

```python
def smart_vector_search(graph, query, preferred_vector="general"):
    """Search with fallback to other vector types"""
    
    # Try preferred vector type first
    results = graph.vector_search_by_type(query, preferred_vector, limit=10)
    
    if len(results) < 5:  # If insufficient results
        # Try other available vector types
        for vector_type in ["description", "content", "type"]:
            if vector_type != preferred_vector:
                additional = graph.vector_search_by_type(query, vector_type, limit=5)
                results.extend(additional)
    
    return deduplicate_and_rank(results)
```

## Performance Considerations

### Vector Storage Efficiency

```python
# Monitor vector counts per type
stats = graph.get_statistics()
print(f"Total vectors: {stats['vector_count']}")
print(f"Vectors by type: {stats['vectors_by_type']}")
```

### Memory Usage

- Each vector typically requires 384-1536 bytes (depending on model)
- Multiple vectors per object increase memory usage proportionally
- Monitor total vector count to stay within memory limits

### Search Performance

- Type-specific searches are faster than cross-type searches
- Fewer vector types per object improve search speed
- Consider vector type cardinality when designing mappings

## Best Practices

### Mapping Design
1. **Semantic Clarity**: Each vector type should represent a distinct semantic aspect
2. **Property Relevance**: Only include properties relevant to the vector's purpose
3. **Consistency**: Use consistent mapping patterns across similar object types
4. **Performance**: Balance semantic precision with computational efficiency

### Property Selection
1. **Text Quality**: Prefer properties with rich, descriptive text content
2. **Stability**: Use properties that don't change frequently
3. **Completeness**: Ensure mapped properties are commonly populated
4. **Uniqueness**: Avoid redundant properties in the same vector

### Vector Type Strategy
1. **Purpose-Driven**: Create vector types based on search use cases
2. **Granularity**: Balance between too few (imprecise) and too many (complex) types
3. **Fallback**: Always include a "general" vector type as fallback
4. **Evolution**: Design mappings to accommodate future property additions

### Testing and Validation
1. **Search Quality**: Test search results across different vector types
2. **Coverage**: Ensure all important object types have appropriate mappings
3. **Performance**: Monitor search latency and memory usage
4. **Relevance**: Validate that vector types produce semantically relevant results
