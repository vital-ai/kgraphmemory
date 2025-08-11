"""
KGraphFrameBridge - Specialized bridge for managing frames and their slots.

Handles KGFrame and KGSlot objects with SPARQL traversal of frame-slot relationships.
Slots only exist inside frames, so this bridge manages both frames and their contained slots.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from .kgraph_bridge_utilities import KGraphBridgeUtilities

# Import ontology classes
try:
    from ai_haley_kg_domain.model.KGFrame import KGFrame
    from ai_haley_kg_domain.model.KGSlot import KGSlot
    from ai_haley_kg_domain.model.KGTextSlot import KGTextSlot
    from ai_haley_kg_domain.model.KGEntitySlot import KGEntitySlot
    from ai_haley_kg_domain.model.KGDateTimeSlot import KGDateTimeSlot
    from ai_haley_kg_domain.model.KGBooleanSlot import KGBooleanSlot
except ImportError as e:
    print(f"Warning: Could not import ontology classes: {e}")
    KGFrame = None
    KGSlot = None
    KGTextSlot = None
    KGEntitySlot = None
    KGDateTimeSlot = None
    KGBooleanSlot = None


class KGraphFrameBridge:
    """
    Specialized bridge for managing frames and their slots.
    
    Provides high-level methods for:
    - Creating and managing KGFrame objects
    - Creating and managing KGSlot objects (which only exist inside frames)
    - SPARQL traversal of frame-slot relationships
    - Retrieving complete frame structures with all slots
    - Optionally traversing to entities referenced in entity slots
    """
    
    def __init__(self, kgraph, parent_bridge=None):
        """
        Initialize the frame bridge.
        
        Args:
            kgraph: KGraph instance
            parent_bridge: Parent KGraphBridge instance for cross-helper access
        """
        self.kgraph = kgraph
        self.parent_bridge = parent_bridge
        self.utils = KGraphBridgeUtilities(kgraph)
    
    # ============================================================================
    # FRAME MANAGEMENT
    # ============================================================================
    
    def create_frame(self, *, frame_instance=None, name: str = None, frame_type: str = None,
                    description: str = None) -> str:
        """
        Create a new KGFrame object.
        
        Args:
            frame_instance: Optional KGFrame instance to add directly
            name: Frame name (used if frame_instance not provided, defaults to generated name)
            frame_type: Type of frame (used if frame_instance not provided)
            description: Optional description (used if frame_instance not provided)
            
        Returns:
            URI of created frame
        """
        if frame_instance is not None:
            # Add the provided frame instance directly
            if self.kgraph.add_object(frame_instance):
                return str(frame_instance.URI)
            else:
                raise RuntimeError("Failed to add KGFrame instance")
        
        # Create frame from named parameters
        frame_props = {
            'hasName': name or self.utils.generate_name_with_timestamp("Frame")
        }
        
        if frame_type:
            frame_props['hasKGFrameType'] = frame_type
        if description:
            frame_props['hasKGFrameDescription'] = description
        
        frame_uri = self.utils.create_node('KGFrame', **frame_props)
        if not frame_uri:
            raise RuntimeError("Failed to create KGFrame")
        
        return frame_uri
    
    def create_frame_for_interaction(self, name: str, interaction_uri: str,
                                    frame_type: str = None, description: str = None) -> str:
        """
        Create a frame and link it to an interaction.
        
        Args:
            name: Frame name
            interaction_uri: URI of interaction to link to
            frame_type: Type of frame
            description: Optional description
            
        Returns:
            URI of created frame
        """
        frame_uri = self.create_frame(name, frame_type, description)
        self.utils.link_to_interaction(frame_uri, interaction_uri, "KGFrame")
        return frame_uri
    
    # ============================================================================
    # SLOT MANAGEMENT (Slots only exist inside frames)
    # ============================================================================
    
    def create_text_slot(self, *, frame_ref=None, slot_instance=None, slot_name: str = None, value: str = None) -> str:
        """
        Create a KGTextSlot and link it to a frame.
        
        Args:
            frame_ref: Frame URI (str) or KGFrame instance to contain this slot
            slot_instance: Optional KGTextSlot instance to add directly
            slot_name: Name of the slot (used if slot_instance not provided)
            value: Text value (used if slot_instance not provided)
            
        Returns:
            URI of created slot
        """
        # Extract frame URI from frame reference
        if hasattr(frame_ref, 'URI'):
            frame_uri = str(frame_ref.URI)
        elif isinstance(frame_ref, str):
            frame_uri = frame_ref
        else:
            raise ValueError("frame_ref must be a frame URI (str) or KGFrame instance")
        
        if slot_instance is not None:
            # Add the provided slot instance directly and link to frame
            if self.kgraph.add_object(slot_instance):
                slot_uri = str(slot_instance.URI)
                # Create edge linking frame to slot
                edge_uri = self.utils.create_edge('Edge_hasKGSlot', frame_uri, slot_uri)
                if not edge_uri:
                    raise RuntimeError("Failed to link slot to frame")
                return slot_uri
            else:
                raise RuntimeError("Failed to add KGTextSlot instance")
        
        # Create slot from named parameters
        if not slot_name or value is None:
            raise ValueError("slot_name and value are required when slot_instance is not provided")
        
        slot_props = {
            'hasName': slot_name,
            'hasKGSlotTextValue': value,
            'hasKGSlotType': 'text'
        }
        
        slot_uri, edge_uri = self.utils.create_node_with_edge(
            'KGTextSlot',
            'Edge_hasKGSlot',
            frame_uri,
            link_as_destination=True,  # Frame is source, slot is destination
            **slot_props
        )
        
        if not slot_uri:
            raise RuntimeError("Failed to create KGTextSlot")
        
        return slot_uri
    
    def create_entity_slot(self, frame_uri: str, slot_name: str, entity_uri: str,
                          slot_type: str = None) -> str:
        """
        Create an entity slot and link it to a frame.
        
        Args:
            frame_uri: URI of the frame to contain this slot
            slot_name: Name of the slot
            entity_uri: URI of the entity this slot references
            slot_type: Optional slot type (e.g., "hasSourceEntity", "hasDestinationEntity")
            
        Returns:
            URI of created slot
        """
        slot_props = {
            'hasName': slot_name,
            'hasEntitySlotValue': entity_uri
        }
        
        if slot_type:
            slot_props['hasKGSlotType'] = slot_type
        else:
            slot_props['hasKGSlotType'] = 'entity'
        
        slot_uri, edge_uri = self.utils.create_node_with_edge(
            'KGEntitySlot',
            'Edge_hasKGSlot',
            frame_uri,
            link_as_destination=True,  # Frame is source, slot is destination
            **slot_props
        )
        
        if not slot_uri:
            raise RuntimeError("Failed to create entity slot")
        
        return slot_uri
    
    def create_datetime_slot(self, frame_uri: str, slot_name: str, value: datetime) -> str:
        """
        Create a datetime slot and link it to a frame.
        
        Args:
            frame_uri: URI of the frame to contain this slot
            slot_name: Name of the slot
            value: DateTime value
            
        Returns:
            URI of created slot
        """
        slot_props = {
            'hasName': slot_name,
            'hasKGSlotDateTimeValue': value.isoformat(),
            'hasKGSlotType': 'datetime'
        }
        
        slot_uri, edge_uri = self.utils.create_node_with_edge(
            'KGDateTimeSlot',
            'Edge_hasKGSlot',
            frame_uri,
            link_as_destination=True,  # Frame is source, slot is destination
            **slot_props
        )
        
        if not slot_uri:
            raise RuntimeError("Failed to create datetime slot")
        
        return slot_uri
    
    def create_boolean_slot(self, frame_uri: str, slot_name: str, value: bool) -> str:
        """
        Create a boolean slot and link it to a frame.
        
        Args:
            frame_uri: URI of the frame to contain this slot
            slot_name: Name of the slot
            value: Boolean value
            
        Returns:
            URI of created slot
        """
        slot_props = {
            'hasName': slot_name,
            'hasKGSlotBooleanValue': value,
            'hasKGSlotType': 'boolean'
        }
        
        slot_uri, edge_uri = self.utils.create_node_with_edge(
            'KGBooleanSlot',
            'Edge_hasKGSlot',
            frame_uri,
            link_as_destination=True,  # Frame is source, slot is destination
            **slot_props
        )
        
        if not slot_uri:
            raise RuntimeError("Failed to create boolean slot")
        
        return slot_uri
    
    # ============================================================================
    # FRAME RETRIEVAL WITH SLOT TRAVERSAL
    # ============================================================================
    
    def get_frame_with_slots(self, frame_uri: str, include_entities: bool = False) -> Dict[str, Any]:
        """
        Get a complete frame structure with all its slots using SPARQL traversal.
        
        Args:
            frame_uri: URI of the frame
            include_entities: If True, include entity details for entity slots
            
        Returns:
            Dictionary with frame properties and all slots
        """
        # Base query to get frame properties and slots
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?frame ?frameName ?frameType ?frameDescription
               ?slot ?slotName ?slotType ?slotClass
               ?textValue ?entityValue ?datetimeValue ?booleanValue
        WHERE {{
            # Frame properties
            <{frame_uri}> a kg:KGFrame .
            BIND(<{frame_uri}> AS ?frame)
            OPTIONAL {{ ?frame vital-core:hasName ?frameName }}
            OPTIONAL {{ ?frame kg:hasKGFrameType ?frameType }}
            OPTIONAL {{ ?frame kg:hasKGFrameDescription ?frameDescription }}
            
            # Slots connected to this frame via edges
            OPTIONAL {{
                ?edge a kg:Edge_hasKGSlot .
                ?edge vital-core:hasEdgeSource ?frame .
                ?edge vital-core:hasEdgeDestination ?slot .
                
                # Slot properties
                ?slot a ?slotClass .
                OPTIONAL {{ ?slot vital-core:hasName ?slotName }}
                OPTIONAL {{ ?slot kg:hasKGSlotType ?slotType }}
                
                # Slot values based on type
                OPTIONAL {{ ?slot kg:hasKGSlotTextValue ?textValue }}
                OPTIONAL {{ ?slot kg:hasEntitySlotValue ?entityValue }}
                OPTIONAL {{ ?slot kg:hasKGSlotDateTimeValue ?datetimeValue }}
                OPTIONAL {{ ?slot kg:hasKGSlotBooleanValue ?booleanValue }}
            }}
        }}
        ORDER BY ?slotName
        """
        
        results = self.kgraph.sparql_query(query)
        
        if not results:
            return None
        
        # Process results into structured format
        frame_data = {
            'frame_uri': frame_uri,
            'frame_properties': {},
            'slots': [],
            'slot_count': 0
        }
        
        # Extract frame properties from first result
        first_result = results[0]
        frame_data['frame_properties'] = {
            'hasName': first_result.get('frameName'),
            'hasKGFrameType': first_result.get('frameType'),
            'hasKGFrameDescription': first_result.get('frameDescription')
        }
        
        # Process slots
        slots_by_uri = {}
        for result in results:
            slot_uri = result.get('slot')
            if slot_uri and slot_uri not in slots_by_uri:
                slot_class = result.get('slotClass', '')
                slot_type = slot_class.split('#')[-1] if '#' in slot_class else slot_class
                
                slot_data = {
                    'slot_uri': slot_uri,
                    'slot_name': result.get('slotName'),
                    'slot_type': result.get('slotType'),
                    'slot_class': slot_type,
                    'value': None
                }
                
                # Determine value based on slot type
                if result.get('textValue'):
                    slot_data['value'] = result.get('textValue')
                elif result.get('entityValue'):
                    slot_data['value'] = result.get('entityValue')
                    if include_entities:
                        slot_data['entity_details'] = self._get_entity_details(result.get('entityValue'))
                elif result.get('datetimeValue'):
                    slot_data['value'] = result.get('datetimeValue')
                elif result.get('booleanValue') is not None:
                    slot_data['value'] = result.get('booleanValue')
                
                slots_by_uri[slot_uri] = slot_data
        
        frame_data['slots'] = list(slots_by_uri.values())
        frame_data['slot_count'] = len(frame_data['slots'])
        
        return frame_data
    
    def get_frames_for_interaction(self, interaction_uri: str, include_slots: bool = True,
                                  include_entities: bool = False) -> List[Dict[str, Any]]:
        """
        Get all frames for an interaction, optionally with their slots.
        
        Args:
            interaction_uri: URI of the interaction
            include_slots: If True, include all slots for each frame
            include_entities: If True, include entity details for entity slots
            
        Returns:
            List of frame dictionaries with optional slot data
        """
        # Get frame URIs linked to the interaction
        frame_objects = self.utils.get_linked_objects(interaction_uri, "KGFrame")
        
        frames = []
        for frame_obj in frame_objects:
            frame_uri = frame_obj.get('object')
            if frame_uri:
                if include_slots:
                    frame_data = self.get_frame_with_slots(frame_uri, include_entities)
                    if frame_data:
                        frames.append(frame_data)
                else:
                    # Just get basic frame properties
                    frame_props = self.utils.get_object_properties(frame_uri)
                    frames.append({
                        'frame_uri': frame_uri,
                        'frame_properties': frame_props
                    })
        
        return frames
    
    # ============================================================================
    # SPECIALIZED FRAME PATTERNS
    # ============================================================================
    
    def create_address_frame(self, street: str = None, city: str = None,
                           state: str = None, zip_code: str = None,
                           country: str = None) -> str:
        """
        Create an address frame with text slots for address components.
        
        Args:
            street: Street address
            city: City name
            state: State/province
            zip_code: ZIP/postal code
            country: Country
            
        Returns:
            URI of created address frame
        """
        frame_uri = self.create_frame("Address", "AddressFrame", "Address information")
        
        # Create slots for each address component
        if street:
            self.create_text_slot(frame_uri, "street", street)
        if city:
            self.create_text_slot(frame_uri, "city", city)
        if state:
            self.create_text_slot(frame_uri, "state", state)
        if zip_code:
            self.create_text_slot(frame_uri, "zip", zip_code)
        if country:
            self.create_text_slot(frame_uri, "country", country)
        
        return frame_uri
    
    def create_relationship_frame(self, frame_type: str, source_entity_uri: str,
                                 destination_entity_uri: str, relationship_name: str = None) -> str:
        """
        Create a relationship frame connecting two entities (similar to WordNet pattern).
        
        Args:
            frame_type: Type of relationship frame
            source_entity_uri: URI of source entity
            destination_entity_uri: URI of destination entity
            relationship_name: Optional name for the relationship
            
        Returns:
            URI of created relationship frame
        """
        frame_name = relationship_name or f"Relationship_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        frame_uri = self.create_frame(frame_name, frame_type, f"Relationship: {frame_type}")
        
        # Create source and destination entity slots
        self.create_entity_slot(frame_uri, "source", source_entity_uri, "hasSourceEntity")
        self.create_entity_slot(frame_uri, "destination", destination_entity_uri, "hasDestinationEntity")
        
        return frame_uri
    
    # ============================================================================
    # SEARCH AND FILTER
    # ============================================================================
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for frames using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of frame search results
        """
        return self.utils.search_by_type(query, "KGFrame", limit)
    
    def get_frames_by_type(self, frame_type: str, include_slots: bool = False) -> List[Dict[str, Any]]:
        """
        Get all frames of a specific type.
        
        Args:
            frame_type: Frame type to filter by
            include_slots: If True, include slots for each frame
            
        Returns:
            List of frame dictionaries
        """
        frame_objects = self.utils.filter_by_property("KGFrame", "hasKGFrameType", frame_type)
        
        if not include_slots:
            return frame_objects
        
        # Include slots for each frame
        frames_with_slots = []
        for frame_obj in frame_objects:
            frame_uri = frame_obj.get('object')
            if frame_uri:
                frame_data = self.get_frame_with_slots(frame_uri)
                if frame_data:
                    frames_with_slots.append(frame_data)
        
        return frames_with_slots
    
    def find_frames_with_entity(self, entity_uri: str) -> List[Dict[str, Any]]:
        """
        Find all frames that contain slots referencing a specific entity.
        
        Args:
            entity_uri: URI of the entity to find
            
        Returns:
            List of frame dictionaries that reference the entity
        """
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT DISTINCT ?frame ?frameName ?frameType
        WHERE {{
            ?frame a kg:KGFrame .
            OPTIONAL {{ ?frame vital-core:hasName ?frameName }}
            OPTIONAL {{ ?frame kg:hasKGFrameType ?frameType }}
            
            # Find slots in this frame that reference the entity
            ?edge a kg:Edge_hasKGSlot .
            ?edge vital-core:hasEdgeSource ?frame .
            ?edge vital-core:hasEdgeDestination ?slot .
            ?slot a kg:KGEntitySlot .
            ?slot kg:hasEntitySlotValue <{entity_uri}> .
        }}
        """
        
        results = self.kgraph.sparql_query(query)
        return [dict(result) for result in results]
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    def _get_entity_details(self, entity_uri: str) -> Dict[str, Any]:
        """
        Get basic details about an entity referenced in a slot.
        
        Args:
            entity_uri: URI of the entity
            
        Returns:
            Dictionary with entity details
        """
        try:
            entity_props = self.utils.get_object_properties(entity_uri)
            return {
                'entity_uri': entity_uri,
                'properties': entity_props
            }
        except Exception as e:
            print(f"Warning: Could not get entity details for {entity_uri}: {e}")
            return {
                'entity_uri': entity_uri,
                'properties': {},
                'error': str(e)
            }
