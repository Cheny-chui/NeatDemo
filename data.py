POLICY_DATA = {
    'map': {
        'm': ['r'],
        'r': ['j'],
        'e': ['j'],
        'j': []
    },
    'reachability': {
        ('m', 'j'): (1, -1),
        ('i', 'j'): (1, -1)
    },
    'isolation': {
        ('i', 'j'): (1, -1),
        ('m', 'j'): (0, -1),
    },
    'waypoint': {
        ('m', 'r'): (1, -1),
        ('r', 'j'): (1, -1)
    },
    'path_length': {
        ('m', 'r'): (1, 2),
        ('r', 'j'): (1, 2)
    },
    'multipath': { # 多路径 和 path_length互相冲突，path_length作用于单路径，要么就要 n = n*m 限制总体
        ('i', 'j'): (3, -1),
    }
}

CONFIG_DATA = {
    'reachability': {
        'd': ['f'],
        'f': ['j'],
        'i': ['d'],
        'j': ['k'],
        'm': ['p'],
        'p': [],
    },
    'isolation': {
        'd': ['f'],
        'f': ['j'],
        'i': ['d'],
        'j': [],
        'm': ['p'],
        'p': ['q'],
        'q': ['j'],
    },
    'waypoint': {  # m->j 必须过 r
        'j': [],
        'm': ['p'],
        'p': ['q'],
        'q': ['j'],
    },
    'path_length': {
        'j': [],
        'm': ['p'],
        'p': ['q'],
        'q': ['j'],
    },
    'multipath': {
        'd': ['f'],
        'f': ['j'],
        'i': ['d'],
        'j': [],
    }
}

TOPO_DATA = {
    'a': ['i'],
    'b': ['i'],
    'c': ['i', 'h'],
    'd': ['i', 'f'],
    'e': ['i', 'g'],
    'f': ['d', 'j'],
    'g': ['e', 'j'],
    'h': ['c', 'j'],
    'i': ['a', 'b', 'c', 'd', 'e', 'DROP'],
    'j': ['f', 'g', 'h', 'k', 'q', 'DROP'],
    'k': ['j'],
    'm': ['p', 'DROP'],
    'p': ['m', 'q', 'r'],
    'q': ['j', 'p', 'r'],
    'r': ['q', 'p'],
    'DROP': ['m', 'i', 'j'],
}
