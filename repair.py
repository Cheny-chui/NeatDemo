import json

from core.repair import repair
from preprocess.read_data import set_topo, set_configuration, set_policy

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
