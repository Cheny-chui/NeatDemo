def get_remove_links(loops_set: list[tuple[str, ...]], policies: list[tuple[str, ...]]):
    # 没有loop，直接退出
    if not len(loops_set):
        return None
    # link: [loop1,loop2]
    link_loop_map = {}
    for loop in loops_set:
        for i in range(1, len(loop)):
            edge = (loop[i - 1], loop[i])
            if edge not in link_loop_map:
                link_loop_map[edge] = set()
            link_loop_map[edge].add(loop)

    # 得到公共边
    # loops: shared_links
    shared_links = {}
    for link, loops in link_loop_map.items():
        if len(loops) > 1:
            key = tuple(loops)
            if key not in shared_links:
                shared_links[key] = set()
            shared_links[key].add(link)

    solved_loops = set()
    deleted_links = set()

    # 根据loops的长度降序，以免多删边
    temp = {}
    for loops in sorted(shared_links,key=len,reverse=True):
        temp[loops] = shared_links[loops]
    shared_links = temp

    # 删除公共边
    for loops, links in shared_links.items():
        have_loop_to_repair = False
        for loop in loops:
            if loop not in solved_loops:
                have_loop_to_repair = True
                solved_loops.add(loop)
        if have_loop_to_repair:
            for link in links:
                if link not in deleted_links:
                    deleted_links.add(link)

    # 删除dst发出的边
    if len(solved_loops) < len(loops_set):
        remain_loops = set()
        for loop in loops_set:
            if loop not in solved_loops:
                remain_loops.add(loop)
        for loop in remain_loops:
            for policy in policies:
                node_count = 0
                dst = None
                for node in policy[-1:]:
                    if node in loop:
                        if node_count == 0:
                            dst = node
                        node_count += 1
                if dst is not None:
                    for i in range(len(loop)):
                        if loop[i] == dst:
                            solved_loops.add(loop)
                            deleted_links.add(tuple([loop[i], loop[i + 1]]))
                            break
                    break
    # 在剩下的环路选择一条边（rule）删除
    if len(solved_loops) < len(loops_set):
        for loop in loops_set:
            if loop not in solved_loops:
                solved_loops.add(loop)
                # 任选一条边删除
                to_be_deleted_link = tuple([loop[0], loop[1]])
                deleted_links.add(to_be_deleted_link)

    return solved_loops, deleted_links
