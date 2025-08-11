# Default property-to-vector mappings for KGraph
# Maps RDF type URIs to dictionaries of vector_id -> list of property URIs
# This allows multiple vectors per type, each with its own semantic purpose

DEFAULT_VECTOR_MAPPINGS = {
    # VITAL_Node - basic node properties
    "http://vital.ai/ontology/vital-core#VITAL_Node": {
        "general": [
            "http://vital.ai/ontology/vital-core#hasName",
            "http://vital.ai/ontology/vital-core#hasDescription"
        ]
    },
    
    # VITAL_Edge - basic edge properties  
    "http://vital.ai/ontology/vital-core#VITAL_Edge": {
        "general": [
            "http://vital.ai/ontology/vital-core#hasName",
            "http://vital.ai/ontology/vital-core#hasDescription"
        ]
    },
    
    # KG Entity types - separate vectors for type and value
    "http://vital.ai/ontology/haley-ai-kg#KGEntity": {
        "entity_type": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGEntityTypeDescription"
        ],
        "entity_value": [
            "http://vital.ai/ontology/vital-core#hasName",
            "http://vital.ai/ontology/haley-ai-kg#hasKGraphDescription"
        ]
    },
    
    # KG Frame types - separate vectors for type and description
    "http://vital.ai/ontology/haley-ai-kg#KGFrame": {
        "type": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGFrameTypeDescription"
        ],
        "description": [
            "http://vital.ai/ontology/vital-core#hasDescription"
        ],
        "general": [
            "http://vital.ai/ontology/vital-core#hasName", 
            "http://vital.ai/ontology/haley-ai-kg#hasKGFrameTypeDescription",
            "http://vital.ai/ontology/vital-core#hasDescription"
        ]
    },
    
    # KG Slot types - base slot with only type description
    "http://vital.ai/ontology/haley-ai-kg#KGSlot": {
        "slot_type": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGSlotTypeDescription"
        ]
    },
    
    # KG Text Slot - has both type and value vectors
    "http://vital.ai/ontology/haley-ai-kg#KGTextSlot": {
        "slot_type": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGSlotTypeDescription"
        ],
        "slot_value": [
            "http://vital.ai/ontology/haley-ai-kg#hasTextSlotValue"
        ]
    },
    
    # KG Long Text Slot - has both type and value vectors
    "http://vital.ai/ontology/haley-ai-kg#KGLongTextSlot": {
        "slot_type": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGSlotTypeDescription"
        ],
        "slot_value": [
            "http://vital.ai/ontology/haley-ai-kg#hasLongTextSlotValue"
        ]
    },
    
    # KG DateTime Slot - only has type description
    "http://vital.ai/ontology/haley-ai-kg#KGDateTimeSlot": {
        "slot_type": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGSlotTypeDescription"
        ]
    },
    
    # KG Number Slot - only has type description
    "http://vital.ai/ontology/haley-ai-kg#KGNumberSlot": {
        "slot_type": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGSlotTypeDescription"
        ]
    },
    
    # KG Interaction types
    "http://vital.ai/ontology/haley-ai-kg#KGInteraction": {
        "general": [
            "http://vital.ai/ontology/vital-core#hasName",
            "http://vital.ai/ontology/vital-core#hasDescription",
            "http://vital.ai/ontology/haley-ai-kg#hasKGraphDescription"
        ],
        "description": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGraphDescription"
        ],
        "name": [
            "http://vital.ai/ontology/vital-core#hasName"
        ]
    },
    
    # KG Actor types
    "http://vital.ai/ontology/haley-ai-kg#KGActor": {
        "general": [
            "http://vital.ai/ontology/vital-core#hasName",
            "http://vital.ai/ontology/vital-core#hasDescription",
            "http://vital.ai/ontology/haley-ai-kg#hasKGraphDescription"
        ],
        "description": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGraphDescription"
        ],
        "name": [
            "http://vital.ai/ontology/vital-core#hasName"
        ]
    },
    
    # KG Agent types
    "http://vital.ai/ontology/haley-ai-kg#KGAgent": {
        "general": [
            "http://vital.ai/ontology/vital-core#hasName",
            "http://vital.ai/ontology/vital-core#hasDescription",
            "http://vital.ai/ontology/haley-ai-kg#hasKGraphDescription"
        ],
        "description": [
            "http://vital.ai/ontology/haley-ai-kg#hasKGraphDescription"
        ],
        "name": [
            "http://vital.ai/ontology/vital-core#hasName"
        ]
    },
    
    # Add more type mappings as needed
    # Format: "type_uri": {"vector_id": ["property_uri1", "property_uri2", ...], ...}
}

def get_default_mappings():
    """
    Get the default property-to-vector mappings.
    
    Returns:
        Dictionary mapping type URIs to dictionaries of vector_id -> property URIs
    """
    return DEFAULT_VECTOR_MAPPINGS.copy()

def get_vector_mappings_for_type(type_uri: str, custom_mappings: dict = None):
    """
    Get all vector mappings for a specific type URI.
    
    Args:
        type_uri: The RDF type URI
        custom_mappings: Optional custom mappings to override defaults
        
    Returns:
        Dictionary mapping vector_id to list of property URIs
    """
    mappings = custom_mappings if custom_mappings else DEFAULT_VECTOR_MAPPINGS
    return mappings.get(type_uri, {})

def get_vector_properties_for_type(type_uri: str, vector_id: str = "general", custom_mappings: dict = None):
    """
    Get the vector properties for a specific type URI and vector ID.
    
    Args:
        type_uri: The RDF type URI
        vector_id: The specific vector ID (defaults to "general")
        custom_mappings: Optional custom mappings to override defaults
        
    Returns:
        List of property URIs to use for vector generation
    """
    type_mappings = get_vector_mappings_for_type(type_uri, custom_mappings)
    return type_mappings.get(vector_id, [])

def get_available_vector_ids_for_type(type_uri: str, custom_mappings: dict = None):
    """
    Get all available vector IDs for a specific type URI.
    
    Args:
        type_uri: The RDF type URI
        custom_mappings: Optional custom mappings to override defaults
        
    Returns:
        List of vector IDs available for this type
    """
    type_mappings = get_vector_mappings_for_type(type_uri, custom_mappings)
    return list(type_mappings.keys())
