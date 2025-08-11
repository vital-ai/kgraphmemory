"""
KGraphEntityBridge - Specialized bridge for managing entities and frames.

Handles KGEntity, KGFrame, KGSlot and related objects.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from .kgraph_bridge_utilities import KGraphBridgeUtilities

# Import ontology classes
try:
    from ai_haley_kg_domain.model.KGEntity import KGEntity
    from ai_haley_kg_domain.model.KGFrame import KGFrame
except ImportError as e:
    print(f"Warning: Could not import ontology classes: {e}")
    KGEntity = None
    KGFrame = None


class KGraphEntityBridge:
    """
    Specialized bridge for managing entities and frames.
    
    Provides high-level methods for creating and managing:
    - KGEntity objects (people, organizations, locations, etc.)
    - KGFrame objects (structured data containers)
    - KGSlot objects (typed data fields)
    - Entity-frame relationships
    """
    
    def __init__(self, kgraph, parent_bridge=None):
        """
        Initialize the entity bridge.
        
        Args:
            kgraph: KGraph instance
            parent_bridge: Parent KGraphBridge instance for cross-helper access
        """
        self.kgraph = kgraph
        self.parent_bridge = parent_bridge
        self.utils = KGraphBridgeUtilities(kgraph)
    
    # ============================================================================
    # ENTITY MANAGEMENT
    # ============================================================================
    
    def create_entity(self, name: str, entity_type: str = None,
                     description: str = None) -> str:
        """
        Create a new entity.
        
        Args:
            name: Entity name
            entity_type: Type of entity
            description: Optional description
            
        Returns:
            URI of created entity
        """
        if not KGEntity:
            raise ImportError("KGEntity class not available")
        
        entity = KGEntity()
        entity.URI = URIGenerator.generate_uri()
        entity.hasName = name
        
        if entity_type:
            entity.hasKGEntityType = entity_type
        if description:
            entity.hasKGEntityDescription = description
        
        self.kgraph.add_object(entity)
        return str(entity.URI)
    
    def create_person_entity(self, name: str, **attributes) -> str:
        """
        Create a person entity.
        
        Args:
            name: Person's name
            **attributes: Additional attributes
            
        Returns:
            URI of created person entity
        """
        return self.create_entity(name, "Person", f"Person named {name}")
    
    def create_organization_entity(self, name: str, org_type: str = None) -> str:
        """
        Create an organization entity.
        
        Args:
            name: Organization name
            org_type: Type of organization
            
        Returns:
            URI of created organization entity
        """
        description = f"Organization named {name}"
        if org_type:
            description += f" of type {org_type}"
        
        return self.create_entity(name, "Organization", description)
    
    def create_location_entity(self, name: str, location_type: str = None) -> str:
        """
        Create a location entity.
        
        Args:
            name: Location name
            location_type: Type of location (city, country, building, etc.)
            
        Returns:
            URI of created location entity
        """
        description = f"Location named {name}"
        if location_type:
            description += f" of type {location_type}"
        
        return self.create_entity(name, "Location", description)
    
    # ============================================================================
    # FRAME MANAGEMENT
    # ============================================================================
    
    def create_frame(self, name: str, frame_type: str = None,
                    description: str = None) -> str:
        """
        Create a new frame.
        
        Args:
            name: Frame name
            frame_type: Type of frame
            description: Optional description
            
        Returns:
            URI of created frame
        """
        if not KGFrame:
            raise ImportError("KGFrame class not available")
        
        frame = KGFrame()
        frame.URI = URIGenerator.generate_uri()
        frame.hasName = name
        
        if frame_type:
            frame.hasKGFrameType = frame_type
        if description:
            frame.hasKGFrameDescription = description
        
        self.kgraph.add_object(frame)
        return str(frame.URI)
    
    def create_address_frame(self, street: str = None, city: str = None,
                           state: str = None, zip_code: str = None,
                           country: str = None) -> str:
        """
        Create an address frame with slots for address components.
        
        Args:
            street: Street address
            city: City name
            state: State/province
            zip_code: ZIP/postal code
            country: Country
            
        Returns:
            URI of created address frame
        """
        slots = {}
        if street:
            slots['street'] = street
        if city:
            slots['city'] = city
        if state:
            slots['state'] = state
        if zip_code:
            slots['zip'] = zip_code
        if country:
            slots['country'] = country
        
        return self.utils.create_frame_with_slots("Address", "AddressFrame", slots)
    
    def create_contact_frame(self, email: str = None, phone: str = None,
                           website: str = None) -> str:
        """
        Create a contact information frame.
        
        Args:
            email: Email address
            phone: Phone number
            website: Website URL
            
        Returns:
            URI of created contact frame
        """
        slots = {}
        if email:
            slots['email'] = email
        if phone:
            slots['phone'] = phone
        if website:
            slots['website'] = website
        
        return self.utils.create_frame_with_slots("Contact", "ContactFrame", slots)
    
    # ============================================================================
    # ENTITY-FRAME RELATIONSHIPS
    # ============================================================================
    
    def add_address_to_entity(self, entity_uri: str, street: str = None,
                             city: str = None, state: str = None,
                             zip_code: str = None, country: str = None) -> str:
        """
        Add an address frame to an entity.
        
        Args:
            entity_uri: URI of entity
            street: Street address
            city: City name
            state: State/province
            zip_code: ZIP/postal code
            country: Country
            
        Returns:
            URI of created address frame
        """
        address_frame_uri = self.create_address_frame(street, city, state, zip_code, country)
        self.utils.link_frame_to_entity(address_frame_uri, entity_uri)
        return address_frame_uri
    
    def add_contact_to_entity(self, entity_uri: str, email: str = None,
                             phone: str = None, website: str = None) -> str:
        """
        Add a contact frame to an entity.
        
        Args:
            entity_uri: URI of entity
            email: Email address
            phone: Phone number
            website: Website URL
            
        Returns:
            URI of created contact frame
        """
        contact_frame_uri = self.create_contact_frame(email, phone, website)
        self.utils.link_frame_to_entity(contact_frame_uri, entity_uri)
        return contact_frame_uri
    
    def create_person_with_address(self, name: str, street: str = None,
                                  city: str = None, state: str = None,
                                  zip_code: str = None, country: str = None) -> str:
        """
        Create a person entity with an address frame in one operation.
        
        Args:
            name: Person's name
            street: Street address
            city: City name
            state: State/province
            zip_code: ZIP/postal code
            country: Country
            
        Returns:
            URI of created person entity
        """
        person_uri = self.create_person_entity(name)
        
        if any([street, city, state, zip_code, country]):
            self.add_address_to_entity(person_uri, street, city, state, zip_code, country)
        
        return person_uri
    
    def link_entity_to_frame(self, entity_uri: str, frame_uri: str) -> str:
        """
        Link an entity to a frame.
        
        Args:
            entity_uri: URI of entity
            frame_uri: URI of frame
            
        Returns:
            URI of created edge
        """
        return self.utils.link_frame_to_entity(frame_uri, entity_uri)
    
    # ============================================================================
    # SEARCH AND QUERY
    # ============================================================================
    
    def search(self, query: str, entity_type: str = None,
              limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for entities using vector similarity.
        
        Args:
            query: Search query
            entity_type: Optional entity type filter
            limit: Maximum results
            
        Returns:
            List of entity search results
        """
        filters = {}
        if entity_type:
            filters['entity_type'] = entity_type
        
        return self.utils.search_by_type(query, "KGEntity", limit)
    
    def get_entity_frames(self, entity_uri: str) -> List[Dict[str, Any]]:
        """
        Get all frames linked to an entity.
        
        Args:
            entity_uri: URI of entity
            
        Returns:
            List of frame dictionaries
        """
        return self.utils.get_linked_objects(entity_uri, "KGFrame", "Edge_hasKGFrame")
    
    def get_frame_slots(self, frame_uri: str) -> List[Dict[str, Any]]:
        """
        Get all slots in a frame.
        
        Args:
            frame_uri: URI of frame
            
        Returns:
            List of slot dictionaries
        """
        return self.utils.get_linked_objects(frame_uri, "KGSlot", "Edge_hasKGSlot")
    
    def get_entities_by_type(self, entity_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get all entities of a specific type.
        
        Args:
            entity_type: Type of entities to find
            limit: Optional limit on results
            
        Returns:
            List of entity dictionaries
        """
        return self.utils.filter_by_property("KGEntity", "hasKGEntityType", entity_type)
    
    def find_entities_with_address(self, city: str = None, state: str = None,
                                  country: str = None) -> List[Dict[str, Any]]:
        """
        Find entities that have address frames matching criteria.
        
        Args:
            city: City to match
            state: State to match
            country: Country to match
            
        Returns:
            List of entity dictionaries
        """
        # This would require a more complex SPARQL query to traverse entity->frame->slot relationships
        # For now, return a basic search
        search_terms = []
        if city:
            search_terms.append(city)
        if state:
            search_terms.append(state)
        if country:
            search_terms.append(country)
        
        if search_terms:
            query = " ".join(search_terms)
            return self.search(query)
        else:
            return []
