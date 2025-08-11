"""
KGraphDocumentBridge - Specialized bridge for managing documents and textual content.

Handles KGDocument and related objects for storing document information in memory.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from .kgraph_bridge_utilities import KGraphBridgeUtilities

# Import ontology classes
try:
    from ai_haley_kg_domain.model.KGDocument import KGDocument
except ImportError as e:
    print(f"Warning: Could not import ontology classes: {e}")
    KGDocument = None


class KGraphDocumentBridge:
    """
    Specialized bridge for managing documents and textual content.
    
    Provides high-level methods for:
    - Creating and managing KGDocument objects
    - Linking documents to interactions
    - Document search and retrieval
    - Document metadata management
    """
    
    def __init__(self, kgraph, parent_bridge=None):
        """
        Initialize the document bridge.
        
        Args:
            kgraph: KGraph instance
            parent_bridge: Parent KGraphBridge instance for cross-helper access
        """
        self.kgraph = kgraph
        self.parent_bridge = parent_bridge
        self.utils = KGraphBridgeUtilities(kgraph)
    
    # ============================================================================
    # DOCUMENT MANAGEMENT
    # ============================================================================
    
    def create_document(self, name: str, content: str, doc_type: str = None,
                       source: str = None, author: str = None) -> str:
        """
        Create a new document.
        
        Args:
            name: Document name/title
            content: Document content
            doc_type: Type of document (e.g., "text", "markdown", "html", "pdf")
            source: Source of the document (e.g., URL, file path)
            author: Document author
            
        Returns:
            URI of created document
        """
        doc_props = {
            'hasName': name,
            'hasKGDocumentContent': content
        }
        
        if doc_type:
            doc_props['hasKGDocumentType'] = doc_type
        if source:
            doc_props['hasKGDocumentSource'] = source
        if author:
            doc_props['hasKGDocumentAuthor'] = author
        
        doc_uri = self.utils.create_node('KGDocument', **doc_props)
        if not doc_uri:
            raise RuntimeError("Failed to create document")
        
        return doc_uri
    
    def create_document_for_interaction(self, name: str, content: str,
                                       interaction_uri: str, doc_type: str = None,
                                       source: str = None, author: str = None) -> str:
        """
        Create a document and link it to an interaction.
        
        Args:
            name: Document name/title
            content: Document content
            interaction_uri: URI of interaction to link to
            doc_type: Type of document
            source: Source of the document
            author: Document author
            
        Returns:
            URI of created document
        """
        doc_uri = self.create_document(name, content, doc_type, source, author)
        self.utils.link_to_interaction(doc_uri, interaction_uri, "KGDocument")
        return doc_uri
    
    def update_document_content(self, doc_uri: str, content: str) -> bool:
        """
        Update the content of a document.
        
        Args:
            doc_uri: URI of the document
            content: New content
            
        Returns:
            True if updated successfully
        """
        try:
            doc_obj = self.kgraph.get_object(doc_uri)
            if doc_obj:
                doc_obj.hasKGDocumentContent = content
                doc_obj.hasKGDocumentLastModified = self.utils.generate_timestamp()
                self.kgraph.update_object(doc_obj)
                return True
            return False
        except Exception as e:
            print(f"Warning: Failed to update document content: {e}")
            return False
    
    def add_document_metadata(self, doc_uri: str, metadata_key: str, metadata_value: str) -> bool:
        """
        Add metadata to a document.
        
        Args:
            doc_uri: URI of the document
            metadata_key: Metadata key
            metadata_value: Metadata value
            
        Returns:
            True if added successfully
        """
        try:
            doc_obj = self.kgraph.get_object(doc_uri)
            if doc_obj:
                # Store metadata as a property (this would depend on the ontology structure)
                setattr(doc_obj, f"hasKGDocumentMetadata_{metadata_key}", metadata_value)
                self.kgraph.update_object(doc_obj)
                return True
            return False
        except Exception as e:
            print(f"Warning: Failed to add document metadata: {e}")
            return False
    
    # ============================================================================
    # DOCUMENT RELATIONSHIPS
    # ============================================================================
    
    def link_document_to_interaction(self, doc_uri: str, interaction_uri: str) -> str:
        """
        Link a document to an interaction.
        
        Args:
            doc_uri: URI of the document
            interaction_uri: URI of the interaction
            
        Returns:
            URI of created edge
        """
        return self.utils.link_to_interaction(doc_uri, interaction_uri, "KGDocument")
    
    def link_document_to_entity(self, doc_uri: str, entity_uri: str) -> str:
        """
        Link a document to an entity.
        
        Args:
            doc_uri: URI of the document
            entity_uri: URI of the entity
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGDocument", entity_uri, doc_uri)
    
    def link_document_to_task(self, doc_uri: str, task_uri: str) -> str:
        """
        Link a document to a task.
        
        Args:
            doc_uri: URI of the document
            task_uri: URI of the task
            
        Returns:
            URI of created edge
        """
        return self.utils.create_edge("Edge_hasKGDocument", task_uri, doc_uri)
    
    # ============================================================================
    # DOCUMENT QUERIES
    # ============================================================================
    
    def get_documents_for_interaction(self, interaction_uri: str) -> List[Dict[str, Any]]:
        """
        Get all documents for an interaction.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            List of document dictionaries
        """
        return self.utils.get_linked_objects(interaction_uri, "KGDocument")
    
    def get_document_details(self, doc_uri: str) -> Dict[str, Any]:
        """
        Get detailed information about a document.
        
        Args:
            doc_uri: URI of the document
            
        Returns:
            Dictionary with document details
        """
        doc_props = self.utils.get_object_properties(doc_uri)
        
        return {
            'document_uri': doc_uri,
            'properties': doc_props,
            'content_length': len(doc_props.get('hasKGDocumentContent', '')),
            'type': doc_props.get('hasKGDocumentType', 'unknown'),
            'author': doc_props.get('hasKGDocumentAuthor', 'unknown'),
            'source': doc_props.get('hasKGDocumentSource', 'unknown')
        }
    
    def get_document_content(self, doc_uri: str) -> Optional[str]:
        """
        Get the content of a document.
        
        Args:
            doc_uri: URI of the document
            
        Returns:
            Document content or None if not found
        """
        try:
            doc_obj = self.kgraph.get_object(doc_uri)
            if doc_obj and hasattr(doc_obj, 'hasKGDocumentContent'):
                return doc_obj.hasKGDocumentContent
            return None
        except Exception as e:
            print(f"Warning: Failed to get document content: {e}")
            return None
    
    def get_interaction_document_summary(self, interaction_uri: str) -> Dict[str, Any]:
        """
        Get a summary of all documents for an interaction.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            Dictionary with document summary
        """
        documents = self.get_documents_for_interaction(interaction_uri)
        
        summary = {
            'interaction_uri': interaction_uri,
            'total_documents': len(documents),
            'documents_by_type': {},
            'total_content_length': 0,
            'document_details': []
        }
        
        for doc in documents:
            doc_uri = doc.get('object')
            if doc_uri:
                doc_details = self.get_document_details(doc_uri)
                summary['document_details'].append(doc_details)
                
                # Count by type
                doc_type = doc_details.get('type', 'unknown')
                summary['documents_by_type'][doc_type] = summary['documents_by_type'].get(doc_type, 0) + 1
                
                # Add to total content length
                summary['total_content_length'] += doc_details.get('content_length', 0)
        
        return summary
    
    # ============================================================================
    # SEARCH AND FILTER
    # ============================================================================
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of document search results
        """
        return self.utils.search_by_type(query, "KGDocument", limit)
    
    def search_document_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents by content using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of document search results with content snippets
        """
        # This would use vector search on document content
        results = self.search(query, limit)
        
        # Enhance results with content snippets
        enhanced_results = []
        for result in results:
            doc_uri = result.get('uri')
            if doc_uri:
                content = self.get_document_content(doc_uri)
                if content:
                    # Add a content snippet (first 200 characters)
                    result['content_snippet'] = content[:200] + "..." if len(content) > 200 else content
                enhanced_results.append(result)
        
        return enhanced_results
    
    def get_documents_by_type(self, doc_type: str) -> List[Dict[str, Any]]:
        """
        Get all documents of a specific type.
        
        Args:
            doc_type: Document type to filter by
            
        Returns:
            List of document dictionaries
        """
        return self.utils.filter_by_property("KGDocument", "hasKGDocumentType", doc_type)
    
    def get_documents_by_author(self, author: str) -> List[Dict[str, Any]]:
        """
        Get all documents by a specific author.
        
        Args:
            author: Author name to filter by
            
        Returns:
            List of document dictionaries
        """
        return self.utils.filter_by_property("KGDocument", "hasKGDocumentAuthor", author)
    
    def get_documents_by_source(self, source: str) -> List[Dict[str, Any]]:
        """
        Get all documents from a specific source.
        
        Args:
            source: Source to filter by
            
        Returns:
            List of document dictionaries
        """
        return self.utils.filter_by_property("KGDocument", "hasKGDocumentSource", source)
    
    def get_recent_documents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recently created documents.
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of recent document dictionaries
        """
        # This would require a SPARQL query ordered by timestamp
        # For now, return all documents (would need proper ordering in production)
        return self.utils.get_objects_by_type("KGDocument", limit)
