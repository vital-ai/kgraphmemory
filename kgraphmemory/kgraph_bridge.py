"""
KGraphBridge - High-level bridge interface for KGraph that provides intuitive access
to knowledge graph operations for AI agents.

This class encapsulates a KGraph instance and provides specialized bridge classes
for different object types and interaction patterns.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from .kgraph import KGraph
from .kgraph_interaction_bridge import KGraphInteractionBridge
from .kgraph_chat_bridge import KGraphChatBridge
from .kgraph_task_bridge import KGraphTaskBridge
from .kgraph_entity_bridge import KGraphEntityBridge
from .kgraph_document_bridge import KGraphDocumentBridge
from .kgraph_tool_bridge import KGraphToolBridge
from .kgraph_frame_bridge import KGraphFrameBridge


class KGraphBridge:
    """
    High-level bridge interface for KGraph that provides intuitive access to
    knowledge graph operations through specialized bridge classes.
    
    This class acts as the main entry point for AI agents to interact with
    the knowledge graph, delegating to specialized bridge classes for different
    object types and interaction patterns.
    """
    
    def __init__(self, graph_id: str, embedding_model, graph_uri: str,
                 vector_mappings: Dict[str, Any] = None):
        """
        Initialize the KGraphBridge.
        
        Args:
            graph_id: Unique identifier for the graph
            embedding_model: Embedding model for vector operations
            graph_uri: URI for the named graph
            vector_mappings: Optional custom vector mappings
        """
        self.graph_id = graph_id
        self.graph_uri = graph_uri
        
        # Create the underlying KGraph instance
        self.kgraph = KGraph(graph_id, embedding_model, graph_uri, vector_mappings)
        
        # Initialize specialized bridge classes with parent bridge reference
        # This allows helpers to access other helpers for cross-object queries
        self.interactions = KGraphInteractionBridge(self.kgraph, self)
        self.chat = KGraphChatBridge(self.kgraph, self)
        self.tasks = KGraphTaskBridge(self.kgraph, self)
        self.entities = KGraphEntityBridge(self.kgraph, self)
        self.documents = KGraphDocumentBridge(self.kgraph, self)
        self.tools = KGraphToolBridge(self.kgraph, self)
        self.frames = KGraphFrameBridge(self.kgraph, self)
    

    
    # ============================================================================
    # DIRECT KGRAPH ACCESS
    # ============================================================================
    
    def add_object(self, graph_object):
        """Add an object directly to the underlying KGraph."""
        return self.kgraph.add_object(graph_object)
    
    def get_object_by_uri(self, object_uri: str):
        """Get an object by its URI."""
        return self.kgraph.get_object(object_uri)
    
    def sparql_query(self, query: str):
        """Execute a SPARQL query on the underlying KGraph."""
        return self.kgraph.sparql_query(query)
    
    def vector_search(self, query: str, vector_id: str = None, limit: int = 10,
                     filters: Dict[str, Any] = None):
        """Perform vector search on the underlying KGraph."""
        return self.kgraph.vector_search(query, vector_id, limit, filters)
    
    def hybrid_search(self, query: str, sparql_filter: str = None,
                     vector_filters: Dict[str, Any] = None, limit: int = 10):
        """Perform hybrid search on the underlying KGraph."""
        return self.kgraph.hybrid_search(query, sparql_filter, vector_filters, limit)
    
    # ============================================================================
    # CONVENIENCE METHODS FOR COMMON PATTERNS
    # ============================================================================
    

    
    def add_user_message(self, content: str, interaction_uri: str, 
                        user_name: str = None) -> str:
        """Add a user message to an interaction."""
        return self.interactions.add_user_message(content, user_name, interaction_uri)
    
    def add_bot_message(self, content: str, interaction_uri: str,
                       agent_name: str = None) -> str:
        """Add a bot message to an interaction."""
        return self.interactions.add_bot_message(content, agent_name, interaction_uri)
    
    def create_person_with_address(self, name: str, street: str = None,
                                  city: str = None, state: str = None,
                                  zip_code: str = None, country: str = None) -> str:
        """Create a person entity with an address frame."""
        return self.entities.create_person_with_address(
            name, street, city, state, zip_code, country
        )
    
    def create_task_for_interaction(self, name: str, interaction_uri: str,
                                   description: str = None, task_type: str = None) -> str:
        """Create a task and link it to an interaction."""
        return self.tasks.create_task_for_interaction(name, interaction_uri, description, task_type)
    
    def store_tool_request(self, tool_name: str, request_data: str, interaction_uri: str) -> str:
        """Store a tool request in memory (does not execute the tool)."""
        return self.tools.store_tool_request(tool_name, request_data, interaction_uri)
    
    def store_tool_response(self, request_uri: str, response_data: str, success: bool = True) -> str:
        """Store a tool response in memory for a previously stored request."""
        return self.tools.store_tool_response(request_uri, response_data, success)
    
    # ============================================================================
    # CONTEXT AND SEARCH METHODS
    # ============================================================================
    
    def get_interaction_context(self, interaction_uri: str,
                               include_messages: bool = True,
                               include_entities: bool = True,
                               include_documents: bool = True,
                               include_tasks: bool = True) -> Dict[str, Any]:
        """Get comprehensive context for an interaction."""
        return self.interactions.get_interaction_context(
            interaction_uri, include_messages, include_entities,
            include_documents, include_tasks
        )
    
    def search_all(self, query: str, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all object types."""
        return {
            'entities': self.entities.search(query, limit=limit),
            'documents': self.documents.search(query, limit=limit),
            'tasks': self.tasks.search(query, limit=limit),
            'interactions': self.interactions.search(query, limit=limit),
            'chat_interactions': self.chat.search_chat_interactions(query, limit=limit),
            'chat_messages': self.chat.search_chat_messages(query, limit=limit),
            'frames': self.frames.search(query, limit=limit)
        }
    
    # ============================================================================
    # STATISTICS AND MANAGEMENT
    # ============================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from the underlying KGraph."""
        return self.kgraph.get_stats()
    
    def clear(self):
        """Clear all data from the underlying KGraph."""
        self.kgraph.clear()
    
    def get_bridge_id(self) -> str:
        """Get the bridge identifier."""
        return self.graph_id
    
    def get_graph_uri(self) -> str:
        """Get the graph URI."""
        return self.graph_uri