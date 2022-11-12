import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.loop_free import get_remove_links
from core.repair import repair
from parse.configuration_graph import init_configuration_graph
from parse.policy_graph import init_policy, have_policy_path, clear_global
from parse.topo_graph import init_topo_graph


def repair_loops(loop_free_data: dict[str, dict]):
    ret = {"status": True, "link_delta": {}}
    for ec, loop_data in loop_free_data.items():
        ret["link_delta"][ec] = {}
        loops = loop_data["loops"]
        receive_policies = loop_data["policies"]
        policies = list()
        for policy in receive_policies:
            temp_list = policy["path"]
            policies.append(tuple(temp_list))
        loop_set = list()
        for loop in loops:
            loop_set.append(tuple(loop))
        _, deleted_links = get_remove_links(loop_set, policies)
        print(f"delete links: {deleted_links}")
        ret["link_delta"][ec]["delete_links"] = list(deleted_links)
        ret["link_delta"][ec]["add_links"] = list()
    return ret


def repair_policies(repair_data: dict[str, dict]):
    ret = {"status": True, "link_delta": {}}
    clear_global()
    for ec, data in repair_data.items():
        ret["link_delta"][ec] = {}
        configuration_graph = data["configuration_graph"]
        init_configuration_graph(configuration_graph)
        receive_policies: list[dict] = data["policies"]
        policies: set[tuple] = set()
        isolation_policies: list[dict] = list()
        for policy in receive_policies:  # 只add 非isolation policy
            if policy["type"] == "isolation":
                isolation_policies.append(policy)
            else:
                path: list[str] = policy["path"]
                for i in range(len(path) - 1):
                    policies.add(tuple([path[i], path[i + 1], 1, -1]))
        init_policy(policies)
        policies = set()
        for policy in isolation_policies:  # add isolation policy
            path: list[str] = policy["path"]
            p = path[0]
            q = path[1]
            if have_policy_path(p, q):
                ret["status"] = False
                ret["message"] = "There is a conflict in reachability policy and isolation policy."
                return ret
            policies.add(tuple([path[0], path[1], 0, -1]))
        init_policy(policies)

        edge_addition, edge_deletion = repair()
        print(f"delete links: {edge_deletion}")
        print(f"add links: {edge_addition}")
        if edge_addition is None and edge_addition is None:
            ret["status"] = False
            ret["message"] = "gurobi can not find any answer."
            ret["link_delta"][ec]["delete_links"] = list()
            ret["link_delta"][ec]["add_links"] = list()
        else:
            ret["link_delta"][ec]["delete_links"] = list(edge_deletion)
            ret["link_delta"][ec]["add_links"] = list(edge_addition)
            if len(edge_addition) == 0 and len(edge_deletion) == 0:
                ret["status"] = False
                ret["message"] = "gurobi says no need to change, there must be something wrong."
    return ret


class UpdateRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        verifier_request = json.loads(body)
        print(verifier_request)
        loop_free_data = verifier_request["loop_free_data"]
        repair_data = verifier_request["repair_data"]
        response_data = {}
        if loop_free_data:
            print("repair loops....")
            response_data = repair_loops(loop_free_data)
        elif repair_data:
            print("repair policies....")
            response_data = repair_policies(repair_data)
        else:
            response_data["status"] = 0
            response_data["message"] = "nothing to repair."
            print("nothing to repair.")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(response_data), 'utf-8'))


def read_topo():
    topo_graph: dict[str, set] = {}
    with open("./networkconfig/odltopo.txt", mode='r') as file:
        temp: str = file.readline()
        while temp:
            elements = temp.split(' ')
            node1 = elements[0].split('.')[0]
            node2 = elements[1].split('.')[0]
            if node1 not in topo_graph:
                topo_graph[node1] = set()
            topo_graph[node1].add(node2)
            temp = file.readline()
        file.close()
    init_topo_graph(topo_graph)


if __name__ == "__main__":
    # read net topo
    read_topo()
    server_address = ("127.0.0.1", 41421)
    httpd = HTTPServer(server_address, UpdateRequestHandler)
    print("server start at localhost:41421...")
    httpd.serve_forever()
