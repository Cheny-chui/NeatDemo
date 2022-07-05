import gurobipy
import data
import typing
import queue

target_policy = 'multipath'

POLICY = data.POLICY_DATA[target_policy]
CONFIG = data.CONFIG_DATA[target_policy]
TOPO = data.TOPO_DATA


# 获取边集
def get_edge_set(graph):
    result = gurobipy.tuplelist()
    for pre, nexts in graph.items():
        for next in nexts:
            result.append((pre, next))
    return result


POLICY_PATH = set()


def have_policy_path(node1: str, node2: str) -> bool:
    if (node1, node2) in POLICY_PATH:
        return True
    q = queue.Queue()
    q.put(node1)
    graph = data.POLICY_DATA['map']
    while not q.empty():
        now = q.get()
        if now == node2:
            POLICY_PATH.add((node1, node2))
            return True
        for i in graph[now]:
            if i == node2:
                POLICY_PATH.add((node1, node2))
                return True
            q.put(i)
    return False


E_topo = get_edge_set(TOPO)
E_config = get_edge_set(CONFIG)


def run(POLICY: typing.Dict[tuple[str, str], tuple[int, int]]):
    # 边集

    # 创建优化模型
    MODEL = gurobipy.Model()
    # 创建变量
    x_ij = MODEL.addVars(E_topo, vtype=gurobipy.GRB.BINARY)
    x_ijpq = MODEL.addVars(E_topo, POLICY, vtype=gurobipy.GRB.BINARY)
    # 更新变量环境
    MODEL.update()

    # 目标函数
    MODEL.setObjective(
        gurobipy.quicksum(x_ij[i, j] for (i, j) in E_topo if (i, j) not in E_config) - gurobipy.quicksum(
            x_ij[i, j] for (i, j) in E_topo if (i, j) in E_config),
        sense=gurobipy.GRB.MINIMIZE)

    # 创建约束
    # (1) & (2) 上面存的TOPO是双向边，所以不用显式声明(2)的Constrain
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] / len(POLICY) for p, q in POLICY)
        <= x_ij[i, j] for i, j in E_topo
    )

    # 没有被映射到Policy就不能被映射到Config
    # 此约束添加了 就会删除所有 ”不该“ 有的边
    MODEL.addConstrs(
        gurobipy.quicksum(x_ijpq[i, j, p, q] for p, q in POLICY)
        >= x_ij[i, j] for i, j in E_topo
    )

    # (3) 避免loop
    MODEL.addConstrs(
        x_ij[i, j] + x_ij[j, i] <= 1
        for i, j in E_topo
    )

    # (4) 单播
    # MODEL.addConstrs(
    #     gurobipy.quicksum(x_ij[i, j] for j in TOPO[i]) <= 1
    #     for i in TOPO
    # )

    for (p, q), (m, n) in POLICY.items():
        # waypoint
        MODEL.addConstrs(
            gurobipy.quicksum(x_ijpq[i, j, p, q] for j in TOPO[i]) == 0
            for p, q in POLICY for i in TOPO if i != p and i != q and
            i in data.POLICY_DATA['map'] and (have_policy_path(i, p) or have_policy_path(i, q))
        )
        MODEL.addConstrs(
            gurobipy.quicksum(x_ijpq[j, i, p, q] for j in TOPO[i]) == 0
            for p, q in POLICY for i in TOPO if i != p and i != q and
            i in data.POLICY_DATA['map'] and (have_policy_path(i, p) or have_policy_path(i, q))
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
                for i in TOPO if i != p and i != q and i != 'DROP' and not (
                        i in data.POLICY_DATA['map'] and (have_policy_path(i, p) or have_policy_path(i, q)))
            )
        elif m == 1:
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for j in TOPO[i]) == 1
                for i in TOPO if i == p
            )
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[j, i, p, q] for j in TOPO[i]) == 0
                for i in TOPO if i == p
            )

            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[j, i, p, q] for j in TOPO[i]) == 1
                for i in TOPO if i == q
            )
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for j in TOPO[i]) == 0
                for i in TOPO if i == q
            )
            # else
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in TOPO[i]) == 0
                for i in TOPO if i != p and i != q and not (
                        i in data.POLICY_DATA['map'] and (have_policy_path(i, p) or have_policy_path(i, q)))
            )
        elif m > 1:
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for j in TOPO[i]) >= m
                for i in TOPO if i == p
            )
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[j, i, p, q] for j in TOPO[i]) == 0
                for i in TOPO if i == p
            )

            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[j, i, p, q] for j in TOPO[i]) >= m
                for i in TOPO if i == q
            )
            MODEL.addConstrs(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for j in TOPO[i]) == 0
                for i in TOPO if i == q
            )
            # else
            MODEL.addConstrs(
                gurobipy.quicksum((x_ijpq[i, j, p, q] - x_ijpq[j, i, p, q]) for j in TOPO[i]) == 0
                for i in TOPO if i != p and i != q and not (
                        i in data.POLICY_DATA['map'] and (have_policy_path(i, p) or have_policy_path(i, q)))
            )
        # path length
        if n != -1:
            MODEL.addConstr(
                gurobipy.quicksum(x_ijpq[i, j, p, q] for i, j in E_topo) <= n
            )
    MODEL.update()

    # 执行
    MODEL.optimize()
    return MODEL.getAttr('x', x_ij) if MODEL.status == gurobipy.GRB.Status.OPTIMAL else None


if __name__ == '__main__':
    result = run(POLICY)
    if result:
        for k, v in result.items():
            if v == 1 and (k not in E_config):
                print(f'添加边: {k}')
            if v == 0 and (k in E_config):
                print(f'删除边: {k}')
