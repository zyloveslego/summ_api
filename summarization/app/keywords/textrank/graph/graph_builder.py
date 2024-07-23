from .graph import Graph


def _add_nodes(graph, nodes):
    for item in nodes:
        if not graph.has_node(item):
            graph.add_node(item)


def _remove_unreachable_nodes(graph):
    """Removes unreachable nodes (nodes with no edges), inplace.
    """
    for node in graph.nodes():
        if sum(graph.edge_weight((node, other)) for other in graph.neighbors(node)) == 0:
            graph.del_node(node)


# def build_word_graph(token_dict, tag_filtered_tokens, original_tokens, weighting):
#     graph = Graph()
#     _add_nodes(graph, tag_filtered_tokens)
#     weighting.set_graph_weighted_edges(graph=graph, token_dict=token_dict, original_tokens=original_tokens)
#     _remove_unreachable_nodes(graph)
#     return graph

def build_word_graph(token_dict, tag_filtered_tokens, original_tokens, weighting):
    graph = Graph()
    _add_nodes(graph, tag_filtered_tokens)
    weighting.set_graph_weighted_edges(graph=graph, token_dict=token_dict, original_tokens=original_tokens)
    _remove_unreachable_nodes(graph)
    return graph


def build_sentence_graph(token_dict, token_list, weighting):
    graph = Graph()
    _add_nodes(graph, [s.token for s in token_list])
    weighting.set_graph_weighted_edges(graph=graph, token_dict=token_dict, original_tokens=None)
    _remove_unreachable_nodes(graph)
    return graph
