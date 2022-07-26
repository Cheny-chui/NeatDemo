import queue

POLICY_DATA = {
    'reachability': {
        ('m', 'j'): (1, -1),
        ('i', 'j'): (1, -1)
    },
    'isolation': {
        ('m', 'j'): (1, -1),
        ('i', 'j'): (0, -1),
    },
    'waypoint': {
        ('m', 'r'): (1, -1),
        ('r', 'j'): (1, -1)
    },
    'path_length': {
        ('m', 'j'): (1, 3)
    },
    'multipath': {  # 多路径 和 path_length互相冲突，path_length作用于单路径，要么就要 n = n*m 限制总体
        ('i', 'j'): (3, -1),
    },
}

POLICY_GRAPH = {
    'reachability': {
        'm': ['j'],
        'i': ['j'],
        'j': []
    },
    'isolation': {
        'm': ['j'],
        'i': ['j'],
        'j': []
    },
    'waypoint': {
        'm': ['r'],
        'r': ['j'],
        'j': []
    },
    'path_length': {
        'm': ['j'],
        'j': []
    },
    'multipath': {
        'i': ['j'],
        'j': []
    },
}


def get_policy():
    pass


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
