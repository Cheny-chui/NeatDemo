import queue
from .topo_graph import add_drop

POLICY = {}

POLICY_NODE_CHILDREN = {

}

POLICY_NODE_ANCESTOR = {

}


def init_policy(policies: set[tuple[str, str, int, int]]):
    for policy in policies:  # (p:str,q:str,m:int,n:int)
        (p, q, m, n) = policy
        POLICY[(p, q)] = (m, n)

        if m == 0:  # 添加 isolation的 DROP
            add_drop(p, q)

        if p not in POLICY_NODE_CHILDREN:
            POLICY_NODE_CHILDREN[p] = set()
        if q not in POLICY_NODE_CHILDREN:
            POLICY_NODE_CHILDREN[q] = set()
        if p not in POLICY_NODE_ANCESTOR:
            POLICY_NODE_ANCESTOR[p] = set()
        if q not in POLICY_NODE_ANCESTOR:
            POLICY_NODE_ANCESTOR[q] = set()

        POLICY_NODE_CHILDREN[p].add(q)
        POLICY_NODE_CHILDREN[p].union(POLICY_NODE_CHILDREN[q])
        for ancestor in POLICY_NODE_ANCESTOR[p]:
            POLICY_NODE_CHILDREN[ancestor].add(q)
            POLICY_NODE_CHILDREN[ancestor].union(POLICY_NODE_CHILDREN[q])

        POLICY_NODE_ANCESTOR[q].add(p)
        POLICY_NODE_ANCESTOR[q].union(p)
        for child in POLICY_NODE_CHILDREN[q]:
            POLICY_NODE_ANCESTOR[child].add(p)
            POLICY_NODE_ANCESTOR[child].union(p)


def get_policy():
    return POLICY


def get_policy_graph():
    return POLICY_NODE_CHILDREN


def have_policy_path(policy_graph, node1: str, node2: str) -> bool:
    if node2 in POLICY_NODE_CHILDREN[node1]:
        return True
    return False
