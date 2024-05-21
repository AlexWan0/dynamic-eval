from graphviz import Digraph


def _add_edges(graph, node, parent=None, counter=[0]):
    node_id = str(counter[0])
    counter[0] += 1

    if parent is not None:
        graph.edge(node_id, parent)

    if isinstance(node[1], list):
        graph.node(node_id, node[0])
        for child in node[1]:
            _add_edges(graph, child, node_id, counter)
    else:
        graph.node(node_id, str(node[1]))

def make_graphviz(tree_vals):
    graph = Digraph()
    graph.attr(rankdir='BT')
    _add_edges(graph, tree_vals)
    return graph
