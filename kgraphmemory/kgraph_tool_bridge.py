"""
KGraphToolBridge - Specialized bridge for managing tool requests and responses.

Handles KGTool, KGToolRequest, KGToolResult objects for storing tool interaction data in memory.
This bridge does NOT execute tools - it only stores tool requests and responses.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from .kgraph_bridge_utilities import KGraphBridgeUtilities

# Import ontology classes
try:
    from ai_haley_kg_domain.model.KGTool import KGTool
    from ai_haley_kg_domain.model.KGToolRequest import KGToolRequest
    from ai_haley_kg_domain.model.KGToolResult import KGToolResult
except ImportError as e:
    print(f"Warning: Could not import ontology classes: {e}")
    KGTool = None
    KGToolRequest = None
    KGToolResult = None


class KGraphToolBridge:
    """
    Specialized bridge for managing tool requests and responses in memory.
    
    Provides high-level methods for:
    - Creating and managing KGTool definitions
    - Storing KGToolRequest objects (tool invocation requests)
    - Storing KGToolResult objects (tool execution results)
    - Linking tool requests/results to interactions
    
    Note: This bridge does NOT execute tools - it only stores tool interaction data.
    """
    
    def __init__(self, kgraph, parent_bridge=None):
        """
        Initialize the tool bridge.
        
        Args:
            kgraph: KGraph instance
            parent_bridge: Parent KGraphBridge instance for cross-helper access
        """
        self.kgraph = kgraph
        self.parent_bridge = parent_bridge
        self.utils = KGraphBridgeUtilities(kgraph)
    
    # ============================================================================
    # TOOL DEFINITION MANAGEMENT
    # ============================================================================
    
    def create_tool(self, name: str, tool_type: str, description: str = None,
                   parameters_schema: str = None) -> str:
        """
        Create a tool definition.
        
        Args:
            name: Tool name
            tool_type: Type of tool (e.g., "api", "function", "service")
            description: Optional description
            parameters_schema: Optional JSON schema for tool parameters
            
        Returns:
            URI of created tool
        """
        tool_props = {
            'hasName': name,
            'hasKGToolType': tool_type
        }
        
        if description:
            tool_props['hasKGToolDescription'] = description
        if parameters_schema:
            tool_props['hasKGToolParametersSchema'] = parameters_schema
        
        tool_uri = self.utils.create_node('KGTool', **tool_props)
        if not tool_uri:
            raise RuntimeError("Failed to create tool")
        
        return tool_uri
    
    def get_tool_by_name(self, name: str) -> Optional[str]:
        """
        Get a tool URI by its name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool URI or None if not found
        """
        tools = self.utils.filter_by_property("KGTool", "hasName", name)
        return tools[0].get('object') if tools else None
    
    # ============================================================================
    # TOOL REQUEST STORAGE
    # ============================================================================
    
    def store_tool_request(self, tool_name: str, request_data: str,
                          interaction_uri: str, parameters: str = None) -> str:
        """
        Store a tool request in memory (does not execute the tool).
        
        Args:
            tool_name: Name of the tool being requested
            request_data: Request data/payload
            interaction_uri: URI of the interaction this request belongs to
            parameters: Optional parameters for the tool request
            
        Returns:
            URI of created tool request
        """
        # Get or create the tool
        tool_uri = self.get_tool_by_name(tool_name)
        if not tool_uri:
            tool_uri = self.create_tool(tool_name, "external_tool", f"Tool: {tool_name}")
        
        # Create the tool request
        request_props = {
            'hasName': self.utils.generate_name_with_timestamp("ToolRequest"),
            'hasKGToolRequestData': request_data,
            'hasKGToolRequestStatus': 'pending'
        }
        
        if parameters:
            request_props['hasKGToolRequestParameters'] = parameters
        
        # Create request and link to tool and interaction
        request_uri, edge_uri = self.utils.create_node_with_edge(
            'KGToolRequest',
            'Edge_hasKGTool',
            tool_uri,
            link_as_destination=False,  # Request is source, tool is destination
            **request_props
        )
        
        if not request_uri:
            raise RuntimeError("Failed to create tool request")
        
        # Link request to interaction
        self.utils.link_to_interaction(request_uri, interaction_uri, "KGToolRequest")
        
        return request_uri
    
    def update_tool_request_status(self, request_uri: str, status: str) -> bool:
        """
        Update the status of a tool request.
        
        Args:
            request_uri: URI of the tool request
            status: New status (e.g., 'pending', 'executing', 'completed', 'failed')
            
        Returns:
            True if updated successfully
        """
        try:
            request_obj = self.kgraph.get_object(request_uri)
            if request_obj:
                request_obj.hasKGToolRequestStatus = status
                self.kgraph.update_object(request_obj)
                return True
            return False
        except Exception as e:
            print(f"Warning: Failed to update tool request status: {e}")
            return False
    
    # ============================================================================
    # TOOL RESPONSE STORAGE
    # ============================================================================
    
    def store_tool_response(self, request_uri: str, response_data: str,
                           success: bool = True, error_message: str = None) -> str:
        """
        Store a tool response in memory for a previously stored request.
        
        Args:
            request_uri: URI of the tool request this responds to
            response_data: Response data/payload
            success: Whether the tool execution was successful
            error_message: Optional error message if execution failed
            
        Returns:
            URI of created tool result
        """
        result_props = {
            'hasName': self.utils.generate_name_with_timestamp("ToolResult"),
            'hasKGToolResultData': response_data,
            'hasKGToolResultSuccess': success
        }
        
        if error_message:
            result_props['hasKGToolResultError'] = error_message
        
        # Create result and link to request
        result_uri, edge_uri = self.utils.create_node_with_edge(
            'KGToolResult',
            'Edge_hasKGToolResult',
            request_uri,
            link_as_destination=True,  # Request is source, result is destination
            **result_props
        )
        
        if not result_uri:
            raise RuntimeError("Failed to create tool result")
        
        # Update request status
        status = 'completed' if success else 'failed'
        self.update_tool_request_status(request_uri, status)
        
        return result_uri
    
    # ============================================================================
    # TOOL INTERACTION QUERIES
    # ============================================================================
    
    def get_tool_requests_for_interaction(self, interaction_uri: str) -> List[Dict[str, Any]]:
        """
        Get all tool requests for an interaction.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            List of tool request dictionaries
        """
        return self.utils.get_linked_objects(interaction_uri, "KGToolRequest")
    
    def get_tool_results_for_request(self, request_uri: str) -> List[Dict[str, Any]]:
        """
        Get all results for a tool request.
        
        Args:
            request_uri: URI of the tool request
            
        Returns:
            List of tool result dictionaries
        """
        return self.utils.get_linked_objects(request_uri, "KGToolResult", "Edge_hasKGToolResult")
    
    def get_tool_request_with_results(self, request_uri: str) -> Dict[str, Any]:
        """
        Get a tool request with all its results.
        
        Args:
            request_uri: URI of the tool request
            
        Returns:
            Dictionary with request data and results
        """
        request_props = self.utils.get_object_properties(request_uri)
        results = self.get_tool_results_for_request(request_uri)
        
        return {
            'request_uri': request_uri,
            'request_properties': request_props,
            'results': results
        }
    
    def get_interaction_tool_summary(self, interaction_uri: str) -> Dict[str, Any]:
        """
        Get a summary of all tool interactions for an interaction.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            Dictionary with tool interaction summary
        """
        requests = self.get_tool_requests_for_interaction(interaction_uri)
        
        summary = {
            'interaction_uri': interaction_uri,
            'total_requests': len(requests),
            'requests_with_results': [],
            'pending_requests': [],
            'failed_requests': []
        }
        
        for request in requests:
            request_uri = request.get('object')
            if request_uri:
                request_data = self.get_tool_request_with_results(request_uri)
                
                # Categorize based on status
                status = request_data['request_properties'].get('hasKGToolRequestStatus', 'unknown')
                if status == 'pending':
                    summary['pending_requests'].append(request_data)
                elif status == 'failed':
                    summary['failed_requests'].append(request_data)
                else:
                    summary['requests_with_results'].append(request_data)
        
        return summary
    
    # ============================================================================
    # SEARCH AND FILTER
    # ============================================================================
    
    def search_tools(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tools using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of tool search results
        """
        return self.utils.search_by_type(query, "KGTool", limit)
    
    def get_tools_by_type(self, tool_type: str) -> List[Dict[str, Any]]:
        """
        Get all tools of a specific type.
        
        Args:
            tool_type: Type of tools to find
            
        Returns:
            List of tool dictionaries
        """
        return self.utils.filter_by_property("KGTool", "hasKGToolType", tool_type)
    
    def get_pending_tool_requests(self) -> List[Dict[str, Any]]:
        """
        Get all pending tool requests across all interactions.
        
        Returns:
            List of pending tool request dictionaries
        """
        return self.utils.filter_by_property("KGToolRequest", "hasKGToolRequestStatus", "pending")
