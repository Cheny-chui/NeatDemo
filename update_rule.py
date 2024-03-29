import json
import sys


def get_device_rules() -> dict[str, dict[str, list]]:
    device_rules = {}
    with open('data/odlrule.txt') as input:
        lines = input.readlines()
        lines = ''.join(lines).strip('\n').splitlines()
        current_dev = ''
        for line in lines:
            elements = line.split(' ')
            if elements[0] == '$devicename':
                current_dev = elements[1]
                if current_dev not in device_rules:
                    device_rules[current_dev] = dict()
            else:
                prefix, action = elements
                if prefix not in device_rules[current_dev]:
                    device_rules[current_dev][prefix] = list()
                device_rules[current_dev][prefix].append(action)
    return device_rules


def get_edge_port() -> dict[tuple, tuple]:
    edge_port: dict[tuple, tuple] = {}
    with open('data/odltopo.txt') as input:
        lines = input.readlines()
        lines = ''.join(lines).strip('\n').splitlines()
        edge_flag = False
        for line in lines:
            if line == 'edges:':
                edge_flag = True
                continue
            if edge_flag:
                elements = line.split(' ')
                dev_port_1, dev_port_2 = elements[0], elements[1]
                dev1, port1 = dev_port_1.split('.')
                dev2, port2 = dev_port_2.split('.')
                edge_port[(dev1, dev2)] = (port1, port2)
    return edge_port


# 将rules存入txt
def set_rules(device_rules: dict[str, dict[str, list]]):
    with open('new_odlrule.txt', 'w') as output:
        for device, rules in device_rules.items():
            output.write(f'$devicename {device}\n')
            for prefix, actions in rules.items():
                for action in actions:
                    output.write(f'{prefix} {action}\n')


# usage: python update_rule.py ec_str
if __name__ == '__main__':
    if len(sys.argv) > 1:
        ec = sys.argv[1]
    else:
        ec = "11.0.0.0/8"
    device_rules = get_device_rules()
    edge_port = get_edge_port()
    with open('output.json') as f:
        changes = json.load(f)
        deleted_links = changes['deleted_links']
        added_links = changes['added_links']

    if deleted_links:
        for link in deleted_links:
            port = edge_port[tuple(link)]
            foward_device = link[0]
            foward_port = port[0]
            # 获取对应节点的rule的引用
            rules: dict = device_rules[foward_device]  # prefix: actions
            if ec not in rules:
                rules[ec] = list()
                rules[ec].append('default')
            else:
                rules[ec].remove(foward_port)
                if len(rules[ec]) == 0:  # 加上细粒度丢弃规则
                    rules[ec].append('default')
    if added_links:
        for link in added_links:
            port = edge_port[tuple(link)]
            foward_device = link[0]
            foward_port = port[0]
            # 获取对应节点的rule的引用
            rules: dict = device_rules[foward_device]  # prefix: actions
            if ec not in rules:
                rules[ec] = list()
            rules[ec].append(port[0])

    set_rules(device_rules)
