from typing import List, Dict, Any, Optional
from vital_ai_vitalsigns.embedding.embedding_model import EmbeddingModel
from .kgraph import KGraph
from .default_vector_mappings import get_default_mappings


class KGraphMemory:
    """
    Memory manager for multiple KGraphs.
    Manages creation, removal, lookup, and listing of KGraphs.
    Ensures all KGraphs are created with the same embedding model.
    """
    
    def __init__(self, embedding_model: EmbeddingModel, 
                 default_vector_mappings: Optional[Dict[str, Dict[str, List[str]]]] = None):
        """
        Initialize the KGraphMemory manager.
        
        Args:
            embedding_model: EmbeddingModel to be used by all KGraphs
            default_vector_mappings: Optional default vector mappings for all KGraphs
        """
        self.embedding_model = embedding_model
        self.default_vector_mappings = default_vector_mappings or get_default_mappings()
        
        # Registry of managed KGraphs
        self._kgraphs: Dict[str, KGraph] = {}
        
    def create_kgraph(self, graph_id: str, graph_uri: str,
                      vector_mappings: Optional[Dict[str, Dict[str, List[str]]]] = None) -> KGraph:
        """
        Create a new KGraph and add it to the memory.
        
        Args:
            graph_id: Unique identifier for the KGraph
            graph_uri: Named graph URI for RDF triples
            vector_mappings: Optional custom vector mappings (uses default if not provided)
            
        Returns:
            The created KGraph instance
            
        Raises:
            ValueError: If graph_id already exists
        """
        if graph_id in self._kgraphs:
            raise ValueError(f"KGraph with ID '{graph_id}' already exists")
        
        # Use provided mappings or default
        mappings = vector_mappings if vector_mappings else self.default_vector_mappings
        
        # Create the KGraph
        kgraph = KGraph(
            graph_id=graph_id,
            embedding_model=self.embedding_model,
            graph_uri=graph_uri,
            vector_mappings=mappings
        )
        
        # Register it
        self._kgraphs[graph_id] = kgraph
        
        return kgraph
    
    def get_kgraph(self, graph_id: str) -> Optional[KGraph]:
        """
        Get a KGraph by its ID.
        
        Args:
            graph_id: ID of the KGraph to retrieve
            
        Returns:
            KGraph instance or None if not found
        """
        return self._kgraphs.get(graph_id)
    
    def remove_kgraph(self, graph_id: str) -> bool:
        """
        Remove a KGraph from memory.
        
        Args:
            graph_id: ID of the KGraph to remove
            
        Returns:
            True if removed, False if not found
        """
        if graph_id in self._kgraphs:
            # Clear the KGraph data before removing
            self._kgraphs[graph_id].clear()
            del self._kgraphs[graph_id]
            return True
        return False
    
    def list_kgraphs(self) -> List[str]:
        """
        Get a list of all KGraph IDs.
        
        Returns:
            List of KGraph IDs
        """
        return list(self._kgraphs.keys())
    
    def has_kgraph(self, graph_id: str) -> bool:
        """
        Check if a KGraph exists.
        
        Args:
            graph_id: ID of the KGraph to check
            
        Returns:
            True if exists, False otherwise
        """
        return graph_id in self._kgraphs
    
    def get_kgraph_stats(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific KGraph.
        
        Args:
            graph_id: ID of the KGraph
            
        Returns:
            Statistics dictionary or None if not found
        """
        kgraph = self.get_kgraph(graph_id)
        return kgraph.get_stats() if kgraph else None
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all KGraphs.
        
        Returns:
            Dictionary mapping graph_id to statistics
        """
        return {
            graph_id: kgraph.get_stats()
            for graph_id, kgraph in self._kgraphs.items()
        }
    
    def clear_all(self):
        """
        Clear all KGraphs from memory.
        """
        for kgraph in self._kgraphs.values():
            kgraph.clear()
        self._kgraphs.clear()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get overall memory statistics.
        
        Returns:
            Dictionary with memory-level statistics
        """
        total_rdf_triples = 0
        total_vector_records = 0
        total_objects = 0
        
        for kgraph in self._kgraphs.values():
            stats = kgraph.get_stats()
            total_rdf_triples += stats['rdf_triple_count']
            total_vector_records += stats['vector_record_count']
            total_objects += stats['registered_objects']
        
        return {
            'total_kgraphs': len(self._kgraphs),
            'kgraph_ids': list(self._kgraphs.keys()),
            'total_rdf_triples': total_rdf_triples,
            'total_vector_records': total_vector_records,
            'total_objects': total_objects,
            'embedding_model_id': self.embedding_model.get_model_id()
        }
    
    def search_across_kgraphs(self, query_text: str, vector_id: Optional[str] = None,
                              limit_per_graph: int = 5, 
                              filters: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all KGraphs in memory.
        
        Args:
            query_text: Text to search for
            vector_id: Optional specific vector type to search
            limit_per_graph: Maximum results per KGraph
            filters: Optional metadata filters
            
        Returns:
            Dictionary mapping graph_id to search results
        """
        results = {}
        
        for graph_id, kgraph in self._kgraphs.items():
            try:
                if vector_id:
                    graph_results = kgraph.vector_search_by_type(
                        query_text=query_text,
                        vector_id=vector_id,
                        limit=limit_per_graph,
                        filters=filters
                    )
                else:
                    graph_results = kgraph.vector_search(
                        query_text=query_text,
                        limit=limit_per_graph,
                        filters=filters
                    )
                
                if graph_results:
                    results[graph_id] = graph_results
                    
            except Exception as e:
                print(f"Error searching KGraph '{graph_id}': {e}")
                
        return results
    
    def sparql_query_across_kgraphs(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute a SPARQL query across all KGraphs.
        
        Args:
            query: SPARQL query string
            
        Returns:
            Dictionary mapping graph_id to query results
        """
        results = {}
        
        for graph_id, kgraph in self._kgraphs.items():
            try:
                graph_results = kgraph.sparql_query(query)
                if graph_results:
                    results[graph_id] = graph_results
            except Exception as e:
                print(f"Error executing SPARQL on KGraph '{graph_id}': {e}")
                
        return results
    
    def get_embedding_model(self) -> EmbeddingModel:
        """
        Get the embedding model used by this memory.
        
        Returns:
            The EmbeddingModel instance
        """
        return self.embedding_model
    
    def update_default_vector_mappings(self, new_mappings: Dict[str, Dict[str, List[str]]]):
        """
        Update the default vector mappings for future KGraphs.
        Note: This does not affect existing KGraphs.
        
        Args:
            new_mappings: New default vector mappings
        """
        self.default_vector_mappings = new_mappings
    
    def count(self) -> int:
        """
        Get the number of KGraphs in memory.
        
        Returns:
            Number of KGraphs
        """
        return len(self._kgraphs)