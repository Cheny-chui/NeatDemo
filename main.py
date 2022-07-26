from core import repair
from core import policy_graph

if __name__ == '__main__':
    for key, value in policy_graph.POLICY_DATA.items():
        print(f'========{key}========')
        repair.repair(policy=value,
                      policy_graph=policy_graph.POLICY_GRAPH[key])
