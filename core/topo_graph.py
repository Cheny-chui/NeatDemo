import gurobipy

TOPO_GRAPH = {
    'a': ['i'],
    'b': ['i'],
    'c': ['i', 'f'],
    'd': ['i', 'g'],
    'e': ['i', 'h'],
    'f': ['c', 'j'],
    'g': ['d', 'j'],
    'h': ['e', 'j'],
    'i': ['a', 'b', 'c', 'd', 'e', 'DROP'],
    'j': ['f', 'g', 'h', 'q', 'DROP'],
    'm': ['p'],
    'p': ['m', 'q', 'r'],
    'q': ['j', 'p', 'r'],
    'r': ['p', 'q'],
    'DROP': ['i', 'j'],
}


def get_topo_graph():
    return TOPO_GRAPH


# 获取边集
def get_topo_edge():
    result = gurobipy.tuplelist()
    for pre, Next in TOPO_GRAPH.items():
        for next in Next:
            result.append((pre, next))
    return result
