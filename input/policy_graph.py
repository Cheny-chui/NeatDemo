import queue
from .topo_graph import add_drop

POLICY = {}

POLICY_GRAPH = {}


def init_policy(policies: set[tuple[str, str, int, int]]):
    for policy in policies:  # (p:str,q:str,m:int,n:int)
        (p, q, m, n) = policy
        POLICY[(p, q)] = (m, n)

        if m == 0:  # 添加 isolation的 DROP
            add_drop(p, q)

        if p not in POLICY_GRAPH:
            POLICY_GRAPH[p] = list()
        if q not in POLICY_GRAPH:
            POLICY_GRAPH[q] = list()
        POLICY_GRAPH[p].append(q)


def get_policy():
    return POLICY


def get_policy_graph():
    return POLICY_GRAPH


POLICY_PATH = set()


def have_policy_path(policy_graph, node1: str, node2: str) -> bool:
    if (node1, node2) in POLICY_PATH:
        return True
    q = queue.Queue()
    q.put(node1)
    while not q.empty():
        now = q.get()
        if now == node2:
            POLICY_PATH.add((node1, node2))
            return True
        for i in policy_graph[now]:
            if i == node2:
                POLICY_PATH.add((node1, node2))
                return True
            q.put(i)
    return False
