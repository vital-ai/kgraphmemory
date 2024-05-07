from ai_haley_kg_domain.model.Edge_hasEntityKGFrame import Edge_hasEntityKGFrame
from ai_haley_kg_domain.model.Edge_hasInteractionKGEntity import Edge_hasInteractionKGEntity
from ai_haley_kg_domain.model.Edge_hasInteractionKGFrame import Edge_hasInteractionKGFrame
from ai_haley_kg_domain.model.Edge_hasKGRelation import Edge_hasKGRelation
from ai_haley_kg_domain.model.Edge_hasKGSlot import Edge_hasKGSlot
from ai_haley_kg_domain.model.KGEntity import KGEntity
from ai_haley_kg_domain.model.KGFrame import KGFrame
from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from ai_haley_kg_domain.model.KGSlot import KGSlot
from vital_ai_vitalsigns.query.result_element import ResultElement
from vital_ai_vitalsigns.query.result_list import ResultList

from kgraphmemory.kgraph import KGraph
from kgraphmemory.kgresult_list import KGResultList
from kgraphmemory.kgresult_match import KGResultMatch
from kgraphmemory.kgstatus import KGStatus
from kgraphmemory.utils.uri_generator import URIGenerator


class KGInteractionGraph(KGraph):
    def __init__(self, interaction: KGInteraction):
        super().__init__()
        self._interaction = interaction

    def get_interaction(self):
        return self._interaction

    def set_interaction(self, interaction: KGInteraction):
        # adjust edges from interaction --> nodes
        self._interaction = interaction

    def get_messages(self) -> ResultList:
        pass

    def search_entities(self, entity_type: str) -> KGResultList:
        interaction_uri = str(self._interaction.URI)
        result_list = KGResultList()
        print('InteractionURI: ' + interaction_uri)
        nodes = self.graph.get_nodes_outgoing(interaction_uri)
        entities = [node for node in nodes if isinstance(node, KGEntity)]
        # TODO push filter into search
        print('Searching entities...')
        results = self.graph.search(entity_type, 'http://vital.ai/ontology/haley-ai-kg#KGEntity', 1000)
        print('Searching entities...done.')
        for r in results:
            go = r.graph_object
            print(f"Entity Name: {go.name}")
            go_score = r.score
            if isinstance(go, KGEntity):
                if go in entities:
                    match = KGResultMatch(go_score)
                    match.add_match("entity", go)
                    result_list.add_result(match)
        return result_list

    def search_entity_frames(
            self,
            entity_type: str,
            frame_type: str) -> KGResultList:

        result_list = KGResultList()

        entity_result_list = self.search_entities(entity_type)

        if len(entity_result_list) > 0:
            entity_match = entity_result_list[0]
            entity = entity_match['entity']
            entity_uri = entity.URI

            print('Searching entity frames...')
            frame_result_list = self.search_entity_frames(entity_uri, frame_type)

            if len(frame_result_list) > 0:
                frame_match = frame_result_list[0]
                frame = frame_match['frame']

                result_match = KGResultMatch()

                result_match.add_match('entity', entity)
                result_match.add_match('frame', frame)

                result_list.add_result(result_match)

        return result_list

    def search_entity_frame_slots(
            self,
            entity_type: str,
            frame_type: str,
            slot_type: str) -> KGResultList:

        result_list = KGResultList()

        print('Searching entities...')
        entity_result_list = self.search_entities(entity_type)

        if len(entity_result_list) > 0:

            for entity_match in entity_result_list:
                # entity_match = entity_result_list[0]
                entity = entity_match.matches['entity']
                entity_uri = entity.URI

                print('Searching entity frames...')
                frame_result_list = self.search_entity_frames(entity_uri, frame_type)

                if len(frame_result_list) > 0:
                    frame_match = frame_result_list[0]
                    frame = frame_match.matches['frame']
                    frame_uri = frame.URI

                    print('Searching entity frame slots...')
                    slot_result_list = self.search_frame_slots(frame_uri, slot_type)

                    if len(slot_result_list) > 0:
                        slot_match = slot_result_list[0]
                        slot = slot_match.matches['slot']
                        slot_uri = slot.URI

                        result_match = KGResultMatch()

                        result_match.add_match('entity', entity)
                        result_match.add_match('frame', frame)
                        result_match.add_match('slot', slot)

                        result_list.add_result(result_match)

        return result_list

    def get_entities(self) -> ResultList:
        result_list = ResultList()
        for g in self.graph:
            if isinstance(g, KGEntity):
                result_list.add_result(g)
        return result_list

    def get_relations(self) -> ResultList:
        result_list = ResultList()
        for g in self.graph:
            if isinstance(g, Edge_hasKGRelation):
                result_list.add_result(g)
        return result_list

    def search_relations(self, relation_type: str) -> KGResultList:
        result_list = KGResultList()

        relations = [edge for edge in self.graph if isinstance(edge, Edge_hasKGRelation)]

        results = self.graph.search(relation_type, None, 1000)

        for r in results:
            go = r.graph_object
            go_score = r.score
            if isinstance(go, Edge_hasKGRelation):
                if go in relations:
                    match = KGResultMatch(go_score)
                    match.add_match("relation", go)
                    result_list.add_result(match)

        return result_list

    def get_entity_relations(
            self,
            entity_uri: str,
            include_source: bool = True,
            include_destination: bool = True) -> ResultList:

        result_list = ResultList()

        if include_source:
            in_edges = self.graph.get_edges_incoming(entity_uri)
            rel_in_edges = [edge for edge in in_edges if isinstance(edge, Edge_hasKGRelation)]
            for r in rel_in_edges:
                result_list.add_result(r)

        if include_destination:
            out_edges = self.graph.get_edges_outgoing(entity_uri)
            rel_out_edges = [edge for edge in out_edges if isinstance(edge, Edge_hasKGRelation)]
            for r in rel_out_edges:
                result_list.add_result(r)

        return result_list

    def search_entity_relations(
            self,
            entity_uri,
            relation_type: str) -> KGResultList:
        result_list = KGResultList()
        in_edges = self.graph.get_edges_incoming(entity_uri)
        out_edges = self.graph.get_edges_outgoing(entity_uri)
        rel_out_edges = [edge for edge in out_edges if isinstance(edge, Edge_hasKGRelation)]
        rel_in_edges = [edge for edge in in_edges if isinstance(edge, Edge_hasKGRelation)]
        edges = rel_out_edges + rel_in_edges
        # TODO push filter into search
        results = self.graph.search(relation_type, None, 1000)
        for r in results:
            go = r.graph_object
            go_score = r.score
            if isinstance(go, Edge_hasKGRelation):
                if go in edges:
                    match = KGResultMatch(go_score)
                    match.add_match("relation", go)
                    result_list.add_result(match)
        return result_list

    def get_frames(self) -> ResultList:
        interaction_uri = str(self._interaction.URI)
        nodes = self.graph.get_nodes_outgoing(interaction_uri)
        frames = [node for node in nodes if isinstance(node, KGFrame)]
        result_list = ResultList()
        for f in frames:
            result_list.add_result(f)
        return result_list

    def search_frames(self, frame_type: str) -> KGResultList:
        interaction_uri = self._interaction.URI
        result_list = KGResultList()
        nodes = self.graph.get_nodes_outgoing(interaction_uri)
        frames = [node for node in nodes if isinstance(node, KGFrame)]
        # TODO push filter into search
        results = self.graph.search(frame_type, 'http://vital.ai/ontology/haley-ai-kg#KGFrame', 1000)
        for r in results:
            go = r.graph_object
            go_score = r.score
            if isinstance(go, KGFrame):
                if go in frames:
                    match = KGResultMatch(go_score)
                    match.add_match("frame", go)
                    result_list.add_result(match)
        return result_list

    def get_entity_frames(self, entity_uri: str) -> ResultList:
        entity = self.graph.get(entity_uri)
        nodes = self.graph.get_nodes_outgoing(entity_uri)
        frames = [node for node in nodes if isinstance(node, KGFrame)]
        result_list = ResultList()
        for f in frames:
            result_list.add_result(f)
        return result_list

    def search_entity_frames(
            self,
            entity_uri: str,
            frame_type: str) -> KGResultList:
        result_list = KGResultList()
        nodes = self.graph.get_nodes_outgoing(entity_uri)
        frames = [node for node in nodes if isinstance(node, KGFrame)]
        # TODO push filter into search
        results = self.graph.search(frame_type, 'http://vital.ai/ontology/haley-ai-kg#KGFrame', 1000)
        for r in results:
            go = r.graph_object
            go_score = r.score
            if isinstance(go, KGFrame):
                if go in frames:
                    match = KGResultMatch(go_score)
                    match.add_match("frame", go)
                    result_list.add_result(match)
        return result_list

    def get_frame_slots(self, frame_uri: str) -> ResultList:
        frame = self.graph.get(frame_uri)
        nodes = self.graph.get_nodes_outgoing(frame_uri)
        slots = [node for node in nodes if isinstance(node, KGSlot)]
        result_list = ResultList()
        for s in slots:
            result_list.add_result(s)
        return result_list

    def search_frame_slots(
            self,
            frame_uri: str,
            slot_type: str) -> KGResultList:
        result_list = KGResultList()
        nodes = self.graph.get_nodes_outgoing(str(frame_uri))
        slots = [node for node in nodes if isinstance(node, KGSlot)]
        # TODO push filter into search
        # Must account for all types of slots in filter
        results = self.graph.search(slot_type, None, 1000)
        for r in results:
            go = r.graph_object
            go_score = r.score
            if isinstance(go, KGSlot):
                if go in slots:
                    slot_name = go.name

                    # print(f"SlotName: {slot_name} : {go_score}")

                    match = KGResultMatch(go_score)
                    match.add_match("slot", go)
                    result_list.add_result(match)
        return result_list

    def add_message(self, message) -> KGStatus:
        status = KGStatus()
        return status

    def add_entity(self, entity) -> KGStatus:
        interaction_uri = self._interaction.URI
        edge = Edge_hasInteractionKGEntity()
        edge.URI = URIGenerator.generate_uri()
        edge.name = 'edge: ' + str(edge.URI)
        edge.edgeSource = interaction_uri
        edge.edgeDestination = entity.URI
        self.graph.add_objects([entity, edge])
        status = KGStatus()
        return status

    def add_frame(self, frame) -> KGStatus:
        interaction_uri = self._interaction.URI
        edge = Edge_hasInteractionKGFrame()
        edge.URI = URIGenerator.generate_uri()
        edge.name = 'edge: ' + str(edge.URI)
        edge.edgeSource = interaction_uri
        edge.edgeDestination = frame.URI
        self.graph.add_objects([frame, edge])
        status = KGStatus()
        return status

    # Relation is type Edge_hasKGRelation
    # top level relations must have each entity connected
    # to the interaction
    def add_relation(self, relation) -> KGStatus:
        self.graph.add_objects([relation])
        status = KGStatus()
        return status

    def add_entity_frame(self, entity_uri: str, frame) -> KGStatus:
        # interaction must be connected to entity
        interaction_uri = self._interaction.URI
        edge = Edge_hasEntityKGFrame()
        edge.URI = URIGenerator.generate_uri()
        edge.name = 'edge: ' + str(edge.URI)
        edge.edgeSource = entity_uri
        edge.edgeDestination = frame.URI
        self.graph.add_objects([frame, edge])
        status = KGStatus()
        return status

    def add_frame_slot(self, frame_uri: str, slot) -> KGStatus:
        # interaction must be connected to entity, connected
        # to frame
        interaction_uri = self._interaction.URI
        edge = Edge_hasKGSlot()
        edge.URI = URIGenerator.generate_uri()
        edge.name = 'edge: ' + str(edge.URI)
        edge.edgeSource = frame_uri
        edge.edgeDestination = slot.URI
        self.graph.add_objects([slot, edge])
        status = KGStatus()
        return status

    # removing handles removing edges

    def remove_entity(self, entity_uri: str) -> KGStatus:
        status = KGStatus()
        return status

    def remove_frame(self, frame_uri: str) -> KGStatus:
        status = KGStatus()
        return status

    def remove_relation(self, relation_uri: str) -> KGStatus:
        status = KGStatus()
        return status

    def remove_slot(self, slot_uri: str) -> KGStatus:
        status = KGStatus()
        return status
