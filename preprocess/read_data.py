import json
from .policy_graph import init_policy
from .topo_graph import init_topo_graph
from .configuration_graph import init_configuration_graph


def read_repair_data():
    with open('data/repair_data.json') as json_data:
        data = json.load(json_data)

        policy_data = data['policy_data']
        policies = policy_data['policies']
        policies_set = set()
        for policy in policies:
            policies_set.add(tuple(policy))
        init_policy(policies_set)

        topo_data = data['topo_data']
        graph = topo_data['graph']
        for key in graph:
            graph[key] = set(graph[key])
        init_topo_graph(graph)

        configuration_data = data['configuration_data']
        graph = configuration_data['graph']
        tuple_graph = {}
        for key in graph:
            source, dst = key.split('-')
            tuple_graph[(source, dst)] = graph[key]
        init_configuration_graph(tuple_graph)
