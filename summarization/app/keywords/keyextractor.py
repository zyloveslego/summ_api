from abc import ABC, abstractmethod


class KeyExtractor(ABC):
    @abstractmethod
    def _generate_candidate(self, text):
        raise NotImplementedError

    @abstractmethod
    def extract(self, text, ratio=0.2, words=None, split=False, scores=False):
        raise NotImplementedError

    @abstractmethod
    def _post_processing(self, text, token_dict, graph, pagerank_scores, ratio, words):
        raise NotImplementedError
