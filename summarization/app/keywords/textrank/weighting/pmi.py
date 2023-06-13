from itertools import combinations as _combinations
from queue import Queue
from six.moves import xrange
from .weighting import Weighting
import math


class PMI(Weighting):
    def __init__(self, language):
        self.WINDOW_SIZE = 4
        if language == "chinese":
            self.WINDOW_SIZE = 5
        self.edges_dct = dict()
        self.word_dct = dict()
        self.num_windows = 0

    def set_graph_weighted_edges(self, graph, token_dict, original_tokens):
        self.num_windows = len(original_tokens)//self.WINDOW_SIZE + 1
        self._co_occurrence(graph, token_dict, original_tokens)
        self._set_pmi_weight(graph)

    def _set_pmi_weight(self, graph):
        for edge in self.edges_dct:
            lemma_a, lemma_b = edge
            p_ij = self.edges_dct[edge]/self.num_windows
            p_i = self.word_dct[lemma_a]/self.num_windows
            p_j = self.word_dct[lemma_b]/self.num_windows
            _w = max(math.log(p_ij / (p_i * p_j), 2), 0.01)
            if graph.has_node(lemma_a) and graph.has_node(lemma_b) and graph.has_edge(edge):
                graph.set_edge_properties(edge, weight=_w)

    def _co_occurrence(self, graph, token_dict, original_tokens):
        """Updates given `graph` by setting edges between nodes if they exists in `tokens` and `graph`.
        Words are taken from `split_text` with window size :const:`~gensim.parsing.keywords.WINDOW_SIZE`.
        Parameters
        ----------
        graph : :class:~gensim.summarization.graph.Graph
            Given graph.
        token_dict : dict
            Original units (words) as keys and processed units (tokens) as values.
        original_tokens : list of str
            Splitted text.
        """
        self._process_first_window(graph, token_dict, original_tokens)
        self._process_text(graph, token_dict, original_tokens)

    def _process_first_window(self, graph, token_dict, original_tokens):
        """Sets an edges between nodes taken from first :const:`~gensim.parsing.keywords.WINDOW_SIZE`
        words of `split_text` if they exist in `tokens` and `graph`, inplace.
        Parameters
        ----------
        graph : :class:~gensim.summarization.graph.Graph
            Given graph.
        token_dict : dict
            Original units (words) as keys and processed units (tokens) as values.
        original_tokens : list of str
            Splitted text.
        """
        first_window = self._get_first_window(original_tokens)
        for word_a, word_b in _combinations(first_window, 2):

            if word_a in token_dict:
                lemma = token_dict[word_a].token
                self.word_dct[lemma] = self.word_dct.get(lemma, 0) + 1

            self._set_graph_edge(graph, token_dict, word_a, word_b)

    def _process_text(self, graph, token_dict, original_tokens):
        """Process `split_text` by updating given `graph` with new edges between nodes
        if they exists in `tokens` and `graph`.
        Words are taken from `split_text` with window size :const:`~gensim.parsing.keywords.WINDOW_SIZE`.
        Parameters
        ----------
        graph : :class:`~gensim.summarization.graph.Graph`
            Given graph.
        token_dict : dict
            Original units (words) as keys and processed units (tokens) as values.
        original_tokens : list of str
            Splitted text.
        """
        queue = self._init_queue(original_tokens)
        for i in xrange(self.WINDOW_SIZE, len(original_tokens)):
            word = original_tokens[i]
            self._process_word(graph, token_dict, queue, word)
            self._update_queue(queue, word)

    def _get_first_window(self, original_tokens):
        """Get first :const:`~gensim.parsing.keywords.WINDOW_SIZE` tokens from given `split_text`.
        Parameters
        ----------
        original_tokens : list of str
            Splitted text.
        Returns
        -------
        list of str
            First :const:`~gensim.parsing.keywords.WINDOW_SIZE` tokens.
        """
        return original_tokens[:self.WINDOW_SIZE]

    def _set_graph_edge(self, graph, tokens, word_a, word_b):
        """Sets an edge between nodes named word_a and word_b if they exists in `tokens` and `graph`, inplace.
        Parameters
        ----------
        graph : :class:~gensim.summarization.graph.Graph
            Given graph.
        tokens : dict
            Original units (words) as keys and processed units (tokens) as values.
        word_a : str
            First word, name of first node.
        word_b : str
            Second word, name of second node.
        """
        if word_a in tokens and word_b in tokens:
            lemma_a = tokens[word_a].token
            lemma_b = tokens[word_b].token

            edge = (lemma_a, lemma_b)
            reverse_edge = (lemma_b, lemma_a)

            if edge in self.edges_dct or reverse_edge in self.edges_dct:
                if edge in self.edges_dct:
                    self.edges_dct[edge] = self.edges_dct.get(edge, 0) + 1
                else:
                    self.edges_dct[reverse_edge] = self.edges_dct.get(reverse_edge, 0) + 1
            else:
                self.edges_dct[edge] = self.edges_dct.get(edge, 0) + 1

            self.word_dct[lemma_b] = self.word_dct.get(lemma_b, 0) + 1

            if graph.has_node(lemma_a) and graph.has_node(lemma_b) and not graph.has_edge(edge):
                graph.add_edge(edge)

            # add weight
            # if graph.has_node(lemma_a) and graph.has_node(lemma_b):
            #     if not graph.has_edge(edge):
            #         graph.add_edge(edge)
            #     else:
            #         weight = graph.get_edge_properties(edge)["weight"]
            #         graph.set_edge_properties(edge, weight=weight+1)

    def _init_queue(self, original_tokens):
        """Initialize queue by first words from `split_text`.
        Parameters
        ----------
        original_tokens : list of str
            Splitted text.
        Returns
        -------
        Queue
            Initialized queue.
        """
        queue = Queue()
        first_window = self._get_first_window(original_tokens)
        for word in first_window[1:]:
            queue.put(word)
        return queue

    def _process_word(self, graph, tokens, queue, word):
        """Sets edge between `word` and each element in queue in `graph` if such nodes
        exist in `tokens` and `graph`.
        Parameters
        ----------
        graph : :class:`~gensim.summarization.graph.Graph`
            Given graph.
        tokens : dict
            Original units (words) as keys and processed units (tokens) as values.
        queue : Queue
            Given queue.
        word : str
            Word, possible `node` in graph and item in `tokens`.
        """
        if word in tokens:
            lemma = tokens[word].token
            self.word_dct[lemma] = self.word_dct.get(lemma, 0) + 1

        for word_to_compare in self._queue_iterator(queue):
            self._set_graph_edge(graph, tokens, word, word_to_compare)

    def _update_queue(self, queue, word):
        """Updates given `queue` (removes last item and puts `word`).
        Parameters
        ----------
        queue : Queue
            Given queue.
        word : str
            Word to be added to queue.
        """
        queue.get()
        queue.put(word)
        assert queue.qsize() == (self.WINDOW_SIZE - 1)

    def _queue_iterator(self, queue):
        """Represents iterator of the given queue.
        Parameters
        ----------
        queue : Queue
            Given queue.
        Yields
        ------
        str
            Current item of queue.
        """
        iterations = queue.qsize()
        for i in range(iterations):
            var = queue.get()
            yield var
            queue.put(var)