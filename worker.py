#!/usr/bin/python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import sys

class WorkerHandler(BaseHTTPRequestHandler):
    def prime(self, n):
        i = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += 1
        return True

    def calc(self, n):
        p = 1
        while n > 0:
            p += 1
            if self.prime(p):
                n -= 1
        return p

    def do_GET(self):
        try:
            args = self.path.split('/')
            if len(args) != 2:
                raise Exception()
            n = int(args[1])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(self.calc(n)).encode('utf-8'))
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)

# Run with host name and port number argument
# Example : python worker.py 127.0.0.1 8080
HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])

if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT_NUMBER), WorkerHandler)
    server.serve_forever();
