# Ontology Structure

## Haley AI Knowledge Graph Ontology

The KGraphMemory system is built on the `haley-ai-kg-0.1.0.owl` ontology, which provides a comprehensive semantic framework for AI agent knowledge representation.

## Ontology Overview

- **Namespace**: `http://vital.ai/ontology/haley-ai-kg#`
- **Version**: 0.1.0
- **Base Package**: `ai.haley.kg.domain`
- **Imports**: `haley-ai-question` ontology

## Core Annotation Properties

### Vectorization Annotations

#### isVectorized
- **Purpose**: Marks properties for inclusion in primary content vectors
- **Range**: `xsd:boolean`
- **Usage**: Applied to properties that should be vectorized for general semantic search

#### isVectorizedType
- **Purpose**: Marks properties for inclusion in type-specific vectors
- **Range**: `xsd:boolean`
- **Usage**: Applied to properties that represent object type information

## Core Classes Hierarchy

### Base Classes

#### KGNode
The fundamental base class for all knowledge graph nodes.

#### KGEntity
Represents entities in the knowledge graph.
- **Subclasses**: Various entity types (Person, Organization, Location, etc.)
- **Key Properties**: `hasName`, `hasKGEntityType`, `hasKGEntityDescription`

#### KGFrame
Represents frame-based knowledge structures.
- **Purpose**: Organize related information into coherent frames
- **Key Properties**: `hasKGFrameType`, `hasKGFrameDescription`

#### KGDocument
Represents documents and textual content.
- **Key Properties**: `hasKGDocumentContent`, `hasKGDocumentType`, `hasKGDocumentDescription`

### Agent-Related Classes

#### KGAgent
Represents AI agents in the system.
- **Key Properties**: `hasKGAgentType`, `hasKGAgentDescription`
- **Relationships**: Can have frames, actions, and interactions

#### KGActor
Represents actors (human or AI) in interactions.
- **Key Properties**: `hasKGActorType`, `hasName`

#### KGAction
Represents actions that can be performed.
- **Key Properties**: `hasKGActionType`, `hasKGActionDescription`

### Interaction Classes

#### KGChatMessage
Represents chat messages in conversations.
- **Types**: `KGChatUserMessage`, `KGChatBotMessage`
- **Key Properties**: `hasKGChatMessageContent`, `hasKGChatMessageType`

#### KGChatInteraction
Represents complete chat interactions.
- **Key Properties**: `hasKGChatInteractionType`, `hasKGChatInteractionDescription`

#### KGInteraction
General interaction representation.
- **Key Properties**: `hasKGInteractionType`, `hasKGInteractionDescription`

### Content Classes

#### KGMedia
Represents media content (images, audio, video).
- **Subclasses**: `KGAudio`, `KGImage`, `KGVideo`

#### KGCodeDocument
Represents code and programming content.
- **Key Properties**: `hasKGCodeLanguage`, `hasKGCodeContent`

### Slot Classes

Slot classes represent typed data containers:

#### KGTextSlot
For text content.

#### KGDateTimeSlot
For temporal information.

#### KGBooleanSlot
For boolean values.

#### KGChoiceSlot
For selection from options.

#### KGAudioSlot, KGImageSlot, KGCodeSlot
For multimedia content.

## Edge Classes and Relationships

### Edge Annotation Pattern

Each edge class defines source and destination constraints:

```xml
<owl:Class rdf:about="http://vital.ai/ontology/haley-ai-kg#Edge_hasEntityKGFrame">
    <rdfs:subClassOf rdf:resource="http://vital.ai/ontology/haley-ai-kg#Edge_hasKGEdge"/>
    <vital-core:hasEdgeDestDomain rdf:resource="http://vital.ai/ontology/haley-ai-kg#KGFrame"/>
    <vital-core:hasEdgeSrcDomain rdf:resource="http://vital.ai/ontology/haley-ai-kg#KGEntity"/>
    <vital-core:hasEdgeSrcDomain rdf:resource="http://vital.ai/ontology/haley-ai-kg#KGEntityMention"/>
</owl:Class>
```

### Key Relationship Types

#### Entity Relationships
- `Edge_hasEntityKGFrame`: Entity → Frame
- `Edge_hasEntityKGStatement`: Entity → Statement
- `Edge_hasKGEntity`: Various → Entity

#### Agent Relationships
- `Edge_hasKGAgent`: Various → Agent
- `Edge_hasKGActor`: Various → Actor
- `Edge_hasAgentKGFrame`: Agent → Frame

#### Content Relationships
- `Edge_hasKGDocument`: Various → Document
- `Edge_hasKGMedia`: Various → Media
- `Edge_hasKGChatMessage`: Various → ChatMessage

#### Frame Relationships
- `Edge_hasKGFrame`: Various → Frame
- `Edge_hasInteractionKGFrame`: Interaction → Frame

## Type System

### Entity Types
The ontology defines various entity type classifications:
- `KGEntityType`: Base type for entity classification
- `KGPersonType`, `KGOrganizationType`, etc.

### Frame Types
- `KGFrameType`: Base type for frame classification
- Specialized frame types for different domains

### Action Types
- `KGActionType`: Classification of possible actions
- Domain-specific action taxonomies

## Vectorization Strategy

### Default Vector Mappings

Based on the ontology annotations, default mappings are:

```python
{
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
    }
}
```

### Vectorization Principles

1. **Type Vectors**: Capture categorical/taxonomic information
2. **Description Vectors**: Capture descriptive/explanatory content
3. **Content Vectors**: Capture main body/content information
4. **General Vectors**: Capture overall semantic representation

## Integration with VitalSigns

### Class Generation
The VitalSigns library automatically generates Python classes from OWL definitions:

```python
from ai_haley_kg_domain.model.KGEntity import KGEntity
from ai_haley_kg_domain.model.KGFrame import KGFrame
from ai_haley_kg_domain.model.Edge_hasEntityKGFrame import Edge_hasEntityKGFrame
```

### Property Access
Generated classes provide type-safe property access:

```python
entity = KGEntity()
entity.hasName = "Example Entity"
entity.hasKGEntityType = entity_type_uri
entity.hasKGEntityDescription = "Description of the entity"
```

### Validation
The VitalSigns framework provides:
- Type validation for properties
- Cardinality constraints
- Domain/range validation for relationships

## Extensibility

### Custom Classes
The ontology can be extended with:
- New entity types
- Custom frame types
- Domain-specific relationships
- Additional annotation properties

### Custom Vector Types
New vector types can be added by:
- Defining new annotation properties
- Extending vector mapping configurations
- Implementing custom vectorization logic

## Best Practices

### Ontology Usage
1. Use appropriate base classes for new concepts
2. Follow naming conventions (CamelCase for classes, hasPropertyName for properties)
3. Apply vectorization annotations consistently
4. Define clear domain/range constraints for relationships

### Implementation Guidelines
1. Leverage generated classes for type safety
2. Use URI namespaces consistently
3. Apply vectorization mappings based on use cases
4. Validate ontology compliance in applications
