import gurobipy

from .compress import get_compressed_graph

from preprocess.configuration_graph import get_configuration_graph
from preprocess.topo_graph import get_topo_graph
from preprocess.policy_graph import have_policy_path
from preprocess.policy_graph import get_policy
from preprocess.policy_graph import get_policy_graph


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
    policy_graph = get_policy_graph()
    configuration_graph = get_configuration_graph()

    # 压缩图
    if flag is not None:
        configuration_graph, topo_graph, configuration_flow, configuration_edge_flow \
            = get_compressed_graph(policies,
                                   configuration_graph,
                                   topo_graph)

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
        gurobipy.quicksum(x_ij[i, j] for (i, j) in topo_edges if (i, j) not in configuration_edges)
        -
        gurobipy.quicksum(x_ij[i, j] for (i, j) in topo_edges if (i, j) in configuration_edges),
        sense=gurobipy.GRB.MINIMIZE)

    # 创建约束
    # (1) & (2) 上面存的TOPO是双向边，所以不用显式声明(2)的Constrain
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] / len(policies) for p, q in policies)
        <= x_ij[i, j] for i, j in topo_edges
    )

    # 没有被映射到Policy就不能被映射到Config
    # 此约束添加了 就会删除所有 ”不该“ 有的边
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] for p, q in policies)
        >= x_ij[i, j] for i, j in topo_edges
    )

    # (3) 避免loop
    MODEL.addConstrs(
        x_ij[i, j] + x_ij[j, i] <= 1
        for i, j in topo_edges
    )

    # # (4) 单播 与多路径冲突
    # MODEL.addConstrs(
    #     gurobipy.quicksum(x_ij[i, j] for j in topo_graph[i]) <= 1
    #     for i in topo_graph
    # )

    for (p, q), (m, n) in policies.items():
        # waypoint
        MODEL.addConstrs(
            gurobipy.quicksum(x_ijpq[i, j, p, q] for j in topo_graph[i]) == 0
            for i in topo_graph if i != p and i != q and
            i in policy_graph and (
                    have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph,
                                                                             i, q))
        )
        MODEL.addConstrs(
            gurobipy.quicksum(x_ijpq[j, i, p, q] for j in topo_graph[i]) == 0
            for i in topo_graph if i != p and i != q and
            i in policy_graph and (
                    have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q))
        )
        if m == 0:  # Isolation
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for j in topo_graph[i]) == 1
                for i in topo_graph if i == p
            )
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[j, i, p, q] for j in topo_graph[i]) == 0
                for i in topo_graph if i == p
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq['DROP', j, p, q] for j in topo_graph['DROP']) == 0
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, 'DROP', p, q] for j in topo_graph['DROP']) == 1
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[q, j, p, q] for j in topo_graph[q]) == 0
            )
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in topo_graph[i]) == 0
                for i in topo_graph if i != p and i != q and i != 'DROP'
                and
                not (i in policy_graph and (
                        have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q)))
            )
        elif m <= 1:  # reachability
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, 'DROP', p, q] for j in topo_graph['DROP']) == 0
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[p, j, p, q] for j in topo_graph[p]) == 1
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, p, p, q] for j in topo_graph[p]) == 0
            )

            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, q, p, q] for j in topo_graph[q]) == 1
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[q, j, p, q] for j in topo_graph[q]) == 0
            )
            # else
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in topo_graph[i]) == 0
                for i in topo_graph if i != p and i != q
                and not (
                        i in policy_graph and (
                        have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q)))
            )
        elif m > 1:  # multi_path
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, 'DROP', p, q] for j in topo_graph['DROP']) == 0
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[p, j, p, q] for j in topo_graph[p]) >= m
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, p, p, q] for j in topo_graph[p]) == 0
            )

            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, q, p, q] for j in topo_graph[q]) >= m
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[q, j, p, q] for j in topo_graph[q]) == 0
            )
            # else
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in topo_graph[i]) == 0
                for i in topo_graph if i != p and i != q
                and not (
                        i in policy_graph and (
                        have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q)))
            )

        if n != -1:  # path length
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for i, j in topo_edges) <= n
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
                print(f'添加边: {(i, j)}')
                edge_addition.add(tuple([i, j]))
            if value == 0 and ((i, j) in configuration_edges):
                print(f'删除边: {(i, j)}')
                edge_deletion.add(tuple([i, j]))
    if flag is not None:
        pass
        # TODO map back
    else:
        result = {'edge_addition': edge_addition, 'edge_deletion': edge_deletion}
        return result
