from abc import abstractmethod, ABC


class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text, length_ratio=None, sentence_ratio=None, words_count=None, sentence_count=None, score=False):
        raise NotImplementedError
