from abc import ABC, abstractmethod


class Weighting(ABC):
    @abstractmethod
    def set_graph_weighted_edges(self, graph, token_dict, original_tokens):
        raise NotImplementedError
