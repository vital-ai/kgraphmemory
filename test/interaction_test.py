from datetime import datetime, timezone
from SPARQLWrapper import SPARQLWrapper, JSON
from ai_haley_kg_domain.model.KGDateTimeSlot import KGDateTimeSlot
from ai_haley_kg_domain.model.KGEntity import KGEntity
from ai_haley_kg_domain.model.KGFrame import KGFrame
from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from ai_haley_kg_domain.model.KGSlot import KGSlot
from ai_haley_kg_domain.model.KGTextSlot import KGTextSlot
from ai_haley_kg_domain.model.properties.Property_hasKGEntityTypeDescription import Property_hasKGEntityTypeDescription
from ai_haley_kg_domain.model.properties.Property_hasKGFrameTypeDescription import Property_hasKGFrameTypeDescription
from ai_haley_kg_domain.model.properties.Property_hasKGSlotTypeDescription import Property_hasKGSlotTypeDescription
from vital_ai_vitalsigns.embedding.embedding_model import EmbeddingModel
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from kgraphmemory.kginteraction_graph import KGInteractionGraph
from kgraphmemory.utils.uri_generator import URIGenerator
import matplotlib.pyplot as plt
import networkx as nx
import logging


def main():
    print('Hello World')
    logging.basicConfig(level=logging.INFO)

    vs = VitalSigns()
    embedder = EmbeddingModel()
    vs.put_embedding_model(embedder.get_model_id(), embedder)

    interaction = KGInteraction()
    interaction.URI = URIGenerator.generate_uri()
    print(interaction.to_json())

    graph = KGInteractionGraph(interaction)

    # entity_class_uri = KGEntity.get_class_uri()
    # frame_class_uri = KGFrame.get_class_uri()
    # slot_class_uri = KGSlot.get_class_uri()

    # entity_type_description_property_uri = Property_hasKGEntityTypeDescription.get_uri()
    # frame_type_description_property_uri = Property_hasKGFrameTypeDescription.get_uri()
    # slot_type_description_property_uri = Property_hasKGSlotTypeDescription.get_uri()

    # graph.graph.set_vector_properties(entity_class_uri, [entity_type_description_property_uri])
    # graph.graph.set_vector_properties(frame_class_uri, [frame_type_description_property_uri])
    # graph.graph.set_vector_properties(slot_class_uri, [slot_type_description_property_uri])

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    query_orig = """
        SELECT DISTINCT ?person ?personLabel ?birthDate ?deathDate ?partyLabel WHERE {
            ?person wdt:P39 wd:Q11696;  # Position held = President of the United States
                    wdt:P569 ?birthDate; # Date of birth
                    wdt:P102 ?party .    # Political party

            OPTIONAL { ?person wdt:P570 ?deathDate } # Date of death (optional)

            # Ensure the person is human and exclude fictional characters
            ?person wdt:P31 wd:Q5 .      # Instance of human

            # Get labels for person and party
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        ORDER BY ?birthDate
        """

    query = """
    SELECT ?person ?personLabel ?birthDate ?deathDate (GROUP_CONCAT(DISTINCT ?partyLabel; separator=", ") AS ?parties) WHERE {
        ?person wdt:P39 wd:Q11696; # Position held = President of the United States
        wdt:P569 ?birthDate .  # Date of birth
  
        OPTIONAL { ?person wdt:P570 ?deathDate } # Date of death (optional)
        OPTIONAL { ?person wdt:P102 ?party .     # Political party
             ?party rdfs:label ?partyLabel 
             FILTER (lang(?partyLabel) = "en")
        }

        # Ensure the person is human and exclude fictional characters
        ?person wdt:P31 wd:Q5 .           # Instance of human

        # Get labels for person
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    
    GROUP BY ?person ?personLabel ?birthDate ?deathDate
    ORDER BY ?birthDate
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    entity_count = 0

    entity_name_list = []

    # skip plot
    first_entity = False

    for result in results["results"]["bindings"]:

        name = result["personLabel"]["value"]

        birth_date_raw = result["birthDate"]["value"]
        birth_date = parse_date(birth_date_raw)

        death_date_raw = result.get("deathDate", {}).get("value")
        death_date = parse_date(death_date_raw)

        # party = result["partyLabel"]["value"]
        party = result["parties"]["value"]

        entity_name_list.append(name)

        print(f"{name}:")
        print(f"  Birth Date: {birth_date}")
        print(f"  Death Date String: {death_date_raw}")
        print(f"  Death Date: {death_date}")
        print(f"  Party: {party}")
        print()

        president = KGEntity()
        president.URI = URIGenerator.generate_uri()
        president.name = name
        president.kGEntityType = 'urn:president_type'
        president.kGEntityTypeDescription = 'US President'

        bio_frame = KGFrame()
        bio_frame.URI = URIGenerator.generate_uri()
        bio_frame.name = 'biography frame: ' + name
        bio_frame.kGFrameType = 'urn:biography_type'
        bio_frame.kGFrameTypeDescription = 'Biography Description'

        birth_slot = KGDateTimeSlot()
        birth_slot.URI = URIGenerator.generate_uri()
        # birth_slot.name = 'birth date slot: ' + name
        birth_slot.kGSlotType = 'urn:birth_type'
        birth_slot.kGSlotTypeDescription = 'The date the person was born'
        birth_slot.dateTimeSlotValue = birth_date

        birth_slot.name = 'The date the person was born'

        death_slot = KGDateTimeSlot()
        death_slot.URI = URIGenerator.generate_uri()
        # death_slot.name = 'death date slot: ' + name
        death_slot.kGSlotType = 'urn:death_type'
        death_slot.kGSlotTypeDescription = 'The date the person died'
        death_slot.dateTimeSlotValue = death_date

        death_slot.name = 'The date the person died'

        party_slot = KGTextSlot()
        party_slot.URI = URIGenerator.generate_uri()
        # party_slot.name = 'party slot: ' + name
        party_slot.kGSlotType = 'urn:political_party_type'
        party_slot.kGSlotTypeDescription = 'Political Party or Parties, Political Affiliation'
        party_slot.textSlotValue = party

        party_slot.name = 'Political Party or Parties, Political Affiliation'

        president_graph = [
            president,
            bio_frame,
            birth_slot,
            death_slot,
            party_slot
        ]

        entity_count = entity_count + 1

        if first_entity:

            first_entity = False

            def wrap_label(label, width):
                """Wrap the label to a given width."""
                import textwrap
                return '\n'.join(textwrap.wrap(label, width))

            nx_g = nx.Graph()

            nx_g.add_node(0, label='KGInteraction')

            nx_g.add_node(1, label=(wrap_label('KGEntity: ' + str(president.name), 15)))

            nx_g.add_node(2, label='Biography Frame')

            nx_g.add_node(3, label='KGSlot: Birth')

            nx_g.add_node(4, label='KGSlot: Death')

            nx_g.add_node(5, label='KGSlot: Political Party')

            nx_g.add_edge(0, 1, label='hasKGEntity')

            nx_g.add_edge(1, 2, label='hasKGFrame')

            nx_g.add_edge(2, 3, label='hasKGSlot')

            nx_g.add_edge(2, 4, label='hasKGSlot')

            nx_g.add_edge(2, 5, label='hasKGSlot')

            pos = nx.spring_layout(nx_g, seed=42)

            pos[0] = (-1, 1)

            fig, ax = plt.subplots(figsize=(8, 8))

            # plt.figure(figsize=(8, 6))
            # plt.xlim(-2, 2)
            # plt.ylim(-1.5, 1.5)

            nx.draw(nx_g, pos, node_color='skyblue', edge_color='gray', font_weight='bold', node_size=800, ax=ax)

            edge_labels = nx.get_edge_attributes(nx_g, 'label')

            nx.draw_networkx_edge_labels(nx_g, pos, edge_labels=edge_labels, ax=ax)

            node_labels = nx.get_node_attributes(nx_g, 'label')

            nx.draw_networkx_labels(
                nx_g,
                pos,
                labels=node_labels,
                verticalalignment='bottom',
                horizontalalignment='center',
                ax=ax
                # bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3'),
                # bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3')
            )

            ax.set_xlim(ax.get_xlim()[0] * 1.1, ax.get_xlim()[1] * 1.1)
            ax.set_ylim(ax.get_ylim()[0] * 1.1, ax.get_ylim()[1] * 1.1)

            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

            plt.savefig("/Users/hadfield/Desktop/kgentity_graph_1.png")

            plt.show()

        for g in president_graph:
            print(g.to_json())

        # add objects to graph
        # print('Adding: ' + president.to_json())

        graph.add_entity(president)
        graph.add_entity_frame(president.URI, bio_frame)
        graph.add_frame_slot(bio_frame.URI, birth_slot)
        graph.add_frame_slot(bio_frame.URI, death_slot)
        graph.add_frame_slot(bio_frame.URI, party_slot)

    # print(f"Entity Count: {entity_count}")

    graph_results = graph.search_entity_frame_slots(
        'president',
        'biography',
        'voting')

    result_count = len(graph_results)

    # print(f"Result Count: {result_count}")

    birth_count = 0
    death_count = 0
    party_count = 0

    for r in graph_results:
        matches = r.matches
        entity = matches['entity']
        frame = matches['frame']
        slot = matches['slot']

        # print(entity.to_json())
        # print(frame.to_json())
        # print(slot.to_json())

        name = entity.name
        frame_name = frame.name
        slot_name = slot.name

        slot_value = None

        if isinstance(slot, KGTextSlot):
            slot_value = slot.textSlotValue

        # TODO fix date typing
        if isinstance(slot, KGDateTimeSlot):
            slot_value = slot.dateTimeSlotValue

        # print(f"Name: {name} Frame: {frame_name} Slot: {slot_name}")

        print(f"{name}: {slot_value}")

        if 'Political' in str(slot_name):
            party_count += 1

        if 'born' in str(slot_name):
            birth_count += 1

        if 'died' in str(slot_name):
            death_count += 1

    print(f"Party Count: {party_count}")
    print(f"Birth Count: {birth_count}")
    print(f"Death Count: {death_count}")

    print(f"Result Count: {result_count}")

    # for n in entity_name_list:
    #    print(n)


def parse_date(date_string):
    """Parse a date string into a datetime object or return None."""
    if date_string:
        try:
            date_format = "%Y-%m-%dT%H:%M:%SZ"

            # Parse the date string
            dt = datetime.strptime(date_string, date_format)

            # Set the timezone to UTC
            dt = dt.replace(tzinfo=timezone.utc)

            return dt
        except ValueError:
            return None
    return None


if __name__ == "__main__":
    main()
