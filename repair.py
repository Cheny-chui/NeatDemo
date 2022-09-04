import json

from core.repair import repair
from preprocess.read_data import read_repair_data

if __name__ == '__main__':
    # repair reachability
    read_repair_data()
    result = repair()
    with open('output.json', 'w') as output:
        for key in result:
            result[key] = list(result[key])
        json.dump(result, output)
