def map_addition_back(topo_graph: dict, cluster_i: tuple, cluster_j: tuple, p: str, q: str):
    """
        调用此函数后，需要存储 cluster_edge_to_original_edge: dict 以供 map_deletion_back 使用
    """
    result = list()
    for i in cluster_i:
        for j in cluster_j:
            if j in topo_graph[i]:
                result.append(tuple([i, j, p, q]))
                break  # 有一条边就行
    return result


def map_deletion_back(cluster_edge_to_original_edge: dict, cluster_i: tuple, cluster_j: tuple, p: str, q: str):
    original_edge = cluster_edge_to_original_edge[(cluster_i, cluster_j, p, q)]
    result = list()
    for edge in original_edge:
        result.append(tuple([edge[0], edge[1], p, q]))
    return result
