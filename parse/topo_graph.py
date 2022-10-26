import gurobipy

TOPO_GRAPH = {}


# 输入 拓扑图
def init_topo_graph(graph: dict[str, set[str]]):
    # 一定要添加一个 DROP 节点 供isolation使用
    graph['drop'] = set()
    global TOPO_GRAPH
    TOPO_GRAPH = graph
    return


def get_topo_graph():
    return TOPO_GRAPH


# 添加DROP节点
def add_drop(i, j):
    if 'drop' not in TOPO_GRAPH:
        TOPO_GRAPH['drop'] = list()
    if i not in TOPO_GRAPH['drop']:
        TOPO_GRAPH['drop'].append(i)
        TOPO_GRAPH[i].append('drop')
    if j not in TOPO_GRAPH['drop']:
        TOPO_GRAPH['drop'].append(j)
        TOPO_GRAPH[j].append('drop')
