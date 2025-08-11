from typing import List, Dict, Any, Optional, Union, Iterator, TypeVar
import pyoxigraph as ox
from pyoxigraph import Store, Quad, NamedNode, BlankNode, Literal, Triple
from pyoxigraph import Variable, QuerySolutions, QueryTriples, QueryBoolean
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from rdflib import URIRef as RDFLibURIRef, Literal as RDFLibLiteral, BNode as RDFLibBNode
import logging

# Follow VitalSigns TypeVar pattern for GraphObject type annotations
G = TypeVar('G', bound=Optional['GraphObject'])


class KGraphRDFDB:
    """
    In-memory RDF database using pyoxigraph.
    Supports CRUD operations and SPARQL queries with a unique string identifier.
    """
    
    def __init__(self, store_id: str):
        """
        Initialize the RDF database with a unique identifier.
        
        Args:
            store_id: Unique string identifier for this RDF store instance
        """
        self.store_id = store_id
        # Create in-memory store (no path provided)
        self.store = Store()
        # Set up logger for this instance
        self.logger = logging.getLogger(f"KGraphRDFDB.{store_id}")
        
    def add_triple(self, subject: Union[str, NamedNode, BlankNode], 
                   predicate: Union[str, NamedNode], 
                   obj: Union[str, NamedNode, BlankNode, Literal],
                   graph: Optional[Union[str, NamedNode]] = None) -> bool:
        """
        Add a single triple to the store.
        
        Args:
            subject: Subject of the triple
            predicate: Predicate of the triple
            obj: Object of the triple
            graph: Optional named graph
            
        Returns:
            True if the triple was added, False if it already existed
        """
        try:
            # Convert strings to appropriate RDF terms
            s = self._to_rdf_term(subject, allow_literal=False)
            p = self._to_rdf_term(predicate, allow_literal=False, force_named_node=True)
            o = self._to_rdf_term(obj)
            
            if graph:
                g = self._to_rdf_term(graph, allow_literal=False, force_named_node=True)
                quad = Quad(s, p, o, g)
                self.logger.debug(f"Adding quad: ({s}, {p}, {o}, {g})")
            else:
                quad = Quad(s, p, o)
                self.logger.debug(f"Adding triple: ({s}, {p}, {o})")
                
            self.store.add(quad)
            self.logger.debug(f"Successfully added quad to store")
            return True
        except Exception as e:
            self.logger.error(f"Error adding triple: {e}")
            print(f"Error adding triple: {e}")
            return False
    
    def add_triples(self, triples: List[tuple]) -> int:
        """
        Add multiple triples to the store.
        
        Args:
            triples: List of tuples (subject, predicate, object) or (subject, predicate, object, graph)
            
        Returns:
            Number of triples successfully added
        """
        added_count = 0
        for triple in triples:
            if len(triple) == 3:
                s, p, o = triple
                if self.add_triple(s, p, o):
                    added_count += 1
            elif len(triple) == 4:
                s, p, o, g = triple
                if self.add_triple(s, p, o, g):
                    added_count += 1
        return added_count
    
    def remove_triple(self, subject: Union[str, NamedNode, BlankNode, None] = None,
                      predicate: Union[str, NamedNode, None] = None,
                      obj: Union[str, NamedNode, BlankNode, Literal, None] = None,
                      graph: Optional[Union[str, NamedNode]] = None) -> int:
        """
        Remove triples matching the given pattern.
        
        Args:
            subject: Subject pattern (None for wildcard)
            predicate: Predicate pattern (None for wildcard)
            obj: Object pattern (None for wildcard)
            graph: Graph pattern (None for wildcard)
            
        Returns:
            Number of triples removed
        """
        try:
            # Convert to RDF terms, allowing None for wildcards
            s = self._to_rdf_term(subject, allow_literal=False) if subject is not None else None
            p = self._to_rdf_term(predicate, allow_literal=False, force_named_node=True) if predicate is not None else None
            o = self._to_rdf_term(obj) if obj is not None else None
            g = self._to_rdf_term(graph, allow_literal=False, force_named_node=True) if graph is not None else None
            
            # Find matching quads first
            matching_quads = list(self.store.quads_for_pattern(s, p, o, g))
            
            # Remove them
            for quad in matching_quads:
                self.store.remove(quad)
                
            return len(matching_quads)
        except Exception as e:
            print(f"Error removing triples: {e}")
            return 0
    
    def get_triples(self, subject: Union[str, NamedNode, BlankNode, None] = None,
                    predicate: Union[str, NamedNode, None] = None,
                    obj: Union[str, NamedNode, BlankNode, Literal, None] = None,
                    graph: Optional[Union[str, NamedNode]] = None) -> List[tuple]:
        """
        Retrieve triples matching the given pattern.
        
        Args:
            subject: Subject pattern (None for wildcard)
            predicate: Predicate pattern (None for wildcard)
            obj: Object pattern (None for wildcard)
            graph: Graph pattern (None for wildcard)
            
        Returns:
            List of tuples (subject, predicate, object, graph)
        """
        try:
            # Convert to RDF terms, allowing None for wildcards
            s = self._to_rdf_term(subject, allow_literal=False) if subject is not None else None
            p = self._to_rdf_term(predicate, allow_literal=False, force_named_node=True) if predicate is not None else None
            o = self._to_rdf_term(obj) if obj is not None else None
            g = self._to_rdf_term(graph, allow_literal=False, force_named_node=True) if graph is not None else None
            
            results = []
            for quad in self.store.quads_for_pattern(s, p, o, g):
                results.append((
                    str(quad.subject),
                    str(quad.predicate), 
                    str(quad.object),
                    str(quad.graph_name) if quad.graph_name else None
                ))
            return results
        except Exception as e:
            print(f"Error getting triples: {e}")
            return []
    
    def update_triple(self, old_subject: Union[str, NamedNode, BlankNode],
                      old_predicate: Union[str, NamedNode],
                      old_object: Union[str, NamedNode, BlankNode, Literal],
                      new_subject: Union[str, NamedNode, BlankNode],
                      new_predicate: Union[str, NamedNode],
                      new_object: Union[str, NamedNode, BlankNode, Literal],
                      graph: Optional[Union[str, NamedNode]] = None) -> bool:
        """
        Update a triple by removing the old one and adding the new one.
        
        Args:
            old_subject, old_predicate, old_object: Old triple to remove
            new_subject, new_predicate, new_object: New triple to add
            graph: Optional named graph
            
        Returns:
            True if update was successful
        """
        removed = self.remove_triple(old_subject, old_predicate, old_object, graph)
        if removed > 0:
            return self.add_triple(new_subject, new_predicate, new_object, graph)
        return False
    
    def import_rdf(self, rdf_data: str, format: str = "ntriples", graph: Optional[Union[str, NamedNode]] = None) -> bool:
        """
        Import RDF data directly into the store.
        
        Args:
            rdf_data: RDF data as string
            format: RDF format (turtle, ntriples, rdfxml, etc.)
            graph: Optional named graph to import into
            
        Returns:
            True if import was successful
        """
        try:
            from io import StringIO
            from pyoxigraph import Quad, Store, RdfFormat
            
            # Convert graph to NamedNode if needed
            graph_node = None
            if graph is not None:
                graph_node = self._to_rdf_term(graph, allow_literal=False, force_named_node=True)
            
            # Convert format string to RdfFormat object
            if format == "ntriples":
                rdf_format = RdfFormat.N_TRIPLES
            elif format == "turtle":
                rdf_format = RdfFormat.TURTLE
            elif format == "rdfxml":
                rdf_format = RdfFormat.RDF_XML
            else:
                rdf_format = RdfFormat.N_TRIPLES  # Default to ntriples
            
            # Load the RDF data and then move triples to the named graph if specified
            temp_store = Store()
            temp_store.load(StringIO(rdf_data), rdf_format)
            
            # If a named graph is specified, move all triples to that graph
            if graph_node:
                for quad in temp_store:
                    # Create a new quad with the specified graph
                    new_quad = Quad(quad.subject, quad.predicate, quad.object, graph_node)
                    self.store.add(new_quad)
            else:
                # No named graph, just add all quads as-is
                for quad in temp_store:
                    self.store.add(quad)
            
            return True
        except Exception as e:
            print(f"Error importing RDF data: {e}")
            return False
    
    def sparql_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL SELECT query.
        
        Args:
            query: SPARQL query string
            
        Returns:
            List of result bindings as dictionaries
        """
        try:
            self.logger.debug(f"Executing SPARQL query: {query}")
            results = self.store.query(query)
            self.logger.debug(f"Query returned results of type: {type(results)}")
            
            if isinstance(results, QuerySolutions):
                # SELECT queries return QuerySolutions
                result_list = []
                # Get variable names from the QuerySolutions object
                variables = results.variables
                self.logger.debug(f"Query variables: {variables}")
                
                solution_count = 0
                for solution in results:
                    solution_count += 1
                    binding = {}
                    # Access solution values by index using the variable names
                    for i, variable in enumerate(variables):
                        try:
                            value = solution[i]
                            if value is not None:
                                binding[str(variable)] = str(value)
                        except (IndexError, TypeError):
                            # Skip if we can't access this variable
                            continue
                    result_list.append(binding)
                    self.logger.debug(f"Solution {solution_count}: {binding}")
                
                self.logger.debug(f"Query returned {len(result_list)} solutions")
                return result_list
            elif isinstance(results, QueryTriples):
                # CONSTRUCT queries return QueryTriples
                result_list = []
                for triple in results:
                    result_list.append({
                        "subject": str(triple.subject),
                        "predicate": str(triple.predicate),
                        "object": str(triple.object)
                    })
                return result_list
            elif isinstance(results, QueryBoolean):
                # ASK queries return QueryBoolean
                return [{"result": bool(results)}]
            else:
                # Fallback for other result types
                return [{"result": str(results)}]
                
        except Exception as e:
            print(f"Error executing SPARQL query: {e}")
            return []
    
    def sparql_construct(self, query: str) -> List[tuple]:
        """
        Execute a SPARQL CONSTRUCT query.
        
        Args:
            query: SPARQL CONSTRUCT query string
            
        Returns:
            List of constructed triples as tuples
        """
        try:
            results = self.store.query(query)
            triples = []
            
            for triple in results:
                triples.append((
                    str(triple.subject),
                    str(triple.predicate),
                    str(triple.object)
                ))
            return triples
            
        except Exception as e:
            print(f"Error executing SPARQL CONSTRUCT query: {e}")
            return []
    
    def sparql_ask(self, query: str) -> bool:
        """
        Execute a SPARQL ASK query.
        
        Args:
            query: SPARQL ASK query string
            
        Returns:
            Boolean result
        """
        try:
            result = self.store.query(query)
            return bool(result)
        except Exception as e:
            print(f"Error executing SPARQL ASK query: {e}")
            return False
    
    def sparql_update(self, update: str) -> bool:
        """
        Execute a SPARQL UPDATE query.
        
        Args:
            update: SPARQL UPDATE string
            
        Returns:
            True if update was successful
        """
        try:
            self.store.update(update)
            return True
        except Exception as e:
            print(f"Error executing SPARQL UPDATE: {e}")
            return False
    
    def load_from_string(self, data: str, format: str = "turtle") -> bool:
        """
        Load RDF data from a string.
        
        Args:
            data: RDF data as string
            format: RDF format (turtle, rdf/xml, n-triples, etc.)
            
        Returns:
            True if loading was successful
        """
        try:
            if format.lower() == "turtle" or format.lower() == "ttl":
                self.store.load(data.encode(), "text/turtle")
            elif format.lower() == "rdf/xml" or format.lower() == "xml":
                self.store.load(data.encode(), "application/rdf+xml")
            elif format.lower() == "n-triples" or format.lower() == "nt":
                self.store.load(data.encode(), "application/n-triples")
            elif format.lower() == "n-quads" or format.lower() == "nq":
                self.store.load(data.encode(), "application/n-quads")
            else:
                # Default to turtle
                self.store.load(data.encode(), "text/turtle")
            return True
        except Exception as e:
            print(f"Error loading RDF data: {e}")
            return False
    
    def load_from_file_batch(self, file_path: str, format: str = "ntriples", 
                           batch_size: int = 100000, progress_callback=None) -> bool:
        """
        Load RDF data from a file in batches for memory efficiency.
        Uses pyoxigraph's bulk_load for optimal performance on large files.
        
        Args:
            file_path: Path to the RDF file
            format: RDF format (ntriples, turtle, rdf/xml, etc.)
            batch_size: Number of lines to process in each batch (default 100k for better performance)
            progress_callback: Optional callback function for progress reporting
            
        Returns:
            True if loading was successful
        """
        try:
            import os
            from pyoxigraph import RdfFormat
            
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            # Map format strings to RdfFormat constants
            format_map = {
                "ntriples": RdfFormat.N_TRIPLES,
                "nt": RdfFormat.N_TRIPLES,
                "n-triples": RdfFormat.N_TRIPLES,
                "turtle": RdfFormat.TURTLE,
                "ttl": RdfFormat.TURTLE,
                "rdf/xml": RdfFormat.RDF_XML,
                "xml": RdfFormat.RDF_XML,
                "nquads": RdfFormat.N_QUADS,
                "nq": RdfFormat.N_QUADS,
                "n-quads": RdfFormat.N_QUADS,
                "trig": RdfFormat.TRIG,
                "jsonld": RdfFormat.JSON_LD,
                "json-ld": RdfFormat.JSON_LD
            }
            
            rdf_format = format_map.get(format.lower(), RdfFormat.N_TRIPLES)
            
            total_lines = 0
            processed_lines = 0
            batch_lines = []
            
            # Count total lines for progress reporting
            if progress_callback:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines = sum(1 for _ in f)
                print(f"Total lines to process: {total_lines:,}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        batch_lines.append(line)
                    
                    # Process batch when it reaches the specified size
                    if len(batch_lines) >= batch_size:
                        batch_data = '\n'.join(batch_lines)
                        # Use bulk_load for better performance (no transactional guarantees)
                        self.store.bulk_load(input=batch_data.encode('utf-8'), format=rdf_format)
                        
                        processed_lines += len(batch_lines)
                        if progress_callback:
                            progress_callback(processed_lines, total_lines, line_num)
                        
                        batch_lines = []  # Clear the batch
                
                # Process remaining lines in the final batch
                if batch_lines:
                    batch_data = '\n'.join(batch_lines)
                    self.store.bulk_load(input=batch_data.encode('utf-8'), format=rdf_format)
                    
                    processed_lines += len(batch_lines)
                    if progress_callback:
                        progress_callback(processed_lines, total_lines, line_num)
            
            print(f"Successfully loaded {processed_lines:,} triples from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return False
    
    def bulk_load_file(self, file_path: str, format: str = "ntriples") -> bool:
        """
        Load an entire RDF file using pyoxigraph's bulk_load for maximum performance.
        Best for large files where transactional guarantees are not needed.
        
        Args:
            file_path: Path to the RDF file
            format: RDF format (ntriples, turtle, rdf/xml, etc.)
            
        Returns:
            True if loading was successful
        """
        try:
            import os
            from pyoxigraph import RdfFormat
            
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            # Map format strings to RdfFormat constants
            format_map = {
                "ntriples": RdfFormat.N_TRIPLES,
                "nt": RdfFormat.N_TRIPLES,
                "n-triples": RdfFormat.N_TRIPLES,
                "turtle": RdfFormat.TURTLE,
                "ttl": RdfFormat.TURTLE,
                "rdf/xml": RdfFormat.RDF_XML,
                "xml": RdfFormat.RDF_XML,
                "nquads": RdfFormat.N_QUADS,
                "nq": RdfFormat.N_QUADS,
                "n-quads": RdfFormat.N_QUADS,
                "trig": RdfFormat.TRIG,
                "jsonld": RdfFormat.JSON_LD,
                "json-ld": RdfFormat.JSON_LD
            }
            
            rdf_format = format_map.get(format.lower(), RdfFormat.N_TRIPLES)
            
            print(f"Loading file {file_path} using bulk_load...")
            # Use bulk_load with file path for maximum performance
            self.store.bulk_load(path=file_path, format=rdf_format)
            
            print(f"Successfully bulk loaded {file_path}")
            return True
            
        except Exception as e:
            print(f"Error bulk loading file {file_path}: {e}")
            return False
    
    def serialize(self, format: str = "turtle") -> str:
        """
        Serialize the RDF store to a string.
        
        Args:
            format: Output format (turtle, rdf/xml, n-triples, etc.)
            
        Returns:
            Serialized RDF data as string
        """
        try:
            if format.lower() == "turtle" or format.lower() == "ttl":
                return self.store.dump("text/turtle").decode()
            elif format.lower() == "rdf/xml" or format.lower() == "xml":
                return self.store.dump("application/rdf+xml").decode()
            elif format.lower() == "n-triples" or format.lower() == "nt":
                return self.store.dump("application/n-triples").decode()
            elif format.lower() == "n-quads" or format.lower() == "nq":
                return self.store.dump("application/n-quads").decode()
            else:
                # Default to turtle
                return self.store.dump("text/turtle").decode()
        except Exception as e:
            print(f"Error serializing RDF data: {e}")
            return ""
    
    def count_triples(self) -> int:
        """
        Count the total number of triples in the store.
        
        Returns:
            Number of triples
        """
        return len(list(self.store.quads_for_pattern(None, None, None, None)))
    
    def add_graph_object_triples(self, graph_object: GraphObject, graph: Optional[Union[str, NamedNode]] = None) -> bool:
        """
        Add RDF triples for a GraphObject using property instances' to_rdf() methods.
        This ensures proper XSD typing for all properties including datetime values.
        
        Args:
            graph_object: Concrete GraphObject instance (e.g., KGEntity, VITAL_Node, VITAL_Edge).
                         Note: GraphObject is abstract - pass concrete subclass instances only.
            graph: Optional named graph to add triples to
            
        Returns:
            True if triples were successfully added
        """
        try:
            object_uri = str(graph_object.URI)
            self.logger.debug(f"Adding GraphObject triples for: {object_uri}")
            
            # Add class type triples
            class_uri = graph_object.get_class_uri()
            self.add_triple(object_uri, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", class_uri, graph)
            self.add_triple(object_uri, "http://vital.ai/ontology/vital-core#vitaltype", class_uri, graph)
            
            # Access property instances directly from _properties and use their to_rdf() method
            if hasattr(graph_object, '_properties'):
                for prop_uri, prop_instance in graph_object._properties.items():
                    try:
                        # Get RDF data from property instance with proper XSD typing
                        rdf_data = prop_instance.to_rdf()
                        self.logger.debug(f"Property {prop_uri} RDF data: {rdf_data}")
                        
                        # Add triple with proper typing based on RDF data
                        self._add_property_triple(object_uri, prop_uri, rdf_data, graph)
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing property {prop_uri}: {e}")
                        continue
            
            self.logger.debug(f"Successfully added triples for {object_uri}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding GraphObject triples: {e}")
            print(f"Error adding GraphObject triples: {e}")
            return False
    
    def get_graph_object(self, subject_uri: str, graph: Optional[Union[str, NamedNode]] = None) -> G:
        """
        Retrieve a GraphObject by converting RDF triples using VitalSigns.
        This method handles the RDF-specific conversion properly.
        
        Args:
            subject_uri: URI of the subject to retrieve
            graph: Optional named graph to search in
            
        Returns:
            GraphObject instance or None if not found
        """
        try:
            # Get all triples for this subject
            triples = self.get_triples(subject=subject_uri, graph=graph)
            
            if not triples:
                return None
            
            # Convert string triples to RDFLib objects for VitalSigns compatibility
            # VitalSigns expects RDFLib URIRef/Literal objects, not strings
            from rdflib import URIRef, Literal, BNode
            
            def triple_generator():
                for quad in triples:
                    subject, predicate, obj, graph_name = quad
                    
                    # Convert pyoxigraph objects to RDFLib objects for VitalSigns compatibility
                    # VitalSigns from_triples() expects RDFLib URIRef/Literal objects
                    rdf_subject = self._to_rdflib_term(subject)
                    rdf_predicate = self._to_rdflib_term(predicate)
                    rdf_object = self._to_rdflib_term(obj)
                        
                    yield (rdf_subject, rdf_predicate, rdf_object)
            
            # Use VitalSigns to create GraphObject from triples
            vs = VitalSigns()
            graph_object = vs.from_triples(triple_generator())
            
            return graph_object
            
        except Exception as e:
            self.logger.error(f"Error retrieving GraphObject for {subject_uri}: {e}")
            return None
    
    def get_graph_objects_batch(self, subject_uris: List[str], graph: Optional[Union[str, NamedNode]] = None) -> Dict[str, G]:
        """
        Retrieve multiple GraphObjects by URIs in a single batch operation.
        Uses pyoxigraph's efficient quads_for_pattern method for better performance.
        
        Args:
            subject_uris: List of subject URIs to retrieve
            graph: Optional named graph to search in
            
        Returns:
            Dictionary mapping subject URIs to GraphObject instances (excludes objects not found)
        """
        if not subject_uris:
            return {}
        
        try:
            from pyoxigraph import NamedNode
            from rdflib import URIRef, Literal, BNode
            
            # Convert graph parameter to pyoxigraph format
            graph_node = None
            if graph:
                if isinstance(graph, str):
                    graph_node = NamedNode(graph)
                else:
                    graph_node = graph
            
            # Collect all triples for all subjects in one efficient operation
            all_triples = {}
            
            # Use pyoxigraph's quads_for_pattern for efficient batch retrieval
            for subject_uri in subject_uris:
                try:
                    subject_node = NamedNode(subject_uri)
                    # Get all quads where this URI is the subject
                    quads = list(self.store.quads_for_pattern(subject=subject_node, predicate=None, object=None, graph_name=graph_node))
                    
                    if quads:
                        # Convert pyoxigraph quads to string format for consistency
                        triples = []
                        for quad in quads:
                            subject_str = str(quad.subject)
                            predicate_str = str(quad.predicate) 
                            object_str = str(quad.object)
                            graph_str = str(quad.graph_name) if quad.graph_name else None
                            triples.append((subject_str, predicate_str, object_str, graph_str))
                        
                        all_triples[subject_uri] = triples
                        
                except Exception as e:
                    print(f"Warning: Could not retrieve triples for {subject_uri}: {e}")
                    continue
            
            # Convert collected triples to GraphObjects using VitalSigns
            result_objects = {}
            vs = VitalSigns()
            
            for subject_uri, triples in all_triples.items():
                try:
                    def triple_generator():
                        for subject, predicate, obj, graph_name in triples:
                            # Convert pyoxigraph objects to RDFLib objects for VitalSigns compatibility
                            rdf_subject = self._to_rdflib_term(subject)
                            rdf_predicate = self._to_rdflib_term(predicate)
                            rdf_object = self._to_rdflib_term(obj)
                            
                            yield (rdf_subject, rdf_predicate, rdf_object)
                    
                    # Use VitalSigns to create GraphObject from triples
                    graph_object = vs.from_triples(triple_generator())
                    if graph_object:
                        result_objects[subject_uri] = graph_object
                        
                except Exception as e:
                    print(f"Warning: Could not reconstruct GraphObject for {subject_uri}: {e}")
                    continue
            
            return result_objects
            
        except Exception as e:
            print(f"Error in batch GraphObject retrieval: {e}")
            return {}
    
    def clear(self):
        """
        Clear all triples from the store.
        """
        self.store.clear()
    
    def get_namespaces(self) -> Dict[str, str]:
        """
        Get all namespace prefixes defined in the store.
        
        Returns:
            Dictionary of prefix -> namespace URI mappings
        """
        # Note: pyoxigraph doesn't have built-in namespace management
        # This would need to be implemented separately if needed
        return {}
    
    def _add_property_triple(self, subject_uri: str, prop_uri: str, rdf_data: Dict[str, Any], graph: Optional[Union[str, NamedNode]] = None) -> bool:
        """
        Add a property triple using RDF data from property instance's to_rdf() method.
        
        Args:
            subject_uri: Subject URI
            prop_uri: Property URI
            rdf_data: RDF data dictionary from prop_instance.to_rdf()
            graph: Optional named graph
            
        Returns:
            True if triple was added successfully
        """
        try:
            datatype = rdf_data.get("datatype")
            value = rdf_data.get("value")
            
            if value is None:
                return False
            
            if datatype == list:
                # Handle list values
                value_list = value
                data_class = rdf_data.get("data_class")
                
                for v in value_list:
                    if data_class and hasattr(data_class, '__name__') and 'URIRef' in data_class.__name__:
                        # URI reference
                        self.add_triple(subject_uri, prop_uri, str(v), graph)
                    else:
                        # Literal with datatype
                        typed_literal = self._create_typed_literal(v, data_class)
                        self.add_triple(subject_uri, prop_uri, typed_literal, graph)
            
            elif hasattr(datatype, '__name__') and 'URIRef' in datatype.__name__:
                # URI reference
                self.add_triple(subject_uri, prop_uri, str(value), graph)
            
            else:
                # Literal with XSD datatype
                typed_literal = self._create_typed_literal(value, datatype)
                self.add_triple(subject_uri, prop_uri, typed_literal, graph)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error adding property triple for {prop_uri}: {e}")
            return False
    
    def _create_typed_literal(self, value: Any, datatype: Any) -> Union[str, Literal]:
        """
        Create a properly typed literal based on the datatype from property RDF data.
        
        Args:
            value: Property value
            datatype: Datatype from property RDF data
            
        Returns:
            Typed literal or plain string
        """
        try:
            # Handle different datatype formats
            if hasattr(datatype, '__name__'):
                datatype_name = datatype.__name__
            elif hasattr(datatype, 'toPython'):
                # RDFLib datatype
                return Literal(str(value), datatype=NamedNode(str(datatype)))
            elif isinstance(datatype, str) and datatype.startswith('http'):
                # Direct XSD URI
                return Literal(str(value), datatype=NamedNode(datatype))
            else:
                datatype_name = str(datatype)
            
            # Map Python types to XSD types (similar to GraphObject.to_rdf())
            if 'datetime' in datatype_name.lower():
                return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#dateTime"))
            elif 'int' in datatype_name.lower():
                return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#integer"))
            elif 'float' in datatype_name.lower():
                return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#float"))
            elif 'bool' in datatype_name.lower():
                return Literal(str(value).lower(), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#boolean"))
            else:
                # Default to string
                return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#string"))
                
        except Exception as e:
            self.logger.warning(f"Error creating typed literal for value '{value}' with datatype '{datatype}': {e}")
            # Fallback to plain string
            return str(value)
    
    def _parse_ntriples(self, ntriples_data: str) -> List[tuple]:
        """
        Parse N-Triples data and extract individual triples.
        
        Args:
            ntriples_data: N-Triples formatted RDF data
            
        Returns:
            List of (subject, predicate, object) tuples
        """
        triples = []
        
        try:
            # Split into lines and process each triple
            lines = ntriples_data.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse N-Triple line: <subject> <predicate> <object> .
                # Handle both URI and literal objects
                parts = self._parse_ntriple_line(line)
                if parts:
                    triples.append(parts)
            
            self.logger.debug(f"Parsed {len(triples)} triples from N-Triples data")
            return triples
            
        except Exception as e:
            self.logger.error(f"Error parsing N-Triples data: {e}")
            return []
    
    def _parse_ntriple_line(self, line: str) -> Optional[tuple]:
        """
        Parse a single N-Triple line into subject, predicate, object.
        
        Args:
            line: Single N-Triple line
            
        Returns:
            Tuple of (subject, predicate, object) or None if parsing fails
        """
        try:
            # Remove trailing period and whitespace
            line = line.rstrip(' .')
            
            # Find the positions of the three components
            # Subject: always starts with < and ends with >
            if not line.startswith('<'):
                return None
            
            subject_end = line.find('>', 1)
            if subject_end == -1:
                return None
            
            subject = line[1:subject_end]  # Remove < >
            
            # Find predicate: starts after subject
            remaining = line[subject_end + 1:].strip()
            if not remaining.startswith('<'):
                return None
            
            predicate_end = remaining.find('>', 1)
            if predicate_end == -1:
                return None
            
            predicate = remaining[1:predicate_end]  # Remove < >
            
            # Object: everything after predicate
            obj_part = remaining[predicate_end + 1:].strip()
            
            # Parse object - could be URI <...> or literal "..."^^<datatype>
            if obj_part.startswith('<') and obj_part.endswith('>'):
                # URI object
                obj = obj_part[1:-1]  # Remove < >
            elif obj_part.startswith('"'):
                # Literal object - may have datatype
                obj = self._parse_literal_object(obj_part)
            else:
                # Plain literal
                obj = obj_part
            
            return (subject, predicate, obj)
            
        except Exception as e:
            self.logger.warning(f"Error parsing N-Triple line '{line}': {e}")
            return None
    
    def _to_rdflib_term(self, term):
        """
        Convert pyoxigraph terms to RDFLib terms for VitalSigns compatibility.
        Only converts when interfacing with VitalSigns - keeps pyoxigraph types elsewhere.
        
        Args:
            term: Pyoxigraph NamedNode, BlankNode, Literal, or string
            
        Returns:
            Corresponding RDFLib URIRef, BNode, or Literal
        """
        if isinstance(term, NamedNode):
            return RDFLibURIRef(str(term))
        elif isinstance(term, BlankNode):
            return RDFLibBNode(str(term))
        elif isinstance(term, Literal):
            # Pyoxigraph Literal - convert to RDFLib Literal with proper XSD typing
            value = term.value
            datatype = term.datatype
            if datatype:
                return RDFLibLiteral(value, datatype=RDFLibURIRef(str(datatype)))
            else:
                return RDFLibLiteral(value)
        else:
            # String representation - parse for XSD typing
            term_str = str(term)
            if term_str.startswith('<') and term_str.endswith('>'):
                # URI reference
                return RDFLibURIRef(term_str.strip('<>'))
            elif term_str.startswith('_:'):
                # Blank node
                return RDFLibBNode(term_str[2:])
            else:
                # Literal - use existing parser for XSD typing
                return self._parse_stored_literal(term_str)
    
    def _parse_stored_literal(self, stored_literal: str) -> RDFLibLiteral:
        """
        Parse a stored literal value that may contain XSD datatype information.
        Handles both plain literals and XSD-typed literals from RDF storage.
        Returns RDFLib Literal objects that VitalSigns can process with toPython().
        
        Args:
            stored_literal: Literal string from RDF store (may include XSD typing)
            
        Returns:
            Properly typed RDFLib Literal object
        """
        try:
            # Check if this is an XSD-typed literal: "value"^^<datatype>
            if '^^<' in stored_literal:
                # Split on ^^< to separate value and datatype
                value_part, datatype_part = stored_literal.split('^^<', 1)
                
                # Remove quotes from value
                value = value_part.strip('"').strip("'")
                
                # Remove > from datatype and create URIRef
                datatype_uri = datatype_part.rstrip('>')
                
                # Return as RDFLib Literal with proper datatype
                # This allows VitalSigns to use obj_value.toPython() correctly
                return RDFLibLiteral(value, datatype=RDFLibURIRef(datatype_uri))
            else:
                # Plain literal - just remove quotes and angle brackets
                clean_value = stored_literal.strip('<>').strip('"').strip("'")
                return RDFLibLiteral(clean_value)
                
        except Exception as e:
            self.logger.warning(f"Error parsing stored literal '{stored_literal}': {e}")
            # Fallback to plain literal
            clean_value = stored_literal.strip('<>').strip('"').strip("'")
            return RDFLibLiteral(clean_value)
    
    def _parse_literal_object(self, literal_part: str) -> Union[str, Literal]:
        """
        Parse a literal object that may have XSD datatype information.
        
        Args:
            literal_part: Literal part of N-Triple (e.g., "value"^^<datatype>)
            
        Returns:
            Literal object with proper datatype or plain string
        """
        try:
            # Check if it has datatype: "value"^^<datatype>
            if '^^<' in literal_part:
                # Split on ^^< to separate value and datatype
                value_part, datatype_part = literal_part.split('^^<', 1)
                
                # Remove quotes from value
                value = value_part.strip('"')
                
                # Remove > from datatype
                datatype = datatype_part.rstrip('>')
                
                # Return as pyoxigraph Literal with datatype
                return Literal(value, datatype=NamedNode(datatype))
            else:
                # Plain literal - remove quotes
                return literal_part.strip('"')
                
        except Exception as e:
            self.logger.warning(f"Error parsing literal '{literal_part}': {e}")
            # Fallback to plain string
            return literal_part.strip('"')
    
    def _get_typed_literal(self, graph_object: GraphObject, prop_uri: str, value: Any) -> Union[NamedNode, BlankNode, Literal]:
        """
        Get a properly typed RDF literal based on VitalSigns property metadata.
        
        Args:
            graph_object: The GraphObject instance to get property metadata from
            prop_uri: Property URI
            value: Property value
            
        Returns:
            Properly typed RDF term
        """
        try:
            # Get property metadata from the GraphObject
            allowed_props = graph_object.get_allowed_properties()
            prop_metadata = None
            
            # Find the property metadata by URI
            for prop in allowed_props:
                if str(prop.get('uri', '')) == prop_uri:
                    prop_metadata = prop
                    break
            
            if prop_metadata:
                prop_class = prop_metadata.get('prop_class')
                self.logger.debug(f"Property {prop_uri} has class: {prop_class}")
                
                # Handle different property types with proper XSD typing
                if prop_class:
                    class_name = prop_class.__name__ if hasattr(prop_class, '__name__') else str(prop_class)
                    
                    if 'DateTime' in class_name:
                        # DateTime property - use xsd:dateTime
                        return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#dateTime"))
                    elif 'Date' in class_name:
                        # Date property - use xsd:date
                        return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#date"))
                    elif 'Long' in class_name or 'Integer' in class_name:
                        # Numeric property - use xsd:long or xsd:integer
                        return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#long"))
                    elif 'Double' in class_name or 'Float' in class_name:
                        # Decimal property - use xsd:double
                        return Literal(str(value), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#double"))
                    elif 'Boolean' in class_name:
                        # Boolean property - use xsd:boolean
                        return Literal(str(value).lower(), datatype=NamedNode("http://www.w3.org/2001/XMLSchema#boolean"))
            
            # Default: return as string literal
            self.logger.debug(f"No specific typing found for {prop_uri}, using string literal")
            return Literal(str(value))
            
        except Exception as e:
            self.logger.warning(f"Error getting typed literal for {prop_uri}: {e}")
            # Fallback to string literal
            return Literal(str(value))
    
    def _to_rdf_term(self, term: Union[str, NamedNode, BlankNode, Literal], 
                     allow_literal: bool = True, 
                     force_named_node: bool = False) -> Union[NamedNode, BlankNode, Literal]:
        """
        Convert a term to an appropriate RDF term.
        
        Args:
            term: Input term
            allow_literal: Whether to allow literal values
            force_named_node: Force conversion to NamedNode
            
        Returns:
            Appropriate RDF term
        """
        if isinstance(term, (NamedNode, BlankNode, Literal)):
            return term
        
        if isinstance(term, str):
            if force_named_node or (term.startswith('http://') or term.startswith('https://') or term.startswith('urn:')):
                return NamedNode(term)
            elif term.startswith('_:'):
                return BlankNode(term[2:])  # Remove _: prefix
            elif allow_literal:
                return Literal(term)
            else:
                # Assume it's a URI if not allowing literals
                return NamedNode(term)
        
        raise ValueError(f"Cannot convert {term} to RDF term")
    
    def get_store_id(self) -> str:
        """
        Get the unique identifier for this store.
        
        Returns:
            Store identifier string
        """
        return self.store_id