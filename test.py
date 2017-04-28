#!/usr/bin/python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import sleep

import sys

myvar = 0

class LoadBalancerHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.myvar = 0

    def do_POST(self):
        try:
            print(self.request.get('cpu_workload'))
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title></head>")
        self.wfile.write("<body><p>This is a test.</p>")

        global myvar
        print myvar
        myvar += 1
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        # sleep(10)
        self.wfile.write("<p>You accessed path: %d</p>" % myvar)
        self.wfile.write("</body></html>")

class MyServer(HTTPServer):
    """docstring for ."""
    def __init__(self, address, handler):
        super(address, handler).__init__()
        self.myvar = 0


# Run with host name and port number argument
# Example : python loadbalancer.py 127.0.0.1 8080
HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])


if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT_NUMBER), LoadBalancerHandler)
    print "here"
    # t = Thread(target=server.serve_forever)
    server.serve_forever()
    # t.start()
    # print "here2"
