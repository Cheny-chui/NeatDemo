TEST_POLICY = {
    ('Host_A', 'Host_B'): (2, -1),
}

TEST_TOPO = {
    'Host_A': ['ER_1', 'ER_2'],
    'Host_B': ['ER_3', 'ER_4'],
    'ER_1': ['Host_A', 'FW_1', 'FW_2'],
    'ER_2': ['Host_A', 'FW_2'],
    'ER_3': ['Host_B', 'FW_3', 'FW_4'],
    'ER_4': ['Host_B', 'FW_3'],
    'FW_1': ['ER_1', 'CR_1'],
    'FW_2': ['ER_1', 'ER_2', 'CR_1'],
    'FW_3': ['ER_3', 'ER_4', 'CR_1'],
    'FW_4': ['ER_3', 'CR_1'],
    'CR_1': ['FW_1', 'FW_2', 'FW_3', 'FW_4'],
}

TEST_CONFIGURATION = {
    'Host_A': ['ER_2'],
    'Host_B': [],
    'ER_2': ['FW_2'],
    'ER_3': ['Host_B'],
    'ER_4': ['Host_B'],
    'FW_2': ['CR_1'],
    'FW_3': ['ER_3', 'ER_4'],
    'FW_4': ['ER_3'],
    'CR_1': ['FW_3', 'FW_4'],
}


# 每个node的id 第一个下划线之前为 label
def get_label(node_id: str):
    label = node_id.split('_')[0]
    return label


# 本来应该要对Topo图进行标记，但由于不与Configuration重合的Topo图本来就不进行压缩，因此只需要标记Configuration
def get_uncompressed_node(policy_graph: dict, configuration_graph: dict, topo_graph: dict):
    uncompressed_node = set()
    for policy in policy_graph:
        if policy_graph[policy][0] > 1:
            start = policy[0]
            end = policy[1]
            # start's child
            for child in configuration_graph[start]:
                uncompressed_node.add(child)
            # end's father
            for neighbor in topo_graph[end]:
                if neighbor not in configuration_graph[end]:
                    uncompressed_node.add(neighbor)
    return uncompressed_node


def verify_bisimulation(graph: dict, node1: str, node2: str):
    if get_label(node1) != get_label(node2):
        return False
    if node1 == node2:
        return True
    flag = False
    # 对于所有的child1
    for child1 in graph[node1]:
        # 存在一个child2
        for child2 in graph[node2]:
            flag = verify_bisimulation(graph, child1, child2)
            if flag:
                break
    if not flag:
        return False
    flag = False
    # 对于所有的child2
    for child2 in graph[node2]:
        # 存在一个child1
        for child1 in graph[node1]:
            flag = verify_bisimulation(graph, child1, child2)
            if flag:
                break
    if not flag:
        return False
    return True


def get_compressed_graph(policy_graph: dict, configuration_graph: dict, topo_graph: dict):
    uncompressed_node = get_uncompressed_node(policy_graph, configuration_graph, topo_graph)

    label_dict = {}
    for node in configuration_graph:
        if node in uncompressed_node:  # 不压缩此类节点
            label_dict[node] = list([node])
            continue
        label = get_label(node)
        if label not in label_dict:
            label_dict[label] = list()
        label_dict[label].append(node)

    # node: its bisimulative bros
    bisimulation_dict = {}
    for label, nodes in label_dict.items():
        for i in range(len(nodes)):
            if len(nodes) == 1:
                bisimulation_dict[nodes[i]] = list([nodes[i]])
            for j in range(i + 1, len(nodes)):
                if nodes[i] not in bisimulation_dict:
                    bisimulation_dict[nodes[i]] = list([nodes[i]])
                if nodes[j] not in bisimulation_dict:
                    bisimulation_dict[nodes[j]] = list([nodes[j]])
                if nodes[i] in bisimulation_dict[nodes[j]]:
                    continue
                flag = verify_bisimulation(configuration_graph, nodes[i], nodes[j])
                if flag:
                    bisimulation_dict[nodes[i]].append(nodes[j])
                    bisimulation_dict[nodes[j]].append(nodes[i])
                    # bisimulation 是等价关系，可以传递
                    for other in bisimulation_dict[nodes[i]]:
                        if other not in bisimulation_dict[nodes[j]]:
                            bisimulation_dict[other].append(nodes[j])
                            bisimulation_dict[nodes[j]].append(other)
                    for other in bisimulation_dict[nodes[j]]:
                        if other not in bisimulation_dict[nodes[i]]:
                            bisimulation_dict[other].append(nodes[i])
                            bisimulation_dict[nodes[i]].append(other)

    # a set of bisimulative nodes set
    clusters = set()
    node_cluster_dict = {}
    for _, brs in bisimulation_dict.items():
        cluster = tuple(sorted(brs))
        if cluster in clusters:
            continue
        clusters.add(cluster)
        for i in brs:
            node_cluster_dict[i] = cluster

    # get compressed graph
    compressed_configuration_graph = {}
    for cluster in clusters:
        if cluster not in compressed_configuration_graph:
            compressed_configuration_graph[cluster] = list()
        for node in cluster:
            for child in configuration_graph[node]:
                if node_cluster_dict[child] not in compressed_configuration_graph[cluster]:
                    compressed_configuration_graph[cluster].append(node_cluster_dict[child])

    compressed_topo_graph = {}
    # 先把 压缩配置图 无向化
    for cluster, children in compressed_configuration_graph.items():
        if cluster not in compressed_topo_graph:
            compressed_topo_graph[cluster] = list()
        for child in children:
            if child not in compressed_topo_graph:
                compressed_topo_graph[child] = list()
            if cluster not in compressed_topo_graph[child]:
                compressed_topo_graph[child].append(cluster)
            if child not in compressed_topo_graph[cluster]:
                compressed_topo_graph[cluster].append(child)

    for node, children in topo_graph.items():
        # 此节点不在 配置图 中
        if node not in node_cluster_dict:
            cluster = tuple([node])
            node_cluster_dict[node] = cluster
            compressed_topo_graph[cluster] = list()
        else:
            cluster = node_cluster_dict[node]
        for child in children:
            # 此节点不在 配置图 中
            if child not in node_cluster_dict:
                child_cluster = tuple([child])
                node_cluster_dict[child] = child_cluster
                compressed_topo_graph[child_cluster] = list()
            else:
                child_cluster = node_cluster_dict[child]
            if child_cluster not in compressed_topo_graph[cluster]:
                compressed_topo_graph[cluster].append(child_cluster)
            if cluster not in compressed_topo_graph[child_cluster]:
                compressed_topo_graph[child_cluster].append(cluster)

    return compressed_configuration_graph, compressed_topo_graph


if __name__ == "__main__":
    get_compressed_graph(TEST_POLICY, TEST_CONFIGURATION, TEST_TOPO)
