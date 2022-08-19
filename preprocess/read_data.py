import json
from .policy_graph import init_policy
from .topo_graph import init_topo_graph
from .configuration_graph import init_configuration_graph

def set_policy():
    with open('data/policy_data.json') as data:
        policy_data = json.load(data)
        policies = policy_data['policies']
        policies_set = set()
        for policy in policies:
            policies_set.add(tuple(policy))
        init_policy(policies_set)


def set_topo():
    with open('data/topo_data.json') as data:
        topo_data = json.load(data)
        graph = topo_data['graph']
        for key in graph:
            graph[key] = set(graph[key])
        init_topo_graph(graph)


def set_configuration():
    with open('data/configuration_data.json') as data:
        configuration_data = json.load(data)
        graph = configuration_data['graph']
        for key in graph:
            graph[key] = set(graph[key])
        init_configuration_graph(graph)