#!/usr/bin/python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import requests
import sys

loadBalancerList = []

class LoadBalancerHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        #Don't change init order. If changed, exception is gonna happen
        self.status = 'LEADER'
        self.server_list = {}
        self.raftlog = []
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        try:
            print(self.request.get('cpu_workload'))
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)

    def do_GET(self):
        try:
            args = self.path.split('/')
            if len(args) < 5:
                raise Exception()
            sender = args[1]
            server_host = args[2]
            server_port = args[3]
            server_workload = float(args[4])
            print(server_host+server_port)
            self.server_list[str(server_host+server_port)] = server_workload

            self.send_response(200)
            self.end_headers()

            for key in self.server_list:
                print(self.wfile.write(self.server_list[key]))
                #self.wfile.write(server_list[key].encode('utf-8'))

            if sender == 'CLIENT':
                self.process_client_request(server_workload)
            elif sender == 'FOLLOWER':
                pass
            elif sender == 'CANDIDATE':
                pass
            elif sender == 'LEADER':
                print('process_leader_request')
            # Print to check if data is accepted correctly
            # self.wfile.write(server_port.encode('utf-8'))
            # self.wfile.write('\n'.encode('utf-8'))
            # self.wfile.write(str(server_workload).encode('utf-8'))
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)

    def getLoadBalancerList(self, filename):
        with open(filename) as fp:
            for line in fp:
                loadBalancerList.append(line)            
            
    def process_client_request(self, server_workload):
        """ Handle requests issued by clients. """
        if self.status == 'LEADER':
            self.raftlog.append(server_workload)
            print(self.raftlog)
            self.broadcast_request('AppendEntries', server_workload)

    def broadcast_request(self, msg_type, data=None):
        """ Broadcrast a msg_type request to all servers """
        self.getLoadBalancerList('loadbalancer.txt')
        for url in loadBalancerList:
            url = url + 'LEADER/' + HOST_NAME + '/' + str(PORT_NUMBER) + '/' + str(data)
            print(url)
            r = requests.get(str(url))
            #print(r.status_code, r.reason)

# Run with host name and port number argument
# Example : python loadbalancer.py 127.0.0.1 8080
HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])

if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT_NUMBER), LoadBalancerHandler)
    server.serve_forever();
