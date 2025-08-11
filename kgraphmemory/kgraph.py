from typing import List, Dict, Any, Optional, Union, Tuple, TypeVar
import uuid
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node
from vital_ai_vitalsigns.model.VITAL_Edge import VITAL_Edge

# Follow VitalSigns TypeVar pattern for GraphObject type annotations
G = TypeVar('G', bound=Optional['GraphObject'])
from vital_ai_vitalsigns.embedding.embedding_model import EmbeddingModel
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from .kgraph_rdf_db import KGraphRDFDB
from .kgraph_vector_db import KGraphVectorDB
from .default_vector_mappings import (
    get_default_mappings, get_vector_mappings_for_type, 
    get_vector_properties_for_type, get_available_vector_ids_for_type
)
import logging

class KGraph:
    """
    Unified knowledge graph that maintains data synchronization between RDF and vector stores.
    Supports standardized data objects (VITAL_Node, VITAL_Edge) with automatic conversion
    to triples and vectors based on configurable property mappings.
    """
    
    def __init__(self, graph_id: str, embedding_model: EmbeddingModel, graph_uri: str,
                 vector_mappings: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the KGraph with paired RDF and vector stores.
        
        Args:
            graph_id: Unique identifier for this graph instance
            embedding_model: EmbeddingModel for text vectorization
            graph_uri: Named graph URI for RDF triples
            vector_mappings: Optional custom property-to-vector mappings
        """
        self.graph_id = graph_id
        self.embedding_model = embedding_model
        self.graph_uri = graph_uri
        
        # Set up logger for this instance
        self.logger = logging.getLogger(f"KGraph.{graph_id}")
        self.logger.debug(f"Initializing KGraph: {graph_id} with graph_uri: {graph_uri}")
        
        # Use custom mappings or defaults
        self.vector_mappings = vector_mappings if vector_mappings else get_default_mappings()
        self.logger.debug(f"Vector mappings configured: {len(self.vector_mappings)} object types")
        
        # Initialize paired stores
        self.rdf_store = KGraphRDFDB(f"{graph_id}_rdf")
        self.vector_store = KGraphVectorDB(f"{graph_id}_vector", embedding_model)
        
        # Track object URIs for synchronization
        self._object_registry: Dict[str, str] = {}  # URI -> object_type mapping
    
    def add_object(self, graph_object: GraphObject) -> bool:
        """
        Add a GraphObject to both RDF and vector stores.
        
        Args:
            graph_object: Concrete GraphObject instance (e.g., KGEntity, VITAL_Node, VITAL_Edge).
                         Note: GraphObject is abstract - pass concrete subclass instances only.
            
        Returns:
            True if successfully added to both stores
        """
        try:
            object_uri = str(graph_object.URI)
            object_type = graph_object.get_class_uri()
            self.logger.debug(f"Adding object: {object_uri} of type: {object_type}")
            
            # Add RDF triples directly from object properties
            rdf_success = self._add_graph_object_triples(graph_object)
            
            # Convert to vector representations and add to vector store
            vector_data_list = self._graph_object_to_vector_data(graph_object)
            for vector_id, vector_text, metadata in vector_data_list:
                if vector_text:  
                    # Generate UUID-compatible record ID from URI and vector_id
                    import hashlib
                    import uuid
                    combined_string = f"{object_uri}#{vector_id}"
                    # Create a deterministic UUID from the combined string
                    namespace = uuid.NAMESPACE_URL
                    vector_record_id = str(uuid.uuid5(namespace, combined_string))
                    # Store the original URI in metadata for lookup
                    metadata['original_record_id'] = combined_string
                    self.vector_store.add_text(text=vector_text, metadata=metadata, record_id=vector_record_id)
            
            # Register object
            self._object_registry[object_uri] = object_type
            
            return True
            
        except Exception as e:
            print(f"Error adding object {graph_object.URI}: {e}")
            return False
    
    def add_objects(self, graph_objects: List[GraphObject]) -> int:
        """
        Add multiple GraphObjects in batch.
        
        Args:
            graph_objects: List of concrete GraphObject instances (e.g., KGEntity, VITAL_Node, VITAL_Edge).
                          Note: GraphObject is abstract - pass concrete subclass instances only.
            
        Returns:
            Number of objects successfully added
        """
        success_count = 0
        for obj in graph_objects:
            if self.add_object(obj):
                success_count += 1
        return success_count
    
    def update_object(self, graph_object: GraphObject) -> bool:
        """
        Update a GraphObject in both stores.
        
        Args:
            graph_object: Updated concrete GraphObject instance (e.g., KGEntity, VITAL_Node, VITAL_Edge).
                         Note: GraphObject is abstract - pass concrete subclass instances only.
            
        Returns:
            True if successfully updated
        """
        try:
            object_uri = str(graph_object.URI)
            object_type = graph_object.get_class_uri()
            
            # Remove existing triples for this object
            self.rdf_store.remove_triple(subject=object_uri, graph=self.graph_uri)
            
            # Remove all vector records for this object
            vector_ids = get_available_vector_ids_for_type(object_type, self.vector_mappings)
            for vector_id in vector_ids:
                vector_record_id = f"{object_uri}#{vector_id}"
                self.vector_store.delete(vector_record_id)
            
            # Add updated object
            return self.add_object(graph_object)
            
        except Exception as e:
            print(f"Error updating object {graph_object.URI}: {e}")
            return False
    
    def remove_object(self, object_uri: str) -> bool:
        """
        Remove an object from both stores.
        
        Args:
            object_uri: URI of the object to remove
            
        Returns:
            True if successfully removed
        """
        try:
            # Get object type for vector cleanup
            object_type = self._object_registry.get(object_uri)
            
            # Remove from RDF store (as subject)
            self.rdf_store.remove_triple(subject=object_uri, graph=self.graph_uri)
            
            # Remove from RDF store (as object in edges)
            self.rdf_store.remove_triple(obj=object_uri, graph=self.graph_uri)
            
            # Remove all vector records for this object
            if object_type:
                vector_ids = get_available_vector_ids_for_type(object_type, self.vector_mappings)
                for vector_id in vector_ids:
                    vector_record_id = f"{object_uri}#{vector_id}"
                    self.vector_store.delete(vector_record_id)
            
            # Remove from registry
            self._object_registry.pop(object_uri, None)
            
            return True
            
        except Exception as e:
            print(f"Error removing object {object_uri}: {e}")
            return False
    

    
    def sparql_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL query on the RDF store.
        
        Args:
            query: SPARQL query string
            
        Returns:
            List of result bindings
        """
        self.logger.debug(f"Executing SPARQL query via KGraph")
        results = self.rdf_store.sparql_query(query)
        self.logger.debug(f"SPARQL query returned {len(results)} results")
        return results
    
    def sparql_construct(self, query: str) -> List[tuple]:
        """
        Execute a SPARQL CONSTRUCT query on the RDF store.
        
        Args:
            query: SPARQL CONSTRUCT query string
            
        Returns:
            List of constructed triples
        """
        return self.rdf_store.sparql_construct(query)
    
    def sparql_ask(self, query: str) -> bool:
        """
        Execute a SPARQL ASK query on the RDF store.
        
        Args:
            query: SPARQL ASK query string
            
        Returns:
            Boolean result
        """
        return self.rdf_store.sparql_ask(query)
    
    def vector_search(self, query_text: str, limit: int = 10,
                      filters: Optional[Dict[str, Any]] = None,
                      score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search the vector store using text similarity (searches all vectors).
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            filters: Optional metadata filters
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and metadata
        """
        return self.vector_store.search_by_text(
            query_text=query_text,
            limit=limit,
            filters=filters,
            score_threshold=score_threshold
        )
    
    def vector_search_by_type(self, query_text: str, vector_id: str, limit: int = 10,
                              filters: Optional[Dict[str, Any]] = None,
                              score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search the vector store using text similarity for a specific vector type.
        
        Args:
            query_text: Text to search for
            vector_id: Specific vector ID to search (e.g., "type", "description", "general")
            limit: Maximum number of results
            filters: Optional metadata filters
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and metadata
        """
        # Add vector_id filter to existing filters
        if filters is None:
            filters = {}
        filters['vector_id'] = vector_id
        
        return self.vector_store.search_by_text(
            query_text=query_text,
            limit=limit,
            filters=filters,
            score_threshold=score_threshold
        )
    
    def vector_search_by_vector(self, query_vector: List[float], limit: int = 10,
                                filters: Optional[Dict[str, Any]] = None,
                                score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search the vector store using a vector.
        
        Args:
            query_vector: Vector to search with
            limit: Maximum number of results
            filters: Optional metadata filters
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and metadata
        """
        return self.vector_store.search_by_vector(
            query_vector=query_vector,
            limit=limit,
            filters=filters,
            score_threshold=score_threshold
        )
    
    def hybrid_search(self, query_text: str, sparql_filter: Optional[str] = None,
                      vector_filters: Optional[Dict[str, Any]] = None,
                      limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining SPARQL and vector similarity.
        
        Args:
            query_text: Text query for vector search
            sparql_filter: Optional SPARQL query to filter candidates
            vector_filters: Optional vector metadata filters
            limit: Maximum number of results
            
        Returns:
            Combined search results
        """
        # Get vector search results
        vector_results = self.vector_search(
            query_text=query_text,
            filters=vector_filters,
            limit=limit * 2  # Get more candidates for filtering
        )
        
        # If no SPARQL filter, return vector results
        if not sparql_filter:
            return vector_results[:limit]
        
        # Apply SPARQL filter to vector results
        filtered_results = []
        for result in vector_results:
            object_uri = result['id']
            
            # Check if object matches SPARQL filter
            ask_query = f"""
            ASK {{
                GRAPH <{self.graph_uri}> {{
                    <{object_uri}> ?p ?o .
                    {sparql_filter}
                }}
            }}
            """
            
            if self.sparql_ask(ask_query):
                # Enrich with RDF data
                rdf_data = self.get_object(object_uri)
                result['rdf_data'] = rdf_data
                filtered_results.append(result)
                
                if len(filtered_results) >= limit:
                    break
        
        return filtered_results
    
    def _add_graph_object_triples(self, graph_object: GraphObject) -> bool:
        """
        Add GraphObject properties as RDF triples by delegating to the RDF store.
        
        Args:
            graph_object: GraphObject to add
            
        Returns:
            True if successful
        """
        # Delegate all RDF-specific logic to the RDF database class
        return self.rdf_store.add_graph_object_triples(graph_object, self.graph_uri)
    

    def _graph_object_to_vector_data(self, graph_object: GraphObject) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Convert a GraphObject to vector data for multiple vectors.
        
        Args:
            graph_object: The GraphObject to convert
            
        Returns:
            List of tuples (vector_id, vector_text, metadata_dict)
        """
        object_uri = str(graph_object.URI)
        object_type = graph_object.get_class_uri()
        
        # Get all vector mappings for this type
        vector_mappings = get_vector_mappings_for_type(object_type, self.vector_mappings)
        
        # Get property values using the built-in to_json() method
        try:
            import json
            json_str = graph_object.to_json()
            obj_data = json.loads(json_str)
            
            # Create a mapping from property URIs to values
            property_values = {}
            
            # Get all property URIs we need for vector generation
            all_prop_uris = self._get_all_property_uris_from_mappings(vector_mappings)
            
            for prop_uri in all_prop_uris:
                # Look for the property URI directly in the JSON data
                if prop_uri in obj_data:
                    property_values[prop_uri] = obj_data[prop_uri]
                    
        except Exception as e:
            print(f"Error extracting properties from JSON: {e}")
            # Fallback: try to get property values directly using get_property_value
            property_values = {}
            all_prop_uris = self._get_all_property_uris_from_mappings(vector_mappings)
            
            for prop_uri in all_prop_uris:
                try:
                    value = graph_object.get_property_value(prop_uri)
                    if value is not None:
                        property_values[prop_uri] = value
                except:
                    continue
        
        # Base metadata shared across all vectors (store URIs directly)
        base_metadata = {
            'uri': object_uri,
            'type': object_type,
            'graph_uri': self.graph_uri
        }
        
        # Add property values to metadata using URIs as keys
        for prop_uri, prop_value in property_values.items():
            if prop_value is not None:
                base_metadata[prop_uri] = prop_value
        
        vector_data_list = []
        
        # Create a vector for each vector_id
        for vector_id, vector_property_uris in vector_mappings.items():
            # Extract text from specified property URIs for this vector
            text_parts = []
            
            for prop_uri in vector_property_uris:
                if prop_uri in property_values:
                    value = property_values[prop_uri]
                    if isinstance(value, str) and value.strip():
                        text_parts.append(value.strip())
            
            # Combine text parts for this vector
            vector_text = ' '.join(text_parts) if text_parts else ''
            
            # Create metadata specific to this vector (URIs as keys)
            vector_metadata = base_metadata.copy()
            vector_metadata['vector_id'] = vector_id
            vector_metadata['vector_property_uris'] = vector_property_uris
            
            vector_data_list.append((vector_id, vector_text, vector_metadata))
        
        return vector_data_list
    
    def _get_all_property_uris_from_mappings(self, vector_mappings: Dict[str, List[str]]) -> set:
        """
        Extract all unique property URIs from vector mappings.
        
        Args:
            vector_mappings: Dictionary of vector_id -> list of property URIs
            
        Returns:
            Set of all unique property URIs
        """
        all_uris = set()
        for vector_property_uris in vector_mappings.values():
            all_uris.update(vector_property_uris)
        return all_uris
    

    def get_object_vectors(self, object_uri: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all vector representations for a specific object.
        
        Args:
            object_uri: URI of the object
            
        Returns:
            Dictionary mapping vector_id to vector data
        """
        object_type = self._object_registry.get(object_uri)
        if not object_type:
            return {}
        
        vector_ids = get_available_vector_ids_for_type(object_type, self.vector_mappings)
        object_vectors = {}
        
        for vector_id in vector_ids:
            vector_record_id = f"{object_uri}#{vector_id}"
            vector_data = self.vector_store.get_by_id(vector_record_id)
            if vector_data:
                object_vectors[vector_id] = vector_data
        
        return object_vectors
    
    def get_available_vector_types_for_object(self, object_uri: str) -> List[str]:
        """
        Get available vector types for a specific object.
        
        Args:
            object_uri: URI of the object
            
        Returns:
            List of vector IDs available for this object
        """
        object_type = self._object_registry.get(object_uri)
        if not object_type:
            return []
        
        return get_available_vector_ids_for_type(object_type, self.vector_mappings)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the graph stores.
        
        Returns:
            Dictionary with store statistics
        """
        return {
            'graph_id': self.graph_id,
            'graph_uri': self.graph_uri,
            'rdf_triple_count': self.rdf_store.count_triples(),
            'vector_record_count': self.vector_store.count(),
            'registered_objects': len(self._object_registry),
            'vector_mappings_count': len(self.vector_mappings)
        }
    
    def clear(self):
        """
        Clear all data from both stores.
        """
        self.rdf_store.clear()
        self.vector_store.clear()
        self._object_registry.clear()
    
    def get_graph_id(self) -> str:
        """
        Get the graph identifier.
        
        Returns:
            Graph ID string
        """
        return self.graph_id
    
    def get_object(self, object_uri: str) -> G:
        """
        Retrieve a GraphObject by URI, converting RDF triples back to object.
        Delegates to KGraphRDFDB for proper RDF library handling.
        
        Args:
            object_uri: URI of the object to retrieve
            
        Returns:
            GraphObject instance or None if not found
        """
        return self.rdf_store.get_graph_object(object_uri, self.graph_uri)
    
    def get_objects_batch(self, object_uris: List[str]) -> Dict[str, G]:
        """
        Retrieve multiple GraphObjects by URIs in a single batch operation.
        Uses efficient pyoxigraph batch retrieval for better performance.
        
        Args:
            object_uris: List of URIs to retrieve
            
        Returns:
            Dictionary mapping URIs to GraphObject instances (excludes objects not found)
        """
        return self.rdf_store.get_graph_objects_batch(object_uris, self.graph_uri)
    
    def get_object_list(self, object_uris: List[str]) -> List[G]:
        """
        Retrieve multiple GraphObjects by URIs.
        
        Args:
            object_uris: List of URIs to retrieve
            
        Returns:
            List of GraphObject instances (excludes objects not found)
        """
        result_objects = []
        
        for uri in object_uris:
            obj = self.get_object(uri)
            if obj is not None:
                result_objects.append(obj)
        
        return result_objects