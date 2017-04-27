#!/usr/bin/python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import sys

class LoadBalancerHandler(BaseHTTPRequestHandler):
    server_list = {}

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
            if len(args) != 4:
                raise Exception()
            server_host = args[1]
            server_port = args[2]
            server_workload = float(args[3])
            server_list[server_host+server_port] = server_workload

            self.send_response(200)
            self.end_headers()

            for key in server_list:
                self.wfile.write(server_list[key].encode('utf-8'))

            # Print to check if data is accepted correctly
            # self.wfile.write(server_port.encode('utf-8'))
            # self.wfile.write('\n'.encode('utf-8'))
            # self.wfile.write(str(server_workload).encode('utf-8'))
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)

# Run with host name and port number argument
# Example : python loadbalancer.py 127.0.0.1 8080
HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])

if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT_NUMBER), LoadBalancerHandler)
    server.serve_forever();
