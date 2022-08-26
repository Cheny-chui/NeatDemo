from core.repair import repair
from preprocess.read_data import *

TOPO_GRAPH_DATA = {
    'a': ['i'],
    'b': ['i'],
    'c': ['i', 'f'],
    'd': ['i', 'g'],
    'e': ['i', 'h'],
    'f': ['c', 'j'],
    'g': ['d', 'j'],
    'h': ['e', 'j'],
    'i': ['a', 'b', 'c', 'd', 'e'],
    'j': ['f', 'g', 'h', 'q'],
    'm': ['p'],
    'p': ['m', 'q', 'r'],
    'q': ['j', 'p', 'r'],
    'r': ['p', 'q'],
    'DROP': [],
}

POLICY_DATA = {
    'reachability': {
        ('m', 'j', 1, -1),
        ('i', 'j', 1, -1)
    },
    # 'isolation': {
    #     ('m', 'j', 1, -1),
    #     ('i', 'j', 0, -1),
    # # },
    # 'waypoint': {
    #     ('m', 'r', 1, -1),
    #     ('r', 'j', 1, -1)
    # },
    # 'path_length': {
    #     ('m', 'j', 1, 3)
    # },
    # 'multipath': {  # 多路径 和 path_length互相冲突，path_length作用于单路径，要么就要 n = n*m 限制总体
    #     ('i', 'j', 3, -1),
    # },
}

if __name__ == '__main__':
    # repair reachability
    set_topo()
    set_policy()
    set_configuration()
    result = repair()
    with open('output.json', 'w') as output:
        for key in result:
            result[key] = list(result[key])
        json.dump(result, output)
