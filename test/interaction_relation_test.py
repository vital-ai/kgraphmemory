from ai_haley_kg_domain.model.KGEntity import KGEntity
from ai_haley_kg_domain.model.KGInteraction import KGInteraction

from kgraphmemory.kginteraction_graph import KGInteractionGraph
from kgraphmemory.utils.uri_generator import URIGenerator


def main():
    print('Hello World')

    interaction = KGInteraction()

    interaction.URI = URIGenerator.generate_uri()

    print(interaction.to_json())

    graph = KGInteractionGraph(interaction)

    # people
    person1 = KGEntity()
    person1.URI = URIGenerator.generate_uri()

    person2 = KGEntity()
    person2.URI = URIGenerator.generate_uri()

    person3 = KGEntity()
    person3.URI = URIGenerator.generate_uri()

    person4 = KGEntity()
    person4.URI = URIGenerator.generate_uri()

    # company
    company1 = KGEntity()
    company1.URI = URIGenerator.generate_uri()

    company2 = KGEntity()
    company2.URI = URIGenerator.generate_uri()

    # location
    location1 = KGEntity()
    location1.URI = URIGenerator.generate_uri()

    location2 = KGEntity()
    location2.URI = URIGenerator.generate_uri()

    location3 = KGEntity()
    location3.URI = URIGenerator.generate_uri()

    # relations

    # people --> company

    # people --> location

    # company --> location

    # add to interaction graph

    # query people at location

    # visualize entity/relation graph


if __name__ == "__main__":
    main()


