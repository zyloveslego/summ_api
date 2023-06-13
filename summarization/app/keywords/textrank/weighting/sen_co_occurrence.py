from .weighting import Weighting
from math import log10


class SentenceCoOccur(Weighting):
    def __init__(self, language):
        self.language = language
        
    def set_graph_weighted_edges(self, graph, token_dict, original_tokens):
        for sentence_1 in graph.nodes():
            for sentence_2 in graph.nodes():

                edge = (sentence_1, sentence_2)
                if sentence_1 != sentence_2 and not graph.has_edge(edge):
                    similarity = self._get_similarity(sentence_1, sentence_2)
                    if similarity != 0:
                        graph.add_edge(edge, similarity)

        # Handles the case in which all similarities are zero.
        # The resultant summary will consist of random sentences.
        if all(graph.edge_weight(edge) == 0 for edge in graph.edges()):
            self._create_valid_graph(graph)

    def _get_similarity(self, s1, s2):
        words_sentence_one = s1.split()
        words_sentence_two = s2.split()

        common_word_count = self._count_common_words(words_sentence_one, words_sentence_two)

        log_s1 = log10(len(words_sentence_one))
        log_s2 = log10(len(words_sentence_two))

        if log_s1 + log_s2 == 0:
            return 0

        return common_word_count / (log_s1 + log_s2)

    def _count_common_words(self, words_sentence_one, words_sentence_two):
        return len(set(words_sentence_one) & set(words_sentence_two))

    def _create_valid_graph(self, graph):
        nodes = graph.nodes()

        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i == j:
                    continue

                edge = (nodes[i], nodes[j])

                if graph.has_edge(edge):
                    graph.del_edge(edge)

                graph.add_edge(edge, 1)