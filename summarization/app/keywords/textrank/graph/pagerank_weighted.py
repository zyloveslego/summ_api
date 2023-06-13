import numpy
from numpy import empty as empty_matrix
from scipy.linalg import eig
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigs
from six.moves import xrange
from summarization.app.topic_modeling.demo import llda_topic_word
from summarization.app.keywords.tf_idf.tf_idf_keyword import TFIDFKeywords
from summarization.app.keywords.textrank.graph.token_position import *

WITHOUT_BIAS = 0
WITH_POSITION_BIAS = 1
WITH_TOPIC_POSITION_BIAS = 2
WITH_TFIDF_POSITION_BIAS = 3


def get_page_rank_score(graph, token_list, position_topic_biased, article_structure):
    if position_topic_biased == WITHOUT_BIAS or article_structure == UNIFORM:
        return pagerank_weighted(graph)

    if position_topic_biased == WITH_POSITION_BIAS:
        pagerank_scores = pagerank_weighted_position_biased(graph, token_list, article_structure)
    elif position_topic_biased == WITH_TOPIC_POSITION_BIAS:
        pagerank_scores = pagerank_weighted_topic_position_biased(graph, token_list, article_structure)
    elif position_topic_biased == WITH_TFIDF_POSITION_BIAS:
        pagerank_scores = pagerank_weighted_topic_position_biased(graph, token_list, article_structure)
    else:
        pagerank_scores = pagerank_weighted(graph)
    return pagerank_scores


def my_get_page_rank_score(graph, token_list, position_topic_biased, article_structure, text):
    if position_topic_biased == WITHOUT_BIAS or article_structure == UNIFORM:
        return pagerank_weighted(graph)

    if position_topic_biased == WITH_POSITION_BIAS:
        # pagerank_scores = pagerank_weighted_position_biased(graph, token_list, article_structure)
        pagerank_scores = my_pagerank_weighted_position_biased(graph, token_list, article_structure, text)
    elif position_topic_biased == WITH_TOPIC_POSITION_BIAS:
        pagerank_scores = pagerank_weighted_topic_position_biased(graph, token_list, article_structure)
    elif position_topic_biased == WITH_TFIDF_POSITION_BIAS:
        pagerank_scores = pagerank_weighted_topic_position_biased(graph, token_list, article_structure)
    else:
        pagerank_scores = pagerank_weighted(graph)
    return pagerank_scores


def pagerank_weighted(graph, damping=0.85):
    """Get dictionary of `graph` nodes and its ranks.

    Parameters
    ----------
    graph : :class:`~gensim.summarization.graph.Graph`
        Given graph.
    damping : float
        Damping parameter, optional

    Returns
    -------
    dict
        Nodes of `graph` as keys, its ranks as values.

    """
    adjacency_matrix = build_adjacency_matrix(graph)
    probability_matrix = build_probability_matrix(graph)

    pagerank_matrix = damping * adjacency_matrix.todense() + (1 - damping) * probability_matrix

    vec = principal_eigenvector(pagerank_matrix.T)

    # Because pagerank_matrix is positive, vec is always real (i.e. not complex)
    return process_results(graph, vec.real)


def pagerank_weighted_position_biased(graph, token_list, article_structure, damping=0.85):
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
    token_position_dict = get_token_position_weight(token_list, article_structure)
    probability_matrix = build_probability_matrix_position_biased(graph, token_position_dict)

    pagerank_matrix = damping * adjacency_matrix.todense() + (1 - damping) * probability_matrix

    vec = principal_eigenvector(pagerank_matrix.T)

    # Because pagerank_matrix is positive, vec is always real (i.e. not complex)
    return process_results(graph, vec.real)


def my_pagerank_weighted_position_biased(graph, token_list, article_structure, text, damping=0.85):
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

    # 这里修改
    # token_position_dict = get_token_position_weight(token_list, article_structure)

    # mine
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    article_structure = 4

    token_position_dict = my_token_position_weight(token_list, article_structure, model, text)
    # ---

    probability_matrix = build_probability_matrix_position_biased(graph, token_position_dict)

    pagerank_matrix = damping * adjacency_matrix.todense() + (1 - damping) * probability_matrix

    vec = principal_eigenvector(pagerank_matrix.T)

    # Because pagerank_matrix is positive, vec is always real (i.e. not complex)
    return process_results(graph, vec.real)


def pagerank_weighted_topic_position_biased(graph, token_list, article_structure, damping=0.85):
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
    adjacency_matrix = build_topic_adjacency_matrix(graph, token_list)
    token_position_dict = get_token_position_weight(token_list, article_structure)
    probability_matrix = build_probability_matrix_position_biased(graph, token_position_dict)

    pagerank_matrix = damping * adjacency_matrix.todense() + (1 - damping) * probability_matrix

    vec = principal_eigenvector(pagerank_matrix.T)

    # Because pagerank_matrix is positive, vec is always real (i.e. not complex)
    return process_results(graph, vec.real)


def pagerank_weighted_tfidf_position_biased(graph, token_list, article_structure, damping=0.85):
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
    adjacency_matrix = build_tfidf_adjacency_matrix(graph, token_list)
    token_position_dict = get_token_position_weight(token_list, article_structure=article_structure)
    probability_matrix = build_probability_matrix_position_biased(graph, token_position_dict)

    pagerank_matrix = damping * adjacency_matrix.todense() + (1 - damping) * probability_matrix

    vec = principal_eigenvector(pagerank_matrix.T)

    # Because pagerank_matrix is positive, vec is always real (i.e. not complex)
    return process_results(graph, vec.real)


def build_adjacency_matrix(graph):
    """Get matrix representation of given `graph`.

    Parameters
    ----------
    graph : :class:`~gensim.summarization.graph.Graph`
        Given graph.

    Returns
    -------
    :class:`scipy.sparse.csr_matrix`, shape = [n, n]
        Adjacency matrix of given `graph`, n is number of nodes.

    """
    row = []
    col = []
    data = []
    nodes = graph.nodes()
    length = len(nodes)

    for i in xrange(length):
        current_node = nodes[i]
        neighbors_sum = sum(graph.edge_weight((current_node, neighbor)) for neighbor in graph.neighbors(current_node))
        for j in xrange(length):
            edge_weight = float(graph.edge_weight((current_node, nodes[j])))
            if i != j and edge_weight != 0.0:
                row.append(i)
                col.append(j)
                data.append(edge_weight / neighbors_sum)

    return csr_matrix((data, (row, col)), shape=(length, length))


def build_tfidf_adjacency_matrix(graph, token_list):
    """Get matrix representation of given `graph`.

    Parameters
    ----------
    graph : :class:`~gensim.summarization.graph.Graph`
        Given graph.

    Returns
    -------
    :class:`scipy.sparse.csr_matrix`, shape = [n, n]
        Adjacency matrix of given `graph`, n is number of nodes.

    """
    # get tf idf
    tf_idf_kw = TFIDFKeywords(cv_model_path="/Users/hao/Code/Summarization/app/keywords/tf_idf/cv.pkl",
                              tf_idf_path="/Users/hao/Code/Summarization/app/keywords/tf_idf/tfidf_transformer.pkl")
    tokens = [unit.token for unit in token_list]
    tf_idf_keywords = tf_idf_kw.extract(" ".join(tokens))

    row = []
    col = []
    data = []
    nodes = graph.nodes()
    length = len(nodes)

    for i in xrange(length):
        current_node = nodes[i]

        weights = {}
        for neighbor in graph.neighbors(current_node):
            # edge weight
            edge_weight = graph.edge_weight((current_node, neighbor))

            score = 0
            for word in neighbor.split(" "):
                if word in tf_idf_keywords:
                    score += tf_idf_keywords[word]

            weights[(current_node, neighbor)] = edge_weight * score

        # rank
        neighbors_sum = sum([score for (current_node, neighbor), score in weights.items()])

        for j in xrange(length):
            if (current_node, nodes[j]) not in weights:
                score = 0
            else:
                score = weights[(current_node, nodes[j])]
            edge_weight = float(score)
            if i != j and edge_weight != 0.0:
                row.append(i)
                col.append(j)
                data.append(edge_weight / neighbors_sum)

    return csr_matrix((data, (row, col)), shape=(length, length))


def build_topic_adjacency_matrix(graph, token_list):
    """Get matrix representation of given `graph`.

    Parameters
    ----------
    graph : :class:`~gensim.summarization.graph.Graph`
        Given graph.

    Returns
    -------
    :class:`scipy.sparse.csr_matrix`, shape = [n, n]
        Adjacency matrix of given `graph`, n is number of nodes.

    """
    tokens = [unit.token for unit in token_list]
    topic, word_topic = llda_topic_word(tokens)
    row = []
    col = []
    data = []
    nodes = graph.nodes()
    length = len(nodes)

    for i in xrange(length):
        current_node = nodes[i]

        weight_list = []
        for neighbor in graph.neighbors(current_node):
            # edge weight
            edge_weight = graph.edge_weight((current_node, neighbor))

            score = 0
            for word in neighbor.split(" "):
                if word in word_topic:
                    score += word_topic[word]

            weight_list.append(((current_node, neighbor), edge_weight, score))

        # remove 0, some word may not present in llda,
        # in this case we assign the smallest score to the word rather than 0.
        weight_list = sorted(weight_list, key=lambda x: x[2])
        if weight_list[0][2] == 0:
            second_smallest = weight_list[-1][2]
            # for x in weight_list:
            #     if weight_list[0][2] < x[2]:
            #         second_smallest = x[2]
            #         break
            if second_smallest == 0:
                for idx in range(len(weight_list)):
                    (current_node, neighbor), edge_weight, score = weight_list[idx]
                    weight_list[idx] = (current_node, neighbor), edge_weight, 1
            else:
                for idx in range(len(weight_list)):
                    (current_node, neighbor), edge_weight, score = weight_list[idx]
                    if score == 0:
                        weight_list[idx] = (current_node, neighbor), edge_weight, second_smallest

        weight_list = sorted(weight_list, key=lambda x: x[2])
        # score to rank
        rank_count = {}
        rank_list = []
        prev_score, prev_rank = -1, 0
        for (current_node, neighbor), edge_weight, score in weight_list:
            if score > prev_score:
                rank_list.append(((current_node, neighbor), edge_weight, prev_rank + 1))
                prev_rank = prev_rank + 1
                prev_score = score
            else:
                rank_list.append(((current_node, neighbor), edge_weight, prev_rank))
            rank_count[prev_rank] = rank_count.get(prev_rank, 0) + 1

        # rank
        unit_socre = 1 / sum([key * val for key, val in rank_count.items()])

        score_list = {}
        neighbors_sum = 0
        for (current_node, neighbor), edge_weight, rank in rank_list:
            neighbors_sum += edge_weight * rank * unit_socre
            score_list[(current_node, neighbor)] = neighbors_sum

        for j in xrange(length):
            if (current_node, nodes[j]) not in score_list:
                score = 0
            else:
                score = score_list[(current_node, nodes[j])]
            edge_weight = float(score)
            if i != j and edge_weight != 0.0:
                row.append(i)
                col.append(j)
                data.append(edge_weight / neighbors_sum)

    return csr_matrix((data, (row, col)), shape=(length, length))


def build_probability_matrix(graph):
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
    dimension = len(graph.nodes())
    matrix = empty_matrix((dimension, dimension))

    probability = 1.0 / float(dimension)
    matrix.fill(probability)

    return matrix


def build_probability_matrix_position_biased(graph, token_position_dict):
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
    filtered_token_dict = {}
    for token in token_position_dict:
        if token in graph.nodes():
            total_score = total_score + token_position_dict[token]
            filtered_token_dict[token] = token_position_dict[token]

    # normalize and init
    probability_vec = []
    for node in graph.nodes():
        normalized_score = filtered_token_dict[node] / total_score
        probability_vec.append(normalized_score)
    dimension = len(graph.nodes())

    _biased_probability_matrix = []
    for i in range(dimension):
        _biased_probability_matrix.append(probability_vec)

    _biased_probability_matrix = numpy.array(_biased_probability_matrix)
    return _biased_probability_matrix


def principal_eigenvector(a):
    """Get eigenvector of square matrix `a`.

    Parameters
    ----------
    a : numpy.ndarray, shape = [n, n]
        Given matrix.

    Returns
    -------
    numpy.ndarray, shape = [n, ]
        Eigenvector of matrix `a`.

    """
    # Note that we prefer to use `eigs` even for dense matrix
    # because we need only one eigenvector. See #441, #438 for discussion.

    # But it doesn't work for dim A < 3, so we just handle this special case
    if len(a) < 3:
        vals, vecs = eig(a)
        ind = numpy.abs(vals).argmax()
        return vecs[:, ind]
    else:
        vals, vecs = eigs(a, k=1)
        return vecs[:, 0]


def process_results(graph, vec):
    """Get `graph` nodes and corresponding absolute values of provided eigenvector.
    This function is helper for :func:`~gensim.summarization.pagerank_weighted.pagerank_weighted`

    Parameters
    ----------
    graph : :class:`~gensim.summarization.graph.Graph`
        Given graph.
    vec : numpy.ndarray, shape = [n, ]
        Given eigenvector, n is number of nodes of `graph`.

    Returns
    -------
    dict
        Graph nodes as keys, corresponding elements of eigenvector as values.

    """
    scores = {}
    for i, node in enumerate(graph.nodes()):
        scores[node] = abs(vec[i])

    return scores
