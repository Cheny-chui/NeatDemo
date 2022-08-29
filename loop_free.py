from preprocess.loop_free import loop_free
import json

if __name__ == '__main__':
    result = loop_free()
    print(result)
    with open('output.json', 'w') as output:
        for key in result:
            result[key] = list(result[key])
        json.dump(result, output)
