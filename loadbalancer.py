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
        self.term = 1
        self.last_uncommitted = -1
        self.last_committed = -1
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
                # only process if node is leader
                if self.status == 'LEADER':
                    message['term'] = self.term
                    message['server'] = server_host+':'+server_port
                    message['workload'] = float(args[4])
                    self.last_uncommitted += 1
                    message['index'] = self.last_uncommitted
                    self.server_list[str(server_host+':'+server_port)] = message['workload']

                    self.send_response(200)
                    self.end_headers()
                    self.process_client_request(message)
                    for key in self.server_list:
                        print(self.wfile.write(self.server_list[key]))
            elif sender == 'FOLLOWER':
                message['msg_type'] = args[4]
                message['term'] = self.term
                message['server'] = args[6]
                message['workload'] = args[5]
                message['index'] = args[7]
                self.send_response(200)
                self.end_headers()
                self.process_follower_request(message)
            elif sender == 'CANDIDATE':
                pass
            elif sender == 'LEADER':
                print('process_leader_request')
                message['msg_type'] = args[4]
                message['term'] = self.term
                message['server'] = args[6]
                message['workload'] = args[5]
                message['index'] = args[7]
                self.send_response(200)
                self.end_headers()
                self.process_leader_request(server_host, str(server_port), message)
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)

    def process_client_request(self, msg):
        """ Handle requests issued by clients. """
        if self.status == 'LEADER':
            msg['count'] = 1
            self.raftlog.append(msg)
            self.last_uncommitted += 1
            print(self.raftlog)
            self.broadcast_request('AppendEntries', msg)

    def process_leader_request(self, leader_host, leader_port, msg):
        if msg['msg_type'] == 'AppendEntries':
            if self.is_consistent(msg):
                msg['count'] = 1
                self.raftlog.append(msg)
                self.last_uncommitted += 1
                print(self.raftlog)
                url = 'http://' + leader_host + ':' + leader_port + '/FOLLOWER/' + HOST_NAME + '/' + str(PORT_NUMBER) + '/' + 'AcceptAppendEntries' + '/' + str(msg['workload']) + '/' + str(msg['server']) + '/' + str(self.last_uncommitted)
                print(url)
                r = requests.get('http://' + leader_host + ':' + leader_port + '/FOLLOWER/' + HOST_NAME + '/' + str(PORT_NUMBER) + '/' + 'AcceptAppendEntries' + '/' + str(msg['workload']) + '/' + str(msg['server']) + '/' + str(self.last_uncommitted))
        elif msg['msg_type'] == 'AppendEntriesCommitted':
            if self.is_consistent(msg):
                majority = len(config.LOAD_BALANCER) / 2 + 1
                self.raftlog[msg['index']]['count'] = majority #committed
                self.last_committed += 1

    def process_follower_request(self, sender, msg):
        """ Handle requests issued by followers. """
        # To do : retrieve voting
        if msg['msg_type'] == 'AcceptAppendEntries':
            if self.status == 'LEADER':
                self.raftlog[msg['index']]['count'] += 1
                majority = len(config.LOAD_BALANCER) / 2 + 1
                if (self.raftlog[msg['index']]['count'] == majority):
                    self.last_committed += 1
                    # TO DO : CALCULATE PRIME NUMBER AND SEND TO CLIENT
                    self.broadcast_request('AppendEntriesCommitted', msg)

    def broadcast_request(self, msg_type, msg):
        """ Broadcrast a msg_type request to all servers """
        for server in config.LOAD_BALANCER:
            if not ((server[0] == HOST_NAME) and (server[1] == PORT_NUMBER)):
                url = 'http://' + str(server[0]) + ':' + str(server[1]) + '/LEADER/' + HOST_NAME + '/' + str(PORT_NUMBER) + '/' + str(msg_type) + '/' + str(msg['workload']) + '/' + str(msg['server']) + '/' + str(msg['index'])
                print(url)
                r = requests.get('http://' + str(server[0]) + ':' + str(server[1]) + '/LEADER/' + HOST_NAME + '/' + str(PORT_NUMBER) + '/' + str(msg_type) + '/' + str(msg['workload']) + '/' + str(msg['server']) + '/' + str(msg['index']))
                #print(r.status_code, r.reason)

    def is_consistent(self, msg):
        """
        Before a follower performs an AppendEntries call,
        check to see if the leader is valid.
        """
        # If the leader has a higher term, update our own term.
        if msg['term'] > self.term:
            self.term = msg['term']
        return True

# Run with host name and port number argument
# Example : python loadbalancer.py 127.0.0.1 8080
HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])

if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT_NUMBER), LoadBalancerHandler)
    server.serve_forever();
