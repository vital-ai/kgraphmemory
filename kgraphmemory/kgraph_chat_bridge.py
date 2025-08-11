"""
KGraphChatBridge - Specialized bridge for managing chat interactions and messages.

Handles KGChatInteraction, KGChatMessage, and related chat-specific objects.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from .kgraph_bridge_utilities import KGraphBridgeUtilities

# Import ontology classes
try:
    from ai_haley_kg_domain.model.KGChatInteraction import KGChatInteraction
    from ai_haley_kg_domain.model.KGChatUserMessage import KGChatUserMessage
    from ai_haley_kg_domain.model.KGChatBotMessage import KGChatBotMessage
    from ai_haley_kg_domain.model.KGActor import KGActor
    from ai_haley_kg_domain.model.KGAgent import KGAgent
except ImportError as e:
    print(f"Warning: Could not import ontology classes: {e}")
    KGChatInteraction = None
    KGChatUserMessage = None
    KGChatBotMessage = None
    KGActor = None
    KGAgent = None


class KGraphChatBridge:
    """
    CRUD bridge for managing chat interactions and chat messages.
    
    Provides stateless CRUD operations for:
    - KGChatInteraction objects
    - KGChatUserMessage and KGChatBotMessage objects
    - Chat-specific actor and agent objects
    - Edges linking chat objects together
    - Querying and retrieving chat data
    """
    
    def __init__(self, kgraph, parent_bridge=None):
        """
        Initialize the chat bridge.
        
        Args:
            kgraph: KGraph instance
            parent_bridge: Parent KGraphBridge instance for cross-helper access
        """
        self.kgraph = kgraph
        self.parent_bridge = parent_bridge
        self.utils = KGraphBridgeUtilities(kgraph)
    
    # ============================================================================
    # KGCHATINTERACTION CRUD OPERATIONS
    # ============================================================================
    
    def create_chat_interaction(self, name: str = None, chat_type: str = "conversation",
                               description: str = None) -> str:
        """
        Create a new KGChatInteraction object.
        
        Args:
            name: Chat interaction name (auto-generated if None)
            chat_type: Type of chat interaction
            description: Optional description
            
        Returns:
            URI of created chat interaction
        """
        chat_props = {
            'hasName': name or self.utils.generate_name_with_timestamp("Chat"),
            'hasKGChatInteractionType': chat_type
        }
        
        if description:
            chat_props['hasKGChatInteractionDescription'] = description
        
        chat_interaction_uri = self.utils.create_node('KGChatInteraction', **chat_props)
        
        if not chat_interaction_uri:
            raise RuntimeError("Failed to create KGChatInteraction")
        
        return chat_interaction_uri
    
    def get_chat_interaction(self, chat_interaction_uri: str) -> Dict[str, Any]:
        """
        Get a KGChatInteraction object by URI.
        
        Args:
            chat_interaction_uri: URI of the chat interaction
            
        Returns:
            Dictionary with chat interaction properties
        """
        return self.utils.get_object_properties(chat_interaction_uri)
    
    def update_chat_interaction(self, chat_interaction_uri: str, **properties) -> bool:
        """
        Update properties of a KGChatInteraction object.
        
        Args:
            chat_interaction_uri: URI of the chat interaction
            **properties: Properties to update
            
        Returns:
            True if successful
        """
        return self.utils.update_object_properties(chat_interaction_uri, **properties)
    
    def delete_chat_interaction(self, chat_interaction_uri: str) -> bool:
        """
        Delete a KGChatInteraction object and its edges.
        
        Args:
            chat_interaction_uri: URI of the chat interaction
            
        Returns:
            True if successful
        """
        return self.utils.delete_object_and_edges(chat_interaction_uri)
    
    def query_chat_interactions(self, chat_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query KGChatInteraction objects by type.
        
        Args:
            chat_type: Optional type filter
            limit: Maximum results
            
        Returns:
            List of chat interaction objects
        """
        if chat_type:
            return self.utils.filter_by_property("KGChatInteraction", "hasKGChatInteractionType", chat_type, limit)
        else:
            return self.utils.get_objects_by_type("KGChatInteraction", limit)
    
    # ============================================================================
    # CHAT MESSAGE CRUD OPERATIONS
    # ============================================================================
    
    def create_user_message(self, content: str, user_name: str = None,
                           timestamp: str = None) -> str:
        """
        Create a KGChatUserMessage object.
        
        Args:
            content: Message content
            user_name: Optional user name
            timestamp: Optional timestamp
            
        Returns:
            URI of created user message
        """
        message_props = {
            'hasKGChatMessageContent': content,
            'hasKGChatMessageType': 'user'
        }
        
        if user_name:
            message_props['hasKGChatMessageActor'] = user_name
        
        if timestamp:
            message_props['hasKGChatMessageTimestamp'] = timestamp
        
        message_uri = self.utils.create_node('KGChatUserMessage', **message_props)
        
        if not message_uri:
            raise RuntimeError("Failed to create KGChatUserMessage")
        
        return message_uri
    
    def create_bot_message(self, content: str, agent_name: str = None,
                          timestamp: str = None) -> str:
        """
        Create a KGChatBotMessage object.
        
        Args:
            content: Message content
            agent_name: Optional agent name
            timestamp: Optional timestamp
            
        Returns:
            URI of created bot message
        """
        message_props = {
            'hasKGChatMessageContent': content,
            'hasKGChatMessageType': 'bot'
        }
        
        if agent_name:
            message_props['hasKGChatMessageActor'] = agent_name
        
        if timestamp:
            message_props['hasKGChatMessageTimestamp'] = timestamp
        
        message_uri = self.utils.create_node('KGChatBotMessage', **message_props)
        
        if not message_uri:
            raise RuntimeError("Failed to create KGChatBotMessage")
        
        return message_uri
    
    def get_chat_messages(self, interaction_uri: str, use_edge_traversal: bool = False) -> List[Dict[str, Any]]:
        """
        Get all chat messages for an interaction using SPARQL traversal.
        
        Args:
            interaction_uri: URI of the chat interaction
            use_edge_traversal: If True, use edge-based traversal; if False, use property-based
            
        Returns:
            List of message dictionaries with full details
        """
        if not interaction_uri:
            return []
        
        if use_edge_traversal:
            # Use edge-based traversal (similar to frame-slot pattern)
            query = f"""
            PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
            PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
            
            SELECT ?message ?messageClass ?content ?type ?timestamp ?actor ?actorName
            WHERE {{
                # Start from interaction and traverse via edges to messages
                <{interaction_uri}> a kg:KGChatInteraction .
                
                # Find edges connecting interaction to messages
                ?edge a kg:Edge_hasKGChatMessage .
                ?edge vital-core:hasEdgeSource <{interaction_uri}> .
                ?edge vital-core:hasEdgeDestination ?message .
                
                # Message properties
                ?message a ?messageClass .
                OPTIONAL {{ ?message kg:hasKGChatMessageContent ?content }}
                OPTIONAL {{ ?message kg:hasKGChatMessageType ?type }}
                OPTIONAL {{ ?message vital-core:hasTimestamp ?timestamp }}
                OPTIONAL {{ ?message kg:hasKGChatMessageActor ?actor }}
                
                # Actor details
                OPTIONAL {{
                    ?actor vital-core:hasName ?actorName
                }}
                
                FILTER(?messageClass = kg:KGChatUserMessage || ?messageClass = kg:KGChatBotMessage)
            }}
            ORDER BY ?timestamp
            """
        else:
            # Use property-based traversal (current approach)
            query = f"""
            PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
            PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
            
            SELECT ?message ?messageClass ?content ?type ?timestamp ?actor ?actorName
            WHERE {{
                ?message a ?messageClass ;
                         kg:hasKGChatMessageContent ?content ;
                         kg:hasKGChatMessageType ?type ;
                         vital-core:hasTimestamp ?timestamp .
                
                # Link to interaction via property
                ?message kg:hasKGChatInteractionURI <{interaction_uri}> .
                
                # Optional actor information
                OPTIONAL {{ ?message kg:hasKGChatMessageActor ?actor }}
                OPTIONAL {{
                    ?actor vital-core:hasName ?actorName
                }}
                
                FILTER(?messageClass = kg:KGChatUserMessage || ?messageClass = kg:KGChatBotMessage)
            }}
            ORDER BY ?timestamp
            """
        
        results = self.kgraph.sparql_query(query)
        
        # Process results into structured format
        messages = []
        for result in results:
            message_class = result.get('messageClass', '')
            message_type = message_class.split('#')[-1] if '#' in message_class else message_class
            
            message_data = {
                'message_uri': result.get('message'),
                'message_type': message_type,
                'content': result.get('content'),
                'type': result.get('type'),
                'timestamp': result.get('timestamp'),
                'actor_uri': result.get('actor'),
                'actor_name': result.get('actorName')
            }
            messages.append(message_data)
        
        return messages
    
    def get_user_message(self, message_uri: str) -> Dict[str, Any]:
        """
        Get a KGChatUserMessage object by URI.
        
        Args:
            message_uri: URI of the user message
            
        Returns:
            Dictionary with user message properties
        """
        return self.utils.get_object_properties(message_uri)
    
    def get_bot_message(self, message_uri: str) -> Dict[str, Any]:
        """
        Get a KGChatBotMessage object by URI.
        
        Args:
            message_uri: URI of the bot message
            
        Returns:
            Dictionary with bot message properties
        """
        return self.utils.get_object_properties(message_uri)
    
    def update_user_message(self, message_uri: str, **properties) -> bool:
        """
        Update properties of a KGChatUserMessage object.
        
        Args:
            message_uri: URI of the user message
            **properties: Properties to update
            
        Returns:
            True if successful
        """
        return self.utils.update_object_properties(message_uri, **properties)
    
    def update_bot_message(self, message_uri: str, **properties) -> bool:
        """
        Update properties of a KGChatBotMessage object.
        
        Args:
            message_uri: URI of the bot message
            **properties: Properties to update
            
        Returns:
            True if successful
        """
        return self.utils.update_object_properties(message_uri, **properties)
    
    def delete_user_message(self, message_uri: str) -> bool:
        """
        Delete a KGChatUserMessage object and its edges.
        
        Args:
            message_uri: URI of the user message
            
        Returns:
            True if successful
        """
        return self.utils.delete_object_and_edges(message_uri)
    
    def delete_bot_message(self, message_uri: str) -> bool:
        """
        Delete a KGChatBotMessage object and its edges.
        
        Args:
            message_uri: URI of the bot message
            
        Returns:
            True if successful
        """
        return self.utils.delete_object_and_edges(message_uri)
    
    # ============================================================================
    # EDGE OPERATIONS (LINKING)
    # ============================================================================
    
    def link_message_to_chat(self, chat_interaction_uri: str, message_uri: str) -> str:
        """
        Create an edge linking a message to a chat interaction.
        
        Args:
            chat_interaction_uri: URI of chat interaction
            message_uri: URI of message
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGChatMessage", chat_interaction_uri, message_uri)
    
    def unlink_message_from_chat(self, chat_interaction_uri: str, message_uri: str) -> bool:
        """
        Remove edge linking a message to a chat interaction.
        
        Args:
            chat_interaction_uri: URI of chat interaction
            message_uri: URI of message
            
        Returns:
            True if successful
        """
        return self.utils.delete_edge("Edge_hasKGChatMessage", chat_interaction_uri, message_uri)
    
    def link_chat_to_interaction(self, interaction_uri: str, chat_interaction_uri: str) -> str:
        """
        Create an edge linking a chat interaction to a general interaction.
        
        Args:
            interaction_uri: URI of general interaction
            chat_interaction_uri: URI of chat interaction
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGChatInteraction", interaction_uri, chat_interaction_uri)
    
    def unlink_chat_from_interaction(self, interaction_uri: str, chat_interaction_uri: str) -> bool:
        """
        Remove edge linking a chat interaction to a general interaction.
        
        Args:
            interaction_uri: URI of general interaction
            chat_interaction_uri: URI of chat interaction
            
        Returns:
            True if successful
        """
        return self.utils.delete_edge("Edge_hasKGChatInteraction", interaction_uri, chat_interaction_uri)
    
    # ============================================================================
    # CHAT ACTOR/AGENT CRUD OPERATIONS
    # ============================================================================
    
    def create_chat_actor(self, name: str, actor_type: str = "user", description: str = None) -> str:
        """
        Create a KGActor object for chat interactions.
        
        Args:
            name: Actor name
            actor_type: Type of actor
            description: Optional description
            
        Returns:
            URI of created actor
        """
        actor_props = {
            'hasName': name,
            'hasKGActorType': actor_type
        }
        
        if description:
            actor_props['hasKGActorDescription'] = description
        
        actor_uri = self.utils.create_node('KGActor', **actor_props)
        
        if not actor_uri:
            raise RuntimeError("Failed to create KGActor")
        
        return actor_uri
    
    def create_chat_agent(self, name: str, agent_type: str = "assistant") -> str:
        """
        Create an AI agent for chat interactions.
        
        Args:
            name: Agent name
            agent_type: Type of agent
            
        Returns:
            URI of created agent
        """
        agent_uri = self.utils.create_node(
            'KGAgent',
            hasName=name,
            hasKGAgentType=agent_type
        )
        
        if not agent_uri:
            raise RuntimeError("Failed to create chat agent")
        
        return agent_uri
    
    def link_actor_to_chat(self, interaction_uri: str, actor_uri: str) -> str:
        """
        Link an actor to a chat interaction.
        
        Args:
            interaction_uri: URI of chat interaction
            actor_uri: URI of actor
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGActor", interaction_uri, actor_uri)
    
    def link_agent_to_chat(self, interaction_uri: str, agent_uri: str) -> str:
        """
        Link an agent to a chat interaction.
        
        Args:
            interaction_uri: URI of chat interaction
            agent_uri: URI of agent
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGAgent", interaction_uri, agent_uri)
    
    # ============================================================================
    # CHAT CONTEXT AND SEARCH
    # ============================================================================
    
    def get_chat_context(self, interaction_uri: str,
                        include_entities: bool = True,
                        include_documents: bool = True,
                        include_tasks: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive context for a chat interaction.
        
        Args:
            interaction_uri: Chat interaction URI
            include_entities: Include linked entities
            include_documents: Include linked documents
            include_tasks: Include linked tasks
            
        Returns:
            Dictionary with chat context
        """
        if not interaction_uri:
            return {}
        
        context = {
            'interaction_uri': interaction_uri,
            'messages': self.get_chat_messages(interaction_uri),
            'entities': [],
            'documents': [],
            'tasks': [],
            'actors': [],
            'agents': []
        }
        
        if include_entities:
            context['entities'] = self.utils.get_linked_objects(interaction_uri, "KGEntity")
        
        if include_documents:
            context['documents'] = self.utils.get_linked_objects(interaction_uri, "KGDocument")
        
        if include_tasks:
            context['tasks'] = self.utils.get_linked_objects(interaction_uri, "KGTask")
        
        # Get actors and agents
        context['actors'] = self.utils.get_linked_objects(interaction_uri, "KGActor")
        context['agents'] = self.utils.get_linked_objects(interaction_uri, "KGAgent")
        
        return context
    
    def search_chat_interactions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for chat interactions using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of chat interaction search results
        """
        return self.utils.search_by_type(query, "KGChatInteraction", limit)
    
    def search_chat_messages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for chat messages using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of chat message search results
        """
        # Search both user and bot messages
        user_results = self.utils.search_by_type(query, "KGChatUserMessage", limit // 2)
        bot_results = self.utils.search_by_type(query, "KGChatBotMessage", limit // 2)
        
        # Combine and sort by score
        all_results = user_results + bot_results
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return all_results[:limit]
