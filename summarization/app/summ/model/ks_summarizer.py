from math import log10

from summarization.app.summ.model.textrank_sentence.pagerank_weighted import pagerank_weighted_scipy as _pagerank
from summarization.app.summ.model.textrank_sentence.pagerank_weighted import pagerank_weighted_position_biased as _pagerank_position_biased
from summarization.app.summ.model.textrank_sentence.preprocessing.textcleaner import clean_text_by_sentences as _clean_text_by_sentences
from summarization.app.summ.model.textrank_sentence.preprocessing.textcleaner import clean_text_by_sentences_self_define as _clean_text_by_sentences_self_define
from summarization.app.summ.model.textrank_sentence.commons import build_graph as _build_graph
from summarization.app.summ.model.textrank_sentence.commons import remove_unreachable_nodes as _remove_unreachable_nodes
import math
from summarization.app.utils.tovec_service import ToVecService
from itertools import combinations
import nltk
from nltk.corpus import stopwords
import string
import statistics


def _wmd_metric(x, y, to_vec_service):
    return to_vec_service.wmd(x, y)


def _set_graph_edge_weights(graph):
    for sentence_1 in graph.nodes():
        for sentence_2 in graph.nodes():

            edge = (sentence_1, sentence_2)
            if sentence_1 != sentence_2 and not graph.has_edge(edge):
                similarity = _get_similarity(sentence_1, sentence_2)
                if similarity != 0:
                    graph.add_edge(edge, similarity)

    # Handles the case in which all similarities are zero.
    # The resultant summary will consist of random sentences.
    if all(graph.edge_weight(edge) == 0 for edge in graph.edges()):
        _create_valid_graph(graph)


def _pairwise_dist( sentences, to_vec_service):
    stopword_en = set(stopwords.words('english'))
    stopword_en = stopword_en.union(string.punctuation)

    dist_dct = {}
    iterator = combinations(range(len(sentences)), 2)
    dists = []
    for i, j in iterator:
        sen_1 = ' '.join(w for w in nltk.word_tokenize(sentences[i].text) if w not in stopword_en)
        sen_2 = ' '.join(w for w in nltk.word_tokenize(sentences[j].text) if w not in stopword_en)
        dist = _wmd_metric(sen_1, sen_2, to_vec_service)
        dist_dct[(sentences[i].token, sentences[j].token)] = dist
        dists.append(dist)

    dists.sort(reverse=True)
    dist_threshold = dists[:int(len(dists)*0.3)][-1]

    res = {}
    for key, val in dist_dct.items():
        if val >= dist_threshold:
            res[key] = val

    return res


def _set_graph_edge_weights_semantic(graph, sentences):
    to_vec_service = ToVecService.set_default_by_language("english")
    sen_dist_dct = _pairwise_dist(sentences, to_vec_service)

    similarity_scores = []
    for sentence_1 in graph.nodes():
        for sentence_2 in graph.nodes():

            edge = (sentence_1, sentence_2)
            if sentence_1 != sentence_2 and not graph.has_edge(edge):
                similarity = _get_similarity_semantic(sentence_1, sentence_2)
                if similarity != 0:
                    graph.add_edge(edge, similarity)
                    similarity_scores.append(similarity)
    avg_similarity = statistics.mean(similarity_scores)

    for sentence_1 in graph.nodes():
        for sentence_2 in graph.nodes():
            edge = (sentence_1, sentence_2)
            if sentence_1 != sentence_2 and ((sentence_1, sentence_2) in sen_dist_dct or (sentence_2, sentence_1) in sen_dist_dct):
                if graph.has_edge(edge):
                    adjusted_weight = avg_similarity + graph.edge_weight(edge)
                    graph.set_edge_properties(edge, wt=adjusted_weight)
                else:
                    graph.add_edge(edge, wt=avg_similarity)

    # Handles the case in which all similarities are zero.
    # The resultant summary will consist of random sentences.
    if all(graph.edge_weight(edge) == 0 for edge in graph.edges()):
        _create_valid_graph(graph)


def _get_similarity_semantic(s1, s2):

    words_sentence_one = s1.split()
    words_sentence_two = s2.split()

    common_word_count = _count_common_words(words_sentence_one, words_sentence_two)

    log_s1 = log10(len(words_sentence_one))
    log_s2 = log10(len(words_sentence_two))

    if log_s1 + log_s2 == 0:
        return 0

    return common_word_count / (log_s1 + log_s2)


def _create_valid_graph(graph):
    nodes = graph.nodes()

    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i == j:
                continue

            edge = (nodes[i], nodes[j])

            if graph.has_edge(edge):
                graph.del_edge(edge)

            graph.add_edge(edge, 1)


def _get_similarity(s1, s2):
    words_sentence_one = s1.split()
    words_sentence_two = s2.split()

    common_word_count = _count_common_words(words_sentence_one, words_sentence_two)

    log_s1 = log10(len(words_sentence_one))
    log_s2 = log10(len(words_sentence_two))

    if log_s1 + log_s2 == 0:
        return 0

    return common_word_count / (log_s1 + log_s2)


def _count_common_words(words_sentence_one, words_sentence_two):
    return len(set(words_sentence_one) & set(words_sentence_two))


def _format_results(extracted_sentences, split, score):
    if score:
        return [(sentence.text, sentence.score) for sentence in extracted_sentences]
    if split:
        return [sentence.text for sentence in extracted_sentences]
    return [sentence.text for sentence in extracted_sentences]


def _add_scores_to_sentences(sentences, scores):
    for sentence in sentences:
        # Adds the score to the object if it has one.
        if sentence.token in scores:
            sentence.score = scores[sentence.token]
        else:
            sentence.score = 0


def _get_sentences_with_word_count(sentences, words):
    """ Given a list of sentences, returns a list of sentences with a
    total word count similar to the word count provided.
    """
    word_count = 0
    selected_sentences = []
    # Loops until the word count is reached.
    for sentence in sentences:
        words_in_sentence = len(sentence.text.split())

        # Checks if the inclusion of the sentence gives a better approximation
        # to the word parameter.

        # constrain here for restrict condition
        # if abs(words - word_count - words_in_sentence) > abs(words - word_count):
        #     return selected_sentences

        selected_sentences.append(sentence)
        word_count += words_in_sentence

        # constrain here for loose condition
        if abs(words - word_count - words_in_sentence) > abs(words - word_count):
            return selected_sentences

    return selected_sentences


def _extract_most_important_sentences(sentences, ratio, words, sentence_count):
    sentences.sort(key=lambda s: s.score, reverse=True)

    # If no "words" option is selected, the number of sentences is
    # reduced by the provided ratio.
    if sentence_count:
        return sentences[:int(sentence_count)]

    if words is None:
        length = math.ceil(len(sentences) * ratio)
        return sentences[:int(length)]

    # Else, the ratio is ignored.
    else:
        return _get_sentences_with_word_count(sentences, words)


def summarize(text, ratio=0.2, sentence_count=None, words=None, language="english", split=False, scores=False, semantic_edge=False, position_biased=True):
    if not isinstance(text, str):
        raise ValueError("Text parameter must be a Unicode object (str)!")

    # Gets a list of processed sentences.
    sentences = _clean_text_by_sentences(text, language)

    # Creates the graph and calculates the similarity coefficient for every pair of nodes.
    graph = _build_graph([sentence.token for sentence in sentences])

    if semantic_edge:
        _set_graph_edge_weights_semantic(graph, sentences)
    else:
        _set_graph_edge_weights(graph)

    # Remove all nodes with all edges weights equal to zero.
    _remove_unreachable_nodes(graph)

    # PageRank cannot be run in an empty graph.
    if len(graph.nodes()) == 0:
        return [] if split else ""

    # Ranks the tokens using the PageRank algorithm. Returns dict of sentence -> score
    if not position_biased:
        pagerank_scores = _pagerank(graph)
    else:
        pagerank_scores = _pagerank_position_biased(graph, sentences)

    # Adds the summa scores to the sentence objects.
    _add_scores_to_sentences(sentences, pagerank_scores)

    # Extracts the most important sentences with the selected criterion.
    extracted_sentences = _extract_most_important_sentences(sentences, ratio, words, sentence_count)

    # Sorts the extracted sentences by apparition order in the original text.
    extracted_sentences.sort(key=lambda s: s.index)

    return _format_results(extracted_sentences, split, scores)


def sentence_rank(text, language="english"):
    # Gets a list of processed sentences.
    sentences = _clean_text_by_sentences_self_define(text, language)

    # Creates the graph and calculates the similarity coefficient for every pair of nodes.
    graph = _build_graph([sentence.token for sentence in sentences])
    _set_graph_edge_weights(graph)

    # Remove all nodes with all edges weights equal to zero.
    _remove_unreachable_nodes(graph)

    # PageRank cannot be run in an empty graph.
    if len(graph.nodes()) == 0:
        return []

    # Ranks the tokens using the PageRank algorithm. Returns dict of sentence -> score
    pagerank_scores = _pagerank(graph)

    # Adds the summa scores to the sentence objects.
    _add_scores_to_sentences(sentences, pagerank_scores)

    return sentences


def get_graph(text, language="english"):
    sentences = _clean_text_by_sentences(text, language)

    graph = _build_graph([sentence.token for sentence in sentences])
    _set_graph_edge_weights(graph)

    return graph
