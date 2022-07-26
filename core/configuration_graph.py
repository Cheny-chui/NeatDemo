import gurobipy

CONFIGURATION_GRAPH = {

}


def get_configuration_graph():
    return CONFIGURATION_GRAPH


# 获取边集
def get_configuration_edge():
    result = gurobipy.tuplelist()
    for pre, Next in CONFIGURATION_GRAPH.items():
        for next in Next:
            result.append((pre, next))
    return result


def add_edge(i: str, j: str):
    if i in CONFIGURATION_GRAPH and j not in CONFIGURATION_GRAPH[i]:
        CONFIGURATION_GRAPH[i].append(j)
    elif i not in CONFIGURATION_GRAPH:
        CONFIGURATION_GRAPH[i] = list()
        CONFIGURATION_GRAPH[i].append(j)


def del_edge(i: str, j: str):
    CONFIGURATION_GRAPH[i].remove(j)
