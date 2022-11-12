import gurobipy

from parse.configuration_graph import get_configuration_graph
from parse.topo_graph import get_topo_graph
from parse.policy_graph import have_policy_path, POLICY_GRAPH, POLICY_NODE_CHILDREN
from parse.policy_graph import get_policy


def get_edges(graph):
    result = gurobipy.tuplelist()
    for pre, children in graph.items():
        for child in children:
            result.append((pre, child))
    return result


def repair(flag=None):
    # 图
    topo_graph = get_topo_graph()
    policies = get_policy()
    configuration_graph = get_configuration_graph()

    # 边集
    topo_edges = get_edges(topo_graph)
    configuration_edges = get_edges(configuration_graph)

    # 创建优化模型
    MODEL = gurobipy.Model()
    # 创建变量
    x_ij = MODEL.addVars(topo_edges, vtype=gurobipy.GRB.BINARY)
    x_ijpq = MODEL.addVars(topo_edges, policies, vtype=gurobipy.GRB.BINARY)

    # 更新变量环境
    MODEL.update()

    # 目标函数
    # x_ij
    MODEL.setObjective(
        gurobipy.quicksum(x_ij[i, j] for (i, j) in topo_edges
                          if (i, j) not in configuration_edges)
        -
        gurobipy.quicksum(x_ij[i, j] for (i, j) in topo_edges
                          if (i, j) in configuration_edges),
        sense=gurobipy.GRB.MINIMIZE)

    # 被映射到Policy就被映射到Config
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] / len(policies) for p, q in policies)
        <= x_ij[i, j] for i, j in topo_edges
    )

    # 没被映射到Policy就不能被映射到Config 这里不能和上面一样归一化
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] for p, q in policies)
        >= x_ij[i, j] for i, j in topo_edges
    )

    # (3) 避免自环
    MODEL.addConstrs(
        x_ij[i, j] + x_ij[j, i] <= 1
        for i, j in topo_edges
    )

    # (4) 单播 与 EC模型一致
    MODEL.addConstrs(
        gurobipy.quicksum(x_ij[i, j] for j in topo_graph[i]) <= 1
        for i in topo_graph
    )

    for (p, q), (m, n) in policies.items():
        if m == 0:  # Isolation
            # Isolation不能映射到任何路径
            MODEL.addConstrs(x_ijpq[i, j, p, q] == 0 for i, j in topo_edges)
            candidate = set(POLICY_NODE_CHILDREN[p])
            candidate.add(p)
            for source in candidate:
                # 移除 q, i
                MODEL.addConstrs(
                    x_ijpq[q, j, source, x] == 0
                    for x in POLICY_GRAPH[source]
                    for j in topo_graph[q]
                )
                # 移除 i, q
                MODEL.addConstrs(
                    x_ijpq[i, q, source, x] == 0
                    for x in POLICY_GRAPH[source]
                    for i in topo_graph[q]
                )
        elif m == 1:  # reachability
            for i in topo_graph:
                if i == p:
                    MODEL.addConstr(
                        gurobipy.quicksum(x_ijpq[i, j, p, q]
                                          for j in topo_graph[i]) == 1
                    )
                    MODEL.addConstr(
                        gurobipy.quicksum(x_ijpq[j, i, p, q]
                                          for j in topo_graph[i]) == 0
                    )
                elif i == q:
                    MODEL.addConstr(
                        gurobipy.quicksum(x_ijpq[i, j, p, q]
                                          for j in topo_graph[q]) == 0
                    )
                    MODEL.addConstr(
                        gurobipy.quicksum(x_ijpq[j, i, p, q]
                                          for j in topo_graph[q]) == 1
                    )
                else:
                    MODEL.addConstr(
                        gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q])
                                          for j in topo_graph[i]) == 0
                    )
                    # waypoint
                    if have_policy_path(i, q) or have_policy_path(i, p):
                        MODEL.addConstr(
                            gurobipy.quicksum(x_ijpq[i, j, p, q]
                                              for j in topo_graph[i]) == 0
                        )
    MODEL.update()

    # 执行
    MODEL.optimize()

    edge_addition = set()
    edge_deletion = set()

    if MODEL.status == gurobipy.GRB.Status.OPTIMAL:
        configuration_edge_select = MODEL.getAttr('x', x_ij)
        for ((i, j), value) in configuration_edge_select.items():
            if value == 1 and (i, j) not in configuration_edges:
                edge_addition.add(tuple([i, j]))
            if value == 0 and ((i, j) in configuration_edges):
                edge_deletion.add(tuple([i, j]))
        return edge_addition, edge_deletion
    else:
        return None, None
