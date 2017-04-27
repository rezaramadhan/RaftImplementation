#!/usr/bin/python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import requests
import sys
import config

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
            #if len(args) < 5:
            #    raise Exception()
            sender = args[1]
            server_host = args[2]
            server_port = args[3]
            message = {}
            # server_workload = float(args[4])
            # print(server_host+server_port)

            if sender == 'CLIENT':
                message['workload'] = float(args[4])
                self.server_list[str(server_host+':'+server_port)] = message['workload']

                for key in self.server_list:
                    print(self.wfile.write(self.server_list[key]))            
                    self.process_client_request(message)
            elif sender == 'FOLLOWER':
                pass
            elif sender == 'CANDIDATE':
                pass
            elif sender == 'LEADER':
                print('process_leader_request')
                message['msg_type'] = args[4]
                message['value'] = args[5]
                self.process_leader_request(message)			
            self.send_response(200)
            self.end_headers()
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)          
            
    def process_client_request(self, msg):
        """ Handle requests issued by clients. """
        if self.status == 'LEADER':
            self.raftlog.append(msg)
            print(self.raftlog)
            self.broadcast_request('AppendEntries', msg)
    
    def process_leader_request(self, msg):
        if self.status != 'FOLLOWER':
            self.status = 'FOLLOWER'

        if msg['msg_type'] == 'AppendEntries':
            self.raftlog.append(msg)
            print(self.raftlog)

    def broadcast_request(self, msg_type, msg):
        """ Broadcrast a msg_type request to all servers """
        for server in config.LOAD_BALANCER:
            if not ((server[0] == HOST_NAME) and (server[1] == PORT_NUMBER)):
                url = 'http://' + str(server[0]) + ':' + str(server[1]) + '/LEADER/' + HOST_NAME + '/' + str(PORT_NUMBER) + '/' + str(msg_type) + '/' + str(msg['workload'])
                print(url)
                r = requests.get('http://' + str(server[0]) + ':' + str(server[1]) + '/LEADER/' + HOST_NAME + '/' + str(PORT_NUMBER) + '/' + str(msg_type) + '/' + str(msg['workload']))
                #print(r.status_code, r.reason)

# Run with host name and port number argument
# Example : python loadbalancer.py 127.0.0.1 8080
HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])

if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT_NUMBER), LoadBalancerHandler)
    server.serve_forever();
