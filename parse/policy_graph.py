POLICY = {}

POLICY_GRAPH: dict[str, set] = {}

POLICY_NODE_CHILDREN: dict[str, set] = {}

POLICY_NODE_ANCESTOR: dict[str, set] = {}


def clear_global():
    POLICY_NODE_ANCESTOR.clear()
    POLICY_NODE_CHILDREN.clear()
    POLICY_GRAPH.clear()
    POLICY.clear()


def init_set(p, q):
    if p not in POLICY_NODE_CHILDREN:
        POLICY_NODE_CHILDREN[p] = set()
    if q not in POLICY_NODE_CHILDREN:
        POLICY_NODE_CHILDREN[q] = set()
    if p not in POLICY_NODE_ANCESTOR:
        POLICY_NODE_ANCESTOR[p] = set()
    if q not in POLICY_NODE_ANCESTOR:
        POLICY_NODE_ANCESTOR[q] = set()


def add_child(ancestor, child):
    POLICY_NODE_CHILDREN[ancestor].add(child)
    POLICY_NODE_CHILDREN[ancestor].union(POLICY_NODE_CHILDREN[child])


def add_ancestor(child, ancestor):
    POLICY_NODE_ANCESTOR[child].add(ancestor)
    POLICY_NODE_ANCESTOR[child].union(ancestor)


def init_policy(policies: set[tuple[str, str, int, int]]):
    for policy in policies:  # (p:str,q:str,m:int,n:int)
        (p, q, m, n) = policy
        POLICY[(p, q)] = (m, n)

        init_set(p, q)
        if p not in POLICY_GRAPH:
            POLICY_GRAPH[p] = set()
        if q not in POLICY_GRAPH:
            POLICY_GRAPH[q] = set()
        if m == 0:  # isolation 不需要更新Policy图相关数据结构
            return

        POLICY_GRAPH[p].add(q)
        # q add into p's child set
        add_child(p, q)
        for ancestor in POLICY_NODE_ANCESTOR[p]:
            add_child(ancestor, q)

        add_ancestor(q, p)
        for child in POLICY_NODE_CHILDREN[q]:
            add_ancestor(child, p)


def get_policy():
    return POLICY


def have_policy_path(node1: str, node2: str) -> bool:
    if node1 in POLICY_NODE_CHILDREN and node2 in POLICY_NODE_CHILDREN[node1] \
            or \
            node2 in POLICY_NODE_CHILDREN and node1 in POLICY_NODE_CHILDREN[node2]:
        return True
    return False
