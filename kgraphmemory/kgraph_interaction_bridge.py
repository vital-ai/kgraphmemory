"""
KGraphInteractionBridge - Specialized bridge for managing general interactions.

Handles KGInteraction and related objects (excluding chat-specific functionality).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from .kgraph_bridge_utilities import KGraphBridgeUtilities

# Import ontology classes
try:
    from ai_haley_kg_domain.model.KGInteraction import KGInteraction
    from ai_haley_kg_domain.model.KGActor import KGActor
    from ai_haley_kg_domain.model.KGAgent import KGAgent
except ImportError as e:
    print(f"Warning: Could not import ontology classes: {e}")
    KGInteraction = None
    KGActor = None
    KGAgent = None


class KGraphInteractionBridge:
    """
    CRUD bridge for managing KGInteraction objects.
    
    Provides stateless CRUD operations for:
    - KGInteraction objects
    - Actor and agent objects
    - Edges linking actors/agents to interactions
    - Querying and retrieving interaction data
    """
    
    def __init__(self, kgraph, parent_bridge=None):
        """
        Initialize the interaction bridge.
        
        Args:
            kgraph: KGraph instance
            parent_bridge: Parent KGraphBridge instance for cross-helper access
        """
        self.kgraph = kgraph
        self.parent_bridge = parent_bridge
        self.utils = KGraphBridgeUtilities(kgraph)
    
    # ============================================================================
    # KGINTERACTION CRUD OPERATIONS
    # ============================================================================
    
    def create_interaction(self, *, interaction_instance=None, name: str = None, interaction_type: str = "general",
                          description: str = None) -> str:
        """
        Create a new KGInteraction object.
        
        Args:
            interaction_instance: Optional KGInteraction instance to add directly
            name: Interaction name (auto-generated if None and instance not provided)
            interaction_type: Type of interaction (used if instance not provided)
            description: Optional description (used if instance not provided)
            
        Returns:
            URI of created interaction
        """
        if interaction_instance is not None:
            # Add the provided interaction instance directly
            if self.kgraph.add_object(interaction_instance):
                return str(interaction_instance.URI)
            else:
                raise RuntimeError("Failed to add KGInteraction instance")
        
        # Create interaction from named parameters
        try:
            from ai_haley_kg_domain.model.KGInteraction import KGInteraction
            from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
            
            interaction = KGInteraction()
            interaction.URI = URIGenerator.generate_uri()
            interaction.name = name or self.utils.generate_name_with_timestamp("Interaction")
            
            # Add timestamp for date-based searches
            now = datetime.now()
            interaction.timestamp = int(now.timestamp() * 1000)  # Unix timestamp in milliseconds
            interaction.objectUpdateTime = now.isoformat() + "Z"  # ISO datetime for SPARQL
            
            if description:
                interaction.kGraphDescription = description
            
            interaction_uri = self.utils.create_node(interaction)
            
            if not interaction_uri:
                raise RuntimeError("Failed to create KGInteraction")
            
            return interaction_uri
            
        except ImportError:
            raise RuntimeError("KGInteraction class not available")
    
    def get_interaction(self, interaction_uri: str) -> Dict[str, Any]:
        """
        Get a KGInteraction object by URI.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            Dictionary with interaction properties
        """
        return self.utils.get_object_properties(interaction_uri)
    
    def update_interaction(self, interaction_uri: str, **properties) -> bool:
        """
        Update properties of a KGInteraction object.
        
        Args:
            interaction_uri: URI of the interaction
            **properties: Properties to update
            
        Returns:
            True if successful
        """
        return self.utils.update_object_properties(interaction_uri, **properties)
    
    def delete_interaction(self, interaction_uri: str) -> bool:
        """
        Delete a KGInteraction object and its edges.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            True if successful
        """
        return self.utils.delete_object_and_edges(interaction_uri)
    
    def query_interactions(self, interaction_type: str = None, limit: int = 10) -> List[Any]:
        """
        Query interactions by type as ontology class instances.
        
        Args:
            interaction_type: Optional type filter
            limit: Maximum results
            
        Returns:
            List of KGInteraction ontology class instances
        """
        if interaction_type:
            return self.utils.filter_by_property("KGInteraction", "hasKGInteractionType", interaction_type, limit)
        else:
            return self.utils.get_objects_by_type("KGInteraction", limit)
    
    # ============================================================================
    # ACTOR/AGENT CRUD OPERATIONS
    # ============================================================================
    
    def create_actor(self, *, actor_instance=None, name: str = None, actor_type: str = "user", description: str = None) -> str:
        """
        Create a KGActor object.
        
        Args:
            actor_instance: Optional KGActor instance to add directly
            name: Actor name (used if actor_instance not provided)
            actor_type: Type of actor (used if actor_instance not provided)
            description: Optional description (used if actor_instance not provided)
            
        Returns:
            URI of created actor
        """
        if actor_instance is not None:
            # Add the provided actor instance directly
            if self.kgraph.add_object(actor_instance):
                return str(actor_instance.URI)
            else:
                raise RuntimeError("Failed to add KGActor instance")
        
        # Create actor from named parameters
        if not name:
            raise ValueError("name is required when actor_instance is not provided")
        
        try:
            from ai_haley_kg_domain.model.KGActor import KGActor
            from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
            
            actor = KGActor()
            actor.URI = URIGenerator.generate_uri()
            actor.name = name
            
            if description:
                actor.kGraphDescription = description
            
            actor_uri = self.utils.create_node(actor)
            
            if not actor_uri:
                raise RuntimeError("Failed to create KGActor")
            
            return actor_uri
            
        except ImportError:
            raise RuntimeError("KGActor class not available")
    
    def create_agent(self, *, agent_instance=None, name: str = None, agent_type: str = "assistant", description: str = None) -> str:
        """
        Create a KGAgent object.
        
        Args:
            agent_instance: Optional KGAgent instance to add directly
            name: Agent name (used if agent_instance not provided)
            agent_type: Type of agent (used if agent_instance not provided)
            description: Optional description (used if agent_instance not provided)
            
        Returns:
            URI of created agent
        """
        if agent_instance is not None:
            # Add the provided agent instance directly
            if self.kgraph.add_object(agent_instance):
                return str(agent_instance.URI)
            else:
                raise RuntimeError("Failed to add KGAgent instance")
        
        # Create agent from named parameters
        if not name:
            raise ValueError("name is required when agent_instance is not provided")
        
        try:
            from ai_haley_kg_domain.model.KGAgent import KGAgent
            from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
            
            agent = KGAgent()
            agent.URI = URIGenerator.generate_uri()
            agent.name = name
            
            if description:
                agent.kGraphDescription = description
            
            agent_uri = self.utils.create_node(agent)
            
            if not agent_uri:
                raise RuntimeError("Failed to create KGAgent")
            
            return agent_uri
            
        except ImportError:
            raise RuntimeError("KGAgent class not available")
    
    def get_actor(self, actor_uri: str) -> Dict[str, Any]:
        """
        Get a KGActor object by URI.
        
        Args:
            actor_uri: URI of the actor
            
        Returns:
            Dictionary with actor properties
        """
        return self.utils.get_object_properties(actor_uri)
    
    def get_agent(self, agent_uri: str) -> Dict[str, Any]:
        """
        Get a KGAgent object by URI.
        
        Args:
            agent_uri: URI of the agent
            
        Returns:
            Dictionary with agent properties
        """
        return self.utils.get_object_properties(agent_uri)
    
    def update_actor(self, actor_uri: str, **properties) -> bool:
        """
        Update properties of a KGActor object.
        
        Args:
            actor_uri: URI of the actor
            **properties: Properties to update
            
        Returns:
            True if successful
        """
        return self.utils.update_object_properties(actor_uri, **properties)
    
    def update_agent(self, agent_uri: str, **properties) -> bool:
        """
        Update properties of a KGAgent object.
        
        Args:
            agent_uri: URI of the agent
            **properties: Properties to update
            
        Returns:
            True if successful
        """
        return self.utils.update_object_properties(agent_uri, **properties)
    
    def delete_actor(self, actor_uri: str) -> bool:
        """
        Delete a KGActor object and its edges.
        
        Args:
            actor_uri: URI of the actor
            
        Returns:
            True if successful
        """
        return self.utils.delete_object_and_edges(actor_uri)
    
    def delete_agent(self, agent_uri: str) -> bool:
        """
        Delete a KGAgent object and its edges.
        
        Args:
            agent_uri: URI of the agent
            
        Returns:
            True if successful
        """
        return self.utils.delete_object_and_edges(agent_uri)
    
    # ============================================================================
    # EDGE OPERATIONS (LINKING)
    # ============================================================================
    
    def link_actor_to_interaction(self, interaction_uri: str, actor_uri: str) -> str:
        """
        Create an edge linking an actor to an interaction.
        
        Args:
            interaction_uri: URI of interaction
            actor_uri: URI of actor
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGActor", interaction_uri, actor_uri)
    
    def link_agent_to_interaction(self, interaction_uri: str, agent_uri: str) -> str:
        """
        Create an edge linking an agent to an interaction.
        
        Args:
            interaction_uri: URI of interaction
            agent_uri: URI of agent
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGAgent", interaction_uri, agent_uri)
    
    def unlink_actor_from_interaction(self, interaction_uri: str, actor_uri: str) -> bool:
        """
        Remove edge linking an actor to an interaction.
        
        Args:
            interaction_uri: URI of interaction
            actor_uri: URI of actor
            
        Returns:
            True if successful
        """
        return self.utils.delete_edge("Edge_hasKGActor", interaction_uri, actor_uri)
    
    def unlink_agent_from_interaction(self, interaction_uri: str, agent_uri: str) -> bool:
        """
        Remove edge linking an agent to an interaction.
        
        Args:
            interaction_uri: URI of interaction
            agent_uri: URI of agent
            
        Returns:
            True if successful
        """
        return self.utils.delete_edge("Edge_hasKGAgent", interaction_uri, agent_uri)
    
    # ============================================================================
    # QUERY OPERATIONS
    # ============================================================================
    
    def get_linked_objects(self, interaction_uri: str, object_type: str) -> List[Any]:
        """
        Get objects linked to an interaction by type as ontology class instances.
        
        Args:
            interaction_uri: URI of the interaction
            object_type: Type of objects to retrieve ("KGEntity", "KGDocument", etc.)
            
        Returns:
            List of linked ontology class instances
        """
        return self.utils.get_linked_objects(interaction_uri, object_type)
    
    def get_interaction_actors(self, interaction_uri: str) -> List[Any]:
        """
        Get actors linked to an interaction as ontology class instances.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            List of KGActor ontology class instances
        """
        return self.get_linked_objects(interaction_uri, "KGActor")
    
    def get_interaction_agents(self, interaction_uri: str) -> List[Any]:
        """
        Get agents linked to an interaction as ontology class instances.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            List of KGAgent ontology class instances
        """
        return self.get_linked_objects(interaction_uri, "KGAgent")
    
    def search_interactions(self, query: str, limit: int = 10, vector_id: str = "general") -> List[Dict[str, Any]]:
        """
        Search for KGInteraction objects using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            vector_id: Which vector to search ("general", "description", "name")
            
        Returns:
            List of interaction search results
        """
        return self.utils.search_by_type(query, "KGInteraction", limit, vector_id)
    
    def search_actors(self, query: str, limit: int = 10, vector_id: str = "general") -> List[Dict[str, Any]]:
        """
        Search for KGActor objects using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            vector_id: Which vector to search ("general", "description", "name")
            
        Returns:
            List of actor search results
        """
        return self.utils.search_by_type(query, "KGActor", limit, vector_id)
    
    def search_agents(self, query: str, limit: int = 10, vector_id: str = "general") -> List[Dict[str, Any]]:
        """
        Search for KGAgent objects using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            vector_id: Which vector to search ("general", "description", "name")
            
        Returns:
            List of agent search results
        """
        return self.utils.search_by_type(query, "KGAgent", limit, vector_id)
    
    def search_interactions_by_date(self, start_date: str = None, end_date: str = None, 
                                   interaction_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search interactions by date range using SPARQL.
        
        Args:
            start_date: Start date in ISO format (e.g., "2023-01-01T00:00:00Z")
            end_date: End date in ISO format (e.g., "2023-12-31T23:59:59Z")
            interaction_type: Optional interaction type URI to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of interaction dictionaries with metadata
        """
        # Build SPARQL query for date-based search using hasObjectUpdateTime
        # Include the named graph from the KGraph instance
        graph_uri = self.kgraph.graph_uri
        query = f"""
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT ?interaction ?name ?type ?updateTime WHERE {{
                GRAPH <{graph_uri}> {{
                    ?interaction a <http://vital.ai/ontology/haley-ai-kg#KGInteraction> .
                    ?interaction <http://vital.ai/ontology/vital-core#hasName> ?name .
                    OPTIONAL {{ ?interaction <http://vital.ai/ontology/haley-ai-kg#hasKGInteractionType> ?type }}
                    OPTIONAL {{ ?interaction <http://vital.ai/ontology/vital-aimp#hasObjectUpdateTime> ?updateTime }}
                }}
        """
        
        # Add date filters if provided
        if start_date:
            query += f'                FILTER (?updateTime >= "{start_date}"^^xsd:dateTime)\n'
        if end_date:
            query += f'                FILTER (?updateTime <= "{end_date}"^^xsd:dateTime)\n'
        if interaction_type:
            query += f'                FILTER (?type = "{interaction_type}")\n'
            
        query += f"""
            }}
            ORDER BY DESC(?updateTime)
            LIMIT {limit}
        """
        
        results = self.kgraph.sparql_query(query)
        
        # Process results into structured format
        interactions = []
        for result in results:
            interaction_data = {
                'interaction_uri': result.get('?interaction'),
                'name': result.get('?name'),
                'type': result.get('?type'),
                'updateTime': result.get('?updateTime')
            }
            interactions.append(interaction_data)
        
        return interactions
