CONFIGURATION_GRAPH: dict[tuple[str, str], set[float]] = {}


def init_configuration_graph(graph: dict[tuple[str, str], set[float]]):
    global CONFIGURATION_GRAPH
    # 重新初始化 配置图
    CONFIGURATION_GRAPH = graph


def get_configuration_graph():
    return CONFIGURATION_GRAPH
