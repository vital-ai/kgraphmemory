from kgraphmemory.kgresult_match import KGResultMatch


class KGResultList(list[KGResultMatch]):
    def add_result(self, result: KGResultMatch):
        if not isinstance(result, KGResultMatch):
            raise TypeError("Result must be a KGResultMatch instance.")
        self.append(result)

    def get_results(self):
        # Return the entire list of KGResultMatch objects
        return self
