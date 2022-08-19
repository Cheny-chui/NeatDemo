from input.topo_graph import get_topo_graph


def map_addition_back(cluster_i: tuple, cluster_j: tuple, p: str, q: str):
    result = set()
    topo_graph = get_topo_graph()
    for i in cluster_i:
        for j in cluster_j:
            if j in topo_graph[i]:
                result.add(tuple([i, j, p, q]))
                break  # 有一条边就行
    return result


def map_deletion_back(cluster_i: tuple, cluster_j: tuple, p: str, q: str):
    # TODO 如何得到压缩边对应的原边
    return
