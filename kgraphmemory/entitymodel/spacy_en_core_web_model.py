from kgraphmemory.entitymodel.entitymodel import EntityModel
from enum import Enum
from collections import namedtuple


class SpacyEnCoreWebModel(EntityModel):
    @classmethod
    def get_label_description(cls, label):
        entity_info = SpacyEnCoreWebEntityType.get_by_label(label)
        entity_description = entity_info.value.description
        return entity_description

    @classmethod
    def get_entity_type_list(cls):
        return SpacyEnCoreWebEntityType.list_all()


SpacyEnCoreWebEntityTypeInfo = namedtuple('SpacyEnCoreWebEntityTypeInfo', ['label', 'description'])


class SpacyEnCoreWebEntityType(Enum):
    PERSON = SpacyEnCoreWebEntityTypeInfo(label="PERSON", description="People, including fictional")
    NORP = SpacyEnCoreWebEntityTypeInfo(label="NORP", description="Nationalities, religious and political groups")
    FAC = SpacyEnCoreWebEntityTypeInfo(label="FAC", description="Facilities for activities")
    ORG = SpacyEnCoreWebEntityTypeInfo(label="ORG", description="Organizations, companies, agencies, institutions")
    GPE = SpacyEnCoreWebEntityTypeInfo(label="GPE", description="Countries, cities, states")
    LOC = SpacyEnCoreWebEntityTypeInfo(label="LOC", description="Non-GPE locations, mountain ranges, bodies of water")
    PRODUCT = SpacyEnCoreWebEntityTypeInfo(label="PRODUCT", description="Objects, vehicles, foods, etc. (not services)")
    EVENT = SpacyEnCoreWebEntityTypeInfo(label="EVENT", description="Named hurricanes, battles, wars, sports events, etc.")
    WORK_OF_ART = SpacyEnCoreWebEntityTypeInfo(label="WORK_OF_ART", description="Titles of books, songs, etc.")
    LAW = SpacyEnCoreWebEntityTypeInfo(label="LAW", description="Named documents made into laws")
    LANGUAGE = SpacyEnCoreWebEntityTypeInfo(label="LANGUAGE", description="Any named language")
    DATE = SpacyEnCoreWebEntityTypeInfo(label="DATE", description="Absolute or relative dates or periods")
    TIME = SpacyEnCoreWebEntityTypeInfo(label="TIME", description="Times smaller than a day")
    PERCENT = SpacyEnCoreWebEntityTypeInfo(label="PERCENT", description="Percentage, including \"%\"")
    MONEY = SpacyEnCoreWebEntityTypeInfo(label="MONEY", description="Monetary values, including unit")
    QUANTITY = SpacyEnCoreWebEntityTypeInfo(label="QUANTITY", description="Measurements, as of weight or distance")
    ORDINAL = SpacyEnCoreWebEntityTypeInfo(label="ORDINAL", description="\"first\", \"second\", etc.")
    CARDINAL = SpacyEnCoreWebEntityTypeInfo(label="CARDINAL", description="Numerals that do not fall under another type")

    @classmethod
    def get_by_label(cls, label):
        for item in cls:
            if item.value.label == label:
                return item
        raise ValueError(f"No entity type found with label: {label}")

    @classmethod
    def list_all(cls):
        return list(cls)