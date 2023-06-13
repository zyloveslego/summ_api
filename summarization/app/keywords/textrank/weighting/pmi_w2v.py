from .weighting import Weighting
from .pmi import PMI
from itertools import combinations as _combinations
from summarization.app.utils.tovec_service import ToVecService
import summarization.app.definitions as definitions


def get_combinations(token_dict):
    words = list(token_dict.keys())
    for combo in _combinations(words, 2):
        yield combo


class PMI_W2V(Weighting):
    def __init__(self, language):
        self.pmi = PMI(language)
        self.to_vec_service = ToVecService.set_default_by_language(language)

        # threshold set by experience, can be changed in definition file
        if language == "english":
            self.threshold = definitions.W2V_EN_MODEL_THRESHOLD
        else:
            self.threshold = definitions.W2V_CN_MODEL_THRESHOLD

    def set_graph_weighted_edges(self, graph, token_dict, original_tokens):
        self.pmi.set_graph_weighted_edges(graph, token_dict, original_tokens)
        self.set_w2v_edge(graph, token_dict)

    # def set_w2v_edge(self, graph, token_dict):
    #     combo_generator = get_combinations(token_dict)
    #     for word1, word2 in combo_generator:
    #         lemma_a = token_dict[word1].token
    #         lemma_b = token_dict[word2].token
    #         edge = (lemma_a, lemma_b)
    #         if graph.has_node(lemma_a) and graph.has_node(lemma_b):
    #             weight = self.to_vec_service.word_similarity(word1, word2)
    #             # print(word1, word2, weight)
    #             if weight > self.threshold:
    #                 if not graph.has_edge(edge):
    #                     graph.add_edge(edge, wt=weight)

    def set_w2v_edge(self, graph, token_dict):
        pair_weights = self.to_vec_service.pairwise_word_similarity(list(token_dict.keys()))
        combo_generator = get_combinations(token_dict)
        for word1, word2 in combo_generator:
            lemma_a = token_dict[word1].token
            lemma_b = token_dict[word2].token
            edge = (lemma_a, lemma_b)
            if graph.has_node(lemma_a) and graph.has_node(lemma_b):
                if (word1, word2) in pair_weights:
                    weight = pair_weights[(word1, word2)]
                else:
                    weight = pair_weights[(word2, word1)]

                # print(word1, word2, weight)
                if weight > self.threshold:
                    if not graph.has_edge(edge):
                        graph.add_edge(edge, wt=weight)
