from .weighting import Weighting
from summarization.app.utils.tovec_service import ToVecService
from itertools import combinations as _combinations


def get_combinations(token_dict):
    words = list(token_dict.keys())
    for combo in _combinations(words, 5):
        yield combo


class W2V(Weighting):
    def __init__(self, language):
        self.language = language
        self.to_vec_service = ToVecService.set_default_by_language(language)

    # def set_graph_weighted_edges(self, graph, token_dict, original_tokens):
    #     combo_generator = get_combinations(token_dict)
    #     for word1, word2 in combo_generator:
    #         lemma_a = token_dict[word1].token
    #         lemma_b = token_dict[word2].token
    #         edge = (lemma_a, lemma_b)
    #         if graph.has_node(lemma_a) and graph.has_node(lemma_b) and not graph.has_edge(edge):
    #             weight = self.to_vec_service.word_similarity(word1, word2)
    #             if weight > 0:
    #                 graph.add_edge(edge)
    #                 graph.set_edge_properties(edge, weight=weight)

    def set_graph_weighted_edges(self, graph, token_dict, original_tokens):
        pair_weights = self.to_vec_service.pairwise_word_similarity(list(token_dict.keys()))
        combo_generator = get_combinations(token_dict)
        for word1, word2 in combo_generator:
            lemma_a = token_dict[word1].token
            lemma_b = token_dict[word2].token
            edge = (lemma_a, lemma_b)
            if graph.has_node(lemma_a) and graph.has_node(lemma_b) and not graph.has_edge(edge):
                if (word1, word2) in pair_weights:
                    weight = pair_weights[(word1, word2)]
                else:
                    weight = pair_weights[(word2, word1)]

                if weight > 0:
                    graph.add_edge(edge)
                    graph.set_edge_properties(edge, weight=weight)
