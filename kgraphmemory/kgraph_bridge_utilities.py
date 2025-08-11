"""
KGraphBridge Utilities - Shared utility functions for all bridge classes.

Contains common functions used across different bridge classes to avoid code duplication
and ensure consistent behavior.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator


class KGraphBridgeUtilities:
    """
    Shared utility functions for KGraph bridge classes.
    
    Provides common functionality for:
    - Edge creation and management
    - Object linking patterns
    - SPARQL query helpers
    - Property and attribute handling
    """
    
    def __init__(self, kgraph):
        """
        Initialize utilities with KGraph instance.
        
        Args:
            kgraph: KGraph instance to operate on
        """
        self.kgraph = kgraph
    
    # ============================================================================
    # NODE CREATION PATTERNS
    # ============================================================================
    
    def create_node(self, node_instance) -> Optional[str]:
        """
        Add a valid graph object instance to the graph.
        
        Args:
            node_instance: A valid graph object instance (e.g., KGEntity, KGInteraction, etc.)
            
        Returns:
            URI of the added node or None if failed
        """
        try:
            # Ensure the node has a valid URI
            if not hasattr(node_instance, 'URI') or not node_instance.URI:
                raise ValueError("Graph object instance must have a valid URI")
            
            # Add the node to the graph
            success = self.kgraph.add_object(node_instance)
            if success:
                return str(node_instance.URI)
            else:
                print(f"Warning: Failed to add node {node_instance.URI} to graph")
                return None
            
        except Exception as e:
            print(f"Warning: Could not add node to graph: {e}")
            return None
    
    def create_node_and_link_to_interaction(self, node_class_name: str, 
                                           interaction_uri: str = None,
                                           **properties) -> Optional[str]:
        """
        Create a node and automatically link it to an interaction.
        
        Args:
            node_class_name: Name of the node class
            interaction_uri: URI of interaction to link to
            **properties: Properties to set on the node
            
        Returns:
            URI of created node or None if failed
        """
        node_uri = self.create_node(node_class_name, **properties)
        if node_uri and interaction_uri:
            self.link_to_interaction(node_uri, interaction_uri, node_class_name)
        return node_uri
    
    # ============================================================================
    # EDGE CREATION AND MANAGEMENT
    # ============================================================================
    
    def create_edge(self, edge_type: str, source_uri: str, dest_uri: str) -> Optional[str]:
        """
        Create an edge between two objects.
        
        Args:
            edge_type: Type of edge to create (e.g., "Edge_hasKGEntity")
            source_uri: Source object URI
            dest_uri: Destination object URI
            
        Returns:
            URI of created edge or None if failed
        """
        try:
            # Dynamically import the edge class
            edge_module = f"ai_haley_kg_domain.model.{edge_type}"
            edge_class = getattr(__import__(edge_module, fromlist=[edge_type]), edge_type)
            
            edge = edge_class()
            edge.URI = URIGenerator.generate_uri()
            
            # Get allowed properties for this edge type
            allowed_props = {}
            try:
                allowed_list = edge.get_allowed_properties()
                for prop_info in allowed_list:
                    uri = prop_info['uri']
                    prop_name = uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]
                    allowed_props[prop_name] = uri
            except:
                pass
            
            # Set source and destination using correct property names
            if hasattr(edge, 'edgeSource'):
                edge.edgeSource = source_uri
            elif hasattr(edge, 'hasEdgeSource'):
                edge.hasEdgeSource = source_uri
            elif 'hasEdgeSource' in allowed_props:
                setattr(edge, 'hasEdgeSource', source_uri)
            
            if hasattr(edge, 'edgeDestination'):
                edge.edgeDestination = dest_uri
            elif hasattr(edge, 'hasEdgeDestination'):
                edge.hasEdgeDestination = dest_uri
            elif 'hasEdgeDestination' in allowed_props:
                setattr(edge, 'hasEdgeDestination', dest_uri)
            
            # Set timestamp if supported
            if hasattr(edge, 'hasTimestamp'):
                try:
                    edge.hasTimestamp = self.generate_timestamp()
                except:
                    pass
            
            self.kgraph.add_object(edge)
            return str(edge.URI)
            
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not create edge {edge_type}: {e}")
            return None
    
    def delete_edge(self, edge_type: str, source_uri: str, dest_uri: str) -> bool:
        """
        Delete an edge between two objects.
        
        Args:
            edge_type: Type of edge to delete (e.g., "Edge_hasKGEntity")
            source_uri: Source object URI
            dest_uri: Destination object URI
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the edge to delete
            query = f"""
            PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
            
            SELECT ?edge WHERE {{
                ?edge a kg:{edge_type} ;
                      kg:hasEdgeSource <{source_uri}> ;
                      kg:hasEdgeDestination <{dest_uri}> .
            }}
            """
            
            results = self.kgraph.sparql_query(query)
            
            # Delete each matching edge
            success = False
            for result in results:
                edge_uri = result.get('edge')
                if edge_uri:
                    try:
                        if hasattr(self.kgraph, 'delete_object_by_uri'):
                            self.kgraph.delete_object_by_uri(edge_uri)
                        else:
                            # Fallback to remove_object if delete_object_by_uri doesn't exist
                            edge_obj = self.kgraph.get_object(edge_uri)
                            if edge_obj:
                                self.kgraph.remove_object(edge_obj)
                        success = True
                    except Exception as e:
                        print(f"Warning: Could not delete edge {edge_uri}: {e}")
            
            return success
            
        except Exception as e:
            print(f"Warning: Could not delete edge {edge_type}: {e}")
            return False
    
    def create_node_with_edge(self, node_class_name: str, edge_type: str,
                             source_uri: str, link_as_destination: bool = True,
                             **node_properties) -> tuple[Optional[str], Optional[str]]:
        """
        Create a node and an edge in one operation.
        
        Args:
            node_class_name: Name of the node class to create
            edge_type: Type of edge to create
            source_uri: URI of the source object for the edge
            link_as_destination: If True, new node is edge destination; if False, new node is source
            **node_properties: Properties to set on the new node
            
        Returns:
            Tuple of (node_uri, edge_uri) or (None, None) if failed
        """
        node_uri = self.create_node(node_class_name, **node_properties)
        if not node_uri:
            return None, None
        
        if link_as_destination:
            edge_uri = self.create_edge(edge_type, source_uri, node_uri)
        else:
            edge_uri = self.create_edge(edge_type, node_uri, source_uri)
        
        return node_uri, edge_uri
    
    def link_objects(self, edge_type: str, source_uri: str, dest_uri: str) -> Optional[str]:
        """
        Link two objects with an edge (alias for create_edge).
        
        Args:
            edge_type: Type of edge
            source_uri: Source object URI
            dest_uri: Destination object URI
            
        Returns:
            URI of created edge or None if failed
        """
        return self.create_edge(edge_type, source_uri, dest_uri)
    
    # ============================================================================
    # COMMON LINKING PATTERNS
    # ============================================================================
    
    def link_to_interaction(self, object_uri: str, interaction_uri: str, 
                           object_type: str) -> Optional[str]:
        """
        Link an object to an interaction using the appropriate edge type.
        
        Args:
            object_uri: URI of object to link
            interaction_uri: URI of interaction
            object_type: Type of object (determines edge type)
            
        Returns:
            URI of created edge or None if failed
        """
        edge_type_map = {
            'KGEntity': 'Edge_hasKGEntity',
            'KGDocument': 'Edge_hasKGDocument',
            'KGTask': 'Edge_hasKGTask',
            'KGFrame': 'Edge_hasKGFrame',
            'KGTool': 'Edge_hasKGTool',
            'KGToolRequest': 'Edge_hasKGToolRequest',
            'KGToolResult': 'Edge_hasKGToolResult',
            'KGChatMessage': 'Edge_hasKGChatMessage',
            'KGActor': 'Edge_hasKGActor',
            'KGAgent': 'Edge_hasKGAgent'
        }
        
        edge_type = edge_type_map.get(object_type)
        if not edge_type:
            print(f"Warning: No edge type mapping for object type {object_type}")
            return None
        
        return self.create_edge(edge_type, interaction_uri, object_uri)
    
    def link_slot_to_frame(self, slot_uri: str, frame_uri: str) -> Optional[str]:
        """
        Link a slot to a frame.
        
        Args:
            slot_uri: URI of slot
            frame_uri: URI of frame
            
        Returns:
            URI of created edge or None if failed
        """
        return self.create_edge("Edge_hasKGSlot", frame_uri, slot_uri)
    
    def link_frame_to_entity(self, frame_uri: str, entity_uri: str) -> Optional[str]:
        """
        Link a frame to an entity.
        
        Args:
            frame_uri: URI of frame
            entity_uri: URI of entity
            
        Returns:
            URI of created edge or None if failed
        """
        return self.create_edge("Edge_hasKGFrame", entity_uri, frame_uri)
    
    # ============================================================================
    # SPARQL QUERY HELPERS
    # ============================================================================
    
    def get_linked_objects(self, source_uri: str, target_type: str, 
                          edge_type: str = None) -> List[Any]:
        """
        Get objects linked to a source object by edge type as ontology class instances.
        
        Args:
            source_uri: URI of source object
            target_type: Type of target objects to find
            edge_type: Optional specific edge type
            
        Returns:
            List of linked ontology class instances
        """
        edge_filter = f"?edge a kg:Edge_{edge_type} ." if edge_type else ""
        graph_uri = self.kgraph.graph_uri
        
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?target WHERE {{
            GRAPH <{graph_uri}> {{
                ?edge ?sourceProp <{source_uri}> ;
                      ?destProp ?target .
                ?target a kg:{target_type} .
                {edge_filter}
                FILTER(STRSTARTS(STR(?sourceProp), "http://vital.ai/ontology/vital-core#hasEdgeSource") ||
                       STRSTARTS(STR(?sourceProp), "http://vital.ai/ontology/vital-core#hasEdgeDestination"))
                FILTER(STRSTARTS(STR(?destProp), "http://vital.ai/ontology/vital-core#hasEdgeSource") ||
                       STRSTARTS(STR(?destProp), "http://vital.ai/ontology/vital-core#hasEdgeDestination"))
                FILTER(?sourceProp != ?destProp)
            }}
        }}
        """
        
        results = self.kgraph.sparql_query(query)
        
        # Convert URIs to ontology class instances
        instances = []
        for result in results:
            target_uri = result.get('?target')
            if target_uri:
                # Strip angle brackets from URI if present
                clean_uri = target_uri.strip('<>')
                instance = self.kgraph.get_object(clean_uri)
                if instance:
                    instances.append(instance)
        
        return instances
    
    def get_objects_by_type(self, object_type: str, limit: int = None) -> List[Any]:
        """
        Get all objects of a specific type as ontology class instances.
        
        Args:
            object_type: Type of objects to find
            limit: Optional limit on results
            
        Returns:
            List of ontology class instances
        """
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?object WHERE {{
            GRAPH <{self.kgraph.graph_uri}> {{
                ?object rdf:type kg:{object_type} .
            }}
        }}
        {limit_clause}
        """
        
        results = self.kgraph.sparql_query(query)
        
        # Convert URIs to ontology class instances
        instances = []
        for result in results:
            # Handle both '?object' and 'object' key formats
            object_uri = result.get('object') or result.get('?object')
            if object_uri:
                # Clean URI by removing angle brackets if present
                object_uri = object_uri.strip('<>')
            if object_uri:
                instance = self.kgraph.get_object(object_uri)
                if instance:
                    instances.append(instance)
        
        return instances
    
    def get_object_properties(self, object_uri: str) -> Dict[str, Any]:
        """
        Get all properties of an object.
        
        Args:
            object_uri: URI of object
            
        Returns:
            Dictionary of property-value pairs
        """
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?property ?value WHERE {{
            <{object_uri}> ?property ?value .
        }}
        """
        
        results = self.kgraph.sparql_query(query)
        properties = {}
        for result in results:
            prop = result.get('property', '')
            value = result.get('value', '')
            # Extract property name from URI
            if '#' in prop:
                prop_name = prop.split('#')[-1]
            else:
                prop_name = prop.split('/')[-1]
            properties[prop_name] = value
        
        return properties
    
    def update_object_properties(self, object_uri: str, **properties) -> bool:
        """
        Update properties of an existing object.
        
        Args:
            object_uri: URI of object to update
            **properties: Properties to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the object instance from the graph
            obj = self.kgraph.get_object(object_uri)
            if not obj:
                print(f"Warning: Object {object_uri} not found or could not be reconstructed as instance")
                return False
            
            # Get allowed properties for this object type
            allowed_props = {}
            try:
                allowed_list = obj.get_allowed_properties()
                for prop_info in allowed_list:
                    uri = prop_info['uri']
                    # Extract property name from URI
                    prop_name = uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]
                    # Map common property patterns
                    if prop_name == 'hasName':
                        prop_name = 'name'
                    elif prop_name == 'hasKGraphDescription':
                        prop_name = 'kGraphDescription'
                    allowed_props[prop_name] = uri
            except:
                # Fallback to direct property setting if get_allowed_properties fails
                pass
            
            # Update properties
            for prop_name, prop_value in properties.items():
                # Try direct property name first
                if hasattr(obj, prop_name):
                    setattr(obj, prop_name, prop_value)
                # Try mapped property name
                elif prop_name in allowed_props and hasattr(obj, prop_name):
                    setattr(obj, prop_name, prop_value)
                else:
                    print(f"Warning: Property {prop_name} not found on object {object_uri}")
            
            # Update the object in the graph
            self.kgraph.update_object(obj)
            return True
            
        except Exception as e:
            print(f"Warning: Could not update object {object_uri}: {e}")
            return False
    

    def delete_object_and_edges(self, object_uri: str) -> bool:
        """
        Delete an object and all its associated edges.
        
        Args:
            object_uri: URI of object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, find and delete all edges connected to this object
            edge_query = f"""
            PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
            
            SELECT ?edge WHERE {{
                ?edge a ?edgeType ;
                      ?sourceProp <{object_uri}> .
                FILTER(STRSTARTS(STR(?edgeType), "http://vital.ai/ontology/haley-ai-kg#Edge_"))
            }}
            UNION
            {{
                ?edge a ?edgeType ;
                      ?destProp <{object_uri}> .
                FILTER(STRSTARTS(STR(?edgeType), "http://vital.ai/ontology/haley-ai-kg#Edge_"))
            }}
            """
            
            edge_results = self.kgraph.sparql_query(edge_query)
            
            # Delete each edge
            for result in edge_results:
                edge_uri = result.get('edge')
                if edge_uri:
                    try:
                        if hasattr(self.kgraph, 'delete_object_by_uri'):
                            self.kgraph.delete_object_by_uri(edge_uri)
                        else:
                            # Fallback to remove_object if delete_object_by_uri doesn't exist
                            edge_obj = self.kgraph.get_object(edge_uri)
                            if edge_obj:
                                self.kgraph.remove_object(edge_obj)
                    except:
                        pass  # Continue even if edge deletion fails
            
            # Delete the object itself
            try:
                if hasattr(self.kgraph, 'delete_object_by_uri'):
                    success = self.kgraph.delete_object_by_uri(object_uri)
                else:
                    # Fallback to remove_object if delete_object_by_uri doesn't exist
                    obj = self.kgraph.get_object(object_uri)
                    if obj:
                        success = self.kgraph.remove_object(obj)
                    else:
                        success = False
            except Exception as e:
                print(f"Warning: Could not delete object {object_uri}: {e}")
                success = False
            
            return success
            
        except Exception as e:
            print(f"Warning: Could not delete object {object_uri}: {e}")
            return False
    
    # ============================================================================
    # SLOT AND FRAME UTILITIES
    # ============================================================================
    
    def create_text_slot(self, slot_name: str, value: str) -> str:
        """
        Create a text slot with a value.
        
        Args:
            slot_name: Name of the slot
            value: Text value
            
        Returns:
            URI of created slot
        """
        try:
            from ai_haley_kg_domain.model.KGTextSlot import KGTextSlot
            
            slot = KGTextSlot()
            slot.URI = URIGenerator.generate_uri()
            slot.hasName = slot_name
            slot.hasKGSlotTextValue = value
            
            self.kgraph.add_object(slot)
            return str(slot.URI)
            
        except ImportError:
            raise ImportError("KGTextSlot class not available")
    
    def create_datetime_slot(self, slot_name: str, value: datetime) -> str:
        """
        Create a datetime slot with a value.
        
        Args:
            slot_name: Name of the slot
            value: DateTime value
            
        Returns:
            URI of created slot
        """
        try:
            from ai_haley_kg_domain.model.KGDateTimeSlot import KGDateTimeSlot
            
            slot = KGDateTimeSlot()
            slot.URI = URIGenerator.generate_uri()
            slot.hasName = slot_name
            slot.hasKGSlotDateTimeValue = value.isoformat()
            
            self.kgraph.add_object(slot)
            return str(slot.URI)
            
        except ImportError:
            raise ImportError("KGDateTimeSlot class not available")
    
    def create_boolean_slot(self, slot_name: str, value: bool) -> str:
        """
        Create a boolean slot with a value.
        
        Args:
            slot_name: Name of the slot
            value: Boolean value
            
        Returns:
            URI of created slot
        """
        try:
            from ai_haley_kg_domain.model.KGBooleanSlot import KGBooleanSlot
            
            slot = KGBooleanSlot()
            slot.URI = URIGenerator.generate_uri()
            slot.hasName = slot_name
            slot.hasKGSlotBooleanValue = value
            
            self.kgraph.add_object(slot)
            return str(slot.URI)
            
        except ImportError:
            raise ImportError("KGBooleanSlot class not available")
    
    def create_frame_with_slots(self, frame_name: str, frame_type: str,
                               slots: Dict[str, Any]) -> str:
        """
        Create a frame with multiple slots.
        
        Args:
            frame_name: Name of the frame
            frame_type: Type of the frame
            slots: Dictionary of slot_name -> value pairs
            
        Returns:
            URI of created frame
        """
        try:
            from ai_haley_kg_domain.model.KGFrame import KGFrame
            
            frame = KGFrame()
            frame.URI = URIGenerator.generate_uri()
            frame.hasName = frame_name
            frame.hasKGFrameType = frame_type
            
            self.kgraph.add_object(frame)
            frame_uri = str(frame.URI)
            
            # Create and link slots
            for slot_name, value in slots.items():
                if isinstance(value, str):
                    slot_uri = self.create_text_slot(slot_name, value)
                elif isinstance(value, datetime):
                    slot_uri = self.create_datetime_slot(slot_name, value)
                elif isinstance(value, bool):
                    slot_uri = self.create_boolean_slot(slot_name, value)
                else:
                    # Convert to string as fallback
                    slot_uri = self.create_text_slot(slot_name, str(value))
                
                self.link_slot_to_frame(slot_uri, frame_uri)
            
            return frame_uri
            
        except ImportError:
            raise ImportError("KGFrame class not available")
    
    # ============================================================================
    # SEARCH AND FILTER UTILITIES
    # ============================================================================
    
    def search_by_type(self, query: str, object_type: str, 
                      limit: int = 10, vector_id: str = "general") -> List[Dict[str, Any]]:
        """
        Vector search for objects of a specific type using a specific vector.
        
        Args:
            query: Search query
            object_type: Type of objects to search
            limit: Maximum results
            vector_id: Which vector to search ("general", "description", "name", etc.)
            
        Returns:
            List of search results
        """
        # Use vector_search_by_type which supports vector_id parameter
        # Temporarily remove object_type filter to test if vector search works
        # TODO: Fix metadata filtering - the object_type filter might be causing issues
        return self.kgraph.vector_search_by_type(query, vector_id, limit=limit)
    
    def filter_by_property(self, object_type: str, property_name: str,
                          property_value: str, limit: int = None) -> List[Any]:
        """
        Filter objects by a specific property value as ontology class instances.
        
        Args:
            object_type: Type of objects to filter
            property_name: Name of property to filter by
            property_value: Value to match
            limit: Optional limit on results
            
        Returns:
            List of matching ontology class instances
        """
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?object WHERE {{
            GRAPH <{self.kgraph.graph_uri}> {{
                ?object a kg:{object_type} ;
                        vital-core:{property_name} "{property_value}" .
            }}
        }}
        {limit_clause}
        """
        
        results = self.kgraph.sparql_query(query)
        
        # Convert URIs to ontology class instances
        instances = []
        for result in results:
            # Handle both '?object' and 'object' key formats
            object_uri = result.get('object') or result.get('?object')
            if object_uri:
                # Clean URI by removing angle brackets if present
                object_uri = object_uri.strip('<>')
            if object_uri:
                instance = self.kgraph.get_object(object_uri)
                if instance:
                    instances.append(instance)
        
        return instances
    
    # ============================================================================
    # VALIDATION AND UTILITY METHODS
    # ============================================================================
    
    def validate_uri(self, uri: str) -> bool:
        """
        Validate that a URI exists in the graph.
        
        Args:
            uri: URI to validate
            
        Returns:
            True if URI exists, False otherwise
        """
        try:
            obj = self.kgraph.get_object(uri)
            return obj is not None
        except:
            return False
    
    def get_object_type(self, uri: str) -> Optional[str]:
        """
        Get the type of an object by its URI.
        
        Args:
            uri: URI of object
            
        Returns:
            Object type or None if not found
        """
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        
        SELECT ?type WHERE {{
            <{uri}> a ?type .
            FILTER(STRSTARTS(STR(?type), "http://vital.ai/ontology/haley-ai-kg#"))
        }}
        LIMIT 1
        """
        
        results = self.kgraph.sparql_query(query)
        if results:
            type_uri = results[0].get('type', '')
            if '#' in type_uri:
                return type_uri.split('#')[-1]
        return None
    
    def generate_timestamp(self) -> str:
        """
        Generate a standardized timestamp string.
        
        Returns:
            ISO format timestamp string
        """
        return datetime.now().isoformat()
    
    def generate_name_with_timestamp(self, base_name: str) -> str:
        """
        Generate a name with timestamp suffix.
        
        Args:
            base_name: Base name to use
            
        Returns:
            Name with timestamp suffix
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}"
