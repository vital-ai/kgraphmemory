from SPARQLWrapper import SPARQLWrapper
from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from kgraphmemory.kginteraction_graph import KGInteractionGraph


class KGraphMemoryMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# types have descriptions which are used in instances
# of objects using that type
# this allows the description text to be used in vector search
# to find instances of interest

# TODO
# update to maintain a list of N graphs, similar to graph store with graph URIs


class KGraphMemory(metaclass=KGraphMemoryMeta):

    def __init__(self):
        self._graph_map = {}
        self._graph_database = None

    def set_graph_database(self, graph_database: SPARQLWrapper):
        self._graph_database = graph_database

    def unset_graph_database(self, graph_database: SPARQLWrapper):
        self._graph_database = None

    def save_entity_type(self, entity_type):
        pass

    def delete_entity_type(self, entity_type_uri: str):
        pass

    def save_relation_type(self, relation_type):
        pass

    def delete_relation_type(self, entity_type_uri: str):
        pass

    def save_frame_type(self, frame_type):
        pass

    def delete_frame_type(self, frame_type_uri: str):
        pass

    def save_slot_type(self, slot_type):
        pass

    def delete_slot_type(self, slot_type_uri: str):
        pass

    def create_interaction_graph(self, interaction: KGInteraction):
        graph_uri = interaction.URI
        graph = KGInteractionGraph(interaction)
        self._graph_map[graph_uri] = graph
        return graph

    def serialize_interaction_graph(self, graph_uri: str):
        pass

    def recall_interaction_graph(self, graph_uri: str):
        pass

    def delete_interaction_graph(self, graph_uri: str):
        pass

    def retrieve_interaction_graphs(
            self,
            account_uri: str,
            login_uri: str = None,
            after_interaction_uri: str = None,
            limit: int = 10):
        pass

    def get_entity_types(
            self,
            after_entity_type_uri: str = None,
            limit: int = 10,
            include_db: bool = False):
        # get from graphs and graph database
        return None

    def get_relation_types(
            self,
            after_relation_type_uri: str = None,
            limit: int = 10,
            include_db: bool = False):
        # get from graphs and graph database
        return None

    def get_frame_types(
            self,
            after_frame_type_uri: str = None,
            limit: int = 10,
            include_db: bool = False):
        # get from graphs and graph database
        return None

    def get_slot_types(
            self,
            after_slot_type_uri: str = None,
            limit: int = 10,
            include_db: bool = False):
        # get from graphs and graph database
        return None

    def get_interaction_graph(self, graph_uri: str):
        # local memory, not database
        return self._graph_map[graph_uri]

    def remove_interaction_graph(self, graph_uri: str):
        # local memory, not database
        graph = self._graph_map.pop(graph_uri)
        return graph

