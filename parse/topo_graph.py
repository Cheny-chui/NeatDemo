import gurobipy

TOPO_GRAPH = {}


# 输入 拓扑图
def init_topo_graph(graph: dict[str, set[str]]):
    global TOPO_GRAPH
    TOPO_GRAPH = graph
    return


def get_topo_graph():
    return TOPO_GRAPH

