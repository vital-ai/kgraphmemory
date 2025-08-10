from collections import OrderedDict
from typing import Union

from vital_ai_vitalsigns.model.VITAL_Edge import VITAL_Edge
from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node


class KGResultMatch:
    def __init__(self, score: float = 1.0):
        self.matches: OrderedDict[str, Union[VITAL_Node, VITAL_Edge]] = OrderedDict()
        self.score = score

    def add_match(self, key: str, value: Union[VITAL_Node, VITAL_Edge]):
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")
        if not isinstance(value, (VITAL_Node, VITAL_Edge)):
            raise TypeError("Value must be a Node or an Edge.")
        self.matches[key] = value

    def get_match(self, key: str) -> Union[VITAL_Node, VITAL_Edge, None]:
        # Retrieve a value by key from the ordered dictionary
        return self.matches.get(key)
