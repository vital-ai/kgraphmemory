from typing import List, Dict, Any, Optional, Union
import uuid
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, 
    Range, MatchValue, MatchText, MatchAny, SearchRequest
)
from vital_ai_vitalsigns.embedding.embedding_model import EmbeddingModel


class KGraphVectorDB:
    """
    In-memory vector database using Qdrant with integrated embedding model.
    Supports mixed data types (vectors + metadata fields) with efficient search and filtering.
    """
    
    def __init__(self, db_id: str, embedding_model: EmbeddingModel, 
                 collection_name: str = "kgraph_vectors", 
                 distance_metric: Distance = Distance.COSINE):
        """
        Initialize the vector database with a unique identifier and embedding model.
        
        Args:
            db_id: Unique string identifier for this vector database instance
            embedding_model: EmbeddingModel instance for text vectorization
            collection_name: Name for the Qdrant collection
            distance_metric: Distance metric for vector similarity (COSINE, DOT, EUCLIDEAN)
        """
        self.db_id = db_id
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        
        # Initialize in-memory Qdrant client
        self.client = QdrantClient(":memory:")
        
        # Get vector dimension from embedding model
        self.vector_dim = self._get_vector_dimension()
        
        # Create collection
        self._create_collection()
        
    def _get_vector_dimension(self) -> int:
        """
        Determine vector dimension by testing the embedding model.
        """
        test_vector = self.embedding_model.vectorize("test")
        return len(test_vector)
    
    def _create_collection(self):
        """
        Create the Qdrant collection with appropriate vector configuration.
        """
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_dim,
                    distance=self.distance_metric
                )
            )
        except Exception as e:
            # Collection might already exist
            pass
    
    def add_text(self, text: str, metadata: Dict[str, Any], 
                 record_id: Optional[Union[str, int]] = None) -> str:
        """
        Add a text record by automatically generating its vector embedding.
        
        Args:
            text: Text to be vectorized and stored
            metadata: Dictionary of metadata fields
            record_id: Optional custom ID, otherwise generates UUID
            
        Returns:
            The ID of the inserted record
        """
        vector = self.embedding_model.vectorize(text)
        return self.add_vector(vector, metadata, record_id, text)
    
    def add_vector(self, vector: Union[List[float], np.ndarray], metadata: Dict[str, Any],
                   record_id: Optional[Union[str, int]] = None, 
                   original_text: Optional[str] = None) -> str:
        """
        Add a vector record with metadata.
        
        Args:
            vector: Vector embedding
            metadata: Dictionary of metadata fields
            record_id: Optional custom ID, otherwise generates UUID
            original_text: Optional original text for reference
            
        Returns:
            The ID of the inserted record
        """
        if record_id is None:
            record_id = str(uuid.uuid4())
        
        # Ensure vector is the right format
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        
        # Add original text to metadata if provided
        payload = dict(metadata)
        if original_text:
            payload['_original_text'] = original_text
        
        point = PointStruct(
            id=record_id,
            vector=vector,
            payload=payload
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return str(record_id)
    
    def add_batch_texts(self, texts: List[str], metadatas: List[Dict[str, Any]],
                        record_ids: Optional[List[Union[str, int]]] = None) -> List[str]:
        """
        Add multiple text records in batch for efficiency.
        
        Args:
            texts: List of texts to vectorize and store
            metadatas: List of metadata dictionaries
            record_ids: Optional list of custom IDs
            
        Returns:
            List of record IDs
        """
        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must have the same length")
        
        if record_ids and len(record_ids) != len(texts):
            raise ValueError("record_ids must have the same length as texts")
        
        # Generate vectors for all texts
        vectors = self.embedding_model.vectorize(texts)
        
        # Prepare points
        points = []
        ids = []
        
        for i, (text, vector, metadata) in enumerate(zip(texts, vectors, metadatas)):
            record_id = record_ids[i] if record_ids else str(uuid.uuid4())
            ids.append(str(record_id))
            
            payload = dict(metadata)
            payload['_original_text'] = text
            
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()
            
            points.append(PointStruct(
                id=record_id,
                vector=vector,
                payload=payload
            ))
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return ids
    
    def search_by_text(self, query_text: str, limit: int = 10, 
                       filters: Optional[Dict[str, Any]] = None,
                       score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for similar records using text query.
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            filters: Optional metadata filters
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and metadata
        """
        query_vector = self.embedding_model.vectorize(query_text)
        return self.search_by_vector(query_vector, limit, filters, score_threshold)
    
    def search_by_vector(self, query_vector: Union[List[float], np.ndarray], 
                         limit: int = 10, filters: Optional[Dict[str, Any]] = None,
                         score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for similar records using vector query.
        
        Args:
            query_vector: Vector to search for
            limit: Maximum number of results
            filters: Optional metadata filters
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and metadata
        """
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()
        
        # Build filter if provided
        query_filter = None
        if filters:
            query_filter = self._build_filter(filters)
        
        # Use the query_points API (updated from deprecated search method)
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold
        ).points
        
        return [
            {
                'id': result.id,
                'score': result.score,
                'metadata': result.payload
            }
            for result in results
        ]
    
    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """
        Build Qdrant filter from dictionary specification.
        
        Args:
            filters: Dictionary with filter conditions
            
        Returns:
            Qdrant Filter object
        """
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, dict):
                # Range or complex condition
                if 'gte' in value or 'lte' in value or 'gt' in value or 'lt' in value:
                    range_condition = Range(
                        gte=value.get('gte'),
                        lte=value.get('lte'),
                        gt=value.get('gt'),
                        lt=value.get('lt')
                    )
                    conditions.append(FieldCondition(key=key, range=range_condition))
                elif 'in' in value:
                    conditions.append(FieldCondition(key=key, match=MatchAny(any=value['in'])))
            elif isinstance(value, list):
                # Match any of the values
                conditions.append(FieldCondition(key=key, match=MatchAny(any=value)))
            else:
                # Exact match
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        
        return Filter(must=conditions)
    
    def update(self, record_id: Union[str, int], vector: Optional[Union[List[float], np.ndarray]] = None,
               metadata: Optional[Dict[str, Any]] = None, text: Optional[str] = None):
        """
        Update an existing record.
        
        Args:
            record_id: ID of record to update
            vector: New vector (optional)
            metadata: New metadata (optional)
            text: New text to vectorize (optional, takes precedence over vector)
        """
        if text:
            vector = self.embedding_model.vectorize(text)
            if metadata is None:
                metadata = {}
            metadata['_original_text'] = text
        
        if vector is not None:
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()
            
            point = PointStruct(
                id=record_id,
                vector=vector,
                payload=metadata or {}
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        elif metadata:
            # Update only metadata
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=metadata,
                points=[record_id]
            )
    
    def delete(self, record_ids: Union[str, int, List[Union[str, int]]]):
        """
        Delete records by ID(s).
        
        Args:
            record_ids: Single ID or list of IDs to delete
        """
        if not isinstance(record_ids, list):
            record_ids = [record_ids]
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=record_ids
        )
    
    def get_by_id(self, record_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Retrieve a record by its ID.
        
        Args:
            record_id: ID of the record
            
        Returns:
            Record data or None if not found
        """
        results = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[record_id],
            with_vectors=True
        )
        
        if results:
            result = results[0]
            return {
                'id': result.id,
                'vector': result.vector,
                'metadata': result.payload
            }
        return None
    
    def count(self) -> int:
        """
        Get the total number of records in the database.
        
        Returns:
            Number of records
        """
        info = self.client.get_collection(self.collection_name)
        return info.points_count
    
    def clear(self):
        """
        Clear all records from the database.
        """
        self.client.delete_collection(self.collection_name)
        self._create_collection()
    
    def get_db_id(self) -> str:
        """
        Get the unique identifier for this database.
        
        Returns:
            Database identifier string
        """
        return self.db_id