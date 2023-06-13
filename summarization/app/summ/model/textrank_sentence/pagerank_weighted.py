from scipy.sparse import csr_matrix
from scipy.linalg import eig
from numpy import empty as empty_matrix
import numpy as np

try:
    from numpy import VisibleDeprecationWarning
    import warnings

    warnings.filterwarnings("ignore", category=VisibleDeprecationWarning)
except ImportError:
    pass

CONVERGENCE_THRESHOLD = 0.0001


def pagerank_weighted(graph, initial_value=None, damping=0.85):
    """Calculates PageRank for an undirected graph"""
    if initial_value == None: initial_value = 1.0 / len(graph.nodes())
    scores = dict.fromkeys(graph.nodes(), initial_value)

    iteration_quantity = 0
    for iteration_number in range(100):
        iteration_quantity += 1
        convergence_achieved = 0
        for i in graph.nodes():
            rank = 1 - damping
            for j in graph.neighbors(i):
                neighbors_sum = sum(graph.edge_weight((j, k)) for k in graph.neighbors(j))
                rank += damping * scores[j] * graph.edge_weight((j, i)) / neighbors_sum

            if abs(scores[i] - rank) <= CONVERGENCE_THRESHOLD:
                convergence_achieved += 1

            scores[i] = rank

        if convergence_achieved == len(graph.nodes()):
            break

    return scores


def pagerank_weighted_scipy(graph, damping=0.85):
    adjacency_matrix = build_adjacency_matrix(graph)
    probability_matrix = build_probability_matrix(graph)

    pagerank_matrix = damping * adjacency_matrix.todense() + (1 - damping) * probability_matrix
    vals, vecs = eig(pagerank_matrix, left=True, right=False)
    return process_results(graph, vecs)


def pagerank_weighted_position_biased(graph, sentence_list, damping=0.85):
    """Get dictionary of `graph` nodes and its ranks.

    Parameters
    ----------
    graph : :class:`~gensim.summarization.graph.Graph`
        Given graph.
    token_list: for biased page rank.

    damping : float
        Damping parameter, optional

    Returns
    -------
    dict
        Nodes of `graph` as keys, its ranks as values.

    """
    adjacency_matrix = build_adjacency_matrix(graph)
    sentence_position_dict = sentence_postion_weight(sentence_list)
    probability_matrix = build_probability_matrix_position_biased(graph, sentence_position_dict)

    pagerank_matrix = damping * adjacency_matrix.todense() + (1 - damping) * probability_matrix

    vals, vecs = eig(pagerank_matrix, left=True, right=False)

    # Because pagerank_matrix is positive, vec is always real (i.e. not complex)
    return process_results(graph, vecs)


def build_probability_matrix_position_biased(graph, sentence_position_dict):
    """Get square matrix of shape (n, n), where n is number of nodes of the
    given `graph`.

    Parameters
    ----------
    graph : :class:`~gensim.summarization.graph.Graph`
        Given graph.

    Returns
    -------
    numpy.ndarray, shape = [n, n]
        Eigenvector of matrix `a`, n is number of nodes of `graph`.

    """
    total_score = 0
    for sentence in sentence_position_dict:
        if sentence in graph.nodes():
            total_score = total_score + sentence_position_dict[sentence]

    # normalize and init
    probability_vec = []
    for node in graph.nodes():
        normalized_score = sentence_position_dict[node] / total_score
        probability_vec.append(normalized_score)
    dimension = len(graph.nodes())

    _biased_probability_matrix = []
    for i in range(dimension):
        _biased_probability_matrix.append(probability_vec)

    _biased_probability_matrix = np.array(_biased_probability_matrix)
    return _biased_probability_matrix


def build_adjacency_matrix(graph):
    row = []
    col = []
    data = []
    nodes = graph.nodes()
    length = len(nodes)

    for i in range(length):
        current_node = nodes[i]
        neighbors_sum = sum(graph.edge_weight((current_node, neighbor)) for neighbor in graph.neighbors(current_node))
        for j in range(length):
            edge_weight = float(graph.edge_weight((current_node, nodes[j])))
            if i != j and edge_weight != 0:
                row.append(i)
                col.append(j)
                data.append(edge_weight / neighbors_sum)

    return csr_matrix((data, (row, col)), shape=(length, length))


def build_probability_matrix(graph):
    dimension = len(graph.nodes())
    matrix = empty_matrix((dimension, dimension))

    probability = 1 / float(dimension)
    matrix.fill(probability)

    return matrix


def process_results(graph, vecs):
    scores = {}
    for i, node in enumerate(graph.nodes()):
        scores[node] = abs(vecs[i][0])

    return scores


def sentence_postion_weight(sentence_list):
    sentence_dict = {}
    for idx, sentence in enumerate(sentence_list):
        sentence_dict[sentence.token] = 1.0 / float(idx+5)

    return sentence_dict