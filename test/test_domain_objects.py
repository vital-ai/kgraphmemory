from ai_haley_kg_domain.model.KGEntity import KGEntity
from vital_ai_vitalsigns.vitalsigns import VitalSigns


def main():

    print('Hello World')

    # vs = VitalSigns()
    # vs.get_registry().build_registry()

    kg_entity = KGEntity()
    kg_entity.URI = 'urn:kg_entity123'
    kg_entity.name = 'KG Entity Name'

    print(kg_entity.to_json())
    print(kg_entity.to_rdf())


if __name__ == "__main__":
    main()
