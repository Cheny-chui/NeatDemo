import gurobipy
import typing

from core.configuration_graph import get_configuration_edge, add_edge, del_edge
from core.topo_graph import get_topo_graph, get_topo_edge
from core.policy_graph import have_policy_path

last_flow = {}


def repair(policy: typing.Dict[tuple[str, str], tuple[int, int]], policy_graph):
    TOPO = get_topo_graph()
    E_topo = get_topo_edge()
    E_config = get_configuration_edge()

    # 创建优化模型
    MODEL = gurobipy.Model()
    # 创建变量
    x_ij = MODEL.addVars(E_topo, vtype=gurobipy.GRB.BINARY)
    x_ijpq = MODEL.addVars(E_topo, policy, vtype=gurobipy.GRB.BINARY)

    # 更新变量环境
    MODEL.update()

    # 目标函数
    # TODO 考虑将目标函数设为 x_ijpq的最小修改
    MODEL.setObjective(
        gurobipy.quicksum(x_ij[i, j] for (i, j) in E_topo if (i, j) not in E_config) - gurobipy.quicksum(
            x_ij[i, j] for (i, j) in E_topo if (i, j) in E_config),
        sense=gurobipy.GRB.MINIMIZE)

    # 创建约束
    # (1) & (2) 上面存的TOPO是双向边，所以不用显式声明(2)的Constrain
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] / len(policy) for p, q in policy)
        <= x_ij[i, j] for i, j in E_topo
    )

    # 没有被映射到Policy就不能被映射到Config
    # 此约束添加了 就会删除所有 ”不该“ 有的边
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] for p, q in policy)
        >= x_ij[i, j] for i, j in E_topo
    )

    # (3) 避免loop
    MODEL.addConstrs(
        x_ij[i, j] + x_ij[j, i] <= 1
        for i, j in E_topo
    )

    # # (4) 单播 与多路径冲突
    # MODEL.addConstrs(
    #     gurobipy.quicksum(x_ij[i, j] for j in TOPO[i]) <= 1
    #     for i in TOPO
    # )

    for (p, q), (m, n) in policy.items():
        # waypoint
        MODEL.addConstrs(
            gurobipy.quicksum(x_ijpq[i, j, p, q] for j in TOPO[i]) == 0
            for i in TOPO if i != p and i != q and
            i in policy_graph and (
                    have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph,
                                                                             i, q))
        )
        MODEL.addConstrs(
            gurobipy.quicksum(x_ijpq[j, i, p, q] for j in TOPO[i]) == 0
            for i in TOPO if i != p and i != q and
            i in policy_graph and (
                    have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q))
        )
        if m == 0:  # Isolation
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for j in TOPO[i]) == 1
                for i in TOPO if i == p
            )
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[j, i, p, q] for j in TOPO[i]) == 0
                for i in TOPO if i == p
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq['DROP', j, p, q] for j in TOPO['DROP']) == 0
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, 'DROP', p, q] for j in TOPO['DROP']) == 1
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[q, j, p, q] for j in TOPO[q]) == 0
            )
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in TOPO[i]) == 0
                for i in TOPO if i != p and i != q and i != 'DROP'
                and
                not (i in policy_graph and (
                        have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q)))
            )
        elif m <= 1:  # reachability
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, 'DROP', p, q] for j in TOPO['DROP']) == 0
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[p, j, p, q] for j in TOPO[p]) == 1
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, p, p, q] for j in TOPO[p]) == 0
            )

            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, q, p, q] for j in TOPO[q]) == 1
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[q, j, p, q] for j in TOPO[q]) == 0
            )
            # else
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in TOPO[i]) == 0
                for i in TOPO if i != p and i != q
                and not (
                        i in policy_graph and (
                        have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q)))
            )
        elif m > 1:  # multi_path
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, 'DROP', p, q] for j in TOPO['DROP']) == 0
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[p, j, p, q] for j in TOPO[p]) >= m
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, p, p, q] for j in TOPO[p]) == 0
            )

            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[j, q, p, q] for j in TOPO[q]) >= m
            )
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[q, j, p, q] for j in TOPO[q]) == 0
            )
            # else
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in TOPO[i]) == 0
                for i in TOPO if i != p and i != q
                and not (
                        i in policy_graph and (
                        have_policy_path(policy_graph, i, p) or have_policy_path(policy_graph, i, q)))
            )

        if n != -1:  # path length
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for i, j in E_topo) <= n
            )
    MODEL.update()

    # 执行
    MODEL.optimize()
    if MODEL.status == gurobipy.GRB.Status.OPTIMAL:
        config_select, config_flow = MODEL.getAttr('x', x_ij), MODEL.getAttr('x', x_ijpq)
        for (key, value) in config_select.items():
            if value == 1:
                if key not in E_config:
                    print(f'添加边: {key}')
                    add_edge(key[0], key[1])
                    last_flow[key] = list()
                    for (i, j, p, q) in config_flow:
                        if (i, j) == key and config_flow[i, j, p, q]:
                            print(f'    此边流量:{p, q}')
                            last_flow[key].append((p, q))
                else:
                    flow = list()
                    for (i, j, p, q) in config_flow:
                        if (i, j) == key and config_flow[i, j, p, q]:
                            flow.append((p, q))
                    if flow != last_flow[key]:
                        print(f'修改边: {key}')
                        print(f'    边{key}的流量变化: {last_flow[key]} ===>>> {flow}')
                        last_flow[key] = flow
                    else:
                        print(f'边{key}的流量还是: {flow}')
            if value == 0 and (key in E_config):
                print(f'删除边: {key}')
                del_edge(key[0], key[1])
                if key in last_flow:
                    print(f'    此边流量:{last_flow[key]}')
                    last_flow.pop(key)
    return
