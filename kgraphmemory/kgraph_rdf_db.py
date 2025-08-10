from typing import List, Dict, Any, Optional, Union, Iterator, TypeVar
import pyoxigraph as ox
from pyoxigraph import Store, Quad, NamedNode, BlankNode, Literal, Triple
from pyoxigraph import Variable, QuerySolutions, QueryTriples, QueryBoolean
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from vital_ai_vitalsigns.model.GraphObject import GraphObject

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
            else:
                quad = Quad(s, p, o)
                
            self.store.add(quad)
            return True
        except Exception as e:
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
            results = self.store.query(query)
            
            if isinstance(results, QuerySolutions):
                # SELECT queries return QuerySolutions
                result_list = []
                # Get variable names from the QuerySolutions object
                variables = results.variables
                
                for solution in results:
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
        Add RDF triples for a GraphObject using its to_dict() method.
        Handles special cases for 'URI', 'type', and 'types' fields.
        
        Args:
            graph_object: Concrete GraphObject instance (e.g., KGEntity, VITAL_Node, VITAL_Edge).
                         Note: GraphObject is abstract - pass concrete subclass instances only.
            graph: Optional named graph to add triples to
            
        Returns:
            True if triples were successfully added
        """
        try:
            object_uri = str(graph_object.URI)
            
            # Get property values using the built-in to_dict() method (returns structured data)
            property_dict = graph_object.to_dict()
            
            # Collect all unique type URIs first
            type_uris = set()
            
            # Handle type properties to collect unique types
            if 'type' in property_dict and property_dict['type']:
                type_uris.add(str(property_dict['type']))
            
            if 'types' in property_dict and property_dict['types']:
                if isinstance(property_dict['types'], list):
                    for type_uri in property_dict['types']:
                        if type_uri:
                            type_uris.add(str(type_uri))
                else:
                    type_uris.add(str(property_dict['types']))
            
            # Add unique rdf:type triples
            rdf_type_predicate = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            for type_uri in type_uris:
                self.add_triple(object_uri, rdf_type_predicate, type_uri, graph)
            
            # Handle URI property mapping
            if 'URI' in property_dict and property_dict['URI']:
                uri_property = "http://vital.ai/ontology/vital-core#URIProp"
                self.add_triple(object_uri, uri_property, str(property_dict['URI']), graph)
            
            # Add other property triples using URIs directly from dictionary
            for prop_uri, value in property_dict.items():
                if prop_uri not in ['URI', 'type', 'types'] and value is not None:
                    # Regular property
                    if isinstance(value, list):
                        # Skip other list values for now
                        continue
                    else:
                        self.add_triple(object_uri, prop_uri, str(value), graph)
            
            return True
        except Exception as e:
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
                for subject, predicate, obj, graph_name in triples:
                    # Clean all URI strings by removing angle brackets
                    clean_subject = subject.strip('<>')
                    clean_predicate = predicate.strip('<>')
                    clean_obj = obj.strip('<>')
                    
                    # Convert subject to proper RDFLib object
                    if clean_subject.startswith('_:'):
                        # Blank node
                        rdf_subject = BNode(clean_subject[2:])  # Remove '_:' prefix
                    else:
                        # URI reference
                        rdf_subject = URIRef(clean_subject)
                    
                    # Convert predicate to URIRef (predicates are always URIs)
                    rdf_predicate = URIRef(clean_predicate)
                    
                    # Convert object to proper RDFLib object
                    if clean_obj.startswith('_:'):
                        # Blank node
                        rdf_object = BNode(clean_obj[2:])  # Remove '_:' prefix
                    elif clean_obj.startswith('http://') or clean_obj.startswith('https://'):
                        # URI reference
                        rdf_object = URIRef(clean_obj)
                    else:
                        # Literal value - strip quotes if present
                        clean_literal = obj.strip('<>').strip('"').strip("'")
                        rdf_object = Literal(clean_literal)
                    
                    yield (rdf_subject, rdf_predicate, rdf_object)
            
            # Use VitalSigns to create GraphObject from triples
            vs = VitalSigns()
            graph_object = vs.from_triples(triple_generator())
            
            return graph_object
            
        except Exception as e:
            print(f"Error retrieving GraphObject for {subject_uri}: {e}")
            return None
    
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