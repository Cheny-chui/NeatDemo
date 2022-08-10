"""
"""

TEST_POLICY = {
    ('a', 'b'),
    ('p', 'q')
}

TEST_CONFIGURATION_GRAPH = {
    'a': ['c', ],
    'b': ['a', ],
    'c': ['b', 'd', ],
    'd': ['e', ],
    'e': ['f', ],
    'f': ['h', ],
    'g': ['f', ],
    'h': ['d', 'g', ],
}

TEST_FLOW = {
    ('a', 'c'): {('p', 'q'), ('a', 'b')},
    ('b', 'a'): {('p', 'q'), ('a', 'b')},
    ('c', 'b'): {('p', 'q'), ('a', 'b')},
    ('c', 'd'): {('p', 'q'), },
    ('d', 'e'): {('p', 'q'), },
    ('e', 'f'): {('p', 'q'), },
    ('f', 'h'): {('p', 'q'), },
    ('g', 'f'): {('p', 'q'), },
    ('h', 'd'): {('p', 'q'), },
    ('h', 'g'): {('p', 'q'), },
}


def dfs(flow, graph, loops, root, now, stack: list):
    if now in stack:
        return
    stack.append(now)
    for next in graph[now]:
        if flow in TEST_FLOW[now, next]:
            if next == root:  # 只看对应flow的边
                key = tuple(sorted(stack))
                stack.append(root)
                value = tuple(stack)
                if key not in loops:
                    loops[key] = value
                stack.pop()
                continue
            dfs(flow, graph, loops, root, next, stack)
    stack.pop()
    return


# 考虑几百个设备，因此直接用dfs跑
def get_loops(flow, graph=None):
    if graph is None:
        graph = TEST_CONFIGURATION_GRAPH
    # sorted_loop: true_loop
    loops = {}
    for node in graph:
        dfs(flow, graph, loops, node, node, [])

    return loops


def remove_links(flow, detected_loops: dict):
    # 没有loop，直接退出
    if not len(detected_loops):
        return None
    # link: [loop1,loop2]
    link_loop_map = {}
    for sorted_loop, true_loop in detected_loops.items():
        for i in range(1, len(true_loop)):
            edge = (true_loop[i - 1], true_loop[i])
            if edge not in link_loop_map:
                link_loop_map[edge] = list()
            link_loop_map[edge].append(sorted_loop)

    # 得到公共边
    # loops: links
    shared_links = {}
    for link, loops in link_loop_map.items():
        if len(loops) > 1:
            sorted_loop = tuple(loops)
            if sorted_loop not in shared_links:
                shared_links[sorted_loop] = list()
            shared_links[sorted_loop].append(link)

    solved_loops = set()
    deleted_links = set()

    # 删除公共边
    for sorted_loop, true_loop in shared_links.items():
        for i in sorted_loop:
            solved_loops.add(i)
        deleted_links.add(true_loop[0])

    # 删除dst发出的边
    if len(solved_loops) < len(detected_loops):
        for sorted_loop, true_loop in detected_loops.items():
            for dst in flow[-1:]:
                if sorted_loop not in solved_loops and dst in sorted_loop:
                    solved_loops.add(sorted_loop)
                    for i, node in enumerate(true_loop):
                        if node == dst:
                            to_be_deleted_link = tuple([true_loop[i], true_loop[i + 1 % len(true_loop)]])
                            deleted_links.add(to_be_deleted_link)
                            break

    # 在剩下的环路选择一条边（rule）删除
    if len(solved_loops) < len(detected_loops):
        for sorted_loop, true_loop in detected_loops.items():
            if sorted_loop not in solved_loops:
                solved_loops.add(sorted_loop)
                # 任选一条边删除
                to_be_deleted_link = tuple([true_loop[0], true_loop[1]])
                deleted_links.add(to_be_deleted_link)

    # TODO 下发给底层以删除link

    return solved_loops, deleted_links


if __name__ == '__main__':
    for policy in TEST_POLICY:
        print(remove_links(policy, get_loops(policy)))
