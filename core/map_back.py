from input.configuration_graph import get_configuration_flow


def map_addition_back(topo_graph: dict, cluster_i: tuple, cluster_j: tuple, p: str, q: str):
    result = set()
    for i in cluster_i:
        for j in cluster_j:
            if j in topo_graph[i]:
                result.add(tuple([i, j, p, q]))
                break  # 有一条边就行
    return result


def map_deletion_back(cluster_i: tuple, cluster_j: tuple, p: str, q: str):
    edge_flows = get_configuration_flow()
    original_edge = set()
    for i in cluster_i:
        for j in cluster_j:
            if (i, j, p, q) in edge_flows:
                original_edge.add(tuple([i, j, p, q]))
    return original_edge
