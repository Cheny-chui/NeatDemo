CONFIGURATION_GRAPH: dict[str, set[str]] = {}


def init_configuration_graph(graph: dict[str, set[str]]):
    global CONFIGURATION_GRAPH
    # 重新初始化 配置图
    CONFIGURATION_GRAPH = graph


def get_configuration_graph():
    return CONFIGURATION_GRAPH
