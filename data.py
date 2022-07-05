POLICY_DATA = {
    'map': {
        'm': ['r'],
        'r': ['j'],
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
    'multipath': {  # 多路径 和 path_length互相冲突，path_length作用于单路径，要么就要 n = n*m 限制总体
        ('i', 'j'): (3, -1),
    },
    'load_balance': {
        ('a', 'm'): (0.2, -1),
        ('a', 'p'): (0.2, -1),
        ('a', 'h'): (0.2, -1),
        ('a', 'f'): (0.2, -1),
        ('a', 'g'): (0.2, -1),
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

    },
    'load_balance': {

    }
}

TOPO_DATA = {
    'a': ['i'],
    'c': ['i', 'h', 'm', 'p'],
    'd': ['i', 'f'],
    'e': ['f', 'h', 'i', 'g'],
    'f': ['d', 'e', 'j'],
    'g': ['e', 'j'],
    'h': ['c', 'e', 'j'],
    'i': ['a', 'c', 'd', 'e', 'DROP'],
    'j': ['f', 'g', 'h', 'k', 'q', 'DROP'],
    'k': ['j'],
    'm': ['c', 'p', 'DROP'],
    'p': ['c', 'm', 'q', 'r'],
    'q': ['j', 'p', 'r'],
    'r': ['q', 'p'],
    'DROP': ['m', 'i', 'j'],
}
