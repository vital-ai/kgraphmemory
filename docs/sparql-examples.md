# SPARQL Query Examples

## Overview

This document provides practical SPARQL query examples for the KGraphMemory system. All queries work with the Haley AI Knowledge Graph ontology and can be executed using the `sparql_query()` method.

## Basic Query Patterns

### Simple Entity Retrieval

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Get all entities with their names
SELECT ?entity ?name WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name .
}
```

### Entity by Type

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>

# Find all entities of a specific type
SELECT ?entity ?name ?type WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name ;
            kg:hasKGEntityType ?type .
    FILTER(CONTAINS(STR(?type), "Person"))
}
```

### Property Filtering

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find entities with descriptions containing specific text
SELECT ?entity ?name ?description WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name ;
            kg:hasKGEntityDescription ?description .
    FILTER(CONTAINS(LCASE(?description), "technology"))
}
```

## Relationship Queries

### Entity-Frame Relationships

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find entities and their associated frames
SELECT ?entity ?entityName ?frame ?frameName WHERE {
    ?edge a kg:Edge_hasEntityKGFrame ;
          vital-core:hasEdgeSource ?entity ;
          vital-core:hasEdgeDestination ?frame .
    ?entity vital-core:hasName ?entityName .
    ?frame vital-core:hasName ?frameName .
}
```

### Agent Interactions

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find agents and their interactions
SELECT ?agent ?agentName ?interaction ?interactionType WHERE {
    ?edge a kg:Edge_hasKGAgent ;
          vital-core:hasEdgeSource ?interaction ;
          vital-core:hasEdgeDestination ?agent .
    ?agent vital-core:hasName ?agentName .
    ?interaction kg:hasKGInteractionType ?interactionType .
}
```

### Document Relationships

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find documents and their associated entities
SELECT ?document ?docName ?entity ?entityName WHERE {
    ?edge a kg:Edge_hasKGDocument ;
          vital-core:hasEdgeSource ?entity ;
          vital-core:hasEdgeDestination ?document .
    ?document vital-core:hasName ?docName .
    ?entity vital-core:hasName ?entityName .
}
```

## Chat and Interaction Queries

### Chat Message History

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Get chat messages in chronological order
SELECT ?message ?content ?type ?timestamp WHERE {
    ?message a kg:KGChatMessage ;
             kg:hasKGChatMessageContent ?content ;
             kg:hasKGChatMessageType ?type ;
             vital-core:hasTimestamp ?timestamp .
}
ORDER BY ?timestamp
```

### User vs Bot Messages

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>

# Separate user and bot messages
SELECT ?message ?content ?messageType WHERE {
    {
        ?message a kg:KGChatUserMessage ;
                 kg:hasKGChatMessageContent ?content .
        BIND("user" AS ?messageType)
    }
    UNION
    {
        ?message a kg:KGChatBotMessage ;
                 kg:hasKGChatMessageContent ?content .
        BIND("bot" AS ?messageType)
    }
}
```

### Interaction Context

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find interactions with their context and participants
SELECT ?interaction ?type ?actor ?actorName ?frame ?frameType WHERE {
    ?interaction a kg:KGChatInteraction ;
                 kg:hasKGInteractionType ?type .
    
    # Get actor
    ?actorEdge a kg:Edge_hasKGActor ;
               vital-core:hasEdgeSource ?interaction ;
               vital-core:hasEdgeDestination ?actor .
    ?actor vital-core:hasName ?actorName .
    
    # Get associated frame
    OPTIONAL {
        ?frameEdge a kg:Edge_hasInteractionKGFrame ;
                   vital-core:hasEdgeSource ?interaction ;
                   vital-core:hasEdgeDestination ?frame .
        ?frame kg:hasKGFrameType ?frameType .
    }
}
```

## Advanced Patterns

### Hierarchical Relationships

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find entity hierarchies (entities that contain other entities)
SELECT ?parent ?parentName ?child ?childName WHERE {
    ?edge a kg:Edge_hasKGEntity ;
          vital-core:hasEdgeSource ?parent ;
          vital-core:hasEdgeDestination ?child .
    ?parent vital-core:hasName ?parentName .
    ?child vital-core:hasName ?childName .
    FILTER(?parent != ?child)
}
```

### Multi-hop Relationships

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find entities connected through frames (2-hop relationship)
SELECT ?entity1 ?entity1Name ?frame ?entity2 ?entity2Name WHERE {
    # Entity1 -> Frame
    ?edge1 a kg:Edge_hasEntityKGFrame ;
           vital-core:hasEdgeSource ?entity1 ;
           vital-core:hasEdgeDestination ?frame .
    
    # Entity2 -> Same Frame
    ?edge2 a kg:Edge_hasEntityKGFrame ;
           vital-core:hasEdgeSource ?entity2 ;
           vital-core:hasEdgeDestination ?frame .
    
    ?entity1 vital-core:hasName ?entity1Name .
    ?entity2 vital-core:hasName ?entity2Name .
    
    FILTER(?entity1 != ?entity2)
}
```

### Aggregation Queries

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Count entities by type
SELECT ?entityType (COUNT(?entity) AS ?count) WHERE {
    ?entity a kg:KGEntity ;
            kg:hasKGEntityType ?entityType .
}
GROUP BY ?entityType
ORDER BY DESC(?count)
```

### Temporal Queries

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Find recent interactions (last 24 hours)
SELECT ?interaction ?type ?timestamp WHERE {
    ?interaction a kg:KGChatInteraction ;
                 kg:hasKGInteractionType ?type ;
                 vital-core:hasTimestamp ?timestamp .
    
    FILTER(?timestamp > (NOW() - "P1D"^^xsd:duration))
}
ORDER BY DESC(?timestamp)
```

## Construct Queries

### Building Knowledge Graphs

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Construct a subgraph of entities and their relationships
CONSTRUCT {
    ?entity1 kg:relatedTo ?entity2 .
    ?entity1 vital-core:hasName ?name1 .
    ?entity2 vital-core:hasName ?name2 .
} WHERE {
    ?edge a kg:Edge_hasEntityKGFrame ;
          vital-core:hasEdgeSource ?entity1 ;
          vital-core:hasEdgeDestination ?frame .
    
    ?edge2 a kg:Edge_hasEntityKGFrame ;
           vital-core:hasEdgeSource ?entity2 ;
           vital-core:hasEdgeDestination ?frame .
    
    ?entity1 vital-core:hasName ?name1 .
    ?entity2 vital-core:hasName ?name2 .
    
    FILTER(?entity1 != ?entity2)
}
```

### Data Transformation

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Transform chat messages into simplified format
CONSTRUCT {
    ?message kg:hasSimpleContent ?content ;
             kg:hasSimpleType ?simpleType ;
             kg:hasSimpleTimestamp ?timestamp .
} WHERE {
    ?message a kg:KGChatMessage ;
             kg:hasKGChatMessageContent ?content ;
             vital-core:hasTimestamp ?timestamp .
    
    BIND(IF(EXISTS{?message a kg:KGChatUserMessage}, "user", "bot") AS ?simpleType)
}
```

## Performance Optimization

### Indexed Property Queries

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Use specific property paths for better performance
SELECT ?entity ?name WHERE {
    ?entity a kg:KGEntity .
    ?entity vital-core:hasName ?name .
    # More efficient than using property paths
}
```

### Limited Result Sets

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Limit results for large datasets
SELECT ?entity ?name ?description WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name ;
            kg:hasKGEntityDescription ?description .
}
ORDER BY ?name
LIMIT 100
```

### Selective Filtering

```sparql
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

# Filter early in the query for better performance
SELECT ?entity ?name ?frame WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name .
    
    # Apply filters early
    FILTER(STRLEN(?name) > 3)
    
    # Then join with other patterns
    OPTIONAL {
        ?edge a kg:Edge_hasEntityKGFrame ;
              vital-core:hasEdgeSource ?entity ;
              vital-core:hasEdgeDestination ?frame .
    }
}
```

## Integration with Python

### Basic Query Execution

```python
# Execute SPARQL query
query = """
PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
PREFIX vital-core: <http://vital.ai/ontology/vital-core#>

SELECT ?entity ?name WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name .
}
"""

results = graph.sparql_query(query)
for result in results:
    print(f"Entity: {result['entity']}, Name: {result['name']}")
```

### Parameterized Queries

```python
def find_entities_by_type(graph, entity_type):
    query = f"""
    PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
    PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
    
    SELECT ?entity ?name WHERE {{
        ?entity a kg:KGEntity ;
                vital-core:hasName ?name ;
                kg:hasKGEntityType <{entity_type}> .
    }}
    """
    return graph.sparql_query(query)
```

### Query Building

```python
class SPARQLQueryBuilder:
    def __init__(self):
        self.prefixes = {
            'kg': 'http://vital.ai/ontology/haley-ai-kg#',
            'vital-core': 'http://vital.ai/ontology/vital-core#'
        }
        self.select_vars = []
        self.where_patterns = []
        self.filters = []
    
    def add_entity_pattern(self, var_name='entity'):
        self.select_vars.append(f'?{var_name}')
        self.where_patterns.append(f'?{var_name} a kg:KGEntity')
        return self
    
    def add_name_pattern(self, entity_var='entity', name_var='name'):
        self.select_vars.append(f'?{name_var}')
        self.where_patterns.append(f'?{entity_var} vital-core:hasName ?{name_var}')
        return self
    
    def build(self):
        prefixes = '\n'.join([f'PREFIX {k}: <{v}>' for k, v in self.prefixes.items()])
        select = f"SELECT {' '.join(set(self.select_vars))}"
        where = "WHERE {\n    " + " .\n    ".join(self.where_patterns) + " ."
        if self.filters:
            where += "\n    " + "\n    ".join([f"FILTER({f})" for f in self.filters])
        where += "\n}"
        
        return f"{prefixes}\n\n{select} {where}"

# Usage
builder = SPARQLQueryBuilder()
query = builder.add_entity_pattern().add_name_pattern().build()
```

## Common Patterns Summary

### Entity Queries
- Basic entity retrieval with properties
- Filtering by type, name, or description
- Entity relationships and connections

### Interaction Queries
- Chat message history and analysis
- Agent-user interactions
- Context and participant tracking

### Relationship Queries
- Direct relationships (entity-frame, agent-action)
- Multi-hop connections
- Hierarchical structures

### Temporal Queries
- Time-based filtering
- Chronological ordering
- Recent activity tracking

### Aggregation Queries
- Counting by type or category
- Statistical analysis
- Summary reporting
