import _thread
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

from core.loop_free import get_remove_links
from core.repair import repair
from parse.configuration_graph import init_configuration_graph
from parse.policy_graph import init_policy
from parse.topo_graph import init_topo_graph


def start_apkeep():
    os.system("java -jar ./apkeep.jar")


def repair_loops(loop_free_data: dict[str, dict]):
    file = open('./networkconfig/odlrule.txt', mode='w')
    file.close()
    for ec, loop_data in loop_free_data.items():
        loops = loop_data["loops"]
        reachabilityPolicies = loop_data["reachability_policies"]
        policies = list()
        for policy in reachabilityPolicies:
            temp_list = list()
            temp_list.append(policy["from"])
            temp_list.append(policy["to"])
            policies.append(tuple(temp_list))
        loop_set = list()
        for loop in loops:
            loop_set.append(tuple(loop))
        _, deleted_links = get_remove_links(loop_set, policies)
        print(f"delete links: {deleted_links}")
        with open('./networkconfig/odlrule.txt', mode='a') as file:
            for link in deleted_links:
                file.write(f"$devicename {link[0]}\n")
                file.write(f"{ec} drop")
            file.close()


def repair_policies(repair_data: dict[str, dict]):
    file = open('./networkconfig/odlrule.txt', mode='w')
    file.close()
    for ec, data in repair_data.items():
        configuration_graph = data["configuration_graph"]
        init_configuration_graph(configuration_graph)
        reachability_policies = data["reachability_policies"]
        policies: set[tuple[str, str, int, int]] = set()
        for reachability_policy in reachability_policies:
            policy: tuple[str, str, int, int] = \
                tuple([reachability_policy['from'], reachability_policy['to'], 1, -1])
            policies.add(policy)
        init_policy(policies)
        edge_addition, edge_deletion = repair()
        print(f"delete links: {edge_deletion}")
        print(f"add links: {edge_addition}")
        with open('./networkconfig/odlrule.txt', mode='a') as file:
            for link in edge_deletion:
                file.write(f"$devicename {link[0]}\n")
                file.write(f"{ec} drop")
            for link in edge_addition:
                file.write(f"$devicename {link[0]}\n")
                if link[1] == "drop":
                    file.write(f"{ec} {link[1]}")
                else:
                    file.write(f"{ec} {edge_to_interface[f'{link[0]}-{link[1]}']}")
            file.close()


class UpdateRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/update":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # request
            while True:
                apkeep_response = requests.get("http://127.0.0.1:41420/verify").json()
                loop_free_data = apkeep_response["loop_free_data"]
                repair_data = apkeep_response["repair_data"]
                if loop_free_data:
                    print("repair loops....")
                    repair_loops(loop_free_data)
                elif repair_data:
                    print("repair policies....")
                    repair_policies(repair_data)
                else:
                    print("repair complete.")
                    break
        else:
            self.send_error(404, "NO CONTEXT FOR PATH")


edge_to_interface: dict[str, str] = {}


def read_topo():
    topo_graph: dict[str, set] = {}
    with open("./networkconfig/odltopo.txt", mode='r') as file:
        temp: str = file.readline()
        while temp:
            elements = temp.split(' ')
            node1 = elements[0].split('.')[0]
            node2 = elements[1].split('.')[0]
            edge_to_interface[f"{node1}-{node2}"] = elements[0].split('.')[1]
            if node1 not in topo_graph:
                topo_graph[node1] = set()
            topo_graph[node1].add(node2)
            temp = file.readline()
        file.close()
    init_topo_graph(topo_graph)


if __name__ == "__main__":
    # read net topo
    read_topo()
    _thread.start_new_thread(start_apkeep, ())
    server_address = ("127.0.0.1", 41421)
    httpd = HTTPServer(server_address, UpdateRequestHandler)
    httpd.serve_forever()
