CONFIGURATION_GRAPH = {}

EDGE_FLOW = {}


def init_configuration_graph(graph: dict[str, list[str]], edge_flow: dict[tuple[str, str], set[tuple[str, str]]]):
    global CONFIGURATION_GRAPH, EDGE_FLOW
    # 重新初始化 配置图 和 此配置图上的流
    CONFIGURATION_GRAPH = graph
    EDGE_FLOW = edge_flow


def get_edge_flows(graph: dict[tuple[str, str], set[tuple[str, str]]]):
    result = set()
    for (i, j) in graph:
        for (p, q) in graph[i, j]:
            result.add(tuple([i, j, p, q]))
    return result


def get_configuration_graph():
    return CONFIGURATION_GRAPH


def get_configuration_flow():
    return EDGE_FLOW


def get_configuration_edge_flows():
    return get_edge_flows(CONFIGURATION_GRAPH)
